# ComfyUI-RICHIEPIC-H3

A small ComfyUI extension by RICHIEPIC Bt. for MiniMax H3 RefMod work:

- **H3 Reference Gallery (Photos / Video / Audio)** (`RICHIEPIC_H3ReferenceGallery`): one node that collects
  references from a thumbnail gallery and from upstream nodes, in one ordered list for the RefMod builder.
- **Example workflows**: building a RefMod, and a head swap that uses a RefMod instead of a reference image.

RefMod creation, loading and conditioning use the upstream
[ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod) nodes directly. This repository
contains no third-party node code and installs nothing at runtime; dependencies are managed by your pipeline.

## Install

```
cd ComfyUI/custom_nodes
git clone https://github.com/richiepic/ComfyUI-RICHIEPIC-H3
```

Install the dependencies below, then restart ComfyUI. No Python packages beyond ComfyUI's own (PIL, numpy, torch, PyAV).

## Dependencies

Tested together on ComfyUI 0.42.0 (`7cebca5`), frontend 1.57.1, Windows 11, RTX 5090.

### Custom node packs

| Pack | Repository | Tested version | Used by | Nodes used |
| --- | --- | --- | --- | --- |
| ComfyUI-MiniMaxH3Mod | https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod | 0.2.7, `517e8c4` | Builder, Head Swap | `MiniMaxH3RefModMasterExtract`, `MiniMaxH3RefModsLoader`, `MiniMaxH3RefModTextEncode` |
| ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes | 1.5.3, `ab72eda` | Head Swap | `SetNode`, `GetNode`, `ImageResizeKJv2`, `ColorMatchV2`, `ModelPreviewOverrideKJ`; comparison group: `ImageConcatMulti`, `AddLabel`, `SomethingToString` |
| ComfyUI-VideoHelperSuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite | 1.7.9, `4d907be` | Head Swap | `VHS_LoadVideoFFmpeg`, `VHS_VideoInfo` |
| Comfyui_Minimax_h3_latent_Upscaler | https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler | `40316cf` | Head Swap (second pass) | `MinimaxH3LatentUpscaler3D` |
| ComfyUI-Easy-Use | https://github.com/yolain/ComfyUI-Easy-Use | 1.4.1 (registry install) | Head Swap | `easy showAnything` |
| ComfyUI-Pixaroma | https://github.com/pixaroma/ComfyUI-Pixaroma | 1.4.248 (registry install) | Head Swap | `PixaromaGroupSwitch` (comparison group on / off) |

The gallery node itself needs none of these. Its outputs match the upstream input types:
`refs` (`H3_REF_LIST`) → `refs_bundle` and `audio` (`AUDIO`) → `audio` of **Create H3 RefMod Master**.

### Models and LoRAs (Head Swap workflow)

