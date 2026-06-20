"""Markdown formatting orchestration."""

from __future__ import annotations

import re
from pathlib import Path

from harrix_pylib.md_format.code_guard import extract_code_blocks, restore_code_blocks
from harrix_pylib.md_format.front_matter import (
    collapse_extra_blank_lines,
    compact_front_matter,
    join_front_matter,
    split_front_matter,
)
from harrix_pylib.md_format.list_format import ensure_blank_line_after_lists
from harrix_pylib.md_format.options import FormatOptions
from harrix_pylib.md_format.parser import get_markdown_parser
from harrix_pylib.md_format.printer import render_tokens
from harrix_pylib.md_format.table_format import ensure_blank_line_after_tables, unwrap_spurious_table_rows


def format_markdown_content(text: str, *, end_of_line: str = "crlf") -> str:
    """Format Markdown text with Prettier-like defaults."""
    options = FormatOptions(end_of_line=end_of_line)
    return _format_with_options(text, options)


def normalize_line_endings(text: str) -> str:
    r"""Normalize mixed or corrupted line endings to LF.

    Handles CRLF applied twice (``\r\r\n``), which otherwise becomes a blank
    line between every source line after the legacy two-step ``\r`` cleanup or
    after :func:`pathlib.Path.read_text` universal-newline translation.
    """
    return re.sub(r"\r+\n", "\n", text).replace("\r", "\n")


def read_markdown_text(filename: Path | str) -> str:
    r"""Read Markdown from disk without universal-newline mangling of ``\r\r\n``."""
    path = Path(filename)
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return normalize_line_endings(data.decode("utf-8"))


def _format_with_options(text: str, options: FormatOptions) -> str:
    normalized = normalize_line_endings(text)
    front_matter, body = split_front_matter(normalized)
    if front_matter:
        front_matter = compact_front_matter(front_matter)
    body, code_blocks = extract_code_blocks(body)
    body = collapse_extra_blank_lines(body)
    body = unwrap_spurious_table_rows(ensure_blank_line_after_tables(body))
    body = ensure_blank_line_after_lists(body)
    if not body.strip() and front_matter:
        result = front_matter.rstrip() + "\n"
    else:
        parser = get_markdown_parser()
        tokens = parser.parse(body)
        rendered_body = restore_code_blocks(render_tokens(tokens), code_blocks)
        result = join_front_matter(front_matter, rendered_body)
    return _normalize_end_of_line(result, options.end_of_line)


def _normalize_end_of_line(text: str, end_of_line: str) -> str:
    normalized = normalize_line_endings(text)
    if end_of_line == "lf":
        return normalized
    if end_of_line == "crlf":
        return normalized.replace("\n", "\r\n")
    msg = f"Unsupported end_of_line value: {end_of_line}"
    raise ValueError(msg)
