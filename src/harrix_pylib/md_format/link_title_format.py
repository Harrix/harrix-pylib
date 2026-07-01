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
    return min(candidates, key=lambda candidate: _title_quote_priority(title, candidate))


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
        prefix = body[match.start() : match.end()]
        destination = body[match.end() : close_index]
        suffix = body[close_index]
        parts.append(_normalize_inline_link(prefix, destination, suffix))
        last = close_index + 1
    return "".join(parts)


def split_inline_destination(destination: str) -> tuple[str, str | None]:
    destination = destination.strip()
    if destination.startswith("<") and destination.endswith(">"):
        return destination, None
    url, title = _split_trailing_link_title(destination)
    if title is not None:
        if title in {'""', "''"}:
            return url, None
        return url, title
    return destination, None


def _canonicalize_link_title_content(content: str) -> str:
    """Normalize lightly escaped one-character titles from CommonMark parsing."""
    if content == "\\)":
        return ")"
    if content == '"':
        return "'\""
    if content == "'":
        return "\"'"
    if content == '\\"':
        return "'\""
    if content == "\\'":
        return "\"'"
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
    in_single = False
    in_double = False
    index = open_paren + 1
    while index < len(text):
        char = text[index]
        if char == "\\" and (in_single or in_double) and index + 1 < len(text):
            index += 2
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            index += 1
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            index += 1
            continue
        if not in_single and not in_double:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return index
        index += 1
    return None


def _is_escaped_at(text: str, index: int) -> bool:
    backslashes = 0
    position = index - 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def _normalize_inline_link(prefix: str, destination: str, suffix: str) -> str:
    url, title = split_inline_destination(destination)
    if title is None:
        return f"{prefix}{destination}{suffix}"
    return f"{prefix}{url} {format_link_title(_unescape_title(title))}{suffix}"


def _balanced_paren_title_close(text: str, open_index: int) -> int | None:
    index = open_index + 1
    while index < len(text):
        if text[index] == "\\" and index + 1 < len(text):
            index += 2
            continue
        if text[index] == ")":
            if index > open_index + 1 and text[index - 1] == "\\":
                index += 1
                continue
            return index
        if text[index] == "(":
            return None
        index += 1
    return None


def _split_trailing_link_title(rest: str) -> tuple[str, str | None]:
    rest = rest.rstrip()
    space_paren = rest.rfind(" (")
    if space_paren >= 0:
        open_paren = space_paren + 1
        close_paren = _balanced_paren_title_close(rest, open_paren)
        if close_paren is not None:
            return rest[:open_paren].rstrip(), rest[open_paren : close_paren + 1]
    if not rest or rest[-1] not in "\"'":
        return rest, None
    delimiter = rest[-1]
    index = len(rest) - 2
    while index >= 0:
        if rest[index] == delimiter and not _is_escaped_at(rest, index):
            if index == 0 or rest[index - 1].isspace():
                return rest[:index].rstrip(), rest[index:]
        index -= 1
    return rest, None


def _title_quote_priority(content: str, quoted: str) -> tuple[int, int]:
    delimiter = quoted[0]
    if '"' in content and "'" not in content:
        return (len(quoted), 0 if delimiter == "'" else 1)
    if "'" in content and '"' not in content:
        return (len(quoted), 0 if delimiter == '"' else 1)
    return (len(quoted), 0 if delimiter == '"' else 1)


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
    return _canonicalize_link_title_content("".join(result))
