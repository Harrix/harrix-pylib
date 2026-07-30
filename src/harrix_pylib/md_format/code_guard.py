"""Protect fenced code blocks from Markdown formatting."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from harrix_pylib.md_format.code_fence import _fence_marker_for_content, _identify_code_blocks
from harrix_pylib.md_format.math_format import _format_math_content
from harrix_pylib.md_format.text_lines import _join_lines, _make_placeholder, _split_lines

if TYPE_CHECKING:
    from collections.abc import Callable

    from harrix_pylib.md_format.options import _FormatOptions

PLACEHOLDER_PREFIX = "HSKMDFMTCODE"
_MIN_FENCED_BLOCK_LINES = 2
_FENCE_OPEN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})[ \t]*$")

_LATEX_DOCUMENT_RE = re.compile(r"\\documentclass\b|\\begin\{document\}")


@dataclass(frozen=True)
class _CodeBlock:
    """Stored fenced code block extracted from Markdown body."""

    index: int
    lines: list[str]
    base_indent: str
    tight: bool = False


def _extract_code_blocks(body: str) -> tuple[str, list[_CodeBlock]]:
    """Replace fenced code blocks with placeholders and store originals verbatim."""
    lines, has_trailing_newline = _split_lines(body)
    code_block_info = list(_identify_code_blocks(lines))
    result: list[str] = []
    blocks: list[_CodeBlock] = []
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
        placeholder_line = f"{base_indent}{_make_placeholder(PLACEHOLDER_PREFIX, index)}"

        inserted_blank = False
        if result and result[-1].strip():
            result.append("")
            inserted_blank = True
        result.append(placeholder_line)
        if line_index < len(lines) and lines[line_index].strip():
            result.append("")
            inserted_blank = True

        blocks.append(_CodeBlock(index=index, lines=block_lines, base_indent=base_indent, tight=inserted_blank))
        index += 1

    return _join_lines(result, trailing_newline=has_trailing_newline), blocks


def _fence_language(info: str) -> str:
    """Return the first info-string token lowercased, or empty string."""
    stripped = info.strip()
    if not stripped:
        return ""
    return stripped.split()[0].lower()


def _format_fenced_code_body(language: str, body: str, *, options: _FormatOptions | None) -> str:
    """Format a fenced code body for a supported language when enabled."""
    if options is not None and not options.format_code_blocks:
        return body
    formatter = _CODE_BLOCK_BODY_FORMATTERS.get(language)
    if formatter is None or not body.strip():
        return body
    return formatter(body.strip("\n"), options=options)


def _format_markdown_code_body(body: str, *, options: _FormatOptions | None = None) -> str:
    """Format a fenced `md` / `markdown` body with `MdFormatter` (LF inside the fence)."""
    from harrix_pylib.md_format.formatter import _format_with_options  # noqa: PLC0415
    from harrix_pylib.md_format.options import _FormatOptions as FormatOptions  # noqa: PLC0415

    nested = FormatOptions(
        end_of_line="lf",
        prose_wrap=options.prose_wrap if options is not None else "preserve",
        print_width=options.print_width if options is not None else 80,
        apply_prose_fixes=options.apply_prose_fixes if options is not None else True,
        format_math=options.format_math if options is not None else True,
        format_code_blocks=options.format_code_blocks if options is not None else True,
    )
    return _format_with_options(body, nested).strip("\n")


def _format_markdown_fence_block(block_lines: list[str], *, _options: _FormatOptions | None) -> list[str]:
    """Normalize fence length and optionally format supported language bodies."""
    if len(block_lines) < _MIN_FENCED_BLOCK_LINES:
        return block_lines

    open_match = _FENCE_OPEN_RE.match(block_lines[0])
    if open_match is not None:
        language = _fence_language(open_match.group(3))
        original_body_lines = block_lines[1:-1]
        body = "\n".join(original_body_lines)
        formatted_body = _format_fenced_code_body(language, body, options=_options)
        # Keep original lines when the formatter did not change content (also preserves
        # blank-only fences, which round-trip poorly through "\n".join / split).
        if formatted_body != body.strip("\n"):
            body_lines = [] if formatted_body == "" else formatted_body.split("\n")
            block_lines = [block_lines[0], *body_lines, block_lines[-1]]

    return _normalize_fence_length(block_lines)


def _format_math_or_leave_latex_document(body: str, *, options: _FormatOptions | None = None) -> str:  # noqa: ARG001
    """Format TeX math; leave full LaTeX documents unchanged."""
    if _LATEX_DOCUMENT_RE.search(body):
        return body
    return _format_math_content(body, display=True)


def _leading_whitespace(line: str) -> str:
    """Return leading whitespace from a line."""
    return line[: len(line) - len(line.lstrip())]


def _normalize_fence_length(block_lines: list[str]) -> list[str]:
    """Shrink or grow fence markers to the shortest length that still wraps content.

    Needed length is `max(3, longest_marker_run_in_content + 1)`. Extra backticks or
    tildes on the opening/closing lines are removed; fences that are too short for
    nested fences inside the body are lengthened.

    """
    if len(block_lines) < _MIN_FENCED_BLOCK_LINES:
        return block_lines

    open_match = _FENCE_OPEN_RE.match(block_lines[0])
    close_match = _FENCE_CLOSE_RE.match(block_lines[-1])
    if open_match is None or close_match is None:
        return block_lines

    open_indent, open_fence, info = open_match.group(1), open_match.group(2), open_match.group(3)
    close_indent, close_fence = close_match.group(1), close_match.group(2)
    marker = open_fence[0]
    if close_fence[0] != marker:
        return block_lines

    content = "\n".join(block_lines[1:-1])
    fence = _fence_marker_for_content(content, marker=marker)
    return [f"{open_indent}{fence}{info}", *block_lines[1:-1], f"{close_indent}{fence}"]


def _reindent_line(line: str, base_indent: str, current_indent: str) -> str:
    """Reindent a code line from `base_indent` to `current_indent`."""
    if not line.strip():
        return line
    if base_indent and line.startswith(base_indent):
        return current_indent + line[len(base_indent) :]
    if base_indent:
        return current_indent + line
    return line


def _restore_code_blocks(text: str, blocks: list[_CodeBlock], *, options: _FormatOptions | None = None) -> str:
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
            block_lines = _format_markdown_fence_block(block.lines, _options=options)
            current_indent = _leading_whitespace(line)
            restored.extend(_reindent_line(block_line, block.base_indent, current_indent) for block_line in block_lines)
            continue
        restored.append(line)
    return _join_lines(restored, trailing_newline=has_trailing_newline)


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


# Language tag (first info-string token, lowercased) -> body formatter.
# Extend this map when adding formatters for other fenced languages.
_CODE_BLOCK_BODY_FORMATTERS: dict[str, Callable[..., str]] = {
    "latex": _format_math_or_leave_latex_document,
    "markdown": _format_markdown_code_body,
    "md": _format_markdown_code_body,
    "tex": _format_math_or_leave_latex_document,
}
