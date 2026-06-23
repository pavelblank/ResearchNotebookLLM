"""
Research NotebookLM — Web UI + API (v3.0)
Author: Pavel Blank <pavelblank@gmail.com>
Run: python webapp/app.py
Open: http://localhost:8080
"""

import os, sys, time, shutil, json, secrets
os.environ["OLLAMA_HOST"] = "http://127.0.0.1:11434"
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Make engine importable
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from engine.db import list_notebooks, list_sources, delete_notebook, get_or_create_notebook, delete_source, get_source_title
from engine.ingest import ingest_pdf, ingest_url, ingest_youtube, ingest_text
from engine.rag import ask, ask_with_sources, summarise_sources, generate_guide, generate_source_summary, detect_best_model, detect_engine, get_provider_status, _load_providers, _save_providers
from dotenv import dotenv_values, set_key

app = Flask(__name__)
# Load secret key from .env; generate a random one if not set (safe for local-only use)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB upload limit
# Restrict CORS to localhost only — prevents other websites from reading your data
_cors_origins = [o.strip() for o in os.environ.get(
    'CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080'
).split(',') if o.strip()]
CORS(app, origins=_cors_origins)

ALLOWED_UPLOAD_EXTENSIONS = {'.pdf', '.txt', '.md'}
_META_ALLOWED_KEYS = {'name', 'description', 'tags', 'created'}

ENV_FILE   = ROOT / ".env"
OUTPUT_DIR = ROOT / "output"
PROJECTS_DIR = ROOT / "data" / "projects"
TRASH_DIR    = ROOT / "data" / "trash"

# ── Persistent chat history (saved to disk per project) ────────────────────
_chat_cache: dict[str, list] = {}  # in-memory cache, loaded from disk


def _chat_file(notebook: str) -> Path:
    """Path to the chat history JSON file for a notebook."""
    pdir = _project_dir(notebook)
    pdir.mkdir(parents=True, exist_ok=True)
    return pdir / "chat_history.json"


def _load_chat(notebook: str) -> list:
    """Load chat history from disk (with in-memory cache)."""
    if notebook in _chat_cache:
        return _chat_cache[notebook]
    cf = _chat_file(notebook)
    if cf.exists():
        try:
            data = json.loads(cf.read_text(encoding="utf-8"))
            _chat_cache[notebook] = data
            return data
        except Exception:
            pass
    _chat_cache[notebook] = []
    return []


def _save_chat(notebook: str):
    """Persist chat history to disk."""
    history = _chat_cache.get(notebook, [])
    cf = _chat_file(notebook)
    cf.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_chat(notebook: str, q: str, a: str):
    """Append a turn and auto-save."""
    if notebook not in _chat_cache:
        _chat_cache[notebook] = []
    _chat_cache[notebook].append({
        "q": q, "a": a,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    _save_chat(notebook)


def _get_chat_summary(history: list) -> str:
    """Build a context summary from older turns (beyond the recent window)."""
    if len(history) <= 10:
        return ""
    older = history[:-10]
    lines = ["PREVIOUS DISCUSSION SUMMARY:"]
    for turn in older:
        lines.append(f"Q: {turn['q'][:120]}")
        lines.append(f"A: {turn['a'][:200]}")
        lines.append("---")
    return "\n".join(lines)


def load_env():
    if ENV_FILE.exists():
        return dotenv_values(ENV_FILE)
    return {}


# -- Project folder management -----------------------------------------------

def _safe_name(name: str) -> str:
    """Convert notebook name to safe folder name."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name).strip("_")


def _project_dir(notebook: str) -> Path:
    """Return the project directory for a notebook."""
    return PROJECTS_DIR / _safe_name(notebook)


def _ensure_project_dirs(notebook: str):
    """Create project folder structure if it doesn't exist."""
    pdir = _project_dir(notebook)
    (pdir / "sources").mkdir(parents=True, exist_ok=True)
    (pdir / "notes").mkdir(parents=True, exist_ok=True)
    (pdir / "exports").mkdir(parents=True, exist_ok=True)
    return pdir


def _get_project_meta(notebook: str) -> dict:
    """Read project metadata from disk."""
    pdir = _project_dir(notebook)
    meta_file = pdir / "meta.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "name": notebook,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": "",
        "tags": [],
    }


def _save_project_meta(notebook: str, meta: dict):
    """Save project metadata to disk."""
    pdir = _project_dir(notebook)
    pdir.mkdir(parents=True, exist_ok=True)
    meta_file = pdir / "meta.json"
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def _list_project_files(notebook: str) -> list[dict]:
    """List source files in a project."""
    pdir = _project_dir(notebook)
    sources_dir = pdir / "sources"
    if not sources_dir.exists():
        return []
    files = []
    for f in sorted(sources_dir.iterdir()):
        if f.is_file() and f.name != "README.md":
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": time.strftime("%Y-%m-%d %H:%M", time.localtime(f.stat().st_mtime)),
            })
    return files


