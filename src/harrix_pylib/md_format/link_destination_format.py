"""Preserve and format inline link destinations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from harrix_pylib.md_format.link_title_format import (
    _unescape_title,
    format_link_title,
    scan_inline_links,
    split_inline_destination,
)
from harrix_pylib.md_format.text_lines import make_placeholder

PLACEHOLDER_PREFIX = "HSKMDFMTLD"


@dataclass(frozen=True)
class LinkDestination:
    """Stored original link destination text."""

    index: int
    destination: str
    title: str | None = None


def extract_link_destinations(body: str) -> tuple[str, list[LinkDestination]]:
    """Replace link destinations with placeholders before parsing."""
    from harrix_pylib.md_format.inline_link_format import prepare_inline_links  # noqa: PLC0415

    return prepare_inline_links(body)


def format_inline_link_destination(destination: str) -> str:
    """Return canonical destination text for inline links and images."""
    url, title = split_inline_destination(destination.strip())
    formatted_url = _format_link_url(url)
    if title is None:
        return formatted_url
    return f"{formatted_url} {title}"


def format_link_url(url: str, *, wrap_parentheses: bool = True) -> str:
    """Return canonical URL text for links and reference definitions."""
    return _format_link_url(url, wrap_parentheses=wrap_parentheses)


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


def _extract_link_destinations_from_text(body: str, *, start_index: int) -> tuple[str, list[LinkDestination]]:
    entries: list[LinkDestination] = []
    index = start_index

    def handler(prefix: str, destination: str, suffix: str) -> str:
        nonlocal index
        url, title = split_inline_destination(destination)
        display_title = format_link_title(_unescape_title(title)) if title is not None else None
        entries.append(LinkDestination(index=index, destination=url, title=display_title))
        title_suffix = f" {title}" if title is not None else ""
        replacement = f"{prefix}{make_placeholder(PLACEHOLDER_PREFIX, index)}{title_suffix}{suffix}"
        index += 1
        return replacement

    return scan_inline_links(body, handler), entries


def _format_link_url(url: str, *, wrap_parentheses: bool = True) -> str:
    url = url.replace("&amp;", "&")
    if url.startswith("<") and url.endswith(">"):
        return url
    if wrap_parentheses and "()" in url:
        encoded = _encode_special_characters(url)
        return f"<{encoded}>"
    return url
