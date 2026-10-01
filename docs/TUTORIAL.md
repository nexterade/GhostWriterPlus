================================================================================
TUTORIAL.md — GhostWriter+
Panduan Lengkap Penggunaan
================================================================================
Versi    : v3.3.2
Update   : 2026-09-29
Author   : @nexterade
Berlaku  : Seluruh komponen proyek GhostWriter+
📎 FILE TERKAIT:
   · docs/CHECKPOINT.md   : aturan baku & filosofi proyek
   · docs/BACKLOG.md      : product roadmap & PR tracker
   · docs/STATE.md        : snapshot status teknis
   · docs/GLOSARIUM.md    : command, flag, istilah
   · README.md            : dokumentasi publik
================================================================================

DAFTAR ISI:
  1.  Pengenalan
  2.  Instalasi
  3.  Quick Start
  4.  Import Chat (File Lokal)
  5.  Import Chat (Share URL)
  6.  Import Ebook (EPUB/MOBI/TXT/PDF)
  7.  Import Comic ZIP
  8.  Live Backup DeepSeek
  9.  Reader Mode (Horizontal / Vertical)
  10. Annotation (Bookmark, Highlight, Note)
  11. Zoom & Navigation
  12. Keyboard Shortcuts
  13. Serve Output
  14. Sync & Prune
  15. Troubleshooting
  16. Tips & Trik
  17. v3.2.5 — Viewer & Landing Tools
  18. v3.2.5 — Reader Enhancements
  19. FAQ

================================================================================
1. PENGENALAN
================================================================================

APA ITU GHOSTWRITER+?
─────────────────────────────────────────────────────────────
GhostWriter+ adalah tool CLI Python yang mengubah:
  · Arsip obrolan AI (ChatGPT, Claude, Gemini, DeepSeek)
  · Ebook (EPUB, MOBI, TXT, PDF)
  · Comic/manga/webtoon (ZIP)

Menjadi **web viewer interaktif** yang bisa dibuka di browser lokal.

Semua data disimpan **di device lu sendiri** (local-first, no-cloud).

SIAPA YANG COCOK PAKE?
─────────────────────────────────────────────────────────────
  · Developer yang mau arsip chat AI secara lokal
  · Pembaca ebook/comic yang mau viewer ringan offline
  · User Android yang mau akses arsip dari HP

APA YANG BISA DILAKUIN?
─────────────────────────────────────────────────────────────
  · Import chat dari 5+ platform (JSON/MD/DOCX/Share URL)
  · Live backup dari akun DeepSeek
  · Import ebook (text reflow + image mode)
  · Import comic ZIP (manga, webtoon, comic strip)
  · Baca dengan reader hybrid (Horizontal/Vertical)
  · Annotate (bookmark, highlight, note)
  · Search, export, print

================================================================================
2. INSTALASI
================================================================================

STEP 1 — CLONE REPO
─────────────────────────────────────────────────────────────
git clone https://github.com/nexterade/GhostWriterPlus.git
cd GhostWriterPlus

STEP 2 — INSTALL PYTHON DEPENDENCIES
─────────────────────────────────────────────────────────────
pip install -r requirements.txt

Dependencies:
  · jinja2         — Template engine
  · requests       — HTTP (DeepSeek + share URL)
  · python-docx    — Parse .docx
  · pypdf          — Baca metadata PDF
  · pdf2image      — Render PDF (fallback)
  · Pillow         — Image processing
  · mobi           — MOBI fallback (optional)

STEP 3 — INSTALL POPPLER (WAJIB)
─────────────────────────────────────────────────────────────
Poppler dibutuhkan buat render PDF.

  Termux   : pkg install poppler
  Ubuntu   : sudo apt install poppler-utils
  macOS    : brew install poppler
  Windows  : download dari github.com/oschwartz10612/poppler-windows

Cek instalasi:
  pdftoppm -v

STEP 4 — (OPTIONAL) INSTALL CALIBRE
─────────────────────────────────────────────────────────────
Calibre dibutuhkan buat convert MOBI → EPUB.

  Ubuntu   : sudo apt install calibre
  macOS    : brew install calibre
  Termux   : gak ada package resmi (fallback ke paket Python `mobi`)

STEP 5 — VERIFIKASI
─────────────────────────────────────────────────────────────
Jalankan:
  python3 main.py

