================================================================================
BACKLOG.md — GhostWriter+
Product Roadmap & PR Tracker
================================================================================
Versi    : v3.3.2
Update   : 2026-09-30
Berlaku  : Seluruh komponen proyek GhostWriter+

STATUS:
  v3.2.5     = Baseline (sebelum polish)
  v3.3.2     = Semua batch polish selesai
  v3.2.6+    = Polish Roadmap (7 batch)

================================================================================
🎯 ROADMAP POLISH — v3.2.6 → v3.3.2
================================================================================

Tujuan    : Polish layout & UX seluruh project
Prinsip   : Compact + Detail + Visual + Consistent + Accessible
Executor  : ChatGPT (ZIP in → ZIP out)

| Batch | Versi  | Scope               | Status | Estimasi |
|-------|--------|---------------------|--------|----------|
| 1 | v3.2.6 | Reader Core         | [x]    | 1 sesi   |
| 2 | v3.2.7 | Reader Overlays     | [x]    | 1 sesi   |
| 3 | v3.2.8 | Reader Content      | [x]    | 0.5 sesi |
| 4 | v3.2.9 | Viewer Redesign     | [x]    | 1.5 sesi |
| 5 | v3.3.0 | Landing Page        | [x]    | 1 sesi   |
| 6 | v3.3.1 | CLI Polish          | [x]    | 0.5 sesi |
| 7 | v3.3.2 | Cross-cutting       | [x]    | 1 sesi   |

================================================================================
📌 ATURAN PROAKTIF CHATGPT (WAJIB)
================================================================================

1. **JANGAN TANYA KONFIRMASI** — langsung eksekusi.
2. **KALAU ADA BUG** — fix langsung, catat di CHANGELOG.
3. **KALAU ADA AMBIGU** — pake judgment terbaik, catat asumsi di CHANGELOG.
4. **KALAU ADA FILE HILANG** — bikin file baru dengan asumsi wajar.
5. **KALAU ADA KONFLIK** — pilih yang paling masuk akal, catat di CHANGELOG.
6. **JANGAN INTERRUPT USER** — kecuali blocker fatal.
7. **SELESAIKAN SEMUA** sebelum balikin ZIP.
8. **UPDATE CHANGELOG** dengan semua perubahan + asumsi + bug fix.
9. **VERSION BUMP** di semua file yang perlu.
10. **KALAU RAGU** — pilih opsi paling konservatif, catat di CHANGELOG, lanjut.

================================================================================
📘 BATCH 1 — READER CORE (v3.2.6)  [x] DONE
================================================================================
Priority   : 🔴 High
Dependency : Tidak ada
Estimasi   : 1 sesi
Test       : Manual di Quetta + test suite

SCOPE:
  Redesign layout reader utama — header, TTS bar, footer, sidebar kiri, sidebar kanan.
  Fix mojibake di semua file reader.

═══════════════════════════════════════════════════════════════════════════════
FILE 1 — templates/reader/partials/header.html
═══════════════════════════════════════════════════════════════════════════════

REPLACE FULL. Struktur:

<header id="main-header">
  <!-- ROW 1: Main header -->
  <div class="header-main-row">
    <div class="header-info">
      <button class="sidebar-toggle" id="sidebar-toggle" title="Toggle library" aria-label="Toggle library">👻</button>
      <div class="status-dot"></div>
      <div class="header-title-group">
        <div class="header-title" id="chat-title">{{ TITLE }}</div>
        <div class="header-subtitle" id="header-subtitle">{{ SUBTITLE }}</div>
      </div>
    </div>
    <div class="header-tools">
      <button class="header-btn" id="theme-toggle" title="Toggle tema" aria-label="Toggle tema">🌙</button>
      <div class="header-menu-wrapper">
        <button class="header-btn" id="settings-toggle" title="Pengaturan" aria-label="Pengaturan" aria-expanded="false">🧭</button>
        <div class="header-menu-dropdown" id="settings-menu" aria-hidden="true">
          <button class="header-menu-item" data-settings-action="mode"><span class="icon">↔</span> Mode baca</button>
          <button class="header-menu-item" data-settings-action="settings"><span class="icon">⚙</span> Reading settings</button>
          <div class="header-menu-divider"></div>
          <button class="header-menu-item" id="bookmark-action" data-settings-action="bookmark"><span class="icon" id="bookmark-icon">☆</span> Bookmark halaman</button>
          <button class="header-menu-item" data-settings-action="notes"><span class="icon">✎</span> Notes & Highlight</button>
          <div class="header-menu-divider"></div>
          <button class="header-menu-item" data-settings-action="export-annotations-json"><span class="icon">⇩</span> Export JSON</button>
          <button class="header-menu-item" data-settings-action="export-annotations-md"><span class="icon">📝</span> Export MD</button>
          <div class="header-menu-divider"></div>
          <button class="header-menu-item" data-settings-action="properties"><span class="icon">ⓘ</span> Properties buku</button>
        </div>
      </div>
      <button class="header-btn" id="pages-toggle" title="Daftar halaman" aria-label="Daftar halaman">📑</button>
    </div>
  </div>

  <!-- ROW 2: TTS bar + clock -->
  <div class="tts-bar" id="tts-bar">
    <button class="tts-bar-btn" id="tts-play" title="Baca halaman" aria-label="Baca halaman">
      <span class="tts-icon">🔊</span>
      <span class="tts-label">Baca</span>
    </button>
    <div class="tts-bar-divider"></div>
    <button class="tts-bar-btn" id="tts-pause" title="Pause" aria-label="Pause" disabled>
      <span class="tts-icon">⏯</span>
      <span class="tts-label">Pause</span>
    </button>
    <div class="tts-bar-divider"></div>
    <button class="tts-bar-btn" id="tts-stop" title="Stop" aria-label="Stop" disabled>
      <span class="tts-icon">⏹</span>
      <span class="tts-label">Stop</span>
    </button>
    <div class="tts-bar-divider"></div>
    <span class="tts-clock" id="footer-clock">🕐 --:--</span>
  </div>
