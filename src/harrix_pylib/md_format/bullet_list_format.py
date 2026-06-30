"""Preserve bullet-list markers from source lines."""

from __future__ import annotations

import re

_BULLET_ITEM_RE = re.compile(r"^(\s*)([-*+])\s+")


def extract_bullet_list_marker_groups(body: str) -> tuple[str, list[list[str]]]:
    """Collect source bullet markers for each contiguous bullet list."""
    lines, trailing = _split_lines(body)
    groups: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        match = _BULLET_ITEM_RE.match(line)
        if match:
            marker = match.group(2)
            if current and marker != current[-1] and len({*current}) == 1:
                groups.append(current)
                current = [marker]
            else:
                current.append(marker)
            continue
        if current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return _join_lines(lines, trailing_newline=trailing), groups


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
