@echo off
REM Auto-start Flask app + tunnel on boot
cd /d E:\openclaw-data\workspace\shift-scheduler

REM Start Flask
start /B D:\PYTHON\python.exe app.py

REM Wait for Flask to start
timeout /t 3 /nobreak >nul

REM Start tunnel
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:8080 nokey@localhost.run
