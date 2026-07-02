"""Detect loose-list layout from source lines."""

from __future__ import annotations

from dataclasses import dataclass

from harrix_pylib.md_format.code_guard import PLACEHOLDER_PREFIX as CODE_PLACEHOLDER_PREFIX
from harrix_pylib.md_format.list_format import is_list_line
from harrix_pylib.md_format.text_lines import join_lines, split_lines


@dataclass(frozen=True)
class ListLayout:
    """Loose-list spacing for one list in source order."""

    gaps_before_item: list[bool]
    loose_items: list[bool]


def extract_list_layouts(body: str, tight_code_indices: set[int] | None = None) -> tuple[str, list[ListLayout]]:
    """Collect loose-list layout metadata for each list in the document."""
    lines, trailing = split_lines(body)
    scan_lines = _drop_code_placeholder_blanks(lines, tight_code_indices or set())
    layouts: list[ListLayout] = []
    index = 0
    while index < len(scan_lines):
        if not is_list_line(scan_lines[index]):
            index += 1
            continue
        index = _scan_list(scan_lines, index, layouts)
    return join_lines(lines, trailing_newline=trailing), layouts


def _blank_separates_sibling_items(lines: list[str], item_index: int, base_indent: int) -> bool:
    """True when a blank line in source separates two same-level list markers."""
    if item_index == 0 or lines[item_index - 1].strip():
        return False
    parent_marker = _parent_list_marker_line(lines, item_index - 1, base_indent)
    if parent_marker is None:
        return True
    return "](" not in parent_marker


def _consume_item(lines: list[str], start: int, base_indent: int, nested_layouts: list[ListLayout]) -> tuple[int, bool]:
    index = start + 1
    loose = False
    pending_blank = False
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            pending_blank = True
            index += 1
            continue
        indent = _line_indent(line)
        if is_list_line(line) and indent == base_indent:
            break
        if is_list_line(line) and indent > base_indent:
            if pending_blank:
                parent_marker = lines[start]
                if "](" not in parent_marker:
                    loose = True
            pending_blank = False
            index = _scan_list(lines, index, nested_layouts)
            continue
        if indent > base_indent:
            if pending_blank:
                loose = True
            pending_blank = False
            index += 1
            continue
        break
    return index, loose


def _drop_code_placeholder_blanks(lines: list[str], tight_code_indices: set[int]) -> list[str]:
    """Ignore blank lines that were auto-inserted around tightly attached code placeholders."""
    if not tight_code_indices:
        return lines

    def _tight_placeholder(line: str) -> bool:
        stripped = line.strip()
        if not stripped.startswith(CODE_PLACEHOLDER_PREFIX):
            return False
        try:
            return int(stripped.removeprefix(CODE_PLACEHOLDER_PREFIX)) in tight_code_indices
        except ValueError:
            return False

    is_tight = [_tight_placeholder(line) for line in lines]
    result: list[str] = []
    for index, line in enumerate(lines):
        if not line.strip():
            prev_is_tight = index > 0 and is_tight[index - 1]
            next_is_tight = index + 1 < len(lines) and is_tight[index + 1]
            if prev_is_tight or next_is_tight:
                continue
        result.append(line)
    return result


def _is_ordered_list_line(line: str) -> bool:
    """Return True when the line starts an ordered list item (not bullet)."""
    import re  # noqa: PLC0415

    return bool(re.match(r"^\s*\d+[.)]\s", line))


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _parent_list_marker_line(lines: list[str], from_index: int, base_indent: int) -> str | None:
    index = from_index
    while index >= 0:
        line = lines[index]
        if is_list_line(line) and _line_indent(line) == base_indent:
            return line
        index -= 1
    return None


def _scan_list(lines: list[str], start: int, layouts: list[ListLayout]) -> int:
    base_indent = _line_indent(lines[start])
    start_is_ordered = _is_ordered_list_line(lines[start])
    gaps_before_item = [False]
    loose_items: list[bool] = []
    nested_layouts: list[ListLayout] = []
    index = start
    while index < len(lines):
        current_line = lines[index]
        if not (
            is_list_line(current_line)
            and _line_indent(current_line) == base_indent
            and _is_ordered_list_line(current_line) == start_is_ordered
        ):
            break
        if index != start:
            gaps_before_item.append(_blank_separates_sibling_items(lines, index, base_indent))
        item_end, item_loose = _consume_item(lines, index, base_indent, nested_layouts)
        loose_items.append(item_loose)
        index = item_end
    layouts.append(
        ListLayout(
            gaps_before_item=gaps_before_item,
            loose_items=loose_items or [False],
        )
    )
    layouts.extend(nested_layouts)
    return index
