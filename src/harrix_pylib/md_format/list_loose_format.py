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


def _consume_item(
    lines: list[str], start: int, base_indent: int, nested_layouts: list[ListLayout]
) -> tuple[int, bool]:
    index = start + 1
    saw_blank = False
    saw_nested_list = False
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            saw_blank = True
            index += 1
            continue
        indent = _line_indent(line)
        if is_list_line(line) and indent == base_indent:
            break
        if is_list_line(line) and indent > base_indent:
            saw_nested_list = True
            index = _scan_list(lines, index, nested_layouts)
            continue
        if indent > base_indent:
            saw_blank = False
            index += 1
            continue
        break
    return index, saw_blank and saw_nested_list


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
        if index != start and index > 0 and not lines[index - 1].strip():
            gaps_before_item.append(True)
        elif index != start:
            gaps_before_item.append(False)
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
