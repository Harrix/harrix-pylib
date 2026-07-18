"""Preserve ordered-list marker numbers from source lines."""

from __future__ import annotations

import re

from harrix_pylib.md_format.text_lines import _join_lines, _split_lines

_ORDERED_ITEM_RE = re.compile(r"^(\s*)(?:>\s*)?(\d+)([.)])\s+")
_BLOCKQUOTE_LIST_CONTINUATION_RE = re.compile(r"^>\s{2,}\S")


def _extract_ordered_list_marker_groups(body: str) -> tuple[str, list[list[int]]]:
    """Collect source marker numbers for each contiguous ordered list."""
    lines, trailing = _split_lines(body)
    groups: list[list[int]] = []
    current: list[int] = []
    current_indent: int | None = None
    for line in lines:
        if line.startswith(("    ", "\t")):
            continue
        match = _ORDERED_ITEM_RE.match(line)
        if match:
            indent = len(match.group(1))
            if current and current_indent is not None and indent == current_indent:
                # Continue same list (possibly after blank lines / continuation lines).
                current.append(int(match.group(2)))
            else:
                if current:
                    groups.append(current)
                current = [int(match.group(2))]
                current_indent = indent
            continue
        stripped = line.strip()
        if not stripped:
            # Blank line — may separate loose list items; keep current open.
            continue
        # A non-empty, non-list line: if it's indented deeper than current_indent,
        # it's a continuation of the current item; otherwise close the group.
        if current and current_indent is not None:
            line_indent = len(line) - len(line.lstrip())
            if line_indent > current_indent:
                # Continuation content — don't close the group.
                continue
            if _is_blockquote_list_continuation_line(line):
                continue
        # Different content at same or lower indent — close the group.
        if current:
            groups.append(current)
            current = []
            current_indent = None
    if current:
        groups.append(current)
    return _join_lines(lines, trailing_newline=trailing), groups


def _is_blockquote_list_continuation_line(line: str) -> bool:
    """Return whether a blockquote line continues the previous list item body."""
    return bool(_BLOCKQUOTE_LIST_CONTINUATION_RE.match(line))


def _is_git_diff_friendly_ordered_list(markers: list[int]) -> bool:
    """Return whether ordered list markers should use git-diff-friendly `1.` suffixes."""
    if len(markers) < 2:
        return False
    if markers[1] != 1:
        return False
    if markers[0] != 0:
        return True
    return len(markers) > 2 and markers[2] == 1


def _ordered_list_item_number(markers: list[int], item_index: int) -> int:
    """Compute the rendered marker number for an ordered-list item."""
    if not markers:
        return item_index + 1
    if _is_git_diff_friendly_ordered_list(markers):
        return markers[0] if item_index == 0 else 1
    return markers[0] + item_index


def _parse_ordered_list_marker(line: str) -> tuple[int, str] | None:
    """Return marker number and delimiter from an ordered-list source line."""
    match = _ORDERED_ITEM_RE.match(line)
    if not match:
        return None
    return int(match.group(2)), match.group(3)
