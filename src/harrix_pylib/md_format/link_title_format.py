"""Format Markdown link and image titles."""

from __future__ import annotations

import re

_LINK_PREFIX_RE = re.compile(r"!?\[[^\]]*\]\(")


def format_link_title(title: str) -> str:
    """Return a canonical quoted title for inline links and images."""
    title = _canonicalize_link_title_content(title)
    candidates: list[str] = []
    for delimiter in ('"', "'"):
        escaped = _escape_title_content(title, delimiter)
        candidates.append(f"{delimiter}{escaped}{delimiter}")
    return min(candidates, key=lambda candidate: (len(candidate), candidate[0] != '"'))


def normalize_inline_link_titles(body: str) -> str:
    """Normalize quoted titles in inline links before parsing."""
    parts: list[str] = []
    last = 0
    while last < len(body):
        match = _LINK_PREFIX_RE.search(body, last)
        if match is None:
            parts.append(body[last:])
            break
        parts.append(body[last : match.start()])
        open_paren = match.end() - 1
        close_index = _find_link_close_paren(body, open_paren)
        if close_index is None:
            parts.append(body[match.start() : match.end()])
            last = match.end()
            continue
        prefix = body[match.start():open_paren]
        destination = body[match.end() : close_index]
        suffix = body[close_index]
        parts.append(_normalize_inline_link(prefix, destination, suffix))
        last = close_index + 1
    return "".join(parts)


def _canonicalize_link_title_content(content: str) -> str:
    """Normalize lightly escaped one-character titles from CommonMark parsing."""
    if len(content) == 2 and content[0] == "\\" and content[1] in "\"'":
        return content[1]
    if len(content) == 2 and content[0] == "\\" and content[1] == ")":
        return ")"
    return content


def _escape_title_content(content: str, delimiter: str) -> str:
    escaped: list[str] = []
    for char in content:
        if char in {"\\", delimiter}:
            escaped.append("\\")
        escaped.append(char)
    return "".join(escaped)


def _find_link_close_paren(text: str, open_paren: int) -> int | None:
    if open_paren >= len(text) or text[open_paren] != "(":
        return None
    depth = 1
    for index in range(open_paren + 1, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _normalize_inline_link(prefix: str, destination: str, suffix: str) -> str:
    url, title = split_inline_destination(destination)
    if title is None:
        return f"{prefix}{destination}{suffix}"
    return f"{prefix}{url} {format_link_title(_unescape_title(title))}{suffix}"


def split_inline_destination(destination: str) -> tuple[str, str | None]:
    destination = destination.strip()
    if destination.startswith("<") and destination.endswith(">"):
        return destination, None
    title_match = re.search(
        r'\s+("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\((?:\\.|[^)\\])*\))\s*$',
        destination,
    )
    if title_match:
        title = title_match.group(1)
        url = destination[: title_match.start()].rstrip()
        if title in {'""', "''"}:
            return url, None
        return url, title
    return destination, None


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
