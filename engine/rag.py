"""
Research NotebookLM — RAG query engine.
Author: Pavel Blank <pavelblank@gmail.com>
Strict grounding: answers only from ChromaDB-indexed sources.
Fallback chain: P1 → P2 → ... → Ollama (local).
"""

import os, json, requests as _req
from pathlib import Path
os.environ["OLLAMA_HOST"] = "http://127.0.0.1:11434"

from dotenv import load_dotenv
_dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(_dotenv_path, override=True)

import ollama as ol
from engine.db import query_chunks

ROOT = Path(__file__).parent.parent
PROVIDERS_FILE = ROOT / "data" / "providers.json"

SYSTEM_PROMPT = """You are a strict research assistant with access ONLY to the source excerpts provided below.

CRITICAL RULES — you must follow every one of these without exception:
- ONLY answer from the source excerpts provided in this message. Nothing else.
- You have NO internet access and NO external knowledge — do not use training data or memory.
- If the answer is NOT clearly in the excerpts: respond with exactly "Not found in provided sources." Do not guess, infer, or fill in gaps.
- Never fabricate statistics, names, dates, quotes, or conclusions.
- Never add context "you might find useful" that isn't directly from the excerpts.
- Quote or paraphrase directly from the sources and cite by title: (Source: *Title*)
- Format responses in Markdown: **bold** for key findings, bullet points for lists, > blockquotes for direct quotes."""

# ── Guide generation prompts ─────────────────────────────────────────────────

GUIDE_PROMPTS = {
    "faq": """Based ONLY on the provided source excerpts, generate 6 insightful FAQ questions with detailed answers.

Format each as:
**Q: [Question a researcher would ask]**
A: [Detailed answer citing specific evidence from sources]

---

Make questions progressively deeper — start with "What is X?" and end with analytical questions like "What are the implications of Y?". Cite sources by title.""",

    "study_guide": """Create a comprehensive study guide based ONLY on the provided source excerpts.

## 📚 Key Concepts & Definitions
[List each key term/concept with its definition as stated in the sources]

## 🎯 Core Arguments & Claims
[The main arguments made across the sources, with evidence]

## 📊 Evidence, Data & Examples
[Specific statistics, case studies, quotes from sources]

## 🔗 Connections & Patterns
[How the sources relate to or contradict each other]

## ❓ Critical Review Questions
[5 questions for deeper analytical thinking about these sources]

Cite source titles throughout.""",

    "key_themes": """Extract the 5-8 dominant themes from the provided source excerpts.

For each theme use this format:

### 🏷️ [Theme Name]
**What it is:** [One sentence definition]
**Evidence from sources:** [2-3 specific pieces of evidence with source titles]
**Why it matters:** [Significance or implication]

---

Order themes from most to least prominent in the sources.""",

    "timeline": """Extract all chronological information from the provided source excerpts.

Present as a timeline in this format:
**📅 [Date/Year/Period]** — [Event or Development]
> *Evidence: "[quote or paraphrase]" — Source: Title*

If specific dates aren't mentioned, group by phases/stages and label them clearly.
If the content is not time-based, instead create a **Logical Progression** showing how ideas build on each other.""",

    "briefing": """Write a crisp executive briefing based ONLY on the provided source excerpts.

## 📋 What These Sources Cover
[2 sentences: topic and scope]

## 🔍 Key Findings
- [Finding 1 — with source evidence]
- [Finding 2 — with source evidence]
- [Finding 3 — with source evidence]
- [Finding 4 — with source evidence]
- [Finding 5 — with source evidence]

## ⚠️ Critical Gaps or Contradictions
[What the sources disagree on, or what's missing]

## ✅ Bottom Line
[1-2 sentence actionable takeaway a decision-maker needs]""",
}


# ── Provider management ──────────────────────────────────────────────────────

