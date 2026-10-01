================================================================================
STATE.md — GhostWriter+
Snapshot Status Teknis, Arsitektur, & Fitur
================================================================================
Versi    : v3.3.4
Update   : 2026-09-29
Author   : @nexterade
Berlaku  : Seluruh komponen proyek GhostWriter+
📎 FILE TERKAIT:
   · docs/CHECKPOINT.md   : aturan baku & filosofi proyek
   · docs/BACKLOG.md      : product roadmap & PR tracker
   · docs/GLOSARIUM.md    : command & flag
   · docs/CHANGELOG.md    : history perubahan
   · docs/TUTORIAL.md     : panduan penggunaan
================================================================================


================================================================================
1. OVERVIEW PROYEK
================================================================================

GhostWriter+ adalah tool CLI Python untuk mengarsipkan dan membaca konten
digital secara lokal, dengan output HTML interaktif yang bisa dibuka via
browser lokal.

Fitur utama:
  · Render arsip obrolan AI (ChatGPT, Claude, Gemini, DeepSeek) jadi viewer
  · Live backup dari akun DeepSeek (via token DevTools)
  · Import PDF ebook (image mode — cocok buat scan)
  · Import EPUB/MOBI/TXT (native parser — text reflow)
  · Import Comic ZIP (manga, webtoon, comic strip)
  · Landing page unified dengan tab, search, sort, filter
  · Reader Hybrid (Horizontal / Vertical)
  · Page flip (CSS 3D), zoom (pinch + double-tap + pan)
  · Annotation (bookmark, highlight, note) via IndexedDB
  · Share URL import (public chat links)
  · Offline-first (no CDN buat core features)

Target user:
  · Developer yang mau arsip chat AI secara lokal
  · Pembaca ebook/comic yang mau viewer ringan offline

Prinsip:
  · Local-first — semua data disimpan di device user
  · No-cloud — gak ada server backend, semua static HTML
  · Fast — ringan, bisa jalan di Termux/Android
  · Konsisten visual — theme dark/light, animasi smooth
  · Self-contained output — 1 file HTML, gak butuh asset eksternal
  · Offline-first — fitur core gak butuh network


================================================================================
2. ARSITEKTUR FOLDER
================================================================================

