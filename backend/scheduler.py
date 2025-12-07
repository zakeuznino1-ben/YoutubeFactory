from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from database import SessionLocal, Channel

class RobotMandor:
    def __init__(self, stream_engine):
        self.engine = stream_engine
        self.scheduler = BackgroundScheduler()
        
        # JAM KERJA
        self.START_HOUR = 8  # Jam 8 Pagi
        self.END_HOUR = 20   # Jam 8 Malam

    def cek_jadwal(self):
        """
        Fungsi ini akan dijalankan setiap 1 menit.
        """
        sekarang = datetime.now()
        jam_sekarang = sekarang.hour
        print(f"[MANDOR] Cek Rutin jam {sekarang.strftime('%H:%M:%S')}...")

        # Buka koneksi database sebentar
        db = SessionLocal()
        channels = db.query(Channel).all()

        # Tentukan apakah ini JAM KERJA?
        is_working_hours = self.START_HOUR <= jam_sekarang < self.END_HOUR
        
        # Cari Base Directory (agar path video akurat)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

        for channel in channels:
            # LOGIKA UTAMA MULTI-CHANNEL & CONTENT-AWARE
            
            if is_working_hours:
                # -- JAM KERJA (HARUS LIVE) --
                # Cek database bilang OFFLINE atau mesin mati
                if channel.status != "LIVE" or not self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA KERJA! Menyalakan {channel.channel_name} (ID: {channel.id})...")
                    
                    # --- UPDATE PENTING DISINI ---
                    # 1. Ambil nama file dari Database
                    filename = channel.video_source if channel.video_source else "test.mp4"
                    
                    # 2. Susun Path Lengkap
                    video_path = os.path.join(assets_dir, filename)
                    
                    # 3. Cek apakah file ada? Kalau tidak, pakai default
                    if not os.path.exists(video_path):
                        print(f"   [WARN] File {filename} hilang! Pakai test.mp4.")
                        video_path = os.path.join(assets_dir, "test.mp4")
                    # -----------------------------
                    
                    # Gunakan fake key unik per channel
                    fake_key = f"auto-key-{channel.id}"
                    
                    # NYALAKAN MESIN
                    self.engine.start_stream(video_path, fake_key, channel.id)
                    
                    # Update DB
                    channel.status = "LIVE"
                    db.commit()
            
            else:
                # -- JAM ISTIRAHAT (HARUS MATI) --
                if channel.status == "LIVE" or self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA TIDUR! Mematikan {channel.channel_name} (ID: {channel.id})...")
                    
                    self.engine.stop_stream(channel.id)
                    
                    channel.status = "OFFLINE"
                    db.commit()

        db.close()

    def start(self):
        self.scheduler.add_job(self.cek_jadwal, 'interval', minutes=1)
        self.scheduler.start()
        print("INFO: Robot Mandor V4.1 (Content-Aware) sudah aktif.")