# -- Pages ------------------------------------------------------------------

@app.route("/")
def index():
    notebooks = list_notebooks()
    # Enrich with project metadata
    for nb in notebooks:
        meta = _get_project_meta(nb["name"])
        nb["description"] = meta.get("description", "")
        nb["created"] = meta.get("created", "")
        nb["source_count"] = len(_list_project_files(nb["name"]))
    for nb in notebooks:
        nb["count"] = nb.get("source_count", 0)
    total_sources = sum(nb.get("source_count", 0) for nb in notebooks)
    total_notes   = sum(len(_load_notes(nb["name"])) for nb in notebooks)
    model = detect_best_model()
    engine = detect_engine()
    return render_template("index.html", notebooks=notebooks, model=model, engine=engine,
                           total_sources=total_sources, total_notes=total_notes)


@app.route("/notebook/")
@app.route("/notebook")
def notebook_empty():
    return redirect("/")


@app.route("/notebook/<name>")
def notebook_view(name):
    # Redirect to home if name is blank or contains no usable characters
    if not name or not any(c.isalnum() or c in "-_" for c in name):
        return redirect("/")
    # Redirect to home if this notebook doesn't actually exist
    notebooks = list_notebooks()
    known_ids = {nb["id"] for nb in notebooks}
    if name not in known_ids:
        return redirect("/")
    sources = list_sources(name)
    history = _load_chat(name)
    meta = _get_project_meta(name)
    files = _list_project_files(name)
    notes = _load_notes(name)
    model = detect_best_model()
    engine = detect_engine()
    for nb in notebooks:
        m = _get_project_meta(nb["name"])
        nb["description"] = m.get("description", "")
        nb["count"] = len(_list_project_files(nb["name"]))
    # Flag which sources have a Docling-converted .md file available
    sources_dir = _project_dir(name) / "sources"
    for s in sources:
        md_path = sources_dir / (s["title"] + ".md")
        s["has_md"] = md_path.exists()
    return render_template("notebook.html", notebook=name, sources=sources,
                           history=history, model=model, engine=engine,
                           meta=meta, files=files, notebooks=notebooks, notes=notes)


