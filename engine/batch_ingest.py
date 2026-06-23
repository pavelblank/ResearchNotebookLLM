"""
Batch ingest a folder of PDFs + URLs into one research notebook.
No source limit — add as many as needed.

Usage:
  python batch_ingest.py --folder C:/Research/Papers --name "My PhD Review"
  python batch_ingest.py --urls links.txt --name "Cybersecurity Sources"
  python batch_ingest.py --folder ./pdfs --urls links.txt

links.txt format: one URL per line  (# = comment)
"""

import os, sys, time, argparse, requests, base64, subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_BASE       = os.getenv("OPEN_NOTEBOOK_API", "http://localhost:5055/api")
FREE_API_KEY   = os.getenv("FREE_API_KEY", "")
FREE_API_BASE  = os.getenv("FREE_API_BASE", "")
FREE_API_MODEL = os.getenv("FREE_API_MODEL", "")
OLLAMA_BASE    = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OUTPUT_DIR     = Path(__file__).parent.parent / os.getenv("OUTPUT_DIR", "output")

RESEARCH_SYSTEM_PROMPT = """You are a strict academic research assistant.
Answer ONLY from provided source documents.
If information is NOT in sources, say: "Not found in provided sources."
Never speculate or add external knowledge. Always cite which source contains the information."""


def detect_model():
    if FREE_API_KEY and FREE_API_BASE and FREE_API_MODEL:
        return FREE_API_MODEL, "openai", FREE_API_BASE, FREE_API_KEY
    try:
        res = subprocess.run(["ollama","list"], capture_output=True, text=True, timeout=5)
        available = [l.split()[0] for l in res.stdout.strip().split("\n")[1:] if l]
        for p in ["gemma4:e2b","gemma4:12b","gemma3:latest","llama3.2:latest"]:
            if p in available: return p, "ollama", OLLAMA_BASE, ""
        if available: return available[0], "ollama", OLLAMA_BASE, ""
    except: pass
    print("[ERROR] No model found."); sys.exit(1)


def get_or_register_model(name, provider, api_base, api_key):
    r = requests.get(f"{API_BASE}/models"); r.raise_for_status()
    for m in r.json():
        if m["name"]==name and m["provider"]==provider: return m["id"]
    payload = {"name":name,"provider":provider,"type":"language"}
    if api_base: payload["api_base"]=api_base
    if api_key:  payload["api_key"]=api_key
    r = requests.post(f"{API_BASE}/models", json=payload); r.raise_for_status()
    return r.json()["id"]


def add_pdf(nb_id, path):
    r = requests.post(f"{API_BASE}/sources/json", json={
        "type":"pdf","file_data":base64.b64encode(path.read_bytes()).decode(),
        "file_name":path.name,"notebooks":[nb_id],"embed":True,"async_processing":True})
    try: r.raise_for_status(); return r.json()["id"]
    except Exception as e: print(f"  [!] {path.name}: {e}"); return None


def add_url(nb_id, url):
    r = requests.post(f"{API_BASE}/sources/json", json={
        "type":"link","url":url,"notebooks":[nb_id],"embed":True,"async_processing":True})
    try: r.raise_for_status(); return r.json()["id"]
    except Exception as e: print(f"  [!] {url[:60]}: {e}"); return None


def wait_all(source_ids, timeout=900):
    print(f"[*] Processing {len(source_ids)} source(s)...")
    deadline = time.time() + timeout
    failed = []
    for sid in source_ids:
        while time.time() < deadline:
            try:
                r = requests.get(f"{API_BASE}/sources/{sid}/status"); r.raise_for_status()
                d = r.json(); status = d.get("status",""); msg = d.get("message","")
                print(f"  [{sid[:20]}] {status}: {msg[:70]}")
                if status == "completed": break
                if status == "failed":   failed.append(sid); break
                time.sleep(6)
            except Exception as e: print(f"  [!] {e}"); time.sleep(6)
    good = [s for s in source_ids if s not in failed]
    print(f"[OK] {len(good)}/{len(source_ids)} sources ready.")
    return good


