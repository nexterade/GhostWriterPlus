from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]


def render_reader():
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))
    return env.get_template("reader/reader.html").render(
        TITLE="Test Reader", SUBTITLE="Book", TOTAL_PAGES=2,
        FAVICON_LINK="", LOGO_SVG="<svg></svg>",
        READER_JSON='{"title":"Test Reader","type":"ebook","sections":[{"src":"p1.jpg"},{"src":"p2.jpg"}]}',
    )


def test_reader_exposes_only_two_modes():
    html = render_reader()
    assert 'data-mode="horizontal"' in html
    assert 'data-mode="vertical"' in html
    for old in ('data-mode="novel"', 'data-mode="comic"', 'data-mode="manga"', 'data-mode="webtoon"'):
        assert old not in html


def test_reader_mode_source_is_two_state():
    js = (ROOT / "templates/reader/script.js").read_text(encoding="utf-8")
    assert "mode==='vertical'" in js
    assert "mode==='horizontal'" in js
    assert "enterFocus" not in js
    assert "exitFocus" not in js
    assert "mode==='manga'" not in js
    assert "mode==='novel'" not in js


def test_reader_header_is_brand_plus_floating_title():
    html = render_reader()
    assert 'reader-brand-name' in html
    assert 'GhostReader+' in html
    assert 'header-title' in html
    assert 'header-subtitle' in html
    assert 'id="reader-mode-label"' not in html
    assert 'reader-chrome' in html
    assert 'id="sidebar-toggle"' in html
    assert 'id="header-menu-toggle"' in html


def test_vertical_and_rtl_layout_exist():
    css = (ROOT / "templates/reader/style.css").read_text(encoding="utf-8")
    assert ".reader-app.vertical" in css
    assert ".reader-app.rtl" in css
