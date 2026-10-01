"""ChatGPT official export ZIP importer.

The official ChatGPT data export is a ZIP archive. The conversation source of
truth is normally ``conversations.json``; the archive can also contain HTML,
DAT and metadata/attachment files. This importer safely extracts the archive
into a temporary directory, feeds conversations.json through the existing
JSONChatParser, and uses sibling extracted files for attachment resolution.
"""
from __future__ import annotations

import os
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from parsers.json_parser import JSONChatParser


MAX_FILES = 10_000
MAX_TOTAL_UNCOMPRESSED = 500 * 1024 * 1024
MAX_MEMBER_SIZE = 100 * 1024 * 1024


def _safe_member_path(root: Path, member: zipfile.ZipInfo) -> Path:
    """Return a safe extraction target; reject absolute/path traversal entries."""
    name = member.filename.replace("\\", "/")
    if not name or name.endswith("/"):
        return root / name
    p = Path(name)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError(f"ZIP entry path tidak aman: {member.filename}")
    target = (root / p).resolve()
    root_resolved = root.resolve()
    if target != root_resolved and root_resolved not in target.parents:
        raise ValueError(f"ZIP entry path tidak aman: {member.filename}")
    return target


def inspect_zip(path: str | Path) -> Dict[str, object]:
    """Inspect a ChatGPT export ZIP without extracting it."""
    path = Path(path)
    if not zipfile.is_zipfile(path):
        raise ValueError("Bukan file ZIP yang valid.")

    names: List[str] = []
    total = 0
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        if len(infos) > MAX_FILES:
            raise ValueError(f"ZIP berisi terlalu banyak file ({len(infos):,}).")
        for info in infos:
            names.append(info.filename)
            total += info.file_size
            if info.file_size > MAX_MEMBER_SIZE:
                raise ValueError(f"ZIP entry terlalu besar: {info.filename}")
            if total > MAX_TOTAL_UNCOMPRESSED:
                raise ValueError("Ukuran hasil ekstraksi ZIP melebihi batas aman 500 MB.")

    normalized = {n.replace("\\", "/").lower() for n in names}
    conversation_files = [n for n in names if Path(n).name.lower() == "conversations.json"]
    html_files = [n for n in names if n.lower().endswith((".html", ".htm"))]
    dat_files = [n for n in names if n.lower().endswith(".dat")]
    return {
        "names": names,
        "conversation_files": conversation_files,
        "html_files": html_files,
        "dat_files": dat_files,
        "total_uncompressed": total,
        "is_chatgpt_export": bool(conversation_files) or "conversations.json" in normalized,
    }


def extract_conversations_json(path: str | Path) -> Tuple[tempfile.TemporaryDirectory, Path, Dict[str, object]]:
    """Safely extract a ChatGPT export and return its tempdir + JSON path."""
    path = Path(path)
    meta = inspect_zip(path)
    conversation_files = list(meta["conversation_files"])
    if not conversation_files:
        raise ValueError(
            "ZIP ChatGPT tidak berisi conversations.json. "
            "HTML/DAT saja belum cukup untuk reconstruct percakapan secara aman."
        )

    tempdir = tempfile.TemporaryDirectory(prefix="gw_chatgpt_")
    root = Path(tempdir.name)
    try:
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                target = _safe_member_path(root, info)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as src, open(target, "wb") as dst:
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        dst.write(chunk)

        json_path = root / conversation_files[0]
        if not json_path.is_file():
            raise ValueError("conversations.json gagal diekstrak.")
        return tempdir, json_path, meta
    except Exception:
        tempdir.cleanup()
        raise


def import_export_zip(path: str | Path) -> Tuple[JSONChatParser, tempfile.TemporaryDirectory, Dict[str, object]]:
    """Create a JSON parser backed by a safely extracted official export."""
    tempdir, json_path, meta = extract_conversations_json(path)
    parser = JSONChatParser(str(json_path))
    if not parser.validate():
        tempdir.cleanup()
        raise ValueError("conversations.json tidak valid / tidak bisa dibaca sebagai JSON UTF-8.")
    return parser, tempdir, meta
