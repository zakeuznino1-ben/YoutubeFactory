import requests
import datetime

class TelegramNotifier:
    def __init__(self):
        # --- KONFIGURASI RAHASIA ---
        # GANTI DENGAN DATA DARI BOTFATHER & USERINFOBOT
        self.TOKEN = 8423476587:AAExuNZLZEWOymrHG6D8vjT95Phh82Surcc
        self.CHAT_ID = 1336983495
        # ---------------------------
        
    def send_message(self, message):
        """Mengirim pesan teks ke Telegram Bos."""
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            text = f"🤖 [Laporan Mandor - {timestamp}]\n\n{message}"
            
            url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
            data = {"chat_id": self.CHAT_ID, "text": text}
            
            requests.post(url, data=data, timeout=5)
            print(f"[NOTIFIER] Pesan terkirim: {message}")
            return True
        except Exception as e:
            print(f"[ERROR] Gagal lapor bos: {e}")
            return False

# --- TEST AREA ---
if __name__ == "__main__":
    bot = TelegramNotifier()
    bot.send_message("Halo Bos! Sistem Notifikasi Youtube Factory sudah aktif. 🚀")