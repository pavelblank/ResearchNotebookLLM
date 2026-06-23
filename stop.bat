@echo off
echo ============================================================
echo   ResearchPilot -- Stopping
echo ============================================================
echo.
echo [*] Stopping Flask app (port 8080)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080 " 2^>nul') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo [OK] Stopped.
echo.
pause
