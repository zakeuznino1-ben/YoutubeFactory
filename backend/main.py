from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

app = FastAPI()

# Menyiapkan lokasi folder frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    # Ini fungsi untuk menampilkan halaman dashboard
    return templates.TemplateResponse("dashboard.html", {"request": request, "status": "SISTEM SIAP"})

if __name__ == "__main__":
    # Menjalankan server di port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)