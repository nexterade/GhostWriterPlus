================================================================================
GLOSARIUM.md — GhostWriter+
Referensi Command, Flag, Argumen, & Istilah
================================================================================
Versi    : v3.3.2
Update   : 2026-09-29
Author   : @nexterade
Berlaku  : Seluruh komponen proyek GhostWriter+
📎 FILE TERKAIT:
   · docs/CHECKPOINT.md   : aturan baku & filosofi proyek
   · docs/BACKLOG.md      : product roadmap & PR tracker
   · docs/STATE.md        : snapshot status teknis
   · docs/CHANGELOG.md    : history perubahan
   · docs/TUTORIAL.md     : panduan penggunaan
================================================================================

CARA PAKAI FILE INI:
────────────────────
Cari command/flag/istilah yang lu butuh. Struktur:
  · COMMAND — CLI command utama
  · FLAG — argumen CLI
  · MENU — pilihan wizard mode
  · ENV VAR — environment variable
  · STORAGE KEY — localStorage / IndexedDB key
  · ISTILAH — terminologi proyek

================================================================================
1. COMMAND UTAMA
================================================================================

python3 main.py
─────────────────────────────────────────────────────────────
Deskripsi : Entry point CLI + wizard mode.
Usage     : python3 main.py [input_file] [flags]
Tanpa arg : Masuk mode wizard interaktif (menu 1-6)
Dengan arg: Mode CLI langsung (render file)
Contoh    :
  $ python3 main.py
  $ python3 main.py backup.json
  $ python3 main.py backup.json --all
  $ python3 main.py backup.json --chat-index 0

python3 serve.py
─────────────────────────────────────────────────────────────
Deskripsi : Local HTTP server buat serve folder public/.
Usage     : python3 serve.py [flags]
Default   : Port 8000, auto-open browser
Auto-fix  : Migrate reader lama ke template terbaru (v3.0.9+)
Contoh    :
  $ python3 serve.py
  $ python3 serve.py --port 8080
  $ python3 serve.py --no-open

python3 sync.py
─────────────────────────────────────────────────────────────
Deskripsi : Regenerate public/index.json + public/index.html.
Usage     : python3 sync.py [flags]
Kapan     : Kalau nambah/hapus folder manual di public/
Auto-sync : Udah jalan otomatis setelah render (chat/PDF/comic)
Contoh    :
  $ python3 sync.py
  $ python3 sync.py --clean
  $ python3 sync.py --clean --dry-run
  $ python3 sync.py --clean --yes

python3 -m pytest -q
─────────────────────────────────────────────────────────────
Deskripsi : Run test suite (pytest).
Usage     : python3 -m pytest -q
Expected  : 50 tests passed
Kapan     : Sebelum rilis / setelah edit core

python3 -m tools.download_vendor
─────────────────────────────────────────────────────────────
Deskripsi : Download vendor assets ke public/vendor/.
Usage     : python3 -m tools.download_vendor
Auto-run  : Kalau asset missing, auto-download silent via main.py
Kapan     : Manual, kalau vendor asset korup / hilang

================================================================================
2. FLAG — MAIN.PY
================================================================================

--chat-index N
─────────────────────────────────────────────────────────────
Tipe      : Integer
Default   : None (render semua)
Deskripsi : Pilih convo berdasarkan index (0-based).
Contoh    : python3 main.py backup.json --chat-index 0
            (render convo pertama aja)

--all
─────────────────────────────────────────────────────────────
Tipe      : Boolean flag
Default   : False
Deskripsi : Render semua convo dalam file.
Contoh    : python3 main.py backup.json --all

================================================================================
3. FLAG — SERVE.PY
================================================================================

--port, -p N
─────────────────────────────────────────────────────────────
Tipe      : Integer
Default   : 8000
Deskripsi : Port HTTP server.
Contoh    : python3 serve.py --port 8080

--no-open
─────────────────────────────────────────────────────────────
Tipe      : Boolean flag
Default   : False (auto-open browser)
Deskripsi : Jangan auto-open browser, tanya dulu.
Contoh    : python3 serve.py --no-open

================================================================================
4. FLAG — SYNC.PY
================================================================================

--clean
─────────────────────────────────────────────────────────────
Tipe      : Boolean flag
Default   : False
Deskripsi : Prune folder stale di public/history/ yang gak ada
            di source backup.
Contoh    : python3 sync.py --clean