@app.route("/settings")
def settings_page():
    providers_file = ROOT / "data" / "providers.json"
    if providers_file.exists():
        data = json.loads(providers_file.read_text(encoding="utf-8"))
        engines = data.get("providers", [])
    else:
        engines = []
    # List trash items
    trash_items = []
    if TRASH_DIR.exists():
        for item in sorted(TRASH_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if item.is_dir():
                meta_file = item / "meta.json"
                meta = {}
                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                trash_items.append({
                    "id": item.name,
                    "name": meta.get("name", item.name),
                    "deleted_at": meta.get("deleted_at", ""),
                    "source_count": meta.get("source_count", 0),
                })
    notebooks = list_notebooks()
    for nb in notebooks:
        nb["count"] = len(_list_project_files(nb["name"]))
    return render_template("settings.html", engines=engines, trash_items=trash_items,
                           notebooks=notebooks)


# -- API: Providers ---------------------------------------------------------

def _mask_key(key: str) -> str:
    """Mask an API key so it's safe to send to the browser."""
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return key[:4] + "***" + key[-4:]


@app.route("/api/providers", methods=["GET"])
def api_providers_get():
    from engine.rag import PROVIDERS_FILE
    if PROVIDERS_FILE.exists():
        data = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
        providers = data.get("providers", [])
        # Never send raw API keys to the browser
        masked = []
        for p in providers:
            p2 = dict(p)
            p2["api_key"] = _mask_key(p2.get("api_key", ""))
            masked.append(p2)
        return jsonify(masked)
    return jsonify([])


@app.route("/api/providers", methods=["POST"])
def api_providers_save():
    from engine.rag import PROVIDERS_FILE
    data = request.json
    new_providers = data.get("providers", [])
    # Load original providers to restore masked keys
    existing_by_id = {}
    if PROVIDERS_FILE.exists():
        try:
            old = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
            for p in old.get("providers", []):
                existing_by_id[p.get("id", "")] = p
        except Exception:
            pass
    for p in new_providers:
        key = p.get("api_key", "")
        if "***" in key:
            # Key was masked — restore original from file
            orig = existing_by_id.get(p.get("id", ""), {})
            p["api_key"] = orig.get("api_key", "")
    _save_providers(new_providers)
    return jsonify({"ok": True, "count": len(new_providers)})


# -- API: Notebooks ---------------------------------------------------------

@app.route("/api/notebooks", methods=["GET"])
def api_notebooks():
    notebooks = list_notebooks()
    for nb in notebooks:
        meta = _get_project_meta(nb["name"])
        nb["description"] = meta.get("description", "")
        nb["created"] = meta.get("created", "")
        nb["source_count"] = len(_list_project_files(nb["name"]))
        nb["count"] = nb["source_count"]
    return jsonify(notebooks)


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    if not q or len(q) < 2:
        return jsonify({"results": []})
    results = []
    for nb in list_notebooks():
        if q in nb["name"].lower():
            results.append({"type": "project", "name": nb["name"], "id": nb["id"]})
        for f in _list_project_files(nb["name"]):
            if q in f["name"].lower():
                results.append({"type": "file", "project": nb["name"], "project_id": nb["id"], "name": f["name"]})
    return jsonify({"results": results[:20]})


@app.route("/api/notebooks", methods=["POST"])
def api_create_notebook():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Name required"}), 400
    # Create ChromaDB collection
    get_or_create_notebook(name)
    # Create project folder structure
    pdir = _ensure_project_dirs(name)
    meta = {
        "name": name,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": request.json.get("description", ""),
        "tags": request.json.get("tags", []),
    }
    _save_project_meta(name, meta)
    return jsonify({"ok": True, "name": name})


@app.route("/api/notebooks/<name>", methods=["DELETE"])
def api_delete_notebook(name):
    """Move notebook to trash (soft delete)."""
    # Move project folder to trash
    pdir = _project_dir(name)
    if pdir.exists():
        ts = time.strftime("%Y%m%d_%H%M%S")
        trash_name = f"{_safe_name(name)}_{ts}"
        trash_dest = TRASH_DIR / trash_name
        TRASH_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pdir), str(trash_dest))
        # Update trash meta
        meta = _get_project_meta(name) if (trash_dest / "meta.json").exists() else {"name": name}
        meta["deleted_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        meta["original_name"] = name
        meta["source_count"] = len(list_sources(name))
        (trash_dest / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    # Delete ChromaDB collection
    delete_notebook(name)
    _chat_cache.pop(name, None)
    return jsonify({"ok": True, "trashed": True})


# -- API: Trash --------------------------------------------------------------

@app.route("/api/trash", methods=["GET"])
def api_trash_list():
    """List all items in trash."""
    items = []
    if TRASH_DIR.exists():
        for item in sorted(TRASH_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if item.is_dir():
                meta_file = item / "meta.json"
                meta = {}
                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                items.append({
                    "id": item.name,
                    "name": meta.get("name", meta.get("original_name", item.name)),
                    "deleted_at": meta.get("deleted_at", ""),
                    "source_count": meta.get("source_count", 0),
                })
    return jsonify({"ok": True, "items": items})


@app.route("/api/trash/<trash_id>/restore", methods=["POST"])
def api_trash_restore(trash_id):
    """Restore a notebook from trash."""
    trash_dir = TRASH_DIR / trash_id
    try:
        trash_dir.resolve().relative_to(TRASH_DIR.resolve())
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid path"}), 400
    if not trash_dir.exists():
        return jsonify({"ok": False, "error": "Not found in trash"}), 404
    meta_file = trash_dir / "meta.json"
    meta = {}
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    original_name = meta.get("original_name", trash_id)
    dest = _project_dir(original_name)
    if dest.exists():
        return jsonify({"ok": False, "error": "A notebook with this name already exists"}), 400
    shutil.move(str(trash_dir), str(dest))
    # Re-create ChromaDB collection from files (if needed)
    return jsonify({"ok": True, "name": original_name})


@app.route("/api/trash/<trash_id>", methods=["DELETE"])
def api_trash_permanent_delete(trash_id):
    """Permanently delete a trash item."""
    trash_dir = TRASH_DIR / trash_id
    try:
        trash_dir.resolve().relative_to(TRASH_DIR.resolve())
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid path"}), 400
    if not trash_dir.exists():
        return jsonify({"ok": False, "error": "Not found in trash"}), 404
    shutil.rmtree(str(trash_dir))
    return jsonify({"ok": True})


@app.route("/api/trash/empty", methods=["POST"])
def api_trash_empty():
    """Empty entire trash."""
    if TRASH_DIR.exists():
        shutil.rmtree(str(TRASH_DIR))
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    return jsonify({"ok": True})


# -- API: Ingest -------------------------------------------------------------

@app.route("/api/ingest", methods=["POST"])
def api_ingest():
    notebook = request.form.get("notebook", "").strip()
    if not notebook:
        return jsonify({"ok": False, "error": "notebook required"}), 400

    # Ensure project dirs exist
    pdir = _ensure_project_dirs(notebook)
    results = []

    # File upload — PDF, TXT, MD
    for f in request.files.getlist("pdfs"):
        if not f or not f.filename:
            continue
        # Sanitise filename to prevent path traversal
        safe_name = secure_filename(f.filename)
        if not safe_name:
            results.append({"ok": False, "error": "Invalid filename", "file": f.filename})
            continue
        suffix = Path(safe_name).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            results.append({"ok": False, "error": f"Unsupported file type: {suffix}", "file": safe_name})
            continue
        save_path = pdir / "sources" / safe_name
        f.save(str(save_path))

        if suffix == ".pdf":
            r = ingest_pdf(str(save_path), notebook)
        else:  # .txt or .md
            text = save_path.read_text(encoding="utf-8", errors="replace")
            r = ingest_text(text, save_path.stem, notebook)

        r["file"] = safe_name
        results.append(r)

    # URLs
    urls_raw = request.form.get("urls", "")
    for url in urls_raw.splitlines():
        url = url.strip()
        if not url or url.startswith("#"):
            continue
        if "youtube.com" in url or "youtu.be" in url:
            r = ingest_youtube(url, notebook)
        else:
            r = ingest_url(url, notebook)
        r["url"] = url
        # Save URL reference to project
        urls_file = pdir / "sources" / "_urls.txt"
        with open(str(urls_file), "a", encoding="utf-8") as uf:
            uf.write(url + "\n")
        results.append(r)

    # Raw text
    text = request.form.get("text", "").strip()
    title = request.form.get("text_title", "Pasted Text").strip()
    if text:
        r = ingest_text(text, title, notebook)
        # Save text to project
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:50]
        text_file = pdir / "sources" / f"{safe_title}.md"
        text_file.write_text(text, encoding="utf-8")
        results.append(r)

    ok_count = sum(1 for r in results if r.get("ok"))
    return jsonify({"ok": True, "results": results, "ingested": ok_count})


# -- API: Delete source (removes from ChromaDB + file from disk) -------------

@app.route("/api/source/<notebook>/<source_id>", methods=["DELETE"])
def api_delete_source(notebook, source_id):
    # Get the title before deleting so we can find the file
    title = get_source_title(notebook, source_id)
    chunks_deleted = delete_source(notebook, source_id)
    if chunks_deleted == 0:
        return jsonify({"ok": False, "error": "Source not found"}), 404

    # Try to delete the physical file from sources dir
    pdir = _project_dir(notebook)
    sources_dir = pdir / "sources"
    deleted_file = None
    if title and sources_dir.exists():
        for ext in (".pdf", ".txt", ".md", ".docx"):
            candidate = sources_dir / (title + ext)
            if candidate.exists():
                candidate.unlink()
                deleted_file = candidate.name
                break

    return jsonify({"ok": True, "chunks": chunks_deleted, "file": deleted_file})


# -- API: Delete file from disk only -----------------------------------------

@app.route("/api/file/<notebook>/<path:filename>", methods=["DELETE"])
def api_delete_file(notebook, filename):
    pdir = _project_dir(notebook)
    file_path = pdir / "sources" / filename
    if not file_path.exists():
        return jsonify({"ok": False, "error": "File not found"}), 404
    # Security: ensure the resolved path is inside the sources dir
    try:
        file_path.resolve().relative_to((pdir / "sources").resolve())
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid path"}), 400
    file_path.unlink()
    return jsonify({"ok": True, "file": filename})


# -- API: Chat --------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data       = request.json
    notebook   = data.get("notebook", "").strip()
    question   = data.get("question", "").strip()
    model      = data.get("model", None)
    source_id  = data.get("source_id", None) or None
    source_ids = data.get("source_ids", None) or None
    if source_ids and not isinstance(source_ids, list):
        source_ids = [source_ids]

    if not notebook or not question:
        return jsonify({"ok": False, "error": "notebook and question required"}), 400

    history = _load_chat(notebook)
    try:
        result = ask_with_sources(notebook, question, model=model, history=history,
                                  source_id=source_id, source_ids=source_ids)
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines are currently unavailable. Check Settings → Providers or ensure Ollama is running.", "detail": str(e)}), 503

    _append_chat(notebook, question, result["answer"])

    return jsonify({
        "ok": True,
        "answer": result["answer"],
        "sources": result["sources"],
        "model": model or detect_best_model()
    })


# -- API: Notebook Guide -------------------------------------------------------

@app.route("/api/guide/<notebook>/<guide_type>", methods=["POST"])
def api_guide(notebook, guide_type):
    valid = {"faq", "study_guide", "key_themes", "timeline", "briefing"}
    if guide_type not in valid:
        return jsonify({"ok": False, "error": f"Unknown type. Use: {valid}"}), 400
    try:
        result = generate_guide(notebook, guide_type)
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines are currently unavailable.", "detail": str(e)}), 503
    return jsonify({"ok": True, "content": result, "type": guide_type})


# -- API: Source summary -------------------------------------------------------

@app.route("/api/source/<notebook>/<source_id>/summary", methods=["POST"])
def api_source_summary(notebook, source_id):
    sources = list_sources(notebook)
    source = next((s for s in sources if s["source_id"] == source_id), None)
    if not source:
        return jsonify({"ok": False, "error": "Source not found"}), 404
    summary = generate_source_summary(notebook, source_id, source["title"])
    return jsonify({"ok": True, "summary": summary, "title": source["title"]})


# -- API: Notes ---------------------------------------------------------------

def _notes_file(notebook: str) -> Path:
    pdir = _project_dir(notebook)
    pdir.mkdir(parents=True, exist_ok=True)
    return pdir / "notes.json"

def _load_notes(notebook: str) -> list:
    f = _notes_file(notebook)
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

def _save_notes(notebook: str, notes: list):
    _notes_file(notebook).write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")

@app.route("/api/notes/<notebook>", methods=["GET"])
def api_notes_get(notebook):
    return jsonify({"ok": True, "notes": _load_notes(notebook)})

@app.route("/api/notes/<notebook>", methods=["POST"])
def api_notes_add(notebook):
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"ok": False, "error": "text required"}), 400
    notes = _load_notes(notebook)
    note = {
        "id": str(int(time.time() * 1000)),
        "text": text,
        "label": data.get("label", "note"),
        "source": data.get("source", ""),
        "ts": time.strftime("%Y-%m-%d %H:%M"),
    }
    notes.append(note)
    _save_notes(notebook, notes)
    return jsonify({"ok": True, "note": note})

