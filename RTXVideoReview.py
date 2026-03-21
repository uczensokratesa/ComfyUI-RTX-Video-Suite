"""
RTX Video Review & Go
Universal node to preview video and decide whether to continue the workflow.
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

class RTXVideoReviewGo:
    status_by_id = {}
    video_paths = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Input path of the video to review"
                }),
                "enable_review": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "If enabled, pauses workflow to show the video player"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    FUNCTION = "execute"
    CATEGORY = "RTX Video Suite"
    OUTPUT_NODE = True

    def execute(self, video_path, enable_review, unique_id):
        node_id = str(unique_id) 

        # Logika czyszczenia ścieżki (obsługa batch/vae streaming)
        paths = [p.strip() for p in video_path.replace('\n', ',').split(',')]
        valid = [p for p in paths if p.lower().endswith(('.mp4', '.mov', '.webm', '.mkv', '.avi')) 
                 and '.temp.' not in p.lower()]

        clean_path = valid[-1] if valid else video_path.strip()

        if not enable_review:
            print(f"⏭️ [Review Go] Review disabled → Passing: {os.path.basename(clean_path)}")
            return (clean_path,)

        # Rejestracja ścieżki i pauza
        self.video_paths[node_id] = clean_path
        self.status_by_id[node_id] = "waiting"

        PromptServer.instance.send_sync("rtx_show_review_player", {
            "node_id": node_id,
            "video_path": clean_path
        })

        print(f"⏸️ [Review Go] Node {node_id} paused - waiting for approval...")

        while self.status_by_id.get(node_id) == "waiting":
            time.sleep(0.4)

        # Cleanup i decyzja
        self.video_paths.pop(node_id, None)
        status = self.status_by_id.pop(node_id, None)

        if status == "cancelled":
            print(f"❌ [Review Go] Workflow cancelled by user at node {node_id}")
            raise InterruptProcessingException()

        print(f"▶️ [Review Go] Video approved → Continuing workflow")
        return (clean_path,)

# ====================== API ROUTES ======================

@PromptServer.instance.routes.get("/rtx_review/video/{node_id}")
async def serve_video(request):
    node_id = request.match_info["node_id"]
    path = RTXVideoReviewGo.video_paths.get(node_id)

    if not path or not os.path.exists(path):
        await asyncio.sleep(0.3)
        path = RTXVideoReviewGo.video_paths.get(node_id)

    if not path or not os.path.exists(path):
        return web.Response(status=404, text="Video file not found")

    return web.FileResponse(path, headers={
        "Content-Type": "video/mp4",
        "Cache-Control": "no-cache"
    })

@PromptServer.instance.routes.post("/rtx_review/continue/{node_id}")
async def api_continue(request):
    node_id = request.match_info["node_id"]
    RTXVideoReviewGo.status_by_id[node_id] = "continue"
    return web.json_response({"status": "ok"})

@PromptServer.instance.routes.post("/rtx_review/cancel/{node_id}")
async def api_cancel(request):
    node_id = request.match_info["node_id"]
    RTXVideoReviewGo.status_by_id[node_id] = "cancelled"
    return web.json_response({"status": "ok"})

# MAPPINGS
NODE_CLASS_MAPPINGS = {"RTXVideoReviewGo": RTXVideoReviewGo}
NODE_DISPLAY_NAME_MAPPINGS = {"RTXVideoReviewGo": "🎬 Video Review & Go"}
