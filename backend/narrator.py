import asyncio
import edge_tts
import os

# Suara ID yang bagus (Bahasa Indonesia):
# id-ID-GadisNeural (Perempuan, Muda, Natural)
# id-ID-ArdiNeural (Laki-laki, Kalem)
VOICE = "id-ID-GadisNeural"

async def _generate_audio(text, output_file):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_file)

def buat_suara(text, output_filename="tts_output.mp3"):
    """Fungsi pembungkus agar bisa dipanggil oleh script Editor biasa"""
    print(f"🗣️ [NARRATOR] Mengucapkan: '{text}'")
    
    # Tentukan lokasi simpan (di folder assets sementara)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "assets", output_filename)
    
    try:
        # Jalankan Async function dalam mode Sync
        asyncio.run(_generate_audio(text, output_path))
        print(f"   -> Audio tersimpan: {output_filename}")
        return output_path
    except Exception as e:
        print(f"❌ [TTS ERROR] Gagal bicara: {e}")
        return None

if __name__ == "__main__":
    # Test Mulut
    buat_suara("Halo bos, sistem narator sudah siap bertugas.")