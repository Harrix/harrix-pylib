"""Markdown formatting orchestration."""

from __future__ import annotations

import re
from pathlib import Path

from harrix_pylib.md_format.autolink_format import extract_angle_autolinks, restore_angle_autolinks
from harrix_pylib.md_format.bullet_list_format import extract_bullet_list_marker_groups
from harrix_pylib.md_format.code_guard import extract_code_blocks, restore_code_blocks
from harrix_pylib.md_format.front_matter import (
    collapse_extra_blank_lines,
    compact_front_matter,
    join_front_matter,
    split_front_matter,
    trim_trailing_blank_lines,
)
from harrix_pylib.md_format.hard_break_format import HardBreakStyles, extract_backslash_hard_breaks
from harrix_pylib.md_format.ignore_format import extract_ignore_blocks, restore_ignore_blocks
from harrix_pylib.md_format.list_format import ensure_blank_line_after_lists
from harrix_pylib.md_format.list_loose_format import extract_list_layouts
from harrix_pylib.md_format.options import FormatOptions
from harrix_pylib.md_format.ordered_list_format import extract_ordered_list_marker_groups
from harrix_pylib.md_format.parser import get_markdown_parser
from harrix_pylib.md_format.printer import render_tokens
from harrix_pylib.md_format.reference_format import extract_reference_blocks, restore_reference_blocks
from harrix_pylib.md_format.table_format import ensure_blank_line_after_tables, unwrap_spurious_table_rows
from harrix_pylib.md_format.task_list_format import extract_task_list_markers

_EMPTY_FENCE_RE = re.compile(r"(?m)^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})[ \t]*\n(?P=indent)(?P=fence)[ \t]*$")


def format_markdown_content(
    text: str,
    *,
    end_of_line: str = "crlf",
    prose_wrap: str = "preserve",
    print_width: int = 80,
) -> str:
    """Format Markdown text.

    ``prose_wrap`` matches Prettier: ``preserve`` (default), ``always``, or ``never``.
    Line wrapping uses ``print_width`` only when ``prose_wrap`` is ``always``.
    """
    options = FormatOptions(end_of_line=end_of_line, prose_wrap=prose_wrap, print_width=print_width)
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


def _ensure_blank_line_in_empty_fences(body: str) -> str:
    """Ensure empty fenced blocks are parsed as fences, not inline code."""
    return _EMPTY_FENCE_RE.sub(r"\g<indent>\g<fence>\n\n\g<indent>\g<fence>", body)


def _format_with_options(text: str, options: FormatOptions) -> str:
    normalized = normalize_line_endings(text)
    front_matter, body = split_front_matter(normalized)
    if front_matter:
        front_matter = compact_front_matter(front_matter)
    body = _ensure_blank_line_in_empty_fences(body)
    body, ignore_blocks = extract_ignore_blocks(body)
    body, hard_break_styles = extract_backslash_hard_breaks(body)
    body, angle_autolinks = extract_angle_autolinks(body)
    body, code_blocks = extract_code_blocks(body)
    body, reference_blocks = extract_reference_blocks(body)
    body, ordered_list_marker_groups = extract_ordered_list_marker_groups(body)
    body, bullet_list_marker_groups = extract_bullet_list_marker_groups(body)
    body, list_layouts = extract_list_layouts(body)
    body, task_list_markers = extract_task_list_markers(body)
    body = collapse_extra_blank_lines(body)
    body = unwrap_spurious_table_rows(ensure_blank_line_after_tables(body))
    body = ensure_blank_line_after_lists(body)
    if not body.strip() and front_matter and not reference_blocks:
        result = front_matter.rstrip() + "\n"
    elif not body.strip() and not front_matter and reference_blocks:
        rendered_body = restore_reference_blocks("", reference_blocks, options=options)
        result = rendered_body
    else:
        source_lines = body.split("\n")
        parser = get_markdown_parser()
        tokens = parser.parse(body)
        rendered_body = render_tokens(
            tokens,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=hard_break_styles,
            list_layouts=list_layouts,
            source_lines=source_lines,
        )
        rendered_body = restore_code_blocks(rendered_body, code_blocks)
        rendered_body = restore_angle_autolinks(rendered_body, angle_autolinks)
        rendered_body = restore_reference_blocks(rendered_body, reference_blocks, options=options)
        rendered_body = restore_ignore_blocks(rendered_body, ignore_blocks)
        result = join_front_matter(front_matter, rendered_body) if front_matter else rendered_body
    result = trim_trailing_blank_lines(result)
    return _normalize_end_of_line(result, options.end_of_line)


def _normalize_end_of_line(text: str, end_of_line: str) -> str:
    normalized = normalize_line_endings(text)
    if end_of_line == "lf":
        return normalized
    if end_of_line == "crlf":
        return normalized.replace("\n", "\r\n")
    msg = f"Unsupported end_of_line value: {end_of_line}"
    raise ValueError(msg)
