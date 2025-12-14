import os
import random
import re

# --- PATCH FIX ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# --- KONFIGURASI IMAGEMAGICK (UNTUK MAC BIARKAN DEFAULT, DI PC NANTI EDIT) ---
from moviepy.config import change_settings
# Saat di Mac, baris ini mungkin tidak perlu diubah. 
# Nanti di PC, pastikan path-nya benar via Notepad jika perlu.
# change_settings({"IMAGEMAGICK_BINARY": r"C:\Path\To\magick.exe"})

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip, vfx
from brain import ask_gemini
from narrator import buat_suara

# KONFIGURASI PATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOOTAGE = os.path.join(BASE_DIR, "factory_line", "raw_footage")
INPUT_MUSIC = os.path.join(BASE_DIR, "factory_line", "raw_music")
INPUT_SFX = os.path.join(BASE_DIR, "factory_line", "raw_sfx") # FOLDER BARU UNTUK SFX
OUTPUT_DIR = os.path.join(BASE_DIR, "assets")
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "Montserrat-ExtraBold.ttf")

# Buat folder SFX jika belum ada
if not os.path.exists(INPUT_SFX):
    os.makedirs(INPUT_SFX)

def get_files_by_keyword(folder, extension, keyword=None):
    if not os.path.exists(folder): return []
    files = [f for f in os.listdir(folder) if f.endswith(extension)]
    if keyword:
        # Filter longgar: cari file yang mengandung kata kunci
        filtered = [f for f in files if keyword.lower() in f.lower()]
        # Jika tidak ada yang cocok, kembalikan semua (fallback) agar tidak crash
        return filtered if filtered else files
    return files

def split_text_into_chunks(text):
    # Pecah per kalimat (titik/tanda tanya/seru)
    chunks = re.split(r'(?<=[.?!])\s+', text)
    return [c for c in chunks if c.strip()]

# --- FITUR BARU 1: KEN BURNS EFFECT (SLOW ZOOM) ---
def zoom_in_effect(clip, zoom_ratio=0.04):
    """Efek Zoom In perlahan sebesar 4% per detik"""
    def effect(get_frame, t):
        img = clip.get_frame(t)
        h, w = img.shape[:2]
        # Zoom factor bertambah seiring waktu t
        scale = 1 + (zoom_ratio * t)
        
        # Hitung crop center
        new_w = w / scale
        new_h = h / scale
        x1 = (w - new_w) / 2
        y1 = (h - new_h) / 2
        
        # Karena kita pakai MoviePy vfx.resize nanti, kita return frame asli saja
        # Teknik Zoom paling aman di MoviePy adalah via resize properti clip
        return img 

    # Cara simple zoom di MoviePy: Resize clip jadi lebih besar seiring waktu, lalu crop tengahnya
    # Tapi ini berat. Kita pakai cara 'Resize' statis lalu crop dinamis? 
    # Tidak, cara termudah dan teringan:
    return clip.resize(lambda t : 1 + 0.02*t).set_position(('center', 'center'))

def create_scene(text_chunk, video_pool, scene_idx):
    print(f"   🎬 [SCENE {scene_idx}] Merakit: '{text_chunk[:20]}...'")
    
    # 1. AUDIO & DURASI
    temp_audio_path = os.path.join(OUTPUT_DIR, f"temp_voice_{scene_idx}.mp3")
    buat_suara(text_chunk, temp_audio_path)
    audio_clip = AudioFileClip(temp_audio_path)
    duration = audio_clip.duration + 0.3 # Buffer dikit
    
    # 2. VIDEO VISUAL
    video_file = random.choice(video_pool)
    video_clip = VideoFileClip(os.path.join(INPUT_FOOTAGE, video_file))
    
    # Loop/Cut Logic
    if video_clip.duration < duration:
        video_clip = video_clip.loop(duration=duration)
    else:
        # Random start point
        max_start = video_clip.duration - duration
        start_t = random.uniform(0, max_start)
        video_clip = video_clip.subclip(start_t, start_t + duration)
    
    # 3. RESIZE VERTICAL (9:16)
    if video_clip.w > video_clip.h:
        video_clip = video_clip.resize(height=1920)
        video_clip = video_clip.crop(x1=video_clip.w/2 - 540, y1=0, width=1080, height=1920)
    else:
        video_clip = video_clip.resize(width=1080)
        
    # 4. TERAPKAN EFEK ZOOM (KEN BURNS) - FITUR BARU
    # Kita pakai resize lambda: zoom in 2% per detik (smooth)
    # Gunakan CompositeVideoClip untuk menahan ukuran frame 1080x1920
    video_zoomed = video_clip.resize(lambda t : 1 + 0.02*t) # Zooming
    video_zoomed = video_zoomed.set_position(('center', 'center'))
    video_base = CompositeVideoClip([video_zoomed], size=(1080,1920)).set_duration(duration)

    # 5. SUBTITLE
    txt_clip = TextClip(
        text_chunk, font=FONT_PATH, fontsize=45, color='white', 
        size=(900, None), method='caption', stroke_color='black', stroke_width=2, align='center'
    )
    txt_clip = txt_clip.set_position(('center', 'center')).set_duration(duration)
    
    final_scene = CompositeVideoClip([video_base, txt_clip]).set_audio(audio_clip)
    return final_scene