project/
├── main.py                          # CLI entry point + wizard mode
├── serve.py                         # Local HTTP server (serve public/)
├── sync.py                          # Regenerate index.json + index.html
├── exporter.py                      # HTMLExporter buat chat viewer
├── requirements.txt                 # Python dependencies
├── README.md                        # Dokumentasi publik
├── CONTRIBUTING.md                  # Panduan kontribusi
├── Licence.md                       # Lisensi (MIT)
│
├── core/                            # Core utilities (BARU v3.0.1)
│   └── paths.py                     # Single source of truth path canonical
│
├── docs/                            # Dokumentasi
│   ├── CHECKPOINT.md                # Aturan baku proyek
│   ├── STATE.md                     # ← file ini
│   ├── BACKLOG.md                   # Product roadmap (PR I-VIII)
│   ├── GLOSARIUM.md                 # Command, flag, argumen
│   ├── TUTORIAL.md                  # Panduan lengkap
│   ├── ANNOTATIONS.md               # Schema annotation
│   └── CHANGELOG.md                 # History perubahan (BARU)
│
├── inputs/                          # Folder input default
│   ├── *.json / *.md / *.docx       # File backup chat
│   ├── *.epub / *.mobi / *.txt      # Ebook text
│   ├── *.pdf                        # PDF ebook
│   └── *.zip                        # Comic ZIP
│
├── public/                          # Output HTML (di-serve)
│   ├── index.html                   # Landing page (auto)
│   ├── index.json                   # Metadata index (auto)
│   ├── history/                     # Chat viewer output
│   ├── readers/                     # Ebook output
│   ├── comics/                      # Comic output
│   └── vendor/                      # JS/CSS libraries
│
├── templates/                       # Template modular (v2.8.0+)
│   ├── _shared/
│   │   └── base.html                # HTML skeleton
│   │
│   ├── viewer/                      # GhostReader+ Chat
│   │   ├── viewer.html              # Main entry
│   │   ├── style.css                # Semua CSS
│   │   ├── script.js                # Semua JS
│   │   ├── mini-markdown.js         # Offline-first markdown
│   │   └── partials/
│   │       ├── loader.html
│   │       ├── overlays.html
│   │       ├── help-modal.html
│   │       ├── sidebar.html
│   │       ├── header.html
│   │       ├── chat-container.html
│   │       ├── floating-nav.html
│   │       ├── search-bar.html
│   │       ├── right-rail.html
│   │       └── toast.html
│   │
│   └── reader/                      # GhostReader+ Ebook/Comic
│       ├── reader.html              # Main entry
│       ├── style.css                # Semua CSS
│       ├── script.js                # Semua JS
│       └── partials/
│           ├── loader.html
│           ├── overlays.html
│           ├── help-modal.html
│           ├── sidebar.html
│           ├── header.html
│           ├── reader-container.html
│           ├── page-slider.html
│           ├── right-rail.html
│           └── toast.html
│
├── parsers/                         # Parser file input
│   ├── __init__.py
│   ├── base.py                      # ABC BaseParser
│   ├── json_parser.py               # Multi-platform JSON
│   ├── md_parser.py                 # Markdown
│   └── docx_parser.py               # DOCX
│
├── importers/                       # Importer
│   ├── __init__.py
│   ├── _reader_common.py            # Shared helper
│   ├── pdf_importer.py              # PDF → image
│   ├── comic_importer.py            # ZIP → image
│   ├── ebook_importer.py            # EPUB/MOBI/TXT
│   ├── chat_importer.py             # Local chat file
│   └── chat_url_importer.py         # Share URL
│
├── tools/                           # Utility modules
│   ├── __init__.py
│   ├── theme.py                     # Colors, theme, LOGO_SVG
│   ├── loading.py                   # Spinner, print helpers
│   ├── checklist.py                 # Interactive checklist
│   ├── prompt.py                    # Prompt helpers
│   ├── dist_index.py                # Index generator
│   ├── download_vendor.py           # Vendor downloader
│   ├── nomedia.py                   # Auto .nomedia
│   └── deepseek_backup.py           # DeepSeekLiveBackup
│
├── tests/                           # Test suite (50 passed)
│   ├── __init__.py
│   ├── test_annotations.py
│   ├── test_core.py
│   ├── test_ebook_importer.py
│   ├── test_reader_features.py
│   ├── test_reader_focus.py
│   ├── test_reader_modes.py
│   └── test_viewer_nested_collapse.py
│
├── data/                            # Data runtime (BARU v3.0.1)
│   ├── chats/
│   ├── ebooks/
│   ├── comics/
│   ├── backups/
│   └── tmp/
│
├── attachments/                     # Attachment chat manual
│   └── PENDING.md
├── .deepseek_token                  # Token cache (chmod 600)
└── .gitignore                       # Ignore: public/, data/, inputs/


================================================================================
3. DEPENDENCY & ENVIRONMENT
================================================================================

Python version:
  · Python 3.8+ (tested di Termux Python 3.11)

Python packages (requirements.txt):
  · jinja2             # Template engine
  · requests           # HTTP request (DeepSeek + share URL)
  · python-docx        # Parse file .docx
  · pypdf              # Baca metadata & count halaman PDF
  · pdf2image          # Render PDF (fallback)
  · Pillow             # Save image ke disk
  · mobi               # MOBI fallback (optional)

System dependencies:
  · Poppler (pdftoppm) — WAJIB buat PDF importer
    - Termux  : pkg install poppler
    - Ubuntu  : sudo apt install poppler-utils
    - macOS   : brew install poppler
  · Calibre (ebook-convert) — OPTIONAL buat MOBI
    - Termux  : gak ada package resmi
    - Ubuntu  : sudo apt install calibre
    - macOS   : brew install calibre

Tested environment:
  · Termux (Android) — primary
  · Ubuntu 22.04 — secondary
  · Windows 10/11 — partial (belum test Poppler)