</header>

SPESIFIKASI:
  · 👻 = sidebar toggle (kiri)
  · 🌙 = theme toggle
  · 🧭 = settings dropdown (bukan TTS)
  · 📑 = pages toggle (buka sidebar kanan)
  · TTS bar = permanent, disabled state pas idle
  · Clock = update tiap 30 detik (format HH:MM)
  · Pause icon dynamic: ⏯ → ⏸️ (playing) → ▶️ (paused)

═══════════════════════════════════════════════════════════════════════════════
FILE 2 — templates/reader/partials/footer.html (BARU)
═══════════════════════════════════════════════════════════════════════════════

BUAT FILE BARU. Struktur:

<footer class="reader-footer" id="reader-footer">
  <!-- Slider -->
  <div class="slider-bar" id="slider-bar">
    <span id="page-label">1 / {{ TOTAL_PAGES }}</span>
    <input id="progress-slider" type="range" min="1" max="{{ TOTAL_PAGES }}" value="1" aria-label="Reading progress">
    <span id="percent-label">0%</span>
  </div>

  <!-- Stats -->
  <div class="stats-footer" id="stats-footer">
    <div class="stats-row">
      <span class="stat-item" title="Progress">
        <span class="stat-icon">📊</span>
        <span class="stat-value" id="footer-stat-progress">0%</span>
      </span>
      <span class="stat-sep">·</span>
      <span class="stat-item" title="Halaman">
        <span class="stat-icon">📄</span>
        <span class="stat-value" id="footer-stat-current">1/{{ TOTAL_PAGES }}</span>
      </span>
      <span class="stat-sep">·</span>
      <span class="stat-item" title="Terlihat">
        <span class="stat-icon">👁️</span>
        <span class="stat-value" id="footer-stat-seen">0</span>
      </span>
      <span class="stat-sep">·</span>
      <span class="stat-item" title="Waktu baca">
        <span class="stat-icon">⏱️</span>
        <span class="stat-value" id="footer-stat-time">0d</span>
      </span>
    </div>
    <div class="stats-row">
      <span class="stat-item" title="Streak">
        <span class="stat-icon">📈</span>
        <span class="stat-value" id="footer-stat-streak">0 hari</span>
      </span>
    </div>
  </div>
</footer>

SPESIFIKASI:
  · Slider = page label + range + percent
  · Stats row 1 = progress, halaman, terlihat, waktu
  · Stats row 2 = streak
  · Padding bottom = safe-area-inset-bottom

═══════════════════════════════════════════════════════════════════════════════
FILE 3 — templates/reader/partials/sidebar.html
═══════════════════════════════════════════════════════════════════════════════

REPLACE FULL. Struktur:

