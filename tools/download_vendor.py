"""
GhostWriter — tools/download_vendor.py

Download vendor JS/CSS libraries ke <project_root>/public/vendor/.

Path absolute (via __file__), gak peduli CWD — jalanin dari mana aja
tetep output ke tempat yang bener.

Vendor assets:
    - marked.min.js                       (markdown parser)
    - highlight.min.js                    (syntax highlight)
    - highlight-tokyo-night-dark.min.css  (theme)
    - katex.min.js                        (math render)
    - katex.min.css                       (math style)
    - katex-auto-render.min.js            (auto math)

Auto-run dari main.py kalau asset missing (via ensure_vendor_ready()).
"""

import os
import urllib.request
from pathlib import Path


# ============================================================
# PATH (ABSOLUTE — gak peduli CWD)
# ============================================================

# File ini ada di <project_root>/tools/download_vendor.py
# parent = tools/
# parent.parent = project_root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = PROJECT_ROOT / "public" / "vendor"


# ============================================================
# ASSETS
# ============================================================

ASSETS = {
    "marked.min.js": "https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js",
    "highlight.min.js": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
    "highlight-tokyo-night-dark.min.css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css",
    "katex.min.js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",
    "katex.min.css": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css",
    "katex-auto-render.min.js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js",
    "vysmo-flipbook.esm.js": "https://esm.unpkg.com/@vysmo/flipbook@0.5.0",
}


# ============================================================
# DOWNLOAD
# ============================================================

def download_all(verbose: bool = True) -> tuple:
    """
    Download semua vendor assets ke public/vendor/.

    Args:
        verbose: Kalau True, print progress per file.

    Returns:
        (downloaded, skipped, failed) — tuple count.
    """
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    failed = 0

    for filename, url in ASSETS.items():
        target = VENDOR_DIR / filename

        # Skip kalau udah ada & gak kosong
        if target.exists() and target.stat().st_size > 0:
            if verbose:
                print(f"  [✓] Udah ada: {filename}")
            skipped += 1
            continue

        if verbose:
            print(f"  [⬇️] Downloading: {filename}")

        try:
            urllib.request.urlretrieve(url, target)
            size = target.stat().st_size
            if verbose:
                print(f"      → {size} bytes")
            downloaded += 1
        except Exception as e:
            if verbose:
                print(f"  [X] Gagal download {filename}: {e}")
            failed += 1

    if verbose:
        print()
        print(f"  Total: {downloaded} downloaded, {skipped} skipped, {failed} failed")

    return downloaded, skipped, failed


def ensure_vendor_ready() -> bool:
    """
    Cek apakah semua vendor asset ada. Kalau ada yang missing,
    auto-download (silent).

    Return True kalau semua asset ada setelah cek/download.
    """
    missing = [
        name for name in ASSETS
        if not (VENDOR_DIR / name).exists()
        or (VENDOR_DIR / name).stat().st_size == 0
    ]

    if not missing:
        return True

    # Ada yang missing — download silent
    download_all(verbose=False)

    # Re-verify
    for name in ASSETS:
        target = VENDOR_DIR / name
        if not target.exists() or target.stat().st_size == 0:
            return False
    return True


# ============================================================
# CLI ENTRY
# ============================================================

if __name__ == "__main__":
    print("📦 Download vendor assets...")
    print(f"    Project root : {PROJECT_ROOT}")
    print(f"    Target       : {VENDOR_DIR}")
    print()
    download_all()