@app.route("/api/notes/<notebook>/<note_id>", methods=["DELETE"])
def api_notes_delete(notebook, note_id):
    notes = _load_notes(notebook)
    notes = [n for n in notes if n.get("id") != note_id]
    _save_notes(notebook, notes)
    return jsonify({"ok": True})


# -- API: Summarise ---------------------------------------------------------

@app.route("/api/summarise", methods=["POST"])
def api_summarise():
    data     = request.json
    notebook = data.get("notebook", "").strip()
    model    = data.get("model", None)
    if not notebook:
        return jsonify({"ok": False, "error": "notebook required"}), 400
    try:
        answer = summarise_sources(notebook, model)
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines are currently unavailable.", "detail": str(e)}), 503
    return jsonify({"ok": True, "answer": answer})


# -- API: Save session ------------------------------------------------------

@app.route("/api/save", methods=["POST"])
def api_save():
    data     = request.json
    notebook = data.get("notebook", "").strip()
    history  = _load_chat(notebook)
    if not history:
        return jsonify({"ok": False, "error": "Nothing to save"}), 400

    # Save to project exports folder
    pdir = _project_dir(notebook)
    exports_dir = pdir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    ts   = time.strftime("%Y%m%d_%H%M%S")
    path = exports_dir / f"{_safe_name(notebook)}_{ts}.md"
    lines = [f"# Research Session: {notebook}\n", f"*Saved: {time.strftime('%Y-%m-%d %H:%M')}*\n\n---\n"]
    for turn in history:
        lines.append(f"\n**Q [{turn['ts']}]:** {turn['q']}\n\n**A:** {turn['a']}\n\n---\n")
    path.write_text("\n".join(lines), encoding="utf-8")

    # Also save to output dir for backwards compat
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{notebook}_{ts}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    return jsonify({"ok": True, "path": str(path)})


