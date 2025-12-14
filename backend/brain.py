import google.generativeai as genai
import os

# --- KONFIGURASI ---
# PENTING: SAAT DI GITHUB, BIARKAN INI KOSONG/PLACEHOLDER.
# ISI MANUAL SAAT DI PC PRODUKSI AGAR TIDAK BOCOR.
API_KEY = "TEMPEL_API_KEY_GOOGLE_DISINI_SAAT_DI_PC" 

if API_KEY == "TEMPEL_API_KEY_GOOGLE_DISINI_SAAT_DI_PC":
    # Cek environment variable jika ada (opsional)
    API_KEY = os.getenv("GEMINI_API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)

def ask_gemini(tema):
    """Meminta Gemini membuatkan Naskah Storytelling V4.5 (Viral Hook)"""
    print(f"🧠 [BRAIN V4.5] Merancang naskah viral tema '{tema}'...")
    
    # Pilih Model Terbaik
    model_name = 'gemini-2.0-flash-exp' # Coba versi eksperimental jika ada
    # Fallback logic sederhana bisa ditambahkan nanti
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Gunakan Flash yang stabil
        
        # PROMPT V4.5: THE HOOK & STORYTELLER
        prompt = (
            f"Bertindaklah sebagai Scriptwriter konten viral TikTok/Shorts. Topik: '{tema}'.\n"
            f"Buatkan naskah cerita pendek (Bahasa Indonesia) dengan struktur ini:\n"
            f"1. HOOK (Kalimat Pertama): Harus provokatif, mengejutkan, atau pertanyaan retoris yang membuat orang stop scrolling.\n"
            f"2. ISI: Lanjutkan dengan storytelling yang emosional dan deep.\n"
            f"3. RETENTION: Pecah menjadi kalimat-kalimat pendek.\n"
            f"Syarat Teknis:\n"
            f"- Total panjang sekitar 100-130 kata (Target 40-55 detik).\n"
            f"- Jangan pakai tanda kutip, jangan pakai label 'Hook:' atau 'Isi:'.\n"
            f"- Langsung tulis naskah mentahnya saja."
        )
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"   -> Ide Viral: {text[:50]}...")
        return text
    except Exception as e:
        print(f"❌ [BRAIN ERROR] Gagal berpikir: {e}")
        return "Pernahkah kamu merasa sepi di tengah keramaian? Hujan malam ini membawa jawaban yang tak terucap."

if __name__ == "__main__":
    # Test Otak
    ask_gemini("hujan")