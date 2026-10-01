## [3.3.4] — Viewer Header Controls Hotfix

### Fixed
- Fix **left sidebar toggle** yang tidak dapat dibuka pada layout desktop maupun mobile.
- Fix tombol **Help (?)** yang dapat menjadi inert ketika initialization viewer tertunda.
- Fix tombol **More (⋮)** dan dropdown-nya agar selalu memiliki handler sejak awal DOM initialization.
- Centralize binding untuk tiga kontrol header kritis agar tidak terjadi double-binding/open-then-close akibat listener duplikat.
- Header diberi stacking context yang lebih tinggi supaya tombol dan dropdown tidak tertutup content/overlay.

### Changed
- Sidebar toggle sekarang tersedia pada semua breakpoint; desktop tidak lagi kehilangan akses untuk membuka sidebar yang sedang collapsed.
- Viewer template dinaikkan ke `v3.3.4` agar generated viewer lama dengan marker `v3.3.3` otomatis diregenerasi.

### Assumptions
- Behavior menu existing dipertahankan; perubahan hanya memperbaiki lifecycle binding dan layering UI.

# v3.3.2 — Cross-cutting Polish (2026-09-30)


## [3.3.2] — Reader tools menu redesign

- Redesigned reader tools dropdown into category-based expandable sections.
- Grouped **Navigasi & Anotasi**, **Tampilan & Statistik**, and **Ekspor** into nested menu sections.
- Removed duplicate TTS actions from the dropdown; TTS remains available exclusively in the dedicated reader control bar.
- Preserved existing menu action handlers and behavior for bookmark, pages, notes, reading mode/settings, statistics, properties, and annotation exports.

## [3.3.2]

### Fixed
- Reader empty-state overlay no longer renders over valid page content; the `[hidden]` state is now enforced by the stylesheet.
- Server-side reader migration now refreshes generated reader HTML when the release marker matches but the generated markup is stale and lacks the current Batch 2 settings contract.

### Verified
- Reading settings follow the Batch 2 blueprint: page animation, fit, brightness, direction, and TTS voice; legacy Focus Mode/auto-hide controls are not part of the settings popover.

- Theme tokens, typography, spacing, focus states, ARIA labels, keyboard navigation, reduced-motion handling, and mobile touch targets reviewed across reader/viewer/landing/CLI.
- Added `.gitignore` coverage for generated/runtime folders and credentials.
- Removed stale absolute-path contents from `.nomedia` markers.
- Assumption: existing behavior remains authoritative; changes are additive UI polish unless required to repair stale markup/version markers.

## [3.3.1]
- CLI menu receives compact iconography, terminal-height-aware checklist rendering, and palette aliases for consistent Midnight styling.
- Spinner cadence normalized without changing workflow semantics.

## [3.3.0]
- Landing page generator polished with sticky search/sort controls, persistent grid/list mode, favorites/recent sections, and keyboard focus states.
- Regenerated `public/index.html` and `public/index.json` from the canonical generator.

## [3.2.9]
- Viewer layout split into modular header, chat container, floating navigation, and search partials.
- Preserved nested message/code collapse and per-code-block copy/fullscreen/menu controls.
- Added compact focus states and mobile touch targets.

## [3.2.8]
- Reader content partials added for book stage, empty state, and floating top/bottom navigation.
- Added smooth hover/focus reveal for reader quick navigation.

## [3.2.7]
- Reader popovers/modals/toast/loader split into dedicated partials and standardized to compact dimensions, radius, and shadows.
- Added ARIA dialog/status semantics.

## [3.2.6]
- Reader core split into header, footer, left statistics sidebar, right page rail, and content partials.
- Added permanent TTS control bar, clock, footer reading statistics, and accessible page navigation.
- Preserved Horizontal/Vertical reader modes, page flip, brightness, annotations, properties, and reading statistics.

# v3.2.5 — Reader/Viewer Audit Fixes (2026-09-30)

- Fixed horizontal Page Flip for text pages: EPUB/TXT pages now render as DOM content on both curl faces instead of showing blank faces.
- Added automatic landscape 2-page spread for horizontal reader at viewport width ≥769px; RTL reverses page order and spread navigation advances by two pages.
- Page Flip automatically uses the existing slide transition while 2-page spread is active, matching the documented landscape behavior.
- Defined reader `--viewer-accent` and `--viewer-accent-glow` theme tokens.
- Fixed EPUB manifest hrefs containing URL-encoded resource names such as `%20`.
- Removed stale tap-to-hide instructions from current reader documentation; historical changelog entries remain historical.
- Cleaned release `.nomedia` markers so they contain no machine-specific absolute paths.
- Added regression tests for encoded EPUB resources, text Page Flip faces, landscape spread, and reader theme tokens.