# -- API: Sources / Model / Status ------------------------------------------

@app.route("/api/sources/<notebook>")
def api_sources(notebook):
    return jsonify(list_sources(notebook))


@app.route("/api/source/<notebook>/<source_id>/read")
def api_read_source(notebook, source_id):
    """Read a source file — looks up title from ChromaDB, finds file by title."""
    pdir = _project_dir(notebook)
    sources_dir = pdir / "sources"

    # Get the stored title for this source_id from ChromaDB
    title = get_source_title(notebook, source_id)

    mode = request.args.get("mode", "")  # 'pdf' forces PDF text, 'md' forces markdown

    if title and sources_dir.exists():
        md_path  = sources_dir / (title + ".md")
        pdf_path = sources_dir / (title + ".pdf")

        # Explicit MD view
        if mode == "md" and md_path.exists():
            content = md_path.read_text(encoding="utf-8", errors="replace")
            return jsonify({"ok": True, "content": content, "format": "markdown", "title": title})

        # Explicit PDF view (or default when no .md exists)
        if mode == "pdf" or (not md_path.exists()):
            if pdf_path.exists():
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(str(pdf_path))
                    pages = [p.extract_text() or "" for p in reader.pages]
                    return jsonify({"ok": True, "content": "\n\n".join(pages), "format": "pdf", "title": title})
                except Exception as e:
                    return jsonify({"ok": False, "error": str(e)})

        # Default: prefer Docling markdown
        if md_path.exists():
            content = md_path.read_text(encoding="utf-8", errors="replace")
            return jsonify({"ok": True, "content": content, "format": "markdown", "title": title})

        # Plain text source
        for ext in (".txt",):
            text_path = sources_dir / (title + ext)
            if text_path.exists():
                content = text_path.read_text(encoding="utf-8", errors="replace")
                return jsonify({"ok": True, "content": content, "format": "markdown", "title": title})

        # Fallback: read first chunk text from ChromaDB directly
        from engine.db import get_or_create_notebook as _get_col
        col = _get_col(notebook)
        results = col.get(where={"source_id": source_id}, include=["documents"])
        docs = results.get("documents") or []
        if docs:
            preview = "\n\n---\n\n".join(docs[:5])
            return jsonify({"ok": True, "content": preview, "format": "chunks", "title": title})

    return jsonify({"ok": False, "error": "Source file not found on disk"})


