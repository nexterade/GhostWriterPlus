"""Multi-platform chat importer.

Supports local exports (JSON/Markdown/DOCX) plus public share URLs from
ChatGPT/OpenAI, Claude, Gemini, DeepSeek and generic public chat pages.
"""
import glob
import os
import re
from typing import List
from pathlib import Path

from parsers.json_parser import JSONChatParser
from parsers.md_parser import MarkdownChatParser
from parsers.docx_parser import DocxChatParser
from importers.chatgpt_export_importer import inspect_zip, import_export_zip
from exporter import HTMLExporter
from tools.loading import (
    print_section, print_info, print_success, print_error, print_warn,
    print_numbered,
)
from tools.prompt import prompt as _prompt
from importers._reader_common import ensure_dir, slugify, unique_folder_name
from core.paths import ROOT, INPUTS, PUBLIC, HISTORY



def _platform(path):
    n = os.path.basename(path).lower()
    if "deepseek" in n:
        return "DeepSeek"
    if "claude" in n or "anthropic" in n:
        return "Claude"
    if "gemini" in n or "bard" in n:
        return "Gemini"
    if "chatgpt" in n or "openai" in n:
        return "ChatGPT/OpenAI"
    return "Generic"


def _parser(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        return JSONChatParser(path)
    if ext == ".md":
        return MarkdownChatParser(path)
    if ext == ".docx":
        return DocxChatParser(path)
    raise ValueError("Format chat tidak didukung. Pakai ZIP ChatGPT, JSON, Markdown, atau DOCX.")


def _scan():
    INPUTS.mkdir(parents=True, exist_ok=True)
    out = []
    for pat in ("*.zip", "*.json", "*.md", "*.docx"):
        out.extend(str(p.resolve()) for p in INPUTS.glob(pat) if p.is_file())
    return sorted(set(out), key=lambda p: os.path.basename(p).lower())


def _parse_selection(raw: str, count: int) -> List[int]:
    """Parse `all`, `1,3`, `1-5` into zero-based positions."""
    if raw.lower() in ("all", "semua", "a", "*"):
        return list(range(count))
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                a, b = map(int, part.split("-", 1))
                a, b = max(1, a), min(count, b)
                if a <= b:
                    ids.extend(range(a - 1, b))
            except ValueError:
                continue
        else:
            try:
                n = int(part) - 1
                if 0 <= n < count:
                    ids.append(n)
            except ValueError:
                continue
    return sorted(set(ids))


def _export_data(data, source_label: str, source_count: int = 1, output_dir=None) -> bool:
    """Render normalized chat data without destroying an existing archive."""
    title = str(data.get("title") or "").strip()
    if not title or title.casefold() in {"untitled", "tanpa judul", "unknown", "document"}:
        title = "Obrolan AI"
    data["title"] = title

    messages = data.get("messages") or []
    if not messages:
        raise ValueError("0 pesan setelah parsing")

    out_root = Path(output_dir) if output_dir is not None else HISTORY
    if not ensure_dir(out_root):
        raise OSError(f"Gagal membuat folder {out_root}")

    slug_base = slugify(title, max_len=60)
    slug = unique_folder_name(slug_base, out_root)
    out_dir = out_root / slug
    out = out_dir / "index.html"

    HTMLExporter(template_dir="templates", template_name="viewer/viewer.html").export(
        data,
        out,
        convo_count=source_count,
        convo_id=slug,
    )
    print_success(f"✓ {title} · {len(messages)} pesan · {slug}")
    if data.get("source_url"):
        print_info(f"Sumber: {data['source_url']}")
    if data.get("partial_import"):
        print_warn("Share page hanya mengekspos teks yang bisa dibaca; hasil ditandai sebagai partial import.")
    return True


def _import_chatgpt_zip(path: str) -> bool:
    """Import conversations from an official ChatGPT data-export ZIP."""
    print_section("ChatGPT Export ZIP", icon="archive")
    try:
        parser, tempdir, meta = import_export_zip(path)
    except Exception as exc:
        print_error(f"ChatGPT ZIP gagal dibuka: {type(exc).__name__}: {exc}")
        return False

    try:
        print_info("✓ conversations.json terdeteksi")
        print_info(f"📄 HTML: {len(meta.get('html_files', []))} · DAT: {len(meta.get('dat_files', []))}")
        convos = parser.list_conversations()
        if not convos:
            print_error("Tidak ada percakapan terdeteksi di conversations.json.")
            return False

        print_section(f"ChatGPT · {len(convos)} percakapan", icon="folder")
        for i, c in enumerate(convos, 1):
            print_numbered(i, f'{c.get("title") or "Tanpa Judul"} · {c.get("created_at") or ""}')

        raw = _prompt("Render [all / nomor / range]", default="all")
        if raw == "__CANCEL__":
            return False
        positions = _parse_selection(raw, len(convos))
        if not positions:
            print_error("Tidak ada percakapan valid.")
            return False

        ok = 0
        for pos in positions:
            convo = convos[pos]
            raw_index = convo.get("index", pos)
            try:
                data = parser.parse(convo_index=raw_index)
                if not data.get("messages"):
                    raise ValueError("0 pesan setelah parsing")
                if _export_data(data, path, source_count=len(convos)):
                    ok += 1
            except Exception as exc:
                title = convo.get("title") or f"#{pos + 1}"
                print_error(f'Gagal "{title}": {type(exc).__name__}: {exc}')
                if os.environ.get("GW_DEBUG") == "1":
                    import traceback
                    traceback.print_exc()

        try:
            from tools.dist_index import ensure_index_synced
            ensure_index_synced()
        except Exception as exc:
            print_warn(f"Index belum tersinkron: {exc}")
        return ok > 0
    finally:
        tempdir.cleanup()


def handle_chat_import():
    """Import local chat files, including official ChatGPT export ZIP."""
    print_section("Import Chat File", icon="chat")
    print_info("Sumber lokal: ChatGPT Export ZIP / JSON / Markdown / DOCX")
    print_info("Untuk public/share URL gunakan menu utama [6] Import Chat via Share URL.")
    print()

    files = _scan()
    if not files:
        print_warn("Tidak ada file chat di inputs/. Taruh export ZIP/JSON/MD/DOCX di sana.")
        return False

    print_info("Auto-detect: ChatGPT Export · ChatGPT/OpenAI · Claude · Gemini · DeepSeek · Generic")
    print()
    for i, p in enumerate(files, 1):
        label = _platform(p)
        if p.lower().endswith(".zip"):
            try:
                meta = inspect_zip(p)
                label = "ChatGPT Export ZIP" if meta.get("is_chatgpt_export") else "ZIP tidak dikenal"
            except Exception:
                label = "ZIP tidak valid"
        print_numbered(i, f"{os.path.basename(p)} · {label}")
    raw = _prompt(f"Pilih file [1-{len(files)}]", default="1")
    if raw == "__CANCEL__":
        return False
    try:
        idx = int(raw) - 1
        path = files[idx]
    except (ValueError, IndexError):
        print_error("Pilihan file tidak valid.")
        return False

    if path.lower().endswith(".zip"):
        try:
            meta = inspect_zip(path)
        except Exception as exc:
            print_error(f"ZIP tidak valid: {type(exc).__name__}: {exc}")
            return False
        if not meta.get("is_chatgpt_export"):
            print_error("ZIP ini bukan export ChatGPT yang dikenali. Import Comic ZIP tetap melalui menu [3].")
            return False
        return _import_chatgpt_zip(path)

    parser = _parser(path)
    if not parser.validate():
        print_error("File tidak valid / tidak bisa dibaca.")
        return False

    convos = parser.list_conversations()
    if not convos:
        print_error("Tidak ada percakapan terdeteksi.")
        return False

    print_section(f"{_platform(path)} · {len(convos)} percakapan", icon="folder")
    for i, c in enumerate(convos, 1):
        print_numbered(i, f'{c.get("title") or "Tanpa Judul"} · {c.get("created_at") or ""}')

    raw = _prompt("Render [all / nomor / range]", default="all")
    if raw == "__CANCEL__":
        return False
    positions = _parse_selection(raw, len(convos))
    if not positions:
        print_error("Tidak ada percakapan valid.")
        return False

    ok = 0
    for pos in positions:
        convo = convos[pos]
        raw_index = convo.get("index", pos)
        try:
            data = parser.parse(convo_index=raw_index)
            if not data.get("messages"):
                raise ValueError("0 pesan setelah parsing")
            if _export_data(data, path, source_count=len(convos)):
                ok += 1
        except Exception as exc:
            title = convo.get("title") or f"#{pos + 1}"
            print_error(f'Gagal "{title}": {type(exc).__name__}: {exc}')
            if os.environ.get("GW_DEBUG") == "1":
                import traceback
                traceback.print_exc()

    try:
        from tools.dist_index import ensure_index_synced
        ensure_index_synced()
    except Exception as exc:
        print_warn(f"Index belum tersinkron: {exc}")
    return ok > 0