def _load_providers() -> list[dict]:
    if not PROVIDERS_FILE.exists():
        return []
    try:
        data = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
        providers = data.get("providers", [])
        return [p for p in providers if p.get("enabled", True)]
    except Exception:
        return []


def _save_providers(providers: list[dict]):
    PROVIDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROVIDERS_FILE.write_text(json.dumps({"providers": providers}, indent=2), encoding="utf-8")


def _call_api(provider: dict, messages: list[dict]) -> str:
    url = provider["url"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {provider['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": provider["model"],
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
    }
    r = _req.post(url, headers=headers, json=payload, timeout=45)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _call_ollama(provider: dict, messages: list[dict]) -> str:
    model = provider.get("model", "qwen2.5:3b")
    response = ol.chat(model=model, messages=messages)
    return response.message.content


def _llm(messages: list[dict]) -> str:
    """Call LLM through the fallback chain."""
    providers = _load_providers()
    errors = []
    for p in providers:
        try:
            if p.get("is_ollama", False):
                return _call_ollama(p, messages)
            else:
                return _call_api(p, messages)
        except Exception as e:
            errors.append(f"{p.get('name', '?')}: {e}")
            continue
    # Absolute fallback
    try:
        response = ol.chat(model="qwen2.5:3b", messages=messages)
        return response.message.content
    except Exception as e:
        errors.append(f"Ollama fallback: {e}")
    raise RuntimeError("All providers failed:\n" + "\n".join(errors))


def detect_engine() -> str:
    providers = _load_providers()
    return "free_api" if providers else "ollama"


def detect_best_model() -> str:
    providers = _load_providers()
    if providers:
        p = providers[0]
        return f"{p['name']}: {p['model']}"
    try:
        models = ol.list()
        names = [m.model for m in models.models]
        preference = [
            "qwen3.5:9b", "qwen3.5:4b-64k", "qwen3.5:4b",
            "hermes3:latest", "hermes3:3b",
            "qwen2.5:3b", "llama3.2:latest", "gemma3:latest",
        ]
        for p in preference:
            if p in names:
                return p
        if names:
            return names[0]
    except Exception:
        pass
    return "qwen2.5:3b"


def get_provider_status() -> list[dict]:
    all_providers = []
    if PROVIDERS_FILE.exists():
        try:
            data = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
            all_providers = data.get("providers", [])
        except Exception:
            pass
    enabled = _load_providers()
    enabled_ids = {p["id"] for p in enabled}
    result = []
    for i, p in enumerate(all_providers):
        result.append({
            "name": p.get("name", f"Provider {i+1}"),
            "model": p.get("model", "?"),
            "ok": bool(p.get("api_key")) or p.get("is_ollama", False),
            "active": False,
            "enabled": p.get("enabled", True),
            "slot": i + 1,
        })
    if enabled:
        for r in result:
            if r["name"] == enabled[0].get("name"):
                r["active"] = True
                break
    return result


# ── RAG query ────────────────────────────────────────────────────────────────

def ask(notebook: str, question: str, model: str = None, history: list = None) -> str:
    """RAG chat — returns answer string."""
    result = ask_with_sources(notebook, question, model=model, history=history)
    return result["answer"]


def ask_with_sources(notebook: str, question: str, model: str = None, history: list = None,
                     source_id: str = None, source_ids: list = None) -> dict:
    """
    RAG chat — returns {"answer": str, "sources": [...]}.
    Pass source_ids (list) to restrict retrieval to specific sources.
    Pass source_id (str) for a single source (backwards compat).
    """
    # Normalise: prefer source_ids list, fall back to single source_id
    ids = source_ids if source_ids else ([source_id] if source_id else None)
    chunks = query_chunks(notebook, question, n=8, source_ids=ids)
    if not chunks and not history:
        return {
            "answer": "No sources loaded in this notebook. Please add PDFs, URLs, or YouTube links first.",
            "sources": []
        }

    # Collect unique sources used
    seen_sources = {}
    for c in chunks:
        sid = c["meta"].get("source_id", "")
        if sid and sid not in seen_sources:
            seen_sources[sid] = {
                "source_id": sid,
                "title": c["meta"].get("title", sid),
                "type": c["meta"].get("type", ""),
            }
    sources_used = list(seen_sources.values())

    # Build source context block
    context_parts = []
    for i, c in enumerate(chunks, 1):
        title = c["meta"].get("title", "Unknown Source")
        src_type = c["meta"].get("type", "")
        context_parts.append(f"[Source {i} — {title} ({src_type})]:\n{c['text']}")
    context = "\n\n---\n\n".join(context_parts) if context_parts else "No source chunks available."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"SOURCE EXCERPTS:\n\n{context}"},
    ]

    if history:
        RECENT_WINDOW = 10
        if len(history) > RECENT_WINDOW:
            older = history[:-RECENT_WINDOW]
            summary_lines = ["Previous conversation summary:"]
            for turn in older:
                summary_lines.append(f"- Q: {turn['q'][:150]}")
                summary_lines.append(f"  A: {turn['a'][:300]}")
            messages.append({"role": "system", "content": "\n".join(summary_lines)})
        for turn in history[-RECENT_WINDOW:]:
            messages.append({"role": "user", "content": turn["q"]})
            messages.append({"role": "assistant", "content": turn["a"]})

    messages.append({"role": "user", "content": question})

    try:
        answer = _llm(messages)
    except RuntimeError as e:
        answer = str(e)

    return {"answer": answer, "sources": sources_used}