--dry-run
─────────────────────────────────────────────────────────────
Tipe      : Boolean flag
Default   : False
Deskripsi : Preview folder yang bakal dihapus (gak eksekusi).
Contoh    : python3 sync.py --clean --dry-run

--yes, -y
─────────────────────────────────────────────────────────────
Tipe      : Boolean flag
Default   : False
Deskripsi : Skip konfirmasi (buat script/CI).
Contoh    : python3 sync.py --clean --yes

--keep ID1,ID2
─────────────────────────────────────────────────────────────
Tipe      : String (comma-separated)
Default   : "" (auto-detect dari backups/)
Deskripsi : Manual: comma-separated ID yang mau di-keep.
Contoh    : python3 sync.py --clean --keep 1789829764,1789830000

================================================================================
5. MENU — WIZARD MODE
================================================================================

[1] Import Chat File
─────────────────────────────────────────────────────────────
Deskripsi : Import chat dari file lokal.
Format    : JSON, Markdown, DOCX
Platform  : ChatGPT/OpenAI, Claude, Gemini, DeepSeek, Generic
Flow      : Pilih file → pilih convo → render
Output    : public/history/<slug>/index.html

[2] Import Ebook
─────────────────────────────────────────────────────────────
Deskripsi : Import ebook (text reflow + image mode).
Format    : EPUB, MOBI, TXT, PDF
Flow      : Pilih file → konfirmasi → import
Output    : public/readers/<slug>/index.html
Catatan   :
  · EPUB: native parser (ZIP + XML/XHTML)
  · MOBI: calibre `ebook-convert` atau paket `mobi`
  · TXT: pagination otomatis (3000 char/page)
  · PDF: render via Poppler (JPEG 150 DPI)

[3] Import Comic ZIP
─────────────────────────────────────────────────────────────
Deskripsi : Import comic ZIP (manga, webtoon, comic strip).
Format    : .zip (image: jpg, png, webp, gif, bmp, avif)
Flow      : Pilih ZIP → extract → render
Output    : public/comics/<slug>/index.html
Catatan   : Natural sort (1, 2, 10), skip junk files

[4] Live Backup DeepSeek
─────────────────────────────────────────────────────────────
Deskripsi : Backup obrolan dari akun DeepSeek (via token).
Flow      : Paste token → pilih obrolan → backup
Mode      : Incremental (default) / Full
Output    : data/backups/backup_<slug>_<timestamp>.json
            + public/history/<id>/index.html
Catatan   : Attachment pending → attachments/PENDING.md

[5] Tutorial & Panduan
─────────────────────────────────────────────────────────────
Deskripsi : Tampilkan tutorial lengkap.
Isi       : Quick start, PDF/comic import, troubleshooting, dll

[6] Import Chat via Share URL
─────────────────────────────────────────────────────────────
Deskripsi : Import chat dari public share URL.
Platform  : ChatGPT, Claude, Gemini, DeepSeek, Generic
Flow      : Paste URL → fetch → extract → render
Output    : public/history/<slug>/index.html
Catatan   :
  · Structured data (Next/React) diprioritasin
  · Fallback: semantic HTML extraction
  · Kalau partial → flag `partial_import: true`
  · URL private/login-only gak bisa

[0] Keluar
─────────────────────────────────────────────────────────────
Deskripsi : Keluar dari wizard mode.

================================================================================
6. ENV VAR
================================================================================

GW_DEBUG
─────────────────────────────────────────────────────────────
Tipe      : String ("1" = enable)
Default   : "" (disabled)
Deskripsi : Enable debug mode — print full traceback pas error.
Contoh    : GW_DEBUG=1 python3 main.py

GW_DELAY_MIN / GW_DELAY_MAX
─────────────────────────────────────────────────────────────
Tipe      : Float (seconds)
Default   : 1.0 / 3.0
Deskripsi : Human-like delay buat DeepSeek backup (anti-suspend).
Contoh    : GW_DELAY_MIN=2 GW_DELAY_MAX=4 python3 main.py

GW_SESSION_DELAY_MIN / GW_SESSION_DELAY_MAX
─────────────────────────────────────────────────────────────
Tipe      : Float (seconds)
Default   : 3.0 / 7.0
Deskripsi : Delay antar obrolan (DeepSeek backup).
Contoh    : GW_SESSION_DELAY_MIN=5 GW_SESSION_DELAY_MAX=10 python3 main.py

