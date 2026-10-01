"""Interactive prompt helpers shared by CLI and importers."""
CANCEL_SENTINEL = "__CANCEL__"

def is_cancel(text):
    return str(text or "").strip().lower() in {"0", "q", "quit", "cancel", "batal"}

def prompt(text, default=""):
    from tools.theme import C, get_theme
    t=get_theme()
    hint=f" {C.GRAY}[default: {default} | 0=batal]{C.RESET}" if default else f" {C.GRAY}[0=batal]{C.RESET}"
    raw=input(f"{C.ACCENT}->{C.RESET} {C.WHITE}{text}{C.RESET}{hint}: " if t.enabled else f"{text}{hint}: ").strip()
    if is_cancel(raw):
        return CANCEL_SENTINEL
    return default if raw == "" else raw

def prompt_yes_no(text, default="y"):
    value=prompt(text, default=default)
    if is_cancel(value):
        return False
    return str(value).strip().lower() in {"y","yes","ya"}
