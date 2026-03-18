"""
ComfyUI RTX Video Suite - Initialization
This file registers the nodes with ComfyUI.
"""

import sys

# Próbujemy zaimportować mapowania węzłów z naszego głównego pliku logiki
try:
    from .rtx_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    
    # ComfyUI wymaga, aby te dwie zmienne były wyeksportowane w zmiennej __all__
    __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

except ImportError as e:
    print(f"❌ [RTX Video Suite] Błąd ładowania wtyczki: {e}")
    # Zabezpieczenie, aby ComfyUI nie wybuchło, jeśli brakuje pliku rtx_nodes.py
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
    __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
