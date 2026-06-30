"""Format Markdown link and image titles."""

from __future__ import annotations

import re

_INLINE_LINK_RE = re.compile(r"(\[[^\]]*\]\()([^)]+)(\))")


def format_link_title(title: str) -> str:
    """Return a canonical quoted title for inline links and images."""
    candidates: list[str] = []
    for delimiter in ('"', "'"):
        escaped = _escape_title_content(title, delimiter)
        candidates.append(f"{delimiter}{escaped}{delimiter}")
    return min(candidates, key=len)


def normalize_inline_link_titles(body: str) -> str:
    """Normalize quoted titles in inline links before parsing."""
    return _INLINE_LINK_RE.sub(_normalize_inline_link_match, body)


def _escape_title_content(content: str, delimiter: str) -> str:
    escaped: list[str] = []
    for char in content:
        if char in {"\\", delimiter}:
            escaped.append("\\")
        escaped.append(char)
    return "".join(escaped)


def _normalize_inline_link_match(match: re.Match[str]) -> str:
    prefix, destination, suffix = match.group(1), match.group(2), match.group(3)
    url, title = _split_inline_destination(destination)
    if title is None:
        return match.group(0)
    return f"{prefix}{url} {format_link_title(_unescape_title(title))}{suffix}"


def _split_inline_destination(destination: str) -> tuple[str, str | None]:
    destination = destination.strip()
    if destination.startswith("<") and ">" in destination:
        return destination, None
    title_match = re.search(
        r'\s+("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\((?:\\.|[^)\\])*\))\s*$',
        destination,
    )
    if not title_match:
        return destination, None
    title = title_match.group(1)
    url = destination[: title_match.start()].rstrip()
    if title in {'""', "''"}:
        return url, None
    return url, title


def _unescape_title(quoted: str) -> str:
    if not quoted:
        return quoted
    if quoted[0] == "(" and quoted.endswith(")"):
        inner = quoted[1:-1]
    elif len(quoted) >= 2 and quoted[0] == quoted[-1] and quoted[0] in {'"', "'"}:
        inner = quoted[1:-1]
    else:
        return quoted
    result: list[str] = []
    index = 0
    while index < len(inner):
        char = inner[index]
        if char == "\\" and index + 1 < len(inner):
            result.append(inner[index + 1])
            index += 2
            continue
        result.append(char)
        index += 1
    return "".join(result)
