"""Native text ebook importer for EPUB, MOBI and TXT.

EPUB is parsed directly (ZIP + XML/HTML stdlib). MOBI uses calibre's
`ebook-convert` when available, then falls back to the optional `mobi`
package when installed. TXT is split into reader-sized text pages.
"""
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
from urllib.parse import unquote
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

from core.paths import ROOT, INPUTS, READERS
from tools.loading import print_section, print_info, print_success, print_error, print_warn, print_bullet, LoadingSpinner
from importers._reader_common import (
    slugify, unique_folder_name, build_payload, render_reader_html,
    print_access_hint, format_size, get_folder_size,
)

SUPPORTED = {".epub", ".mobi", ".txt", ".pdf"}
CHARS_PER_PAGE = 3000


def scan_ebook_files():
    INPUTS.mkdir(parents=True, exist_ok=True)
    return sorted([p.resolve() for p in INPUTS.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED], key=lambda p: p.name.lower())


class _TextExtractor(HTMLParser):
    BLOCK = {"p", "div", "section", "article", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "tr"}
    SKIP = {"script", "style", "svg", "head", "nav"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.SKIP: self.skip += 1
        if not self.skip and tag in self.BLOCK: self.parts.append("\n")
    def handle_endtag(self, tag):
        tag = tag.lower()
        if not self.skip and tag in self.BLOCK: self.parts.append("\n")
        if tag in self.SKIP and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)
    def text(self):
        s = html.unescape("".join(self.parts))
        s = re.sub(r"\r\n?", "\n", s)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()


def _local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def _read_epub(path: Path):
    with zipfile.ZipFile(path) as zf:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        rootfile = next((e for e in container.iter() if _local(e.tag) == "rootfile"), None)
        if rootfile is None:
            raise ValueError("EPUB container.xml tidak punya rootfile")
        opf_name = rootfile.attrib.get("full-path")
        if not opf_name:
            raise ValueError("EPUB OPF path kosong")
        opf_dir = str(Path(opf_name).parent).replace("\\", "/")
        opf = ET.fromstring(zf.read(opf_name))
        manifest = {}
        spine = []
        title = author = ""
        for e in opf.iter():
            tag = _local(e.tag)
            if tag == "item":
                manifest[e.attrib.get("id", "")] = e.attrib
            elif tag == "itemref":
                spine.append(e.attrib.get("idref"))
            elif tag == "title" and not title and e.text:
                title = e.text.strip()
            elif tag == "creator" and not author and e.text:
                author = e.text.strip()
        sections = []
        for sid in spine:
            item = manifest.get(sid)
            if not item: continue
            href = unquote(item.get("href", "").split("#", 1)[0])
            if not href: continue
            full = str(Path(opf_dir) / href).replace("\\", "/")
            try:
                raw = zf.read(full).decode("utf-8", "ignore")
            except KeyError:
                continue
            ex = _TextExtractor(); ex.feed(raw); text = ex.text()
            if not text: continue
            sections.append({"page": len(sections)+1, "type": "text", "resource": full, "content": text})
        if not sections:
            raise ValueError("EPUB tidak memiliki konten teks yang bisa dibaca")
        return title, author, sections


