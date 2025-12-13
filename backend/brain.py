import google.generativeai as genai
import os

# --- KONFIGURASI ---
# GANTI TULISAN INI DENGAN API KEY DARI GOOGLE AI STUDIO
API_KEY = "AIzaSyCtSEBXQPwOKnNGA6M4hbTHoQDRLftSPMI" 

genai.configure(api_key=API_KEY)

def ask_gemini(tema):
    """Meminta Gemini membuatkan Quotes pendek berdasarkan tema"""
    print(f"🧠 [BRAIN] Memikirkan quotes tentang '{tema}'...")
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Prompt Engineering Khusus Gen Z / Shorts
    prompt = (
        f"Buatkan 1 kalimat quotes pendek (maksimal 12 kata) yang aesthetic, deep, dan relatable "
        f"untuk caption video TikTok/Shorts dengan suasana '{tema}'. "
        f"Gunakan Bahasa Indonesia yang santai tapi puitis. "
        f"Jangan pakai tanda kutip. Langsung kalimatnya saja."
    )
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"   -> Ide: {text}")
        return text
    except Exception as e:
        print(f"❌ [BRAIN ERROR] Gagal berpikir: {e}")
        # Fallback jika error / kuota habis
        return "Nikmati setiap detik yang berlalu."

if __name__ == "__main__":
    # Test Otak
    ask_gemini("hujan malam hari")