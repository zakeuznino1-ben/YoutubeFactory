import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, vfx, CompositeAudioClip, concatenate_audioclips

# KONFIGURASI PABRIK
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOOTAGE = os.path.join(BASE_DIR, "factory_line", "raw_footage")
INPUT_MUSIC = os.path.join(BASE_DIR, "factory_line", "raw_music")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets")

def get_files_by_keyword(folder, extension, keyword=None):
    """Mencari file dalam folder yang mengandung keyword tertentu"""
    files = [f for f in os.listdir(folder) if f.endswith(extension)]
    if keyword:
        # Filter file yang nama filenya mengandung keyword (case insensitive)
        files = [f for f in files if keyword.lower() in f.lower()]
    return files

def render_video(output_filename="hasil_render.mp4", target_duration=60, keyword_filter=None):
    print(f"\n🏭 [FACTORY] Memulai produksi. Tema: {keyword_filter if keyword_filter else 'ACAK'}")
    
    # 1. Cari Bahan Baku Sesuai Tema
    footage_files = get_files_by_keyword(INPUT_FOOTAGE, ('.mp4', '.mov'), keyword_filter)
    music_files = get_files_by_keyword(INPUT_MUSIC, ('.mp3', '.wav'), keyword_filter)

    if not footage_files:
        print(f"❌ Error: Tidak ada video dengan kata kunci '{keyword_filter}'!")
        return
    if not music_files:
        print(f"❌ Error: Tidak ada musik dengan kata kunci '{keyword_filter}'!")
        return

    # 2. Racik Resep (Ambil 1 Video & 1 Musik Acak)
    # Tips: Nanti bisa di-upgrade jadi stitch banyak video, tapi skrg 1 loop dulu.
    selected_video_name = random.choice(footage_files)
    selected_music_name = random.choice(music_files)
    
    video_path = os.path.join(INPUT_FOOTAGE, selected_video_name)
    music_path = os.path.join(INPUT_MUSIC, selected_music_name)

    print(f"   -> Video Source : {selected_video_name}")
    print(f"   -> Audio Source : {selected_music_name}")
    print(f"   -> Target Durasi: {target_duration} detik")

    try:
        # 3. Proses Memasak (Editing)
        clip = VideoFileClip(video_path)
        audio = AudioFileClip(music_path)

        # LOGIKA AUDIO LOOPING
        # Jika durasi lagu lebih pendek dari target video, lagu harus di-loop / disambung
        if audio.duration < target_duration:
            # Hitung butuh berapa kali putar
            n_loops = int(target_duration // audio.duration) + 1
            # Sambung lagu berulang-ulang
            audio = concatenate_audioclips([audio] * n_loops)
        
        # Potong audio sesuai durasi target pas
        final_audio = audio.subclip(0, target_duration)

        # LOGIKA VIDEO LOOPING
        final_clip = clip.loop(duration=target_duration)
        
        # Tempel Audio
        final_clip = final_clip.set_audio(final_audio)

        # Fade In/Out (Video & Audio)
        final_clip = final_clip.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        final_clip = final_clip.audio_fadein(1).audio_fadeout(1)

        # 4. Render / Export
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        print(f"   -> Rendering ke: {output_filename} ...")
        
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=24,     # 24fps cukup untuk cinematic
            preset="ultrafast", # Ganti 'medium' kalau mau kualitas bagus (tapi lama)
            threads=4
        )
        print(f"✅ [FACTORY] Sukses! File tersimpan di: assets/{output_filename}")
        
    except Exception as e:
        print(f"❌ Error Produksi: {e}")

if __name__ == "__main__":
    # MENU INTERAKTIF SAAT DIJALANKAN
    print("--- CONTENT FACTORY V1.0 ---")
    tema = input("Masukkan Tema (christmas / rain): ").strip()
    durasi = input("Durasi detik (contoh 30): ").strip()
    nama_file = input("Nama Output (contoh hasil.mp4): ").strip()
    
    if not durasi: durasi = 30
    if not nama_file: nama_file = f"render_{tema}.mp4"
    
    render_video(output_filename=nama_file, target_duration=int(durasi), keyword_filter=tema)