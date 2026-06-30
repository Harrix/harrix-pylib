"""Detect loose-list layout from source lines."""

from __future__ import annotations

from dataclasses import dataclass

from harrix_pylib.md_format.list_format import is_list_line


@dataclass(frozen=True)
class ListLayout:
    """Loose-list spacing for one list in source order."""

    gaps_before_item: list[bool]
    loose_items: list[bool]


def extract_list_layouts(body: str) -> tuple[str, list[ListLayout]]:
    """Collect loose-list layout metadata for each list in the document."""
    lines, trailing = _split_lines(body)
    layouts: list[ListLayout] = []
    index = 0
    while index < len(lines):
        if not is_list_line(lines[index]):
            index += 1
            continue
        index = _scan_list(lines, index, layouts)
    return _join_lines(lines, trailing_newline=trailing), layouts


def _blank_separates_sibling_items(lines: list[str], item_index: int, base_indent: int) -> bool:
    """True when a blank line in source separates two same-level list markers."""
    if item_index == 0 or lines[item_index - 1].strip():
        return False
    parent_marker = _parent_list_marker_line(lines, item_index - 1, base_indent)
    if parent_marker is None:
        return True
    return "](" not in parent_marker


def _parent_list_marker_line(lines: list[str], from_index: int, base_indent: int) -> str | None:
    index = from_index
    while index >= 0:
        line = lines[index]
        if is_list_line(line) and _line_indent(line) == base_indent:
            return line
        index -= 1
    return None


def _consume_item(
    lines: list[str], start: int, base_indent: int, nested_layouts: list[ListLayout]
) -> tuple[int, bool]:
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


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _scan_list(lines: list[str], start: int, layouts: list[ListLayout]) -> int:
    base_indent = _line_indent(lines[start])
    gaps_before_item = [False]
    loose_items: list[bool] = []
    nested_layouts: list[ListLayout] = []
    index = start
    while index < len(lines):
        if not (is_list_line(lines[index]) and _line_indent(lines[index]) == base_indent):
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
