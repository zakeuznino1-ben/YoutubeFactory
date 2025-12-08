from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from database import SessionLocal, Channel
from drive_manager import DriveManager 
from notifier import TelegramNotifier

class RobotMandor:
    def __init__(self, stream_engine):
        self.engine = stream_engine
        self.scheduler = BackgroundScheduler()
        self.START_HOUR = 8  
        self.END_HOUR = 20   
        
        self.gudang = DriveManager()
        self.lapor = TelegramNotifier()

    def cek_jadwal(self):
        sekarang = datetime.now()
        jam_sekarang = sekarang.hour
        print(f"[MANDOR] Cek Rutin jam {sekarang.strftime('%H:%M:%S')}...")

        db = SessionLocal()
        channels = db.query(Channel).all()
        # CATATAN: Karena Business Trip batal, kita bisa set ini 24 jam jika mau.
        # Tapi biarkan logika jam kerja ini dulu (bisa diedit nanti).
        is_working_hours = True # Override agar nyala terus 24 jam (sesuai judul channel)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

        for channel in channels:
            if is_working_hours:
                # Cek jika status LIVE tapi mesin mati
                if channel.status != "LIVE" or not self.engine.is_active(channel.id):
                    print(f"   -> WAKTUNYA KERJA! Menyalakan {channel.channel_name}...")
                    self.lapor.send_message(f"📢 <b>STARTING STREAM (V5.0)</b>\nChannel: {channel.channel_name}\nMode: Playlist Engine")

                    input_name = channel.video_source if channel.video_source else "test.mp4"
                    
                    # LOGIKA BARU V5.0: DETEKSI PLAYLIST vs FILE
                    final_source = None
                    
                    # Cek 1: Apakah ini NAMA FOLDER playlist? (misal: playlist_natal)
                    if "playlist" in input_name.lower():
                        print(f"   [LOGIC] Terdeteksi mode Playlist: {input_name}")
                        # Download satu folder penuh
                        playlist_files = self.gudang.download_folder(input_name)
                        
                        if playlist_files:
                            final_source = playlist_files # Kirim List ke Engine
                            self.lapor.send_message(f"📂 <b>PLAYLIST READY</b>\nFolder: {input_name}\nJumlah: {len(playlist_files)} Video.")
                        else:
                            print(f"   [ERROR] Playlist kosong/gagal.")
                    
                    # Cek 2: Jika bukan playlist, perlakukan sebagai FILE BIASA
                    if not final_source:
                        video_path = os.path.join(assets_dir, input_name)
                        if not os.path.exists(video_path):
                            self.lapor.send_message(f"📦 <b>STOK KOSONG</b>\nFile: {input_name}\nAction: Download Single File...")
                            if self.gudang.download_video(input_name):
                                final_source = video_path
                        else:
                            final_source = video_path

                    # EKSEKUSI JIKA SOURCE ADA
                    if final_source:
                        real_key = channel.channel_id
                        self.engine.start_stream(final_source, real_key, channel.id)
                        
                        if self.engine.is_active(channel.id):
                            self.lapor.send_message(f"✅ <b>STREAM LIVE</b>\nChannel: {channel.channel_name}")
                            channel.status = "LIVE"
                            db.commit()
                    else:
                        self.lapor.send_message(f"⚠️ <b>GAGAL TOTAL</b>\nTidak ada file/playlist yang bisa diputar.")

            else:
                # Logika Stop (Jika di luar jam kerja)
                if channel.status == "LIVE":
                    self.engine.stop_stream(channel.id)
                    channel.status = "OFFLINE"
                    db.commit()
        db.close()

    def start(self):
        self.scheduler.add_job(self.cek_jadwal, 'interval', minutes=1)
        self.scheduler.start()
        self.lapor.send_message("🏭 <b>SYSTEM V5.0 ONLINE</b>\nUpgrade: Playlist Engine & Folder Support.\nSiap bertugas.")
        print("INFO: Robot Mandor V5.0 (Playlist-Aware) sudah aktif.")