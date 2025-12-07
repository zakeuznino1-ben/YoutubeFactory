from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal, Channel
from stream_engine import LiveEngine
# Import Mandor Baru Kita
from scheduler import RobotMandor

# -- SETUP --
Base.metadata.create_all(bind=engine)
app = FastAPI()

# 1. Inisialisasi Mesin
streamer = LiveEngine()

# 2. Inisialisasi Mandor (Berikan kendali mesin ke mandor)
mandor = RobotMandor(streamer)

# 3. NYALAKAN MANDOR SAAT SERVER START
@app.on_event("startup")
async def startup_event():
    mandor.start()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -- ROUTES --

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    channels = db.query(Channel).all()
    
    # Sinkronisasi Status Nyata (Engine vs Database)
    # Ini fitur "Self-Healing": Kalau engine mati tapi DB bilang LIVE, kita koreksi.
    global_status = False
    for c in channels:
        real_status = streamer.is_active(c.id)
        if real_status:
            global_status = True # Ada minimal 1 yang nyala
            if c.status != "LIVE": # Koreksi DB
                c.status = "LIVE"
                db.commit()
        else:
            if c.status == "LIVE": # Engine mati, tapi DB LIVE -> Ubah jadi OFFLINE
                c.status = "OFFLINE"
                db.commit()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "channels": channels,
        "is_running": global_status, # Cuma buat indikator global di pojok kanan atas
        "jam_kerja": f"{mandor.START_HOUR}:00 - {mandor.END_HOUR}:00"
    })

@app.post("/add-channel")
async def add_channel(
    channel_name: str = Form(...), 
    channel_id: str = Form(...), 
    video_source: str = Form(...), # <--- Parameter Baru
    db: Session = Depends(get_db)
):
    # Simpan nama video ke database
    new_channel = Channel(
        channel_name=channel_name, 
        channel_id=channel_id, 
        video_source=video_source, # <--- Simpan disini
        status="OFFLINE"
    )
    db.add(new_channel)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Tombol Manual masih tetap bisa dipakai (Override)
@app.post("/start-stream/{channel_id}")
async def start_stream(channel_id: int, db: Session = Depends(get_db)):
    # 1. Cari data channel
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        return RedirectResponse(url="/", status_code=303)
        
    # 2. Tentukan Video DARI DATABASE (Bukan Hardcoded lagi)
    # Gunakan nama file dari DB. Jika file tidak ada, fallback ke test.mp4
    filename = channel.video_source if channel.video_source else "test.mp4"
    video_path = os.path.join(ASSETS_DIR, filename)
    
    # Cek apakah file benar-benar ada?
    if not os.path.exists(video_path):
        print(f"ERROR: File {filename} tidak ditemukan! Menggunakan default.")
        video_path = os.path.join(ASSETS_DIR, "test.mp4")

    # Fake Key
    fake_key = f"abcd-1234-channel-{channel_id}" 
    
    # 3. NYALAKAN MESIN
    streamer.start_stream(video_path, fake_key, channel_id) 
    
    # 4. Update Status Database
    channel.status = "LIVE"
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop-stream/{channel_id}")
async def stop_stream(channel_id: int, db: Session = Depends(get_db)):
    # 1. Matikan Mesin (Kirim ID Channel!)
    streamer.stop_stream(channel_id) # <--- PERUBAHAN DISINI
    
    # 2. Update Status Database
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        channel.status = "OFFLINE"
        db.commit()
        
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)