GW_RETRY_DELAY_MIN / GW_RETRY_DELAY_MAX
─────────────────────────────────────────────────────────────
Tipe      : Float (seconds)
Default   : 5.0 / 10.0
Deskripsi : Delay sebelum retry (kalau request gagal).
Contoh    : GW_RETRY_DELAY_MIN=8 GW_RETRY_DELAY_MAX=15 python3 main.py

================================================================================
7. STORAGE KEY — LOCALSTORAGE
================================================================================

gw-theme
─────────────────────────────────────────────────────────────
Value     : "dark" | "light"
Dipakai   : Landing page, viewer, reader (shared).
Deskripsi : Tema aktif. Kalau gak ada, default "dark".

gw-active-tab
─────────────────────────────────────────────────────────────
Value     : "all" | "chat" | "ebook" | "comic"
Dipakai   : Landing page.
Deskripsi : Tab aktif (persist antar reload).

gw-scroll-<title>
─────────────────────────────────────────────────────────────
Value     : Integer (scroll position)
Dipakai   : Viewer (chat).
Deskripsi : Posisi scroll terakhir per chat.

gw3-<book_key>-mode
─────────────────────────────────────────────────────────────
Value     : "horizontal" | "vertical"
Dipakai   : Reader.
Deskripsi : Reader mode terakhir per buku.

gw3-<book_key>-page
─────────────────────────────────────────────────────────────
Value     : Integer (1-based)
Dipakai   : Reader.
Deskripsi : Halaman terakhir dibaca per buku.

gw3-<book_key>-effect
─────────────────────────────────────────────────────────────
Value     : "curl" | "slide" | "fade"
Dipakai   : Reader.
Deskripsi : Efek animasi page turn.

gw3-<book_key>-fit
─────────────────────────────────────────────────────────────
Value     : "auto" | "width" | "height"
Dipakai   : Reader.
Deskripsi : Mode fit gambar.

gw3-<book_key>-direction
─────────────────────────────────────────────────────────────
Value     : "ltr" | "rtl"
Dipakai   : Reader.
Deskripsi : Arah halaman (LTR buat comic barat, RTL buat manga).

gw3-<book_key>-brightness
─────────────────────────────────────────────────────────────
Value     : Integer (30-100)
Dipakai   : Reader.
Deskripsi : Brightness overlay (persentase).

gw3-<book_key>-reading-stats
─────────────────────────────────────────────────────────────
Value     : JSON { seconds, pagesSeen: [] }
Dipakai   : Reader.
Deskripsi : Statistik baca per buku.

================================================================================
8. STORAGE KEY — INDEXEDDB
================================================================================

ghostreader-annotations-v1
─────────────────────────────────────────────────────────────
Database  : IndexedDB
Object    : annotations
Schema    : {
              annotation_id: string,
              book_id: "sha256:...",
              type: "bookmark" | "highlight" | "note",
              location: {
                scheme: "text" | "image",
                page_index: int,
                resource: string
              },
              quote: string (khusus highlight),
              prefix: string (khusus highlight),
              suffix: string (khusus highlight),
              note: string (khusus note),
              created_at: ISO timestamp,
              updated_at: ISO timestamp
            }
Index     : book_id, type
Dipakai   : Reader (annotation).
Migration : Dari localStorage lama otomatis.

================================================================================
9. ISTILAH — TERMINOLOGI PROYEK
================================================================================

AI (Gue)
─────────────────────────────────────────────────────────────
Definisi  : AI Assistant / Co-Developer.
Konteks   : "GUE" di CHECKPOINT = AI.

User (Lu)
─────────────────────────────────────────────────────────────
Definisi  : Solo Developer / Owner Project.
Konteks   : "LU" / "LO" di CHECKPOINT = User.

Batch / PR
─────────────────────────────────────────────────────────────
Definisi  : Milestone besar di roadmap.
Format    : Angka Romawi (PR I, PR II, dst).
Konteks   : "Batch" = istilah lama (v1-v2.8), "PR" = istilah baru (v3.2.3+).

Sub-PR
─────────────────────────────────────────────────────────────
Definisi  : Task kecil di dalam PR.
Format    : Huruf (I-A, II-C, III-D, dst).
Contoh    : PR I-A = Critical fix path leak.

Wizard Mode
─────────────────────────────────────────────────────────────
Definisi  : Mode interaktif CLI (menu 1-6).
Konteks   : Dijalankan tanpa argumen: python3 main.py

CLI Mode
─────────────────────────────────────────────────────────────
Definisi  : Mode non-interaktif (langsung render).
Konteks   : Dijalankan dengan argumen: python3 main.py backup.json

