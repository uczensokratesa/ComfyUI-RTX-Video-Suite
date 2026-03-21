import os
import cv2
import urllib.parse
from aiohttp import web
from server import PromptServer
WEB_DIRECTORY = "./web/js"

class RTXVideoPlayer:
    """
    Passive Video Player for ComfyUI.
    Takes a path, displays the video in the UI, and passes the path forward.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {"forceInput": True, "tooltip": "Path to the video file"}),
                "autoplay": ("BOOLEAN", {"default": True}),
                "loop": ("BOOLEAN", {"default": True}),
                "mute": ("BOOLEAN", {"default": True, "tooltip": "Browsers may block autoplay if not muted"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    FUNCTION = "show_video"
    CATEGORY = "RTX Video Suite"
    OUTPUT_NODE = True

    def show_video(self, video_path, autoplay, loop, mute, unique_id):
        node_id = str(unique_id)

        if not os.path.exists(video_path):
            print(f"❌ [RTX Player] Video not found at: {video_path}")
            return (video_path,)

        # Pobieranie metadanych (jak w Pickerze)
        info_text = "Metadata unavailable"
        try:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                
                size_mb = os.path.getsize(video_path) / (1024 * 1024)
                duration = frames / fps if fps > 0 else 0
                info_text = f"{w}x{h} | {fps:.2f} FPS | {duration:.1f}s | {size_mb:.1f} MB"
        except Exception as e:
            print(f"⚠️ [RTX Player] Could not read metadata: {e}")

        # Przygotowanie bezpiecznego URL dla frontendu
        safe_path = urllib.parse.quote(video_path)
        video_url = f"/rtx_viewer/play?path={safe_path}"

        # Wysyłamy sygnał do przeglądarki (JavaScript)
        PromptServer.instance.send_sync("rtx_play_video", {
            "node_id": node_id,
            "video_url": video_url,
            "autoplay": autoplay,
            "loop": loop,
            "mute": mute,
            "info": info_text
        })

        print(f"📺 [RTX Player] Displaying video in UI: {os.path.basename(video_path)}")
        
        # Oddajemy ścieżkę dalej, by nie blokować łańcucha
        return (video_path,)

# ====================== API ROUTE ======================
# Endpoint pozwalający ComfyUI odtwarzać pliki z dowolnego folderu (np. z pickera)

@PromptServer.instance.routes.get("/rtx_viewer/play")
async def serve_video_file(request):
    video_path = request.query.get("path")
    if not video_path:
        return web.Response(status=400, text="No path provided")
    
    video_path = urllib.parse.unquote(video_path)
    
    if not os.path.exists(video_path):
        return web.Response(status=404, text="Video not found")

    return web.FileResponse(video_path, headers={
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes", # Ważne dla płynnego przewijania wideo w przeglądarce!
        "Cache-Control": "no-cache"
    })

# Pamiętaj o dodaniu tego do MAPPINGS w swoim __init__.py!
NODE_CLASS_MAPPINGS = {"RTXVideoPlayer": RTXVideoPlayer}
NODE_DISPLAY_NAME_MAPPINGS = {"RTXVideoPlayer": "📺 RTX Video Player"}
