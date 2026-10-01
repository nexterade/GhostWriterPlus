"""GhostWriter+ canonical filesystem layout.

All application code resolves paths from this module instead of the process CWD.
This is the primary guard against FileNotFoundError when launched from Termux,
file managers, or another working directory.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUTS = ROOT / "inputs"
PUBLIC = ROOT / "public"
READERS = PUBLIC / "readers"
COMICS = PUBLIC / "comics"
HISTORY = PUBLIC / "history"
DATA = ROOT / "data"
CHAT_DATA = DATA / "chats"
EBOOK_DATA = DATA / "ebooks"
COMIC_DATA = DATA / "comics"
BACKUPS = DATA / "backups"
TEMP = DATA / "tmp"
TEMPLATES = ROOT / "templates"

STANDARD_DIRS = (
    INPUTS, PUBLIC, READERS, COMICS, HISTORY,
    DATA, CHAT_DATA, EBOOK_DATA, COMIC_DATA, BACKUPS, TEMP,
)


def ensure_layout() -> None:
    for path in STANDARD_DIRS:
        path.mkdir(parents=True, exist_ok=True)


def project_path(value) -> Path:
    """Resolve a project-relative path without ever depending on cwd."""
    p = Path(value).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (ROOT / p).resolve()


def input_path(value) -> Path:
    return project_path(value)
