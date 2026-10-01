from pathlib import Path
import re
from importers.chat_importer import _export_data
from importers.chat_url_importer import detect_platform
from tools.dist_index import scan_dist

ROOT = Path(__file__).resolve().parents[1]


def test_export_data_accepts_output_dir():
    import tempfile
    from pathlib import Path
    data={'title':'Temp Export','messages':[{'role':'user','content':'Hi','timestamp':''}]}
    with tempfile.TemporaryDirectory() as td:
        assert _export_data(data,'test',1,output_dir=Path(td))
        assert (Path(td)/'temp-export'/'index.html').is_file()


def test_dist_scan_preserves_display_title_and_size_kb():
    items=scan_dist()
    for item in items:
        assert 'size_kb' in item
        assert 'title' in item


def test_viewer_template_version_marker():
    html=(ROOT/'templates/viewer/viewer.html').read_text()
    assert 'gw-viewer-template-version' in html
    assert re.search(r'content="3\.\d+\.\d+"', html)


def test_viewer_features_are_declared():
    html=(ROOT/'templates/viewer/partials/header.html').read_text()
    js=(ROOT/'templates/viewer/script.js').read_text()
    for token in ('export-md','export-json','role-user','role-ai','collapse-all'):
        assert token in html
    assert 'function exportChatMarkdown' in js
    assert 'function exportChatJSON' in js
    assert 'new RegExp' in js


def test_landing_features_are_declared():
    src=(ROOT/'tools/dist_index.py').read_text()
    for token in ('gw-recent','gw-favorites','gw-view','favorite-btn','view-grid','keyboard-active'):
        assert token in src


def test_reader_enhancements_are_declared():
    html=(ROOT/'templates/reader/reader.html').read_text()
    header=(ROOT/'templates/reader/partials/header.html').read_text()
    js=(ROOT/'templates/reader/script.js').read_text()
    for token in ('global-stats','export-annotations-json','export-annotations-md'):
        assert token in html or token in header
    # TTS is intentionally kept in the dedicated control bar; no duplicate menu actions.
    assert 'id="tts-play"' in header
    assert 'data-menu-action="tts"' not in header
    assert 'speechSynthesis' in js
    assert 'exportAnnotations' in js
    assert 'globalStats' in js


def test_extended_platform_hosts():
    for url, name in {
        'https://www.perplexity.ai/search/test':'Perplexity',
        'https://copilot.microsoft.com/shares/test':'Copilot',
        'https://grok.com/share/test':'Grok',
        'https://x.ai/share/test':'Grok',
        'https://poe.com/s/test':'Poe',
        'https://you.com/search?q=test':'You.com',
    }.items():
        assert detect_platform(url) == name


def test_current_release_version_markers_exist():
    checkpoint=(ROOT/'docs/CHECKPOINT.md').read_text()
    assert 'CONSTANT' in checkpoint
    serve=(ROOT/'serve.py').read_text(); m=re.search(r'READER_TEMPLATE_VERSION = "([^"]+)"', serve); assert m and m.group(1) == '3.3.4'
    assert 'content="3.3.4"' in (ROOT/'templates/reader/reader.html').read_text()
