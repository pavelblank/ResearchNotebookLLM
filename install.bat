@echo off
echo ============================================================
echo   ResearchPilot -- Auto Installer
echo   This will install Python packages and set up Ollama.
echo ============================================================
echo.
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
pause