def chat(nb_id, good_ids, model_id):
    r = requests.post(f"{API_BASE}/chat/context", json={
        "notebook_id":nb_id,
        "context_config":{"sources":{s:"full content" for s in good_ids},"notes":{}}
    }); r.raise_for_status()
    context = r.json()["context"]
    r = requests.post(f"{API_BASE}/chat/sessions",
                      json={"notebook_id":nb_id,"title":"Batch Research"}); r.raise_for_status()
    session_id = r.json()["id"]
    history = []
    print("\n"+"="*60)
    print("  RESEARCH CHAT — answers from YOUR sources only")
    print("  'save' = export  |  'exit' = quit")
    print("="*60)
    while True:
        try: q = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt): break
        if not q: continue
        if q.lower()=="exit": break
        if q.lower()=="save":
            _save(history); continue
        r = requests.post(f"{API_BASE}/chat/execute", json={
            "session_id":session_id,"message":q,"context":context,
            "model_override":model_id,"system_prompt":RESEARCH_SYSTEM_PROMPT
        }); r.raise_for_status()
        ans = next((m["content"] for m in reversed(r.json()["messages"]) if m["type"]=="ai"), None)
        if ans: print(f"\nAI: {ans}"); history.append({"q":q,"a":ans})
        else: print("[!] Empty response.")
    if history: _save(history)


def _save(history):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"research_{ts}.md"
    path.write_text("\n\n---\n\n".join(f"**Q:** {h['q']}\n\n**A:** {h['a']}" for h in history), encoding="utf-8")
    print(f"[OK] Saved: {path}")


def main():
    parser = argparse.ArgumentParser(description="Batch ingest PDFs + URLs → research notebook")
    parser.add_argument("--folder", help="Folder of PDFs")
    parser.add_argument("--urls",   help="Text file with URLs (one per line)")
    parser.add_argument("--name",   default=f"Research {time.strftime('%Y-%m-%d %H:%M')}")
    parser.add_argument("--no-chat", action="store_true")
    args = parser.parse_args()
    if not args.folder and not args.urls: parser.print_help(); sys.exit(1)

    print("="*60); print("  BATCH INGEST — LOCAL NOTEBOOK LM"); print("="*60)
    try:
        r = requests.get("http://localhost:5055/health",timeout=3)
        if not (r.status_code==200 and r.json().get("status")=="healthy"): raise Exception()
        print("[OK] API healthy.")
    except: print("[ERROR] Run start.bat first."); sys.exit(1)

    model_name, provider, api_base, api_key = detect_model()
    model_id = get_or_register_model(model_name, provider, api_base, api_key)
    print(f"[OK] Model: {model_name}")

    r = requests.post(f"{API_BASE}/notebooks",
                      json={"name":args.name,"description":"Batch research notebook"})
    r.raise_for_status(); nb_id = r.json()["id"]
    print(f"[OK] Notebook: '{args.name}'")

    source_ids = []
    if args.folder:
        pdfs = sorted(Path(args.folder).glob("**/*.pdf"))
        print(f"[*] {len(pdfs)} PDF(s) found")
        for pdf in pdfs:
            print(f"  + {pdf.name}")
            sid = add_pdf(nb_id, pdf)
            if sid: source_ids.append(sid)
    if args.urls:
        urls_path = Path(args.urls)
        if not urls_path.exists(): print(f"[ERROR] Not found: {urls_path}"); sys.exit(1)
        urls = [l.strip() for l in urls_path.read_text().splitlines()
                if l.strip() and not l.startswith("#")]
        print(f"[*] {len(urls)} URL(s)")
        for url in urls:
            print(f"  + {url[:80]}")
            sid = add_url(nb_id, url)
            if sid: source_ids.append(sid)

    if not source_ids: print("[ERROR] Nothing added."); sys.exit(1)
    good_ids = wait_all(source_ids)
    print(f"\n[OK] Ready. Open UI: http://localhost:8502")
    if not args.no_chat: chat(nb_id, good_ids, model_id)

if __name__ == "__main__":
    main()