Chat Viewer
─────────────────────────────────────────────────────────────
Definisi  : Tampilan chat (bubble, markdown, code).
File      : templates/viewer/viewer.html
Branding  : GhostReader+ Chat

Reader
─────────────────────────────────────────────────────────────
Definisi  : Tampilan ebook/comic (page flip, zoom).
File      : templates/reader/reader.html
Branding  : GhostReader+ Ebook / Comic

Landing Page
─────────────────────────────────────────────────────────────
Definisi  : Halaman index yang list semua konten.
File      : public/index.html (auto-generated)

Dist Index
─────────────────────────────────────────────────────────────
Definisi  : Metadata index (JSON) buat landing page.
File      : public/index.json (auto-generated)

Reader Payload
─────────────────────────────────────────────────────────────
Definisi  : Data yang dikirim ke reader template.
Schema    : { title, author, pages, sections, book_id, properties }
Contoh    : section: { page, type, src, resource, anchor }

Book ID
─────────────────────────────────────────────────────────────
Definisi  : SHA-256 fingerprint unik per buku.
Format    : "sha256:" + 64-char hex
Kegunaan  : Annotation storage key.

Section
─────────────────────────────────────────────────────────────
Definisi  : 1 halaman di reader (image atau text).
Tipe      : "image" (src) | "text" (content)

Anchor
─────────────────────────────────────────────────────────────
Definisi  : Pointer ke lokasi konten (buat annotation).
Schema    : { scheme: "text" | "image", resource: string }

Slug
─────────────────────────────────────────────────────────────
Definisi  : Nama folder yang di-generate dari title.
Format    : lowercase, dash-separated, max 50 char
Contoh    : "Pahami GhostWriter" → "pahami-ghostwriter"

.momedia (typo: .nomedia)
─────────────────────────────────────────────────────────────
Definisi  : File kosong yang bikin Android skip folder dari Gallery.
File      : .nomedia (dot-prefixed)
Auto-gen  : Setiap render PDF/comic/chat.

Vendor Asset
─────────────────────────────────────────────────────────────
Definisi  : Library eksternal (marked, hljs, katex).
Lokasi    : public/vendor/
Download  : tools/download_vendor.py
Fallback  : CDN (kalau vendor gak ada).

Self-contained
─────────────────────────────────────────────────────────────
Definisi  : Output HTML punya semua CSS/JS inline (gak butuh asset).
Implementasi: Jinja2 {% include %} di dalam <style> & <script>

Offline-First
─────────────────────────────────────────────────────────────
Definisi  : Fitur core works tanpa network.
Implementasi: mini-markdown.js sebagai fallback.
Dilarang  : Core feature bergantung ke CDN.

Path Canonical
─────────────────────────────────────────────────────────────
Definisi  : Path absolute, resolved dari ROOT, bukan CWD.
Implementasi: core/paths.py
Tujuan    : CWD-independent, works dari manapun.

Reader Mode
─────────────────────────────────────────────────────────────
Definisi  : Cara baca konten di reader.
Nilai     : "horizontal" (page-based) | "vertical" (scroll)
Konteks   : Horizontal cover novel/comic/manga; Vertical cover webtoon.

Page Flip
─────────────────────────────────────────────────────────────
Definisi  : Animasi "buka halaman" di reader (Horizontal).
Implementasi: CSS 3D (rotateY + perspective + shadow).
Alternatif: Slide / Fade (user bisa pilih).

Annotation
─────────────────────────────────────────────────────────────
Definisi  : Bookmark, highlight, note di reader.
Storage   : IndexedDB (primary), localStorage (fallback).

Circuit Breaker
─────────────────────────────────────────────────────────────
Definisi  : Pattern untuk skip request yang udah gagal.
Konteks   : DeepSeek attachment download (HTML challenge).
Efek      : 50-150 detik → 1-3 detik (97% saving).

Incremental Backup
─────────────────────────────────────────────────────────────
Definisi  : Backup yang skip obrolan yang gak ada update.
Konteks   : DeepSeek live backup.
Implementasi: Cek `last_message_id` per obrolan.

Partial Import
─────────────────────────────────────────────────────────────
Definisi  : Import yang cuma dapet sebagian konten (share URL).
Flag      : `partial_import: true` di metadata.
Konteks   : Share URL fallback ke HTML text extraction.

