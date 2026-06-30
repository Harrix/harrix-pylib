"""Preserve backslash-style hard line breaks from source."""

from __future__ import annotations

from dataclasses import dataclass, field


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
    lines, trailing = _split_lines(body)
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
    return _join_lines(converted, trailing_newline=trailing), styles


def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


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


def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
