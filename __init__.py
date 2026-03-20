"""
ComfyUI RTX Video & Audio Suite
Main entry point - registers all nodes from:
1. rtx_nodes.py (Upscaling)
2. RTXVideoReview.py (Interactive Review)
3. rtx_audio_muxer.py (Instant Audio Muxing)
"""

# Katalog dla JS/CSS (wymagany dla węzła Review)
WEB_DIRECTORY = "./web/js"

# 1. Import mapowań z rtx_nodes.py
from .rtx_nodes import (
    NODE_CLASS_MAPPINGS as RTX_NODES_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as RTX_NODES_DISPLAY
)

# 2. Import mapowań z RTXVideoReview.py
from .RTXVideoReview import (
    NODE_CLASS_MAPPINGS as REVIEW_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as REVIEW_DISPLAY
)

# 3. Import mapowań z rtx_audio_muxer.py
from .rtx_audio_muxer import (
    NODE_CLASS_MAPPINGS as MUXER_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as MUXER_DISPLAY
)

# --- ŁĄCZENIE MAPOWAŃ (Merging) ---

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(RTX_NODES_MAPPINGS)
NODE_CLASS_MAPPINGS.update(REVIEW_MAPPINGS)
NODE_CLASS_MAPPINGS.update(MUXER_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(RTX_NODES_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(REVIEW_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(MUXER_DISPLAY)

__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'WEB_DIRECTORY'
]

# --- Pełny Komunikat Startowy ---
print("\n" + "="*60)
print("🚀 RTX Video & Audio Suite Loaded Successfully:")
print("  • 📁 NativeVideoPathPicker")
print("  • ⚡ RTXBatchVideoUpscale (Simple)")
print("  • ⚙️  RTXBatchVideoUpscale (Advanced)")
print("  • 📺 VideoReviewAndConfirm (VAE Review → RTX Confirm)")
print("  • 🔊 RTX Audio Muxer (Instant Muxing)")
print("="*60 + "\n")
