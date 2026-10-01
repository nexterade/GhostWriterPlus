import json
import zipfile
from pathlib import Path

from importers.chatgpt_export_importer import inspect_zip, import_export_zip


def _make_export(tmp_path: Path, conversations):
    root = tmp_path / "export"
    root.mkdir()
    (root / "conversations.json").write_text(json.dumps(conversations, ensure_ascii=False), encoding="utf-8")
    (root / "chat.html").write_text("<html>export metadata</html>", encoding="utf-8")
    (root / "model_comparisons.dat").write_bytes(b"placeholder")
    zpath = tmp_path / "chatgpt-export.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in root.iterdir():
            zf.write(p, p.name)
    return zpath


def test_detects_official_chatgpt_export_zip(tmp_path):
    zpath = _make_export(tmp_path, [{"title": "Halo", "mapping": {}}])
    meta = inspect_zip(zpath)
    assert meta["is_chatgpt_export"] is True
    assert meta["conversation_files"] == ["conversations.json"]
    assert meta["html_files"] == ["chat.html"]
    assert meta["dat_files"] == ["model_comparisons.dat"]


def test_imports_conversations_json_from_zip(tmp_path):
    conversations = [{
        "title": "ChatGPT ZIP Test",
        "create_time": 1720000000,
        "mapping": {
            "root": {"id": "root", "message": None},
            "u": {"id": "u", "parent": "root", "message": {
                "author": {"role": "user"},
                "content": {"content_type": "text", "parts": ["Halo"]},
                "create_time": 1720000001,
            }},
            "a": {"id": "a", "parent": "u", "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": ["Halo juga"]},
                "create_time": 1720000002,
            }},
        },
    }]
    zpath = _make_export(tmp_path, conversations)
    parser, tempdir, meta = import_export_zip(zpath)
    try:
        convos = parser.list_conversations()
        assert len(convos) == 1
        assert convos[0]["title"] == "ChatGPT ZIP Test"
        data = parser.parse(0)
        assert [m["role"] for m in data["messages"]] == ["user", "assistant"]
        assert data["messages"][0]["content"] == "Halo"
    finally:
        tempdir.cleanup()


def test_rejects_zip_path_traversal(tmp_path):
    zpath = tmp_path / "evil.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("../conversations.json", "[]")
    try:
        import_export_zip(zpath)
    except ValueError as exc:
        assert "tidak aman" in str(exc).lower()
    else:
        raise AssertionError("path traversal ZIP harus ditolak")


def test_viewer_loader_has_watchdog_and_current_version():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    html = (root / "templates" / "viewer" / "viewer.html").read_text(encoding="utf-8")
    script = (root / "templates" / "viewer" / "script.js").read_text(encoding="utf-8")
    assert 'gw-viewer-template-version" content="3.3.4"' in html
    assert 'Loader watchdog reveal' in script
    assert 'Progress.setTask("reveal", true);' in script
