from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def test_release_markers_are_current():
    serve=(ROOT/'serve.py').read_text()
    assert re.search(r'READER_TEMPLATE_VERSION = "3\.3\.4"', serve)
    assert 'gw-reader-template-version" content="3.3.4"' in (ROOT/'templates/reader/reader.html').read_text()
    assert 'gw-viewer-template-version" content="3.3.4"' in (ROOT/'templates/viewer/viewer.html').read_text()

def test_reader_partial_architecture_exists():
    names=['header.html','footer.html','sidebar.html','right-rail.html','mode-popover.html','settings-popover.html','notes-popover.html','stats-modal.html','global-stats-modal.html','properties-modal.html','toast.html','loader.html','reader-container.html','floating-nav.html']
    base=ROOT/'templates/reader/partials'
    assert all((base/n).is_file() for n in names)

def test_reader_accessibility_and_tts_controls():
    html=(ROOT/'templates/reader/partials/header.html').read_text()
    assert 'aria-label' in html and 'id="tts-play"' in html and 'id="tts-pause"' in html

def test_viewer_nested_collapse_and_code_copy():
    js=(ROOT/'templates/viewer/script.js').read_text()
    assert 'code-collapse-wrap' in js and 'code-view-all' in js and 'data-code-action="copy"' in js

def test_gitignore_covers_runtime_data():
    gi=(ROOT/'.gitignore').read_text()
    for token in ('public/','data/','inputs/','attachments/','.deepseek_token','__pycache__/'):
        assert token in gi


def test_reader_empty_state_is_hidden_when_pages_exist():
    css=(ROOT/'templates/reader/style.css').read_text()
    container=(ROOT/'templates/reader/partials/reader-container.html').read_text()
    assert 'id="reader-empty-state"' in container
    assert '.reader-empty-state[hidden]{display:none !important}' in css


def test_reader_settings_match_batch2_blueprint():
    html=(ROOT/'templates/reader/partials/settings-popover.html').read_text()
    assert 'id="effect-select"' in html
    assert 'id="fit-select"' in html
    assert 'id="brightness-range"' in html
    assert 'id="direction-select"' in html
    assert 'id="tts-voice"' in html
    assert 'Focus Mode' not in html
    assert 'Auto-hide controls' not in html


def test_server_refreshes_same_version_stale_reader_markup():
    src=(ROOT/'serve.py').read_text()
    for token in ('required_runtime_markers', 'brightness-range', 'direction-select', 'tts-voice', 'reader-empty-state', 'data-menu-action="settings"'):
        assert token in src
