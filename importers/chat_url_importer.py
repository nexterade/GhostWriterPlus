"""Import public/shared chat links from common AI platforms.

This module intentionally uses the public share page only; it does not require
an account token or private API access.  The share page is inspected for the
structured JSON that the platform embeds for its client, then normalized via
JSONChatParser.  A conservative HTML-text fallback is provided when a site
only exposes server-rendered text.
"""

import html
import json
import re
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from parsers.json_parser import JSONChatParser


PLATFORM_HOSTS = {
    "chatgpt.com": "ChatGPT",
    "chat.openai.com": "ChatGPT",
    "claude.ai": "Claude",
    "gemini.google.com": "Gemini",
    "chat.deepseek.com": "DeepSeek",
    "deepseek.com": "DeepSeek",
    "perplexity.ai": "Perplexity",
    "copilot.microsoft.com": "Copilot",
    "grok.com": "Grok",
    "x.ai": "Grok",
    "poe.com": "Poe",
    "you.com": "You.com",
}


def normalize_share_url(value: str) -> str:
    """Normalize URLs copied from Android/browser share dialogs.

    Clipboard content can contain surrounding quotes/backticks, zero-width
    characters, non-breaking spaces, or omit the scheme when copied from a
    browser UI. Those should not make an otherwise valid public URL fail the
    initial parser.
    """
    text = str(value or "")
    text = html.unescape(text)
    text = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "").replace("\ufeff", "")
    text = text.replace("\u00a0", " ").strip()
    text = text.strip('\"\'`<>')
    text = re.sub(r"\s+", "", text)
    if text and not re.match(r"^[a-z][a-z0-9+.-]*://", text, flags=re.I):
        if text.lower().startswith("www."):
            text = "https://" + text
    return text


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


class _RoleMessageExtractor(HTMLParser):
    """Best-effort DOM extractor for share pages that expose readable HTML
    but hide/reshape their JSON state.

    It deliberately looks for semantic role attributes first, then conservative
    class/id/test-id hints. This avoids treating navigation/footer text as chat
    content while still recovering static/server-rendered share pages.
    """
    ROLE_KEYS = {"data-message-author-role", "data-role", "data-author-role", "aria-label", "role"}
    ROLE_WORDS = {
        "user": "user", "human": "user", "you": "user", "prompt": "user",
        "assistant": "assistant", "ai": "assistant", "bot": "assistant",
        "claude": "assistant", "chatgpt": "assistant", "gemini": "assistant",
        "deepseek": "assistant",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, str]] = []
        self.skip_depth = 0

    @classmethod
    def _role_from_attrs(cls, attrs: List[Tuple[str, Optional[str]]]) -> Optional[str]:
        amap = {str(k).lower(): (v or "") for k, v in attrs}
        values: List[str] = []
        for key in cls.ROLE_KEYS:
            if key in amap:
                values.append(amap[key])
        values.extend(amap.get(k, "") for k in ("class", "id", "data-testid", "data-test-id"))
        joined = " ".join(values).lower()
        # Strong semantic attributes first.
        for key in ("data-message-author-role", "data-role", "data-author-role", "aria-label", "role"):
            val = amap.get(key, "").lower()
            if val in cls.ROLE_WORDS:
                return cls.ROLE_WORDS[val]
            for word, role in cls.ROLE_WORDS.items():
                if re.search(rf"(?<![a-z]){re.escape(word)}(?![a-z])", val):
                    return role
        # Conservative class/id fallback.
        if re.search(r"(?:^|[-_ ])(?:user|human)(?:[-_ ]|$)|message[-_ ]?user", joined):
            return "user"
        if re.search(r"(?:^|[-_ ])(?:assistant|ai|bot)(?:[-_ ]|$)|message[-_ ]?assistant", joined):
            return "assistant"
        return None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header"}:
            self.skip_depth += 1
            self.stack.append({"tag": tag, "role": None, "parts": [], "skipped": True})
            return
        role = self._role_from_attrs(attrs)
        self.stack.append({"tag": tag, "role": role, "parts": [], "skipped": self.skip_depth > 0})
        if role is not None and self.skip_depth == 0:
            # Capture this node only. Nested role nodes are filtered/deduped later.
            pass

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if not self.stack:
            return
        # HTMLParser can see malformed markup; close the nearest matching frame.
        idx = len(self.stack) - 1
        while idx >= 0 and self.stack[idx]["tag"] != tag:
            idx -= 1
        if idx < 0:
            return
        frame = self.stack[idx]
        self.stack = self.stack[:idx]
        if frame["skipped"]:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if frame["role"] and self.skip_depth == 0:
            text = re.sub(r"[ \t\f\v]+", " ", " ".join(frame["parts"]))
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if len(text) >= 2:
                self.messages.append({"role": frame["role"], "content": text, "timestamp": ""})

    def handle_data(self, data: str) -> None:
        if not self.stack or self.skip_depth:
            return
        value = data.strip()
        if not value:
            return
        # Feed text to all open frames so an outer semantic message survives
        # nested spans/divs.
        for frame in self.stack:
            if not frame["skipped"]:
                frame["parts"].append(value)


