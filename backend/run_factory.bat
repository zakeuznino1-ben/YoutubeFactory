@echo off
:: Judul Jendela
title Youtube Factory Automation Engine v3.1

:: Pindah ke direktori tempat file ini berada (backend)
cd /d "%~dp0"

:: Lapor status
echo [BOOT] Memulai Sistem Youtube Factory...
echo [BOOT] Menghubungkan ke Virtual Environment...

:: Aktifkan Venv & Jalankan Main App
call ..\venv\Scripts\activate
python main.py

:: Jika error/crash, jangan langsung tutup jendela (agar bisa dibaca lognya)
pause