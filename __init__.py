"""ComfyUI-RICHIEPIC-H3: MiniMax H3 RefMod tools (RICHIEPIC Bt.).

- gallery_nodes.py: H3 Reference Gallery (RICHIEPIC Bt., MIT).
- refmod/: RefMod create / load / apply / text encode nodes, vendored from
  ComfyUI-MiniMaxH3Mod (Copyright (c) 2026 Luisa (luisacaotica), MIT) with
  RICHIEPIC_ node ids. See THIRD_PARTY_NOTICES.md and refmod/LICENSE.
"""

from .gallery_nodes import NODE_CLASS_MAPPINGS as _GALLERY, NODE_DISPLAY_NAME_MAPPINGS as _GALLERY_NAMES
from .refmod.nodes import NODE_CLASS_MAPPINGS as _REFMOD, NODE_DISPLAY_NAME_MAPPINGS as _REFMOD_NAMES

WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {**_GALLERY, **_REFMOD}
NODE_DISPLAY_NAME_MAPPINGS = {**_GALLERY_NAMES, **_REFMOD_NAMES}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
