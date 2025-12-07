from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import time
from database import SessionLocal, Channel
# IMPORT BARU: Panggil Robot Gudang
from drive_manager import DriveManager 

class RobotMandor:
    def __init__(self, stream_engine):
        self.engine = stream_engine
        self.scheduler = BackgroundScheduler()
        self.START_HOUR = 8  # Jam Kerja Mulai
        self.END_HOUR = 20   # Jam Kerja Selesai
        
        # Inisialisasi Gudang
        self.gudang = DriveManager()

    def cek_jadwal(self):
        sekarang = datetime.now()
        jam_sekarang = sekarang.hour
        print(f"[MANDOR] Cek Rutin jam {sekarang.strftime('%H:%M:%S')}...")

        db = SessionLocal()
        channels = db.query(Channel).all()
        is_working_hours = self.START_HOUR <= jam_sekarang < self.END_HOUR
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

        for channel in channels:
            if is_working_hours:
                # Cek jika status LIVE tapi mesin mati (atau status OFFLINE)
                if channel.status != "LIVE" or not self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA KERJA! Menyalakan {channel.channel_name}...")
                    
                    # 1. Tentukan Target File
                    filename = channel.video_source if channel.video_source else "test.mp4"
                    video_path = os.path.join(assets_dir, filename)
                    
                    # 2. CEK KETERSEDIAAN FILE (INTEGRASI GUDANG)
                    if not os.path.exists(video_path):
                        print(f"   [STOK KOSONG] File {filename} tidak ada di lokal. Meminta download dari Drive...")
                        
                        # Perintahkan Gudang untuk download
                        sukses_download = self.gudang.download_video(filename)
                        
                        if sukses_download:
                            print(f"   [STOK AMAN] Download selesai. Lanjut streaming.")
                        else:
                            print(f"   [KRITIS] Gagal download dari Drive. Menggunakan video darurat.")
                            video_path = os.path.join(assets_dir, "test.mp4")
                    
                    # 3. Eksekusi Stream
                    fake_key = f"auto-key-{channel.id}"
                    self.engine.start_stream(video_path, fake_key, channel.id)
                    
                    channel.status = "LIVE"
                    db.commit()
            else:
                if channel.status == "LIVE" or self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA TIDUR! Mematikan {channel.channel_name}...")
                    self.engine.stop_stream(channel.id)
                    channel.status = "OFFLINE"
                    db.commit()
        db.close()

    def start(self):
        self.scheduler.add_job(self.cek_jadwal, 'interval', minutes=1)
        self.scheduler.start()
        print("INFO: Robot Mandor V4.2 (Logistics-Aware) sudah aktif.")