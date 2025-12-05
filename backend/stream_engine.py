import subprocess
import os
import signal

# Ini adalah Class untuk mengontrol FFmpeg
class LiveEngine:
    def __init__(self):
        self.process = None # Menyimpan ID proses yang sedang jalan

    def start_stream(self, video_path, stream_key):
        """
        Fungsi untuk menyalakan Streaming.
        video_path: Lokasi file video (assets/test.mp4)
        stream_key: Kunci rahasia dari YouTube Studio
        """
        
        # Cek apakah file video ada?
        if not os.path.exists(video_path):
            print(f"ERROR: File video tidak ditemukan di {video_path}")
            return False

        # Merakit Perintah FFmpeg (Resep Rahasia V3.0)
        # Kita pakai mode 'loop' (-stream_loop -1) agar video berputar terus 24 jam
        command = [
            'ffmpeg',
            '-re',                      # Baca input sesuai kecepatan asli (Native Framerate)
            '-stream_loop', '-1',       # Loop selamanya (Infinite)
            '-i', video_path,           # Input file
            '-c:v', 'libx264',          # Video Codec: H.264
            '-preset', 'veryfast',      # Preset cepat agar CPU hemat
            '-b:v', '3000k',            # Bitrate Video (3000 Kbps - Standar HD)
            '-maxrate', '3000k',
            '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p',
            '-g', '50',                 # Keyframe interval (Wajib 2 detik untuk Youtube)
            '-c:a', 'aac',              # Audio Codec
            '-b:a', '128k',             # Bitrate Audio
            '-ar', '44100',
            '-f', 'flv',                # Format FLV (Wajib untuk RTMP)
            f'rtmp://a.rtmp.youtube.com/live2/{stream_key}' # Alamat Youtube
        ]

        print("INFO: Memulai FFmpeg Engine...")
        
        # Eksekusi perintah di background (subprocess)
        # Kita gunakan Popen agar Python tidak macet menunggu video selesai
        self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"SUCCESS: Stream berjalan dengan PID {self.process.pid}")
        return True

    def stop_stream(self):
        """Fungsi untuk mematikan Streaming"""
        if self.process:
            print("INFO: Mematikan Stream...")
            self.process.terminate() # Kirim sinyal berhenti
            self.process.wait()      # Pastikan benar-benar mati
            self.process = None
            print("SUCCESS: Stream Offline.")
        else:
            print("INFO: Tidak ada stream yang aktif.")

# Kode di bawah ini hanya jalan kalau file ini dijalankan langsung (untuk Tes Manual)
if __name__ == "__main__":
    # SETUP MANUAL UNTUK TES
    # Ganti 'KEY_YOUTUBE_ANDA' dengan Stream Key asli jika mau tes live
    KEY_PALSU = "abcd-1234-efgh-5678" 
    
    # Mencari lokasi file test.mp4 otomatis
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VIDEO_FILE = os.path.join(BASE_DIR, "assets", "test.mp4")

    engine = LiveEngine()
    
    # Coba nyalakan
    try:
        engine.start_stream(VIDEO_FILE, KEY_PALSU)
        input("Tekan ENTER untuk mematikan stream tes ini...")
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop_stream()