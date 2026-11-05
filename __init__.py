"""ComfyUI-RICHIEPIC-H3 (RICHIEPIC Bt., MIT): H3 Reference Gallery node and example workflows.

RefMod creation, loading and conditioning use the upstream ComfyUI-MiniMaxH3Mod nodes,
installed separately. See README.md for dependencies.
"""

from .gallery_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