def _extract_role_messages(page: str) -> List[Dict[str, str]]:
    parser = _RoleMessageExtractor()
    try:
        parser.feed(page)
        parser.close()
    except Exception:
        return []
    rows: List[Dict[str, str]] = []
    seen = set()
    for msg in parser.messages:
        text = re.sub(r"\s+", " ", msg.get("content", "")).strip()
        # Ignore tiny UI labels and obvious chrome.
        if len(text) < 3:
            continue
        key = (msg["role"], text)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"role": msg["role"], "content": text, "timestamp": ""})
    # Prefer the longest unique candidate when nested role-bearing nodes
    # produce the same text with small wrappers.
    compact: List[Dict[str, str]] = []
    for msg in rows:
        duplicate = False
        for other in rows:
            if msg is other or msg["role"] != other["role"]:
                continue
            a, b = msg["content"], other["content"]
            if a != b and (a in b or b in a) and len(a) < len(b) * 0.92:
                if a in b:
                    duplicate = True
                    break
        if not duplicate:
            compact.append(msg)
    return compact


def detect_platform(url: str) -> str:
    host = (urlparse(url).hostname or "").lower().split(":", 1)[0]
    for domain, name in PLATFORM_HOSTS.items():
        if host == domain or host.endswith("." + domain):
            return name
    return "Generic"


def _json_script_blocks(page: str) -> Iterable[str]:
    for m in re.finditer(
        r"<script[^>]*>(.*?)</script>", page, flags=re.I | re.S
    ):
        block = m.group(1).strip()
        if not block:
            continue
        yield html.unescape(block)


def _extract_embedded_json(block: str) -> List[Any]:
    """Extract JSON objects from ordinary and Next/React Flight scripts."""
    out: List[Any] = []
    normalized_variants = [block, html.unescape(block)]

    # Next.js/React Flight commonly serializes payloads inside a quoted JS
    # string, e.g. self.__next_f.push([1,"...{\"mapping\":...}"]).
    # Decode those strings before scanning for balanced JSON objects.
    for m in re.finditer(r'\[(?:1|3),\s*("(?:\\.|[^"\\])*")\s*\]', block, flags=re.S):
        try:
            decoded = json.loads(m.group(1))
            if isinstance(decoded, str):
                normalized_variants.append(decoded)
        except Exception:
            pass

    seen = set()
    for normalized in normalized_variants:
        if normalized in seen:
            continue
        seen.add(normalized)
        for marker in ('"mapping"', '"chat_messages"', '"messages"', '"turns"'):
            cursor = 0
            while True:
                hit = normalized.find(marker, cursor)
                if hit < 0:
                    break
                start = normalized.rfind('{', max(0, hit - 20000), hit)
                if start >= 0:
                    blob = _balanced_json(normalized, start)
                    if blob:
                        try:
                            obj = json.loads(blob)
                            if obj not in out:
                                out.append(obj)
                        except Exception:
                            pass
                cursor = hit + len(marker)
    return out


