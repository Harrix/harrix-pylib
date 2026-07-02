"""Printer submodule: tokens."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from markdown_it.token import Token


def _alignment_separator(align: str) -> str:
    if align == "left":
        return ":--"
    if align == "center":
        return ":-:"
    if align == "right":
        return "--:"
    return "---"


def _choose_emphasis_delimiter(markup: str, prev: str, next_text: str) -> str:
    if markup == "_":
        return "_"
    if prev and prev[-1] in "!∩╝ü" and next_text and next_text[0] in "!∩╝ü":
        return "_"
    if not _has_digit_emphasis_neighbor(prev, next_text):
        return "_"
    return "*"


def _contains_strong(children: list[Token], start: int, end: int) -> bool:
    return any(children[index].type == "strong_open" for index in range(start, end + 1))


def _find_close(tokens: list[Token], index: int, close_type: str) -> int:
    depth = 0
    open_type = close_type.replace("_close", "_open")
    for current in range(index, len(tokens)):
        if tokens[current].type == open_type:
            depth += 1
        elif tokens[current].type == close_type:
            depth -= 1
            if depth == 0:
                return current
    return len(tokens) - 1


def _format_hr_markup(markup: str, *, preserve: bool = False) -> str:
    if not preserve:
        return "---"
    chars = {char for char in markup if not char.isspace()}
    if chars == {"*"}:
        return "***"
    if chars == {"-"}:
        return "---"
    if chars == {"_"}:
        return "___"
    stripped = markup.strip()
    return stripped or "---"


def _has_digit_emphasis_neighbor(prev: str, next_text: str) -> bool:
    return bool(prev and prev[-1].isdigit()) or bool(next_text and next_text[0].isdigit())


def _is_block_marker_line(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith(("-", ">", "|", "#", "```", "~"))


def _link_raw_text(children: list[Token], link_open_index: int) -> str | None:
    """Return raw link label text when it contains only text and soft breaks."""
    parts: list[str] = []
    inner_index = link_open_index + 1
    while inner_index < len(children) and children[inner_index].type != "link_close":
        token = children[inner_index]
        if token.type == "text":
            parts.append(token.content)
        elif token.type == "softbreak":
            parts.append("\n")
        else:
            return None
        inner_index += 1
    return "".join(parts)


def _normalize_bullet_marker(marker: str, *, normalize_star_to_dash: bool = False) -> str:
    if marker == "+":
        return "*"
    if normalize_star_to_dash and marker == "*":
        return "-"
    return marker
