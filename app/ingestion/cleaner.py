import re

_PAGE_MARKER_RE = re.compile(r"^\s*Page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE)
_LONE_NUMBER_RE = re.compile(r"^\s*-?\s*\d+\s*-?\s*$")
_BULLET_RE = re.compile(r"^\s*([-*•]|\d+[.)])\s+")


def clean_text(text: str) -> str:
    """Conservative cleaning: normalize whitespace, drop page markers, preserve
    headings/bullets/numbers/policy words. Never touches wording inside a line.
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _strip_page_headers_footers(text)

    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]

    paragraphs: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            paragraphs.append(" ".join(buffer))
            buffer.clear()

    for line in lines:
        if line == "":
            flush()
            continue
        if _BULLET_RE.match(line):
            flush()
            paragraphs.append(line)
        else:
            buffer.append(line)
    flush()

    return "\n\n".join(p for p in paragraphs if p).strip()


def _strip_page_headers_footers(text: str) -> str:
    lines = text.split("\n")
    kept = [
        ln for ln in lines
        if not _PAGE_MARKER_RE.match(ln) and not _LONE_NUMBER_RE.match(ln)
    ]
    return "\n".join(kept)
