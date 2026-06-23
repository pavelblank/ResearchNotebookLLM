"""
Local NotebookLM - Research Engine
Ingest YouTube / PDF / URLs → RAG-grounded answers (no hallucination)

Usage:
  python meta_engine.py "https://yt.url" path/to/paper.pdf "https://article.url"
"""

import os, sys, time, subprocess, requests, base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_BASE       = os.getenv("OPEN_NOTEBOOK_API", "http://localhost:5055/api")
HEALTH_URL     = "http://localhost:5055/health"
FREE_API_KEY   = os.getenv("FREE_API_KEY", "")
FREE_API_BASE  = os.getenv("FREE_API_BASE", "")
FREE_API_MODEL = os.getenv("FREE_API_MODEL", "")
OLLAMA_BASE    = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
OUTPUT_DIR     = Path(__file__).parent.parent / os.getenv("OUTPUT_DIR", "output")

RESEARCH_SYSTEM_PROMPT = """You are a strict academic research assistant.

RULES — follow exactly:
1. Answer ONLY from the provided source documents.
2. Quote or cite directly from sources when possible. Include source name/title.
3. If information is NOT in the sources, say exactly: "Not found in provided sources."
4. Never speculate, extrapolate, or add external knowledge.
5. When uncertain, say: "The sources do not clearly state this."
6. Structure responses: Key Finding → Direct Evidence → Source Citation.

You must not fabricate references, statistics, or conclusions."""

ANALYSIS_QUERY = (
    "Provide a structured, evidence-based analysis of all sources. "
    "For each key theme: (1) state the finding, (2) quote exact source evidence, "
    "(3) cite which source it came from, (4) note contradictions between sources. "
    "Do not include any information not present in the sources."
)


def check_services():
    try:
        r = requests.get(HEALTH_URL, timeout=3)
        if r.status_code == 200 and r.json().get("status") == "healthy":
            print("[OK] Open Notebook API healthy.")
            return True
    except requests.RequestException:
        pass
    print("[ERROR] Open Notebook not running at http://localhost:5055")
    print("  Fix: run start.bat")
    return False


def detect_model():
    if FREE_API_KEY and FREE_API_BASE and FREE_API_MODEL:
        print(f"[OK] Free API: {FREE_API_MODEL}")
        return FREE_API_MODEL, "openai", FREE_API_BASE, FREE_API_KEY
    try:
        res = subprocess.run(["ollama","list"], capture_output=True, text=True, timeout=5)
        lines = res.stdout.strip().split("\n")[1:]
        available = [l.split()[0] for l in lines if l]
        prefs = ["gemma4:e2b","gemma4:12b","gemma3:latest","llama3.2:latest","mistral:latest"]
        for p in prefs:
            if p in available:
                print(f"[OK] Ollama: {p}")
                return p, "ollama", OLLAMA_BASE, ""
        if available:
            print(f"[OK] Ollama: {available[0]}")
            return available[0], "ollama", OLLAMA_BASE, ""
    except Exception as e:
        print(f"[!] Ollama check: {e}")
    print("[ERROR] No model found. Add FREE_API_KEY to .env or install Ollama.")
    sys.exit(1)


def get_or_register_model(model_name, provider, api_base, api_key):
    r = requests.get(f"{API_BASE}/models"); r.raise_for_status()
    for m in r.json():
        if m["name"] == model_name and m["provider"] == provider:
            return m["id"]
    payload = {"name": model_name, "provider": provider, "type": "language"}
    if api_base: payload["api_base"] = api_base
    if api_key:  payload["api_key"]  = api_key
    r = requests.post(f"{API_BASE}/models", json=payload); r.raise_for_status()
    model_id = r.json()["id"]
    print(f"[OK] Model registered: {model_id}")
    return model_id


def create_notebook(title=None):
    ts = time.strftime("%Y-%m-%d %H:%M")
    r = requests.post(f"{API_BASE}/notebooks", json={
        "name": title or f"Research — {ts}",
        "description": "Grounded RAG notebook — no hallucination"
    }); r.raise_for_status()
    nb_id = r.json()["id"]
    print(f"[OK] Notebook: {nb_id}")
    return nb_id