Kalau muncul banner GhostWriter+ dan menu 6 opsi → instalasi sukses.

Jalankan test suite:
  python3 -m pytest -q

Expected: 50 tests passed.

================================================================================
3. QUICK START
================================================================================

3 LANGKAH — KURANG DARI 30 DETIK
─────────────────────────────────────────────────────────────
1. Taruh file di folder inputs/
   (chat JSON/MD/DOCX, ebook PDF/EPUB, comic ZIP)

2. Jalankan wizard:
   python3 main.py

3. Pilih menu sesuai tipe file:
   [1] Chat File   [2] Ebook   [3] Comic
   [4] Live Backup [5] Tutorial [6] Share URL

4. Buka di browser:
   python3 serve.py

Browser bakal kebuka otomatis ke http://localhost:8000/

LANGKAH DETAIL — RENDER CHAT PERTAMA
─────────────────────────────────────────────────────────────
1. Taruh file `backup.json` di `inputs/`

2. Jalankan:
   python3 main.py

3. Pilih menu [1]

4. Pilih file dari list (atau input path manual)

5. Pilih convo (kalau file bulk)

6. Tunggu render selesai

7. Buka:
   python3 serve.py

8. Browser → http://localhost:8000/

9. Klik item di landing page → masuk ke viewer

================================================================================
4. IMPORT CHAT (FILE LOKAL)
================================================================================

FORMAT YANG DIDUKUNG
─────────────────────────────────────────────────────────────
  · JSON — ChatGPT/OpenAI, Claude, Gemini, DeepSeek, Generic
  · Markdown — heading `## User`, `### Assistant`
  · DOCX — paragraf dengan heading role

PLATFORM YANG DI-DETEKSI
─────────────────────────────────────────────────────────────
  · ChatGPT / OpenAI
  · Claude / Anthropic
  · Gemini / Bard / Google
  · DeepSeek
  · Generic JSON

CARA PAKAI
─────────────────────────────────────────────────────────────
1. Taruh file di `inputs/`
   Contoh: `chatgpt-export.json`

2. Jalankan:
   python3 main.py

3. Pilih menu [1] — Import Chat File

4. Pilih file dari list (atau input path manual)

5. Sistem bakal detect platform otomatis

6. Pilih convo:
   · `1` — convo #1
   · `1,3,5` — convo #1, #3, #5
   · `1-5` — convo #1 sampe #5
   · `all` — semua convo (rekomendasi)

7. Tunggu render selesai

8. Cek hasil:
   public/history/<slug>/index.html

CLI MODE (LANGSUNG)
─────────────────────────────────────────────────────────────
Buat render 1 convo:
  python3 main.py backup.json --chat-index 0

Buat render semua:
  python3 main.py backup.json --all

================================================================================
5. IMPORT CHAT (SHARE URL)
================================================================================

APA ITU?
─────────────────────────────────────────────────────────────
Import chat dari **public share URL** — bukan dari file.
Cocok buat chat yang lu dapet dari share link.

PLATFORM YANG DIDUKUNG
─────────────────────────────────────────────────────────────
  · ChatGPT / OpenAI (chatgpt.com/share/...)
  · Claude (claude.ai/share/...)
  · Gemini (gemini.google.com/share/...)
  · DeepSeek (chat.deepseek.com/share/...)
  · Generic public share page

CARA PAKAI
─────────────────────────────────────────────────────────────
1. Copy public share URL
   Contoh: https://chatgpt.com/share/abc123

2. Jalankan:
   python3 main.py

3. Pilih menu [6] — Import Chat via Share URL

4. Paste URL

5. Tunggu fetch + extract

6. Cek hasil:
   public/history/<slug>/index.html

CATATAN PENTING
─────────────────────────────────────────────────────────────
· **Cuma works buat PUBLIC share link.**
  Kalau URL butuh login → gak bisa diimpor.

· **Partial import flag:**
  Kalau share page cuma nge-expose text (gak structured JSON),
  sistem bakal flag `partial_import: true`.
  Ini limitasi platform, bukan bug.

· **Anti-bot challenge:**
  Kalau platform pake Cloudflare/anti-bot, sistem bakal
  balikin error (bukan partial).

· **Structured data diprioritasin:**
  Sistem coba: Next.js Flight → React State → Semantic HTML
  → Text fallback.

