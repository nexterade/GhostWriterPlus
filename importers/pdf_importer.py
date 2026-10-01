"""Reliable PDF -> image reader importer.

The old implementation mixed CWD-relative paths with pdf2image temporary
files.  This version uses the canonical project paths and calls Poppler's
pdftoppm directly, writing into a staging directory before atomically moving
finished pages into the reader.  A failed page never makes the reader claim
that it succeeded.
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from core.paths import ROOT, INPUTS, READERS, TEMP
from tools.loading import (
    print_section, print_info, print_success, print_error, print_warn,
    print_numbered, print_bullet, LoadingSpinner,
)
from importers._reader_common import (
    slugify, ensure_dir, format_size, get_folder_size,
    render_reader_html, build_payload, unique_folder_name,
    format_duration, print_access_hint,
)

DEFAULT_DPI = 150
JPEG_QUALITY = 85
PAGE_PREFIX = "page_"
PAGE_DIGITS = 4
BATCH_SIZE = 8


def scan_pdf_files() -> list[str]:
    INPUTS.mkdir(parents=True, exist_ok=True)
    return sorted(
        [str(p.resolve()) for p in INPUTS.glob("*.pdf") if p.is_file()],
        key=lambda p: Path(p).name.lower(),
    )


def _check_poppler() -> str | None:
    return shutil.which("pdftoppm")


def _read_pdf_metadata(pdf_path: str) -> dict:
    result = {"title": "", "author": "", "pages": 0}
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        result["pages"] = len(reader.pages)
        meta = reader.metadata
        if meta:
            title = getattr(meta, "title", None) or meta.get("/Title", "")
            author = getattr(meta, "author", None) or meta.get("/Author", "")
            if title:
                result["title"] = str(title).strip()
            if author:
                a = str(author).strip()
                if a.casefold() not in {"anonymous", "unknown", "unknown author", "none", "null"}:
                    result["author"] = a
    except Exception:
        pass
    return result


def _is_generic_pdf_title(title: str) -> bool:
    if not title:
        return True
    normalized = re.sub(r"[\s._-]+", " ", str(title)).strip().casefold()
    return normalized in {"untitled", "tanpa judul", "unknown", "unknown title", "no title", "document", "new document", "ebook"}


def _select_pdf_title(pdf_path: str, metadata_title: str = "") -> str:
    filename_title = Path(pdf_path).stem.strip()
    return metadata_title.strip() if not _is_generic_pdf_title(metadata_title) else (filename_title or "Tanpa Judul")


def _pick_pdf_file() -> str:
    files = scan_pdf_files()
    if not files:
        print_warn(f"Gak ada file .pdf di folder '{INPUTS}'.")
        print_info("Taruh PDF di folder inputs/, atau kasih path manual.")
        from tools.prompt import prompt
        manual = prompt("Path PDF manual")
        if manual in ("", "__CANCEL__"):
            return ""
        p = Path(manual).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p)
        p = p.resolve()
        if not p.is_file() or p.suffix.lower() != ".pdf":
            print_error(f"File PDF gak ditemukan: {p}")
            return ""
        return str(p)

    print_section(f"Ditemukan {len(files)} PDF", icon="folder")
    for i, f in enumerate(files, 1):
        print_numbered(i, f"{Path(f).name}  ({format_size(Path(f).stat().st_size)})")
    from tools.prompt import prompt
    raw = prompt(f"Pilih PDF [1-{len(files)}]", default="1")
    if raw == "__CANCEL__":
        return ""
    if raw.isdigit() and 1 <= int(raw) <= len(files):
        return files[int(raw) - 1]
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p)
    p = p.resolve()
    return str(p) if p.is_file() and p.suffix.lower() == ".pdf" else ""


def _render_batch(pdftoppm: str, pdf_path: Path, first: int, last: int, staging: Path) -> list[tuple[int, Path]]:
    """Render a batch directly to staging and return (page, file) pairs."""
    staging.mkdir(parents=True, exist_ok=True)
    prefix = staging / f"batch_{first:06d}"
    cmd = [
        pdftoppm, "-jpeg", "-r", str(DEFAULT_DPI),
        "-f", str(first), "-l", str(last),
        "-jpegopt", f"quality={JPEG_QUALITY}",
        str(pdf_path), str(prefix),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "pdftoppm gagal").strip()
        raise RuntimeError(detail[-1200:])

    files = sorted(staging.glob(f"{prefix.name}-*.jpg"), key=lambda p: p.name)
    if len(files) != last - first + 1:
        raise RuntimeError(f"pdftoppm menghasilkan {len(files)} file, expected {last-first+1}")
    return [(first + i, p) for i, p in enumerate(files)]


def _render_one(pdftoppm: str, pdf_path: Path, page: int, staging: Path) -> Path:
    staging.mkdir(parents=True, exist_ok=True)
    out = staging / f"single_{page:06d}.jpg"
    cmd = [
        pdftoppm, "-jpeg", "-r", str(DEFAULT_DPI), "-singlefile",
        "-f", str(page), "-l", str(page),
        "-jpegopt", f"quality={JPEG_QUALITY}",
        str(pdf_path), str(out.with_suffix("")),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0 or not out.is_file() or out.stat().st_size == 0:
        detail = (proc.stderr or proc.stdout or "pdftoppm gagal").strip()
        raise RuntimeError(detail[-1200:])
    return out


def _render_pdf_pages(pdf_path: str, total_pages: int, images_dir: Path) -> tuple[list[dict], list[tuple[int, str]]]:
    """Render every page and return successful sections + explicit failures."""
    pdftoppm = _check_poppler()
    if not pdftoppm:
        raise RuntimeError("pdftoppm tidak ditemukan di PATH")

    images_dir.mkdir(parents=True, exist_ok=True)
    staging = TEMP / f"pdf-render-{int(time.time())}-{os.getpid()}"
    staging.mkdir(parents=True, exist_ok=True)
    sections: list[dict] = []
    failures: list[tuple[int, str]] = []

    spinner = LoadingSpinner("Render halaman 0/{} …".format(total_pages))
    spinner.start()
    try:
        for first in range(1, total_pages + 1, BATCH_SIZE):
            last = min(total_pages, first + BATCH_SIZE - 1)
            pct = int((first - 1) * 100 / total_pages) if total_pages else 100
            spinner.update(f"Render halaman {first}–{last}/{total_pages} … {pct}%")
            try:
                pairs = _render_batch(pdftoppm, Path(pdf_path), first, last, staging)
            except Exception as batch_exc:
                spinner.update(f"Batch {first}–{last} gagal — fallback per halaman …")
                pairs = []
                for page in range(first, last + 1):
                    try:
                        spinner.update(f"Render halaman {page}/{total_pages} …")
                        pairs.append((page, _render_one(pdftoppm, Path(pdf_path), page, staging)))
                    except Exception as exc:
                        failures.append((page, str(exc)))

            for page, staged in pairs:
                try:
                    final = images_dir / f"{PAGE_PREFIX}{page:0{PAGE_DIGITS}d}.jpg"
                    if not staged.is_file() or staged.stat().st_size == 0:
                        raise RuntimeError("output kosong")
                    os.replace(staged, final)
                    if not final.is_file() or final.stat().st_size == 0:
                        raise RuntimeError("output final tidak ditemukan")
                    sections.append({"page": page, "type": "image", "src": f"images/{final.name}"})
                except Exception as exc:
                    failures.append((page, str(exc)))

        sections.sort(key=lambda x: x["page"])
        spinner.stop(f"Render selesai: {len(sections)}/{total_pages} halaman", status="ok" if not failures else "warn")
        return sections, failures
    except Exception:
        if spinner.running:
            spinner.stop("Render berhenti karena error", status="error")
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def handle_pdf_import(pdf_path: str | None = None) -> bool:
    print_section("Import Ebook PDF", icon="book")
    print_info("Pipeline baru: PDF → Poppler → staging → atomic move → HTML")
    print()

    try:
        from pypdf import PdfReader  # noqa: F401
    except ImportError:
        print_error("pypdf belum terinstall. Jalankan: pip install -r requirements.txt")
        return False

    pdftoppm = _check_poppler()
    if not pdftoppm:
        print_error("pdftoppm tidak ditemukan. Di Termux: pkg install poppler")
        return False

    if pdf_path is None:
        pdf_path = _pick_pdf_file()
    else:
        pdf_path = str(Path(pdf_path).expanduser().resolve())
        if not Path(pdf_path).is_file() or Path(pdf_path).suffix.lower() != ".pdf":
            print_error(f"File PDF gak ditemukan / format salah: {pdf_path}")
            return False

    if not pdf_path:
        print_warn("Dibatalkan.")
        return False

    spinner = LoadingSpinner("Analisis PDF...")
    spinner.start()
    try:
        meta = _read_pdf_metadata(pdf_path)
        total = meta["pages"]
        if total <= 0:
            spinner.stop("PDF tidak punya halaman", status="error")
            return False
        title = _select_pdf_title(pdf_path, meta["title"])
        author = meta["author"]
        spinner.stop(f"PDF valid: {total} halaman", status="ok")
    except Exception:
        if spinner.running:
            spinner.stop()
        raise

    print()
    print_section("Info Ebook", icon="info")
    print_bullet(f"Judul  : {title}", indent=4)
    if author:
        print_bullet(f"Author : {author}", indent=4)
    print_bullet(f"Halaman: {total}", indent=4)
    print_bullet(f"Size   : {format_size(Path(pdf_path).stat().st_size)}", indent=4)
    print_bullet(f"DPI    : {DEFAULT_DPI}", indent=4)

    from tools.prompt import prompt_yes_no
    if not prompt_yes_no("Lanjut render?", default="y"):
        return False

    READERS.mkdir(parents=True, exist_ok=True)
    slug_base = slugify(title, max_len=50)
    slug = unique_folder_name(slug_base, str(READERS))
    out_dir = READERS / slug
    images_dir = out_dir / "images"
    out_html = out_dir / "index.html"
    images_dir.mkdir(parents=True, exist_ok=True)

    print()
    print_section(f"Render {total} Halaman", icon="hammer")
    start = time.time()
    try:
        sections, failures = _render_pdf_pages(pdf_path, total, images_dir)
    except Exception as exc:
        print_error(f"Render gagal sebelum halaman dibuat: {type(exc).__name__}: {exc}")
        shutil.rmtree(out_dir, ignore_errors=True)
        return False

    ok = len(sections)
    print_success(f"Render selesai: {ok}/{total} halaman")
    if failures:
        print_error(f"{len(failures)} halaman gagal")
        for page, err in failures[:5]:
            print_bullet(f"Hal {page}: {err}", indent=6)
        if len(failures) > 5:
            print_bullet(f"… dan {len(failures)-5} lainnya", indent=6)

    # Never publish a partial ebook as if it were complete.
    if ok != total:
        print_error("Import dibatalkan: asset halaman belum lengkap. Reader tidak dipublikasikan.")
        print_info(f"Output parsial disimpan untuk diagnosis: {out_dir}")
        return False

    spinner = LoadingSpinner("Generate HTML...")
    spinner.start()
    try:
        payload = build_payload(
            title, author, sections,
            properties={
                "format": "PDF",
                "page_count": total,
                "source_name": Path(pdf_path).name,
                "size_bytes": Path(pdf_path).stat().st_size,
                "dpi": DEFAULT_DPI,
            },
        )
        render_reader_html(str(ROOT / "templates" / "reader" / "reader.html"), str(out_html), payload, "ebook")
        # Final integrity check.
        missing = [s["page"] for s in sections if not (out_dir / s["src"]).is_file()]
        if missing:
            raise RuntimeError(f"Asset hilang setelah render: {missing[:10]}")
    except Exception as exc:
        if spinner.running:
            spinner.stop(f"Gagal generate HTML: {exc}", status="error")
        return False
    finally:
        if spinner.running:
            spinner.stop()

    duration = time.time() - start
    print()
    print_section("Import Selesai", icon="check")
    print_success(f"Ebook '{title}' berhasil di-import!")
    print_bullet(f"Halaman : {ok}/{total}", indent=4)
    print_bullet(f"Durasi  : {format_duration(duration)}", indent=4)
    print_bullet(f"Size    : {format_size(get_folder_size(str(out_dir)))}", indent=4)
    print_bullet(f"Lokasi  : {out_dir}", indent=4)
    print_access_hint(slug)
    return True