================================================================================
4. ALUR KERJA (WORKFLOW)
================================================================================

4.1 IMPORT CHAT DARI FILE LOKAL
─────────────────────────────────
1. User taruh file .json/.md/.docx di inputs/
2. Jalankan: python3 main.py
3. Pilih menu [1] — Import Chat File
4. Pilih file, pilih convo (kalau bulk)
5. main.py:
   - Parse via JSONChatParser / MarkdownChatParser / DocxChatParser
   - Normalize ke schema standard
   - Export ke public/history/<slug>/index.html
6. Landing page update otomatis

4.2 IMPORT CHAT VIA SHARE URL
──────────────────────────────
1. Jalankan: python3 main.py
2. Pilih menu [6] — Import Chat via Share URL
3. Paste URL share publik (ChatGPT, Claude, Gemini, DeepSeek, generic)
4. main.py:
   - Fetch share page
   - Extract structured data (Next/React, semantic HTML)
   - Fallback ke HTML text extractor
   - Normalize → export ke public/history/
5. Kalau partial import → ditandai di metadata

4.3 IMPORT EBOOK (EPUB/MOBI/TXT/PDF)
─────────────────────────────────────
1. User taruh file di inputs/
2. Jalankan: python3 main.py
3. Pilih menu [2] — Import Ebook
4. Pilih file (auto-detect format)
5. main.py:
   - EPUB: native parser (ZIP + XML/XHTML)
   - MOBI: convert via calibre, fallback ke paket `mobi`
   - TXT: pagination otomatis (3000 char/page)
   - PDF: render via Poppler → JPEG 150 DPI
   - Generate HTML via templates/reader/reader.html
6. Landing page update otomatis

4.4 IMPORT COMIC ZIP
─────────────────────
1. User taruh file .zip di inputs/
2. Jalankan: python3 main.py
3. Pilih menu [3] — Import Comic ZIP
4. Pilih ZIP
5. main.py:
   - Inspect ZIP (list image, natural sort)
   - Extract image → keep format asli
   - Generate HTML reader
6. Landing page update otomatis

4.5 LIVE BACKUP DEEPSEEK
──────────────────────────
1. Jalankan: python3 main.py
2. Pilih menu [4] — Live Backup DeepSeek
3. Paste token dari DevTools
4. Pilih obrolan (range/checklist/all)
5. main.py:
   - Fetch daftar obrolan via API
   - Backup per obrolan → data/backups/backup_<slug>_<timestamp>.json
   - Auto-prune backup lama (keep 5 versi)
   - Auto-render ke public/history/
6. Attachment pending → attachments/PENDING.md


================================================================================
5. STRUKTUR DATA (SCHEMA)
================================================================================

5.1 CHAT DATA (hasil parse)
────────────────────────────
{
  "title": "Judul Percakapan",
  "created_at": "2026-09-29 10:30",
  "messages": [
    {
      "role": "user" | "assistant" | "system",
      "content": "Isi pesan (markdown)",
      "timestamp": "HH:MM",
      "attachments": [...]
    }
  ],
  "source_url": "https://..." (optional),
  "platform": "ChatGPT" (optional),
  "partial_import": true | false (optional)
}

5.2 READER PAYLOAD (ebook/comic)
─────────────────────────────────
{
  "title": "Judul Ebook/Comic",
  "author": "Author Name",
  "pages": 145,
  "book_id": "sha256:...",
  "annotation_schema": 1,
  "properties": {
    "format": "PDF" | "EPUB" | "MOBI" | "TXT" | "Comic ZIP",
    "page_count": 145,
    "source_name": "book.pdf",
    "size_bytes": 1234567,
    "dpi": 150 (optional)
  },
  "sections": [
    {
      "page": 1,
      "type": "image" | "text",
      "src": "images/page_001.jpg" (kalau image),
      "content": "..." (kalau text),
      "resource": "chapter-1.xhtml" | "images/page_001.jpg",
      "anchor": {"scheme": "text" | "image", "resource": "..."}
    }
  ]
}

