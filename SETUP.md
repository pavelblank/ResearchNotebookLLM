# Research NotebookLM — Setup Guide

Everything you need to go from zero to running in about 15 minutes. No coding required.

---

## What This App Does

Research NotebookLM is your private AI research assistant. You upload your PDFs, documents, and web links, then ask questions and the AI answers based **only** on your documents — nothing leaks to the cloud. Your data stays on your computer.

---

## Before You Start — What You Need

| Requirement | Details |
|---|---|
| **Computer** | Windows 10 or Windows 11 |
| **RAM** | 8 GB minimum, 16 GB recommended (for local AI) |
| **Disk space** | ~5 GB free (for the AI model) |
| **Internet** | Needed during setup only; optional after |

> **Mac / Linux users:** See the [Manual Setup](#manual-setup-mac--linux) section at the bottom.

---

## Step 1 — Download the Project

**Option A — Download ZIP (easiest, no Git needed):**

1. Go to: `https://github.com/pavelblank/ResearchNotebookLLM`
2. Click the green **Code** button
3. Click **Download ZIP**
4. Extract (unzip) the downloaded file to a folder, e.g. `C:\ResearchNotebookLM`

**Option B — Git clone (if you have Git installed):**
```
git clone https://github.com/pavelblank/ResearchNotebookLLM.git
```

---

## Step 2 — Run the Installer

1. Open the folder where you extracted the project
2. **Double-click `install.bat`**

The installer will automatically:
- Check if Python is installed (installs it if not)
- Create a clean Python environment
- Install all required packages
- Install Ollama (the free local AI engine)
- Download a small AI model (~2 GB)
- Create your config files

> **This takes 5–15 minutes on first run.** The largest step is downloading the AI model. You will see progress messages — just wait until it says "INSTALLATION COMPLETE".

> **Tip:** If you see a Windows security warning ("Windows protected your PC"), click **More info** then **Run anyway**. The installer only installs Python packages and Ollama — it does not modify system settings.

---

## Step 3 — (Optional) Add Free AI API Keys

The app works immediately with Ollama (local AI — free, no account needed). But you can get **faster and smarter AI** by adding a free cloud API key.

**Best free options:**

| Provider | Model | Free tier |
|---|---|---|
| [OpenRouter](https://openrouter.ai) | Gemini 2.5 Flash | Generous free tier |
| [NVIDIA NIM](https://build.nvidia.com) | Gemma / Llama | Free with account |
| [Google AI Studio](https://aistudio.google.com) | Gemini 2.0 Flash | Free API key |

**How to add keys:**
1. Sign up at one of the providers above (it's free)
2. Copy your API key
3. Start the app (Step 4)
4. Open **Settings → AI Engines**
5. Paste your key and enable the provider

You can skip this step and use local Ollama for everything.

---

## Step 4 — Start the App

1. **Double-click `start.bat`**
2. A terminal window will open — leave it running
3. Your browser will automatically open to `http://localhost:8080`

> If the browser doesn't open automatically, open it yourself and go to `http://localhost:8080`

**To stop the app:** Close the terminal window (or press `Ctrl+C` inside it).

---

## Step 5 — Your First Project

1. Click **+ New Project** in the left sidebar
2. Give your project a name (e.g. "Climate Research" or "My Thesis")
3. Click the **Sources** tab → **Upload** your PDFs or paste a URL
4. Wait for indexing to finish (the spinner will stop)
5. Go to the **Chat** area and ask a question!

**Example questions to try:**
- *"What are the main findings of this paper?"*
- *"Summarise the key arguments"*
- Or just type: `briefing` → automatic full briefing
- Or type: `quiz` → 10-question quiz from your documents

---

## Troubleshooting

### "Python not found" error
Download and install Python from [python.org](https://python.org). During installation, **tick the box "Add Python to PATH"**, then re-run `install.bat`.

### App doesn't open in browser
Open your browser manually and go to: `http://localhost:8080`

### "Port 8080 already in use" error
Another app is using port 8080. Add this line to your `.env` file:
```
WEBAPP_PORT=8081
```
Then restart with `start.bat` and open `http://localhost:8081`.

### AI gives no answer / "No sources loaded"
You need to add at least one source to your project first. Go to the Sources tab and upload a PDF or paste a URL.

### Ollama not starting
1. Download Ollama manually from [ollama.com](https://ollama.com)
2. Install and run it (it appears in the system tray)
3. Then restart with `start.bat`

### Packages failed to install
Run `install.bat` as Administrator:
- Right-click `install.bat`
- Select **Run as administrator**

### The app is slow with local AI
Local AI (Ollama) runs on your CPU, which is slower. Add a free cloud API key (see Step 3) for much faster responses. Or if your PC has an NVIDIA GPU, Ollama will use it automatically.

---

## Updating the App

When a new version is released:

1. Download the new ZIP from GitHub (or `git pull` if you used Git)
2. Copy your `.env` file and `data/` folder from the old version to the new one
3. Run `install.bat` again to update packages
4. Start with `start.bat`

> Your research projects are saved in the `data/` folder. Keep this folder safe — it's your data!

---

## Where Your Data Is Stored

```
ResearchNotebookLM/
├── data/
│   ├── projects/     ← Your research projects and notes
│   ├── chroma/       ← AI search index (your document vectors)
│   ├── providers.json ← Your AI API keys (never shared)
│   └── trash/        ← Deleted projects (recoverable)
└── .env              ← App settings
```

**Nothing is uploaded to the cloud.** Your documents, notes, and API keys stay on your computer only.

---

## Manual Setup (Mac / Linux)

If you're on Mac or Linux, follow these steps in a terminal:

**Prerequisites:**
- Python 3.10 or newer (`python3 --version`)
- [Ollama](https://ollama.com) (optional but recommended)

**Install:**
```bash
# Clone the repo
git clone https://github.com/pavelblank/ResearchNotebookLLM.git
cd ResearchNotebookLLM

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Copy config
cp .env.example .env
cp data/providers.example.json data/providers.json

# (Optional) Pull a local AI model
ollama pull qwen2.5:3b

# Start the app
python webapp/app.py
```

Then open `http://localhost:8080` in your browser.

---

## Security Notes

- The app binds to **localhost only** — it's not accessible from other devices on your network
- API keys are stored locally in `data/providers.json` and never transmitted except to the AI provider you configured
- Your documents are indexed locally in `data/chroma/` — no cloud storage
- The `.env` and `data/providers.json` files are excluded from Git and will never be uploaded to GitHub

---

## Need Help?

Open an issue on GitHub: `https://github.com/pavelblank/ResearchNotebookLLM/issues`

Include:
- What step you're on
- The exact error message
- Your Windows version (`winver` in the search bar)
