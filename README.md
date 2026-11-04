# ComfyUI-RICHIEPIC-H3

MiniMax H3 RefMod tools for ComfyUI by RICHIEPIC Bt. One pack, no other RefMod pack needed:

- **H3 Reference Gallery (Photos / Video / Audio)**: thumbnail gallery for reference photos, videos and audio.
- **RefMod nodes**: create, save, load, inspect and apply RefMods, the shareable `.safetensors` files that hold a
  pre-encoded MiniMax H3 reference (for example one person's identity). Vendored from
  [ComfyUI-MiniMaxH3Mod](https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod) (MIT, Luisa) at commit `517e8c4`,
  with `RICHIEPIC_` node ids so it can be installed next to the upstream pack without clashing.
- **Example workflows**: building a RefMod, and a head swap that uses the RefMod instead of a reference image.

All nodes are in the `RICHIEPIC/H3 RefMod` category.

## Install

```
cd ComfyUI/custom_nodes
git clone https://github.com/richiepic/ComfyUI-RICHIEPIC-H3
```

Restart ComfyUI. No extra Python packages are needed (PIL, numpy, torch, safetensors and PyAV ship with ComfyUI).
Needs a current ComfyUI with native MiniMax H3 support. The head swap workflow also uses common packs
(KJNodes, VideoHelperSuite and others); ComfyUI lists the missing ones when the workflow is opened.

RefMod files live in `ComfyUI/models/refmods` (or a `refmods` entry in `extra_model_paths.yaml`). Files made with
the upstream ComfyUI-MiniMaxH3Mod are read as they are, and files made here are readable there: the file format
is unchanged, only the node ids differ.

## Nodes

| Node | Id |
| --- | --- |
| H3 Reference Gallery (Photos / Video / Audio) | `RICHIEPIC_H3ReferenceGallery` |
| Create H3 RefMod Master | `RICHIEPIC_H3RefModMasterExtract` |
| Create H3 RefMod | `RICHIEPIC_H3RefModExtract` |
| Create H3 Audio RefMod | `RICHIEPIC_H3RefModAudioExtract` |
| Load H3 RefMods | `RICHIEPIC_H3RefModsLoader` |
| Load H3 RefMod Axis | `RICHIEPIC_H3RefModsAxis` |
| Load H3 RefMod Folder | `RICHIEPIC_H3RefModFolderLoader` |
| H3 RefMod Text Encode | `RICHIEPIC_H3RefModTextEncode` |
| Apply H3 RefMod | `RICHIEPIC_H3RefModApply` |
| H3 RefMod Step Curve | `RICHIEPIC_H3RefModStepCurve` |
| Inspect H3 RefMod | `RICHIEPIC_H3RefModInspect` |
| Save H3 RefMods | `RICHIEPIC_H3RefModSave` |
| Save H3 RefMod Bundle | `RICHIEPIC_H3RefModBundleSave` |
| Fix H3 RefMod Config | `RICHIEPIC_H3RefModConfig` |
| Collect H3 RefMod Masks | `RICHIEPIC_H3RefModMaskList` |
| Continuum RefMod Bridge / Disarm H3 RefMod Bridge | `RICHIEPIC_H3RefModContinuumBridge`, `RICHIEPIC_H3RefModBridgeDisarm` |

File format: [refmod/BUNDLE_FORMAT.md](refmod/BUNDLE_FORMAT.md). The upstream README documents the extraction
modes and Apply curves in detail.

### Moving workflows from ComfyUI-MiniMaxH3Mod

Node ids changed, file format did not. In a workflow `.json`, replace `"MiniMaxH3RefMod` with
`"RICHIEPIC_H3RefMod` (and `"H3ReferenceGallery"` with `"RICHIEPIC_H3ReferenceGallery"`), then open it again.

## H3 Reference Gallery

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

## Workflows

### `workflows/RICHIEPIC_H3_RefMod_Builder.json`

Gallery → **Create H3 RefMod Master** (video VAE + audio VAE). Notes from testing:

- In **Full Reference** mode every image costs tokens: about 330 per image at `ref_resolution` 512. Keep
  `budget_policy` on `error` to see the real count instead of losing references silently.
- Put a close-up portrait first: it sets the canvas, other references are cover-cropped to it.
- Enter the name without `.safetensors`.

### `workflows/RICHIEPIC_H3_Head_Swap_RefMod.json`

Character Swap v1.1 native graph with the **Head Swap v1.0** LoRA; the RefMod is loaded with **Load H3 RefMods**
and presented with **H3 RefMod Text Encode** (prompt: `<Picture 1>`). Set `my_identity_refmod` to your file.

| Folder | File |
| --- | --- |
| `diffusion_models` | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` ([Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)) |
| `text_encoders` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| `vae` | `minimax_h3_video_vae_fp16.safetensors`, `minimax_h3_audio_vae_fp32.safetensors` |
| `loras` | `minimax_h3_head_swap_v1.0_r32.safetensors` ([Alissonerdx/Minimax-H3-ComfyUI](https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI)) |
| `loras` | `minimax_h3_dmd_ref2va_8step_turbo_pruned.safetensors` ([drbaph](https://huggingface.co/drbaph/MiniMax-H3-Turbo-Lora-ComfyUI)) |
| `loras` | `minimax_h3_lms_v1.0_r64.safetensors` (optional second pass) |

- Use the **head swap** LoRA. The character swap LoRA replaces the whole figure.
- Set `Duration` so the loaded frame count lands on H3's `17k+5` grid (for example 5.875 s = 141 frames,
  8.708 s = 209 frames at 24 fps). Add Guide crops longer clips down to the grid.
- The RefMod label is in the `reference_map` output of H3 RefMod Text Encode.

## License

MIT. RICHIEPIC Bt. code: [LICENSE](LICENSE). The `refmod/` folder is Copyright (c) 2026 Luisa (luisacaotica)
under its own MIT license, [refmod/LICENSE](refmod/LICENSE). Details in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Models and LoRAs are not included and have their own licenses.
