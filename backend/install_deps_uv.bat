@echo off
REM Install backend dependencies using uv (Windows)
cd /d %~dp0
uv add -r requirements.txt
uv pip list
echo To run scripts using the same environment, use: uv python <script>.py
pause