================================================================================
6. IMPORT EBOOK (EPUB/MOBI/TXT/PDF)
================================================================================

FORMAT YANG DIDUKUNG
─────────────────────────────────────────────────────────────
  · EPUB — native parser (ZIP + XML/XHTML)
  · MOBI — via Calibre `ebook-convert` atau paket `mobi`
  · TXT  — pagination otomatis (3000 char/page)
  · PDF  — render via Poppler (JPEG 150 DPI)

CARA PAKAI
─────────────────────────────────────────────────────────────
1. Taruh file di `inputs/`
   Contoh: `buku.epub`, `novel.pdf`, `catatan.txt`

2. Jalankan:
   python3 main.py

3. Pilih menu [2] — Import Ebook

4. Pilih file (auto-detect format)

5. Konfirmasi

6. Tunggu import selesai

7. Cek hasil:
   public/readers/<slug>/index.html

CATATAN PER FORMAT
─────────────────────────────────────────────────────────────
EPUB:
  · Native parser — gak butuh dependency eksternal
  · Spine order (urutan sesuai manifest)
  · Text extraction via HTMLParser (stdlib)
  · Support: chapter, paragraf, heading, list

MOBI:
  · Butuh Calibre `ebook-convert` ATAU paket Python `mobi`
  · Kalau Calibre ada → convert ke EPUB → parse
  · Kalau gak ada → fallback ke paket `mobi`
  · Kalau dua-duanya gak ada → error

TXT:
  · Auto-pagination (3000 char/page)
  · Encoding detection: utf-8, utf-16, cp1252, latin-1
  · Cut di akhir kalimat (kalau bisa)

PDF:
  · Image mode (bukan text extraction)
  · Render via Poppler `pdftoppm`
  · DPI 150 (balance kualitas & ukuran)
  · Batch 8 halaman + fallback per halaman
  · Atomic move (staging → final)
  · Partial render → gak dipublish

TITLE FALLBACK
─────────────────────────────────────────────────────────────
Kalau metadata PDF/EPUB "Untitled" atau generic:
  → Sistem fallback ke nama file

Contoh: `buku.pdf` dengan metadata "Untitled"
  → Title: "buku"
  → Slug: "buku"

================================================================================
7. IMPORT COMIC ZIP
================================================================================

CARA PAKAI
─────────────────────────────────────────────────────────────
1. Taruh file .zip di `inputs/`
   Contoh: `manga-chapter-1.zip`

2. Jalankan:
   python3 main.py

3. Pilih menu [3] — Import Comic ZIP

4. Pilih ZIP

5. Konfirmasi

6. Tunggu extract selesai

7. Cek hasil:
   public/comics/<slug>/index.html

FITUR
─────────────────────────────────────────────────────────────
· **Multi-format image:** jpg, jpeg, png, webp, gif, bmp, avif
· **Natural sort:** 1, 2, 10 (bukan 1, 10, 2)
· **Skip junk:**
  · __MACOSX/
  · ._*
  · .DS_Store
  · Thumbs.db
  · desktop.ini
· **Flatten nested folder:** semua gambar jadi 1 urutan
· **Keep format asli:** gak re-encode (preserve animasi GIF)
· **Sortir otomatis:** urutan halaman bener

CARA BIKIN ZIP
─────────────────────────────────────────────────────────────
1. Kumpulin gambar di folder
   Contoh: manga-ch-1/
             ├── page_01.jpg
             ├── page_02.jpg
             └── ...

2. Compress jadi ZIP (via Mixplorer / Zarchive)

3. Nama file = judul comic
   Contoh: `Solo Leveling Ch 1.zip`

================================================================================
8. LIVE BACKUP DEEPSEEK
================================================================================

APA ITU?
─────────────────────────────────────────────────────────────
Tarik obrolan dari akun DeepSeek lu langsung via API.
Butuh token dari DevTools.

CARA PAKAI
─────────────────────────────────────────────────────────────
1. Login ke https://chat.deepseek.com

2. Buka DevTools (F12)
   · Desktop: F12
   · Quetta (Android): setara DevTools

3. Tab **Application** → **Local Storage** → **chat.deepseek.com**

4. Cari key **`userToken`**
   Copy value-nya (panjang, base64-like)

5. Jalankan:
   python3 main.py

6. Pilih menu [4] — Live Backup DeepSeek

7. Paste token

