"""
GhostWriter — Reader Common Helpers

Shared utilities untuk PDF & Comic importer:
- Slug generation (folder name)
- HTML rendering dari templates/reader/reader.html
- Escaping JSON untuk injeksi ke <script>
- Konstanta LOGO_SVG & FAVICON_LINK (samain dengan index.html)
- Auto .nomedia (Batch 7J)
- Auto-sync index (Batch 7M)

Helpers ini dipake bareng sama:
    - importers/pdf_importer.py
    - importers/comic_importer.py
"""

import os
import re
import json
import time
import hashlib
from pathlib import Path

from tools.loading import print_error, print_warn
from tools.theme import get_theme, C
from tools.nomedia import ensure_full_tree
from jinja2 import Environment, FileSystemLoader
from core.paths import ROOT, INPUTS, PUBLIC, TEMPLATES


# ============================================================
# CONSTANTS — SAMAIN DENGAN index.html & viewer.html
# ============================================================

LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="var(--accent, #38bdf8)" aria-hidden="true" '
    'class="gw-logo-svg" width="26" height="26">'
    '<path d="M12 2C7.58 2 4 5.58 4 10v11l2.5-2 2.5 2 2.5-2 2.5 2 '
    '2.5-2 2.5 2V10c0-4.42-3.58-8-8-8zm-3 9a1.25 1.25 0 1 1 0-2.5 '
    '1.25 1.25 0 0 1 0 2.5zm6 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 '
    '0 0 1 0 2.5z"/></svg>'
)

FAVICON_LINK = (
    '<link rel="icon" type="image/svg+xml" '
    'href="data:image/svg+xml;base64,'
    'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9'
    'IjAgMCAyNCAyNCI+PHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiByeD0iNSIg'
    'ZmlsbD0iIzBiMGYxOSIvPjxwYXRoIGZpbGw9IiMzOGJkZjgiIGQ9Ik0xMiA0Qzgu'
    'MTMgNCA1IDcuMTMgNSAxMXY3LjVsMi0xLjUgMiAxLjUgMi0xLjUgMiAxLjUgMi0x'
    'LjUgMiAxLjVWMTFjMC0zLjg3LTMuMTMtNy03LTd6bS0yLjUgN2ExIDEgMCAxIDEg'
    'MC0yIDEgMSAwIDAgMSAwIDJ6bTUgMGExIDEgMCAxIDEgMC0yIDEgMSAwIDAgMSAw'
    'IDJ6Ii8+PC9zdmc+'
    '">'
)


# ============================================================
# UTILITIES
# ============================================================

def get_input_dir(input_dir: str = "inputs") -> str:
    """Return the canonical absolute inputs directory."""
    path = Path(input_dir).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve())

def unique_folder_name(base_slug: str, parent_dir: str) -> str:
    """Return an available folder name using the legacy -2/-3 convention."""
    parent = Path(parent_dir).expanduser()
    if not parent.is_absolute():
        parent = ROOT / parent
    parent.mkdir(parents=True, exist_ok=True)
    candidate = base_slug
    counter = 2
    while (parent / candidate).is_dir():
        candidate = f"{base_slug}-{counter}"
        counter += 1
        if counter > 999:
            candidate = f"{base_slug}-{int(time.time())}"
            break
    return candidate

def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f} detik"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes} menit {secs} detik"

def print_access_hint(slug: str, kind: str = "ebook"):
    t = get_theme()
    base = "readers" if kind == "ebook" else "comics"
    url = f"http://localhost:8000/{base}/{slug}/index.html"
    if t.enabled:
        print(f"  {C.ACCENT_DIM}{'─' * 56}{C.RESET}")
        print(f"  {C.GREEN}✅{C.RESET}  {C.WHITE}Cara buka:{C.RESET}")
        print()
        print(f"  {C.ACCENT_DIM}1.{C.RESET} {C.GRAY}Jalanin server (kalau belum): {C.ACCENT}python3 serve.py{C.RESET}")
        print(f"  {C.ACCENT_DIM}2.{C.RESET} {C.GRAY}Buka: {C.WHITE}{url}{C.RESET}")
        print()
        print(f"  {C.GRAY}Atau akses via landing page kalau udah di-sync.{C.RESET}")
        print(f"  {C.ACCENT_DIM}{'─' * 56}{C.RESET}")
    else:
        print("  " + "─" * 56)
        print("  ✅  Cara buka:")
        print()
        print("  1. Jalanin server (kalau belum): python3 serve.py")
        print(f"  2. Buka: {url}")

def safe_ext(name: str, allowed_exts=(), default: str = ".jpg") -> str:
    ext = os.path.splitext(name)[1].lower()
    return ext if not allowed_exts or ext in allowed_exts else default


def slugify(text: str, max_len: int = 50) -> str:
    """
    Convert title jadi slug aman buat nama folder.
    Contoh: "Fisika Kuantum — Bab 1" -> "fisika-kuantum-bab-1"
    """
    if not text:
        return f"untitled_{int(time.time())}"

    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s\-]+", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")

    if not text:
        return f"untitled_{int(time.time())}"

    return text[:max_len].rstrip("-")


