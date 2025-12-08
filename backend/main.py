from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os
import signal
import sys

# UPDATE V5.0: Menggunakan nama class baru
from stream_engine import StreamEngine 
from scheduler import RobotMandor
from database import init_db, SessionLocal, Channel

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Templates (Dashboard)
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(base_dir), "frontend", "templates")
templates = Jinja2Templates(directory=template_dir)

# Inisialisasi Database
init_db()

# Inisialisasi Global Engine
# UPDATE V5.0: Instansiasi StreamEngine
streamer = StreamEngine() 
mandor = RobotMandor(streamer)

# --- DATA MODELS ---
class ChannelData(BaseModel):
    channel_name: str
    youtube_id: str
    # Video Source bisa berupa nama file ("clip.mp4") atau folder ("playlist_natal")
    video_source: str = None 

# --- ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    # Nyalakan Robot Mandor saat server start
    mandor.start()

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/status")
def get_status():
    db = SessionLocal()
    channels = db.query(Channel).all()
    
    data = []
    for ch in channels:
        is_running = streamer.is_active(ch.id)
        # Auto-correction status jika database bilang LIVE tapi mesin mati
        status_text = "LIVE" if is_running else "OFFLINE"
            
        data.append({
            "id": ch.id,
            "name": ch.channel_name,
            "status": status_text,
            "video_source": ch.video_source,
            "youtube_id": ch.youtube_id
        })
    db.close()
    
    return {
        "system_status": "ONLINE", 
        "version": "V5.0 Playlist Engine",
        "channels": data
    }

@app.post("/add-channel")
def add_channel(data: ChannelData):
    db = SessionLocal()
    new_channel = Channel(
        channel_name=data.channel_name,
        youtube_id=data.youtube_id,
        video_source=data.video_source,
        status="OFFLINE"
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    db.close()
    return {"msg": "Channel Added", "id": new_channel.id}

@app.post("/start-stream/{channel_id}")
def start_stream_endpoint(channel_id: int):
    db = SessionLocal()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    
    if not channel:
        db.close()
        return JSONResponse(status_code=404, content={"msg": "Channel not found"})
    
    # Tentukan File Source
    # Mandor V5.0 yang akan menangani logika download/playlist.
    # Di sini kita hanya menyalakan trigger manual.
    assets_dir = os.path.join(os.path.dirname(base_dir), "assets")
    
    # Cek apakah source berupa folder (playlist) atau file
    # Logika sederhana: Jika tidak ada ekstensi .mp4, anggap folder playlist yg sudah didownload Mandor
    if "." not in channel.video_source:
         # Mode Playlist: Path diarahkan ke folder
         video_path = os.path.join(assets_dir, channel.video_source)
         # Tapi engine butuh list file, biarkan engine menanganinya? 
         # TIDAK. Engine butuh LIST.
         # Untuk manual start lewat tombol, kita cari file list manual.
         # (Sebaiknya biarkan Mandor yang menyalakan otomatis via Scheduler, 
         # tapi untuk tombol manual, kita support basic file dulu).
         pass 
    else:
        video_path = os.path.join(assets_dir, channel.video_source)

    # KUNCI UTAMA (REAL KEY)
    real_key = channel.youtube_id
    
    # Panggil Engine (Sekarang support path folder/list di V5.0)
    # Jika manual start playlist, kita perlu logika extra, tapi coba basic dulu.
    streamer.start_stream(video_path, real_key, channel.id)
    
    channel.status = "LIVE"
    db.commit()
    db.close()
    return {"msg": "Stream Started"}

@app.post("/stop-stream/{channel_id}")
def stop_stream_endpoint(channel_id: int):
    streamer.stop_stream(channel_id)
    
    db = SessionLocal()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        channel.status = "OFFLINE"
        db.commit()
    db.close()
    
    return {"msg": "Stream Stopped"}

# --- AUTO START ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)