<aside class="sidebar reader-sidebar collapsed" id="library-drawer">
  <div class="sidebar-header">
    <a class="gw-brand reader-brand-name" href="../../index.html" title="Kembali ke arsip">
      {{ LOGO_SVG | safe }}
      <span class="gw-wordmark">GhostReader+</span>
    </a>
    <button class="sidebar-icon-btn" id="sidebar-close-btn" title="Tutup sidebar" aria-label="Tutup sidebar">✕</button>
  </div>

  <div class="sidebar-list">
    <!-- BUKU AKTIF -->
    <div class="sidebar-section">
      <div class="sidebar-section-label">
        <span class="section-icon">📖</span> Buku Aktif
      </div>
      <div class="sidebar-book-card">
        <div class="sidebar-book-title">{{ TITLE }}</div>
        <div class="sidebar-book-meta">{{ SUBTITLE }}</div>
        <div class="book-progress-bar">
          <div class="book-progress-fill" id="sidebar-book-progress-fill"></div>
        </div>
        <div class="book-progress-text">
          <span id="sidebar-book-progress-text">0%</span>
          <span id="sidebar-book-page-text">1 / {{ TOTAL_PAGES }}</span>
        </div>
      </div>
    </div>

    <!-- STATISTIK BACA -->
    <div class="sidebar-section">
      <div class="sidebar-section-label">
        <span class="section-icon">📊</span> Statistik Baca
      </div>
      <div class="reader-stats-detail">
        <div class="stat-row stat-progress-row">
          <div class="stat-row-head">
            <span class="stat-icon">📊</span>
            <span class="stat-label">Progress</span>
            <span class="stat-value" id="sidebar-stat-progress">0%</span>
          </div>
          <div class="stat-progress-bar">
            <div class="stat-progress-fill" id="sidebar-stat-progress-fill"></div>
          </div>
        </div>
        <div class="stat-row">
          <span class="stat-icon">📄</span>
          <span class="stat-label">Halaman</span>
          <span class="stat-value" id="sidebar-stat-current">1 / {{ TOTAL_PAGES }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-icon">👁️</span>
          <span class="stat-label">Terlihat</span>
          <span class="stat-value" id="sidebar-stat-seen">0 / {{ TOTAL_PAGES }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-icon">⏱️</span>
          <span class="stat-label">Waktu baca</span>
          <span class="stat-value" id="sidebar-stat-time">0d</span>
        </div>
        <div class="stat-row">
          <span class="stat-icon">📈</span>
          <span class="stat-label">Streak</span>
          <span class="stat-value" id="sidebar-stat-streak">0 hari</span>
        </div>
      </div>
    </div>

    <!-- LIBRARY -->
    <div class="sidebar-section">
      <button class="sidebar-section-toggle" id="library-toggle" aria-expanded="true">
        <span class="section-icon">📚</span>
        <span>Library</span>
        <span class="library-count" id="library-count">(0)</span>
        <span class="toggle-arrow">▾</span>
      </button>
      <div id="library-list" class="library-list"></div>
    </div>
  </div>

  <div class="sidebar-footer">
    <div class="sidebar-footer-brand">
      <span>👻</span>
      <span>v3.2.6</span>
    </div>
    <span class="sidebar-footer-clock" id="sidebar-clock">🕐 --:--</span>
  </div>
</aside>

SPESIFIKASI:
  · Book card = progress bar inline + persen + halaman
  · Stats = 5 metric (progress, halaman, terlihat, waktu, streak)
  · Progress bar = gradient accent → purple
  · Library = collapsible + count
  · Footer = brand + clock realtime

═══════════════════════════════════════════════════════════════════════════════
FILE 4 — templates/reader/partials/right-rail.html
═══════════════════════════════════════════════════════════════════════════════

REPLACE FULL. Struktur:

<aside class="right-rail reader-page-rail collapsed" id="page-drawer">
  <div class="right-rail-header">
    <span class="right-rail-title">▤ Pages</span>
    <button class="header-btn" id="right-rail-close" title="Tutup">✕</button>
  </div>
  <div class="jump-row">
    <input id="page-jump" type="number" min="1" max="{{ TOTAL_PAGES }}" placeholder="Page">
    <button id="page-jump-go">Go</button>
  </div>
  <div id="page-list" class="page-list"></div>
</aside>

SPESIFIKASI:
  · Mode thumbnail (comic) = grid 2 kolom
  · Mode list (novel) = list nomor halaman
  · Active highlight = accent color
  · Compact spacing

═══════════════════════════════════════════════════════════════════════════════
FILE 5 — templates/reader/reader.html
═══════════════════════════════════════════════════════════════════════════════

UPDATE:
  1. Tambah include footer:
     {% include 'reader/partials/footer.html' %}
     Letakkan setelah </main> di dalam .main-area

  2. Update meta version:
     <meta name="gw-reader-template-version" content="3.2.6">

  3. Fix mojibake:
     тШЖ → ☆
     тШЕ → ★

═══════════════════════════════════════════════════════════════════════════════
FILE 6 — templates/reader/style.css
═══════════════════════════════════════════════════════════════════════════════

APPEND CSS (JANGAN REPLACE). Tambahkan di paling bawah:

/* ============================================================
   v3.2.6 — HEADER 2 BARIS
   ============================================================ */

#main-header {
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 30;
}

.header-main-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  min-height: 58px;
}

/* TTS bar */
.tts-bar {
  display: flex;
  align-items: stretch;
  border-top: 1px solid var(--border);
  min-height: 42px;
}

.tts-bar-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 12px;
  background: transparent;
  border: 0;
  color: var(--text);
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  min-width: 0;
}

.tts-bar-btn:hover:not(:disabled) {
  background: var(--surface2);
  color: var(--viewer-accent);
}

.tts-bar-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.tts-bar-btn.active {
  background: var(--viewer-accent-glow);
  color: var(--viewer-accent);
}

.tts-bar-divider {
  width: 1px;
  background: var(--border);
  flex-shrink: 0;
}

.tts-icon {
  font-size: 0.95rem;
  line-height: 1;
}

.tts-label {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tts-clock {
  display: inline-flex;
  align-items: center;
  padding: 0 14px;
  font-family: ui-monospace, monospace;
  font-size: 0.72rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ============================================================
   v3.2.6 — FOOTER
   ============================================================ */

.reader-footer {
  flex-shrink: 0;
  background: var(--surface);
  border-top: 1px solid var(--border);
  z-index: 30;
}

.slider-bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 8px 14px;
  border-bottom: 1px solid var(--border);
  font-size: 0.74rem;
  color: var(--muted);
}

.slider-bar #page-label {
  min-width: 58px;
  font-variant-numeric: tabular-nums;
}