8. Tunggu verifikasi

9. Sistem fetch daftar obrolan

10. Pilih obrolan:
    · `1` — obrolan #1
    · `1,3,5` — #1, #3, #5
    · `1-5` — #1 sampe #5
    · `all` — semua (rekomendasi)
    · `c` — checklist interaktif

11. Tunggu backup selesai

12. Backup otomatis di-render ke HTML

MODE BACKUP
─────────────────────────────────────────────────────────────
· **Incremental (default):**
  Skip obrolan yang gak ada update.
  Cek `last_message_id` per obrolan.

· **Full:**
  Backup ulang semua obrolan (lebih lambat).

ANTI-SUSPEND
─────────────────────────────────────────────────────────────
DeepSeek bisa flag akun kalau request pattern aneh.
GhostWriter+ pake:
  · Human-like delay + jitter (1-3s)
  · Session delay (3-7s antar obrolan)
  · Retry delay (5-10s kalau gagal)
  · Incremental (skip yang gak update)

Configurasi via ENV var:
  GW_DELAY_MIN=2 GW_DELAY_MAX=4 python3 main.py

ATTACHMENT PENDING
─────────────────────────────────────────────────────────────
Kalau obrolan punya attachment (gambar, file), DeepSeek
sering blokir download otomatis.

Solusi:
1. Buka `attachments/PENDING.md`
2. Ikutin langkahnya (~5 menit)
3. Taruh file di `attachments/`
4. Re-render

OUTPUT
─────────────────────────────────────────────────────────────
· Backup JSON: `data/backups/backup_<slug>_<timestamp>.json`
· Reader HTML: `public/history/<id>/index.html`
· Pending manifest: `attachments/PENDING.md`

================================================================================
9. READER MODE (HORIZONTAL / VERTICAL)
================================================================================

2 MODE
─────────────────────────────────────────────────────────────
· **Horizontal** — Page-based, page flip animation
  Cocok buat: Novel, Comic, Manga, Al-Quran, buku scan

· **Vertical** — Continuous scroll, gap minimal
  Cocok buat: Webtoon, Manhwa, comic scroll

CARA GANTI MODE
─────────────────────────────────────────────────────────────
1. Buka reader
   Contoh: http://localhost:8000/readers/<slug>/

2. Klik menu ⋮ di header

3. Pilih "Mode baca"

4. Pilih Horizontal atau Vertical

5. Mode disimpan di localStorage (persist antar session)

PAGE FLIP (HORIZONTAL)
─────────────────────────────────────────────────────────────
Animasi "buka halaman" pake CSS 3D:
  · RotateY + perspective + shadow
  · 680ms transition (smooth)
  · Binding edge (kiri untuk LTR, kanan untuk RTL)

Ganti animasi:
  Settings → Animasi halaman:
    · Page Flip (default)
    · Slide
    · Fade

WEBTOON (VERTICAL)
─────────────────────────────────────────────────────────────
· Continuous scroll
· Gap minimal antar halaman
· Full-width image
· Gak ada page flip
· Gak ada zoom custom (udah full-width)

AUTO 2-PAGE (HORIZONTAL)
─────────────────────────────────────────────────────────────
Kalau landscape + width > 768px:
  → Auto 2-page spread

Binding mengikuti direction:
  · LTR → binding kiri
  · RTL → binding kanan

DIRECTION (LTR/RTL)
─────────────────────────────────────────────────────────────
· **LTR** (Left-to-Right):
  Cocok buat comic barat, novel, ebook text

· **RTL** (Right-to-Left):
  Cocok buat manga Jepang

Ganti direction:
  Settings → Arah halaman → LTR / RTL

================================================================================
10. ANNOTATION (BOOKMARK, HIGHLIGHT, NOTE)
================================================================================

BOOKMARK
─────────────────────────────────────────────────────────────
Cara:
1. Buka halaman yang mau di-bookmark
2. Klik menu ⋮
3. Pilih "Bookmark halaman"

Atau klik tombol ☆ di header (kalau ada).

Bookmark disimpan di **IndexedDB** (persist antar session).

HIGHLIGHT (EPUB/TXT ONLY)
─────────────────────────────────────────────────────────────
Cara:
1. Buka halaman EPUB/TXT
2. **Seleksi teks** yang mau di-highlight
3. Muncul toolbar → klik "✦ Highlight"

