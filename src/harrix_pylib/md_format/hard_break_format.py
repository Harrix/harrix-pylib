"""Preserve backslash-style hard line breaks from source."""

from __future__ import annotations

from dataclasses import dataclass, field

from harrix_pylib.md_format.text_lines import join_lines, split_lines


@dataclass
class HardBreakStyles:
    """Queue of hard-break render styles in document order."""

    backslash_breaks: list[bool] = field(default_factory=list)

    def next_is_backslash(self) -> bool:
        if not self.backslash_breaks:
            return False
        return self.backslash_breaks.pop(0)


def extract_backslash_hard_breaks(body: str) -> tuple[str, HardBreakStyles]:
    """Record hard-break styles and normalize single trailing backslashes for parsing."""
    lines, trailing = split_lines(body)
    styles = HardBreakStyles()
    converted: list[str] = []
    for index, line in enumerate(lines):
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if _line_has_single_backslash_hard_break(line, next_line=next_line):
            styles.backslash_breaks.append(True)
            converted.append(line[:-1] + "  ")
            continue
        if _line_has_space_hard_break(line, next_line=next_line):
            styles.backslash_breaks.append(False)
        converted.append(line)
    return join_lines(converted, trailing_newline=trailing), styles


def _line_has_single_backslash_hard_break(line: str, *, next_line: str) -> bool:
    if not next_line.strip():
        return False
    if not line.endswith("\\"):
        return False
    return not line.endswith("\\\\")


def _line_has_space_hard_break(line: str, *, next_line: str) -> bool:
    if not next_line.strip():
        return False
    return line.endswith("  ") or line.endswith("\t")