def _split_text(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text: return []
    pages = []
    while text:
        if len(text) <= CHARS_PER_PAGE:
            chunk, text = text, ""
        else:
            cut = text.rfind("\n\n", 0, CHARS_PER_PAGE)
            if cut < CHARS_PER_PAGE // 2: cut = text.rfind(" ", 0, CHARS_PER_PAGE)
            if cut < CHARS_PER_PAGE // 2: cut = CHARS_PER_PAGE
            chunk, text = text[:cut].rstrip(), text[cut:].lstrip()
        pages.append({"page": len(pages)+1, "type": "text", "resource": "document.txt", "content": chunk})
    return pages


def _read_txt(path: Path):
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-16", "cp1252", "latin-1"):
        try: text = raw.decode(enc); break
        except UnicodeDecodeError: continue
    else: text = raw.decode("utf-8", "replace")
    return path.stem, "", _split_text(text)


def _mobi_to_epub(path: Path, work: Path) -> Path:
    calibre = shutil.which("ebook-convert")
    if calibre:
        out = work / (path.stem + ".epub")
        proc = subprocess.run([calibre, str(path), str(out)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0 and out.is_file() and out.stat().st_size:
            return out
        raise RuntimeError((proc.stderr or proc.stdout or "ebook-convert gagal")[-1200:])
    try:
        from mobi import extract  # type: ignore
        extracted = extract(str(path))
        # mobi.extract commonly returns (tempdir, filepath) or a path.
        candidates = []
        if isinstance(extracted, (tuple, list)):
            candidates.extend(Path(x) for x in extracted if isinstance(x, str))
        elif isinstance(extracted, str): candidates.append(Path(extracted))
        for p in candidates:
            if p.is_file() and p.suffix.lower() in {".epub", ".html", ".htm"}:
                if p.suffix.lower() == ".epub": return p
                out = work / (path.stem + ".html"); shutil.copy2(p, out); return out
            if p.is_dir():
                for q in p.rglob("*"):
                    if q.is_file() and q.suffix.lower() == ".epub": return q
        raise RuntimeError("paket mobi tidak menghasilkan EPUB/HTML yang bisa dibaca")
    except ImportError:
        raise RuntimeError("MOBI butuh Calibre (ebook-convert) atau paket Python 'mobi'.")


def _read_mobi(path: Path, work: Path):
    converted = _mobi_to_epub(path, work)
    if converted.suffix.lower() == ".epub": return _read_epub(converted)
    raw = converted.read_text("utf-8", errors="ignore")
    ex = _TextExtractor(); ex.feed(raw)
    return path.stem, "", _split_text(ex.text())


def _pick(files):
    if not files:
        print_warn(f"Gak ada EPUB/MOBI/TXT/PDF di folder '{INPUTS}'.")
        raw = input("Path EPUB/MOBI/TXT/PDF (kosong=batal): ").strip()
        if not raw: return None
        p = Path(raw).expanduser().resolve()
        return p if p.is_file() and p.suffix.lower() in SUPPORTED else None
    for i, p in enumerate(files, 1): print(f"  [{i}] {p.name}  ({format_size(p.stat().st_size)})")
    raw = input(f"Pilih file [1-{len(files)}] (default 1): ").strip() or "1"
    if raw.isdigit() and 1 <= int(raw) <= len(files): return files[int(raw)-1]
    p = Path(raw).expanduser().resolve()
    return p if p.is_file() and p.suffix.lower() in SUPPORTED else None


def handle_ebook_import() -> bool:
    print_section("Import Ebook", icon="book")
    print_info("Format: EPUB · MOBI · TXT · PDF")
    path = _pick(scan_ebook_files())
    if not path:
        print_error("File ebook tidak ditemukan / format tidak didukung.")
        return False
    work = Path(tempfile.mkdtemp(prefix="gw-ebook-", dir=str(ROOT / "temp" if (ROOT / "temp").is_dir() else ROOT)))
    try:
        if path.suffix.lower() == ".pdf":
            from importers.pdf_importer import handle_pdf_import
            # The ebook picker already collected the path. Pass it through so
            # the PDF pipeline never asks the user for the same path again.
            return handle_pdf_import(pdf_path=str(path))
        spinner = LoadingSpinner("Membaca ebook..."); spinner.start()
        try:
            if path.suffix.lower() == ".epub": title, author, sections = _read_epub(path)
            elif path.suffix.lower() == ".txt": title, author, sections = _read_txt(path)
            else: title, author, sections = _read_mobi(path, work)
            spinner.stop(f"Konten siap: {len(sections)} halaman", status="ok")
        except Exception:
            if spinner.running:
                spinner.stop()
            raise
        title = title or path.stem
        print_bullet(f"Judul  : {title}", indent=4)
        if author: print_bullet(f"Author : {author}", indent=4)
        print_bullet(f"Halaman: {len(sections)}", indent=4)
        if input("Lanjut import? [Y/n]: ").strip().lower() in {"n", "no", "tidak"}: return False
        READERS.mkdir(parents=True, exist_ok=True)
        slug = unique_folder_name(slugify(title), str(READERS)); out = READERS / slug; out.mkdir(parents=True, exist_ok=True)
        payload = build_payload(
            title, author, sections,
            properties={
                "format": path.suffix.upper().lstrip("."),
                "page_count": len(sections),
                "source_name": path.name,
                "size_bytes": path.stat().st_size,
            },
        )
        render_reader_html(str(ROOT / "templates/reader/reader.html"), str(out / "index.html"), payload, "ebook")
        print_success(f"Ebook '{title}' berhasil di-import!")
        print_bullet(f"Lokasi: {out}", indent=4); print_access_hint(slug)
        return True
    except Exception as exc:
        print_error(f"Import ebook gagal: {type(exc).__name__}: {exc}")
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)