def ensure_dir(path: str) -> bool:
    """Create a directory, resolving project-relative paths canonically."""
    if not path:
        return False
    try:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = ROOT / p
        p.mkdir(parents=True, exist_ok=True)
        return p.is_dir()
    except OSError as e:
        print_error(f"Gagal bikin folder '{path}': {e}")
        return False


def format_size(size_bytes: int) -> str:
    """Human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_folder_size(folder_path: str) -> int:
    """Total size folder recursive."""
    total = 0
    try:
        for dirpath, _, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except OSError:
        pass
    return total


# ============================================================
# JSON INJECTION
# ============================================================

def _safe_json_for_script(data: dict) -> str:
    """
    Serialize dict ke JSON string yang aman buat disuntik ke <script>.
    Handle `</script>` di dalam string dengan escape `</` -> `<\\/`.
    """
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return raw.replace("</", "<\\/")


# ============================================================
# HTML RENDERING
# ============================================================

def _build_subtitle(type_: str, pages: int, author: str = "") -> str:
    """Bikin subtitle konsisten buat header & sidebar."""
    type_label = "Ebook" if type_ == "ebook" else "Comic"
    base = f"{type_label} · {pages} halaman"
    if author and author.strip():
        return f"{base} · {author.strip()}"
    return base


def render_reader_html(template_path: str, output_path: str, payload: dict, type_: str = "ebook") -> str:
    """Render modular reader template with native Jinja2."""
    # Resolve project-relative template paths from this module, not from the
    # process CWD. This matters when GhostWriter+ is launched from Android
    # shells/file managers where CWD may differ from the project root.
    project_root = ROOT
    template_file = Path(template_path)
    if not template_file.is_absolute():
        template_file = project_root / template_file
    if not template_file.is_file():
        raise FileNotFoundError(f"Template gak ada: {template_file}")
    title = payload.get("title") or "Tanpa Judul"
    author = payload.get("author") or ""
    pages = int(payload.get("pages") or len(payload.get("sections") or []))
    type_class = "ebook" if type_ == "ebook" else "comic"
    type_label = "EBOOK" if type_ == "ebook" else "COMIC"
    subtitle = _build_subtitle(type_, pages, author)
    project_root = ROOT
    env = Environment(
        loader=FileSystemLoader([str(project_root / "templates"), str(project_root / "templates" / "_shared")]),
        autoescape=True,
        comment_start_string="{##",
        comment_end_string="##}",
    )
    template_name = "reader/reader.html"
    template = env.get_template(template_name)
    payload_for_script = dict(payload)
    payload_for_script["type"] = type_
    html = template.render(
        TITLE=title, SUBTITLE=subtitle, TYPE_CLASS=type_class, TYPE_LABEL=type_label,
        TOTAL_PAGES=pages, LOGO_SVG=LOGO_SVG, FAVICON_LINK=FAVICON_LINK,
        READER_JSON=_safe_json_for_script(payload_for_script),
    )
    output_file = Path(output_path).expanduser()
    if not output_file.is_absolute():
        output_file = ROOT / output_file
    output_file = output_file.resolve()
    out_dir = output_file.parent
    if not ensure_dir(str(out_dir)):
        raise OSError(f"Gagal bikin folder output: {out_dir}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    try:
        ensure_full_tree(Path(out_dir))
    except Exception as e:
        print_warn(f"Gagal setup .nomedia: {e}")
    try:
        from tools.dist_index import ensure_index_synced
        ensure_index_synced()
    except Exception as e:
        print_warn(f"Gagal update index: {e}")
    return str(output_file)


def _escape_html(text: str) -> str:
    """Escape minimal buat konteks HTML (bukan atribut)."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# ============================================================
# PAYLOAD BUILDER
# ============================================================

def build_payload(title: str, author: str, sections: list, properties: dict | None = None) -> dict:
    """
    Bikin payload standar buat reader.html.

    Args:
        title:    judul ebook/comic
        author:   author (boleh kosong)
        sections: list of {page, type, src/content}

    Returns:
        dict payload siap render
    """
    normalized = []
    for i, raw in enumerate(sections or [], 1):
        sec = dict(raw or {})
        sec["page"] = int(sec.get("page") or i)
        sec["resource"] = sec.get("resource") or sec.get("src") or (f"page-{sec['page']}" if sec.get("type") == "text" else f"page-{sec['page']}")
        if sec.get("type") == "text":
            content = str(sec.get("content") or "")
            sec["anchor"] = {"scheme": "text", "resource": sec["resource"]}
        else:
            sec["anchor"] = {"scheme": "image", "resource": sec.get("resource") or sec.get("src") or f"page-{sec['page']}"}
        normalized.append(sec)
    identity_payload = {
        "title": title or "Tanpa Judul",
        "author": author or "",
        "sections": normalized,
    }
    book_id = "sha256:" + hashlib.sha256(
        json.dumps(identity_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "title": title or "Tanpa Judul",
        "author": author or "",
        "pages": len(normalized),
        "sections": normalized,
        "book_id": book_id,
        "annotation_schema": 1,
        "properties": {
            "format": "Reader",
            "page_count": len(normalized),
            **(properties or {}),
        },
    }