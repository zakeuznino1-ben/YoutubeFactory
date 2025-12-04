from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from sqlalchemy.orm import Session

# Import file database yang baru kita buat
from database import Base, engine, SessionLocal, Channel

# -- SETUP DATABASE --
# Perintah ini akan otomatis membuat file database jika belum ada
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -- SETUP APP --
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))

# -- ROUTES (JALUR) --

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    # Ambil semua data channel dari database
    channels = db.query(Channel).all()
    
    # Hitung statistik sederhana
    total_channel = len(channels)
    active_live = sum(1 for c in channels if c.status == "ONLINE")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "channels": channels,
        "total_channel": total_channel,
        "active_live": active_live
    })

# Fitur Tambah Channel (Hanya untuk Tes)
@app.post("/add-channel")
async def add_channel_dummy(channel_name: str = Form(...), channel_id: str = Form(...), db: Session = Depends(get_db)):
    # Buat data baru
    new_channel = Channel(channel_name=channel_name, channel_id=channel_id, status="OFFLINE")
    db.add(new_channel)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)