5.3 INDEX.JSON SCHEMA
──────────────────────
{
  "count": 27,
  "count_by_type": {
    "chat": 24,
    "ebook": 2,
    "comic": 1
  },
  "generated_at": "2026-09-29T10:30:45",
  "items": [
    {
      "id": "1789829764",
      "folder": "history/1789829764",
      "title": "Pahami GhostWriter",
      "type": "chat",
      "size_kb": 881.7,
      "msg_count": 108,
      "pages": 0,
      "created_at": "2026-09-29 10:24",
      "first_created": "18:24",
      "mtime": 1789829742.06
    }
  ]
}

5.4 ANNOTATION SCHEMA (IndexedDB)
──────────────────────────────────
{
  "annotation_id": "ann_...",
  "book_id": "sha256:...",
  "type": "bookmark" | "highlight" | "note",
  "location": {
    "scheme": "text" | "image",
    "page_index": 0,
    "resource": "chapter-03.xhtml"
  },
  "quote": "..." (khusus highlight),
  "prefix": "..." (khusus highlight),
  "suffix": "..." (khusus highlight),
  "note": "..." (khusus note),
  "created_at": "2026-09-29T00:00:00Z",
  "updated_at": "2026-09-29T00:00:00Z"
}


================================================================================
6. STATUS RILIS — v3.3.2
================================================================================

PR I–VII dan polish batch v3.2.6–v3.3.2 selesai; baseline audit sebelumnya tercatat di v3.2.5.

Reader mobile:
  · Header, content, dan bottom slider berada dalam normal flex flow.
  · Reader memakai 100svh agar bottom slider tetap berada di small viewport.
  · Header dan slider tidak saling menutupi saat Android browser chrome muncul.

Current validation:
  · Python test suite: 50 passed
  · Reader JavaScript syntax: OK
  · Viewer JavaScript syntax: OK

PR berikutnya:
  · PR VIII — v3.3.0+ (PWA, OCR, sync annotations, multi-user, cloud sync)


================================================================================
8. DECISION LOG (KEPUTUSAN TEKNIS)
================================================================================

8.1 PDF IMPORTER — IMAGE MODE ONLY
───────────────────────────────────
Keputusan : Skip text extraction, image-only.
Alasan    : PDF scan modern kebanyakan image-based, text extraction
            gak reliable. User explicitly request image mode.
Impact    : Gak ada OCR, gak ada search text. Kalau butuh, tambah nanti.

8.2 KEEP FORMAT ASLI (COMIC)
─────────────────────────────
Keputusan : Comic importer keep format asli (.jpg, .png, .webp, dll).
Alasan    : Re-encode bisa lossy, hemat CPU, preserve animasi GIF.
Impact    : Image lebih variatif, tapi gak masalah buat browser modern.

8.3 NATURAL SORT (COMIC)
─────────────────────────
Keputusan : Pakai natural sort (1, 2, 10) bukan alfabet (1, 10, 2).
Alasan    : Comic biasanya urut halaman, natural sort lebih intuitif.

8.4 FOLDER OVERWRITE (PDF/COMIC)
─────────────────────────────────
Keputusan : Unique folder name (slug-2, slug-3) kalau slug sama.
Alasan    : Preserve archive lama, gak ada data loss.
Fallback  : Kalau slug base gak ada, pakai itu.

8.5 TAB DI LANDING PAGE
────────────────────────
Keputusan : Tab bar [Semua] [Chat] [Ebook] [Comic], default Chat.
Alasan    : Backward-compatible, scalable.

8.6 AUTO-SYNC SETELAH RENDER
─────────────────────────────
Keputusan : Auto-jalanin sync via ensure_index_synced().
Alasan    : Kalau sync error, handler tetap sukses.

8.7 CSS IMAGE READER
─────────────────────
Keputusan : .reader-page { overflow: visible, no bg, no border }.
Alasan    : Fix image crop + hilangkan padding gelap.

8.8 THEME STORAGE
──────────────────
Keputusan : localStorage key `gw-theme` (shared semua viewer).
Alasan    : Konsisten di seluruh app, user pilih sekali.

