@echo off
REM 57车间排班表 - 启动脚本
cd /d E:\openclaw-data\workspace\shift-scheduler
python -m http.server 8080
pause
