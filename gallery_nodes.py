"""H3 Reference Gallery: one node with thumbnails for photos, videos and audio.

Outputs plug straight into ComfyUI-MiniMaxH3Mod's "Create H3 RefMod Master":
  refs  (H3_REF_LIST) -> refs_bundle
  audio (AUDIO)       -> audio
Optional external inputs (IMAGE, IMAGE sequence, VIDEO) join the same ordered
reference list without touching disk. No import of MiniMaxH3Mod; uses PIL,
numpy, torch and PyAV, which ship with ComfyUI.

Reference order: gallery cards (card order), then external_images (one still per
batch item, batch order), then external_image_sequence (one multi-frame
reference), then external_video_with_audio (one multi-frame reference).
"""

from __future__ import annotations

import hashlib
import json
import os

import numpy as np
import torch
from PIL import Image, ImageOps

import folder_paths

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
AUDIO_EXT = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".opus"}


def kind_of(name):
    ext = os.path.splitext(name)[1].lower()
    if ext in IMAGE_EXT:
        return "image"
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    return None


def parse_gallery(gallery):
    try:
        data = json.loads(gallery or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError(f"H3 Reference Gallery: broken gallery data ({exc}).")
    items = data.get("items", []) if isinstance(data, dict) else data
    out = []
    for item in items:
        if not isinstance(item, dict) or not item.get("name") or item.get("enabled") is False:
            continue
        kind = item.get("kind") or kind_of(item["name"])
        if kind is None:
            continue
        out.append({**item, "kind": kind})
    return out


def resolve_path(item):
    base = folder_paths.get_directory_by_type(item.get("type") or "input")
    if base is None:
        raise ValueError(f"Unknown folder type '{item.get('type')}'.")
    base = os.path.abspath(base)
    path = os.path.abspath(os.path.join(base, os.path.normpath(item.get("subfolder") or ""), item["name"]))
    if os.path.commonpath((base, path)) != base:
        raise ValueError(f"'{item['name']}' points outside the ComfyUI folder.")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"H3 Reference Gallery: file not found: {path}")
    return path


def fit(img, max_edge):
    w, h = img.size
    scale = min(1.0, max_edge / max(w, h))
    if scale < 1.0:
        img = img.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    return img


def load_image(path, max_edge):
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)  # phone photos keep their orientation
        img = fit(img.convert("RGB"), max_edge)
        arr = np.asarray(img, dtype=np.float32) / 255.0
    return torch.from_numpy(arr)[None]  # [1,H,W,C]


