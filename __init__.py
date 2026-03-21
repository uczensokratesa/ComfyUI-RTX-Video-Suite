"""
ComfyUI RTX Video & Audio Suite
Main entry point - registers all nodes from the suite.
"""

# Katalog dla plików JavaScript (Review & Player)
WEB_DIRECTORY = "./web/js"

# 1. Import mapowań z rtx_nodes.py (Upscaling & Path Picker)
from .rtx_nodes import (
    NODE_CLASS_MAPPINGS as RTX_NODES_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as RTX_NODES_DISPLAY
)

# 2. Import mapowań z RTXVideoReview.py (Zmieniony na Review & Go)
from .RTXVideoReview import (
    NODE_CLASS_MAPPINGS as REVIEW_GO_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as REVIEW_GO_DISPLAY
)

# 3. Import mapowań z rtx_audio_muxer.py (Audio Muxing)
from .rtx_audio_muxer import (
    NODE_CLASS_MAPPINGS as MUXER_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as MUXER_DISPLAY
)

# 4. Import mapowań z rtx_video_player.py (Nowy: Passive Player)
from .rtx_video_player import (
    NODE_CLASS_MAPPINGS as PLAYER_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as PLAYER_DISPLAY
)

# --- ŁĄCZENIE WSZYSTKICH MAPOWAŃ (Merging) ---

NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(RTX_NODES_MAPPINGS)
NODE_CLASS_MAPPINGS.update(REVIEW_GO_MAPPINGS)
NODE_CLASS_MAPPINGS.update(MUXER_MAPPINGS)
NODE_CLASS_MAPPINGS.update(PLAYER_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(RTX_NODES_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(REVIEW_GO_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(MUXER_DISPLAY)
NODE_DISPLAY_NAME_MAPPINGS.update(PLAYER_DISPLAY)

__all__ = [
    'NODE_CLASS_MAPPINGS',
    'NODE_DISPLAY_NAME_MAPPINGS',
    'WEB_DIRECTORY'
]

# --- Aktualny Banner Startowy ---
print("\n" + "═" * 70)
print("🚀 RTX Video & Audio Suite - Production v1.1.0 Loaded")
print("═" * 70)
print("  • 📁 NativeVideoPathPicker")
print("  • ⚡ RTXBatchVideoUpscale (Simple & Advanced)")
print("  • 🎬 Video Review & Go (Interactive Pause)")
print("  • 🔊 RTX Audio Muxer (Instant Muxing)")
print("  • 📺 RTX Video Player (Passive UI Viewer)")
print("═" * 70 + "\n")
