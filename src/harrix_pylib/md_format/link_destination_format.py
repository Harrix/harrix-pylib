"""Preserve and format inline link destinations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from harrix_pylib.md_format.link_title_format import _find_link_close_paren, split_inline_destination

PLACEHOLDER_PREFIX = "HSKMDFMTLD"
_LINK_PREFIX_RE = re.compile(r"!?\[[^\]]*\]\(")


@dataclass(frozen=True)
class LinkDestination:
    """Stored original link destination text."""

    index: int
    destination: str
    title: str | None = None


def extract_link_destinations(body: str) -> tuple[str, list[LinkDestination]]:
    """Replace link destinations with placeholders before parsing."""
    lines, trailing = _split_lines(body)
    result_lines: list[str] = []
    entries: list[LinkDestination] = []
    index = 0
    for line in lines:
        if line.lstrip().startswith("|"):
            result_lines.append(line)
            continue
        processed, line_entries = _extract_link_destinations_from_text(line, start_index=index)
        result_lines.append(processed)
        entries.extend(line_entries)
        index += len(line_entries)
    return _join_lines(result_lines, trailing_newline=trailing), entries


def format_link_url(url: str) -> str:
    """Return canonical URL text for links and reference definitions."""
    return _format_link_url(url)


def format_inline_link_destination(destination: str) -> str:
    """Return canonical destination text for inline links and images."""
    url, title = split_inline_destination(destination.strip())
    formatted_url = _format_link_url(url)
    if title is None:
        return formatted_url
    return f"{formatted_url} {title}"


def formatted_href_from_placeholder(href: str, entries_by_index: dict[int, LinkDestination]) -> str | None:
    """Return formatted URL for a placeholder href."""
    if not href.startswith(PLACEHOLDER_PREFIX):
        return None
    try:
        index = int(href.removeprefix(PLACEHOLDER_PREFIX))
    except ValueError:
        return None
    entry = entries_by_index.get(index)
    if entry is None:
        return None
    url, _title = split_inline_destination(format_inline_link_destination(entry.destination))
    return url


def formatted_title_from_placeholder(href: str, entries_by_index: dict[int, LinkDestination]) -> str | None:
    """Return pre-normalized title suffix for a placeholder href."""
    if not href.startswith(PLACEHOLDER_PREFIX):
        return None
    try:
        index = int(href.removeprefix(PLACEHOLDER_PREFIX))
    except ValueError:
        return None
    entry = entries_by_index.get(index)
    if entry is None:
        return None
    return entry.title


def _extract_link_destinations_from_text(
    body: str, *, start_index: int
) -> tuple[str, list[LinkDestination]]:
    parts: list[str] = []
    entries: list[LinkDestination] = []
    index = start_index
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
        url, title = split_inline_destination(destination)
        suffix = body[close_index]
        formatted_title = title
        entries.append(LinkDestination(index=index, destination=url, title=formatted_title))
        title_suffix = f" {title}" if title is not None else ""
        parts.append(f"{prefix}{_placeholder(index)}{title_suffix}{suffix}")
        index += 1
        last = close_index + 1
    return "".join(parts), entries


def _format_link_url(url: str) -> str:
    url = url.replace("&amp;", "&")
    if url.startswith("<") and url.endswith(">"):
        return url
    if "()" in url:
        encoded = _encode_special_characters(url)
        return f"<{encoded}>"
    return url


def _encode_special_characters(url: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(url):
        char = url[index]
        if char == "%" and index + 2 < len(url) and re.fullmatch(r"[0-9A-Fa-f]{2}", url[index + 1 : index + 3]):
            result.append(url[index : index + 3])
            index += 3
            continue
        if char == ">":
            result.append("%3E")
            index += 1
            continue
        result.append(char)
        index += 1
    return "".join(result)


def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


def _placeholder(index: int) -> str:
    return f"{PLACEHOLDER_PREFIX}{index}"


def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
