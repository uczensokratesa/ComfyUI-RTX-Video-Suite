"""
RTX Video Review & Confirm Node
Shows video player inside the node + Continue / Cancel buttons
"""

import os
import time
import asyncio
from aiohttp import web

try:
    from comfy.server import PromptServer
except ImportError:
    from server import PromptServer

from comfy.model_management import InterruptProcessingException

WEB_DIRECTORY = "./web"

class VideoReviewAndConfirm:
    status_by_id = {}
    video_paths = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae_output": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Connect from VAE Streaming output"
                }),
                "enable_review": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "If enabled, shows video player and waits for user decision"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("clean_video_path",)
    FUNCTION = "execute"
    CATEGORY = "RTX Video Suite"
    OUTPUT_NODE = True

    def execute(self, vae_output, enable_review, unique_id):
        # OPTYMALIZACJA 1: Zawsze wymuszamy string dla ID
        node_id = str(unique_id) 

        # Clean path
        paths = [p.strip() for p in vae_output.replace('\n', ',').split(',')]
        valid = [p for p in paths if p.lower().endswith(('.mp4', '.mov', '.webm', '.mkv', '.avi')) 
                 and '.temp.' not in p.lower()]

        clean_path = valid[-1] if valid else vae_output.strip()

        print(f"🎬 [Review Node] Cleaned path: {clean_path}")

        if not enable_review:
            print("⏭️ [Review Node] Review disabled → passing through")
            return (clean_path,)

        # Save path and notify frontend
        self.video_paths[node_id] = clean_path
        self.status_by_id[node_id] = "waiting"

        PromptServer.instance.send_sync("rtx_review_show_video", {
            "node_id": node_id,
            "video_path": clean_path
        })

        print(f"⏸️ [Review Node] Node {node_id} paused - waiting for user decision...")

        while self.status_by_id.get(node_id) == "waiting":
            time.sleep(0.4)

        # Cleanup memory
        self.video_paths.pop(node_id, None)
        status = self.status_by_id.pop(node_id, None)

        if status == "cancelled":
            print(f"❌ [Review Node] Cancelled by user (node {node_id})")
            raise InterruptProcessingException()

        print(f"▶️ [Review Node] Approved → continuing")
        return (clean_path,)

# ====================== API ======================

@PromptServer.instance.routes.get("/rtx_review/video/{node_id}")
async def serve_video(request):
    node_id = request.match_info["node_id"]
    path = VideoReviewAndConfirm.video_paths.get(node_id)

    # OPTYMALIZACJA 2: Fallback na blokadę pliku (Windows)
    if not path or not os.path.exists(path):
        await asyncio.sleep(0.3)
        path = VideoReviewAndConfirm.video_paths.get(node_id)

    if not path or not os.path.exists(path):
        return web.Response(status=404, text="Video not found")

    return web.FileResponse(path, headers={
        "Content-Type": "video/mp4",
        "Cache-Control": "no-cache"
    })

@PromptServer.instance.routes.post("/rtx_review/continue/{node_id}")
async def api_continue(request):
    node_id = request.match_info["node_id"]
    VideoReviewAndConfirm.status_by_id[node_id] = "continue"
    return web.json_response({"status": "ok"})

@PromptServer.instance.routes.post("/rtx_review/cancel/{node_id}")
async def api_cancel(request):
    node_id = request.match_info["node_id"]
    VideoReviewAndConfirm.status_by_id[node_id] = "cancelled"
    return web.json_response({"status": "ok"})

# Registration
NODE_CLASS_MAPPINGS = {"VideoReviewAndConfirm": VideoReviewAndConfirm}
NODE_DISPLAY_NAME_MAPPINGS = {"VideoReviewAndConfirm": "⏸️ VAE Review → RTX Confirm"}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
