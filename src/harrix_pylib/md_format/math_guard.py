"""Protect empty block-math regions from markdown formatting."""

from __future__ import annotations

import re
from dataclasses import dataclass

from harrix_pylib.md_format.code_fence import _identify_code_blocks
from harrix_pylib.md_format.text_lines import _join_lines, _make_placeholder, _split_lines

PLACEHOLDER_PREFIX = "HSKMDFMTMATH"
_MATH_DELIMITER_RE = re.compile(r"^(\s*)\$\$\s*$")


@dataclass(frozen=True)
class EmptyMathBlock:
    """Stored empty ``$$`` block extracted from Markdown body."""

    index: int
    lines: list[str]


def _extract_empty_math_blocks(body: str) -> tuple[str, list[EmptyMathBlock]]:
    """Replace empty block-math regions with placeholders before parsing."""
    lines, has_trailing_newline = _split_lines(body)
    in_code = [inside for _line, inside in _identify_code_blocks(lines)]
    result: list[str] = []
    blocks: list[EmptyMathBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        if in_code[line_index]:
            result.append(lines[line_index])
            line_index += 1
            continue

        close_index = _find_empty_math_block_close(lines, line_index, in_code)
        if close_index is None:
            result.append(lines[line_index])
            line_index += 1
            continue

        block_lines = lines[line_index : close_index + 1]
        base_indent = _leading_whitespace(block_lines[0])
        placeholder_line = f"{base_indent}{_make_placeholder(PLACEHOLDER_PREFIX, index)}"
        result.append(placeholder_line)
        blocks.append(EmptyMathBlock(index=index, lines=block_lines))
        index += 1
        line_index = close_index + 1

    return _join_lines(result, trailing_newline=has_trailing_newline), blocks


def _find_empty_math_block_close(lines: list[str], start: int, in_code: list[bool]) -> int | None:
    open_match = _MATH_DELIMITER_RE.match(lines[start])
    if open_match is None:
        return None
    indent = open_match.group(1)
    line_index = start + 1
    while line_index < len(lines):
        if in_code[line_index]:
            return None
        close_match = _MATH_DELIMITER_RE.match(lines[line_index])
        if close_match is not None and close_match.group(1) == indent:
            if all(not lines[inner].strip() for inner in range(start + 1, line_index)):
                return line_index
            return None
        if lines[line_index].strip():
            return None
        line_index += 1
    return None


def _leading_whitespace(line: str) -> str:
    match = re.match(r"[ \t]*", line)
    return match.group(0) if match else ""


def _restore_empty_math_blocks(text: str, blocks: list[EmptyMathBlock]) -> str:
    """Restore empty block-math regions from placeholders."""
    if not blocks:
        return text

    blocks_by_index = {block.index: block for block in blocks}
    lines, has_trailing_newline = _split_lines(text)
    restored: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(PLACEHOLDER_PREFIX):
            try:
                block_index = int(stripped.removeprefix(PLACEHOLDER_PREFIX))
            except ValueError:
                restored.append(line)
                continue
            block = blocks_by_index.get(block_index)
            if block is None:
                restored.append(line)
                continue
            restored.extend(block.lines)
            continue
        restored.append(line)
    return _join_lines(restored, trailing_newline=has_trailing_newline)