Atau: klik "Highlight teks terpilih" di Notes panel.

Highlight disimpan dengan:
  · `quote` — teks yang di-highlight
  · `prefix` — 48 char sebelum quote
  · `suffix` — 48 char setelah quote

Ini buat recovery kalau pagination berubah.

NOTE
─────────────────────────────────────────────────────────────
Cara:
1. Buka halaman yang mau di-note
2. Klik menu ⋮ → "Notes & Highlight"
3. Tulis catatan di textarea
4. Klik "Simpan catatan"

Note disimpan per halaman.

MIGRASI DARI LAMA
─────────────────────────────────────────────────────────────
Kalau lu punya bookmark/note dari versi lama (localStorage):
  → Otomatis migrasi ke IndexedDB saat buka reader

Data lama gak ilang.

EXPORT ANNOTATION
─────────────────────────────────────────────────────────────
Export annotation tersedia dari menu Tools → Export annotations JSON/MD.

================================================================================
11. ZOOM & NAVIGATION
================================================================================

ZOOM (HORIZONTAL MODE)
─────────────────────────────────────────────────────────────
· **Double-tap** → Zoom 2x
· **Double-tap lagi** → Reset 1x
· **Pinch** → Zoom 1x–4x (smooth)
· **Pan** — Drag saat zoomed
· **Reset** — Pinch out (zoom < 1.2)

Saat zoom aktif:
  · Swipe page di-disable (biar gak konflik)
  · Pan aktif (drag buat geser)

Zoom gak aktif di:
  · Vertical mode (udah full-width)
  · Page flip animation running
  · Sidebar/right rail kebuka

NAVIGATION
─────────────────────────────────────────────────────────────
Horizontal mode:
  · Tap kiri (30% kiri) → halaman sebelumnya
  · Tap kanan (30% kanan) → halaman berikutnya
  · Tidak ada tap-to-hide chrome
  · Swipe kiri/kanan → page turn
  · Keyboard ←/→ atau j/k → page turn
  · Home → awal, End → akhir

Vertical mode:
  · Scroll bebas
  · Page slider di bawah
  · Tap page → scroll ke halaman

PAGE DRAWER
─────────────────────────────────────────────────────────────
Klik menu ⋮ → "Pages" → buka drawer halaman.

Isi:
  · Thumbnail (comic/manga/webtoon)
  · Page number (novel)
  · Jump to page input

Progress bar di bawah (bottom chrome):
  · Drag → lompat ke halaman

================================================================================
12. KEYBOARD SHORTCUTS
================================================================================

CHAT VIEWER
─────────────────────────────────────────────────────────────
  ?         Buka panel keyboard shortcuts
  /         Fokus ke search box
  j / k     Navigate pesan berikutnya / sebelumnya
  Home      Scroll ke paling atas
  End       Scroll ke paling bawah
  Esc       Tutup sidebar / right rail / modal

READER (EBOOK / COMIC)
─────────────────────────────────────────────────────────────
  Esc       Tutup panel / menu
  ← / k     Halaman sebelumnya
  → / j     Halaman berikutnya
  Home      Ke awal
  End       Ke akhir

LANDING PAGE
─────────────────────────────────────────────────────────────
  /         Fokus ke search box

MOBILE GESTURE
─────────────────────────────────────────────────────────────
Chat viewer:
  · Swipe kiri dari tepi → buka sidebar
  · Swipe kanan dari tepi → tutup sidebar
  · Swipe kiri/kanan dari tengah → buka right rail

Reader:
  · Tap kiri/kanan → page turn
  · Tidak ada tap-to-hide chrome
  · Pinch → zoom
  · Double-tap → zoom toggle

================================================================================
13. SERVE OUTPUT
================================================================================

KENAPA BUTUH SERVER?
─────────────────────────────────────────────────────────────
Viewer fetch `index.json` via HTTP. Kalau lu buka HTML
langsung via `file://`, bakal error (CORS).

Jadi WAJIB pake HTTP server.

CARA PAKAI
─────────────────────────────────────────────────────────────
python3 serve.py

Browser kebuka otomatis ke http://localhost:8000/

OPSI
─────────────────────────────────────────────────────────────
Ganti port:
  python3 serve.py --port 8080

Jangan auto-open browser:
  python3 serve.py --no-open

