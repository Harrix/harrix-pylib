"""List line preprocessing for markdown formatting."""

from __future__ import annotations

import re

from harrix_pylib.md_format.table_format import is_table_line

BULLET_LIST_ITEM_RE = re.compile(r"^[-*+]\s")
ORDERED_LIST_ITEM_RE = re.compile(r"^\d+[.)]\s")
LIST_MARKER_LINE_RE = re.compile(r"^[-*+]\s|^\d+[.)]\s")
_LIST_ITEM_PATTERN = BULLET_LIST_ITEM_RE
_ORDERED_LIST_ITEM_PATTERN = ORDERED_LIST_ITEM_RE


def ensure_blank_line_after_lists(body: str) -> str:
    """Insert a blank line after a list when the next line starts a new block."""
    lines = body.split("\n")
    result: list[str] = []
    in_list_context = False
    for line in lines:
        stripped = line.strip()
        if is_list_line(line):
            in_list_context = True
            result.append(line)
            continue
        if not stripped:
            in_list_context = False
            result.append(line)
            continue
        if in_list_context and result and is_list_item_continuation_line(result[-1], line):
            result.append(line)
            continue
        if in_list_context and not is_table_line(line) and not is_list_continuation(line):
            result.append("")
            in_list_context = False
        if not is_list_continuation(line):
            in_list_context = False
        result.append(line)
    return "\n".join(result)


def is_list_continuation(line: str) -> bool:
    """Return whether the line continues the previous list item paragraph."""
    return bool(line.strip() and not is_list_line(line) and line[:1] in {" ", "\t"})


def is_list_item_continuation_line(previous_line: str, line: str) -> bool:
    """Return whether an unindented line continues the previous list item text."""
    if not previous_line.strip() or not line.strip():
        return False
    if is_list_line(line) or is_table_line(line):
        return False
    stripped = line.lstrip()
    if stripped.startswith(">") and line[:1] in {" ", "\t"}:
        return is_list_line(previous_line) or is_list_continuation(previous_line)
    if stripped.startswith(("#", "```", "$$", "<details", "</details>", "<summary", "</summary>", "`", "![", "|")):
        return False
    if stripped.startswith(">") and line[:1] not in {" ", "\t"}:
        return False
    if is_list_line(previous_line):
        return True
    if is_list_continuation(previous_line):
        return True
    return bool(previous_line.startswith(" ") and not is_list_line(previous_line))


def is_list_line(line: str) -> bool:
    """Return whether the line is a bullet or ordered list item."""
    stripped = line.strip()
    if not stripped:
        return False
    return bool(_LIST_ITEM_PATTERN.match(stripped)) or bool(_ORDERED_LIST_ITEM_PATTERN.match(stripped))