def _decode_json_blocks(page: str) -> List[Any]:
    candidates: List[Any] = []
    for block in _json_script_blocks(page):
        # JSON scripts are the cleanest path.
        stripped = block.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                candidates.append(json.loads(stripped))
                continue
            except Exception:
                pass

        # Next/React state is sometimes assigned rather than using a JSON
        # script type. Extract the largest balanced JSON object/array.
        candidates.extend(_extract_embedded_json(stripped))

        for marker in ("__NEXT_DATA__", "__INITIAL_STATE__", "__APOLLO_STATE__"):
            if marker not in stripped:
                continue
            start = min([p for p in (stripped.find("{"), stripped.find("[")) if p >= 0], default=-1)
            if start < 0:
                continue
            blob = _balanced_json(stripped, start)
            if blob:
                try:
                    candidates.append(json.loads(blob))
                except Exception:
                    pass
    return candidates


def _balanced_json(text: str, start: int) -> str:
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return ""


def _walk(value: Any, path: str = "root") -> Iterable[Tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from _walk(child, f"{path}[{i}]")


def _looks_like_message(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    keys = set(item.keys())
    return bool(keys & {"role", "author", "sender", "content", "text", "message"})


def _find_structured_candidates(obj: Any) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []
    seen = set()
    for _, value in _walk(obj):
        if isinstance(value, dict):
            if "chat_messages" in value or "mapping" in value:
                marker = id(value)
                if marker not in seen:
                    found.append(value); seen.add(marker)
            for key in ("messages", "turns", "chat", "conversation"):
                raw = value.get(key)
                if isinstance(raw, list) and raw and sum(_looks_like_message(x) for x in raw[:8]) >= 1:
                    candidate = {
                        "title": value.get("title") or value.get("name") or value.get("conversation_title") or "",
                        "created_at": value.get("created_at") or value.get("create_time") or "",
                        "messages": raw,
                    }
                    found.append(candidate)
    return found


def _parser_from_object(obj: Dict[str, Any], base_url: str, platform: str) -> Optional[Dict[str, Any]]:
    parser = JSONChatParser(base_url)
    parser.raw_data = obj
    parser.base_dir = "."
    try:
        data = parser.parse()
    except Exception:
        return None
    messages = data.get("messages") or []
    if not messages:
        return None
    title = str(data.get("title") or "").strip()
    if not title or title.casefold() in {"untitled", "document", "obrolan ai"}:
        title = f"{platform} Shared Chat"
    data["title"] = title
    data["source_url"] = base_url
    data["platform"] = platform
    return data


def _html_fallback(page: str, title: str, platform: str, url: str) -> Optional[Dict[str, Any]]:
    extractor = _HTMLTextExtractor()
    try:
        extractor.feed(page)
    except Exception:
        return None
    lines: List[str] = []
    seen = set()
    for text in extractor.parts:
        if len(text) < 2 or text in seen:
            continue
        seen.add(text)
        lines.append(text)
    if not lines:
        return None
    # Avoid turning the whole browser chrome into a fake conversation. Keep
    # meaningful content while preserving a clear provenance note.
    body = "\n\n".join(lines)
    low = body.casefold()
    auth_markers = ("sign in", "log in", "create account", "masuk", "daftar")
    if sum(marker in low for marker in auth_markers) >= 2 and len(body) < 20_000:
        return None
    if len(body) > 120_000:
        body = body[:120_000] + "\n\n[Konten dipotong untuk menjaga ukuran arsip.]"
    return {
        "title": title or f"{platform} Shared Chat",
        "created_at": "",
        "messages": [{"role": "assistant", "content": body, "timestamp": ""}],
        "source_url": url,
        "platform": platform,
        "partial_import": True,
    }


def fetch_shared_chat(url: str, timeout: int = 25) -> Dict[str, Any]:
    """Fetch and normalize a public share URL.

    Important: a valid URL and a readable public share page are different
    things. HTTP 401/403/404, bot challenges, and parser mismatches now get
    explicit diagnostics instead of being reported as a generic invalid URL.
    """
    normalized_url = normalize_share_url(url)
    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL tidak valid. Contoh: https://chatgpt.com/share/...")
    if not parsed.hostname or "." not in parsed.hostname:
        raise ValueError("Host URL tidak valid. Pastikan memakai link share publik lengkap.")

    platform = detect_platform(normalized_url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8,id;q=0.6",
        "Cache-Control": "no-cache",
    }
    try:
        res = requests.get(normalized_url, headers=headers, timeout=timeout, allow_redirects=True)
    except requests.exceptions.Timeout as exc:
        raise ValueError("Share page timeout. Koneksi atau server terlalu lambat.") from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Gagal mengakses share URL: {exc}") from exc

    final_url = normalize_share_url(res.url or normalized_url)
    final_platform = detect_platform(final_url)
    if final_platform != "Generic":
        platform = final_platform

    if res.status_code in {401, 403}:
        raise ValueError(
            f"Share URL terdeteksi sebagai {platform}, tetapi server menolak akses (HTTP {res.status_code}). "
            "Pastikan link benar-benar public dan tidak membutuhkan login."
        )
    if res.status_code == 404:
        raise ValueError("Share URL valid secara format, tetapi halaman share tidak ditemukan (HTTP 404). Link mungkin sudah dihapus/kedaluwarsa.")
    if res.status_code >= 400:
        raise ValueError(f"Share page gagal diakses (HTTP {res.status_code}). Ini bukan berarti format URL salah.")

    content_type = (res.headers.get("content-type") or "").lower()
    if "json" in content_type:
        try:
            obj = res.json()
        except ValueError as exc:
            raise ValueError("Server mengaku JSON tetapi respons tidak valid.") from exc
        candidates = _find_structured_candidates(obj)
        if isinstance(obj, dict):
            candidates.insert(0, obj)
        for candidate in candidates:
            data = _parser_from_object(candidate, final_url, platform)
            if data:
                return data
        raise ValueError("Halaman share mengembalikan JSON, tetapi struktur percakapannya belum dikenali.")

    page = res.text
    low_page = page.casefold()
    if any(marker in low_page for marker in ("cf-chl-", "just a moment", "enable javascript and cookies")):
        raise ValueError("Server menampilkan proteksi browser/anti-bot. Halaman share tidak bisa diambil lewat HTTP biasa.")

    title_match = re.search(r"<title[^>]*>(.*?)</title>", page, flags=re.I | re.S)
    page_title = re.sub(r"\s+", " ", html.unescape(title_match.group(1))).strip() if title_match else ""

    for obj in _decode_json_blocks(page):
        for candidate in _find_structured_candidates(obj):
            data = _parser_from_object(candidate, final_url, platform)
            if data:
                return data

    # Static/server-rendered share pages may contain the conversation in DOM
    # even when their private JSON state is unavailable. Recover semantic
    # user/assistant nodes before falling back to browser chrome extraction.
    role_messages = _extract_role_messages(page)
    if role_messages and any(len(m.get("content", "")) >= 20 for m in role_messages):
        return {
            "title": page_title or f"{platform} Shared Chat",
            "created_at": "",
            "messages": role_messages,
            "source_url": final_url,
            "platform": platform,
            "partial_import": True,
            "extractor": "semantic-html",
        }

    fallback = _html_fallback(page, page_title, platform, final_url)
    if fallback:
        fallback["extractor"] = "text-fallback"
        return fallback
    raise ValueError(
        "Share page berhasil dibuka, tetapi data percakapan tidak ditemukan. "
        "Kemungkinan platform mengubah struktur halaman atau share tersebut tidak lagi public."
    )

