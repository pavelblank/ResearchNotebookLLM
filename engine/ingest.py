"""
Document ingestion: PDF, URL, YouTube → chunks → ChromaDB
"""

import re, uuid, hashlib
from pathlib import Path
import trafilatura
import yt_dlp
from pypdf import PdfReader
from engine.db import add_chunks

CHUNK_SIZE    = 800   # words per chunk
CHUNK_OVERLAP = 100   # word overlap between chunks


def _chunk_text(text: str, source_id: str, title: str, doc_type: str) -> list[dict]:
    words = text.split()
    chunks = []
    i = 0
    idx = 0
    while i < len(words):
        chunk_words = words[i : i + CHUNK_SIZE]
        chunk_text  = " ".join(chunk_words).strip()
        if len(chunk_text) > 50:
            cid = hashlib.md5(f"{source_id}_{idx}".encode()).hexdigest()
            chunks.append({
                "id":   cid,
                "text": chunk_text,
                "metadata": {
                    "source_id": source_id,
                    "title":     title,
                    "type":      doc_type,
                    "chunk_idx": idx
                }
            })
            idx += 1
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def ingest_pdf(path: str, notebook: str) -> dict:
    path = Path(path)
    title = path.stem
    source_id = hashlib.md5(str(path).encode()).hexdigest()
    md_path = path.parent / (path.stem + ".md")
    text = None
    method = "pypdf"

    # Try Docling first — preserves tables, headings, figures, formatting
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(str(path))
        docling_text = result.document.export_to_markdown()
        if docling_text and len(docling_text.strip()) > 100:
            text = docling_text
            method = "docling"
            # Save markdown alongside PDF so the reader can show it
            md_path.write_text(text, encoding="utf-8")
    except Exception:
        pass

    # Fallback: pypdf basic text extraction
    if not text or len(text.strip()) < 100:
        try:
            reader = PdfReader(str(path))
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n\n".join(pages)
        except Exception as e:
            return {"ok": False, "error": f"PDF read failed: {e}"}

    if not text or not text.strip():
        return {"ok": False, "error": "No text could be extracted from this PDF"}

    chunks = _chunk_text(text, source_id, title, "pdf")
    add_chunks(notebook, chunks)
    return {"ok": True, "title": title, "chunks": len(chunks), "source_id": source_id, "method": method}


def ingest_url(url: str, notebook: str) -> dict:
    source_id = hashlib.md5(url.encode()).hexdigest()
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return {"ok": False, "error": f"Could not fetch: {url}"}
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
    if not text or len(text.strip()) < 100:
        return {"ok": False, "error": "No useful text extracted from URL"}
    # title from metadata
    meta = trafilatura.extract_metadata(downloaded)
    title = (meta.title if meta and meta.title else url[:80])
    chunks = _chunk_text(text, source_id, title, "url")
    add_chunks(notebook, chunks)
    return {"ok": True, "title": title, "chunks": len(chunks), "source_id": source_id}


def ingest_youtube(url: str, notebook: str) -> dict:
    source_id = hashlib.md5(url.encode()).hexdigest()
    transcript = ""
    title = url

    # Try auto-captions first (fast, no download)
    ydl_opts_sub = {
        "skip_download": True,
        "writeautomaticsub": True,
        "writesubtitles": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "vtt",
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "/tmp/yt_%(id)s",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts_sub) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", url)
            vid_id = info.get("id", "vid")
            # Look for downloaded subtitle file
            import glob, os
            vtt_files = glob.glob(f"/tmp/yt_{vid_id}*.vtt")
            if vtt_files:
                raw = Path(vtt_files[0]).read_text(encoding="utf-8", errors="replace")
                # Strip VTT tags and timestamps
                lines = []
                for line in raw.splitlines():
                    if "-->" in line or line.startswith("WEBVTT") or line.strip().isdigit():
                        continue
                    clean = re.sub(r"<[^>]+>", "", line).strip()
                    if clean:
                        lines.append(clean)
                transcript = " ".join(lines)
                # Cleanup
                for f in vtt_files:
                    try: os.remove(f)
                    except: pass
    except Exception as e:
        return {"ok": False, "error": f"YouTube error: {e}"}

    if not transcript or len(transcript.strip()) < 100:
        return {"ok": False, "error": "No transcript/captions found. Video may not have English subtitles."}

    chunks = _chunk_text(transcript, source_id, title, "youtube")
    add_chunks(notebook, chunks)
    return {"ok": True, "title": title, "chunks": len(chunks), "source_id": source_id}


def ingest_text(text: str, title: str, notebook: str) -> dict:
    source_id = hashlib.md5((title + text[:100]).encode()).hexdigest()
    chunks = _chunk_text(text, source_id, title, "text")
    add_chunks(notebook, chunks)
    return {"ok": True, "title": title, "chunks": len(chunks), "source_id": source_id}
