from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from stream_engine import StreamEngine 
from scheduler import RobotMandor
from database import init_db, SessionLocal, Channel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(base_dir), "frontend", "templates")
templates = Jinja2Templates(directory=template_dir)

init_db()

streamer = StreamEngine() 
mandor = RobotMandor(streamer)

@app.on_event("startup")
def startup_event():
    mandor.start()

# --- PERBAIKAN DI SINI (V5.2) ---
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    # Buka Database untuk mengambil data channel
    db = SessionLocal()
    channels = db.query(Channel).all()
    db.close()
    # Kirim data 'channels' ke tampilan HTML
    return templates.TemplateResponse("dashboard.html", {"request": request, "channels": channels})

@app.get("/api/status")
def get_status():
    db = SessionLocal()
    channels = db.query(Channel).all()
    data = []
    for ch in channels:
        is_running = streamer.is_active(ch.id)
        status_text = "LIVE" if is_running else "OFFLINE"
        data.append({
            "id": ch.id,
            "name": ch.channel_name,
            "status": status_text,
            "video_source": ch.video_source,
            "youtube_id": ch.youtube_id
        })
    db.close()
    return {"system_status": "ONLINE", "version": "V5.2 Display Fix", "channels": data}

@app.post("/add-channel")
def add_channel(
    channel_name: str = Form(...),
    channel_id: str = Form(...),
    video_source: str = Form(...)
):
    db = SessionLocal()
    new_channel = Channel(
        channel_name=channel_name,
        youtube_id=channel_id,
        video_source=video_source,
        status="OFFLINE"
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    db.close()
    return HTMLResponse(content='<script>window.location.href="/"</script>', status_code=200)

@app.post("/start-stream/{channel_id}")
def start_stream_endpoint(channel_id: int):
    db = SessionLocal()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    
    if not channel:
        db.close()
        return JSONResponse(status_code=404, content={"msg": "Channel not found"})
    
    assets_dir = os.path.join(os.path.dirname(base_dir), "assets")
    
    if "." not in channel.video_source:
         video_path = os.path.join(assets_dir, channel.video_source)
    else:
        video_path = os.path.join(assets_dir, channel.video_source)

    real_key = channel.youtube_id
    streamer.start_stream(video_path, real_key, channel.id)
    
    channel.status = "LIVE"
    db.commit()
    db.close()
    return HTMLResponse(content='<script>window.location.href="/"</script>', status_code=200)

@app.post("/stop-stream/{channel_id}")
def stop_stream_endpoint(channel_id: int):
    streamer.stop_stream(channel_id)
    db = SessionLocal()
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if channel:
        channel.status = "OFFLINE"
        db.commit()
    db.close()
    return HTMLResponse(content='<script>window.location.href="/"</script>', status_code=200)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)