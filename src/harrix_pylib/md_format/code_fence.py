"""Detect fenced and inline code regions in Markdown source."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

_MIN_FENCE_LENGTH = 3


def _fence_marker_for_content(content: str, *, marker: str = "`") -> str:
    """Return the shortest fence of `marker` chars that can wrap `content`."""
    return marker * max(_MIN_FENCE_LENGTH, _max_marker_run(content, marker) + 1)


def _identify_code_blocks(lines: Sequence[str]) -> Iterator[tuple[str, bool]]:
    """Yield each line with a flag indicating fenced code-block membership."""
    code_block_delimiter = None
    for line in lines:
        match = re.match(r"^\s*(`{3,})(.*)", line)
        if match:
            delimiter = match.group(1)
            if code_block_delimiter is None:
                code_block_delimiter = delimiter
            elif code_block_delimiter == delimiter:
                code_block_delimiter = None
            yield line, True
            continue
        if code_block_delimiter:
            yield line, True
        else:
            yield line, False


def _identify_code_blocks_line(markdown_line: str) -> Iterator[tuple[str, bool]]:
    """Parse a single Markdown line into text and inline-code segments."""
    # Most prose lines have no backticks; avoid the character-by-character scan.
    if "`" not in markdown_line:
        if markdown_line:
            yield markdown_line, False
        return

    current_text = ""
    in_code = False
    backtick_count = 0

    index = 0
    while index < len(markdown_line):
        if markdown_line[index] == "`":
            count = 1
            while index + 1 < len(markdown_line) and markdown_line[index + 1] == "`":
                count += 1
                index += 1

            if not in_code:
                if current_text:
                    yield current_text, False
                    current_text = ""
                backtick_count = count
                current_text = "`" * count
                in_code = True
            elif count == backtick_count:
                current_text += "`" * count
                yield current_text, True
                current_text = ""
                in_code = False
            else:
                current_text += "`" * count
        else:
            current_text += markdown_line[index]

        index += 1

    if current_text:
        yield current_text, False


def _max_marker_run(text: str, marker: str) -> int:
    """Return the longest run of `marker` characters in `text`."""
    max_run = 0
    current = 0
    for char in text:
        if char == marker:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run
