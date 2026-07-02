"""Protect fenced code blocks from markdown formatting."""

from __future__ import annotations

from dataclasses import dataclass

from harrix_pylib.md_format.code_fence import identify_code_blocks
from harrix_pylib.md_format.options import FormatOptions
from harrix_pylib.md_format.text_lines import join_lines, make_placeholder, split_lines

PLACEHOLDER_PREFIX = "HSKMDFMTCODE"
_MIN_FENCED_BLOCK_LINES = 2


@dataclass(frozen=True)
class CodeBlock:
    """Stored fenced code block extracted from Markdown body."""

    index: int
    lines: list[str]
    base_indent: str
    tight: bool = False


def extract_code_blocks(body: str) -> tuple[str, list[CodeBlock]]:
    """Replace fenced code blocks with placeholders and store originals verbatim."""
    lines, has_trailing_newline = split_lines(body)
    code_block_info = list(identify_code_blocks(lines))
    result: list[str] = []
    blocks: list[CodeBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        if not code_block_info[line_index][1]:
            result.append(line)
            line_index += 1
            continue

        block_lines: list[str] = []
        while line_index < len(lines) and code_block_info[line_index][1]:
            block_lines.append(lines[line_index])
            line_index += 1

        block_lines = _trim_trailing_blank_lines_before_closing_fence(block_lines)
        base_indent = _leading_whitespace(block_lines[0])
        placeholder_line = f"{base_indent}{make_placeholder(PLACEHOLDER_PREFIX, index)}"

        inserted_blank = False
        if result and result[-1].strip():
            result.append("")
            inserted_blank = True
        result.append(placeholder_line)
        if line_index < len(lines) and lines[line_index].strip():
            result.append("")
            inserted_blank = True

        blocks.append(CodeBlock(index=index, lines=block_lines, base_indent=base_indent, tight=inserted_blank))
        index += 1

    return join_lines(result, trailing_newline=has_trailing_newline), blocks


def restore_code_blocks(text: str, blocks: list[CodeBlock], *, options: FormatOptions | None = None) -> str:
    """Restore fenced code blocks from placeholders."""
    if not blocks:
        return text

    blocks_by_index = {block.index: block for block in blocks}
    lines, has_trailing_newline = split_lines(text)
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
            block_lines = _format_markdown_fence_block(block.lines, options=options)
            current_indent = _leading_whitespace(line)
            restored.extend(_reindent_line(block_line, block.base_indent, current_indent) for block_line in block_lines)
            continue
        restored.append(line)
    return join_lines(restored, trailing_newline=has_trailing_newline)


def _format_markdown_fence_block(block_lines: list[str], *, options: FormatOptions | None) -> list[str]:
    if len(block_lines) < _MIN_FENCED_BLOCK_LINES:
        return block_lines
    opening = block_lines[0].strip()
    if not opening.startswith("```"):
        return block_lines
    language = opening[3:].strip().lower()
    if language != "markdown" or options is None:
        return block_lines
    inner = "\n".join(block_lines[1:-1])
    if not inner.strip():
        return block_lines
    from harrix_pylib.md_format.formatter import _format_with_options  # noqa: PLC0415

    formatted_inner = _format_with_options(inner, options).rstrip("\n")
    return [block_lines[0], *formatted_inner.split("\n"), block_lines[-1]]


def _leading_whitespace(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def _reindent_line(line: str, base_indent: str, current_indent: str) -> str:
    if not line.strip():
        return line
    if base_indent and line.startswith(base_indent):
        return current_indent + line[len(base_indent) :]
    if base_indent:
        return current_indent + line
    return line


def _trim_trailing_blank_lines_before_closing_fence(block_lines: list[str]) -> list[str]:
    """Drop blank lines immediately before the closing fence line."""
    if len(block_lines) < _MIN_FENCED_BLOCK_LINES:
        return block_lines

    trimmed = list(block_lines)
    closing_index = len(trimmed) - 1
    while closing_index >= _MIN_FENCED_BLOCK_LINES and trimmed[closing_index - 1].strip() == "":
        trimmed.pop(closing_index - 1)
        closing_index -= 1
    if len(trimmed) == _MIN_FENCED_BLOCK_LINES:
        # Ensure an empty fenced block stays a fenced block (not inline code).
        trimmed.insert(1, "")
    return trimmed
