"""Preserve backslash-style hard line breaks from source."""

from __future__ import annotations

from dataclasses import dataclass, field

from harrix_pylib.md_format.code_fence import _identify_code_blocks
from harrix_pylib.md_format.text_lines import _join_lines, _split_lines


@dataclass
class _HardBreakStyles:
    """Queue of hard-break render styles in document order."""

    backslash_breaks: list[bool] = field(default_factory=list)

    def next_is_backslash(self) -> bool:
        """Return whether the next hard break should use a backslash."""
        if not self.backslash_breaks:
            return False
        return self.backslash_breaks.pop(0)


def _extract_backslash_hard_breaks(body: str) -> tuple[str, _HardBreakStyles]:
    """Record hard-break styles and normalize single trailing backslashes for parsing."""
    lines, trailing = _split_lines(body)
    code_block_info = list(_identify_code_blocks(lines))
    styles = _HardBreakStyles()
    converted: list[str] = []
    for index, line in enumerate(lines):
        if code_block_info[index][1]:
            converted.append(line)
            continue
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if _line_has_single_backslash_hard_break(line, next_line=next_line):
            styles.backslash_breaks.append(True)
            converted.append(line[:-1] + "  ")
            continue
        if _line_has_space_hard_break(line, next_line=next_line):
            styles.backslash_breaks.append(False)
        converted.append(line)
    return _join_lines(converted, trailing_newline=trailing), styles


def _line_has_single_backslash_hard_break(line: str, *, next_line: str) -> bool:
    if not next_line.strip():
        return False
    if not line.endswith("\\"):
        return False
    return not line.endswith("\\\\")


def _line_has_space_hard_break(line: str, *, next_line: str) -> bool:
    if not next_line.strip():
        return False
    return line.endswith(("  ", "\t"))
