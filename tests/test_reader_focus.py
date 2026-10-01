from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]


def render_reader():
    env = Environment(loader=FileSystemLoader([str(ROOT / "templates"), str(ROOT / "templates" / "_shared")]))
    return env.get_template("reader/reader.html").render(
        TITLE="Test", SUBTITLE="Novel", TYPE_CLASS="ebook", TYPE_LABEL="EBOOK",
        TOTAL_PAGES=1, LOGO_SVG="", FAVICON_LINK="",
        READER_JSON='{"type":"ebook","title":"Test","sections":[]}',
    )


def test_reader_template_renders_without_jinja_comment_collision():
    html = render_reader()
    import re
    m = re.search(r'gw-reader-template-version" content="([^"]+)"', html)
    assert m
    assert m.group(1).startswith('3.')
    assert "reader-app" in html


def test_reader_has_no_focus_or_browser_fullscreen_dependency():
    html = render_reader()
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    for token in ("focus-toggle", "focus-exit", "focus-bottom", "focus-mode"):
        assert token not in html
        assert token not in js
        assert token not in css
    for token in ("requestFullscreen", "exitFullscreen", "fullscreenchange"):
        assert token not in js


def test_reader_matches_viewer_chrome_and_has_no_hide_controls():
    html = render_reader()
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    assert 'id="sidebar-toggle"' in html
    assert 'id="header-menu-toggle"' in html
    assert 'id="reader-menu"' in html
    assert 'data-menu-action="bookmark"' in html
    assert 'data-menu-action="pages"' in html
    assert 'data-menu-action="notes"' in html
    assert 'data-menu-action="mode"' in html
    assert 'data-menu-action="settings"' in html
    assert 'data-menu-action="stats"' in html
    assert 'data-menu-action="properties"' in html
    assert 'data-menu-section="navigation"' in html
    assert 'data-menu-section="reading"' in html
    assert 'data-menu-section="export"' in html
    assert 'menu-section-toggle' in html
    assert 'data-menu-action="tts"' not in html
    assert 'id="library-drawer"' in html
    assert 'id="page-drawer"' in html
    assert 'sidebar-stat-progress' in html
    assert 'progress-slider' in html
    assert 'bottom-actions' not in html
    assert 'chrome-hidden' not in html
    assert 'chrome-hidden' not in js
    assert 'chrome-hidden' not in css
    assert 'function reveal' not in js
    assert 'reader-sidebar' in css
    assert 'reader-page-rail' in css
    assert '#main-header' in css


def test_reader_mobile_chrome_keeps_slider_in_flow_after_header():
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    assert ".reader-app{height:100svh;min-height:100svh;display:flex;" in css
    assert ".reader-main-area{flex:1 1 auto;min-width:0;min-height:0;height:100%;display:flex;flex-direction:column;" in css
    assert ".reader-main{flex:1 1 auto;min-width:0;min-height:0;height:auto;position:relative;overflow:hidden}" in css
    assert ".reader-bottom{position:relative;left:auto;right:auto;bottom:auto;flex:0 0 auto;" in css