@app.route("/api/project/<notebook>/files")
def api_project_files(notebook):
    return jsonify({"ok": True, "files": _list_project_files(notebook)})


@app.route("/api/project/<notebook>/meta", methods=["GET"])
def api_project_meta_get(notebook):
    meta = _get_project_meta(notebook)
    return jsonify(meta)


@app.route("/api/project/<notebook>/meta", methods=["POST"])
def api_project_meta_save(notebook):
    data = request.json
    meta = _get_project_meta(notebook)
    for k in _META_ALLOWED_KEYS:
        if k in data:
            meta[k] = data[k]
    _save_project_meta(notebook, meta)
    return jsonify({"ok": True})


@app.route("/api/chat/<notebook>/history")
def api_chat_history(notebook):
    """Get full chat history for a notebook."""
    history = _load_chat(notebook)
    return jsonify({"ok": True, "history": history, "count": len(history)})


@app.route("/api/chat/<notebook>/clear", methods=["POST"])
def api_chat_clear(notebook):
    """Clear chat history for a notebook (saves empty list)."""
    _chat_cache[notebook] = []
    _save_chat(notebook)
    return jsonify({"ok": True})


@app.route("/api/model")
def api_model():
    return jsonify({"model": detect_best_model()})


@app.route("/api/status")
def api_status():
    import ollama as ol
    engine = detect_engine()
    model = detect_best_model()
    providers = get_provider_status()
    ollama_ok = False
    model_names = []
    try:
        models = ol.list()
        model_names = [m.model for m in models.models]
        ollama_ok = True
    except:
        pass
    return jsonify({
        "engine": engine,
        "ollama": ollama_ok,
        "models": model_names,
        "active": model,
        "providers": providers,
    })


# -- API: Mind Map / Graph ----------------------------------------------------

def _graph_cache_file(notebook: str) -> Path:
    return _project_dir(notebook) / "graph_cache.json"

