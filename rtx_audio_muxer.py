import os
import subprocess
import torch
import torchaudio
import folder_paths
import uuid
from datetime import datetime

class RTXAudioMuxer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "forceInput": True, 
                    "tooltip": "Path to the source video file (Must be a saved file, not raw IMAGE tensors)"
                }),
                "filename_prefix": ("STRING", {
                    "default": "RTX_Muxed",
                    "tooltip": "Prefix for the output file. Timestamp will be added automatically."
                }),
                "audio_volume": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 10.0, 
                    "step": 0.1,
                    "tooltip": "1.0 is original volume. 2.0 is double volume, 0.5 is half."
                }),
                "audio_delay_sec": ("FLOAT", {
                    "default": 0.0, 
                    "min": -10.0, 
                    "max": 10.0, 
                    "step": 0.05,
                    "tooltip": "Positive values delay the audio. Negative values advance the audio."
                }),
            },
            "optional": {
                "audio": ("AUDIO", {
                    "tooltip": "Connect raw AUDIO output from nodes like Audio Separator"
                }),
                "audio_path": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Or connect a string path to an existing audio file"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("final_video_path",)
    FUNCTION = "mux_audio"
    CATEGORY = "RTX Video Suite"
    OUTPUT_NODE = True

    def mux_audio(self, video_path, filename_prefix, audio_volume, audio_delay_sec, audio=None, audio_path=None):
        # 1. VALIDATE VIDEO INPUT
        if not video_path or not os.path.exists(video_path):
            print(f"❌ [RTX Muxer] Video file not found: {video_path}")
            return (video_path,)

        output_dir = folder_paths.get_output_directory()
        # Create a dedicated subfolder to keep things organized
        mux_dir = os.path.join(output_dir, "rtx_muxed")
        os.makedirs(mux_dir, exist_ok=True)

        temp_audio_file = None
        final_audio_input = None

        # 2. RESOLVE AUDIO INPUT
        if audio is not None:
            print("🔊 [RTX Muxer] Processing raw AUDIO tensor from node...")
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            
            temp_audio_file = os.path.join(mux_dir, f"temp_audio_{uuid.uuid4().hex}.wav")
            
            if len(waveform.shape) > 2: 
                waveform = waveform[0]
            
            torchaudio.save(temp_audio_file, waveform, sample_rate)
            final_audio_input = temp_audio_file
            
        elif audio_path is not None and os.path.exists(audio_path):
            print(f"🔊 [RTX Muxer] Using audio file from path: {audio_path}")
            final_audio_input = audio_path
        
        else:
            print("⚠️ [RTX Muxer] No valid audio input provided. Passing video through untouched.")
            return (video_path,)

        # 3. GENERATE UNIQUE FILENAME
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_prefix = filename_prefix.strip() if filename_prefix.strip() else "Video"
        output_filename = f"{clean_prefix}_{timestamp}.mp4"
        final_output_path = os.path.join(mux_dir, output_filename)

        # 4. BUILD FFMPEG COMMAND
        cmd = ['ffmpeg', '-y']

        # Handle Audio Delay (Negative delay means we offset the video instead)
        if audio_delay_sec > 0:
            cmd.extend(['-itsoffset', str(audio_delay_sec)])
            cmd.extend(['-i', video_path, '-i', final_audio_input])
        elif audio_delay_sec < 0:
            cmd.extend(['-i', video_path])
            cmd.extend(['-itsoffset', str(abs(audio_delay_sec))])
            cmd.extend(['-i', final_audio_input])
        else:
            cmd.extend(['-i', video_path, '-i', final_audio_input])

        # Core encoding parameters
        cmd.extend([
            '-c:v', 'copy',  # INSTANT video stream copy
            '-c:a', 'aac',   # Universal audio format
            '-map', '0:v:0', # Map video from 1st input
            '-map', '1:a:0', # Map audio from 2nd input
            '-shortest'      # Cut to the shortest stream
        ])

        # Handle Audio Volume
        if audio_volume != 1.0:
            cmd.extend(['-filter:a', f'volume={audio_volume}'])

        cmd.append(final_output_path)

        # 5. EXECUTE AND CLEANUP
        try:
            print(f"🚀 [RTX Muxer] Muxing to: {output_filename}")
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ [RTX Muxer] Success! Saved to: {final_output_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ [RTX Muxer] FFmpeg Error: {e.stderr.decode()}")
            final_output_path = video_path # Fallback to original video on failure
        finally:
            if temp_audio_file and os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)

        return (final_output_path,)

# ══════════════════════════════════════════════════════════════════════
#  MAPPINGS
# ══════════════════════════════════════════════════════════════════════

NODE_CLASS_MAPPINGS = {
    "RTXAudioMuxer": RTXAudioMuxer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RTXAudioMuxer": "🔊 RTX Audio Muxer (Instant)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
