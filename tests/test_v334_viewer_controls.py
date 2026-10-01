from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_viewer_header_controls_bound_before_async_pipeline():
    js = (ROOT / "templates/viewer/script.js").read_text()
    refs = [
        'const helpOverlayEarly = document.getElementById("help-modal-overlay")',
        'const helpToggleEarly = document.getElementById("help-toggle")',
        'const headerMenuToggleEarly = document.getElementById("header-menu-toggle")',
        'sidebarToggle?.addEventListener("click"',
        'helpToggleEarly?.addEventListener("click"',
        'headerMenuToggleEarly?.addEventListener("click"',
    ]
    for ref in refs:
        assert ref in js
    # Critical bindings must occur before the first asynchronous sidebar step.
    assert js.index('sidebarToggle?.addEventListener("click"') < js.index('await safeStep("sidebar"')


def test_viewer_sidebar_toggle_is_visible_by_default():
    css = (ROOT / "templates/viewer/style.css").read_text()
    start = css.index('.sidebar-toggle {')
    end = css.index('}', start)
    block = css[start:end]
    assert 'display: inline-flex' in block


def test_viewer_template_bumped_for_regeneration():
    html = (ROOT / "templates/viewer/viewer.html").read_text()
    assert 'gw-viewer-template-version" content="3.3.4"' in html
