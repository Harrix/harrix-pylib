"""Preserve task-list checkbox markers stripped by the parser."""

from __future__ import annotations

import re
from dataclasses import dataclass

from harrix_pylib.md_format.text_lines import _join_lines, _make_placeholder, _split_lines

PLACEHOLDER_PREFIX = "HSKMDFMTTASK"
_TASK_ITEM_RE = re.compile(r"^(\s*)((?:[-*+])|(?:\d+[.)]))( +)\[([xX ])\]\s+(.*)$")


@dataclass(frozen=True)
class _TaskListMarker:
    """Stored checkbox marker for a task list item."""

    index: int
    checked: bool
    marker_spaces: int = 1


def _extract_task_list_markers(body: str) -> tuple[str, list[_TaskListMarker]]:
    """Replace task-list markers with placeholders the parser will keep in text."""
    lines, trailing = _split_lines(body)
    result: list[str] = []
    markers: list[_TaskListMarker] = []
    index = 0
    for line in lines:
        match = _TASK_ITEM_RE.match(line)
        if not match:
            result.append(line)
            continue
        indent, marker, marker_spaces, checked_char, rest = match.groups()
        checked = checked_char.lower() == "x"
        markers.append(_TaskListMarker(index=index, checked=checked, marker_spaces=len(marker_spaces)))
        result.append(f"{indent}{marker}{marker_spaces}{_make_placeholder(PLACEHOLDER_PREFIX, index)} {rest}")
        index += 1
    return _join_lines(result, trailing_newline=trailing), markers


def _strip_task_placeholder(text: str) -> str:
    """Remove the task-list placeholder token from item text."""
    stripped = text.lstrip()
    if not stripped.startswith(PLACEHOLDER_PREFIX):
        return text
    _, _, rest = stripped.partition(" ")
    return rest.lstrip()


def _task_list_entry_for_text(text: str, markers: list[_TaskListMarker]) -> tuple[str, _TaskListMarker] | None:
    """Return task marker text and metadata when paragraph text starts with a placeholder."""
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
            return ("[x] " if marker.checked else "[ ] ", marker)
    return None


def _task_list_marker_for_text(text: str, markers: list[_TaskListMarker]) -> str | None:
    """Return `[ ] ` or `[x] ` when paragraph text starts with a task placeholder."""
    entry = _task_list_entry_for_text(text, markers)
    return entry[0] if entry else None
