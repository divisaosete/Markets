@echo off
setlocal
cd /d "%~dp0"
echo New Era Markets - Beta estatica para GitHub Pages
python -m backend.preview_pages
if errorlevel 1 pause
endlocal
