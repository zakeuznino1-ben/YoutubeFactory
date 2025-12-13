import os
import random

# --- PATCH FIX: OBAT PENAWAR UNTUK PILLOW TERBARU ---
# Masalah: MoviePy lama mencari 'ANTIALIAS', tapi Pillow baru menghapusnya.
# Solusi: Kita buatkan 'ANTIALIAS' palsu yang mengarah ke 'LANCZOS'.
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ----------------------------------------------------

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, concatenate_audioclips, vfx
from brain import ask_gemini
from narrator import buat_suara

# KONFIGURASI PABRIK
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOOTAGE = os.path.join(BASE_DIR, "factory_line", "raw_footage")
INPUT_MUSIC = os.path.join(BASE_DIR, "factory_line", "raw_music")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets")
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "Montserrat-ExtraBold.ttf")

def get_files_by_keyword(folder, extension, keyword=None):
    files = [f for f in os.listdir(folder) if f.endswith(extension)]
    if keyword:
        files = [f for f in files if keyword.lower() in f.lower()]
    return files

def render_video(output_filename="hasil.mp4", target_duration=60, keyword_filter=None, mode="long"):
    print(f"\n🏭 [FACTORY V3.1] Memulai produksi. Tema: {keyword_filter} | Mode: {mode.upper()}")
    
    # 1. Cari Bahan Baku
    footage_files = get_files_by_keyword(INPUT_FOOTAGE, ('.mp4', '.mov'), keyword_filter)
    music_files = get_files_by_keyword(INPUT_MUSIC, ('.mp3', '.wav'), keyword_filter)

    if not footage_files or not music_files:
        print(f"❌ Error: Bahan baku kurang!")
        return

    selected_video_name = random.choice(footage_files)
    selected_music_name = random.choice(music_files)
    
    video_path = os.path.join(INPUT_FOOTAGE, selected_video_name)
    music_path = os.path.join(INPUT_MUSIC, selected_music_name)

    try:
        # 2. Load Video & Musik Background
        clip = VideoFileClip(video_path)
        bg_music = AudioFileClip(music_path)
        
        # Kecilkan volume musik background (30%)
        bg_music = bg_music.volumex(0.3) 

        # 3. INTELLIGENCE LAYER (Shorts Only)
        quotes_text = ""
        voice_audio = None
        
        if mode == "shorts":
            # A. Brain 2.5 Flash
            quotes_text = ask_gemini(keyword_filter)
            
            # B. TTS Narrator
            voice_path = buat_suara(quotes_text, "temp_voice.mp3")
            if voice_path:
                voice_audio = AudioFileClip(voice_path)

            # C. Resize & Crop 9:16
            print("   -> ✂️ Mengubah format ke VERTICAL (9:16)...")
            if clip.w > clip.h:
                new_height = 1920
                clip = clip.resize(height=new_height)
                center_x = clip.w / 2
                clip = clip.crop(x1=center_x - 540, y1=0, width=1080, height=1920)
            else:
                clip = clip.resize(width=1080)

        # 4. LOOPING
        final_clip = clip.loop(duration=target_duration)
        
        if bg_music.duration < target_duration:
            n_loops = int(target_duration // bg_music.duration) + 1
            bg_music = concatenate_audioclips([bg_music] * n_loops)
        bg_music = bg_music.subclip(0, target_duration)

        # 5. MIXING AUDIO
        final_audio = bg_music
        if voice_audio:
            voice_audio = voice_audio.set_start(1)
            final_audio = CompositeAudioClip([bg_music, voice_audio])
        
        final_clip = final_clip.set_audio(final_audio)

        # 6. TEXT OVERLAY
        if mode == "shorts" and quotes_text:
            print(f"   -> ✍️ Menulis Teks: {quotes_text}")
            txt_clip = TextClip(
                quotes_text, 
                font=FONT_PATH, 
                fontsize=55, 
                color='white', 
                size=(900, None), 
                method='caption', 
                stroke_color='black', 
                stroke_width=3
            )
            txt_clip = txt_clip.set_position('center').set_duration(target_duration)
            final_clip = CompositeVideoClip([final_clip, txt_clip])

        # Fade Effect
        final_clip = final_clip.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        final_clip = final_clip.audio_fadein(1).audio_fadeout(1)

        # 7. RENDER
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
    print("--- CONTENT FACTORY V3.1 (AI POWERED + PATCHED) ---")
    tema = input("1. Tema (christmas/rain): ").strip()
    jenis = input("2. Jenis (long/shorts): ").strip().lower()
    
    durasi = 60
    if jenis == "shorts":
        durasi = 59 
    else:
        d_in = input("3. Durasi (enter=60): ").strip()
        if d_in: durasi = int(d_in)

    nama_file = f"render_{tema}_{jenis}_AI.mp4"
    render_video(nama_file, durasi, tema, jenis)