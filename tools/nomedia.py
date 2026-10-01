"""
GhostWriter — tools/nomedia.py

Auto-generate file .nomedia biar image output (PDF/comic) gak
muncul di Gallery/Photos Android.

Cara kerja:
    File .nomedia kosong di folder → Android Media Scanner SKIP
    folder itu saat indexing gallery.

Kapan dipanggil:
    - Setiap render PDF/comic  → via ensure_full_tree()
    - Setiap render chat       → via ensure_full_tree()
    - Saat init project        → via ensure_nomedia("public")

Standar Android:
    .nomedia didukung sejak Android 4.1 (Jelly Bean, 2012).
    Berlaku per-folder — TIDAK recursive.

Path aman:
    public/                            ← root output
    public/readers/                    ← parent ebook
    public/comics/                     ← parent comic
    public/history/                    ← parent chat
    public/readers/<slug>/             ← per ebook
    public/readers/<slug>/images/      ← per image (WAJIB)
"""

from pathlib import Path


NOMEDIA_FILENAME = ".nomedia"


# ============================================================
# INTERNAL
# ============================================================

def _warn(msg: str) -> None:
    """Internal warning — self-contained, gak import tools.loading."""
    print(f"  ⚠️  {msg}")


def _create_nomedia(folder: Path) -> bool:
    """
    Bikin file .nomedia kosong di folder kalau belum ada.
    Return True kalau file ada (dibuat baru atau udah ada).
    """
    if not isinstance(folder, Path):
        folder = Path(folder)

    nomedia_path = folder / NOMEDIA_FILENAME

    if nomedia_path.exists():
        return True

    try:
        nomedia_path.touch()
        return True
    except OSError as e:
        _warn(f"Gagal bikin .nomedia di {folder}: {e}")
        return False


# ============================================================
# PUBLIC API
# ============================================================

def ensure_nomedia(folder) -> bool:
    """
    Bikin .nomedia di 1 folder (idempotent).
    Return True kalau folder berhasil di-mark.
    """
    folder = Path(folder)
    if not folder.is_dir():
        return False
    return _create_nomedia(folder)


def ensure_parent_chain(folder, stop_at: str = "public") -> None:
    """
    Walk up dari `folder` ke parent sampai ketemu folder `stop_at`.
    Mark .nomedia di setiap folder yang dilewatin (kecuali stop_at
    itu sendiri — tapi termasuk stop_at).

    Contoh:
        ensure_parent_chain(Path("public/readers/slug"), stop_at="public")
        → mark: public/readers/slug
                public/readers
                public
    """
    folder = Path(folder)
    current = folder.parent

    while current and current.name and current.name != stop_at:
        # Safety: jangan lewat root filesystem
        if current == current.parent:
            return
        _create_nomedia(current)
        current = current.parent

    # Mark folder stop_at kalau ketemu
    if current and current.name == stop_at:
        _create_nomedia(current)


def ensure_full_tree(folder) -> bool:
    """
    Bikin .nomedia di:
      - folder itu sendiri
      - folder/images (kalau ada)
      - parent chain sampai 'public'

    Ini API utama yang dipanggil dari render function.
    Return True kalau folder utama berhasil di-mark.
    """
    folder = Path(folder)
    if not folder.is_dir():
        return False

    ok = _create_nomedia(folder)

    images_dir = folder / "images"
    if images_dir.is_dir():
        _create_nomedia(images_dir)

    ensure_parent_chain(folder, stop_at="public")

    return ok


def cleanup_nomedia(folder) -> bool:
    """
    Hapus .nomedia dari folder (debug / manual un-hide).
    Return True kalau file dihapus.
    """
    folder = Path(folder)
    nomedia_path = folder / NOMEDIA_FILENAME

    if not nomedia_path.exists():
        return False

    try:
        nomedia_path.unlink()
        return True
    except OSError:
        return False