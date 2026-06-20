"""Protect fenced code blocks from markdown formatting."""

from __future__ import annotations

from dataclasses import dataclass

PLACEHOLDER_PREFIX = "HSK_MD_FMT_CODE_"


@dataclass(frozen=True)
class CodeBlock:
    """Stored fenced code block extracted from Markdown body."""

    index: int
    lines: list[str]
    base_indent: str


def extract_code_blocks(body: str) -> tuple[str, list[CodeBlock]]:
    """Replace fenced code blocks with placeholders and store originals verbatim."""
    from harrix_pylib.funcs_md import identify_code_blocks  # noqa: PLC0415

    lines, has_trailing_newline = _split_lines(body)
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

        base_indent = _leading_whitespace(block_lines[0])
        blocks.append(CodeBlock(index=index, lines=block_lines, base_indent=base_indent))
        placeholder_line = f"{base_indent}{_placeholder(index)}"

        if result and result[-1].strip():
            result.append("")
        result.append(placeholder_line)
        if line_index < len(lines) and lines[line_index].strip():
            result.append("")

        index += 1

    return _join_lines(result, trailing_newline=has_trailing_newline), blocks


def restore_code_blocks(text: str, blocks: list[CodeBlock]) -> str:
    """Restore fenced code blocks from placeholders."""
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
            current_indent = _leading_whitespace(line)
            restored.extend(_reindent_line(block_line, block.base_indent, current_indent) for block_line in block.lines)
            continue
        restored.append(line)
    return _join_lines(restored, trailing_newline=has_trailing_newline)


def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


def _leading_whitespace(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def _placeholder(index: int) -> str:
    return f"{PLACEHOLDER_PREFIX}{index}"


def _reindent_line(line: str, base_indent: str, current_indent: str) -> str:
    if not line.strip():
        return line
    if base_indent and line.startswith(base_indent):
        return current_indent + line[len(base_indent) :]
    if base_indent:
        return current_indent + line
    return line


def _split_lines(text: str) -> tuple[list[str], bool]:
    """Split text into lines without the trailing split artifact from a final newline."""
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
