"""Preserve task-list checkbox markers stripped by the parser."""

from __future__ import annotations

import re
from dataclasses import dataclass

PLACEHOLDER_PREFIX = "HSKMDFMTTASK"
_TASK_ITEM_RE = re.compile(r"^(\s*)([-*+])\s+\[([xX ])\]\s+(.*)$")


@dataclass(frozen=True)
class TaskListMarker:
    """Stored checkbox marker for a task list item."""

    index: int
    checked: bool


def extract_task_list_markers(body: str) -> tuple[str, list[TaskListMarker]]:
    """Replace task-list markers with placeholders the parser will keep in text."""
    lines, trailing = _split_lines(body)
    result: list[str] = []
    markers: list[TaskListMarker] = []
    index = 0
    for line in lines:
        match = _TASK_ITEM_RE.match(line)
        if not match:
            result.append(line)
            continue
        indent, bullet, checked_char, rest = match.groups()
        checked = checked_char.lower() == "x"
        markers.append(TaskListMarker(index=index, checked=checked))
        result.append(f"{indent}{bullet} {_placeholder(index)} {rest}")
        index += 1
    return _join_lines(result, trailing_newline=trailing), markers


def strip_task_placeholder(text: str) -> str:
    """Remove the task-list placeholder token from item text."""
    stripped = text.lstrip()
    if not stripped.startswith(PLACEHOLDER_PREFIX):
        return text
    _, _, rest = stripped.partition(" ")
    return rest.lstrip()


def task_list_marker_for_text(text: str, markers: list[TaskListMarker]) -> str | None:
    """Return ``[ ] `` or ``[x] `` when paragraph text starts with a task placeholder."""
    stripped = text.lstrip()
    if not stripped.startswith(PLACEHOLDER_PREFIX):
        return None
    token, _, _ = stripped.partition(" ")
    try:
        marker_index = int(token.removeprefix(PLACEHOLDER_PREFIX))
    except ValueError:
        return None
    for marker in markers:
        if marker.index == marker_index:
            return "[x] " if marker.checked else "[ ] "
    return None


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
