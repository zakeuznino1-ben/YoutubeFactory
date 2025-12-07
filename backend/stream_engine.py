import subprocess
import shlex
import os
import signal

class LiveEngine:
    def __init__(self):
        # DULU: self.process = None (Cuma muat 1)
        # SEKARANG: Dictionary { channel_id: process_object }
        self.active_streams = {} 

    def start_stream(self, video_path, stream_key, channel_id):
        """
        Menyalakan stream dengan FILTER ANTI-COPYRIGHT (Auto-Unique).
        """
        if channel_id in self.active_streams:
            print(f"WARN: Channel {channel_id} sudah aktif. Abaikan perintah.")
            return

        # --- KONFIGURASI FILTER ---
        # 1. eq=contrast=1.03:brightness=0.03 : Sedikit menaikkan kontras & kecerahan
        # 2. noise=alls=1:allf=t+u : Menambahkan noise statis acak (sangat tipis)
        # Efek: Mengubah checksum/hash setiap frame video secara total
        video_filter = "eq=contrast=1.03:brightness=0.03:saturation=1.05,noise=alls=1:allf=t+u"

        command = (
            f"ffmpeg -re -stream_loop -1 -i {video_path} "
            f"-filter_complex \"{video_filter}\" "  ### MAGIC SAUCE DISINI ###
            f"-c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k "
            f"-pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 "
            f"-f flv rtmp://a.rtmp.youtube.com/live2/{stream_key}"
        )
        
        args = shlex.split(command)
        
        try:
            # Menggunakan subprocess.PIPE agar output FFmpeg tidak mengotori terminal utama
            process = subprocess.Popen(
                args, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            self.active_streams[channel_id] = process
            print(f"SUCCESS: Stream Channel {channel_id} ON (PID: {process.pid}) [SECURE MODE]")
            
        except Exception as e:
            print(f"ERROR: Gagal menyalakan stream {channel_id}: {e}")

    def stop_stream(self, channel_id):
        """
        Mematikan stream milik channel tertentu saja.
        """
        # 1. Ambil process dari rak
        process = self.active_streams.get(channel_id)
        
        if process:
            # 2. Matikan Process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill() # Paksa bunuh jika bandel
            
            # 3. Hapus dari catatan
            del self.active_streams[channel_id]
            print(f"INFO: Stream Channel {channel_id} berhasil dimatikan.")
        else:
            print(f"WARN: Tidak ada stream aktif untuk Channel {channel_id}.")

    def is_active(self, channel_id):
        """Cek status spesifik satu channel"""
        return channel_id in self.active_streams