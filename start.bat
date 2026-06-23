@echo off
echo ============================================================
echo   Research NotebookLM - Starting...
echo ============================================================
echo.

REM ── Find Python ──────────────────────────────────────────────
set PYTHON=

REM 1. Use virtual environment if present (created by install.bat)
if exist "%~dp0venv\Scripts\python.exe" (
    set PYTHON=%~dp0venv\Scripts\python.exe
    echo [OK] Using virtual environment
    goto :found_python
)

REM 2. Use system Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
    echo [OK] Using system Python: %PY_VER%
    set PYTHON=python
    goto :found_python
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python3
    goto :found_python
)

echo [ERROR] Python not found. Please run install.bat first.
pause & exit /b 1

:found_python

REM ── Start Ollama local AI if not running ─────────────────────
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Starting Ollama local AI...
    start /B ollama serve
    timeout /t 4 /nobreak >nul
    echo [OK] Ollama started
) else (
    echo [OK] Ollama running
)

REM ── Open browser after 3 seconds ─────────────────────────────
start "" /B cmd /C "timeout /t 3 /nobreak >nul && start http://localhost:8080"

echo.
echo [OK] Open your browser at: http://localhost:8080
echo      Keep this window open while using the app.
echo      Close this window to stop.
echo.

cd /d "%~dp0"
%PYTHON% webapp\app.py

pause
