from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal, Channel
# Import Mesin Baru Kita
from stream_engine import LiveEngine

# -- SETUP --
Base.metadata.create_all(bind=engine)
app = FastAPI()

# Inisialisasi Mesin Streaming (Global)
streamer = LiveEngine()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))
ASSETS_DIR = os.path.join(BASE_DIR, "assets") # Lokasi video

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
    
    # Cek status asli mesin
    is_running = False
    if streamer.process:
        is_running = True
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "channels": channels,
        "is_running": is_running # Kirim status ke HTML
    })

@app.post("/add-channel")
async def add_channel(channel_name: str = Form(...), channel_id: str = Form(...), db: Session = Depends(get_db)):
    new_channel = Channel(channel_name=channel_name, channel_id=channel_id, status="OFFLINE")
    db.add(new_channel)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# -- TOMBOL START STREAM --
@app.post("/start-stream/{channel_id}")
async def start_stream(channel_id: int, db: Session = Depends(get_db)):
    # 1. Cari data channel
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        return RedirectResponse(url="/", status_code=303)
        
    # 2. Tentukan Video (Sementara pakai test.mp4 dulu untuk semua)
    video_path = os.path.join(ASSETS_DIR, "test.mp4")
    
    # 3. Kunci Palsu (Nanti diganti real dari database)
    fake_key = "abcd-1234-tes-doang"
    
    # 4. NYALAKAN MESIN
    streamer.start_stream(video_path, fake_key)
    
    # 5. Update Status Database
    channel.status = "LIVE"
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

# -- TOMBOL STOP STREAM --
@app.post("/stop-stream/{channel_id}")
async def stop_stream(channel_id: int, db: Session = Depends(get_db)):
    # 1. Matikan Mesin
    streamer.stop_stream()
    
    # 2. Update Status Database
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        channel.status = "OFFLINE"
        db.commit()
        
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)