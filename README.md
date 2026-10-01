# 👻 GhostWriter+ v3.3.4

> **AI Chat & Digital Content Archive** — Konversi arsip obrolan AI, ebook (EPUB/MOBI/TXT/PDF), dan comic ZIP jadi web viewer interaktif bertema Midnight.

[![Version](https://img.shields.io/badge/version-v3.3.4--GW+-blue)](https://github.com/nexterade/GhostWriterPlus)
[![License](https://img.shields.io/badge/license-MIT-green)](Licence.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-passed-brightgreen)](tests/)

---

## ✨ Fitur

### 💬 Chat Archive
- **Multi-format Parser** — JSON, Markdown, DOCX
- **Multi-platform** — ChatGPT/OpenAI, Claude, Gemini, DeepSeek, Generic JSON
- **Share URL Import** — Paste public share link (ChatGPT, Claude, Gemini, DeepSeek, Perplexity, Copilot, Grok, Poe, You.com)
- **DeepSeek Live Backup** — via Bearer token (auto-refresh, incremental)
- **Attachment Manifest** — list file yang perlu download manual
- **HTML Viewer** — search, copy, collapsible, KaTeX, syntax highlight
- **Code Block Qwen-style** — collapse >10 line, fullscreen, copy, download
- **Action Buttons DeepSeek-style** — Copy, TTS, Share, Bookmark, Menu
- **Export** — save as .md, .json, atau print → PDF
- **Viewer Tools** — export full chat Markdown/JSON, regex search, role filter, collapse/expand semua
- **Offline-first** — mini-markdown parser (no CDN dependency)

### 📖 Ebook Reader (EPUB/MOBI/TXT/PDF)
- **EPUB Native** — ZIP + XML/XHTML parsing, spine order
- **MOBI** — via Calibre `ebook-convert`, fallback ke paket `mobi`
- **TXT** — auto-pagination (3000 char/page)
- **PDF Image Mode** — render tiap halaman jadi JPEG (DPI 150)
- **PDF Batch Render** — 8 halaman per batch, fallback per halaman
- **Metadata Extraction** — title, author, page count
- **Title Fallback** — kalau metadata "Untitled" → pake nama file

### 🎨 Comic Reader (ZIP)
- **Multi-format** — .jpg, .jpeg, .png, .webp, .gif, .bmp, .avif
- **Natural Sort** — 1, 2, 10 (bukan 1, 10, 2)
- **Skip Junk** — __MACOSX, ._*, .DS_Store, Thumbs.db
- **Flatten Nested** — semua gambar jadi 1 urutan

### 📚 Landing Page (Unified)
- **Tab Bar** — [📚 Semua] [💬 Chat] [📖 Ebook] [🎨 Comic]
- **Search Global** — filter by title (semua tipe)
- **Sort** — Terbaru, Judul A-Z, Pesan Terbanyak, Halaman, Ukuran
- **Date Grouping** — Hari Ini, Kemarin, 7 Hari, 30 Hari, Lebih Lama
- **Auto-Sync** — landing page update otomatis setelah render/import
- **Persist Tab** — tab terakhir ke-restore (localStorage)
- **Favorites / Recent** — ⭐ favorit, recent activity max 5, dan Grid/List view

### 📖 Reader Hybrid (GhostReader+)
- **2 Mode** — Horizontal (novel/comic/manga/al-quran) & Vertical (webtoon)
- **Page Flip** — CSS 3D animation (no library, no WebGL)
- **Alternative** — Slide / Fade (user-selectable)
- **Zoom** — Double-tap 2x, pinch 1x–4x, pan
- **Tap Zones** — Kiri/kanan untuk navigasi; tidak ada tap-to-hide chrome
- **Swipe Horizontal** — Page turn (mobile)
- **Keyboard** — ←/→, j/k, Home/End
- **Annotation** — Bookmark, highlight (EPUB/TXT), note (IndexedDB)
- **Reading Stats** — Progress, halaman, waktu baca, streak
- **Properties Buku** — Judul, author, format, halaman, dll
- **TTS Reader** — baca halaman aktif, pause/stop via SpeechSynthesis, pilihan locale Indonesia/English
- **Annotation Export** — JSON/Markdown
- **Global Reading Stats** — agregasi waktu, halaman, buku, dan streak berbasis localStorage
- **Brightness** — Overlay 30%–100%
- **Fit Mode** — Auto / Width / Height
- **Direction** — LTR / RTL (Manga)
- **Arabic Text Mode** — deteksi konten Arab/Quran secara generik dan aktifkan RTL + font Arab; tanpa mapping surah/ayat
- **Landscape** — Auto 2-page spread pada viewport landscape ≥769px; binding mengikuti LTR/RTL
- **Auto-migration** — Reader lama di-repair otomatis (serve.py)

### 🎨 Theme & UX
- **Dark/Light Mode** — toggle di semua viewer
- **CLI Midnight Theme** — spinner, progress bar, checklist
- **Loading Overlay** — progress bar animasi
- **Keyboard Shortcuts** — `?`, `/`, `j/k`, `Home/End`, `Esc`
- **Swipe Gesture** — mobile-friendly
- **Print-Friendly** — CSS @media print buat chat & reader
- **Path Canonical** — works dari CWD manapun (Termux/Android-friendly)

---

## 📦 Instalasi

### 1. Clone repo

    git clone https://github.com/nexterade/GhostWriterPlus.git
    cd GhostWriterPlus

### 2. Install Python dependencies

    pip install -r requirements.txt

**Isi `requirements.txt`:**
- `jinja2` — Template engine
- `requests` — HTTP request (DeepSeek + share URL)
- `python-docx` — Parse .docx
- `pypdf` — Baca metadata PDF
- `pdf2image` — Render PDF (fallback)
- `Pillow` — Image processing
- `mobi` — MOBI fallback (optional)

### 3. Install Poppler (WAJIB buat PDF import)

Poppler (`pdftoppm`) dibutuhkan buat render PDF. Install sesuai OS:

**Termux (Android):**
    pkg install poppler

**Ubuntu / Debian:**
    sudo apt install poppler-utils

**macOS:**
    brew install poppler

**Windows:** download dari [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases), tambahin ke PATH.

### 4. (Optional) Install Calibre buat MOBI

**Ubuntu / Debian:**
    sudo apt install calibre

**macOS:**
    brew install calibre

**Termux:** gak ada package resmi. Fallback ke paket Python `mobi`.

---

## 🚀 Cara Pakai

### Mode Wizard Interaktif

    python3 main.py

Muncul menu 6 opsi:
- `[1]` Import Chat File — JSON / Markdown / DOCX
- `[2]` Import Ebook — EPUB / MOBI / TXT / PDF
- `[3]` Import Comic ZIP — Manga, webtoon, comic strip
- `[4]` Live Backup DeepSeek — Tarik obrolan dari akun
- `[5]` Tutorial & Panduan — Panduan lengkap
- `[6]` Import Chat via Share URL — Paste public share link
- `[0]` Keluar

### Mode CLI Langsung

Render chat dari file backup:

    python3 main.py backup_chat.json
    python3 main.py backup_chat.json --all
    python3 main.py backup_chat.json --chat-index 0

### Taruh File di `inputs/`

Default folder input:
- `inputs/*.json` / `*.md` / `*.docx` — file backup chat
- `inputs/*.epub` / `*.mobi` / `*.txt` / `*.pdf` — ebook
- `inputs/*.zip` — comic ZIP

### Sync Manual

Sync index (kalau nambah/hapus folder manual):

    python3 sync.py

Auto-sync **udah jalan** setiap render/import selesai.

### Prune Folder Stale

Hapus folder yang gak ada di backup source:

    python3 sync.py --clean
    python3 sync.py --clean --dry-run
    python3 sync.py --clean --yes

### Test Suite

    python3 -m pytest -q

Expected: **50 tests passed**.

---

## 🖥️ Serve Output

**Wajib pakai HTTP server**, bukan `file://` (karena viewer fetch `index.json` via HTTP).

    python3 serve.py

Browser kebuka otomatis ke `http://localhost:8000/`.

**Opsi:**
    python3 serve.py --port 8080
    python3 serve.py --no-open

**Auto-migration:** Kalau ada reader lama (sebelum v3.0.9), `serve.py` otomatis repair ke template terbaru.

**Termux:** auto-detect & pakai `termux-open-url`.

---

## ⌨️ Keyboard Shortcuts

### Chat Viewer
| Key | Aksi |
|-----|------|
| `?` | Buka panel keyboard shortcuts |
| `/` | Fokus ke search box |
| `j` / `k` | Navigate pesan berikutnya / sebelumnya |
| `Home` | Scroll ke paling atas |
| `End` | Scroll ke paling bawah |
| `Esc` | Tutup sidebar / right rail / modal |

### Ebook / Comic Reader
| Key | Aksi |
|-----|------|
| `Esc` | Tutup panel / menu |
| `←` / `k` | Halaman sebelumnya |
| `→` / `j` | Halaman berikutnya |
| `Home` | Ke awal |
| `End` | Ke akhir |

### Landing Page
| Key | Aksi |
|-----|------|
| `/` | Fokus ke search box |

---

## 📁 Struktur

    GhostWriterPlus/
    ├── main.py                          # CLI entry point + wizard
    ├── serve.py                         # Local HTTP server + auto-migration
    ├── sync.py                          # Regenerate index + prune stale
    ├── exporter.py                      # HTMLExporter buat chat
    ├── requirements.txt                 # Python dependencies
    ├── README.md                        # ← file ini
    ├── CONTRIBUTING.md                  # Panduan kontribusi
    ├── Licence.md                       # MIT License
    │
    ├── core/                            # Core utilities
    │   └── paths.py                     # Path canonical (ROOT, INPUTS, ...)
    │
    ├── docs/                            # Dokumentasi
    │   ├── CHECKPOINT.md                # Aturan baku proyek
    │   ├── STATE.md                     # Snapshot status teknis
    │   ├── BACKLOG.md                   # Product roadmap (PR I-VIII)
    │   ├── GLOSARIUM.md                 # Command, flag, istilah
    │   ├── TUTORIAL.md                  # Panduan lengkap
    │   ├── ANNOTATIONS.md               # Schema annotation
    │   └── CHANGELOG.md                 # History perubahan
    │
    ├── inputs/                          # Folder input default
    │   ├── *.json / *.md / *.docx       # Chat backup
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
    ├── templates/                       # Template modular (Jinja2)
    │   ├── _shared/
    │   │   └── base.html                # HTML skeleton
    │   ├── viewer/                      # GhostReader+ Chat
    │   │   ├── viewer.html
    │   │   ├── style.css
    │   │   ├── script.js
    │   │   ├── mini-markdown.js         # Offline-first markdown
    │   │   └── partials/*.html
    │   └── reader/                      # GhostReader+ Ebook/Comic
    │       ├── reader.html
    │       ├── style.css
    │       ├── script.js
    │       └── partials/*.html
    │
    ├── parsers/                         # Parser file input
    │   ├── json_parser.py
    │   ├── md_parser.py
    │   └── docx_parser.py
    │
    ├── importers/                       # Importer
    │   ├── _reader_common.py
    │   ├── pdf_importer.py
    │   ├── comic_importer.py
    │   ├── ebook_importer.py
    │   ├── chat_importer.py
    │   └── chat_url_importer.py
    │
    ├── tools/                           # Utility modules
    │   ├── theme.py
    │   ├── loading.py
    │   ├── checklist.py
    │   ├── prompt.py
    │   ├── dist_index.py
    │   ├── download_vendor.py
    │   ├── nomedia.py
    │   └── deepseek_backup.py
    │
    ├── tests/                           # Test suite (32 passed)
    │   └── test_*.py
    │
    ├── data/                            # Data runtime (gitignored)
    │   ├── chats/
    │   ├── ebooks/
    │   ├── comics/
    │   ├── backups/
    │   └── tmp/
    │
    └── attachments/                     # Attachment chat manual
        └── PENDING.md

---

## 🔧 Troubleshooting

### "fetch index.json failed"
Pastiin akses via `http://localhost:8000/`, **bukan** `file://`.

### Port 8000 udah dipake
Ganti port: `python3 serve.py --port 8080`
Atau kill proses lama: `lsof -ti:8000 | xargs kill`

### PDF gak ke-render / error poppler
Install Poppler dulu (lihat **Instalasi → Poppler**).

### Import PDF lambat
Normal — 100 halaman bisa 5-15 menit (tergantung device & DPI).

### Gambar di comic/ebook gak ke-render
1. Cek Console browser (F12) — biasanya path salah
2. Atau format gak didukung (.avif butuh browser modern)

### Token expired terus-terusan
GhostWriter auto-invalidate token cache. Login ulang pake token baru dari DevTools.

### Landing page gak ke-update
Jalankan manual: `python3 sync.py`

### Lampiran gak ke-render
Buka `attachments/PENDING.md` — ikutin langkahnya. DeepSeek blokir download otomatis.

### Share URL import gagal
- Pastikan URL beneran public (bukan login-only)
- Kalau cuma dapet "partial import" → limitasi platform, bukan bug
- Cek Console — mungkin anti-bot challenge (Cloudflare)

---

## 💡 Tips & Trik

| Tips | Command |
|------|---------|
| Render 1 obrolan doang | `python3 main.py backup.json --chat-index 0` |
| Render semua obrolan | `python3 main.py backup.json --all` |
| Ganti port server | `python3 serve.py --port 8080` |
| Sync tanpa render ulang | `python3 sync.py` |
| Debug mode | `GW_DEBUG=1 python3 main.py` |
| Ganti delay backup | `GW_DELAY_MIN=2 GW_DELAY_MAX=4 python3 main.py` |
| Prune folder stale | `python3 sync.py --clean` |
| Preview prune | `python3 sync.py --clean --dry-run` |
| Run test suite | `python3 -m pytest -q` |
| Download vendor assets | `python3 -m tools.download_vendor` |

---

## 🎯 Roadmap v3.3.3

Detail lengkap ada di [`docs/BACKLOG.md`](docs/BACKLOG.md).

- **PR I** — Critical Fixes (path leak, size mismatch, version consistency)
- **PR II** — Documentation Refresh
- **PR III** — Medium Fixes
- **PR IV** — Viewer Features (export chat, search regex, filter role)
- **PR V** — Global Features (keyboard nav, favorites, grid view)
- **PR VI** — Reader Enhancement (Al-Quran mode, TTS, export annotation)
- **PR VII** — Extended Platform (Perplexity, Copilot, Grok, Poe, You.com)

**v3.3.3:** Import official ChatGPT export ZIP ditambahkan tanpa mengubah parser lokal existing. **Coming soon (v3.3.0+):** PWA, OCR, sync annotations, multi-user.

---

## 📜 Lisensi

MIT — lihat [LICENSE](Licence.md).

---

## 🙏 Credits

Dibuat dengan 👻 oleh **[@nexterade](https://github.com/nexterade)**.

**Third-party libraries:**
- [marked.js](https://marked.js.org/) — Markdown parser (fallback)
- [highlight.js](https://highlightjs.org/) — Syntax highlighting (optional)
- [KaTeX](https://katex.org/) — Math rendering (optional)

**Python dependencies:**
- [pypdf](https://pypdf.readthedocs.io/) — PDF metadata
- [pdf2image](https://github.com/Belval/pdf2image) — PDF rendering (fallback)
- [Pillow](https://python-pillow.org/) — Image processing
- [python-docx](https://python-docx.readthedocs.io/) — DOCX parsing
- [Poppler](https://poppler.freedesktop.org/) — PDF rendering backend
- [Calibre](https://calibre-ebook.com/) — MOBI conversion (optional)

---

## ⚠️ Disclaimer

Tool ini untuk **arsip pribadi**. Gunakan dengan bijak. Jangan distribusi konten yang gak lu punya hak-nya.

**Catatan:** Share URL import cuma works buat **public share link**. Private/login-only URL gak bisa diimpor tanpa mekanisme autentikasi yang disediakan platform.