@app.route("/api/graph/<notebook>", methods=["POST"])
def api_graph(notebook):
    import re
    from engine.rag import _llm
    from engine.db import query_chunks

    cache_file = _graph_cache_file(notebook)
    force = request.json.get("force", False) if request.json else False
    sources = list_sources(notebook)
    src_hash = str(sorted(s["source_id"] for s in sources))

    if not force and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("src_hash") == src_hash:
                return jsonify({"ok": True, "nodes": cached["nodes"], "edges": cached["edges"], "cached": True})
        except Exception:
            pass

    if not sources:
        return jsonify({"ok": False, "error": "No sources in this project yet."}), 400

    chunks = query_chunks(notebook, "main concepts themes entities relationships", n=16)
    excerpt = "\n\n---\n\n".join(c["text"] for c in chunks[:16])[:6000]

    prompt = f"""Based ONLY on these source excerpts, extract the key concepts and their relationships as a knowledge graph.

SOURCE EXCERPTS:
{excerpt}

Return ONLY valid JSON (no markdown, no explanation, just the JSON object):
{{
  "nodes": [
    {{"id": "n1", "label": "Concept Name", "type": "concept", "title": "Source Title"}}
  ],
  "edges": [
    {{"from": "n1", "to": "n2", "label": "relates to"}}
  ]
}}

RULES:
- 8 to 18 nodes maximum
- node id must be unique strings like n1, n2, n3...
- edge from/to must reference existing node ids
- node types: concept, person, event, place, finding, method
- labels must be short (1-4 words)
- only include relationships clearly supported by the excerpts
- do NOT include sources, references, or bibliography as nodes"""

    try:
        raw = _llm([{"role": "user", "content": prompt}])
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if not json_match:
            return jsonify({"ok": False, "error": "AI did not return valid graph data. Try again."}), 500
        graph = json.loads(json_match.group())
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        valid_ids = {n["id"] for n in nodes}
        edges = [e for e in edges if e.get("from") in valid_ids and e.get("to") in valid_ids]
        cache_file.write_text(json.dumps({"nodes": nodes, "edges": edges, "src_hash": src_hash}, indent=2), encoding="utf-8")
        return jsonify({"ok": True, "nodes": nodes, "edges": edges, "cached": False})
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "Could not parse graph data. Try regenerating."}), 500
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines unavailable.", "detail": str(e)}), 503


# -- API: Quiz ----------------------------------------------------------------

def _quiz_cache_file(notebook: str) -> Path:
    return _project_dir(notebook) / "quiz_cache.json"

@app.route("/api/quiz/<notebook>", methods=["POST"])
def api_quiz(notebook):
    import re
    from engine.rag import _llm
    from engine.db import query_chunks

    cache_file = _quiz_cache_file(notebook)
    force = request.json.get("force", False) if request.json else False
    sources = list_sources(notebook)
    src_hash = str(sorted(s["source_id"] for s in sources))

    if not force and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("src_hash") == src_hash:
                return jsonify({"ok": True, "questions": cached["questions"], "cached": True})
        except Exception:
            pass

    if not sources:
        return jsonify({"ok": False, "error": "No sources in this project yet."}), 400

    chunks = query_chunks(notebook, "key facts important concepts definitions findings", n=14)
    excerpt = "\n\n---\n\n".join(c["text"] for c in chunks[:14])[:5000]

    prompt = f"""Based ONLY on these source excerpts, generate 6 multiple-choice quiz questions.

SOURCE EXCERPTS:
{excerpt}

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "question": "What does X refer to according to the sources?",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "A",
    "explanation": "According to the sources, ...",
    "source": "Source Title"
  }}
]

RULES:
- Exactly 6 questions
- answer field is just the letter: A, B, C, or D
- all questions must be answerable from the excerpts
- make wrong options plausible but clearly wrong based on sources
- explanation must cite the source"""

    try:
        raw = _llm([{"role": "user", "content": prompt}])
        arr_match = re.search(r'\[[\s\S]*\]', raw)
        if not arr_match:
            return jsonify({"ok": False, "error": "AI did not return valid quiz data. Try again."}), 500
        questions = json.loads(arr_match.group())
        cache_file.write_text(json.dumps({"questions": questions, "src_hash": src_hash}, indent=2), encoding="utf-8")
        return jsonify({"ok": True, "questions": questions, "cached": False})
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "Could not parse quiz data. Try regenerating."}), 500
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines unavailable.", "detail": str(e)}), 503


# -- API: Flashcards ----------------------------------------------------------

def _flashcards_cache_file(notebook: str) -> Path:
    return _project_dir(notebook) / "flashcards_cache.json"

