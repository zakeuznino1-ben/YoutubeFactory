from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from database import SessionLocal, Channel

class RobotMandor:
    def __init__(self, stream_engine):
        self.engine = stream_engine
        self.scheduler = BackgroundScheduler()
        
        # JAM KERJA (Bisa diubah nanti)
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

        for channel in channels:
            # LOGIKA UTAMA MULTI-CHANNEL
            
            if is_working_hours:
                # -- JAM KERJA (HARUS LIVE) --
                # Cek database bilang OFFLINE atau mesin mati
                if channel.status != "LIVE" or not self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA KERJA! Menyalakan {channel.channel_name} (ID: {channel.id})...")
                    
                    # Siapkan Data
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    video_path = os.path.join(base_dir, "assets", "test.mp4")
                    
                    # KUNCI: Gunakan fake key unik per channel
                    fake_key = f"auto-key-{channel.id}"
                    
                    # NYALAKAN MESIN (Kirim channel_id)
                    self.engine.start_stream(video_path, fake_key, channel.id)
                    
                    # Update DB
                    channel.status = "LIVE"
                    db.commit()
            
            else:
                # -- JAM ISTIRAHAT (HARUS MATI) --
                if channel.status == "LIVE" or self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA TIDUR! Mematikan {channel.channel_name} (ID: {channel.id})...")
                    
                    # MATIKAN MESIN (Kirim channel_id)
                    self.engine.stop_stream(channel.id)
                    
                    # Update DB
                    channel.status = "OFFLINE"
                    db.commit()

        db.close()

    def start(self):
        # Tambahkan tugas rutin setiap 1 menit (interval)
        self.scheduler.add_job(self.cek_jadwal, 'interval', minutes=1)
        self.scheduler.start()
        print("INFO: Robot Mandor V4.0 (Multi-Channel) sudah aktif.")