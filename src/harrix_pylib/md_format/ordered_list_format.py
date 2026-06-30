"""Preserve ordered-list marker numbers from source lines."""

from __future__ import annotations

import re

_ORDERED_ITEM_RE = re.compile(r"^(\s*)(\d+)\.\s+")


def extract_ordered_list_marker_groups(body: str) -> tuple[str, list[list[int]]]:
    """Collect source marker numbers for each contiguous ordered list."""
    lines, trailing = _split_lines(body)
    groups: list[list[int]] = []
    current: list[int] = []
    for line in lines:
        match = _ORDERED_ITEM_RE.match(line)
        if match:
            current.append(int(match.group(2)))
            continue
        if current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return _join_lines(lines, trailing_newline=trailing), groups


def is_git_diff_friendly_ordered_list(markers: list[int]) -> bool:
    """Return whether ordered list markers should use git-diff-friendly ``1.`` suffixes."""
    if len(markers) < 2:
        return False
    if markers[1] != 1:
        return False
    if markers[0] != 0:
        return True
    return len(markers) > 2 and markers[2] == 1


def ordered_list_item_number(markers: list[int], item_index: int) -> int:
    """Compute the rendered marker number for an ordered-list item."""
    if not markers:
        return item_index + 1
    if is_git_diff_friendly_ordered_list(markers):
        return markers[0] if item_index == 0 else 1
    return markers[0] + item_index


def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