def summarise_sources(notebook: str, model: str = None) -> str:
    """Generate a comprehensive analysis of all ingested sources."""
    query = (
        "Provide a comprehensive structured analysis of all the research sources. "
        "For each major theme or finding: state it clearly, quote the exact evidence, "
        "name the source. Note any agreements or contradictions between sources."
    )
    return ask(notebook, query, model)


def generate_guide(notebook: str, guide_type: str) -> str:
    """
    Generate a Notebook Guide output of the specified type.
    guide_type: 'faq' | 'study_guide' | 'key_themes' | 'timeline' | 'briefing'
    """
    prompt = GUIDE_PROMPTS.get(guide_type)
    if not prompt:
        return f"Unknown guide type: {guide_type}"

    chunks = query_chunks(notebook, prompt, n=12)
    if not chunks:
        return "No sources loaded. Please add PDFs, URLs, or text sources first."

    context_parts = []
    for i, c in enumerate(chunks, 1):
        title = c["meta"].get("title", "Unknown Source")
        src_type = c["meta"].get("type", "")
        context_parts.append(f"[Source {i} — {title} ({src_type})]:\n{c['text']}")
    context = "\n\n---\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": "You are an expert research analyst. Answer ONLY from the provided source excerpts. Use clear Markdown formatting."},
        {"role": "system", "content": f"SOURCE EXCERPTS:\n\n{context}"},
        {"role": "user", "content": prompt},
    ]

    try:
        return _llm(messages)
    except RuntimeError as e:
        return f"Generation failed: {e}"


def generate_source_summary(notebook: str, source_id: str, source_title: str) -> str:
    """Generate a focused summary for a single source."""
    from engine.db import query_chunks as _qc
    # Query specifically for this source
    chunks = query_chunks(notebook, f"main points of {source_title}", n=10)
    # Filter to this source only
    source_chunks = [c for c in chunks if c["meta"].get("source_id") == source_id]
    if not source_chunks:
        source_chunks = chunks[:5]  # fallback

    context = "\n\n".join(c["text"] for c in source_chunks)
    messages = [
        {"role": "system", "content": "Summarise only the provided text. Be concise and factual. Use bullet points."},
        {"role": "user", "content": f"Summarise this source titled '{source_title}':\n\n{context}"},
    ]
    try:
        return _llm(messages)
    except RuntimeError as e:
        return f"Summary failed: {e}"