# Changelog — GhostWriter+

Semua perubahan penting di proyek GhostWriter+ didokumentasikan di file ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning mengikuti [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Format versi: `vMAJOR.MINOR.PATCH-GW+`

---

## [Unreleased]

### Planned (v3.3.0+)
- **PR VIII** — Future: PWA, OCR, sync annotations, multi-user, cloud sync

## [3.2.4] - 2026-09-29

### Hotfix
- Viewer loader diperbaiki agar `yieldToBrowser()` memiliki timer fallback ketika `requestAnimationFrame` ditahan/throttled oleh browser mobile atau background tab, sehingga loading overlay tidak berhenti di 95% pada tahap "Menyiapkan viewer...".

### Fixed
- **Reader mobile chrome:** header, content, dan bottom page slider kini berada dalam normal flex flow; `.reader-main` mengisi ruang di antara header dan slider.
- **Android browser UI:** reader memakai `100svh` agar slider tetap berada di dalam small viewport saat address bar bawah terlihat.
- **Build hygiene:** patch `VisualViewport` dan absolute-position slider yang tidak diperlukan dihapus.
- **Release artifact:** nama build dinormalisasi menjadi `GhostWriterPlus-v3.2.4.zip`.
- PR I-A: `_export_data()` menerima `output_dir`; test chat export sekarang memakai `TemporaryDirectory()`.
- PR I-B/C: landing chat menyimpan `size_kb`, mempertahankan display title, dan memakai `dedup_key` terpisah.
- PR I-D: version marker current diseragamkan ke v3.2.4 pada server/reader/viewer/docs.
- PR III: `_ANSI_RE` dideduplikasi; test reader tidak lagi mengunci versi patch tertentu; `reader-brand-name` ditambahkan.

### Added
- PR IV: full-chat Markdown/JSON export, regex search dengan fallback plain text, role filter, dan collapse/expand semua bubble.
- PR V: keyboard navigation landing, recent activity, favorites, Grid/List, dan system theme auto.
- PR VI: generic Arabic Text Mode (RTL + Arabic font), TTS reader, annotation JSON/MD export, dan global reading stats.
- PR VII: share URL host Perplexity, Copilot, Grok, Poe, dan You.com.

### Documentation
- README, BACKLOG, STATE, dan TUTORIAL disinkronkan ke v3.2.4.
- `docs/CHECKPOINT.md` diselaraskan ke v3.2.4; aturan layout mobile reader ditambahkan sebagai aturan framework.
- Tidak ada asumsi mapping surah/ayat; VI-A memakai fallback generic Arabic Text Mode.

### Validation
- Full test suite: **40 passed**.

### Planned (v3.3.0+)
- **PR VIII** — Future: PWA, OCR, sync annotations, multi-user, cloud sync

---

## [3.2.3] - 2026-09-29

### Fixed
- Code-block UI gak bergantung ke highlight.js — setiap fenced code block punya header/actions sendiri.
- Per-code-block **Copy** button.
- Inner code collapse CSS — selector sebelumnya target child `<pre>` padahal class `.collapsed` ada di `<pre>` itu sendiri.
- Inner collapse aktif buat code block >10 baris (terpisah dari outer message collapse).
- Tambah `aria-expanded` state ke inner collapse controls.
- Tambah explicit nested-collapse state di setiap code block wrapper.

### Validation
- Full test suite: **32 passed**.

---

## [3.2.1] - 2026-09-29

### Fixed
- Viewer gak lagi depend ke CDN buat core Markdown rendering.
- Tambah **offline-first local rich-text renderer** (`mini-markdown.js`) untuk:
  - Markdown, code fences, links, tables, lists, headings, blockquotes
  - Generated HTML attachment cards
- Generated attachment HTML di-preserve (bukan di-escape jadi raw markup).
- Tambah conservative HTML sanitization buat generated rich content.
- Share URL importer coba semantic HTML message extraction kalau structured JSON/React state gak tersedia.
- Share URL extraction sekarang report semantic-html/text-fallback provenance.
- Menu [1] sekarang **local chat-file import only**; public/share URL import **eksklusif di menu [6]** — ngilangin duplikasi source prompt.

### Validation
- Python test suite: **28 passed** (naik dari sebelumnya).
- Python syntax checks passed.
- Viewer mini-markdown JavaScript syntax check passed.

---

## [3.2.0] - 2026-09-29

### Changed
- **Reader chrome parity** dengan Chat Viewer:
  - Reader header pake structural language yang sama: left sidebar toggle, status dot, title/subtitle group, theme control, top-right dropdown tools.
  - Hapus floating reader header treatment.
  - Bookmark, Pages, Notes/Highlight diakses via top-right **Tools dropdown**.

### Added
- **Viewer-style left sidebar** buat active book, reading statistics, & library.
- **Viewer-style right rail** buat page thumbnails & page jumping.
- Sidebars collapse/expand independen + close dengan shared scrim / Escape behavior.

### Changed (lanjutan)
- Bottom chrome dikurangi jadi **reading-progress slider** only.
- Hapus bottom Bookmark / Pages / Notes action buttons.

### Preserved
- Horizontal / Vertical modes only.
- Page Flip / Slide / Fade.
- Brightness, fit, direction, bookmarks, highlights, notes, reading statistics, book properties.

### Validation
- **28 tests passing**.
- Reader script passes Node syntax validation.

---

## [3.1.8] - 2026-09-29

### Fixed
- `NameError: name 'Path' is not defined` di Live Backup DeepSeek — import `pathlib.Path` di backup module.
- Orphaned CLI loading spinners saat initialization, parsing, rendering, atau network verification raise sebelum normal `spinner.stop()`.
- Defensive spinner cleanup di:
  - Live Backup token verification
  - Ebook/PDF/comic import paths
  - HTML generation paths
- Balik ke main menu setelah handled exception gak ninggalin stale `Verifikasi koneksi ...Xs` spinner.

---

## [3.1.7] - 2026-09-29

### Fixed
- Public Share URL handling buat URL yang di-copy dari Android/browser share dialogs.
- Normalize surrounding quotes/backticks, zero-width characters, HTML entities, & `www.` URLs yang missing explicit scheme.
- Improved Next.js/React Flight extraction buat modern ChatGPT/AI share pages.
- HTTP 401/403/404 & anti-bot responses sekarang report actual access problem (bukan invalid URL format).
- Preserve redirected final URLs saat parsing & exporting imported chats.

### Added
- Regression tests buat URL normalization & Next/React Flight payload extraction.

---

## [3.1.6] - 2026-09-29

### Fixed
- Reader loader hang di **"Menyiapkan kontrol..."** — disebabkan stale `#reader-mode-label` DOM reference setelah floating header redesign.

### Added
- **Statistik baca** — halaman terlihat, progress, waktu baca, halaman aktif, mode.
- **Properties buku** — judul, author, format, jumlah halaman, ukuran sumber, nama file sumber, short book ID.
- Reader properties di-generate dari importer payload.

### Changed
- Landing page branding sekarang **GhostReader+**; CLI tetap **GhostWriter+**.

---

## [3.1.4] - 2026-09-29

### Fixed
- Duplicate PDF path prompt saat pake CLI menu **Import Ebook**.
- Unified ebook picker sekarang accept EPUB, MOBI, TXT, & PDF dalam one pass.
- Kalau PDF dipilih di situ, existing path di-pass langsung ke PDF pipeline (gak re-open picker).
- Direct **Import PDF** behavior tetep sama.
- Audit CLI import flows buat nested-picker pattern yang sama.

---

## [3.1.3] - 2026-09-29

### Changed
- Hapus semua **reader chrome auto-hide/tap-to-hide** behavior. Controls persistent.
- Rework reader header jadi **borderless floating title surface**.
- Consolidate Library, Reader Mode, & Reading Settings jadi **single header menu dropdown**.
- Hapus redundant header mode/settings icon buttons.
- Preserve bottom reading controls, page drawer, annotations, brightness, zoom, page animation controls.

### Fixed
- Hapus sisa `chrome-hidden`/`reveal()` state paths.
- Escape sekarang close header menu bareng panel reader lain.

---

## [3.1.1] - 2026-09-29

### Added
- **Format-agnostic annotation model** buat bookmarks, highlights, & notes.
- **IndexedDB-backed annotation storage** dengan localStorage migration fallback.
- Stable `book_id` fingerprint & per-page/resource content anchors.
- Text highlight anchors retain quote, prefix, & suffix context.
- Annotation documentation di `docs/ANNOTATIONS.md`.

### Changed
- Bookmark & note state gak lagi depend ke raw page-number localStorage keys.
- EPUB/TXT sections retain source resource identifier buat annotation anchoring.
- Comic/PDF image sections expose stable image-resource anchors.

### Compatibility
- Existing bookmarks & page notes dari reader sebelumnya dimigrasi on first load.
- PDF & comic visual-region annotations tetap page/resource based sampai dedicated coordinate annotation UI.

---

## [3.1.0] - 2026-09-29

### Added

**Reader direction:**
- Hapus **Focus Mode** completely.
- Reader presentation direduksi jadi **2 mode**: Horizontal & Vertical.
- Content types gak lagi jadi separate reader modes.

**Horizontal reading:**
- **Page Flip** (book-like 3D curl) sebagai primary page-turn animation.
- **Slide** & **Fade** remain available.
- LTR / RTL page direction.
- Tap zones, swipe, keyboard navigation, page slider, & page drawer.

**Reading controls:**
- Adjustable brightness overlay, persisted per reader.
- Fit: Auto / Width / Height.
- Zoom & pan buat image-based pages.
- Bookmark + automatic last-position persistence.
- Per-page notes.
- Text selection highlighting buat text-based EPUB/TXT pages.

**Format support:**
- **EPUB**: native ZIP/XML/XHTML parsing with spine order.
- **TXT**: automatic pagination into reader text pages.
- **MOBI**: conversion via Calibre `ebook-convert`, optional Python `mobi` fallback.
- **PDF**: existing fixed-layout image pipeline retained.
- **Comic ZIP**: existing image pipeline retained.

### Architecture
- Reader features live di `templates/reader/*`; generated `index.html` remains output artifact.
- Added regression coverage buat reader features & EPUB parsing.

---

## [3.0.9] - 2026-09-29

### Changed
- **Hapus Focus Mode entirely.**
- Consolidate reader jadi **exactly 2 presentation modes**:
  - **Horizontal** — novel, comic, manga, al-quran, scanned books, & page-based reading.
  - **Vertical** — webtoon, manhwa, & continuous-scroll comics.
- Hapus Novel / Comic / Manga / Webtoon as separate reader modes.
- Hapus visible previous/next navigation buttons; page navigation uses tap zones, swipe, keyboard, progress, page drawer, & jump-to-page.
- Tambah optional **LTR / RTL page direction** buat Horizontal mode.
- Migration buat old localStorage reader modes: legacy `webtoon` → `vertical`; other legacy modes → `horizontal`.
- Update server reader-template migration marker ke v3.0.9 (stale generated `index.html` files di-regenerate).
- Reader UI maintained dari `templates/reader/*`; generated reader HTML bukan source of truth.

---

## [3.0.8] - 2026-09-29

### Fixed
- Root cause blank/white **Focus Mode**: app pake one-row CSS grid sementara header/footer di-hide, ninggalin reader main area di implicit auto-sized grid row.
- Focus Mode sekarang pake **block/fixed viewport layout** & posisi `reader-main` + `reader-viewport` explicitly buat fill entire viewport.
- Keep Focus Mode independent dari browser Fullscreen API.
- Added regression test buat viewport-collapse prevention.

---

## [3.0.7] - 2026-09-29

### Fixed
- **Jinja2 template collision** — CSS sequence `{#reader-header` bikin reader generation gagal dengan `Missing end of comment tag`.
- Focus Mode gak lagi pake `requestFullscreen()`, `exitFullscreen()`, atau `fullscreenchange`.
- Focus Mode sekarang own fixed, full-viewport CSS layout.
- Focus entry/exit explicitly reflow & re-render current page.
- Focus exit button tetap above reader surface & pake direct click handler.
- Hapus duplicate page-drawer click binding.
- Hapus Auto-hide timer & Auto-hide setting dari generated reader; center tap jadi explicit hide/unhide control.

### QA
- Added regression tests buat Jinja template rendering & Focus Mode source invariants.
- Full existing core test suite passes.

---

## [3.0.6] - 2026-09-29

### Fixed
- Focus Mode exit button (`×`) sekarang punya real click/touch handler.
- Focus Mode gak lagi call chrome reveal timer saat entering focus.
- Focus control pake single toggle path (`enterFocus` / `exitFocus`).
- Hapus visible floating previous/next arrow buttons dari reader UI.
- Keep invisible page hit zones & keyboard navigation intact.

---

## [3.0.5] - 2026-09-29

### Added
- **Render Spinner** — restored animated CLI loading spinner during PDF page rendering.
- Spinner reports current batch/page & percentage (gak flood terminal dengan one line per batch).
- Added regression coverage buat spinner wiring di PDF render pipeline.

---

## [3.0.4] - 2026-09-29

### Fixed
- **Critical blank-reader bug:** generated reader pages sekarang expose `READER_DATA` di `window`, matching embedded runtime.
- Added **server-side migration** yang repairs existing `public/readers/*/index.html` files tanpa re-render PDF.
- Keep v3.0.3 server Path/string fix intact.

---

## [3.0.3] - 2026-09-29

### Fixed
- `serve.py` crash dengan `AttributeError: 'str' object has no attribute 'resolve'`.
- `run_server()` sekarang canonicalize both `str` & `Path` inputs sebelum filesystem operations.
- Added regression test buat server path contract.
- Added `tests/__init__.py` supaya documented `unittest discover` command works.

### Verification
- Core regression suite: **8/8 tests passing**.
- Local HTTP server smoke test: starts successfully from project directory.

---

## [3.0.1] - 2026-09-29

### Added
- **Public Share URL import** buat ChatGPT/OpenAI, Claude, Gemini, DeepSeek, & generic public pages.
- Direct main-menu shortcut `[6] Import Chat via Share URL`.
- Structured-data extraction dari common Next/React share pages dengan conservative HTML fallback.

### Fixed
- Chat batch import gak lagi assume list position equals parser conversation index.
- One malformed conversation gak lagi abort remaining selected conversations.
- Existing chat archives di-preserve during re-import; collisions pake unique slugs.
- Large PDF imports gak lagi hold entire document render di one giant image list. Rendering sekarang pake **12-page batches** & fallback to single-page rendering kalau batch fails.
- Pillow JPEG save avoids extra `optimize` temporary-resource path yang bisa produce `No such file or directory` di constrained devices.
- PDF import reports actual saved page count (bukan treat Poppler render count as proof of persistence).

### Changed
- `docs/STATE.md` bumped to v3.0.1-GW+.
- Tutorial & README sekarang document Share URL import & resilient PDF rendering.

### Stability rebuild — filesystem/render pipeline
- Added `core/paths.py` as single source of truth buat project paths.
- Hapus CWD-dependent reader/exporter paths dari critical import pipeline.
- Reworked PDF rendering buat call Poppler `pdftoppm` directly dengan staging directory & atomic page moves.
- Partial PDF imports gak lagi published as successful readers.
- Chat exports & share-URL imports sekarang resolve templates/output/index paths dari project root.
- Local server sekarang serves `public/` explicitly tanpa changing process CWD.
- DeepSeek backup state/download defaults rooted in project directory.
- Added path-independence & full-page PDF regression tests.

---

## [3.0.0] - 2026-09-29

### Added
- **Hybrid Reader** combining Moon+ style page reading dengan Webtoon continuous reading.
- Novel, Comic, Manga, & Webtoon modes.
- **Realistic CSS 3D page curl** dengan front/back sheet & binding-edge perspective.
- Auto-spread on wide displays.
- Auto-hide reading chrome.
- Focus Mode.
- **Double-tap zoom, pinch zoom, & pan up to 4×.**
- Multi-platform chat import buat ChatGPT/OpenAI, Claude, Gemini, DeepSeek, & generic JSON; Markdown/DOCX tetep supported.
- Novel page navigation tanpa thumbnail overload.

### Changed
- Reader navigation was rebuilt as a **smaller state machine** instead of incremental v2.8 reader patches.
- Manga uses explicit RTL mode instead of generic RTL toggle.
- Desktop spread respects Manga's right binding.
- PDF titles sekarang fall back ke filename kalau metadata generic/`Untitled`.
- Landing-page page counts dibaca dari explicit reader metadata marker.

### Fixed
- `Untitled` PDF imports producing `untitled` reader URLs ketika PDF metadata generic.
- Reader index showing `0 halaman` despite successfully rendered pages.
- Broken viewer template script block.
- Touch gesture conflicts between zoom & page swipe.
- Pinch handlers sekarang pake non-passive touch events & prevent default browser gesture interference.

### Removed
- Brittle dependency ke old v2.8 reader interaction stack.
- Redundant reader controls yang duplicated page/swipe behavior.

---

## [2.8.1] - 2026-09-29

### Added
- Reader Mode dropdown: **Novel, Comic, Manga, Webtoon**.
- **Focus Mode** buat hide sidebar/header/stats & request browser fullscreen.
- **Zoom baru dari dasar:** double-tap 2x/reset & pinch 1x–4x pada page-based modes.
- **Novel single-page layout** dengan local `GWPageCurl` engine & CSS 3D fallback.
- Text navigation buat ebook & thumbnail grid 2 kolom buat Comic/Manga/Webtoon.

### Changed
- Comic LTR/RTL jadi user-facing **Comic/Manga**.
- Landscape page-based reader otomatis pake two-page spread; portrait one page.
- Floating previous/next navigation sekarang horizontal: kiri/kanan halaman.
- Fit/Paged/Scroll/RTL/Webtoon/Two-Page manual toggles dihapus & digantikan mode/layout otomatis.

### Fixed
- PDF importer sekarang ignore metadata title placeholder seperti `Untitled`/`Tanpa Judul` & pake nama file PDF sebagai fallback.
- SVG/logo HTML yang sebelumnya di-escape Jinja2 sekarang di-render sebagai HTML trusted dengan `| safe`.
- Novel gak lagi nampilin halaman as vertical stack saat Page Curl aktif.
- Touch zoom pake listener non-passive, conflict guard, & `touch-action` yang sesuai.
- Page Curl internal dapat host gesture binding.

### Removed
- Immersive Mode toggle & shortcut `i`.
- Fullscreen toggle terpisah.
- `templates/reader/partials/immersive-btn.html`.
- Toggle manual redundant untuk Paged, Two-Page, RTL, Webtoon, & Fit.

### QA / Notes
- Zoom pada v2.8.1 diperlakukan sebagai implementasi baru; status R4 sebelumnya gak dijadikan asumsi bahwa fitur udah bekerja.
- `@vysmo/flipbook` gak dibundel karena dependency eksternal gak tersedia. Project pake `public/vendor/gw-page-curl.js` sebagai engine lokal.
- Smoke test Python template render buat ebook/comic berhasil.

### Post-release fix — Reader UX / Page Curl
- **Fixed:** keyboard-shortcuts help panel missing modal CSS & bisa render sebagai normal document content.
- **Fixed:** Novel Page Curl effectively disabled karena reader expect canvas element yang gak ada.
- **Changed:** Novel page turns sekarang pake self-contained DOM/CSS book-turn animation dengan real page-under-page stack, perspective, fold direction, & shadow.
- **Preserved:** landscape auto two-page mode, zoom gesture gating, Reader Mode, & existing navigation behavior.

### Post-release UX polish
- **Changed:** Added reader chrome auto-hide after inactivity; tap, pointer movement, atau keyboard navigation reveals controls.
- **Changed:** Added compact mobile header behavior.
- **Changed:** Focus Mode sekarang actually hides header, stats, side rails, & slider.
- **Changed:** Novel page-turn sekarang pake two-sided DOM sheet: outgoing page = front, destination page rendered on turning sheet's back.
- **Changed:** Scroll-to-top/bottom controls limited to Webtoon mode.
- **Fixed:** Unstyled scroll controls appearing at top of mobile reader.
- **Fixed:** Mobile reader chrome crowding.
- **Improved:** Physical-book page-turn realism & transition continuity.
- **Simplified:** Help-modal Reader Mode labels.

### Post-release overhaul — Reader UX v2.8.1
- **Added:** Moon-style reading stage with 3 tap zones.
- **Added:** Compact bottom reading chrome dengan live page progress & direct page slider.
- **Added:** Reading settings drawer dengan 4 page-turn effects: Curl, Slide, Cover, Fade.
- **Added:** Reader brightness overlay control.
- **Added:** Optional **Keep screen awake** via Screen Wake Lock API.
- **Added:** RTL-aware tap, swipe, & keyboard direction buat Manga.
- **Changed:** Reader chrome sekarang overlay (bukan consume viewport).
- **Changed:** Mobile header/stats redesigned.
- **Changed:** Page-mode up/down scroll controls forcibly hidden (available only to Webtoon).
- **Changed:** Page Curl rebuilt as two-sided physical sheet animation.
- **Fixed:** Mobile reader state dimana up/down scroll arrows muncul over page-mode readers.
- **Fixed:** Page-turn interaction conflicts.
- **Fixed:** Reader viewport compressed by persistent navigation chrome.

### Reader overhaul — Moon-style + Webtoon hybrid
- **Added:** Rebuilt reader shell around overlay-based mobile e-reader UX.
- **Added:** Three-zone reading interaction.
- **Added:** Auto-hide reader chrome.
- **Added:** Bookmark current page with persistent localStorage state.
- **Added:** Compact reading toolbar, page progress, direct page slider, settings drawer, brightness overlay, optional Screen Wake Lock, & Focus Mode.
- **Added:** Webtoon mode keeps continuous vertical flow & removes page-turn controls.
- **Changed:** Page-based reading now owns full viewport.
- **Changed:** Novel, Comic, & Manga use same page-stage architecture with mode-specific direction.
- **Changed:** Page curl is two-sided DOM sheet with perspective, binding edge, destination page underneath, shadow/lighting treatment, & drag/tap navigation.
- **Changed:** Landscape uses automatic two-page spread & non-curl transition.
- **Fixed:** Mobile page sizing gak lagi creates narrow page with large blank side area.
- **Fixed:** Legacy up/down scroll buttons absent from page-based modes.
- **Fixed:** Focus Mode gak lagi leaves reader chrome visible above page.
- **Fixed:** Reader controls gak lagi overlap page content as part of normal layout flow.

---

## [2.8.0] - 2026-09-29

### Added
- Page Curl WebGL untuk ebook pada paged mode, dengan drag-scrub & auto-advance.
- Two-Page Auto-Detect berbasis orientation landscape + width > 768px.
- Action Buttons: Copy, TTS, Share, Bookmark, & menu.
- Code Block Qwen-style: language header, fullscreen, copy, collapse >20 baris, View all, download, wrap, select all.
- `docs/TUTORIAL.md`.
- `tools/prompt.py` sebagai modul prompt bersama.
- `public/vendor/gw-page-curl.js` sebagai fallback WebGL dependency-free.

### Changed
- Rebranding CLI jadi **GhostWriter+** & reader/viewer jadi **GhostReader+**.
- Template dipecah jadi `templates/_shared/`, `templates/reader/`, & `templates/viewer/`.
- Jinja2 pake FileSystemLoader multi-folder & native `.render()`.
- `dist_index.py` memproses HTML chat satu kali per file.
- `deepseek_backup.py` memindahkan regex ANSI ke module-level constant.
- Requirements menambah `pypdf>=4.0.0`, `pdf2image>=1.17.0`, `Pillow>=10.0.0`.

### Fixed
- `toggleBtn` undefined di viewer diganti `sidebarToggle`.
- Circular import prompt antara `main.py` & importer dihilangkan.
- Template path exporter/importer diperbarui ke struktur modular.
- HTML escaping reader menambahkan `&quot;` & `&#39;`.
- Banner `serve.py` pake working directory setelah `chdir`, mencegah `public/public`.

### Removed
- `templates/viewer.html` lama.
- `templates/reader.html` lama.

### Assumptions / QA notes
- Blueprint minta riset `turngl`, `flipdocs`, & `@vysmo/flipbook`. Dari ketiganya, `@vysmo/flipbook` dipilih sebagai referensi arsitektur karena WebGL2, image URLs, lazy loading, drag-scrub, autoplay, & ukuran runtime kecil.
- Test browser/device nyata gak bisa dilakukan di runtime ini; smoke test Python, template loading, & JavaScript syntax dilakukan secara lokal.
- `docs/CHECKPOINT.md` sengaja gak diubah.

---

## [2.7.3] - 2026-09-20

### Added
- `tools/prompt.py` — `prompt()`, `prompt_yes_no()`, `is_cancel()`.
- `templates/reader.html` R1-R15 (reader UX overhaul):
  - R1 — Auto-bookmark + resume notif
  - R2 — Toggle hide navbar (immersive mode)
  - R3 — Fullscreen exit fix (mobile) — CRITICAL
  - R4 — Zoom pinch / double-tap
  - R5 — Reading progress bar
  - R6 — Page slider (scrubber)
  - R7 — Thumbnail grid navigasi
  - R8 — Reading stats
  - R9 — Night mode auto
  - R10 — Brightness control
  - R11 — Fit mode toggle
  - R12 — Continuous vs Paged mode
  - R13 — Two-page view (landscape)
  - R14 — RTL mode (manga)
  - R15 — Webtoon mode

### Fixed
- Circular import `main.py` ↔ `importers/*.py`.
- Resolve 156 merge conflict markers di viewer.html.
- `download_vendor.py` output ke root (`vendor/`), bukan `public/vendor/`.
- Fullscreen exit button hilang di mobile (R3).

### Changed
- Git workflow simplify mode — cuma 5 command: status, add, commit, log, checkout.
- Backup manual workflow (`_backups/`).

---

## [2.6.9] - 2026-09-19

### Added
- Initial reader.html dengan fitur dasar (loading, sidebar, fullscreen basic, swipe, keyboard).
- `templates/viewer.html` awal (~1500 baris).

### Fixed
- Landing page "0 halaman" buat ebook/comic.
- Duplikat folder `-2` setelah render ulang.

---

## [2.5.0] - 2026-09-19

### Added
- Backup versioning (PR-32) — timestamp filename, retention 5 versi terbaru.
- Prune stale folder (PR-33) — `--clean` flag di `sync.py`.

### Changed
- Auto-detection valid IDs dari `backups/*.json`.
- Dry-run mode + konfirmasi.

---

## [2.3.0] - 2026-09-19

### Added
- Mobile viewport fragmentation fix (PR-42A/B/C/D):
  - CSS `100dvh` + `env(safe-area-inset-bottom)`.
  - `window.visualViewport` API.
  - Search bar pindah ke bottom.

---

## [2.2.2] - 2026-09-19

### Added
- Circuit breaker pattern (PR-31) — 1x kena HTML challenge → set flag.
- Efek: 50-150 detik → 1-3 detik (97% saving).

---

## [2.2.0] - 2026-09-19

### Added
- DeepSeek live backup — fetch session list, incremental & full mode.
- Attachment manifest (`attachments/PENDING.md`).

### Fixed
- JavaScript parse error cascade (kurung kurawal salah posisi bikin seluruh `<script>` gagal parse).

---

## [2.0.0] - 2026-09-18

### Added
- PDF importer (image mode, DPI 150, JPEG q85).
- Comic ZIP importer (natural sort, skip junk, flatten nested).

### Changed
- Parser: JSON, MD, DOCX (multi-platform: DeepSeek, OpenAI, generic).

---

## [1.0.0] - 2026-09-17

### Added
- Core CLI + wizard mode.
- Parser: JSON chat backup (DeepSeek format).
- HTMLExporter + viewer.html awal.
- Landing page (dist_index.py).

---

<!-- LINK DEFINITIONS -->
[Unreleased]: https://github.com/nexterade/GhostWriterPlus/compare/v3.2.4...HEAD
[3.2.4]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.2.4
[3.2.3]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.2.3
[3.2.1]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.2.1
[3.2.0]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.2.0
[3.1.8]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.8
[3.1.7]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.7
[3.1.6]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.6
[3.1.4]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.4
[3.1.3]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.3
[3.1.1]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.1
[3.1.0]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.1.0
[3.0.9]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.9
[3.0.8]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.8
[3.0.7]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.7
[3.0.6]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.6
[3.0.5]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.5
[3.0.4]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.4
[3.0.3]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.3
[3.0.1]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.1
[3.0.0]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v3.0.0
[2.8.1]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v2.8.1
[2.8.0]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v2.8.0
[2.7.3]: https://github.com/nexterade/GhostWriterPlus/releases/tag/v2.7.3
- Reader chrome layout hotfix: header dan bottom page slider ditempatkan pada row layout terpisah dan dipastikan tetap visible saat berpindah halaman dari Pages.

## [3.3.3] — ChatGPT Export ZIP Import

### Added
- Import langsung **official ChatGPT data-export ZIP** dari menu Import Chat File.
- Auto-detect `conversations.json` di dalam ZIP, termasuk bila berada di subfolder.
- Pemilihan percakapan tetap memakai workflow existing (`all`, nomor, range).
- File HTML/DAT/metadata yang ikut dalam export dikenali dan diekstrak sementara untuk menjaga konteks archive; `conversations.json` menjadi sumber data percakapan.
- Safe ZIP extraction dengan proteksi path traversal, jumlah file, ukuran member, dan total uncompressed size.

### Changed
- Menu Import Chat File sekarang menampilkan `ChatGPT Export ZIP` sebagai format native.
- JSON/Markdown/DOCX importer existing tetap tidak berubah.

### Fixed
- User tidak perlu lagi membuka ZIP ChatGPT secara manual untuk mengambil `conversations.json`.

### Assumptions
- `conversations.json` dianggap source-of-truth untuk isi percakapan official export.
- HTML/DAT yang tidak diperlukan parser tidak dijadikan sumber alternatif otomatis; jika `conversations.json` tidak ada, import ditolak dengan pesan yang jelas daripada menghasilkan arsip parsial.

## [3.3.3] — ChatGPT Export ZIP — Hotfix

### Fixed
- Fix viewer loading overlay yang dapat berhenti di 95% pada mobile/browser ketika initialization flow mengalami runtime exception atau generated viewer masih memakai runtime lama.
- Tambahkan loader watchdog 12 detik sebagai fail-safe; watchdog hanya mengambil alih bila loader belum selesai.
- `serve.py` sekarang mem-patch generated viewer lama dengan watchdog saat server start.
- Sinkronkan marker template viewer ke `v3.3.3`.

### Assumption
- Viewer lama tidak dire-render ulang dari payload chat; hotfix runtime tidak mengubah isi percakapan.