def add_source(notebook_id, source: str):
    source = source.strip()
    path = Path(source)
    if path.exists() and path.is_file():
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            data = base64.b64encode(path.read_bytes()).decode()
            payload = {"type":"pdf","file_data":data,"file_name":path.name,
                       "notebooks":[notebook_id],"embed":True,"async_processing":True}
        elif suffix in (".txt",".md"):
            payload = {"type":"text","content":path.read_text(encoding="utf-8",errors="replace"),
                       "title":path.name,"notebooks":[notebook_id],"embed":True,"async_processing":True}
        else:
            print(f"[!] Unsupported: {suffix}"); return None
        print(f"[*] Adding file: {path.name}")
        r = requests.post(f"{API_BASE}/sources/json", json=payload)
    else:
        print(f"[*] Adding URL: {source[:80]}")
        r = requests.post(f"{API_BASE}/sources/json", json={
            "type":"link","url":source,
            "notebooks":[notebook_id],"embed":True,"async_processing":True
        })
    try:
        r.raise_for_status(); return r.json()["id"]
    except Exception as e:
        print(f"[!] Failed: {e}"); return None


def wait_for_sources(source_ids, timeout=600):
    print(f"[*] Processing {len(source_ids)} source(s)...")
    deadline = time.time() + timeout
    failed = []
    for sid in source_ids:
        while time.time() < deadline:
            r = requests.get(f"{API_BASE}/sources/{sid}/status"); r.raise_for_status()
            data = r.json(); status = data.get("status",""); msg = data.get("message","")
            print(f"  [{sid[:20]}] {status}: {msg[:60]}")
            if status == "completed": break
            if status == "failed":   failed.append(sid); break
            time.sleep(5)
    if failed: print(f"[!] {len(failed)} failed.")
    return [s for s in source_ids if s not in failed]


def build_context(notebook_id, source_ids):
    r = requests.post(f"{API_BASE}/chat/context", json={
        "notebook_id": notebook_id,
        "context_config": {"sources":{s:"full content" for s in source_ids},"notes":{}}
    }); r.raise_for_status()
    return r.json()["context"]


def ask(notebook_id, context, model_id, query, session_id=None):
    if not session_id:
        r = requests.post(f"{API_BASE}/chat/sessions",
                          json={"notebook_id":notebook_id,"title":"Research Chat"})
        r.raise_for_status(); session_id = r.json()["id"]
    r = requests.post(f"{API_BASE}/chat/execute", json={
        "session_id": session_id, "message": query,
        "context": context, "model_override": model_id,
        "system_prompt": RESEARCH_SYSTEM_PROMPT
    }); r.raise_for_status()
    msgs = r.json()["messages"]
    answer = next((m["content"] for m in reversed(msgs) if m["type"]=="ai"), None)
    return answer, session_id


def save_output(content, label="analysis"):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"{label}_{ts}.md"
    path.write_text(content, encoding="utf-8")
    print(f"[OK] Saved: {path}")
    return path


def interactive_chat(notebook_id, context, model_id):
    print("\n" + "="*60)
    print("  RESEARCH CHAT — answers grounded in YOUR sources only")
    print("  'save' = export  |  'exit' = quit")
    print("="*60)
    session_id = None
    history = []
    while True:
        try: q = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt): break
        if not q: continue
        if q.lower() == "exit": break
        if q.lower() == "save":
            if history:
                txt = "\n\n---\n\n".join(f"**Q:** {h['q']}\n\n**A:** {h['a']}" for h in history)
                save_output(txt, "research_session")
            continue
        answer, session_id = ask(notebook_id, context, model_id, q, session_id)
        if answer:
            print(f"\nAI: {answer}")
            history.append({"q":q,"a":answer})
        else:
            print("[!] Empty response.")
    if history:
        txt = "\n\n---\n\n".join(f"**Q:** {h['q']}\n\n**A:** {h['a']}" for h in history)
        save_output(txt, "research_session")


def main():
    print("="*60)
    print("     LOCAL NOTEBOOK LM — RESEARCH ENGINE")
    print("="*60)
    if not check_services(): sys.exit(1)
    model_name, provider, api_base, api_key = detect_model()
    model_id = get_or_register_model(model_name, provider, api_base, api_key)
    sources = sys.argv[1:]
    if not sources:
        print("[ERROR] Provide at least one source.")
        print("  Usage: python meta_engine.py <url_or_pdf_path> [more...]")
        sys.exit(1)
    notebook_id = create_notebook()
    source_ids = [sid for s in sources if (sid := add_source(notebook_id, s))]
    if not source_ids: sys.exit(1)
    good_ids = wait_for_sources(source_ids)
    context = build_context(notebook_id, good_ids)
    print("\n[*] Running initial analysis...")
    answer, _ = ask(notebook_id, context, model_id, ANALYSIS_QUERY)
    if answer: save_output(answer, "initial_analysis")
    interactive_chat(notebook_id, context, model_id)

if __name__ == "__main__":
    main()
