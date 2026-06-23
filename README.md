<div align="center">

<br>

<img src="https://img.shields.io/badge/🔬-ResearchNotebookLM-7C75F5?style=for-the-badge&labelColor=0d0d0d" alt="ResearchNotebookLM" height="42">

<h3>Your Private AI Research Assistant</h3>
<p><strong>Better than Google NotebookLM. Runs 100% on your own machine.</strong></p>

<br>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Local_Vector_DB-FF6B2C?style=flat-square)](https://www.trychroma.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE-MIT)
[![Version](https://img.shields.io/badge/Version-v3.0-7C75F5?style=flat-square)](https://github.com/pavelblank/ResearchNotebookLLM/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows_%7C_Mac_%7C_Linux-555?style=flat-square&logo=windows)](https://github.com/pavelblank/ResearchNotebookLM)

<br>

<table>
<tr>
<td align="center">📄<br><strong>Upload PDFs</strong><br><sub>URLs & YouTube too</sub></td>
<td align="center">💬<br><strong>Ask Questions</strong><br><sub>AI answers from your docs</sub></td>
<td align="center">🔒<br><strong>100% Private</strong><br><sub>Zero data leaves your PC</sub></td>
<td align="center">🔗<br><strong>12 AI Engines</strong><br><sub>Never goes offline</sub></td>
</tr>
</table>

<br>

> **No Docker. No cloud account. No subscription. No data upload.**
> Everything runs on your machine, even the AI.

<br>

**[🚀 Quick Start](#-quick-start) · [✨ Features](#-features-in-detail) · [📋 Prerequisites](#-prerequisites) · [⚙️ Settings](#%EF%B8%8F-settings--configuration) · [🔒 Security](#-security) · [📁 Structure](#-project-structure)**

</div>

<br>

---

## 📸 Screenshots

<table>
<tr>
<td align="center" width="33%">
<img src="docs/screenshots/home.png" alt="Home Page" width="260"><br>
<sub><strong>🏠 Home</strong>: projects, stats, sidebar clock</sub>
</td>
<td align="center" width="33%">
<img src="docs/screenshots/chat.png" alt="Research Chat" width="260"><br>
<sub><strong>💬 Research Chat</strong>: grounded AI answers</sub>
</td>
<td align="center" width="33%">
<img src="docs/screenshots/settings.png" alt="Settings" width="260"><br>
<sub><strong>⚙️ Settings</strong>: AI engines, timezone, clock</sub>
</td>
</tr>
</table>

---

## 💡 Why ResearchNotebookLM?

> *"I was doing serious research: 30+ papers, 3 projects. Google NotebookLM was uploading everything to Google's servers. I wanted the same power, but private, free, and mine."*
> - Pavel Blank, creator

**The problem with cloud research tools:**

- 📤 **Your documents leave your machine** the moment you upload them
- 🔒 **You're locked to one AI.** Google only offers Gemini, nothing else
- 💸 **Free tiers run out** when you actually need them
- 📶 **Requires constant internet.** No wifi, no research
- 🏢 **Their servers, their rules.** What happens to your data?

**ResearchNotebookLM is the answer:**

- ✅ PDFs, notes, and chat history never leave your disk
- ✅ 12 AI engines: OpenRouter, NVIDIA, DeepSeek, Gemma, or run 100% offline with Ollama
- ✅ No subscription, no limits, no account required
- ✅ Works on a plane, in a hospital, in a lab with no internet required
- ✅ Open source, so you can audit every line and change anything

---

## 🆚 ResearchNLM vs Google NotebookLM

<table>
<thead>
<tr>
<th>Feature</th>
<th align="center">ResearchNotebookLM</th>
<th align="center">Google NotebookLM</th>
</tr>
</thead>
<tbody>
<tr><td>🔒 Your data stays on your machine</td><td align="center">✅ Always</td><td align="center">❌ Uploaded to Google</td></tr>
<tr><td>🤖 Choose your AI model</td><td align="center">✅ 12 providers + local Ollama</td><td align="center">❌ Gemini only</td></tr>
<tr><td>💰 Free to use</td><td align="center">✅ Free (use your own keys)</td><td align="center">⚠️ Limited free tier</td></tr>
<tr><td>📁 Unlimited projects</td><td align="center">✅ No limits</td><td align="center">⚠️ Capped</td></tr>
<tr><td>🌐 Works offline</td><td align="center">✅ Ollama local fallback</td><td align="center">❌ Needs internet</td></tr>
<tr><td>🔧 Self-hostable</td><td align="center">✅ Your server</td><td align="center">❌ Google's cloud</td></tr>
<tr><td>📝 Notes system</td><td align="center">✅ Built-in, expandable cards</td><td align="center">✅ Built-in</td></tr>
<tr><td>🎥 YouTube ingestion</td><td align="center">✅ Auto captions via yt-dlp</td><td align="center">✅ Yes</td></tr>
<tr><td>🕐 Sidebar clock & timezone</td><td align="center">✅ Configurable</td><td align="center">❌ No</td></tr>
<tr><td>🔍 Cross-project file search</td><td align="center">✅ Search files across all projects</td><td align="center">❌ Per-notebook only</td></tr>
<tr><td>🛡️ API key security</td><td align="center">✅ Masked in browser, never exposed</td><td align="center">N/A</td></tr>
</tbody>
</table>

---

## ✨ Features in Detail

<table>
<tr>
<td width="50%">

### 🤖 AI-Grounded Chat
- Answers come **only** from your uploaded documents
- AI is explicitly forbidden from using training data or outside knowledge
- Says *"Not found in provided sources"* if the answer is not there
- Cites the source title for every fact

</td>
<td width="50%">

### 🔗 12-Engine Fallback Chain
- Providers are tried in order; if one fails, the next takes over automatically
- Handles rate limits, outages, timeouts, and bad responses
- Final fallback: **local Ollama** (works with no internet)
- The system **never stops** mid-session

</td>
</tr>
<tr>
<td>

### ✨ Do More — AI Actions in Chat
Select one or more sources, then click any action — results appear instantly in Research Chat. Works from the right panel or the mobile bottom sheet:
| Action | Output |
|--------|--------|
| 📋 Briefing | Executive summary + key findings |
| 🏷️ Key Themes | 5+ themes with evidence per source |
| ❓ FAQ | 8 grounded questions & answers |
| 📅 Timeline | Chronological events with dates |
| 🗺 Mind Map | Hierarchical text knowledge tree |
| ❓ Quiz | 10-question multiple-choice test |
| 🃏 Flashcards | 12 study cards — Term / Definition |
| 📊 Knowledge Stats | Concept scores, gaps, source overview |

> **Type a keyword in chat** (`quiz`, `briefing`, `flashcard`, `timeline`…) and it auto-expands to the full action — with your selected source scope applied.

</td>
<td>

### 📄 Multi-Source Ingestion
| Type | Engine |
|------|--------|
| PDF | Docling (OCR + tables) with pypdf fallback |
| Web URL | Trafilatura (full article text) |
| YouTube | yt-dlp (auto captions) |
| Text / Markdown | Direct paste or file upload |

</td>
</tr>
<tr>
<td>

### 📖 Source Viewer
- **PDF button** to read the original extracted text
- **MD button** to view AI-converted Markdown (tables, headings preserved)
- Opens in the left panel; the chat area stays full width

</td>
<td>

### 📝 Notes System
- Save any AI answer as a note in one click
- Write your own manual notes
- Click a note card to **expand** the full content
- Notes persist between sessions, stored per project

</td>
</tr>
<tr>
<td>

### 🔍 Smart Search
- Searches **project names** and **files inside projects**
- Results show file name and parent project
- Click to navigate directly
- Real-time as you type

</td>
<td>

### 🕐 Sidebar Clock & Timezone
- Live time and date displayed in the sidebar
- Fully configurable timezone (25+ regions)
- Gear icon links directly to Clock settings
- Stored in your browser, per-user, no server needed

</td>
</tr>
<tr>
<td>

### 🗑️ Trash & Restore
- Deleting a project moves it to Trash (not permanent)
- Restore from Settings > Trash at any time
- Permanently delete when you are sure
- Project data fully preserved until permanent delete

</td>
<td>

### 📊 Workspace Stats
- Home page shows total Projects, Sources, and Notes at a glance
- Per-project source count shown in sidebar (not chunk count)
- "How it works" guide shown for new users

</td>
</tr>
</table>

---

## 📋 Prerequisites

> **Nothing complex.** You only need Python installed. Everything else is optional.

<table>
<thead>
<tr><th>Requirement</th><th>Version</th><th>Required?</th><th>Notes</th></tr>
</thead>
<tbody>
<tr><td><strong>Python</strong></td><td>3.10+</td><td>✅ Yes</td><td><a href="https://python.org/downloads">python.org/downloads</a></td></tr>
<tr><td><strong>Ollama</strong></td><td>Any</td><td>⭐ Recommended</td><td>Local AI fallback. Get it at <a href="https://ollama.ai">ollama.ai</a></td></tr>
<tr><td><strong>OpenRouter key</strong></td><td>n/a</td><td>💡 Optional</td><td>Free tier available, with much better AI quality</td></tr>
<tr><td><strong>NVIDIA NIM key</strong></td><td>n/a</td><td>💡 Optional</td><td>Free GPU inference. See <a href="https://build.nvidia.com">build.nvidia.com</a></td></tr>
<tr><td><strong>RAM</strong></td><td>4 GB min</td><td>✅ Yes</td><td>8 GB recommended for large PDFs</td></tr>
<tr><td><strong>Disk</strong></td><td>~3 GB</td><td>✅ Yes</td><td>~2 GB for local AI model + your documents</td></tr>
</tbody>
</table>

---

## 🚀 Quick Start

### ⚡ Windows: One Click

<table>
<tr>
<td>

```
Step 1 │ Download this repo
       │ Click green "Code" button > Download ZIP
       │ Extract to any folder

Step 2 │ Double-click  install.bat
       │ Installs Python packages + Ollama
       │ (takes ~5 min on first run)

Step 3 │ Double-click  start.bat
       │ Browser opens automatically

Step 4 │ Open  http://localhost:8080
       │ You're ready to research 🎉
```

</td>
<td align="center">

**That's it.**<br><br>
No Docker.<br>
No cloud account.<br>
No terminal needed.<br><br>
Just double-click and go.<br><br>
📖 **[Full Setup Guide → SETUP.md](SETUP.md)**<br>
<sub>Step-by-step for non-technical users</sub>

</td>
</tr>
</table>

---

### 🛠️ Manual Install (All Platforms)

<details>
<summary><strong>🪟 Windows: Step by Step</strong></summary>

```bash
# 1. Clone the repo
git clone https://github.com/pavelblank/ResearchNotebookLM.git
cd ResearchNotebookLM

# 2. Install Python packages
pip install -r requirements.txt

# 3. Install Ollama (local AI)
winget install Ollama.Ollama

# 4. Pull a local model (~2 GB)
ollama pull qwen2.5:3b

# 5. Copy config files
copy .env.example .env
copy data\providers.example.json data\providers.json

# 6. Run
python webapp\app.py
```
Then open: **http://localhost:8080**

</details>

<details>
<summary><strong>🍎 macOS: Step by Step</strong></summary>

```bash
# 1. Clone the repo
git clone https://github.com/pavelblank/ResearchNotebookLM.git
cd ResearchNotebookLM

# 2. Install Python packages
pip3 install -r requirements.txt

# 3. Install Ollama
brew install ollama

# 4. Pull a local model (~2 GB)
ollama pull qwen2.5:3b

# 5. Copy config files
cp .env.example .env
cp data/providers.example.json data/providers.json

# 6. Run
ollama serve &
python3 webapp/app.py
```
Then open: **http://localhost:8080**

</details>

<details>
<summary><strong>🐧 Linux: Step by Step</strong></summary>

```bash
# 1. Clone the repo
git clone https://github.com/pavelblank/ResearchNotebookLM.git
cd ResearchNotebookLM

# 2. Install Python packages
pip3 install -r requirements.txt

# 3. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 4. Pull a local model (~2 GB)
ollama pull qwen2.5:3b

# 5. Copy config files
cp .env.example .env
cp data/providers.example.json data/providers.json

# 6. Run
ollama serve &
python3 webapp/app.py
```
Then open: **http://localhost:8080**

</details>

> ⚠️ **First install note:** Docling (PDF engine) downloads OCR models (~15 MB) on first PDF upload. This is a one-time download. All future uploads are fast.

---

## 🔑 Getting Free API Keys

> The app works with Ollama only, no keys needed. But free cloud keys give significantly better AI quality.

<table>
<tr>
<td width="50%">

### OpenRouter
**50+ free models (Gemini, Llama, Qwen, etc.)**

1. Go to [openrouter.ai](https://openrouter.ai) and sign up
2. Dashboard > Keys > **Create Key**
3. Copy the key (`sk-or-...`)
4. App > **Settings > AI Engines** > paste key

*Free tier includes Gemini 2.5 Flash, Llama 3, Qwen and more*

</td>
<td width="50%">

### NVIDIA NIM
**Free GPU inference, no credit card needed**

1. Go to [build.nvidia.com](https://build.nvidia.com) and sign up
2. Click **Get API Key**
3. Copy the key (`nvapi-...`)
4. App > **Settings > AI Engines** > paste key

*Free tier includes DeepSeek, Gemma, GLM, MiniMax and more*

</td>
</tr>
</table>

---

## 🏗️ How It Works

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                    YOUR DOCUMENT COMES IN                        │
  │                                                                  │
  │   PDF  ──▶  Docling (OCR + tables + headings)  ──▶  Markdown    │
  │   URL  ──▶  Trafilatura (full article text)     ──▶  Plain text  │
  │   YouTube ▶  yt-dlp (auto captions)             ──▶  Transcript  │
  └─────────────────────────────┬───────────────────────────────────┘
                                │  text chunks
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                   ChromaDB  (local vector DB)                    │
  │   Text is split into chunks and stored as embeddings on disk     │
  └─────────────────────────────┬───────────────────────────────────┘
                                │
                    You ask a question
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │              Semantic Search (cosine similarity)                 │
  │         Top 8 most relevant chunks retrieved                     │
  └─────────────────────────────┬───────────────────────────────────┘
                                │  source excerpts
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                    AI Fallback Chain                             │
  │                                                                  │
  │  1. OpenRouter  ──fail──▶  2. NVIDIA NIM  ──fail──▶  3. ...    │
  │                                               ──fail──▶  Ollama │
  │                                                                  │
  │  Each failure is handled silently; next provider takes over      │
  └─────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
         Answer grounded strictly in YOUR source excerpts
         AI cannot use internet, training data, or memory
```

---

## ⚙️ Settings & Configuration

### In-App Settings

Open the app and click **⚙️ Settings** in the sidebar.

| Section | What You Can Do |
|---------|----------------|
| **AI Engines** | Add, remove, enable/disable, reorder providers |
| **Clock & Timezone** | Choose your local timezone for the sidebar clock |
| **Deleted Projects** | Restore or permanently delete from Trash |

---

### Configuring AI Providers (`data/providers.json`)

<details>
<summary><strong>Click to see full providers.json format</strong></summary>

```json
{
  "providers": [
    {
      "id": "p1",
      "name": "OR Gemini 2.5 Flash",
      "description": "Often free on OpenRouter",
      "url": "https://openrouter.ai/api/v1",
      "model": "google/gemini-2.5-flash",
      "api_key": "sk-or-YOUR_KEY_HERE",
      "enabled": true
    },
    {
      "id": "p2",
      "name": "NV DeepSeek V4",
      "description": "Free NVIDIA inference",
      "url": "https://integrate.api.nvidia.com/v1",
      "model": "deepseek-ai/deepseek-v4-flash",
      "api_key": "nvapi-YOUR_KEY_HERE",
      "enabled": true
    },
    {
      "id": "p3",
      "name": "Ollama Local",
      "description": "No key needed, works offline",
      "url": "http://localhost:11434",
      "model": "qwen2.5:3b",
      "api_key": "ollama",
      "enabled": true,
      "is_ollama": true
    }
  ]
}
```

**Field reference:**

| Field | Required | Description |
|-------|:--------:|-------------|
| `id` | ✅ | Any unique string |
| `name` | ✅ | Display name in UI |
| `url` | ✅ | Base API URL (any OpenAI-compatible endpoint) |
| `model` | ✅ | Model ID for this provider |
| `api_key` | ✅ | Your key, or `"ollama"` for local |
| `enabled` | ✅ | `true` to use, `false` to skip |
| `is_ollama` | optional | `true` only for local Ollama entries |

> Any OpenAI-compatible API works: Groq, Together AI, Mistral, self-hosted vLLM, etc.

</details>

---

### 📍 Where to Update for New Versions

| What changed | File to update | Action needed |
|-------------|---------------|--------------|
| New Python package added | `requirements.txt` | `pip install -r requirements.txt` |
| New AI provider available | `data/providers.json` | Add via Settings > AI Engines |
| UI / template change | `webapp/templates/*.html` | Browser refresh (auto-reloads) |
| Backend logic change | `webapp/app.py` or `engine/*.py` | Restart: `stop.bat` then `start.bat` |
| New version released | Auto-updated | `git pull origin main` then restart |

```bash
# To update to latest version
git pull origin main
pip install -r requirements.txt
# Then restart start.bat
```

---

## 📁 Project Structure

```
ResearchNotebookLM/
│
├── 📄 README.md                   ← You are here
├── 📄 requirements.txt            ← All Python dependencies
├── 📄 .env.example                ← Environment config template
├── 📄 LICENSE                     ← Apache 2.0
├── 📄 LICENSE-MIT                 ← MIT License
├── 📖 SETUP.md                    ← Full non-technical setup guide
│
├── 🪟 install.bat                 ← Windows one-click installer
├── 📜 install.ps1                 ← Windows PowerShell installer script
├── ▶️  start.bat                   ← Windows: start the app
├── ⏹️  stop.bat                    ← Windows: stop the app
│
├── 📁 docs/
│   └── 📁 screenshots/            ← App screenshots (used in README)
│
├── 📁 webapp/                     ← Flask web application
│   ├── 📄 app.py                  ← Main server (all routes + API endpoints)
│   └── 📁 templates/              ← HTML templates (Jinja2)
│       ├── 📄 base.html           ← Shared layout: sidebar, topbar, search, JS
│       ├── 📄 index.html          ← Home page with project list + stats
│       ├── 📄 notebook.html       ← Workspace: sources, chat, notes
│       └── 📄 settings.html       ← AI engines, clock/timezone, trash
│
├── 📁 engine/                     ← AI and data processing core
│   ├── 📄 rag.py                  ← Fallback chain + RAG query engine
│   ├── 📄 ingest.py               ← PDF / URL / YouTube to ChromaDB
│   └── 📄 db.py                   ← ChromaDB vector store manager
│
└── 📁 data/                       ← Auto-created on first run
    ├── 📄 providers.example.json  ← Copy to providers.json, then add your keys
    ├── 📁 chroma/                 ← Vector DB (your indexed documents)
    ├── 📁 projects/               ← Projects, uploads, notes, chat history
    └── 📁 trash/                  ← Soft-deleted projects (restorable)
```

---

## 🔒 Security

<table>
<tr>
<td width="60%">

### Protections Built In

| Threat | How It's Handled |
|--------|-----------------|
| 📁 **Path traversal on upload** | `secure_filename()` strips `../` from all filenames |
| 🦠 **Malicious file types** | Whitelist: only `.pdf` `.txt` `.md` accepted |
| 💾 **Oversized uploads** | Hard 100 MB limit |
| 🔑 **API key theft** | Keys masked in browser (`sk-ab***cdef`); the raw key is never sent to the frontend |
| 💉 **Meta injection** | Project metadata endpoint whitelists allowed keys only |
| 🗂️ **Trash path traversal** | Path validated against trash directory before any operation |
| 🤖 **AI hallucination** | System prompt explicitly forbids outside knowledge and training data |
| 💥 **All providers fail** | Caught and returns a clean `503` error instead of crashing Flask |

</td>
<td width="40%">

### Data Privacy

```
✅  Projects stored on your disk
✅  Vector DB runs locally (ChromaDB)
✅  API keys never committed to git
✅  data/providers.json in .gitignore
✅  Masked keys in Settings UI
✅  No telemetry, no analytics
✅  No accounts required
```

</td>
</tr>
</table>

### Running Publicly (e.g. behind Cloudflare Tunnel)

If you expose the app online, **add authentication at the edge**. The app has no built-in login system:

```
Recommended: Cloudflare Access (Zero Trust) - free, easy, blocks all
             unauthenticated access before it reaches your app
```

> ⚠️ Without edge auth, anyone who knows your URL can use the app and access Settings.

---

## 🗺️ Roadmap

### ✅ Shipped

- [x] 12-provider AI fallback chain
- [x] PDF / URL / YouTube ingestion
- [x] Notes system with expandable cards
- [x] Cross-project file search
- [x] API key masking (security)
- [x] Trash & restore
- [x] Sidebar clock & timezone settings
- [x] Home page stats (projects / sources / notes)
- [x] AI grounding (strictly source-only answers)
- [x] Mind Map: interactive knowledge graph (vis.js)
- [x] Quiz: auto-generated multiple-choice questions
- [x] Flashcards: flip-card study deck with keyboard navigation

### 🔜 Coming Next

- [ ] Suggested Questions: auto-generates 5 research questions when a project opens
- [ ] Mac/Linux one-click install script (`install.sh`)
- [ ] Export session as PDF or Markdown
- [ ] Source deduplication on upload
- [ ] Dark/light theme toggle

---

## 📅 Changelog

### v3.0 (June 2026)
- **Do More panel**: 8 one-click action buttons (Briefing, Themes, FAQ, Timeline, Mind Map, Quiz, Flashcards, Knowledge Stats) — all trigger rich AI responses in the Research Chat
- **Research Chat as primary screen**: all AI outputs — including structured quiz, flashcards, mind map, and knowledge analysis — appear inline in chat
- **Quiz format**: properly structured 10-question multiple-choice with answers and explanations
- **Flashcards format**: 12-card Term/Definition deck with source attribution
- **Mind Map format**: hierarchical text concept map with branches and subtopics
- **Knowledge Stats**: concept importance scores, overview, and knowledge gaps
- **12-hour clock (AM/PM)** in sidebar and Settings
- **Do More panel**: default visible, hide/show button in panel header plus floating right-edge tab
- **Responsive layout**: mobile, tablet, and large screen CSS improvements; no overlapping elements
- **Confirmation on chat clear**: prevents accidental deletion
- **MIT licence** added alongside Apache 2.0

### v2.2 (June 2026)
- **Mind Map tab**: vis.js force-directed knowledge graph extracted from your sources
- **Quiz tab**: AI-generated multiple-choice questions with scoring and explanations
- **Flashcards tab**: flip-card study deck with keyboard navigation (arrow keys + space to flip)
- **Backend caching**: graph, quiz, and flashcard results cached per project

### v2.1 (June 2026)
- **Security hardening**: path traversal protection, file type whitelist, 100 MB upload limit, API key masking, trash path validation
- **AI grounding strengthened**: system prompt now explicitly forbids outside knowledge and training data
- **Sidebar clock & timezone**: live clock with configurable timezone (25+ regions)
- **Home page stats strip**: total projects, sources, and notes at a glance
- **Smart Search**: searches project names and files within projects in real time
- **Source count fix**: sidebar now shows real source file count, not ChromaDB chunk count
- **Note cards**: click to expand full content (was truncated to 300 chars)
- **Model indicator**: single status dot in topbar (green = active, red = unavailable)
- **Settings**: new Clock & Timezone tab added

### v2.0 (May 2026) - Initial public release
- Flask web app with full project management
- 12-provider AI fallback chain with Ollama local fallback
- PDF / URL / YouTube ingestion pipeline
- ChromaDB vector search
- Do More AI actions (Briefing, Themes, FAQ, Timeline, Mind Map, Quiz, Flashcards, Knowledge Stats)
- Notes system, Trash & Restore
- Windows one-click installer

---

## 🛠️ Troubleshooting

<details>
<summary><strong>App won't start</strong></summary>

```bash
# Check Python version (needs 3.10+)
python --version

# Reinstall packages
pip install -r requirements.txt

# Check if port is in use
netstat -ano | findstr :8080      # Windows
lsof -i :8080                     # Mac/Linux
```

</details>

<details>
<summary><strong>"All AI engines unavailable" error</strong></summary>

- Go to **Settings > AI Engines**. At least one provider must have `enabled: true`
- If using Ollama only: make sure it is running with `ollama serve`
- If using API keys: verify the keys are valid and the service is up

</details>

<details>
<summary><strong>First PDF upload is slow (1-2 min)</strong></summary>

This is normal. Docling downloads OCR models (~15 MB) once on first use.
All future uploads are fast.

</details>

<details>
<summary><strong>Sources disappeared after restart</strong></summary>

Your data lives in the `data/` folder. Never delete this folder.
If you moved the project folder, the ChromaDB path may be broken.
Run the app from the original install location.

</details>

<details>
<summary><strong>Port 8080 already in use</strong></summary>

```bash
# Windows
stop.bat
# or:
netstat -ano | findstr :8080
taskkill /PID <pid> /F

# Mac/Linux
kill $(lsof -t -i:8080)
```

</details>

<details>
<summary><strong>Ollama model not found</strong></summary>

```bash
ollama list              # see what's installed
ollama pull qwen2.5:3b   # install the default model
```

</details>

---

## 🤝 Contributing

Contributions are welcome!

```bash
# 1. Fork this repo
# 2. Create your branch
git checkout -b feature/your-idea

# 3. Make changes & commit
git commit -m "add: your feature description"

# 4. Push and open a Pull Request
git push origin feature/your-idea
```

Found a bug? Open an [Issue](https://github.com/pavelblank/ResearchNotebookLM/issues) with steps to reproduce.

---

## 📜 License (MIT) & Apache 2.0

- **[MIT License](LICENSE-MIT)** — free to use, copy, modify, distribute, no conditions
- **[Apache 2.0 License](LICENSE)** — includes patent grant and attribution requirements

Copyright 2026 Pavel Blank. Dual-licensed — use whichever suits your project.

---

## 🧰 Built With

<table>
<tr>
<td align="center"><a href="https://flask.palletsprojects.com"><img src="https://img.shields.io/badge/Flask-Web_Framework-000?style=flat-square&logo=flask" alt="Flask"></a></td>
<td align="center"><a href="https://www.trychroma.com"><img src="https://img.shields.io/badge/ChromaDB-Vector_Database-FF6B2C?style=flat-square" alt="ChromaDB"></a></td>
<td align="center"><a href="https://github.com/DS4SD/docling"><img src="https://img.shields.io/badge/Docling-PDF_Engine-blue?style=flat-square" alt="Docling"></a></td>
</tr>
<tr>
<td align="center"><a href="https://ollama.ai"><img src="https://img.shields.io/badge/Ollama-Local_AI-white?style=flat-square" alt="Ollama"></a></td>
<td align="center"><a href="https://marked.js.org"><img src="https://img.shields.io/badge/marked.js-Markdown-yellow?style=flat-square" alt="marked.js"></a></td>
<td align="center"><a href="https://trafilatura.readthedocs.io"><img src="https://img.shields.io/badge/Trafilatura-Web_Scraper-green?style=flat-square" alt="Trafilatura"></a></td>
</tr>
</table>

---

<div align="center">

<br>

Built by **[Pavel Blank](https://github.com/pavelblank)**

<br>

**If this project helps your research, give it a star. It helps other researchers find it.**

<br>

[![Star](https://img.shields.io/github/stars/pavelblank/ResearchNotebookLM?style=social)](https://github.com/pavelblank/ResearchNotebookLM/stargazers)

</div>
