"""Table line preprocessing for Markdown formatting."""

from __future__ import annotations

import unicodedata

from harrix_pylib.md_format.text_lines import _ensure_blank_line_after_active_block

_EMOJI_CODE_POINT_RANGES = (
    (0x2300, 0x23FF),
    (0x2600, 0x27BF),
    (0x1F000, 0x1FAFF),
)


def _ensure_blank_line_after_tables(body: str) -> str:
    """Insert a blank line after a GFM table when the next line is not a table row."""
    return _ensure_blank_line_after_active_block(body, is_block_line=_is_table_line)


def _is_emoji_base(char: str) -> bool:
    """Return whether a character is treated as a wide emoji base glyph."""
    code = ord(char)
    return any(start <= code <= end for start, end in _EMOJI_CODE_POINT_RANGES)


def _is_table_line(line: str) -> bool:
    """Return whether the line is a GFM table row."""
    stripped = line.strip()
    return bool(stripped) and stripped.startswith("|") and stripped.endswith("|")


def _looks_like_prose_table_row(text: str) -> bool:
    """Return whether a single table cell looks like a misparsed paragraph."""
    min_prose_length = 60
    min_word_count = 5
    return len(text) > min_prose_length or (text.count(" ") >= min_word_count and "." in text)


def _parse_table_cells(line: str) -> list[str] | None:
    """Split a table row into cell values."""
    stripped = line.strip()
    if not _is_table_line(line):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _text_display_width(text: str) -> int:
    """Return the terminal display width of text (emoji and CJK count as 2 columns)."""
    width = 0
    for char in text:
        category = unicodedata.category(char)
        if category in {"Mn", "Me", "Cf"}:
            continue
        if unicodedata.east_asian_width(char) in {"F", "W"} or _is_emoji_base(char):
            width += 2
        else:
            width += 1
    return width


def _unwrap_spurious_table_rows(body: str) -> str:
    r"""Turn `| long prose | | |` rows back into plain paragraphs."""
    min_spurious_width = 3
    lines = body.split("\n")
    result: list[str] = []
    for line in lines:
        cells = _parse_table_cells(line)
        if (
            cells
            and len(cells) >= min_spurious_width
            and cells[0]
            and not any(cells[1:])
            and _looks_like_prose_table_row(cells[0])
        ):
            if result and _is_table_line(result[-1]):
                result.append("")
            result.append(cells[0])
            continue
        result.append(line)
    return "\n".join(result)
