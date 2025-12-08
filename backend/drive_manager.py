import os
import io
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class DriveManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.SERVICE_ACCOUNT_FILE = 'service_account.json'
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ASSETS_DIR = os.path.join(os.path.dirname(self.BASE_DIR), "assets")
        
        self.creds = service_account.Credentials.from_service_account_file(
            os.path.join(self.BASE_DIR, self.SERVICE_ACCOUNT_FILE), 
            scopes=self.SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.creds)

    def download_folder(self, folder_name):
        """
        Mencari folder di Drive, lalu mendownload SEMUA video di dalamnya.
        Mengembalikan list path video lokal.
        """
        print(f"[GUDANG] Mencari folder playlist '{folder_name}'...")
        
        # 1. Cari ID Folder
        q_folder = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=q_folder, pageSize=1, fields="files(id, name)").execute()
        folders = results.get('files', [])

        if not folders:
            print(f"[ERROR] Folder '{folder_name}' tidak ditemukan.")
            return []

        folder_id = folders[0]['id']
        
        # 2. Buat Folder Lokal
        local_folder = os.path.join(self.ASSETS_DIR, folder_name)
        os.makedirs(local_folder, exist_ok=True)

        # 3. List Semua Video di Folder Itu
        q_files = f"'{folder_id}' in parents and mimeType contains 'video/' and trashed = false"
        results = self.service.files().list(q=q_files, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        downloaded_files = []

        if not files:
            print(f"[GUDANG] Folder '{folder_name}' kosong!")
            return []

        print(f"[GUDANG] Menemukan {len(files)} video dalam playlist.")

        # 4. Download Satu per Satu
        for file in files:
            file_id = file['id']
            file_name = file['name']
            destination = os.path.join(local_folder, file_name)
            
            if not os.path.exists(destination):
                print(f"   -> Mendownload: {file_name}...")
                request = self.service.files().get_media(fileId=file_id)
                fh = io.FileIO(destination, 'wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                print(f"   [OK] {file_name} Tersimpan.")
            else:
                print(f"   [SKIP] {file_name} sudah ada.")
            
            downloaded_files.append(destination)
            
        return downloaded_files

# Test Area
if __name__ == "__main__":
    dm = DriveManager()
    # dm.download_folder("playlist_natal")