8.9 PROMPT MODULE EXTRACTION
─────────────────────────────
Keputusan : Pindah prompt helpers dari main.py ke tools/prompt.py.
Alasan    : Hilangkan circular import main.py ↔ importers/*.py.

8.10 GIT WORKFLOW SIMPLIFY
──────────────────────────
Keputusan : Buang git lama, re-init git baru dengan workflow simplify.
Alasan    : User frustasi sama rebase/merge/conflict marker.
Dilarang  : rebase, merge, pull, push, branch, reset --hard.

8.11 WORKFLOW BACKUP MANUAL (JAMAN PURBA MODE)
───────────────────────────────────────────────
Keputusan : Copy folder manual buat "checkpoint" sebelum batch besar.
Alasan    : Git di Termux/shared storage bisa bikin masalah.
Status    : ACTIVE.

8.12 WORKFLOW ZIP
──────────────────
Keputusan : Batch besar pake workflow ZIP (ZIP in → ZIP out).
Alasan    : File besar susah dikirim per file.
Status    : ACTIVE.

8.13 TEMPLATE MODULAR
──────────────────────
Keputusan : Split templates jadi folder modular (_shared, viewer, reader).
Alasan    : File 3000 baris susah maintain.
Struktur  : CSS/JS 1 file per viewer, HTML di partials.
Output    : Self-contained (inline via Jinja2 {% include %}).

8.14 READER REBUILD — HYBRID (v3.0.0)
─────────────────────────────────────
Keputusan : Reader rebuild total — Hybrid (Horizontal / Vertical).
Alasan    : v2.8.x banyak patch incremental, state machine berantakan.
Fitur     : Page flip (CSS 3D, no library), zoom, annotation.
Hasil     : 2 mode aja (Horizontal untuk page-based, Vertical untuk scroll).

8.15 FOCUS MODE DIHAPUS (v3.0.9)
────────────────────────────────
Keputusan : Hapus Focus Mode & browser Fullscreen API dependency.
Alasan    : Di HP hasilnya sama, bikin kompleks.
Hasil     : Saat ini reader tetap memakai 2 mode; chrome persistent dan tidak ada tap-to-hide.

8.16 PATH CANONICAL (v3.0.1)
─────────────────────────────
Keputusan : Bikin core/paths.py — single source of truth.
Alasan    : CWD-dependent path bikin FileNotFoundError di Termux.
Hasil     : Semua path absolute, gak peduli CWD.

8.17 OFFLINE-FIRST MARKDOWN (v3.2.1)
─────────────────────────────────────
Keputusan : Bikin mini-markdown.js — parser lokal.
Alasan    : CDN dependency bikin viewer gak works offline.
Hasil     : ~10 KB parser, support GFM, XSS sanitization.
Fallback  : Kalau marked.js ada, gak dipake.

8.18 ANNOTATION INDEXEDDB (v3.1.1)
──────────────────────────────────
Keputusan : Pake IndexedDB buat annotation, localStorage buat fallback.
Alasan    : IndexedDB lebih scalable, support structured data.
Schema    : {annotation_id, book_id, type, location, quote, prefix, suffix}.
Migration : Dari localStorage lama otomatis.

8.19 CONSOLIDATE CHANGELOG
──────────────────────────
Keputusan : Merge 21+ file CHANGELOG-vX.Y.Z.md → docs/CHANGELOG.md.
Alasan    : Root folder berantakan, susah cari history.
Format    : Keep a Changelog, section per version (terbaru di atas).
Status    : Akan dieksekusi di PR II-E.


================================================================================
9. TESTING CHECKLIST
================================================================================

9.1 SMOKE TEST
───────────────────────────────
1. python3 main.py → menu muncul 6 opsi
2. Pilih [5] Tutorial → tampil lengkap
3. Pilih [0] → keluar

9.2 IMPORT CHAT (JSON/MD/DOCX)
───────────────────────────────
1. Taruh file di inputs/
2. python3 main.py → [1] → pilih file
3. Pilih convo (kalau bulk)
4. Cek public/history/<slug>/index.html ada
5. Buka via serve.py → cek markdown, code, katex

9.3 IMPORT CHAT VIA SHARE URL
──────────────────────────────
1. python3 main.py → [6]
2. Paste URL share publik
3. Cek public/history/<slug>/index.html
4. Kalau partial → cek flag di metadata

9.4 IMPORT PDF
────────────────────────────
1. Taruh PDF di inputs/
2. python3 main.py → [2] → pilih PDF
3. Cek public/readers/<slug>/index.html + images/
4. Cek judul (fallback kalau "Untitled")
5. Buka via serve.py → page flip works

9.5 IMPORT EPUB/MOBI/TXT
────────────────────────────
1. Taruh file di inputs/
2. python3 main.py → [2] → pilih file
3. Cek public/readers/<slug>/index.html
4. Buka via serve.py → teks reflow

9.6 IMPORT COMIC
────────────────
1. Taruh ZIP di inputs/
2. python3 main.py → [3] → pilih ZIP
3. Cek urutan halaman (natural sort)
4. Buka via serve.py → image muncul

9.7 LIVE BACKUP DEEPSEEK
────────────────────────
1. python3 main.py → [4]
2. Paste token dari DevTools
3. Pilih obrolan → backup
4. Cek data/backups/backup_*.json
5. Cek public/history/

9.8 READER FEATURES
────────────────────
1. Buka reader: /readers/<slug>/ atau /comics/<slug>/
2. Mode Horizontal → page flip works
3. Mode Vertical → scroll webtoon
4. Double-tap → zoom 2x
5. Pinch → zoom 1x-4x
6. Bookmark → persisten
7. Highlight teks (EPUB/TXT)
8. Note → persisten
9. Brightness slider
10. Fit: Auto/Width/Height
11. Direction: LTR/RTL (Manga)
12. Landscape → auto 2-page (viewport ≥769px)

9.9 LANDING PAGE
────────────────
1. Buka http://localhost:8000/
2. Tab: Semua, Chat, Ebook, Comic
3. Search: / → filter
4. Sort: Terbaru, Judul A-Z, Pesan, Halaman, Ukuran
5. Cek meta info per tipe

9.10 SERVE.PY AUTO-MIGRATION
─────────────────────────────
1. Render reader lama (versi sebelum v3.0.9)
2. python3 serve.py
3. Cek output: "Memperbarui N reader lama"
4. Reader lama di-regenerate ke template baru

9.11 TEST SUITE
───────────────
1. python3 -m pytest -q
2. Expected: 50 tests passed


================================================================================
10. KNOWN ISSUES
================================================================================

10.1 CRITICAL — RESOLVED IN v3.2.5
────────────────────────────────────
· test_core.py path leak → FIXED; uses TemporaryDirectory.
· scan_dist() size_kb mismatch → FIXED.
· scan_dist() lowercase display title → FIXED via display_title + dedup_key.
· Version consistency → FIXED; current markers use v3.3.4.

10.2 MEDIUM — RESOLVED IN v3.2.5
────────────────────────────────────
· `_ANSI_RE` duplicate → FIXED.
· Reader header structural marker → FIXED.
· Reader version assertion → dynamic semver assertion.
· `print_prompt()` → reviewed; retained because `main.py` still uses it.

10.3 LOW (Nice to have)
───────────────────────
🟢 IntersectionObserver reader.html berat kalau 100+ halaman
   Fix    : Virtualization (future)

🟢 CHANGELOG.md masih 21+ file di root (v3.2.3)
   Fix    : PR II-E (consolidate ke docs/CHANGELOG.md)


================================================================================
12. v3.2.5 IMPLEMENTATION SNAPSHOT
================================================================================


· Test path leak memakai TemporaryDirectory; production history tidak menjadi target test.
· Landing chat metadata memakai display title + dedup key terpisah dan size_kb.
· Viewer: Markdown/JSON export, regex search fallback, role filter, collapse/expand semua.
· Landing: keyboard j/k/Enter/Esc, recent max 5, favorites, Grid/List, system theme auto.
· Reader: generic Arabic Text Mode (RTL + Arabic font), TTS, annotation JSON/MD export, global stats.
· Share URL: Perplexity, Copilot, Grok, Poe, You.com.
· Version marker current: v3.3.2.
· docs/CHECKPOINT.md sengaja tidak diubah.

================================================================================
11. FORENSIC NOTES
================================================================================

11.1 SESSION API DEEPSEEK — RAW RESPONSE KEYS
──────────────────────────────────────────────
{
  "chat_session": {"id", "title", "inserted_at", "updated_at", ...},
  "chat_messages": [{"message_id", "role", "content", "files", ...}],
  "cache_valid": false,
  "route_id": null
}
Catatan:
  · role UPPERCASE (USER, ASSISTANT)
  · inserted_at float epoch
  · files[].id = "file-{uuid}" format
  · search_results cuma muncul kalo search_enabled: true
  · thinking_content cuma muncul kalo thinking_enabled: true

11.2 ENDPOINT BEHAVIORS
────────────────────────
  /users/current                    → verify token
  /chat_session/fetch_page          → list sesi (cursor pagination)
  /chat/history_messages?chat_session_id=X → full message dump
  /file/download?file_id=X          → BROKEN via Bearer (balikin HTML)

11.3 ACCOUNT SUSPENSION LESSONS
────────────────────────────────
Trigger hypothesis:
  · Repeated prompt upload → flag "cross-platform copying"
  · Pattern request berubah drastis → risk control trigger
Mitigation:
  · Human-like delay + jitter (1-3s)
  · Session delay (3-7s)
  · Retry delay (5-10s)
  · Incremental backup

11.4 JAVASCRIPT PARSE ERROR CASCADE (v2.2)
───────────────────────────────────────────
Fenomena: Kurung kurawal `}` salah posisi → seluruh <script> gagal parse.
Lesson  : Browser JS parser forgiving — error muncul di baris gak berhubungan.
Fix     : Selalu cek Console (F12).

11.5 CIRCUIT BREAKER PATTERN (v2.2.2)
──────────────────────────────────────
Konteks : Endpoint /file/download balikin HTML challenge.
Solusi  : 1x kena HTML → set flag, skip request berikutnya.
Efek    : 50-150 detik → 1-3 detik (97% saving).

11.6 MOBILE VIEWPORT FRAGMENTATION (v2.3.0)
────────────────────────────────────────────
Fenomena: Keyboard mobile + address bar + safe-area bikin layout rusak.
Solusi  : CSS 100dvh + env(safe-area-inset-bottom) + visualViewport API.

11.7 BACKUP VERSIONING (v2.5.0)
────────────────────────────────
Solusi  : Backup filename timestamp, retention 5 versi terbaru.

11.8 PRUNE STALE FOLDER (v2.5.0)
─────────────────────────────────
Solusi  : Flag --clean di sync.py, auto-detect valid IDs dari backups.

11.9 SCROLL FADE + DIM + SCALE (v2.6.0)
────────────────────────────────────────
Solusi  : 4 state (init, active, dim-above, dim-below), IntersectionObserver.

11.10 LOADING OVERLAY (v2.6.4)
───────────────────────────────
Solusi  : Full-screen overlay + logo pulse + progress bar + shimmer.

11.11 BIDIRECTIONAL SWIPE GESTURE (v2.6.6)
───────────────────────────────────────────
Solusi  : Swipe bidirectional, edge priority, auto-close.

11.12 GIT WORKFLOW SIMPLIFY (v2.7.3)
─────────────────────────────────────
Solusi  : Cuma 5 command: status, add, commit, log, checkout.

11.13 BATCH 7A — READER R1-R15 (v2.7.3)
────────────────────────────────────────
Konteks : Reader.html di v2.6.9 cuma fitur dasar.
Implementasi: 15 fitur tambahan (auto-bookmark, immersive, zoom, dll).
Lesson  : File >1500 baris → boleh dipecah part.

11.14 BATCH 8 — MAJOR REFACTOR (v2.8.0)
────────────────────────────────────────
Konteks : Rebranding + split templates + new features.
Strategi: Workflow ZIP (user kirim ZIP, AI eksekusi, balikin ZIP).
Lesson  : File besar (>2000 baris) lebih baik dipecah modular.

11.15 READER REBUILD — HYBRID (v3.0.0)
───────────────────────────────────────
Konteks : v2.8.x banyak patch, state machine berantakan.
Strategi: Rebuild total, 2 mode aja (Horizontal/Vertical).
Lesson  : Kadang rebuild lebih baik dari patch increment.

11.16 FOCUS MODE REMOVED (v3.0.9)
──────────────────────────────────
Konteks : Focus Mode + Fullscreen API bikin kompleks.
Strategi saat ini: chrome persistent; tidak ada tap-to-hide.
Lesson  : Fitur yang gak nambah value = hapus.

11.17 PATH CANONICAL (v3.0.1)
──────────────────────────────
Konteks : CWD-dependent path bikin FileNotFoundError.
Strategi: core/paths.py — semua path absolute.
Lesson  : Path relative itu bug waiting to happen.

11.18 OFFLINE-FIRST MARKDOWN (v3.2.1)
──────────────────────────────────────
Konteks : CDN dependency bikin viewer gak works offline.
Strategi: mini-markdown.js — parser lokal ~10 KB.
Lesson  : Fitur core jangan bergantung ke CDN.

11.19 ANNOTATION INDEXEDDB (v3.1.1)
────────────────────────────────────
Konteks : Bookmark/highlight/note butuh storage scalable.
Strategi: IndexedDB primary, localStorage fallback.
Lesson  : Pilih storage sesuai kebutuhan (structured → IndexedDB).

11.20 VERSION CONSISTENCY ISSUE (v3.2.3)
─────────────────────────────────────────
Konteks : Version mismatch di banyak file (serve.py, reader.html, README).
Status  : PENDING (PR I-D).
Lesson  : Version harus single source of truth.


================================================================================
12. REFERENSI FILE KRITIS
================================================================================

- docs/CHECKPOINT.md                : Aturan baku proyek
- docs/BACKLOG.md                   : Product roadmap (PR I-VIII)
- docs/GLOSARIUM.md                 : Command, flag, argumen
- docs/TUTORIAL.md                  : Panduan lengkap
- docs/ANNOTATIONS.md               : Schema annotation
- docs/CHANGELOG.md                 : History perubahan
- core/paths.py                     : Path canonical
- main.py                           : CLI entry point
- serve.py                          : Local HTTP server + auto-migration
- sync.py                           : Index regenerator
- exporter.py                       : HTMLExporter (chat)
- tools/dist_index.py               : Index generator
- tools/deepseek_backup.py          : DeepSeek live backup
- tools/prompt.py                   : Prompt helpers
- importers/_reader_common.py       : Shared helper
- importers/pdf_importer.py         : PDF importer
- importers/comic_importer.py       : Comic ZIP importer
- importers/ebook_importer.py       : EPUB/MOBI/TXT importer
- importers/chat_importer.py        : Local chat file
- importers/chat_url_importer.py    : Share URL importer
- templates/_shared/base.html       : HTML skeleton
- templates/viewer/viewer.html      : GhostReader+ Chat
- templates/viewer/mini-markdown.js : Offline-first markdown
- templates/reader/reader.html      : GhostReader+ Ebook/Comic


================================================================================
END OF STATE.md — GhostWriter+ v3.3.4
================================================================================

## v3.3.2 — POLISH SNAPSHOT

Semua batch v3.2.6–v3.3.2 selesai. Reader dan viewer modular, landing/CLI dipoles, accessibility dan mobile target diperketat, serta runtime/generated-data hygiene diperbarui.


================================================================================
9. STATUS RILIS — v3.3.4
================================================================================

ChatGPT Export ZIP import: DONE. Official export ZIP dapat diproses langsung
melalui menu Import Chat File. conversations.json menjadi source-of-truth;
HTML/DAT dikenali sebagai bagian archive dan diekstrak sementara.

Security: safe extraction + path traversal guard + archive size/file-count limits.
================================================================================
