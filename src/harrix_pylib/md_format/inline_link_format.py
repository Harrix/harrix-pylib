"""Unified inline link scanning and preprocessing."""

from __future__ import annotations

from harrix_pylib.md_format.link_destination_format import PLACEHOLDER_PREFIX, LinkDestination
from harrix_pylib.md_format.link_title_format import (
    _unescape_title,
    format_link_title,
    format_parseable_link_title,
    scan_inline_links,
    split_inline_destination,
)
from harrix_pylib.md_format.text_lines import join_lines, make_placeholder, split_lines


def prepare_inline_links(body: str) -> tuple[str, list[LinkDestination]]:
    """Normalize link titles and extract destinations in a single pass."""
    lines, trailing = split_lines(body)
    result_lines: list[str] = []
    entries: list[LinkDestination] = []
    index = 0
    for line in lines:
        if _should_skip_link_line(line):
            result_lines.append(line)
            continue
        processed, line_entries, index = _prepare_inline_links_in_text(line, start_index=index)
        result_lines.append(processed)
        entries.extend(line_entries)
    return join_lines(result_lines, trailing_newline=trailing), entries


def _prepare_inline_links_in_text(body: str, *, start_index: int) -> tuple[str, list[LinkDestination], int]:
    entries: list[LinkDestination] = []
    index = start_index

    def handler(prefix: str, destination: str, suffix: str) -> str:
        nonlocal index
        url, title = split_inline_destination(destination)
        if title is not None:
            normalized_destination = f"{url} {format_parseable_link_title(_unescape_title(title))}"
        else:
            normalized_destination = destination
        url, title = split_inline_destination(normalized_destination.strip())
        display_title = format_link_title(_unescape_title(title)) if title is not None else None
        entries.append(LinkDestination(index=index, destination=url, title=display_title))
        title_suffix = f" {title}" if title is not None else ""
        replacement = f"{prefix}{make_placeholder(PLACEHOLDER_PREFIX, index)}{title_suffix}{suffix}"
        index += 1
        return replacement

    return scan_inline_links(body, handler), entries, index


def _should_skip_link_line(line: str) -> bool:
    return line.lstrip().startswith("|") or line.startswith("    ") or line.startswith("\t")
