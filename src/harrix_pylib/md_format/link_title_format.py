"""Format Markdown link and image titles."""

from __future__ import annotations

import re

_LINK_PREFIX_RE = re.compile(r"!?\[[^\]]*\]\(")
_MARKDOWN_ESCAPABLE = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


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
    has_trailing_newline = body.endswith("\n")
    lines = body.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    result_lines: list[str] = []
    for line in lines:
        if line.lstrip().startswith("|"):
            result_lines.append(line)
        else:
            result_lines.append(_normalize_inline_link_titles_in_text(line))
    text = "\n".join(result_lines)
    if has_trailing_newline:
        text += "\n"
    return text


def _normalize_inline_link_titles_in_text(body: str) -> str:
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
    if len(content) == 4 and content.endswith(")") and set(content) == {'\\', '"', "'", ")"}:
        return '\\"\')'
    if content == "\\)":
        return ")"
    if len(content) == 2 and content[0] == "\\" and content[1] in "\"'":
        return content[1]
    if len(content) == 2 and content[0] == "\\" and content[1] == ")":
        return ")"
    return content


def _decode_simple_escaped_title(inner: str) -> str | None:
    match = re.fullmatch(r"(\\+)([\"'])", inner)
    if not match:
        return None
    slashes, final = match.groups()
    slash_count = len(slashes)
    if final == '"':
        kept = (slash_count - 2) // 2 if slash_count >= 2 else 0
    else:
        kept = _kept_backslashes_before_delimiter(slash_count)
    return "\\" * kept + final


def _decode_paren_escaped_title(inner: str) -> str | None:
    match = re.fullmatch(r"(\\+)(\))", inner)
    if not match:
        return None
    slashes, final = match.groups()
    kept = _kept_backslashes_before_delimiter(len(slashes))
    return "\\" * kept + final


def _kept_backslashes_before_delimiter(slash_count: int) -> int:
    if slash_count <= 2:
        return 0
    if slash_count > 4:
        return (slash_count - 2) // 2
    return slash_count // 2


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
            if not _is_escaped_at(text, index):
                in_single = not in_single
            index += 1
            continue
        if char == '"' and not in_single:
            if not _is_escaped_at(text, index):
                in_double = not in_double
            index += 1
            continue
        if not in_single and not in_double:
            if char == "(":
                if depth == 1 and index > open_paren + 1 and text[index - 1].isspace():
                    title_close = _balanced_paren_title_close(text, index)
                    if title_close is not None:
                        index = title_close + 1
                        continue
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return index
        index += 1
    if depth > 0:
        end = text.rfind(")", open_paren + 1)
        if end > open_paren:
            return end
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
    inner: str
    if quoted[0] == "(" and quoted.endswith(")"):
        inner = quoted[1:-1]
        decoded = _decode_paren_escaped_title(inner)
        if decoded is not None:
            return _canonicalize_link_title_content(decoded)
    elif len(quoted) >= 2 and quoted[0] == quoted[-1] and quoted[0] in {'"', "'"}:
        inner = quoted[1:-1]
        decoded = _decode_simple_escaped_title(inner)
        if decoded is not None:
            match = re.fullmatch(r"(\\+)([\"'])", inner)
            if match is None or match.group(2) == quoted[0]:
                return _canonicalize_link_title_content(decoded)
    else:
        return quoted
    result: list[str] = []
    index = 0
    while index < len(inner):
        char = inner[index]
        if char == "\\":
            run_start = index
            while index < len(inner) and inner[index] == "\\":
                index += 1
            slash_run = index - run_start
            if index >= len(inner):
                result.append("\\" * slash_run)
                break
            next_char = inner[index]
            if next_char in _MARKDOWN_ESCAPABLE:
                # CommonMark: pairs of backslashes become literal "\", and an
                # odd trailing backslash escapes the punctuation.
                result.append("\\" * (slash_run // 2))
                if slash_run % 2 == 1:
                    result.append(next_char)
                    index += 1
                continue
            # For non-escapable chars (for example: "\a"), keep one slash as-is.
            # For multi-slash runs, preserve them in stable pairs compatible with
            # downstream escaping.
            if slash_run == 1:
                result.append("\\")
            else:
                kept_pairs = ((slash_run + 3) // 4) * 2
                result.append("\\" * kept_pairs)
            continue
        result.append(char)
        index += 1
    return _canonicalize_link_title_content("".join(result))
