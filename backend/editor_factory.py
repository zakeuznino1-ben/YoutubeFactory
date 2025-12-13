import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, vfx, concatenate_audioclips

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

def render_video(output_filename="hasil.mp4", target_duration=60, keyword_filter=None, mode="long"):
    print(f"\n🏭 [FACTORY] Memulai produksi. Tema: {keyword_filter} | Mode: {mode.upper()}")
    
    # 1. Cari Bahan Baku Sesuai Tema
    footage_files = get_files_by_keyword(INPUT_FOOTAGE, ('.mp4', '.mov'), keyword_filter)
    music_files = get_files_by_keyword(INPUT_MUSIC, ('.mp3', '.wav'), keyword_filter)

    if not footage_files or not music_files:
        print(f"❌ Error: Bahan baku kurang untuk keyword '{keyword_filter}'!")
        return

    # 2. Racik Resep (Ambil Acak)
    selected_video_name = random.choice(footage_files)
    selected_music_name = random.choice(music_files)
    
    video_path = os.path.join(INPUT_FOOTAGE, selected_video_name)
    music_path = os.path.join(INPUT_MUSIC, selected_music_name)

    print(f"   -> Video Source : {selected_video_name}")
    print(f"   -> Audio Source : {selected_music_name}")

    try:
        # 3. Load File
        clip = VideoFileClip(video_path)
        audio = AudioFileClip(music_path)

        # --- LOGIKA BARU V2.0: SHORTS (VERTICAL CROP) ---
        if mode == "shorts":
            # Target: 9:16 (Biasanya 1080x1920)
            print("   -> ✂️ Mengubah format ke VERTICAL (9:16)...")
            
            # Strategi Center Crop:
            # 1. Pastikan tingginya 1920 pixel (agar HD)
            # 2. Potong bagian tengah selebar 1080 pixel
            
            if clip.w > clip.h: # Jika Video Landscape
                new_height = 1920
                clip = clip.resize(height=new_height) 
                # Rumus crop tengah: (LebarBaru / 2) - (1080 / 2)
                center_x = clip.w / 2
                clip = clip.crop(x1=center_x - 540, y1=0, width=1080, height=1920)
            else:
                # Jika video aslinya sudah vertikal/kotak, resize lebar ke 1080
                clip = clip.resize(width=1080)
                # Pastikan tinggi tidak kurang dari 1920 (opsional, tapi aman)
                # clip = clip.crop(width=1080, height=1920, x_center=clip.w/2, y_center=clip.h/2)

        # 4. LOGIKA LOOPING (Sama seperti V1.0)
        if audio.duration < target_duration:
            n_loops = int(target_duration // audio.duration) + 1
            audio = concatenate_audioclips([audio] * n_loops)
        
        final_audio = audio.subclip(0, target_duration)
        final_clip = clip.loop(duration=target_duration)
        final_clip = final_clip.set_audio(final_audio)

        # Fade Effect (Supaya halus)
        final_clip = final_clip.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        final_clip = final_clip.audio_fadein(1).audio_fadeout(1)

        # 5. Render / Export
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        print(f"   -> Rendering ke: {output_filename} ...")
        
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=24,
            preset="ultrafast",
            threads=4
        )
        print(f"✅ [FACTORY] Sukses! File: assets/{output_filename}")
        
    except Exception as e:
        print(f"❌ Error Produksi: {e}")

if __name__ == "__main__":
    print("--- CONTENT FACTORY V2.0 (MULTI-FORMAT) ---")
    
    # Input User Baru
    tema = input("1. Masukkan Tema (christmas / rain): ").strip()
    jenis = input("2. Jenis Output (long / shorts): ").strip().lower()
    
    # Default Logic Durasi
    durasi = 60 # Default 1 menit
    if jenis == "shorts":
        durasi = 59 # Shorts maksimal 60 detik, kita set 59 biar aman
        print("   -> Mode Shorts terdeteksi: Durasi otomatis set ke 59 detik.")
    else:
        durasi_input = input("3. Durasi detik (enter utk default 60): ").strip()
        if durasi_input: durasi = int(durasi_input)

    # Nama File Otomatis
    nama_file = f"render_{tema}_{jenis}_v1.mp4"
    
    render_video(output_filename=nama_file, target_duration=durasi, keyword_filter=tema, mode=jenis)