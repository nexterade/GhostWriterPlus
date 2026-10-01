from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]

def render_reader():
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))
    return env.get_template("reader/reader.html").render(
        TITLE="Test", SUBTITLE="Book", TOTAL_PAGES=2, FAVICON_LINK="", LOGO_SVG="",
        READER_JSON='{"title":"Test","type":"ebook","sections":[{"type":"text","content":"hello"},{"type":"image","src":"p.jpg"}]}',
    )

def test_reader_prioritizes_page_flip_brightness_annotations():
    html = render_reader()
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    assert 'value="curl">Page Flip' in html
    assert 'brightness-range' in html
    assert 'data-menu-action="notes"' in html
    assert 'data-menu-action="bookmark"' in html
    assert 'data-menu-action="pages"' in html
    assert 'highlight-selection' in html
    assert 'applyBrightness' in js
    assert 'addHighlight' in js
    assert 'bookmarks' in js

def test_reader_supports_text_and_image_sections():
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    assert "sec.type==='text'" in js
    assert "else{const img=makeImg(i)" in js


def test_reader_loader_has_no_stale_mode_label_dependency():
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    html = render_reader()
    assert "#reader-mode-label" not in js
    assert "modeLabel.textContent" not in js
    assert "reader-info-modal" in html
    assert "Statistik baca" in html
    assert "Properties buku" in html


def test_payload_keeps_book_properties():
    from importers._reader_common import build_payload
    payload = build_payload("Book", "Author", [{"type": "text", "content": "x"}], {"format": "EPUB", "source_name": "book.epub", "size_bytes": 123})
    assert payload["properties"]["format"] == "EPUB"
    assert payload["properties"]["source_name"] == "book.epub"
    assert payload["properties"]["page_count"] == 1


def test_page_flip_supports_text_curl_faces_and_landscape_spread():
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    assert "function setCurlFace" in js
    assert "curl-content" in js
    assert "function isSpread" in js
    assert "orientation: landscape" in js
    assert ".spread-slot" in css


def test_reader_theme_tokens_are_defined():
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    assert "--viewer-accent:var(--accent)" in css
    assert "--viewer-accent-glow" in css


def test_reader_has_no_legacy_floating_header_or_tap_hide_css():
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    docs = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "#reader-header" not in css
    assert ".reader-heading" not in css
    assert ".reader-menu{position:fixed" not in css
    assert "tap-to-hide" in docs
