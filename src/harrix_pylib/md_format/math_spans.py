"""Protect TeX/LaTeX dollar-math spans from Markdown typography autofixes."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

# Single-line `$$...$$` or inline `$...$` (non-empty, non-space abutting `$`).
_INLINE_OR_SINGLE_LINE_MATH_RE = re.compile(r"(?<!\\)(?:\$\$(?:\\.|[^$\\])+?\$\$|\$(?!\$)(?:\\.|[^$\n\\])+?\$(?!\$))")
_DISPLAY_MATH_DELIMITER_RE = re.compile(r"^\s*\$\$\s*$")
_EMPTY_SINGLE_LINE_DISPLAY_MATH_LEN = 4


def display_math_line_flags(lines: Sequence[str], *, in_code: Sequence[bool] | None = None) -> list[bool]:
    """Return per-line flags for display-math `$$...$$` regions (including delimiters)."""
    flags = [False] * len(lines)
    inside = False
    for index, line in enumerate(lines):
        if in_code is not None and in_code[index]:
            continue
        if _DISPLAY_MATH_DELIMITER_RE.match(line):
            flags[index] = True
            inside = not inside
            continue
        stripped = line.strip()
        if (
            stripped.startswith("$$")
            and stripped.endswith("$$")
            and len(stripped) > _EMPTY_SINGLE_LINE_DISPLAY_MATH_LEN
        ):
            flags[index] = True
            continue
        if inside:
            flags[index] = True
    return flags


def iter_code_and_math_segments(
    code_segments: Iterator[tuple[str, bool]] | Sequence[tuple[str, bool]],
) -> Iterator[tuple[str, bool]]:
    """Yield `(segment, protected)` where protected is inline code or dollar-math."""
    for segment, in_code in code_segments:
        if in_code:
            yield segment, True
            continue
        yield from _split_math_segments(segment)


def _split_math_segments(text: str) -> Iterator[tuple[str, bool]]:
    """Split plain text into math / non-math segments."""
    if "$" not in text:
        yield text, False
        return
    last = 0
    for match in _INLINE_OR_SINGLE_LINE_MATH_RE.finditer(text):
        if match.start() > last:
            yield text[last : match.start()], False
        yield match.group(0), True
        last = match.end()
    if last < len(text):
        yield text[last:], False
