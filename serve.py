import os
import sys
import argparse
import json
import http.server
import socketserver
import subprocess
import webbrowser
from functools import partial
from pathlib import Path
from core.paths import ROOT, PUBLIC
from importers._reader_common import render_reader_html


DEFAULT_PORT = 8000
PUBLIC_DIR = str(PUBLIC)


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ACCENT = "\033[38;5;117m"
    GREEN = "\033[38;5;114m"
    YELLOW = "\033[38;5;221m"
    RED = "\033[38;5;203m"
    GRAY = "\033[38;5;245m"
    WHITE = "\033[38;5;255m"


def _supports_ansi() -> bool:
    if not sys.stdout.isatty():
        return False
    return os.environ.get("TERM", "") not in ("", "dumb")


ANSI = _supports_ansi()


def _c(code: str, text: str) -> str:
    if not ANSI:
        return text
    return f"{code}{text}{C.RESET}"


def is_termux() -> bool:
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix


def open_browser(url: str) -> bool:
    try:
        if is_termux():
            subprocess.Popen(
                ["termux-open-url", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        else:
            return webbrowser.open(url)
    except Exception as e:
        print(_c(C.RED, f"  ✗ Gagal buka browser: {e}"))
        return False


def print_banner(port: int, public_path: str):
    print()
    print(_c(C.ACCENT, "━" * 52))
    print(_c(C.BOLD + C.WHITE, "  👻  GhostWriter+ — Local Server"))
    print(_c(C.ACCENT, "━" * 52))
    print()
    print(f"  {_c(C.GRAY, '📂 Serving:')} {_c(C.WHITE, public_path)}")
    print(f"  {_c(C.GRAY, '🔌 Port:')}    {_c(C.WHITE, str(port))}")
    print(f"  {_c(C.GRAY, '🌐 URL:')}     {_c(C.ACCENT, f'http://localhost:{port}/')}")
    print()
    print(_c(C.ACCENT, "━" * 52))
    print(_c(C.GRAY, "  Server berjalan... (Ctrl+C buat stop)"))
    print(_c(C.ACCENT, "━" * 52))
    print()


def prompt_open_browser(url: str, auto_open: bool) -> None:
    if auto_open:
        print(_c(C.ACCENT, "  🌐 Membuka browser..."))
        ok = open_browser(url)
        if ok:
            print(_c(C.GREEN, "  ✓ Browser dibuka"))
        else:
            print(_c(C.YELLOW, "  ⚠ Gagal auto-open. Buka manual:"))
            print(_c(C.WHITE, f"    {url}"))
        print()
        return

    try:
        if ANSI:
            resp = input(
                f"  {C.ACCENT}→{C.RESET} "
                f"{C.WHITE}Buka browser sekarang?{C.RESET} "
                f"{C.GRAY}[Y/n]{C.RESET}: "
            ).strip().lower()
        else:
            resp = input("  Buka browser sekarang? [Y/n]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        return

    if resp in ("", "y", "yes"):
        print(_c(C.ACCENT, "  🌐 Membuka browser..."))
        ok = open_browser(url)
        if ok:
            print(_c(C.GREEN, "  ✓ Browser dibuka"))
        else:
            print(_c(C.YELLOW, "  ⚠ Gagal auto-open. Buka manual:"))
            print(_c(C.WHITE, f"    {url}"))
    else:
        print(_c(C.GRAY, "  ⏭ Skip buka browser."))
        print(_c(C.WHITE, f"  Buka manual: {url}"))
    print()


READER_TEMPLATE_VERSION = "3.3.4"
VIEWER_TEMPLATE_VERSION = "3.3.4"


def migrate_legacy_reader_htmls(public_path: Path) -> int:
    """Refresh stale generated reader HTML from its embedded READER_DATA.

    Reader pages are generated artifacts.  Older files must not stay on an
    old JS/CSS runtime merely because the user did not re-import the source
    ebook after a reader bugfix.  If the embedded payload is recoverable,
    regenerate the same index.html through the canonical template.
    """
    fixed = 0
    for section in ("readers", "comics"):
        root = public_path / section
        if not root.is_dir():
            continue
        for html in root.glob("*/index.html"):
            try:
                text = html.read_text(encoding="utf-8")
                marker = f'<meta name="gw-reader-template-version" content="{READER_TEMPLATE_VERSION}">'
                # A matching version marker alone is not sufficient: generated
                # reader HTML can carry a stale template from an earlier build
                # of the same release. Refresh when the current reader contract
                # is missing, while keeping already-current files untouched.
                required_runtime_markers = (
                    'id="brightness-range"',
                    'id="direction-select"',
                    'id="tts-voice"',
                    'id="reader-empty-state"',
                    'data-menu-action="settings"',
                )
                if (
                    marker in text
                    and "window.READER_DATA = " in text
                    and all(token in text for token in required_runtime_markers)
                ):
                    continue

                prefix = "window.READER_DATA = "
                start = text.find(prefix)
                if start < 0:
                    # Handle the pre-v3.0.4 declaration too.
                    prefix = "const READER_DATA = "
                    start = text.find(prefix)
                if start < 0:
                    continue
                start += len(prefix)
                end = text.find(";</script>", start)
                if end < 0:
                    continue

                payload = json.loads(text[start:end])
                if not isinstance(payload, dict) or not payload.get("sections"):
                    continue
                type_ = str(payload.get("type") or ("comic" if section == "comics" else "ebook"))
                if type_ not in ("ebook", "comic"):
                    type_ = "ebook"

                render_reader_html(str(ROOT / "templates" / "reader" / "reader.html"), str(html), payload, type_)
                fixed += 1
            except (OSError, UnicodeError, ValueError, TypeError, KeyError):
                continue
    return fixed


def migrate_legacy_viewer_htmls(public_path: Path) -> int:
    """Inject a runtime watchdog into stale generated viewer pages."""
    fixed = 0
    root = public_path / "history"
    if not root.is_dir():
        return fixed
    marker = f'<meta name="gw-viewer-runtime-version" content="{VIEWER_TEMPLATE_VERSION}">'
    watchdog = """<script>
(function(){
  var max=12000;
  function reveal(reason){
    var l=document.getElementById("gw-loader");
    if(!l || l.classList.contains("fade-complete")) return;
    console.warn("[GW] Loader watchdog reveal:",reason);
    var f=document.getElementById("gw-loader-fill"),p=document.getElementById("gw-loader-percent"),t=document.getElementById("gw-loader-text");
    if(f)f.style.width="100%"; if(p)p.textContent="100%"; if(t)t.textContent="Siap";
    l.classList.add("hidden"); setTimeout(function(){l.classList.add("fade-complete")},450);
  }
  setTimeout(function(){reveal("legacy viewer initialization timeout")},max);
})();
</script>"""
    for html in root.glob("*/index.html"):
        try:
            text = html.read_text(encoding="utf-8")
            if marker in text or 'id="gw-loader"' not in text:
                continue
            head_end = text.lower().find("</head>")
            if head_end < 0:
                continue
            text = text[:head_end] + marker + watchdog + text[head_end:]
            html.write_text(text, encoding="utf-8")
            fixed += 1
        except (OSError, UnicodeError):
            continue
    return fixed


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        msg = format % args
        if any(ext in msg for ext in (".js", ".css", ".woff", ".png", ".ico", ".svg")):
            return
        print(_c(C.GRAY, f"  {msg}"))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()


def run_server(port: int, public_path, auto_open: bool):
    """Run the local server from a canonical Path.

    Accept both ``Path`` and ``str`` for callers.  Older versions passed a
    string from ``main()`` and then called ``.resolve()`` on it, which caused
    an AttributeError before the HTTP server could even start.
    """
    public_path = Path(public_path).expanduser().resolve()
    actual_serving_path = str(public_path)

    handler = partial(QuietHandler, directory=str(public_path))
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            url = f"http://localhost:{port}/"
            print_banner(port, actual_serving_path)

            if not auto_open:
                prompt_open_browser(url, auto_open=False)

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print()
                print(_c(C.YELLOW, "  ⏹ Server dihentikan. Sampai jumpa! 👻"))
                print()
    except OSError as e:
        if "Address already in use" in str(e) or "in use" in str(e).lower():
            print()
            print(_c(C.RED, f"  ✗ Port {port} udah dipake proses lain."))
            print(_c(C.GRAY, "    Coba:"))
            print(_c(C.WHITE, f"      python3 serve.py --port {port + 1}"))
            print(_c(C.GRAY, "    Atau kill proses lama:"))
            print(_c(C.WHITE, f"      lsof -ti:{port} | xargs kill"))
            print()
            sys.exit(1)
        else:
            raise


def main():
    parser = argparse.ArgumentParser(
        prog="serve.py",
        description="Serve GhostWriter+ output folder di browser."
    )
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT,
                        help=f"Port server (default: {DEFAULT_PORT})")
    parser.add_argument("--no-open", action="store_true",
                        help="Jangan auto-open browser, tanya dulu")
    args = parser.parse_args()

    public_path = Path(PUBLIC_DIR)
    if not public_path.is_dir():
        print()
        print(_c(C.RED, f"  ✗ Folder '{PUBLIC_DIR}/' gak ada."))
        print(_c(C.GRAY, "    Render dulu lewat:"))
        print(_c(C.WHITE, "      python3 main.py"))
        print()
        sys.exit(1)

    fixed_readers = migrate_legacy_reader_htmls(public_path)
    if fixed_readers:
        print(_c(C.GREEN, f"  ✓ Memperbarui {fixed_readers} reader lama ke template {READER_TEMPLATE_VERSION}."))
    fixed_viewers = migrate_legacy_viewer_htmls(public_path)
    if fixed_viewers:
        print(_c(C.GREEN, f"  ✓ Memperbaiki {fixed_viewers} viewer lama dengan loader watchdog {VIEWER_TEMPLATE_VERSION}."))

    if not (public_path / "index.html").is_file():
        print()
        print(_c(C.YELLOW, f"  ⚠ Folder '{PUBLIC_DIR}/' ada tapi index.html belum kebentuk."))
        print(_c(C.GRAY, "    Coba render atau sync dulu:"))
        print(_c(C.WHITE, "      python3 main.py"))
        print(_c(C.WHITE, "      python3 sync.py"))
        print()
        input(_c(C.GRAY, "  [Enter] buat lanjut / Ctrl+C buat batal... "))

    auto_open = not args.no_open
    run_server(args.port, str(public_path), auto_open=auto_open)


if __name__ == "__main__":
    main()