.slider-bar #progress-slider {
  width: 100%;
  height: 18px;
  accent-color: var(--viewer-accent);
}

.slider-bar #percent-label {
  color: var(--viewer-accent);
  font-weight: 600;
  min-width: 32px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.stats-footer {
  padding: 8px 14px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px));
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.7rem;
  color: var(--muted);
}

.stats-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.stat-item .stat-icon {
  font-size: 0.72rem;
  line-height: 1;
}

.stat-item .stat-value {
  color: var(--text);
  font-weight: 600;
}

.stat-sep {
  color: var(--border);
  font-weight: 300;
  user-select: none;
}

/* ============================================================
   v3.2.6 — SIDEBAR KIRI
   ============================================================ */

.sidebar-section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 14px 12px 8px;
  user-select: none;
}

.sidebar-section-label .section-icon {
  font-size: 0.85rem;
  line-height: 1;
}

.sidebar-book-card {
  padding: 12px;
  margin: 0 8px 8px;
  background: var(--viewer-accent-glow);
  border-radius: 10px;
  border-left: 3px solid var(--viewer-accent);
}

.sidebar-book-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
  line-height: 1.35;
  word-break: break-word;
}

.sidebar-book-meta {
  font-size: 0.7rem;
  color: var(--muted);
  line-height: 1.3;
  margin-bottom: 8px;
}

.book-progress-bar {
  width: 100%;
  height: 4px;
  background: var(--surface);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 4px;
}

