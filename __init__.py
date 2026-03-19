"""
ComfyUI RTX Video Suite
Main entry point - registers all nodes from rtx_nodes.py and RTXVideoReview.py
"""

WEB_DIRECTORY = "./web/js"  # for custom JS/CSS (VideoReviewAndConfirm node)

# Import all nodes from rtx_nodes.py
from .rtx_nodes import (
    NODE_CLASS_MAPPINGS as RTX_NODES_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as RTX_NODES_DISPLAY
)

# Import nodes from RTXVideoReview.py
from .RTXVideoReview import (
    NODE_CLASS_MAPPINGS as REVIEW_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as REVIEW_DISPLAY
)

# Merge mappings - no duplicates
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(RTX_NODES_MAPPINGS)
NODE_CLASS_MAPPINGS.update(REVIEW_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(RTX_NODES_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(REVIEW_DISPLAY)

__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'WEB_DIRECTORY'
]

# Optional startup banner
print("RTX Video Suite loaded:")
print("  • NativeVideoPathPicker")
print("  • RTXBatchVideoUpscale (Simple)")
print("  • RTXBatchVideoUpscaleAdvanced")
print("  • VideoReviewAndConfirm (VAE Review → RTX Confirm)")
