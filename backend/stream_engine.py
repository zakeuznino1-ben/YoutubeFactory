import subprocess
import os
import signal
import sys

class StreamEngine:
    def __init__(self):
        self.active_streams = {}
        # URL Server YouTube (Primary)
        self.RTMP_URL = "rtmp://a.rtmp.youtube.com/live2"

    def generate_concat_file(self, video_paths, channel_id):
        """
        Membuat file playlist.txt untuk FFmpeg agar bisa memutar banyak video tanpa jeda.
        """
        list_path = os.path.join(os.path.dirname(video_paths[0]), f"playlist_{channel_id}.txt")
        
        with open(list_path, 'w', encoding='utf-8') as f:
            for video in video_paths:
                # Format FFmpeg: file 'path/to/video.mp4'
                # Escape backslash untuk Windows
                safe_path = video.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")
        
        return list_path

    def start_stream(self, video_source, stream_key, channel_id):
        """
        Menyalakan Stream.
        video_source: Bisa berupa PATH (String) atau LIST OF PATHS (List).
        """
        if channel_id in self.active_streams:
            print(f"[ENGINE] Channel {channel_id} sedang jalan. Restarting...")
            self.stop_stream(channel_id)

        print(f"[ENGINE] Menyalakan Channel {channel_id}...")

        # LOGIKA PLAYLIST V5.0
        # Jika input berupa List (Playlist), buat file concat.
        if isinstance(video_source, list):
            input_file = self.generate_concat_file(video_source, channel_id)
            # -f concat -safe 0 -stream_loop -1 -i playlist.txt
            input_cmd = ["-f", "concat", "-safe", "0", "-stream_loop", "-1", "-i", input_file]
            print(f"[ENGINE] Mode Playlist Aktif: {len(video_source)} Video.")
        else:
            # Mode Single File (Legacy)
            input_file = video_source
            input_cmd = ["-stream_loop", "-1", "-i", input_file]
            print(f"[ENGINE] Mode Single Loop Aktif.")

        # COMMAND FFmpeg "OBAT KUAT" (Anti-Copyright & Stable)
        command = [
            "ffmpeg",
            "-re",
            *input_cmd,
            "-vf", "eq=brightness=0.0:saturation=1.1,unsharp=3:3:1.0", # Filter Manipulasi Pixel
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", "3000k",
            "-maxrate", "3000k",
            "-bufsize", "6000k",
            "-pix_fmt", "yuv420p",
            "-g", "60",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
            f"{self.RTMP_URL}/{stream_key}"
        ]

        # Eksekusi di Background
        process = subprocess.Popen(
            command, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        self.active_streams[channel_id] = process
        print(f"SUCCESS: Stream Channel {channel_id} ON (PID: {process.pid}) [PLAYLIST MODE]")
        return True

    def stop_stream(self, channel_id):
        if channel_id in self.active_streams:
            process = self.active_streams[channel_id]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.active_streams[channel_id]
            print(f"STOPPED: Channel {channel_id}")
            return True
        return False

    def is_active(self, channel_id):
        if channel_id in self.active_streams:
            if self.active_streams[channel_id].poll() is None:
                return True
            else:
                del self.active_streams[channel_id] 
        return False