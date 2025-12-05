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
    is_running = True if streamer.process else False
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "channels": channels, 
        "is_running": is_running,
        # Kirim info jam kerja ke HTML
        "jam_kerja": f"{mandor.START_HOUR}:00 - {mandor.END_HOUR}:00" 
    })

@app.post("/add-channel")
async def add_channel(channel_name: str = Form(...), channel_id: str = Form(...), db: Session = Depends(get_db)):
    new_channel = Channel(channel_name=channel_name, channel_id=channel_id, status="OFFLINE")
    db.add(new_channel)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Tombol Manual masih tetap bisa dipakai (Override)
@app.post("/start-stream/{channel_id}")
async def start_stream(channel_id: int, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel: return RedirectResponse(url="/", status_code=303)
    
    # Paksa Nyala (Manual)
    video_path = os.path.join(ASSETS_DIR, "test.mp4")
    streamer.start_stream(video_path, "manual-override-key")
    channel.status = "LIVE"
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop-stream/{channel_id}")
async def stop_stream(channel_id: int, db: Session = Depends(get_db)):
    streamer.stop_stream()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        channel.status = "OFFLINE"
        db.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)