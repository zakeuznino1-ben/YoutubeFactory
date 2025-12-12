from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import glob  # <--- LIBRARY BARU (Untuk Scan Folder Lokal)
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
        # print(f"[MANDOR] Cek Rutin jam {sekarang.strftime('%H:%M:%S')}...") 

        db = SessionLocal()
        channels = db.query(Channel).all()
        
        # Override agar nyala terus 24 jam
        is_working_hours = True 
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

        for channel in channels:
            if is_working_hours:
                # Cek jika status LIVE tapi mesin mati
                if channel.status == "LIVE": 
                    if not self.engine.is_active(channel.id):
                        print(f"   -> 🚨 WAKTUNYA KERJA! Menyalakan {channel.channel_name}...")
                        self.lapor.send_message(f"📢 <b>STARTING STREAM (V5.6)</b>\nChannel: {channel.channel_name}\nMode: Hybrid Scan")

                        input_name = channel.video_source if channel.video_source else "test.mp4"
                        final_source = None
                        
                        # --- LOGIKA BARU V5.6: HYBRID SCAN (CLOUD + LOCAL) ---
                        
                        # Cek 1: Apakah ini Playlist?
                        if "playlist" in input_name.lower():
                            # A. Langkah Cloud: Cek & Download dari Drive (Sama seperti V5.5)
                            # Ini penting agar jika ada file dari Mac/HP tetap masuk
                            self.gudang.download_folder(input_name)
                            
                            # B. Langkah Local: SCAN ISI FOLDER PC (Ini tambahannya!)
                            # Mandor menghitung ulang semua file .mp4 yang ada di folder komputer
                            local_playlist_path = os.path.join(assets_dir, input_name)
                            
                            # Cari semua file berakhiran .mp4 di dalam folder itu
                            all_files = glob.glob(os.path.join(local_playlist_path, "*.mp4"))
                            
                            if all_files:
                                final_source = all_files # Override source dengan data real di PC
                                jumlah_video = len(all_files)
                                print(f"   [HYBRID] Total Video ditemukan di PC: {jumlah_video}")
                                self.lapor.send_message(f"📂 <b>PLAYLIST UPDATE</b>\nSource: {input_name}\nTotal: {jumlah_video} Video (Siap Putar).")
                            else:
                                print(f"   [ERROR] Folder playlist lokal kosong.")
                        
                        # Cek 2: Single File (Logika Lama V5.5 Tetap Ada)
                        if not final_source:
                            video_path = os.path.join(assets_dir, input_name)
                            # Cek apakah file ada, jika tidak, coba download
                            if not os.path.exists(video_path):
                                self.lapor.send_message(f"📦 <b>STOK KOSONG</b>\nFile: {input_name}\nAction: Download Single File...")
                                if self.gudang.download_video(input_name):
                                    final_source = video_path
                            else:
                                final_source = video_path

                        # EKSEKUSI JIKA SOURCE ADA
                        if final_source:
                            # Menggunakan 'youtube_id' (Fix V5.5 dipertahankan)
                            real_key = channel.youtube_id 
                            
                            self.engine.start_stream(final_source, real_key, channel.id)
                            
                            if self.engine.is_active(channel.id):
                                self.lapor.send_message(f"✅ <b>STREAM LIVE</b>\nChannel: {channel.channel_name}")
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
        self.scheduler.add_job(self.cek_jadwal, 'interval', seconds=30)
        self.scheduler.start()
        self.lapor.send_message("🏭 <b>SYSTEM V5.6 ONLINE</b>\nUpgrade: Hybrid Scan (Local+Cloud).\nSiap bertugas.")
        print("INFO: Robot Mandor V5.6 (Hybrid Scan) sudah aktif.")