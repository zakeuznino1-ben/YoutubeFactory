import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class DriveManager:
    def __init__(self):
        # Konfigurasi Kunci & Akses
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.SERVICE_ACCOUNT_FILE = 'service_account.json'
        
        # Lokasi folder Assets (Tempat bongkar muat)
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ASSETS_DIR = os.path.join(os.path.dirname(self.BASE_DIR), "assets")
        
        # Autentikasi Robot
        self.creds = service_account.Credentials.from_service_account_file(
            os.path.join(self.BASE_DIR, self.SERVICE_ACCOUNT_FILE), 
            scopes=self.SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.creds)

    def download_video(self, filename):
        """
        Mencari file berdasarkan nama di Google Drive (yang sudah di-share ke robot),
        lalu mendownloadnya ke folder assets lokal.
        """
        print(f"[GUDANG] Mencari file '{filename}' di Google Drive...")
        
        # 1. Cari File ID berdasarkan Nama
        results = self.service.files().list(
            q=f"name = '{filename}' and mimeType contains 'video/' and trashed = false",
            pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print(f"[ERROR] File '{filename}' tidak ditemukan di Drive Robot.")
            return False

        # 2. Jika ketemu, ambil ID-nya
        file_id = items[0]['id']
        print(f"[GUDANG] File ditemukan (ID: {file_id}). Mulai download...")

        # 3. Proses Download
        request = self.service.files().get_media(fileId=file_id)
        destination_path = os.path.join(self.ASSETS_DIR, filename)
        
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"   -> Downloading {int(status.progress() * 100)}% ...")

        print(f"[SUKSES] File mendarat di: {destination_path}")
        return True

# --- TEST AREA (Bisa dijalankan langsung untuk cek koneksi) ---
if __name__ == "__main__":
    gudang = DriveManager()
    # Ganti 'nama_video_di_drive.mp4' dengan nama file yang barusan Anda share
    # Contoh: gudang.download_video('clip_A.mp4')
    print("Sistem Gudang Siap. Panggil fungsi download_video() untuk mengetes.")