AUTO-MIGRATION
─────────────────────────────────────────────────────────────
Setiap kali serve.py jalan, dia cek reader lama.

Kalau ada reader versi lama (sebelum v3.0.9):
  → Auto-repair ke template terbaru
  → Keep embedded data

Output: "Memperbarui N reader lama ke template 3.2.3"

================================================================================
14. SYNC & PRUNE
================================================================================

SYNC MANUAL
─────────────────────────────────────────────────────────────
Kalau nambah/hapus folder manual di `public/`:
  python3 sync.py

Auto-sync udah jalan otomatis setiap render selesai.

PRUNE STALE
─────────────────────────────────────────────────────────────
Hapus folder di `public/history/` yang gak ada di backup source:
  python3 sync.py --clean

Preview (dry-run):
  python3 sync.py --clean --dry-run

Skip konfirmasi:
  python3 sync.py --clean --yes

Manual keep:
  python3 sync.py --clean --keep ID1,ID2

================================================================================
15. TROUBLESHOOTING
================================================================================

ERROR UMUM
─────────────────────────────────────────────────────────────
Q: "fetch index.json failed"
A: Pastikan akses via http://localhost:8000/, bukan file://

Q: Port 8000 udah dipake
A: Ganti port: python3 serve.py --port 8080
   Atau kill: lsof -ti:8000 | xargs kill

Q: Token expired terus
A: GhostWriter auto-invalidate token cache.
   Login ulang pake token baru dari DevTools.

PDF / COMIC
─────────────────────────────────────────────────────────────
Q: PDF gak ke-render / error poppler
A: Install Poppler:
   · Termux  : pkg install poppler
   · Ubuntu  : sudo apt install poppler-utils
   · macOS   : brew install poppler

Q: Import PDF lambat
A: Normal — 100 halaman bisa 5-15 menit.
   Tergantung device & DPI.

Q: Gambar di comic gak ke-render
A: Cek Console browser (F12) — biasanya path salah.
   Atau format gak didukung (.avif butuh browser modern).

FITUR GAK JALAN
─────────────────────────────────────────────────────────────
Q: Convo gak muncul di landing page
A: Jalanin sync: python3 sync.py

Q: Lampiran gak ke-render
A: Buka attachments/PENDING.md — ikutin langkahnya.
   DeepSeek blokir download otomatis buat file.

Q: Viewer blank / putih doang
A: Cek Console (F12) — biasanya CORS atau JS error.
   Pastikan akses via http://localhost:8000/

Q: Share URL import gagal
A: · Pastikan URL public (bukan login-only)
   · Kalau partial → limitasi platform, bukan bug
   · Cek anti-bot challenge (Cloudflare)

READER
─────────────────────────────────────────────────────────────
Q: Page flip gak works
A: Cek mode: harus Horizontal (bukan Vertical).
   Settings → Animasi halaman → Page Flip

Q: Zoom gak works
A: Zoom cuma aktif di Horizontal mode.
   Double-tap atau pinch di halaman.

Q: Annotation gak muncul
A: Cek Console — mungkin IndexedDB error.
   Coba reload page.

Q: Reading stats gak update
A: Cek localStorage — mungkin ke-clear.
   Reload page.

================================================================================
16. TIPS & TRIK
================================================================================

RENDER CEPAT
─────────────────────────────────────────────────────────────
Render 1 obrolan doang:
  python3 main.py backup.json --chat-index 0

Render semua:
  python3 main.py backup.json --all

SERVER
─────────────────────────────────────────────────────────────
Ganti port:
  python3 serve.py --port 8080

Sync tanpa render ulang:
  python3 sync.py

DEBUG
─────────────────────────────────────────────────────────────
Debug mode (full traceback):
  GW_DEBUG=1 python3 main.py

Ganti delay backup:
  GW_DELAY_MIN=2 GW_DELAY_MAX=4 python3 main.py

PRUNE
─────────────────────────────────────────────────────────────
Preview prune:
  python3 sync.py --clean --dry-run

Prune tanpa konfirmasi:
  python3 sync.py --clean --yes

TESTING
─────────────────────────────────────────────────────────────
Run test suite:
  python3 -m pytest -q

VENDOR
─────────────────────────────────────────────────────────────
Download vendor assets:
  python3 -m tools.download_vendor

================================================================================
17. v3.2.5 — VIEWER & LANDING TOOLS
================================================================================

