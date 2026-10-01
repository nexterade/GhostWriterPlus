# Contributing — GhostWriter+

Terima kasih udah mau contribute! 👻

GhostWriter+ v3.3.2 pake arsitektur **template modular** + **reader JavaScript self-contained**. Panduan ini bakal ngebantu lu ngerti struktur & cara nambah fitur.

---

## 📋 Daftar Isi

1. [Setup Development](#1-setup-development)
2. [Struktur Folder](#2-struktur-folder)
3. [Menambah Fitur Template](#3-menambah-fitur-template)
4. [Schema Reader](#4-schema-reader)
5. [Import Chat](#5-import-chat)
6. [Testing](#6-testing)
7. [Code Style](#7-code-style)
8. [Pull Request](#8-pull-request)
9. [Report Bug](#9-report-bug)
10. [Feature Request](#10-feature-request)

---

## 1. Setup Development

### 1.1 Clone Repo

    git clone https://github.com/nexterade/GhostWriterPlus.git
    cd GhostWriterPlus

### 1.2 Install Dependencies

    pip install -r requirements.txt

### 1.3 Install System Dependencies

**Poppler (WAJIB buat PDF):**
    # Termux
    pkg install poppler
    
    # Ubuntu/Debian
    sudo apt install poppler-utils
    
    # macOS
    brew install poppler

**Calibre (OPTIONAL buat MOBI):**
    # Ubuntu/Debian
    sudo apt install calibre
    
    # macOS
    brew install calibre

### 1.4 Test Instalasi

    python3 -m pytest -q

Expected: **50 tests passed**.

Kalau ada test yang fail → cek [Troubleshooting](docs/TUTORIAL.md#15-troubleshooting).

### 1.5 Setup Git Workflow (Simplify Mode)

Proyek ini pake **git simplify mode** — cuma 5 command:

    git status              # cek perubahan
    git add .               # add semua
    git commit -m "..."     # commit
    git log --oneline       # liat history
    git checkout HEAD -- <file>  # undo 1 file

**DILARANG pake:**
- `git rebase` — bikin konflik
- `git merge` — gak butuh, solo project
- `git pull` / `git push` — sampai paham remote
- `git branch` — cukup main
- `git reset --hard` — hapus permanen

**Backup manual tetep jalan:** copy folder ke `_backups/` sebelum edit file besar.

---

## 2. Struktur Folder

    GhostWriterPlus/
    ├── main.py                          # CLI entry point + wizard
    ├── serve.py                         # HTTP server + auto-migration
    ├── sync.py                          # Index regenerator + prune
    ├── exporter.py                      # HTMLExporter buat chat
    ├── requirements.txt                 # Python dependencies
    ├── README.md                        # Dokumentasi publik
    ├── CONTRIBUTING.md                  # ← file ini
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
    ├── inputs/                          # Folder input (gitignored)
    │
    ├── public/                          # Output HTML (gitignored)
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
    │   │   ├── style.css                # SEMUA CSS viewer
    │   │   ├── script.js                # SEMUA JS viewer
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
    │   └── reader/                      # GhostReader+ Ebook/Comic
    │       ├── reader.html
    │       ├── style.css                # SEMUA CSS reader
    │       ├── script.js                # SEMUA JS reader
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
    │   ├── base.py                      # ABC BaseParser
    │   ├── json_parser.py               # Multi-platform JSON
    │   ├── md_parser.py                 # Markdown
    │   └── docx_parser.py               # DOCX
    │
    ├── importers/                       # Importer
    │   ├── _reader_common.py            # Shared helper
    │   ├── pdf_importer.py              # PDF → image
    │   ├── comic_importer.py            # ZIP → image
    │   ├── ebook_importer.py            # EPUB/MOBI/TXT
    │   ├── chat_importer.py             # Local chat file
    │   └── chat_url_importer.py         # Share URL
    │
    ├── tools/                           # Utility modules
    │   ├── theme.py                     # Colors, theme, LOGO_SVG
    │   ├── loading.py                   # Spinner, print helpers
    │   ├── checklist.py                 # Interactive checklist
    │   ├── prompt.py                    # Prompt helpers
    │   ├── dist_index.py                # Index generator
    │   ├── download_vendor.py           # Vendor downloader
    │   ├── nomedia.py                   # Auto .nomedia
    │   └── deepseek_backup.py           # DeepSeekLiveBackup
    │
    ├── tests/                           # Test suite (32 passed)
    │   ├── __init__.py
    │   ├── test_annotations.py
    │   ├── test_core.py
    │   ├── test_ebook_importer.py
    │   ├── test_reader_features.py
    │   ├── test_reader_focus.py
    │   ├── test_reader_modes.py
    │   └── test_viewer_nested_collapse.py
    │
    ├── data/                            # Data runtime (gitignored)
    │   ├── chats/
    │   ├── ebooks/
    │   ├── comics/
    │   ├── backups/
    │   └── tmp/
    │
    └── attachments/                     # Attachment chat manual (gitignored)
        └── PENDING.md

---

## 3. Menambah Fitur Template

### 3.1 Prinsip Utama

1. **Markup** — tambahkan ke partial/template yang relevan.
2. **CSS** — tetap inline via `{% include '.../style.css' %}`.
3. **JavaScript** — tetap inline via `{% include '.../script.js' %}`.
4. **Variabel HTML** — wajib pake `| safe` setelah sumbernya dipastikan **trusted**.
5. **Dependency CDN** — DILARANG buat fitur core reader/viewer.
6. **Touch event** — wajib pake `{ passive: false }` kalau handler panggil `preventDefault()`.
7. **Gesture** — jangan bind swipe page ketika zoom aktif; zoom punya prioritas.
8. **Test** — setelah ubah reader/viewer, jalankan syntax check Node + test Python.

### 3.2 Contoh: Nambah Tombol di Sidebar Reader

**Step 1 — Edit partial:**

Buka `templates/reader/partials/sidebar.html`, tambah tombol:

```html
<button class="sidebar-action" id="my-new-button" title="New feature">
    🆕 My Feature
</button>
```

**Step 2 — Tambah CSS:**

Buka `templates/reader/style.css`, tambah style:

```css
.sidebar-action {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface2);
    color: var(--text);
    cursor: pointer;
}
.sidebar-action:hover {
    border-color: var(--accent);
    color: var(--accent);
}
```

**Step 3 — Tambah JS handler:**

Buka `templates/reader/script.js`, tambah handler:

```javascript
document.getElementById('my-new-button')?.addEventListener('click', () => {
    // Logic here
    toast('My feature activated');
});
```

**Step 4 — Test:**

    python3 -m pytest -q
    
    # Manual test
    python3 main.py    # → import ebook
    python3 serve.py   # → buka reader

### 3.3 Contoh: Nambah Fitur di Viewer

Sama kayak reader, tapi di `templates/viewer/`.

### 3.4 Aturan CSS/JS

- **1 file CSS per viewer** (`style.css`)
- **1 file JS per viewer** (`script.js`)
- **JANGAN** split jadi banyak file kecil
- **Gunakan** CSS variables (`--accent`, `--bg`, dll)
- **Gunakan** `var(--theme)` buat dark/light support

### 3.5 Aturan Jinja2

- Template utama: `viewer/viewer.html` atau `reader/reader.html`
- Partial: `viewer/partials/*.html` atau `reader/partials/*.html`
- Include: `{% include 'viewer/partials/sidebar.html' %}`
- CSS/JS: `{% include 'viewer/style.css' %}` di dalam `<style>` atau `<script>`
- Custom comment: `{## ... ##}` (bukan `{# ... #}` — biar gak collision CSS)

### 3.6 Variabel HTML — Wajib `| safe`

**BENAR:**
```html
{{ LOGO_SVG | safe }}
{{ FAVICON_LINK | safe }}
{{ logo_svg | safe }}
{{ favicon_link | safe }}
```

**SALAH:**
```html
{{ LOGO_SVG }}      <!-- Jinja2 autoescape → jadi text -->
```

Kalau gak pake `| safe`, Jinja2 bakal escape `<svg>` jadi `&lt;svg&gt;` dan SVG gak render.

---

## 4. Schema Reader

Payload yang dikirim ke `templates/reader/reader.html`:

```text
{
    title: str,
    author: str,
    pages: int,
    book_id: str,              # "sha256:" + 64-char hex
    annotation_schema: int,    # 1
    properties: {
        format: str,           # "PDF" | "EPUB" | "MOBI" | "TXT" | "Comic ZIP"
        page_count: int,
        source_name: str,      # nama file asli
        size_bytes: int,
        dpi: int,              # (optional, buat PDF)
    },
    sections: [
        {
            page: int,
            type: "image" | "text",
            src: str,           # "images/page_001.jpg" (kalau image)
            content: str,       # konten text (kalau text)
            resource: str,      # identifier resource
            anchor: {
                scheme: "text" | "image",
                resource: str,
            },
        },
    ],
}
```

**Mode `horizontal` & `vertical` adalah state UI** — importer gak perlu bikin HTML berbeda untuk tiap mode.

---

## 5. Import Chat

Semua adapter chat WAJIB menghasilkan schema:

```text
{
    title: str,
    created_at: str,
    messages: [
        {
            role: "user" | "assistant" | "system",
            content: str,
            timestamp: str,
        },
    ],
    source_url: str,           # (optional)
    platform: str,             # (optional)
    partial_import: bool,      # (optional)
}
```

### 5.1 Nambah Format Baru

Tambahkan bentuk JSON baru di `parsers/json_parser.py`, **BUKAN di template viewer**.

Contoh: mau nambah support "Format XYZ":

```python
def _parse_xyz_format(self, data):
    """Parse format XYZ."""
    return {
        "title": data.get("conversation_name", "Untitled"),
        "created_at": data.get("timestamp", ""),
        "messages": [
            {
                "role": "assistant" if m["from"] == "bot" else "user",
                "content": m.get("text", ""),
                "timestamp": m.get("time", ""),
            }
            for m in data.get("chat", [])
        ],
    }
```

Terus panggil di `parse()`:

```python
def parse(self, convo_index=None):
    # ... existing detection
    if self._looks_like_xyz(self.raw_data):
        return self._parse_xyz_format(self.raw_data)
```

### 5.2 Nambah Platform Share URL

Tambah ke `PLATFORM_HOSTS` di `importers/chat_url_importer.py`:

```python
PLATFORM_HOSTS = {
    "chatgpt.com": "ChatGPT",
    "chat.openai.com": "ChatGPT",
    "claude.ai": "Claude",
    "gemini.google.com": "Gemini",
    "chat.deepseek.com": "DeepSeek",
    "deepseek.com": "DeepSeek",
    "perplexity.ai": "Perplexity",   # ← BARU
    "copilot.microsoft.com": "Copilot",   # ← BARU
}
```

### 5.3 Importer Reliability (v3.0.1+)

- Importer baru sebisa mungkin **return data ke schema standard** sebelum export.
- Untuk source URL, pake `importers/chat_url_importer.py` — **JANGAN simpan credential** di source.
- **JANGAN hapus output reader/chat lama** secara otomatis. Gunakan **slug unik** saat collision.
- Untuk batch besar, **proses resource secara chunked** + sediakan fallback per item.
- Tambahkan **regression test** buat parser, URL normalization, & file-output integrity.

---

## 6. Testing

### 6.1 Test Suite

Proyek ini punya **50 tests** di folder `tests/`:

    python3 -m pytest -q

Expected: **50 tests passed**.

### 6.2 Struktur Test

- `test_annotations.py` — Annotation schema & migration
- `test_core.py` — PDF, JSON parser, URL normalization, server, reader render
- `test_ebook_importer.py` — EPUB parser, TXT split, PDF forwarding
- `test_reader_features.py` — Reader UI features
- `test_reader_focus.py` — Reader template, no focus mode
- `test_reader_modes.py` — 2 modes only (Horizontal/Vertical)
- `test_viewer_nested_collapse.py` — Code block nested collapse

### 6.3 Aturan Test (STRICT!)

- **JANGAN nulis ke folder production.**
  Gunakan `TemporaryDirectory()` atau pytest `tmp_path`.
  
- **Cleanup otomatis** via `finally` block.

- **JANGAN hardcode version** di test.
  Pake regex pattern, contoh:
  ```python
  import re
  m = re.search(r'gw-reader-template-version" content="([^"]+)"', html)
  assert m
  assert m.group(1).startswith("3.")
  ```

- **Test path-independent.**
  Test yang nulis file output harus pake temporary dir atau cleanup.

### 6.4 Manual Testing

Setelah edit, test manual:

    python3 main.py    # Test wizard mode
    python3 serve.py   # Test HTTP server
    python3 sync.py    # Test index sync

### 6.5 Node Syntax Check

Buat JS file di `templates/`:

    node --check templates/reader/script.js
    node --check templates/viewer/script.js
    node --check templates/viewer/mini-markdown.js

---

## 7. Code Style

### 7.1 Python

- **PEP 8** — standard style
- **Line length:** 100 chars (soft limit)
- **Indent:** 4 spaces
- **Naming:**
  - `snake_case` buat variable/function
  - `PascalCase` buat class
  - `UPPER_CASE` buat constant
- **Import order:**
  1. Standard library
  2. Third-party
  3. Local (`core/`, `tools/`, `importers/`, `parsers/`)
- **Type hints:** pake kalau bisa (Python 3.8+)
- **Docstring:** pake triple-quote, jelasin purpose

Contoh:
```python
def render_reader_html(
    template_path: str,
    output_path: str,
    payload: dict,
    type_: str = "ebook",
) -> str:
    """Render reader template dengan native Jinja2."""
    # ...
```

### 7.2 JavaScript

- **Modern ES6+** — arrow function, const/let, destructuring
- **Semicolons:** optional (konsisten aja)
- **Indent:** 2 or 4 spaces (konsisten per file)
- **Naming:**
  - `camelCase` buat variable/function
  - `PascalCase` buat class
  - `UPPER_CASE` buat constant
- **Event handler:** pake `addEventListener`, bukan `onclick` inline
- **Passive listener:** pake `{ passive: false }` kalau ada `preventDefault()`

Contoh:
```javascript
function applyZoom(pageEl, zoomLevel) {
    const img = pageEl.querySelector("img");
    if (!img) return;
    const clamped = Math.max(1, Math.min(4, zoomLevel));
    // ...
}
```

### 7.3 CSS

- **CSS variables** buat theme colors
- **BEM-like naming** (`.block__element--modifier`)
- **Mobile-first** media queries
- **Prefix `gw-`** buat class yang spesifik GhostWriter

Contoh:
```css
.gw-loader { /* ... */ }
.gw-loader__inner { /* ... */ }
.gw-loader--hidden { /* ... */ }
```

### 7.4 HTML

- **Semantic tags** (`<aside>`, `<main>`, `<header>`, `<footer>`)
- **ARIA attributes** buat accessibility
- **`aria-label`** buat icon-only button

Contoh:
```html
<button 
    class="header-btn" 
    id="help-toggle" 
    title="Keyboard shortcuts"
    aria-label="Buka keyboard shortcuts"
>?</button>
```

---

## 8. Pull Request

### 8.1 Branch Naming

    feat/nama-fitur        # fitur baru
    fix/nama-bug           # bug fix
    refactor/nama-modul    # refactor
    docs/nama-dokumen      # dokumentasi
    chore/nama-task        # maintenance

### 8.2 Commit Message Format

    <type>(<scope>): <subject>

    <body>

    <footer>

**Type:**
- `feat` — fitur baru
- `fix` — bug fix
- `docs` — dokumentasi
- `refactor` — refactor
- `test` — test
- `chore` — maintenance

**Contoh:**
    feat(reader): add Al-Quran mode
    
    - Split per ayat
    - Audio player per ayat
    - Layout khusus (Arabic font, RTL)
    
    Closes #42

### 8.3 PR Checklist

Sebelum buka PR, pastiin:

- [ ] Test suite passing (`python3 -m pytest -q`)
- [ ] Manual test (wizard mode, render, serve)
- [ ] Code style sesuai (PEP 8, ES6+)
- [ ] Gak ada `console.log` atau `print()` debug
- [ ] Gak ada file auto-generated (`public/`, `data/`, `inputs/`, `attachments/`)
- [ ] Gak ada token/credential di code
- [ ] Documentation update (kalau fitur baru)
- [ ] `docs/CHANGELOG.md` update (kalau penting)
- [ ] Screenshot (kalau UI change)

### 8.4 PR Description Template

```markdown
## Deskripsi
[Jelasin singkat perubahan]

## Tipe
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation

## Test
- [ ] Unit test passing
- [ ] Manual test di [device/browser]

## Screenshot
[Jika ada perubahan UI]

## Related Issues
Closes #42
```

---

## 9. Report Bug

Buka Issue di GitHub dengan info:

### 9.1 Info Wajib

- **Versi GhostWriter+** (contoh: v3.2.3)
- **OS** (Termux, Linux, macOS, Windows)
- **Python version** (`python3 --version`)
- **Browser** (Quetta, Chrome, Firefox, dll)
- **Device** (HP Android, laptop, dll)

### 9.2 Langkah Reproduksi

Tulis step-by-step:
1. Buka menu X
2. Pilih Y
3. Klik Z
4. → Error muncul

### 9.3 Expected vs Actual

- **Expected:** apa yang lu harapin
- **Actual:** apa yang kejadian

### 9.4 Screenshot / Log

- Screenshot error message
- Log dari Console browser (F12)
- Log dari terminal (kalau ada)

### 9.5 Contoh Issue Bug

```markdown
## Deskripsi
Zoom double-tap gak works di reader mode Horizontal.

## Environment
- Versi: v3.2.3
- OS: Termux Android 10
- Python: 3.11
- Browser: Quetta
- Device: Xiaomi Redmi Note 8

## Langkah Reproduksi
1. Buka reader
2. Mode Horizontal
3. Double-tap gambar
4. → Gak ada zoom

## Expected
Gambar zoom 2x

## Actual
Gak ada perubahan

## Screenshot
[attach screenshot]

## Console Log
[attach log]
```

---

## 10. Feature Request

Buka Issue dengan label `enhancement`.

### 10.1 Template Feature Request

```markdown
## Deskripsi
[Jelasin fitur yang diinginkan]

## Use Case
[Kenapa fitur ini berguna? Siapa yang butuh?]

## Contoh Implementasi
[Opsional — kalau ada bayangan]

## Alternative
[Opsional — solusi lain yang mungkin]

## Priority
- [ ] Nice to have
- [ ] Important
- [ ] Critical
```

---

## 📜 License

Dengan contribute, lu setuju kontribusi di-lisensi **MIT**. Lihat [Licence.md](Licence.md).

---

## 🙏 Credits

Dibuat dengan 👻 oleh **[@nexterade](https://github.com/nexterade)**.

**Contributors:**
- [Your name here] — contribute fitur X

---

## 📚 Referensi

- [docs/CHECKPOINT.md](docs/CHECKPOINT.md) — Aturan baku proyek
- [docs/BACKLOG.md](docs/BACKLOG.md) — Product roadmap
- [docs/STATE.md](docs/STATE.md) — Snapshot status teknis
- [docs/GLOSARIUM.md](docs/GLOSARIUM.md) — Command, flag, istilah
- [docs/TUTORIAL.md](docs/TUTORIAL.md) — Panduan lengkap
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — History perubahan
- [docs/ANNOTATIONS.md](docs/ANNOTATIONS.md) — Schema annotation

---

**Terima kasih udah contribute! 👻**
```

---