.book-progress-fill {
  height: 100%;
  width: 0%;
  background: var(--viewer-accent);
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.book-progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 0.66rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.book-progress-text span:first-child {
  color: var(--viewer-accent);
  font-weight: 600;
}

.reader-stats-detail {
  padding: 10px 12px;
  margin: 0 8px 8px;
  background: var(--surface2);
  border-radius: 10px;
  border: 1px solid var(--border);
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.72rem;
}

.stat-row:last-child {
  border-bottom: 0;
}

.stat-row-head {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-bottom: 6px;
}

.stat-icon {
  font-size: 0.8rem;
  flex-shrink: 0;
  width: 18px;
  text-align: center;
  line-height: 1;
}

.stat-label {
  color: var(--muted);
  flex: 1;
  font-size: 0.7rem;
}

.stat-value {
  color: var(--text);
  font-weight: 600;
  font-size: 0.74rem;
  font-variant-numeric: tabular-nums;
}

.stat-progress-row {
  display: block;
  padding: 7px 0;
}

.stat-progress-bar {
  width: 100%;
  height: 5px;
  background: var(--surface);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 4px;
}

.stat-progress-fill {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--viewer-accent), var(--purple, #a78bfa));
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.sidebar-section-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  background: transparent;
  border: 0;
  color: var(--muted);
  font-family: inherit;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s ease;
}

.sidebar-section-toggle:hover {
  color: var(--viewer-accent);
}

.sidebar-section-toggle .section-icon {
  font-size: 0.85rem;
  line-height: 1;
}

.sidebar-section-toggle .library-count {
  color: var(--viewer-accent);
  font-weight: 600;
  letter-spacing: 0;
  font-size: 0.7rem;
}

.sidebar-section-toggle .toggle-arrow {
  margin-left: auto;
  font-size: 0.7rem;
  transition: transform 0.2s ease;
  color: var(--muted);
}

.sidebar-section-toggle[aria-expanded="true"] .toggle-arrow {
  transform: rotate(180deg);
}

.library-list {
  padding: 0 8px 8px;
  max-height: 300px;
  overflow-y: auto;
  transition: max-height 0.25s ease, opacity 0.2s ease;
}

.library-list.collapsed {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  padding: 0 8px;
}

.reader-sidebar .library-item {
  width: 100%;
  text-align: left;
  border: 1px solid var(--border);
  background: var(--surface2);
  color: var(--text);
  padding: 8px 10px;
  border-radius: 8px;
  margin-bottom: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  font-family: inherit;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reader-sidebar .library-item:hover {
  border-color: var(--viewer-accent);
  background: var(--viewer-accent-glow);
  color: var(--viewer-accent);
}

.reader-sidebar .library-item.active {
  border-color: var(--viewer-accent);
  background: var(--viewer-accent-glow);
  color: var(--viewer-accent);
}

.sidebar-footer-brand {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  color: var(--muted);
}

.sidebar-footer-clock {
  font-family: ui-monospace, monospace;
  font-size: 0.7rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

/* ============================================================
   v3.2.6 — MOBILE
   ============================================================ */

@media (max-width: 768px) {
  .reader-sidebar { width: min(320px, 85vw); }
}

@media (max-width: 600px) {
  .header-main-row { padding: 8px 10px; }
  .tts-bar-btn { padding: 8px 8px; font-size: 0.74rem; gap: 4px; }
  .tts-clock { padding: 0 10px; font-size: 0.68rem; }
  .slider-bar { padding: 7px 10px; gap: 8px; }
  .stats-footer { padding: 7px 10px; padding-bottom: calc(7px + env(safe-area-inset-bottom, 0px)); font-size: 0.65rem; }
}

@media (max-width: 480px) {
  .reader-sidebar { width: 85vw; }
  .sidebar-book-title { font-size: 0.8rem; }
}

@media (max-width: 420px) {
  .tts-label { display: none; }
  .tts-bar-btn { padding: 10px; min-height: 42px; }
  .tts-icon { font-size: 1.1rem; }
  .stats-footer { font-size: 0.62rem; }
}

═══════════════════════════════════════════════════════════════════════════════
FILE 7 — templates/reader/script.js
═══════════════════════════════════════════════════════════════════════════════

UPDATE:
  1. Ganti handler closeReaderMenu + header-menu-toggle dengan DUAL DROPDOWN:

     function closeReaderMenu() {
       document.querySelectorAll('.header-menu-dropdown.visible').forEach(d => {
         d.classList.remove('visible');
         d.setAttribute('aria-hidden', 'true');
       });
       const settingsBtn = document.getElementById('settings-toggle');
       if (settingsBtn) settingsBtn.setAttribute('aria-expanded', 'false');
     }

     function setupSettingsDropdown() {
       const toggle = document.getElementById('settings-toggle');
       const menu = document.getElementById('settings-menu');
       if (!toggle || !menu) return;
       toggle.addEventListener('click', (e) => {
         e.stopPropagation();
         const isOpen = menu.classList.contains('visible');
         closeReaderMenu();
         if (!isOpen) {
           menu.classList.add('visible');
           menu.setAttribute('aria-hidden', 'false');
           toggle.setAttribute('aria-expanded', 'true');
         }
       });
     }

     setupSettingsDropdown();

     document.getElementById('pages-toggle')?.addEventListener('click', (e) => {
       e.stopPropagation();
       closeReaderMenu();
       if (rightDrawer.classList.contains('collapsed')) {
         openDrawer(rightDrawer);
       } else {
         closeDrawers();
       }
     });

     document.addEventListener('click', (e) => {
       if (!e.target.closest('.header-menu-wrapper')) closeReaderMenu();
     });

     document.querySelectorAll('[data-settings-action]').forEach(btn => {
       btn.onclick = () => {
         const action = btn.dataset.settingsAction;
         closeReaderMenu();
         if (action === 'mode') {
           modePop.classList.toggle('open');
           settingsPop.classList.remove('open');
           notesPop.classList.remove('open');
         }
         if (action === 'settings') {
           settingsPop.classList.toggle('open');
           modePop.classList.remove('open');
           notesPop.classList.remove('open');
         }
         if (action === 'bookmark') toggleBookmark();
         if (action === 'notes') openNotes();
         if (action === 'export-annotations-json') exportAnnotations('json');
         if (action === 'export-annotations-md') exportAnnotations('md');
         if (action === 'properties') { closeInfoModals(); openInfoModal('properties'); }
       };
     });

  2. TTS Handler:

     let ttsState = 'idle';

     function updateTTSBar() {
       const playBtn = document.getElementById('tts-play');
       const pauseBtn = document.getElementById('tts-pause');
       const stopBtn = document.getElementById('tts-stop');
       if (!playBtn || !pauseBtn || !stopBtn) return;
       const pauseIcon = pauseBtn.querySelector('.tts-icon');
       const pauseLabel = pauseBtn.querySelector('.tts-label');

       if (ttsState === 'idle') {
         playBtn.disabled = false; pauseBtn.disabled = true; stopBtn.disabled = true;
         if (pauseIcon) pauseIcon.textContent = '⏯';
         if (pauseLabel) pauseLabel.textContent = 'Pause';
         playBtn.classList.remove('active'); pauseBtn.classList.remove('active');
       } else if (ttsState === 'playing') {
         playBtn.disabled = true; pauseBtn.disabled = false; stopBtn.disabled = false;
         if (pauseIcon) pauseIcon.textContent = '⏸️';
         if (pauseLabel) pauseLabel.textContent = 'Pause';
         playBtn.classList.add('active'); pauseBtn.classList.add('active');
       } else if (ttsState === 'paused') {
         playBtn.disabled = true; pauseBtn.disabled = false; stopBtn.disabled = false;
         if (pauseIcon) pauseIcon.textContent = '▶️';
         if (pauseLabel) pauseLabel.textContent = 'Resume';
         playBtn.classList.add('active'); pauseBtn.classList.remove('active');
       }
     }

     document.getElementById('tts-play')?.addEventListener('click', () => {
       if (!('speechSynthesis' in window)) { toastMsg('TTS tidak didukung browser ini'); return; }
       if (ttsState === 'playing') return;
       const text = String(pages[index]?.content || '').trim();
       if (!text) { toastMsg('Halaman ini tidak memiliki teks'); return; }
       const u = new SpeechSynthesisUtterance(text);
       u.lang = document.getElementById('tts-voice')?.value || 'id-ID';
       u.onend = () => { ttsState = 'idle'; updateTTSBar(); };
       u.onerror = () => { ttsState = 'idle'; updateTTSBar(); };
       speechSynthesis.cancel();
       speechSynthesis.speak(u);
       ttsState = 'playing';
       updateTTSBar();
       toastMsg(`🔊 Membaca halaman ${index + 1}`);
     });

     document.getElementById('tts-pause')?.addEventListener('click', () => {
       if (!('speechSynthesis' in window)) return;
       if (ttsState === 'playing') { speechSynthesis.pause(); ttsState = 'paused'; toastMsg('TTS dijeda'); }
       else if (ttsState === 'paused') { speechSynthesis.resume(); ttsState = 'playing'; toastMsg('TTS dilanjutkan'); }
       updateTTSBar();
     });

     document.getElementById('tts-stop')?.addEventListener('click', () => {
       if (!('speechSynthesis' in window)) return;
       speechSynthesis.cancel();
       ttsState = 'idle';
       updateTTSBar();
       toastMsg('TTS dihentikan');
     });

  3. Footer Clock:

     function updateClock() {
       const clock = document.getElementById('footer-clock');
       if (!clock) return;
       const now = new Date();
       const hh = String(now.getHours()).padStart(2, '0');
       const mm = String(now.getMinutes()).padStart(2, '0');
       clock.textContent = `🕐 ${hh}:${mm}`;
     }
     updateClock();
     setInterval(updateClock, 30 * 1000);

  4. Stats Footer:

     function updateStatsFooter() {
       const stats = loadReadingStats();
       const seen = Array.isArray(stats.pagesSeen) ? stats.pagesSeen.length : 0;
       const n = pages.length || 1;
       const progressPct = Math.round(((index + 1) / n) * 100);
       const streak = calculateStreak(stats);
       const el = (id) => document.getElementById(id);

       const progressEl = el('footer-stat-progress');
       const currentEl = el('footer-stat-current');
       const seenEl = el('footer-stat-seen');
       const timeEl = el('footer-stat-time');
       const streakEl = el('footer-stat-streak');

       if (progressEl) progressEl.textContent = `${progressPct}%`;
       if (currentEl) currentEl.textContent = `${index + 1}/${n}`;
       if (seenEl) seenEl.textContent = String(seen);
       if (timeEl) timeEl.textContent = formatReadTime(stats.seconds);
       if (streakEl) streakEl.textContent = `${streak} hari`;
     }

     function calculateStreak(stats) {
       const days = new Set(stats.active_days || []);
       let streak = 0;
       for (let t = new Date(); ; t.setDate(t.getDate() - 1)) {
         const d = t.toISOString().slice(0, 10);
         if (!days.has(d)) break;
         streak++;
       }
       return streak;
     }

     // Panggil updateStatsFooter() di dalam updateStatsSidebar()

  5. Book Progress Sidebar:

     function updateBookProgress() {
       const n = pages.length || 1;
       const progressPct = Math.round(((index + 1) / n) * 100);
       const fill = document.getElementById('sidebar-book-progress-fill');
       const text = document.getElementById('sidebar-book-progress-text');
       const pageText = document.getElementById('sidebar-book-page-text');
       if (fill) fill.style.width = `${progressPct}%`;
       if (text) text.textContent = `${progressPct}%`;
       if (pageText) pageText.textContent = `${index + 1} / ${n}`;
     }

  6. Library Toggle:

     document.getElementById('library-toggle')?.addEventListener('click', (e) => {
       const btn = e.currentTarget;
       const list = document.getElementById('library-list');
       if (!list) return;
       const isExpanded = btn.getAttribute('aria-expanded') === 'true';
       btn.setAttribute('aria-expanded', String(!isExpanded));
       list.classList.toggle('collapsed', isExpanded);
     });

  7. Sidebar Clock:

     function updateSidebarClock() {
       const clock = document.getElementById('sidebar-clock');
       if (!clock) return;
       const now = new Date();
       const hh = String(now.getHours()).padStart(2, '0');
       const mm = String(now.getMinutes()).padStart(2, '0');
       clock.textContent = `🕐 ${hh}:${mm}`;
     }
     updateSidebarClock();
     setInterval(updateSidebarClock, 30 * 1000);

  8. Update updateBookmarkButton():

     SEBELUM:
     const b = $('#bookmark-action');
     if (b) b.querySelector('.icon').textContent = active ? '★' : '☆';

     SESUDAH:
     const b = $('#bookmark-icon');
     if (b) b.textContent = active ? '★' : '☆';

  9. Fix MOJIBAKE di seluruh script.js:
     тШЕ → ★
     тШЖ → ☆
     ЁЯУЦ → 📖
     ЁЯОи → 🎨
     ЁЯТм → 💬
     тАФ → —
     тЖТ → →
     тЬУ → ✓
     ЁЯФК → 🔊
     тШАя╕П → ☀️
     ЁЯМЩ → 🌙

═══════════════════════════════════════════════════════════════════════════════
FILE 8 — docs/CHANGELOG.md
═══════════════════════════════════════════════════════════════════════════════

APPEND section [3.2.6] di paling atas (di bawah heading utama):

## [3.2.6] - 2026-09-30

### Changed
- Reader header jadi 2 baris: main header + TTS bar.
- TTS bar permanent dengan disabled state (play/pause/stop + clock).
- Footer reader: slider + stats baca (progress, halaman, terlihat, waktu, streak).
- Sidebar kiri: Compact + Detail + Visual (book card progress, stats detail, library collapsible).
- Sidebar kanan: page drawer compact.
- Icon mapping: 👻 sidebar, 🧭 settings, 📑 pages.
- Clock realtime (🕐 HH:MM) di TTS bar + sidebar footer.

### Fixed
- Mojibake di templates/reader/script.js & reader.html.

### Validation
- Full test suite passing.

═══════════════════════════════════════════════════════════════════════════════
FILE 9 — docs/STATE.md
═══════════════════════════════════════════════════════════════════════════════

UPDATE:
  · Versi: v3.2.6
  · Update: 2026-09-30
  · Section 6 Status Rilis — version bump

═══════════════════════════════════════════════════════════════════════════════
FILE 10 — serve.py
═══════════════════════════════════════════════════════════════════════════════

UPDATE:
  READER_TEMPLATE_VERSION = "3.2.6"

═══════════════════════════════════════════════════════════════════════════════
FILE 11 — tests/test_v324_features.py
═══════════════════════════════════════════════════════════════════════════════

UPDATE assertion:
  assert 'content="3.2.5"' → assert 'content="3.2.6"'
  Atau pake regex dynamic: assert re.search(r'content="3\.2\.\d+"', html)

================================================================================
📘 BATCH 2 — READER OVERLAYS (v3.2.7)  [x] DONE
================================================================================
Priority   : 🟡 Medium
Dependency : Batch 1
Estimasi   : 1 sesi

SCOPE:
  Polish popover, modal, toast, loading overlay.

FILE YANG DIUBAH:
  1.  templates/reader/partials/mode-popover.html
  2.  templates/reader/partials/settings-popover.html
  3.  templates/reader/partials/notes-popover.html
  4.  templates/reader/partials/stats-modal.html
  5.  templates/reader/partials/global-stats-modal.html
  6.  templates/reader/partials/properties-modal.html
  7.  templates/reader/partials/toast.html
  8.  templates/reader/partials/loader.html
  9.  templates/reader/style.css
  10. templates/reader/script.js

DESIGN TOKEN:
  · Popover width: 260px
  · Modal width: 460px
  · Padding: 12px (popover), 18px (modal)
  · Border-radius: 12px
  · Shadow: 0 12px 32px rgba(0,0,0,0.4)

SPESIFIKASI PER FILE:

  mode-popover.html:
    · Header: "Mode baca"
    · 2 opsi: Horizontal, Vertical
    · Icon + label + description
    · Compact

  settings-popover.html:
    · Animasi halaman: select (curl/slide/fade)
    · Fit: select (auto/width/height)
    · Brightness: range 30-100
    · Direction: select (ltr/rtl)
    · TTS voice: select (id-ID/en-US)

  notes-popover.html:
    · Annotation summary
    · Textarea untuk catatan
    · Button Save, Clear
    · Button Highlight
    · Help text

  stats-modal.html:
    · Grid 2x2: halaman, progress, waktu, current
    · Mode info

  global-stats-modal.html:
    · Grid 2x2: total waktu, halaman, buku, streak
    · Buku terakhir

  properties-modal.html:
    · List: judul, author, format, halaman, size, source, book ID

  toast.html:
    · Icon + text
    · Auto-dismiss 2 detik
    · Success/error state

  loader.html:
    · Logo pulse
    · Progress bar shimmer
    · Status text

VALIDASI:
  · Semua popover compact
  · Modal responsive
  · Toast auto-dismiss
  · Test suite passing

================================================================================
📘 BATCH 3 — READER CONTENT (v3.2.8)  [x] DONE
================================================================================
Priority   : 🟡 Medium
Dependency : Batch 1
Estimasi   : 0.5 sesi

SCOPE:
  Polish page content + floating nav + edge cases.

FILE YANG DIUBAH:
  1.  templates/reader/partials/reader-container.html
  2.  templates/reader/partials/floating-nav.html
  3.  templates/reader/style.css
  4.  templates/reader/script.js

SPESIFIKASI:

  reader-container.html:
    · Book stage (existing)
    · Webtoon flow (existing)
    · Edge case: empty page state

  floating-nav.html:
    · Compact 40px
    · Hover reveal
    · Smooth animation
    · Scroll top/bottom buttons

  style.css (append):
    .reader-page { box-shadow: 2 layer; border-radius: 4px; }
    .page-image { max-width, object-fit: contain; }
    .page-text { font-family: Georgia; line-height: 1.85; padding: clamp(28px, 6vw, 72px); }
    body.spread .reader-page { 2-page layout; gap: 2px; }
    .floating-nav { position: absolute; right: 24px; bottom: 80px; }

  script.js (update):
    · Floating nav show/hide logic
    · Edge case handling

VALIDASI:
  · Image page rapi
  · Text page readable
  · Spread mode works
  · Floating nav smooth

================================================================================
📘 BATCH 4 — VIEWER REDESIGN (v3.2.9)  [x] DONE
================================================================================
Priority   : 🟡 Medium
Dependency : Batch 1-3
Estimasi   : 1.5 sesi

SCOPE:
  Redesign chat viewer — konsisten sama reader.

FILE YANG DIUBAH:
  1.  templates/viewer/viewer.html
  2.  templates/viewer/partials/header.html
  3.  templates/viewer/partials/sidebar.html
  4.  templates/viewer/partials/right-rail.html
  5.  templates/viewer/partials/search-bar.html
  6.  templates/viewer/partials/loader.html
  7.  templates/viewer/partials/toast.html
  8.  templates/viewer/partials/chat-container.html
  9.  templates/viewer/style.css
  10. templates/viewer/script.js

SPESIFIKASI:

  header.html:
    · Compact — 1 baris + action bar
    · Icon konsisten kaya reader
    · Sidebar toggle, title, theme, settings, right rail toggle

  sidebar.html:
    · Compact library
    · Recent items
    · Collapsible section

  right-rail.html:
    · User message nav
    · Compact
    · Active highlight

  search-bar.html:
    · Compact
    · Sticky
    · Regex support

  chat-container.html:
    · Bubble user/AI
    · Action buttons compact
    · Code block Qwen-style

  style.css (append):
    .bubble { box-shadow: subtle; border-radius: 16px; }
    .message-row { gap: 24px; }
    .msg-action-btn { compact icon-only; }
    .code-block { Qwen-style; }

  script.js (update):
    · Handler konsisten
    · Fix mojibake (kalau ada)

VALIDASI:
  · Header compact
  · Bubble rapi
  · Code block works
  · Search works

================================================================================
📘 BATCH 5 — LANDING PAGE (v3.3.0)  [x] DONE
================================================================================
Priority   : 🟢 Low
Dependency : Batch 1-4
Estimasi   : 1 sesi

SCOPE:
  Redesign landing page.

FILE YANG DIUBAH:
  1.  tools/dist_index.py
  2.  public/index.html (auto-regenerate)
  3.  public/index.json (auto-regenerate)

SPESIFIKASI:

  Header:
    · Compact brand + theme toggle

  Search + Sort:
    · Sticky pas scroll
    · Compact

  Tab Bar:
    · Pill style
    · Active state

  Card Item:
    · Compact
    · Favorite button
    · Type badge

  Favorites + Recent:
    · Collapsible
    · Max 5 items

  Grid/List:
    · Smooth transition
    · Persist di localStorage

VALIDASI:
  · Semua section rapi
  · Responsive
  · Test suite passing

================================================================================
📘 BATCH 6 — CLI POLISH (v3.3.1)  [x] DONE
================================================================================
Priority   : 🟢 Low
Dependency : Tidak ada
Estimasi   : 0.5 sesi

SCOPE:
  Polish CLI wizard.

FILE YANG DIUBAH:
  1.  main.py
  2.  tools/loading.py
  3.  tools/checklist.py
  4.  tools/theme.py

SPESIFIKASI:

  main.py:
    · Menu compact + icon per item
    · Prompt konsisten
    · Hint jelas

  loading.py:
    · Banner compact ASCII art
    · Spinner smooth
    · Progress bar konsisten

  checklist.py:
    · Compact layout
    · Visual checkbox
    · Better scroll

  theme.py:
    · Color palette review
    · Tambah warna kalau perlu

VALIDASI:
  · Menu rapi
  · Spinner smooth
  · Checklist works

================================================================================
📘 BATCH 7 — CROSS-CUTTING (v3.3.2)  [x] DONE
================================================================================
Priority   : 🟢 Low
Dependency : Batch 1-6
Estimasi   : 1 sesi

SCOPE:
  Polish theme, typography, spacing, accessibility.

FILE YANG DIUBAH:
  1.  templates/reader/style.css
  2.  templates/viewer/style.css
  3.  tools/dist_index.py
  4.  tools/theme.py
  5.  Semua template (focus state, aria)

SPESIFIKASI:

  Theme:
    · Konsisten dark/light
    · CSS variables review

  Typography:
    · Modular scale: 12/14/16/18/20
    · Line-height review
    · Font stack review

  Spacing:
    · 4px / 8px grid
    · Padding review

  Color:
    · Refresh Midnight
    · Accent color review
    · Contrast check

  Accessibility:
    · Focus state
    · ARIA labels
    · Keyboard nav

  Animation:
    · Duration konsisten (0.15s, 0.25s, 0.4s)
    · Easing konsisten (ease, ease-out)

  Mobile:
    · Breakpoint review (360, 420, 480, 600, 768, 1024)
    · Touch target min 44px

VALIDASI:
  · Theme konsisten
  · Typography rapi
  · Accessibility works
  · Test suite passing

================================================================================
📌 ATURAN EKSEKUSI — CHATGPT
================================================================================

1. Baca docs/CHECKPOINT.md SEBELUM eksekusi.
2. Setiap batch = 1 versi bump.
3. Setelah batch selesai → update BACKLOG.md (tandai [x]).
4. Setelah batch selesai → update STATE.md (tambah section).
5. Setelah batch selesai → update CHANGELOG.md (tambah section versi).
6. Setelah batch selesai → update CHECKPOINT.md (kalau ada aturan baru).
7. Test suite WAJIB passing.
8. Kalau ada bug → fix langsung, catat di CHANGELOG.
9. Output = ZIP utuh.
10. Kirim list file yang diubah.

================================================================================
END OF BACKLOG.md — GhostWriter+ v3.3.2
================================================================================