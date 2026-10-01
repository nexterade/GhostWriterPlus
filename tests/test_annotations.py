import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_payload_has_stable_book_identity_and_locations():
    import sys
    sys.path.insert(0, str(ROOT))
    from importers._reader_common import build_payload
    payload = build_payload('Book', 'Author', [
        {'page': 1, 'type': 'text', 'resource': 'chapter-1.xhtml', 'content': 'Hello world'},
        {'page': 2, 'type': 'image', 'src': 'images/0002.jpg'},
    ])
    assert payload['book_id'].startswith('sha256:')
    assert len(payload['book_id']) == 71
    assert payload['sections'][0]['anchor']['scheme'] == 'text'
    assert payload['sections'][1]['anchor']['scheme'] == 'image'
    assert payload['annotation_schema'] == 1

def test_annotation_runtime_uses_indexeddb_and_content_anchors():
    js = (ROOT / 'templates/reader/script.js').read_text(encoding='utf-8')
    assert "ghostreader-annotations-v1" in js
    assert 'objectStore(ANNO_STORE)' in js
    assert "type:'bookmark'" in js
    assert "type:'highlight'" in js
    assert "type:'note'" in js
    assert 'prefix' in js and 'suffix' in js
    assert 'pageLocation' in js
    assert 'resource:sec.resource||sec.src' in js

def test_legacy_annotations_are_migrated():
    js = (ROOT / 'templates/reader/script.js').read_text(encoding='utf-8')
    assert 'migrateLegacyAnnotations' in js
    assert 'localStorage.removeItem(`${keyBase}-bookmarks`)' in js
    assert 'localStorage.removeItem(`${keyBase}-notes-${n.i+1}`)' in js