Viewer menu (⋮) sekarang menyediakan:
  · Export as Markdown — seluruh pesan dengan role/timestamp.
  · Export as JSON — title, created_at, dan messages.
  · Filter role — Semua / User / AI, disimpan di localStorage.
  · Sembunyikan/Tampilkan semua — toggle seluruh bubble collapsible.
  · Search regex — gunakan format /pattern/flags; regex invalid otomatis kembali ke plain text.

Landing page menyediakan:
  · j / k untuk pindah item, Enter untuk membuka, Esc untuk menghapus highlight, / untuk search.
  · Recent max 5 via gw-recent.
  · ⭐ Favorit via gw-favorites.
  · Grid/List via gw-view.
  · Dark/light otomatis mengikuti prefers-color-scheme jika belum ada override manual.

================================================================================
18. v3.2.5 — READER ENHANCEMENTS
================================================================================

  · TTS: menu → Baca halaman (TTS). Locale tersedia id-ID dan en-US; klik lagi saat berbicara untuk stop.
  · Annotation export: JSON atau Markdown dari bookmark, highlight, dan note buku aktif.
  · Statistik global: agregasi localStorage untuk seluruh buku pada origin/browser yang sama.
  · Arabic Text Mode generik: jika metadata/nama konten mengandung indikasi Arabic/Quran, reader memakai RTL dan font Arab. Tidak ada mapping surah/ayat atau audio Al-Quran yang diasumsikan.


================================================================================
17. FAQ
================================================================================

Q: Apakah GhostWriter+ perlu internet?
─────────────────────────────────────────────────────────────
A: Cuma buat:
   · Live Backup DeepSeek (fetch API)
   · Share URL import (fetch page)
   · Download vendor assets (kalau missing)
   Fitur lain works offline.

Q: Apakah data disimpan di cloud?
─────────────────────────────────────────────────────────────
A: GAK. Semua data disimpan di device lu:
   · public/ — output HTML
   · data/ — backup, chat, ebook data
   · attachments/ — attachment manual
   Gak ada server backend.

Q: Bisa jalan di Android/Termux?
─────────────────────────────────────────────────────────────
A: BISA. Primary tested di Termux Python 3.11.
   Butuh: Python 3.8+, Poppler.

Q: Bisa buka di HP?
─────────────────────────────────────────────────────────────
A: BISA. Reader & viewer responsive.
   Akses via http://localhost:8000/ di browser HP.
   Atau IP lokal (kalau HP & server beda device).

Q: Bisa export chat?
─────────────────────────────────────────────────────────────
A: Ya:
   · Save .md per pesan (via menu ⋯)
   · Print / Save as PDF (via header menu)
   · Export full chat → coming soon (PR IV-A/B)

Q: Bisa import dari ChatGPT?
─────────────────────────────────────────────────────────────
A: BISA. 3 cara:
   · Export JSON dari ChatGPT → taruh di inputs/
   · Paste share URL → menu [6]
   · Markdown / DOCX juga didukung

Q: Bisa import dari Claude / Gemini?
─────────────────────────────────────────────────────────────
A: BISA. Auto-detect format JSON.
   Atau paste share URL.

Q: Kenapa nama "GhostWriter+"?
─────────────────────────────────────────────────────────────
A: "Ghost" — karena tool ini bikin arsip chat AI
   yang "gak keliatan" tapi berguna.
   Plus (+) — karena versi ini punya fitur lebih banyak.

Q: Kenapa branding reader = "GhostReader+"?
─────────────────────────────────────────────────────────────
A: Pemisahan branding:
   · CLI = GhostWriter+ (tool)
   · Viewer/Reader = GhostReader+ (UI)
   Biar user awam gak bingung.

Q: Apakah gratis?
─────────────────────────────────────────────────────────────
A: Ya. MIT License. Open source. Bebas pake.

Q: Bisa contribute?
─────────────────────────────────────────────────────────────
A: Bisa. Lihat CONTRIBUTING.md.
   Buat PR, report bug, atau saran fitur.

Q: Ada screenshot?
─────────────────────────────────────────────────────────────
A: Screenshot bakal ada di wiki / release notes.
   Untuk sekarang, langsung coba aja.

================================================================================
END OF TUTORIAL.md — GhostWriter+ v3.3.2
================================================================================