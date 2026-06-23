# ============================================================
#  Research NotebookLM — Installer (Windows)
#  Installs Python packages, Ollama (local AI), and sets up
#  config files so you can run the app immediately.
#
#  Run:  Double-click install.bat
#        OR right-click install.bat -> Run as Administrator
# ============================================================

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Step($msg) { Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [ ! ] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  [ERR] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Research NotebookLM — Setup" -ForegroundColor Magenta
Write-Host "   Your private AI research assistant" -ForegroundColor DarkGray
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ── 1. Find or install Python ─────────────────────────────────────────────────
Write-Step "Checking Python 3.10+..."
$python = $null

foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 10) {
                $python = $cmd
                Write-OK "Found $ver — good to go"
                break
            } else {
                Write-Warn "Found $ver but need 3.10+. Will try to install a newer version."
            }
        }
    } catch {}
}

if (-not $python) {
    Write-Warn "Python 3.10+ not found. Installing Python 3.12 via winget..."
    Write-Warn "This may take a minute. Please wait."
    winget install --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH","User")
    $python = "python"
    Write-OK "Python installed."
    Write-Warn "If this step failed, download Python from https://python.org and re-run install.bat"
}

# ── 2. Create virtual environment ────────────────────────────────────────────
Write-Step "Setting up Python virtual environment..."
$venvPath = Join-Path $ProjectRoot "venv"
if (-not (Test-Path $venvPath)) {
    & $python -m venv $venvPath
    Write-OK "Virtual environment created in 'venv' folder"
} else {
    Write-OK "Virtual environment already exists"
}

# Use the venv Python for all subsequent installs
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
    Write-OK "Using venv Python: $venvPython"
}

# ── 3. Install Python packages ────────────────────────────────────────────────
Write-Step "Installing Python packages..."
Write-Warn "This may take 3-10 minutes on first run (downloads AI/ML libraries)."
Write-Warn "Please wait — do not close this window."

& $python -m pip install --upgrade pip --quiet
& $python -m pip install -r "$ProjectRoot\requirements.txt"

if ($LASTEXITCODE -eq 0) {
    Write-OK "All packages installed successfully."
} else {
    Write-Err "Some packages failed. Check the error messages above."
    Write-Warn "Common fix: run install.bat as Administrator, or check your internet connection."
}

# ── 4. Ollama (free local AI — no API key needed) ────────────────────────────
Write-Step "Checking Ollama (local AI engine)..."
Write-Warn "Ollama lets you run AI completely on your computer — no API key needed."

$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCmd) {
    Write-Warn "Ollama not found. Installing via winget..."
    winget install --id Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH","User")
    Write-OK "Ollama installed."
    Write-Warn "If winget failed, download Ollama from https://ollama.com and install it, then re-run this script."
} else {
    Write-OK "Ollama already installed."
}

# Start Ollama service to check / pull models
$ollamaRunning = $false
try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 | Out-Null
    $ollamaRunning = $true
    Write-OK "Ollama service is running."
} catch {}

if (-not $ollamaRunning) {
    Write-Step "Starting Ollama service..."
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 6
    try {
        Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 | Out-Null
        Write-OK "Ollama started successfully."
        $ollamaRunning = $true
    } catch {
        Write-Warn "Ollama did not start automatically."
        Write-Warn "You can start it manually by running: ollama serve"
        Write-Warn "Or just open Ollama from the Start Menu — it runs in the system tray."
    }
}

# Download a small AI model if none exist
if ($ollamaRunning) {
    Write-Step "Checking local AI models..."
    try {
        $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        $modelCount = ($tags.models | Measure-Object).Count
        if ($modelCount -eq 0) {
            Write-Warn "No local AI models found. Downloading qwen2.5:3b (~2 GB)..."
            Write-Warn "This is a small, capable AI model that runs entirely on your PC."
            Write-Warn "Download may take 5-15 minutes depending on your internet speed."
            & ollama pull qwen2.5:3b
            Write-OK "AI model downloaded and ready."
        } else {
            Write-OK "$modelCount local AI model(s) already available."
        }
    } catch {
        Write-Warn "Could not check Ollama models."
        Write-Warn "Run this command manually after setup: ollama pull qwen2.5:3b"
    }
}

# ── 5. Config files ───────────────────────────────────────────────────────────
Write-Step "Setting up configuration files..."

# Create .env from example
$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item "$ProjectRoot\.env.example" $envFile
    Write-OK "Created .env config file"
} else {
    Write-OK ".env already exists — keeping your settings"
}

# Create data/providers.json from example
$providersFile    = Join-Path $ProjectRoot "data\providers.json"
$providersExample = Join-Path $ProjectRoot "data\providers.example.json"
if (-not (Test-Path $providersFile)) {
    New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "data") | Out-Null
    if (Test-Path $providersExample) {
        Copy-Item $providersExample $providersFile
        Write-OK "Created AI providers config (data\providers.json)"
    }
} else {
    Write-OK "AI providers config already exists"
}

# Create required data directories
foreach ($dir in @("data\projects", "data\chroma", "data\trash", "output")) {
    $dirPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Force -Path $dirPath | Out-Null
    }
}
Write-OK "Data directories ready"

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  To start Research NotebookLM:" -ForegroundColor White
Write-Host "    Double-click  start.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Then open your browser at:  http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "  The app works right away with local AI (Ollama)." -ForegroundColor White
Write-Host "  For faster / smarter AI, add free API keys:" -ForegroundColor Yellow
Write-Host "    - OpenRouter (free): https://openrouter.ai" -ForegroundColor DarkGray
Write-Host "    - NVIDIA NIM (free): https://build.nvidia.com" -ForegroundColor DarkGray
Write-Host "    Then go to  Settings -> AI Engines  inside the app." -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Full setup guide: SETUP.md" -ForegroundColor DarkGray
Write-Host ""
