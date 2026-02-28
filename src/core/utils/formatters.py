import html
import re
import unicodedata
from typing import Optional

_HTML_RE = re.compile(r"<[^>]*>")
_URL_RE = re.compile(r"(?i)\b(?:https?://|www\.|tg://|t\.me/|telegram\.me/|joinchat/)\S+")
_USER_NAME_PLACEHOLDER = "TempUser"

def format_user_name(name: Optional[str]) -> str:
    if not name:
        return _USER_NAME_PLACEHOLDER

    text = html.unescape(name)
    text = unicodedata.normalize("NFKC", text)

    text = _HTML_RE.sub("", text)
    text = _URL_RE.sub("", text)

    allowed_prefixes = {"L", "N"}
    allowed_symbols = {"$", "_", "-", "."}

    chars: list[str] = []

    for char in text:
        cat = unicodedata.category(char)

        if cat == "Mn":
            continue

        if cat[0] in allowed_prefixes or char in allowed_symbols or cat == "Zs":
            chars.append(char)

    cleaned = " ".join("".join(chars).split())

    if not cleaned:
        return _USER_NAME_PLACEHOLDER

    if len(cleaned) > 32:
        cleaned = f"{cleaned[:31]}"

    return cleaned