def render_video_montage(keyword_filter):
    print(f"\n🏭 [FACTORY V4.5 - VIRAL ENGINE] Tema: {keyword_filter}")
    print(f"   ✨ Features: Hook Script + Ken Burns Zoom + SFX Layering")
    
    footage_files = get_files_by_keyword(INPUT_FOOTAGE, ('.mp4', '.mov'), keyword_filter)
    music_files = get_files_by_keyword(INPUT_MUSIC, ('.mp3', '.wav'), keyword_filter)
    # Cari SFX yang cocok dengan tema (misal: rain.mp3)
    sfx_files = get_files_by_keyword(INPUT_SFX, ('.mp3', '.wav'), keyword_filter)
    
    if not footage_files or not music_files:
        print("❌ Error: Bahan baku kurang!")
        return

    # Minta Script Hook
    full_script = ask_gemini(keyword_filter)
    chunks = split_text_into_chunks(full_script)
    
    scenes = []
    total_duration = 0
    for i, chunk in enumerate(chunks):
        try:
            scene = create_scene(chunk, footage_files, i+1)
            scenes.append(scene)
            total_duration += scene.duration
        except Exception as e:
            print(f"⚠️ Skip scene {i}: {e}")

    print(f"   -> 🔗 Menggabungkan {len(scenes)} scenes...")
    final_video = concatenate_videoclips(scenes, method="compose")

    # --- AUDIO MIXING (MUSIC + SFX) ---
    print("   -> 🎵 Mixing Audio Layers...")
    
    # Layer 1: Narator (Sudah ada di final_video)
    
    # Layer 2: Music Background
    bg_music = AudioFileClip(os.path.join(INPUT_MUSIC, random.choice(music_files)))
    if bg_music.duration < total_duration:
        bg_music = bg_music.loop(duration=total_duration+2)
    bg_music = bg_music.subclip(0, total_duration).volumex(0.20) # 20% Volume
    
    # Layer 3: SFX Atmosphere (FITUR BARU)
    sfx_audio = None
    if sfx_files:
        sfx_name = random.choice(sfx_files)
        print(f"   -> 🌧️ Menambahkan Atmosfer: {sfx_name}")
        sfx_clip = AudioFileClip(os.path.join(INPUT_SFX, sfx_name))
        if sfx_clip.duration < total_duration:
            sfx_clip = sfx_clip.loop(duration=total_duration)
        sfx_clip = sfx_clip.subclip(0, total_duration).volumex(0.40) # 40% Volume (Cukup terdengar)
        sfx_audio = sfx_clip
    else:
        print("   -> ℹ️ Tidak ada file SFX spesifik, skip layer atmosfer.")

    # Gabung Semua Audio
    audio_layers = [final_video.audio, bg_music] # Narator + Musik
    if sfx_audio:
        audio_layers.append(sfx_audio) # Tambah SFX jika ada
        
    final_mixed_audio = CompositeAudioClip(audio_layers)
    final_video = final_video.set_audio(final_mixed_audio)

    # RENDER
    output_filename = f"viral_{keyword_filter}_v4.5.mp4"
    print(f"   -> 🚀 Rendering: {output_filename}")
    final_video.write_videofile(
        os.path.join(OUTPUT_DIR, output_filename), 
        fps=24, codec="libx264", audio_codec="aac", threads=4, preset="ultrafast"
    )
    print("✅ VIRAL SHORT SELESAI!")

if __name__ == "__main__":
    tema = input("Tema (rain/christmas): ").strip()
    render_video_montage(tema)