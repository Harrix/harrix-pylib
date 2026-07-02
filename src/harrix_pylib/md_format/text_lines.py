"""Shared line splitting and placeholder helpers for md_format."""

from __future__ import annotations

from collections.abc import Callable


def ensure_blank_line_after_active_block(
    body: str,
    *,
    is_block_line: Callable[[str], bool],
) -> str:
    """Insert a blank line after a block when the next non-empty line starts new content."""
    lines = body.split("\n")
    result: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        is_block = is_block_line(line)
        if in_block and stripped and not is_block:
            result.append("")
            in_block = False
        if is_block:
            in_block = True
        elif stripped:
            in_block = False
        result.append(line)
    return "\n".join(result)


def join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    """Join lines and restore a trailing newline when requested."""
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


def make_placeholder(prefix: str, index: int) -> str:
    """Build a stable placeholder token for protected regions."""
    return f"{prefix}{index}"


def split_lines(text: str) -> tuple[list[str], bool]:
    """Split text into lines without the trailing split artifact from a final newline."""
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
