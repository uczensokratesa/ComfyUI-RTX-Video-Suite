# 🎬 ComfyUI RTX Video Suite (Bulletproof Edition)

Upscaling long videos in ComfyUI finally works exactly as it should. No out-of-memory (OOM) crashes, no killing your SSD with thousands of temporary PNG files, and no silent freezes after 4 hours of rendering.

This suite wraps NVIDIA's MAXINE Video Super Resolution (VSR) SDK into a **bulletproof, production-ready pipeline**. It features true streaming, real non-blocking I/O, and an architecture designed to survive extreme workloads.

## 🌟 Why does this exist?
Most video nodes in ComfyUI do one of two things:
1. They load the entire video into RAM at once (Instant OOM).
2. They save every single processed frame to your hard drive before using FFmpeg to stitch them together (Terrible for SSD lifespan and painfully slow).

**This suite does neither.** It uses a highly optimized *Producer-Consumer* architecture. Frames are read in chunks, processed on your RTX GPU, and the raw RGB bytes are streamed **directly into FFmpeg's memory pipe**. Zero temporary files. Pure speed.

## ✨ Features

* **🛡️ Bulletproof Pipeline:** Hardware-level I/O handling (`os.write`), EINTR resistance, and watchdog threads. If FFmpeg chokes, the GPU waits (True Backpressure). It simply does not crash.
* **💾 Zero Disk I/O:** Frames go from GPU memory straight to the encoder.
* **🖱️ Native Drag & Drop:** A custom Video Path Picker node that supports ComfyUI's native drag-and-drop, but outputs a clean `STRING` path to save your RAM.
* **🎵 Audio Muxing:** Automatically preserves and muxes all original audio and subtitle streams without lossy re-encoding.
* **🖥️ Standalone CLI:** Don't want to open ComfyUI? Run the script directly from your terminal with a beautiful progress bar.

## 🛠️ Prerequisites

You must have an **NVIDIA RTX GPU** and the Maxine VSR SDK installed.

1. Windows: Install the [NVIDIA Video Codec SDK / MAXINE-VFX-SDK](https://github.com/NVIDIA/MAXINE-VFX-SDK).
2. Ensure you have the `nvvfx` Python module available in your ComfyUI environment.
3. **FFmpeg** must be installed and available in your system's PATH.

## 📦 Installation

Navigate to your ComfyUI `custom_nodes` folder and clone this repository:

```bash
cd ComfyUI/custom_nodes
git clone [https://github.com/uczensokratesa/ComfyUI-RTX-Video-Suite.git](https://github.com/uczensokratesa/ComfyUI-RTX-Video-Suite.git)
(Restart ComfyUI after installation).
🧩 The Nodes
1. 🎥 Video Path Picker (Drag & Drop)
Standard Load Video nodes output heavy IMAGE tensors. This node looks identical, allows you to drag & drop videos into it, but smartly outputs the video_path string. This keeps your RAM completely empty before processing starts.

2. 🎬 RTX Batch Upscale (Simple)
The streamlined version. Plug in your video path, choose your scale factor (e.g., 2.0x), select the quality, and hit Queue. It handles the naming, folder creation, and audio muxing automatically.

3. ⚙️ RTX Batch Upscale (Advanced)
For power users. Take full control over the FFmpeg crf quality, specific target resolutions, chunk sizes, and batch sizes to perfectly balance your VRAM usage.

4. ⏸️ VAE Review → RTX Confirm (Interactive Checkpoint)
The ultimate "Human-in-the-loop" bridge. This node acts as a smart gatekeeper between your VAE video generation and the heavy upscaling process. It ensures you never waste hours upscaling a "dud" generation.

Smart Path Sanitization: Automatically cleans messy output strings from VAE Streaming or Video Combine nodes, extracting the exact file path needed for the next step.

Integrated Video Player: Uses high-performance addDOMWidget technology to embed a native HTML5 video player directly onto the node. Watch your generation with full playback controls before committing.

Workflow Synchronization: Pauses the entire ComfyUI execution thread, waiting for your manual "Go" or "Cancel".

Automation-Friendly: Includes an enable_review toggle. Turn it OFF for unattended 24/7 batch processing (where it acts as a silent path cleaner), or ON when you want to curate the results personally.

5. 🔊 RTX Audio Muxer (Instant)
**Fastest way to combine audio with your upscaled video.** This node uses FFmpeg "stream copying" technology to inject audio into a video file in milliseconds, without re-encoding the video (preserving 100% of the RTX Upscale quality).

* **Inputs:**
    * `video_path`: Path to your upscaled MP4 file.
    * `audio`: (Optional) Connect raw AUDIO tensors (e.g., from Audio Separator or Load Audio).
    * `audio_path`: (Optional) Provide a direct path to an existing .mp3 or .wav file.
* **Features:**
    * **Instant Muxing:** No video re-rendering (uses `-c:v copy`).
    * **Audio Delay/Advance:** Precisely sync audio with video (±10 seconds).
    * **Volume Control:** Boost or lower audio levels (0x to 10x).
    * **Auto-Cleanup:** Automatically manages temporary files generated from audio tensors.
    * **Organization:** Saves final files in a dedicated `output/rtx_muxed` folder with timestamps.
> [!IMPORTANT]
> **FFmpeg is required** for the RTX Audio Muxer node. 
> Ensure FFmpeg is installed and added to your system's PATH. 
> You can check this by typing `ffmpeg -version` in your terminal.


💻 CLI Usage (Standalone)
This suite doubles as a standalone Python script!

Bash
# Basic 2x Upscale
python rtx_nodes.py -i input.mp4 -o output.mp4 -s 2.0 -q ULTRA

# Advanced: Custom batch size and disable audio muxing
python rtx_nodes.py -i input.mp4 -o output.mp4 -s 2.0 -b 8 --no-audio
🤝 Credits: The "AI Ensemble"
This codebase is the result of a unique collaboration between a human architect and a choir of AI models:

Claude: UI/UX design, ComfyUI node structuring, and elegant fallback mechanics.

Gemini: Pipeline architecture, FFmpeg stdin piping, and Producer-Consumer queue integration.

Grok: Low-level OS I/O hardening, partial write resistance, and VFR/FPS preservation.

GPT: Deadlock prevention, watchdog threads, and robust audio stream mapping.