HITL (Human-in-the-loop)
─────────────────────────────────────────────────────────────
Definisi  : Proses yang butuh intervensi user.
Konteks   : Live backup (paste token), import (pilih file).

================================================================================
10. CONTOH WORKFLOW
================================================================================

WORKFLOW 1 — RENDER CHAT DARI FILE
─────────────────────────────────────────────────────────────
1. Taruh file backup.json di inputs/
2. Jalankan: python3 main.py
3. Pilih menu [1] — Import Chat File
4. Pilih file, pilih convo (atau all)
5. Tunggu render selesai
6. Jalankan: python3 serve.py
7. Buka http://localhost:8000/

WORKFLOW 2 — IMPORT EBOOK PDF
─────────────────────────────────────────────────────────────
1. Taruh file book.pdf di inputs/
2. Jalankan: python3 main.py
3. Pilih menu [2] — Import Ebook
4. Pilih file, konfirmasi
5. Tunggu render (5-15 menit buat PDF gede)
6. Jalankan: python3 serve.py
7. Buka http://localhost:8000/readers/<slug>/

WORKFLOW 3 — LIVE BACKUP DEEPSEEK
─────────────────────────────────────────────────────────────
1. Login ke chat.deepseek.com
2. Buka DevTools (F12) → Application → Local Storage
3. Copy value dari key `userToken`
4. Jalankan: python3 main.py
5. Pilih menu [4] — Live Backup DeepSeek
6. Paste token
7. Pilih obrolan (range/checklist/all)
8. Tunggu backup selesai
9. Cek data/backups/ + public/history/

WORKFLOW 4 — IMPORT CHAT VIA SHARE URL
─────────────────────────────────────────────────────────────
1. Copy public share URL (ChatGPT, Claude, dll)
2. Jalankan: python3 main.py
3. Pilih menu [6] — Import Chat via Share URL
4. Paste URL
5. Tunggu fetch + extract
6. Cek public/history/<slug>/

WORKFLOW 5 — EXPORT CHAT (via viewer)
─────────────────────────────────────────────────────────────
1. Buka chat viewer: http://localhost:8000/history/<id>/
2. Klik header menu (⋮)
3. Pilih "Print / Save as PDF"
4. Atau klik tombol copy di bawah pesan
5. Atau save .md per pesan (via menu ⋯)

WORKFLOW 6 — BACKUP MANUAL (JAMAN PURBA MODE)
─────────────────────────────────────────────────────────────
1. Buka Mixplorer
2. Copy folder project ke ~/backup_YYYYMMDD/
3. Test perubahan
4. Kalau sukses → copy balik
5. Kalau gagal → restore dari backup

================================================================================
11. TROUBLESHOOTING QUICK REFERENCE
================================================================================

Error: "fetch index.json failed"
─────────────────────────────────────────────────────────────
Penyebab  : Akses via file:// bukan http://
Solusi    : Jalankan `python3 serve.py`, akses http://localhost:8000/

Error: "Port 8000 udah dipake"
─────────────────────────────────────────────────────────────
Penyebab  : Proses lain pake port 8000
Solusi    : python3 serve.py --port 8080
            atau kill: lsof -ti:8000 | xargs kill

Error: "Template gak ada: templates/reader/reader.html"
─────────────────────────────────────────────────────────────
Penyebab  : Path relatif ke CWD, bukan project root
Solusi    : Cek core/paths.py, ensure_layout(), ROOT resolve

Error: "PDF gak ke-render / error poppler"
─────────────────────────────────────────────────────────────
Penyebab  : Poppler (pdftoppm) gak keinstall
Solusi    : pkg install poppler (Termux)

Error: "Token expired"
─────────────────────────────────────────────────────────────
Penyebab  : Token DeepSeek expired
Solusi    : Ambil token baru dari DevTools, paste ulang

Error: "Partial import (share URL)"
─────────────────────────────────────────────────────────────
Penyebab  : Share page cuma nge-expose text (gak structured)
Solusi    : Ini limitasi, bukan bug. Cek flag partial_import.

Error: "Vendor asset hilang"
─────────────────────────────────────────────────────────────
Penyebab  : public/vendor/ kosong atau korup
Solusi    : python3 -m tools.download_vendor

Error: "Landing page gak ke-update"
─────────────────────────────────────────────────────────────
Penyebab  : Index stale
Solusi    : python3 sync.py

================================================================================
END OF GLOSARIUM.md — GhostWriter+ v3.3.2
================================================================================