| ComfyUI folder | File | Source |
| --- | --- | --- |
| `diffusion_models` | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| `text_encoders` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| `vae` | `minimax_h3_video_vae_fp16.safetensors`, `minimax_h3_audio_vae_fp32.safetensors` | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| `loras` | `minimax_h3_head_swap_v1.0_r32.safetensors` (strength 1.0) | [Alissonerdx/Minimax-H3-ComfyUI](https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI) |
| `loras` | `minimax_h3_dmd_ref2va_8step_turbo_pruned.safetensors` (strength 1.0) | [drbaph/MiniMax-H3-Turbo-Lora-ComfyUI](https://huggingface.co/drbaph/MiniMax-H3-Turbo-Lora-ComfyUI) |
| `loras` | `minimax_h3_lms_v1.0_r64.safetensors` (strength 0.7, second pass) | [Alissonerdx/Minimax-H3-ComfyUI](https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI) |
| `latent_upscale_models` | `h3_upscaler_lms_v0.1.safetensors` (second pass) | [Alissonerdx/Minimax-H3-ComfyUI](https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI) |
| `vae_approx` | `taeh3.safetensors` (sampling preview) | [Alissonerdx/Minimax-H3-ComfyUI](https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI) |
| `refmods` | your RefMod, selected in **Load H3 RefMods** (placeholder `my_identity_refmod`) | made with the Builder workflow |

The workflow also contains a `qwen3.5_9b_w4a8_gptq.safetensors` "Prompt Enhancer" CLIP loader from the original
graph; nothing consumes it in this version, so it is not loaded at run time.

The Builder workflow needs only the two H3 VAEs.

## H3 Reference Gallery

Category `RICHIEPIC/H3 RefMod`.

**Gallery files**: drop files on the grid or click **+ Add references** (uploaded to `ComfyUI/input/refgallery/`).
Checkbox = use or skip; × = remove the card (the file stays on disk); drag a card onto another to reorder.
Video and audio cards have start / length fields in seconds (empty = node defaults).

**External inputs** (all optional; existing workflows keep working without them):

| Input | Type | Becomes |
| --- | --- | --- |
| `external_images` | IMAGE | One still reference per batch item, in batch order |
| `external_image_sequence` | IMAGE | One multi-frame reference, frames in order (EXR / PNG / DPX sequence loaders, etc.) |
| `external_video_with_audio` | VIDEO | One multi-frame reference; its soundtrack is an audio candidate |

External tensors are passed through unchanged: no resize, no colour conversion, no re-encode, no disk write. Do
resizing, colour management (for example OCIO to display-referred sRGB), trimming (core **Video Trim**) and
batching upstream. Non-RGB inputs (for example RGBA) are rejected with a message; values outside 0..1 are not
clamped but flagged in the `summary` output. `max_edge`, `max_frames` and the trim settings apply only to
gallery files.

**Reference order** (also printed, numbered, in `summary`; cards show the same `#N`):
1. gallery cards, in card order
2. `external_images`
3. `external_image_sequence`
4. `external_video_with_audio`

**Audio** (`audio_source`): `auto` = first audio card, else the first video soundtrack in reference order.

| Setting | Meaning |
| --- | --- |
| `max_edge` | Longest edge in px for gallery files, downscale only. |
| `max_frames` | Frames kept per gallery video, sampled uniformly from the trimmed range. |
| `video_start`, `video_seconds` | Default trim for gallery videos. `video_seconds` 0 = whole clip. |
| `audio_source` | `none`, `first audio file`, `first video soundtrack`, `auto`. |

Outputs: `refs` (`H3_REF_LIST`), `audio` (`AUDIO`), `count`, `summary`.

### When to use the upstream inputs instead

**Create H3 RefMod Master** has its own `ref_image_N` / `ref_video_N` sockets, and ComfyUI-MiniMaxH3Mod has
**Load H3 RefMod Folder** for a whole folder. Use those when they fit:

- A few individual stills or clips: connect them straight to `ref_image_N` / `ref_video_N`. Master orders its own
  sockets first, then `refs_bundle`.
- A whole folder of files: **Load H3 RefMod Folder** → `refs_bundle`.
- Use the gallery when you need hand-picked files, per-clip trims, one combined order across files and upstream
  nodes, an image batch split into separate stills (a batch on `ref_image_N` keeps only its first image), or the
  audio picked from the same set.

Subject masks on Master follow its reference order: its own image sockets, its own video sockets, then the
`refs_bundle` list in the order above.

## Workflows

### `workflows/RICHIEPIC_H3_RefMod_Builder.json`

Gallery → **Create H3 RefMod Master** (video VAE + audio VAE). Notes from testing:

- **Full Reference** costs about 330 tokens per image at `ref_resolution` 512. Keep `budget_policy` on `error` to
  see the real count instead of losing references silently.
- Put a close-up portrait first: it sets the canvas, other references are cover-cropped to it.
- Enter the name without `.safetensors`. Files are saved to `ComfyUI/models/refmods`.

### `workflows/RICHIEPIC_H3_Head_Swap_RefMod.json`

Character Swap v1.1 native graph with the **Head Swap v1.0** LoRA. The RefMod is loaded with **Load H3 RefMods**
and presented with **H3 RefMod Text Encode**. Set `my_identity_refmod` to your file and `your_guide_video.mp4` to
your clip.

- Frame handling: the guide video is loaded at the `FPS` value (24) and capped at
  `max(5, round(Duration * 24))` rounded up to H3's `17k+5` grid. Set `Duration` so the loaded frame count
  lands on the grid (for example 5.875 s = 141 frames, 8.708 s = 209 frames); Add Guide crops longer clips down
  to the grid.
- The prompt is empty: the head swap LoRA and the RefMod do the work. `<Picture 1>` can be added; the RefMod's
  label is in the `reference_map` output of H3 RefMod Text Encode.
- Use the **head swap** LoRA. The character swap LoRA replaces the whole figure.
- Results are colour matched to the guide (`ColorMatchV2`, `hm-mkl-hm`) and saved with core **Create Video** /
  **Save Video** (24 fps, 10-bit, H.264) as `video/character_swap_first_pass` and
  `video/character_swap_final_pass`.
- The side-by-side comparison group is bypassed by default; turn it on with the **Comparison ON / OFF** switch.

## License

MIT, Copyright (c) 2026 RICHIEPIC Bt. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Dependencies, models and LoRAs are not included and have their own licenses.
