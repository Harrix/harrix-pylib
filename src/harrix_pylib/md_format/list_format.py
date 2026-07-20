"""List line preprocessing for Markdown formatting."""

from __future__ import annotations

import re

from harrix_pylib.md_format.table_format import _is_table_line

BULLET_LIST_ITEM_RE = re.compile(r"^[-*+]\s")
ORDERED_LIST_ITEM_RE = re.compile(r"^\d+[.)]\s")
LIST_MARKER_LINE_RE = re.compile(r"^[-*+]\s|^\d+[.)]\s")
_LIST_ITEM_PATTERN = BULLET_LIST_ITEM_RE
_ORDERED_LIST_ITEM_PATTERN = ORDERED_LIST_ITEM_RE


def _ensure_blank_line_after_lists(body: str) -> str:
    """Insert a blank line after a list when the next line starts a new block."""
    lines = body.split("\n")
    result: list[str] = []
    in_list_context = False
    for line in lines:
        stripped = line.strip()
        if _is_list_line(line):
            in_list_context = True
            result.append(line)
            continue
        if not stripped:
            in_list_context = False
            result.append(line)
            continue
        if in_list_context and result and _is_list_item_continuation_line(result[-1], line):
            result.append(line)
            continue
        if in_list_context and not _is_table_line(line) and not _is_list_continuation(line):
            result.append("")
            in_list_context = False
        if not _is_list_continuation(line):
            in_list_context = False
        result.append(line)
    return "\n".join(result)


def _is_list_continuation(line: str) -> bool:
    """Return whether the line continues the previous list item paragraph."""
    return bool(line.strip() and not _is_list_line(line) and line[:1] in {" ", "\t"})


def _is_list_item_continuation_line(previous_line: str, line: str) -> bool:
    """Return whether an unindented line continues the previous list item text."""
    if not previous_line.strip() or not line.strip():
        return False
    if _is_list_line(line) or _is_table_line(line):
        return False
    stripped = line.lstrip()
    if stripped.startswith(">") and line[:1] in {" ", "\t"}:
        return _is_list_line(previous_line) or _is_list_continuation(previous_line)
    if stripped.startswith(("#", "```", "$$", "<details", "</details>", "<summary", "</summary>", "`", "![", "|")):
        return False
    if stripped.startswith(">") and line[:1] not in {" ", "\t"}:
        return False
    if _is_list_line(previous_line):
        return True
    if _is_list_continuation(previous_line):
        return True
    return bool(previous_line.startswith(" ") and not _is_list_line(previous_line))


def _is_list_line(line: str) -> bool:
    """Return whether the line is a bullet or ordered list item."""
    stripped = line.strip()
    if not stripped:
        return False
    return bool(_LIST_ITEM_PATTERN.match(stripped)) or bool(_ORDERED_LIST_ITEM_PATTERN.match(stripped))