@app.route("/api/flashcards/<notebook>", methods=["POST"])
def api_flashcards(notebook):
    import re
    from engine.rag import _llm
    from engine.db import query_chunks

    cache_file = _flashcards_cache_file(notebook)
    force = request.json.get("force", False) if request.json else False
    sources = list_sources(notebook)
    src_hash = str(sorted(s["source_id"] for s in sources))

    if not force and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("src_hash") == src_hash:
                return jsonify({"ok": True, "cards": cached["cards"], "cached": True})
        except Exception:
            pass

    if not sources:
        return jsonify({"ok": False, "error": "No sources in this project yet."}), 400

    chunks = query_chunks(notebook, "definitions terms concepts vocabulary methods", n=14)
    excerpt = "\n\n---\n\n".join(c["text"] for c in chunks[:14])[:5000]

    prompt = f"""Based ONLY on these source excerpts, generate 10 flashcards for study and review.

SOURCE EXCERPTS:
{excerpt}

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "front": "What is [key term]?",
    "back": "Definition or answer drawn directly from sources.",
    "source": "Source Title"
  }}
]

RULES:
- Exactly 10 flashcards
- front: a key term, concept, or question (keep concise)
- back: the answer/definition as stated in the sources (1-3 sentences max)
- use only content from the provided excerpts
- mix definitions, facts, and conceptual questions"""

    try:
        raw = _llm([{"role": "user", "content": prompt}])
        arr_match = re.search(r'\[[\s\S]*\]', raw)
        if not arr_match:
            return jsonify({"ok": False, "error": "AI did not return valid flashcard data. Try again."}), 500
        cards = json.loads(arr_match.group())
        cache_file.write_text(json.dumps({"cards": cards, "src_hash": src_hash}, indent=2), encoding="utf-8")
        return jsonify({"ok": True, "cards": cards, "cached": False})
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "Could not parse flashcard data. Try regenerating."}), 500
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines unavailable.", "detail": str(e)}), 503


# -- API: Knowledge Summary ---------------------------------------------------

@app.route("/api/knowledge_summary/<notebook>", methods=["POST"])
def api_knowledge_summary(notebook):
    import re
    from engine.rag import _llm
    from engine.db import query_chunks

    cache_file = _project_dir(notebook) / "ksummary_cache.json"
    force = request.json.get("force", False) if request.json else False
    sources = list_sources(notebook)
    src_hash = str(sorted(s["source_id"] for s in sources))

    if not force and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("src_hash") == src_hash:
                return jsonify({"ok": True, "terms": cached["terms"],
                                "summary": cached["summary"], "sources": cached["sources"], "cached": True})
        except Exception:
            pass

    if not sources:
        return jsonify({"ok": False, "error": "No sources in this project yet."}), 400

    chunks = query_chunks(notebook, "key concepts important themes main ideas findings", n=20)
    excerpt = "\n\n---\n\n".join(c["text"] for c in chunks[:20])[:7000]

    prompt = f"""Based ONLY on these source excerpts, identify the most important concepts.

SOURCE EXCERPTS:
{excerpt}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "summary": "One sentence describing what these sources are collectively about.",
  "terms": [
    {{"label": "Concept Name", "score": 9, "category": "main theme"}}
  ]
}}

RULES:
- 8 to 12 terms, sorted by score descending
- score is 1-10 (10 = most central to the sources)
- category must be one of: main theme, method, finding, person, place, event, definition
- labels must be short (1-5 words)
- only include concepts clearly present in the excerpts"""

    try:
        raw = _llm([{"role": "user", "content": prompt}])
        m = re.search(r'\{[\s\S]*\}', raw)
        if not m:
            return jsonify({"ok": False, "error": "AI did not return valid data. Try again."}), 500
        data = json.loads(m.group())
        terms   = data.get("terms", [])[:12]
        summary = data.get("summary", "")
        source_names = [s["title"] for s in sources[:10]]
        result = {"terms": terms, "summary": summary, "sources": source_names, "src_hash": src_hash}
        cache_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return jsonify({"ok": True, "terms": terms, "summary": summary, "sources": source_names, "cached": False})
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "Could not parse data. Try regenerating."}), 500
    except RuntimeError as e:
        return jsonify({"ok": False, "error": "All AI engines unavailable.", "detail": str(e)}), 503


if __name__ == "__main__":
    # Ensure directories exist
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    env = load_env()
    port = int(env.get("WEBAPP_PORT", 8080))
    providers = _load_providers()
    model = detect_best_model()
    if providers:
        chain = " -> ".join(f"{p['name']}" for p in providers)
        print(f"\n{'='*60}")
        print(f"  Local NotebookLM v2 — Research Dashboard")
        print(f"  Open: http://localhost:{port}")
        print(f"  Projects: {PROJECTS_DIR}")
        print(f"  Fallback chain ({len(providers)} providers):")
        for i, p in enumerate(providers):
            print(f"    P{i+1}: {p['name']} ({p['model']})")
        print(f"  Active: {model}")
    else:
        print(f"\n{'='*60}")
        print(f"  Local NotebookLM v2 — Research Dashboard")
        print(f"  Open: http://localhost:{port}")
        print(f"  Projects: {PROJECTS_DIR}")
        print(f"  Engine: Ollama (local only)")
        print(f"  Model: {model}")
    print(f"{'='*60}\n")
    # Bind to 127.0.0.1 (localhost only) by default for privacy
    # Set WEBAPP_HOST=0.0.0.0 in .env only if you need LAN access via a reverse proxy
    host = os.environ.get('WEBAPP_HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=False)
