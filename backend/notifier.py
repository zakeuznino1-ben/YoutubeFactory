import requests
import datetime

class TelegramNotifier:
    def __init__(self):
        # --- DATA RAHASIA (JANGAN DI-PUSH KE GITHUB) ---
        self.TOKEN = "8423476587:AAExuNZLZEWOymrHG6D8vjT95Phh82Surcc"
        self.CHAT_ID = "1336983495"
        # -----------------------------------------------
        
    def send_message(self, message):
        """Mengirim pesan teks ke Telegram Supervisor."""
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M")
            # Format Pesan: Icon + Waktu + Isi
            text = f"🤖 <b>[LAPORAN - {timestamp}]</b>\n\n{message}"
            
            url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
            data = {
                "chat_id": self.CHAT_ID, 
                "text": text, 
                "parse_mode": "HTML" # Agar bisa tebal/miring
            }
            
            requests.post(url, data=data, timeout=5)
            print(f"[NOTIFIER] Laporan terkirim ke Supervisor.")
            return True
        except Exception as e:
            print(f"[ERROR] Gagal lapor Supervisor: {e}")
            return False

# --- TEST AREA ---
if __name__ == "__main__":
    bot = TelegramNotifier()
    bot.send_message("Halo Bos! Supervisor @SupervisorYTbenBot siap memantau pabrik. 🚀")