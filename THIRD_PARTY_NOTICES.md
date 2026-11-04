# Third-party notices

## RefMod nodes: `refmod/` and `web/library_dialog.js`, `web/refmod_apply.js`, `web/refmod_creation_labels.js`, `web/refmod_library.js`, `web/refmod_slots.js`

Vendored from https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod at commit
517e8c419a8584fbf69fceb487bc39d83e6a6ec8 (v0.2.7), licensed under the MIT License:

```text
MIT License

Copyright (c) 2026 Luisa (luisacaotica)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Changes by RICHIEPIC Bt.:
- Node ids renamed from `MiniMaxH3RefMod*` to `RICHIEPIC_H3RefMod*`; category `RICHIEPIC/H3 RefMod`.
- Library route renamed from `/refmods/library` to `/richiepic_h3/refmods/library`; frontend extension names
  prefixed `RICHIEPIC.H3.`.
- Upstream ApplyCond to Apply node migration removed.
- Moved into the `refmod/` subpackage. Not included: tests, example media, the example mod, the standalone
  extraction CLI and the upstream documentation files except `BUNDLE_FORMAT.md`.
- The RefMod file format is unchanged.

## workflows/RICHIEPIC_H3_Head_Swap_RefMod.json

Derived from `workflows/minimax_h3_character_swap_workflow_native_nodes_v1.1.json`
in https://github.com/alisson-anjos/Henge (reviewed at commit 7d825b5), licensed under the MIT License:

```text
MIT License

Copyright (c) 2026 Henge contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Changes: head swap LoRA instead of character swap, reference supplied as a RefMod
(ComfyUI-MiniMaxH3Mod Load H3 RefMods + H3 RefMod Text Encode), RefMods group added, local file names removed.

`__init__.py`, `gallery_nodes.py` and `web/ref_gallery.js` were written for RICHIEPIC Bt. and contain no third-party code.
Models and LoRAs used by the workflows are not included and carry their own licenses.
