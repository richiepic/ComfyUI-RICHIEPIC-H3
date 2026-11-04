# ComfyUI-RICHIEPIC-H3

MiniMax H3 tools for ComfyUI by RICHIEPIC Bt.

- **H3 Reference Gallery (Photos / Video / Audio)**: one node with a thumbnail gallery for
  reference photos, videos and audio. It feeds **Create H3 RefMod Master** of
  [ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod), so an identity can be
  saved once as a shareable RefMod `.safetensors` file.
- **Example workflows**: building a RefMod, and a head swap that uses the RefMod instead of a reference image.

## Install

```
cd ComfyUI/custom_nodes
git clone https://github.com/richiepic/ComfyUI-RICHIEPIC-H3
```

Restart ComfyUI. No extra Python packages are needed (PIL, numpy, torch and PyAV ship with ComfyUI).

Required for the workflows, installed separately:

- A current ComfyUI with native MiniMax H3 support.
- [ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod) (MIT): `git clone` it into
  `custom_nodes`. It is not in ComfyUI Manager.
- The node packs the head swap workflow lists as missing when opened (KJNodes, VideoHelperSuite, and others).

## H3 Reference Gallery

Category `MiniMax-H3/gallery`.

1. Drop files on the grid or click **+ Add references**. Files are uploaded to `ComfyUI/input/refgallery/`.
2. Checkbox = use or skip a card; × = remove the card (the file stays on disk); drag a card onto another to reorder.
3. Video and audio cards have start / length fields in seconds. Empty = node defaults.
4. Connect `refs` → `refs_bundle` and `audio` → `audio` of **Create H3 RefMod Master**.

| Setting | Meaning |
| --- | --- |
| `max_edge` | Longest edge in px, downscale only. |
| `max_frames` | Frames kept per video, sampled uniformly from the trimmed range. |
| `video_start`, `video_seconds` | Default trim for every video. `video_seconds` 0 = whole clip. |
| `audio_source` | `auto`: first audio card, else the first video's soundtrack. |

Outputs: `refs` (H3_REF_LIST: images as 1-frame, videos as multi-frame tensors), `audio`, `count`, `summary`.
Portrait phone videos are rotated like ComfyUI's own video loader does.

## Workflows

### `workflows/RICHIEPIC_H3_RefMod_Builder.json`

Gallery → **Create H3 RefMod Master** (video VAE + audio VAE). Notes from testing:

- In **Full Reference** mode every image costs tokens: about 330 per image at `ref_resolution` 512. Keep
  `budget_policy` on `error` to see the real count instead of losing references silently.
- Put a close-up portrait first: it sets the canvas, other references are cover-cropped to it.
- Enter the name without `.safetensors`.
- Files are saved to `ComfyUI/models/refmods`.

### `workflows/RICHIEPIC_H3_Head_Swap_RefMod.json`

Character Swap v1.1 native graph with the **Head Swap v1.0** LoRA, the RefMod loaded with **Load H3 RefMods**
and presented with **H3 RefMod Text Encode** (prompt: `<Picture 1>`). Set `my_identity_refmod` to your file.

Models:

| Folder | File |
| --- | --- |
| `diffusion_models` | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` ([Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)) |
| `text_encoders` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| `vae` | `minimax_h3_video_vae_fp16.safetensors`, `minimax_h3_audio_vae_fp32.safetensors` |
| `loras` | `minimax_h3_head_swap_v1.0_r32.safetensors` ([Alissonerdx/Minimax-H3-ComfyUI](https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI)) |
| `loras` | `minimax_h3_dmd_ref2va_8step_turbo_pruned.safetensors` ([drbaph](https://huggingface.co/drbaph/MiniMax-H3-Turbo-Lora-ComfyUI)) |
| `loras` | `minimax_h3_lms_v1.0_r64.safetensors` (optional second pass) |

Notes:

- Use the **head swap** LoRA. The character swap LoRA replaces the whole figure.
- Set `Duration` so the loaded frame count lands on H3's `17k+5` grid (for example 5.875 s = 141 frames,
  8.708 s = 209 frames at 24 fps). Add Guide crops longer clips down to the grid.
- The RefMod label is in the `reference_map` output of H3 RefMod Text Encode.

## License

MIT, Copyright (c) 2026 RICHIEPIC Bt. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Models and LoRAs are not included and have their own licenses.