def load_video(path, max_frames, max_edge, start, seconds):
    import av

    end = start + seconds if seconds > 0 else None
    frames = []
    with av.open(path) as container:
        stream = container.streams.video[0]
        stream.thread_type = "AUTO"
        if start > 0 and stream.time_base:
            container.seek(int(start / stream.time_base), stream=stream, backward=True)
        for frame in container.decode(stream):
            t = float(frame.pts * stream.time_base) if frame.pts is not None else None
            if t is not None and t < start:
                continue
            if end is not None and t is not None and t > end:
                break
            img = np.asarray(fit(frame.to_image(), max_edge), dtype=np.uint8)
            # Phone videos store portrait orientation as display-matrix rotation;
            # same convention as ComfyUI's own video loader (comfy_api video_types).
            k = int(round(frame.rotation // 90)) % 4 if getattr(frame, "rotation", 0) else 0
            frames.append(np.rot90(img, k=k, axes=(0, 1)).copy() if k else img)
    if not frames:
        raise ValueError(f"No video frames in the selected range of {os.path.basename(path)}.")
    if len(frames) > max_frames:
        keep = np.linspace(0, len(frames) - 1, max_frames).round().astype(int)
        frames = [frames[i] for i in keep]
    return torch.from_numpy(np.stack(frames).astype(np.float32) / 255.0)  # [T,H,W,C]


def load_audio(path, start, seconds):
    import av

    chunks, rate, t0 = [], None, None
    with av.open(path) as container:
        if not container.streams.audio:
            return None
        stream = container.streams.audio[0]
        rate = stream.rate or stream.codec_context.sample_rate
        resampler = av.AudioResampler(format="fltp", layout="stereo", rate=rate)
        if start > 0 and stream.time_base:
            container.seek(int(start / stream.time_base), stream=stream, backward=True)
        for frame in container.decode(stream):
            if t0 is None:
                t0 = float(frame.pts * stream.time_base) if frame.pts is not None else 0.0
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray())
            if seconds > 0 and frame.pts is not None and float(frame.pts * stream.time_base) > start + seconds + 1:
                break
        for out in resampler.resample(None):
            chunks.append(out.to_ndarray())
    if not chunks:
        return None
    wave = np.concatenate(chunks, axis=1)  # [2,S]
    # A seek lands on the packet before `start`: cut the samples decoded before it.
    a = max(0, int((start - (t0 or 0.0)) * rate))
    b = a + int(seconds * rate) if seconds > 0 else wave.shape[1]
    wave = wave[:, a:b]
    return {"waveform": torch.from_numpy(np.ascontiguousarray(wave))[None], "sample_rate": int(rate)}


def check_frames(t, label):
    """External IMAGE tensors are passed through unchanged; only reject what the H3 VAE cannot take."""
    if t is None:
        return None
    if t.ndim == 3:
        t = t[None]  # a single [H,W,C] image
    if t.ndim != 4 or t.shape[0] == 0:
        raise ValueError(f"H3 Reference Gallery: {label} must be an IMAGE [frames, height, width, channels], "
                         f"got {tuple(t.shape)}.")
    if t.shape[-1] != 3:
        raise ValueError(f"H3 Reference Gallery: {label} has {t.shape[-1]} channels; MiniMax H3 needs RGB. "
                         "Convert upstream (for example core 'Split Image with Alpha').")
    return t


def range_note(t):
    """Values outside 0..1 (linear / HDR EXR) are not clamped here; flag them in the summary."""
    lo, hi = float(t.min()), float(t.max())
    return f"  (values {lo:.3g}..{hi:.3g} outside 0..1: convert to display-referred upstream)" if lo < 0 or hi > 1 else ""


class H3ReferenceGallery:
    """Drag & drop photos, videos and audio; outputs a ref list and one audio track."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gallery": ("STRING", {"default": "[]", "multiline": False,
                    "tooltip": "Managed by the gallery widget (uploaded files in input/refgallery)."}),
                "max_edge": ("INT", {"default": 1024, "min": 256, "max": 4096, "step": 64,
                    "tooltip": "Longest edge in px (downscale only). The RefMod creator resizes to its own ref_resolution anyway."}),
                "max_frames": ("INT", {"default": 240, "min": 2, "max": 4800,
                    "tooltip": "Frames kept per video, sampled uniformly from the trimmed range."}),
                "video_start": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 36000.0, "step": 0.1,
                    "tooltip": "Seconds skipped at the start of every video (per-card trim overrides it)."}),
                "video_seconds": ("FLOAT", {"default": 15.0, "min": 0.0, "max": 3600.0, "step": 0.5,
                    "tooltip": "Seconds used from every video. 0 = whole clip (per-card trim overrides it)."}),
                "audio_source": (["none", "first audio file", "first video soundtrack", "auto"], {"default": "auto",
                    "tooltip": "auto = first audio card, else the first video soundtrack in reference order "
                               "(gallery videos before external_video_with_audio)."}),
            },
            "optional": {
                "external_images": ("IMAGE", {
                    "tooltip": "Stills from upstream nodes. A batch becomes one still reference per item, in batch "
                               "order, after the gallery cards. Passed through unchanged (no resize, no re-encode)."}),
                "external_image_sequence": ("IMAGE", {
                    "tooltip": "Frames of one clip (EXR / PNG / DPX sequence loader, etc.). Becomes one multi-frame "
                               "reference in frame order. Passed through unchanged; max_frames and trim do not apply."}),
                "external_video_with_audio": ("VIDEO", {
                    "tooltip": "A ComfyUI VIDEO (for example core Load Video / Video Trim). Becomes one multi-frame "
                               "reference; its soundtrack can feed the audio output."}),
            },
        }

    RETURN_TYPES = ("H3_REF_LIST", "AUDIO", "INT", "STRING")
    RETURN_NAMES = ("refs", "audio", "count", "summary")
    FUNCTION = "load"
    CATEGORY = "RICHIEPIC/H3 RefMod"
    DESCRIPTION = ("Gallery of reference photos/videos/audio. Connect refs to refs_bundle and audio to audio "
                   "of Create H3 RefMod Master.")

    @classmethod
    def IS_CHANGED(cls, gallery, **kwargs):
        # Only widget values and the gallery files are hashed here; linked inputs (tensors, VIDEO)
        # are tracked by ComfyUI's own cache keys of the upstream nodes.
        widgets = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool)) or v is None}
        h = hashlib.sha256((gallery or "").encode() + json.dumps(widgets, sort_keys=True).encode())
        for item in parse_gallery(gallery):
            try:
                st = os.stat(resolve_path(item))
                h.update(f"{item['name']}:{st.st_size}:{st.st_mtime_ns}".encode())
            except Exception as exc:
                h.update(str(exc).encode())
        return h.hexdigest()

    def load(self, gallery, max_edge=1024, max_frames=240, video_start=0.0, video_seconds=15.0,
             audio_source="auto", external_images=None, external_image_sequence=None,
             external_video_with_audio=None):
        refs, lines, audio = [], [], None
        soundtracks = []  # video soundtracks in reference order, loaded only if needed

        def add(t, text):
            refs.append(t)
            kind = "still" if t.shape[0] == 1 else f"{t.shape[0]} frames"
            lines.append(f"#{len(refs):<3} {text} -> {kind} {tuple(t.shape[1:3])}{range_note(t)}")

        # 1. Gallery cards, in card order.
        for item in parse_gallery(gallery):
            path = resolve_path(item)
            start = float(video_start if item.get("start") is None else item["start"])
            seconds = float(video_seconds if item.get("seconds") is None else item["seconds"])
            if item["kind"] == "image":
                add(load_image(path, max_edge), f"gallery image  {item['name']}")
            elif item["kind"] == "video":
                add(load_video(path, max_frames, max_edge, start, seconds), f"gallery video  {item['name']}")
                soundtracks.append((item["name"], lambda p=path, s=start, d=seconds: load_audio(p, s, d)))
            elif item["kind"] == "audio" and audio is None and audio_source in ("first audio file", "auto"):
                # Audio files ignore the global video trim; only their own card trim applies.
                audio = load_audio(path, float(item.get("start") or 0.0), float(item.get("seconds") or 0.0))
                if audio is not None:
                    lines.append(f"audio  {item['name']} -> {audio['waveform'].shape[-1] / audio['sample_rate']:.1f}s")

        # 2. External stills: one reference per batch item (views, no copy).
        images = check_frames(external_images, "external_images")
        if images is not None:
            for i in range(images.shape[0]):
                add(images[i:i + 1], f"external image {i + 1}/{images.shape[0]}")

        # 3. External image sequence: one multi-frame reference, frame order kept.
        sequence = check_frames(external_image_sequence, "external_image_sequence")
        if sequence is not None:
            add(sequence, "external image sequence")

        # 4. External VIDEO: frames as one reference, soundtrack as an audio candidate.
        if external_video_with_audio is not None:
            parts = external_video_with_audio.get_components()
            add(check_frames(parts.images, "external_video_with_audio"),
                f"external video  {float(parts.frame_rate):.3g} fps")
            if parts.audio is not None:
                soundtracks.append(("external video", lambda a=parts.audio: a))

        if audio is None and soundtracks and audio_source in ("first video soundtrack", "auto"):
            name, get = soundtracks[0]
            audio = get()
            if audio is not None:
                lines.append(f"audio  soundtrack of {name} -> "
                             f"{audio['waveform'].shape[-1] / audio['sample_rate']:.1f}s")
        if not refs and audio is None:
            raise ValueError("H3 Reference Gallery is empty. Add gallery cards or connect an external input.")
        summary = f"{len(refs)} visual refs (order below), audio: {'yes' if audio else 'no'}\n" + "\n".join(lines)
        print("[H3 Reference Gallery] " + summary.replace("\n", "\n  "), flush=True)
        # Master treats an empty list as "no folder refs"; None audio leaves its audio branch off.
        return (refs or None, audio, len(refs), summary)


NODE_CLASS_MAPPINGS = {"RICHIEPIC_H3ReferenceGallery": H3ReferenceGallery}
NODE_DISPLAY_NAME_MAPPINGS = {"RICHIEPIC_H3ReferenceGallery": "H3 Reference Gallery (Photos / Video / Audio)"}
