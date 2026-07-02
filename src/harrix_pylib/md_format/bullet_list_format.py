"""Preserve bullet-list markers from source lines."""

from __future__ import annotations

import re

from harrix_pylib.md_format.text_lines import join_lines, split_lines

_BULLET_ITEM_RE = re.compile(r"^(\s*)([-*+])\s+")


def extract_bullet_list_marker_groups(body: str) -> tuple[str, list[list[str]]]:
    """Collect source bullet markers for each bullet list in document order."""
    lines, trailing = split_lines(body)
    groups: list[list[str]] = []
    stack: list[tuple[int, int]] = []
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        match = _BULLET_ITEM_RE.match(line)
        if not match:
            if not line.strip():
                peek_index = line_index + 1
                while peek_index < len(lines) and not lines[peek_index].strip():
                    peek_index += 1
                if peek_index < len(lines) and _BULLET_ITEM_RE.match(lines[peek_index]):
                    while stack:
                        stack.pop()
            elif not line.startswith(" "):
                while stack:
                    stack.pop()
            line_index += 1
            continue
        indent = len(match.group(1))
        marker = match.group(2)
        while stack and stack[-1][0] > indent:
            stack.pop()
        if stack and stack[-1][0] == indent:
            group_idx = stack[-1][1]
            current_group = groups[group_idx]
            if current_group and marker != current_group[-1] and len(set(current_group)) == 1:
                while stack:
                    stack.pop()
                groups.append([marker])
                stack.append((indent, len(groups) - 1))
            else:
                current_group.append(marker)
        else:
            groups.append([marker])
            stack.append((indent, len(groups) - 1))
        line_index += 1
    return join_lines(lines, trailing_newline=trailing), groups
