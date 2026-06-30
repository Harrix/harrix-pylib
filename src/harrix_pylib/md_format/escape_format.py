"""Escape literal Markdown syntax in plain text."""

from __future__ import annotations

import re
import unicodedata

from harrix_pylib.md_format.code_guard import PLACEHOLDER_PREFIX

_PUNCTUATION = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\u3000\uff5e")
_IDENTIFIER_UNDERSCORE_BEFORE = frozenset(" \t\r\n(;,.")
_IDENTIFIER_UNDERSCORE_AFTER = frozenset("<")
_ARROW_PREFIX = "->"
_ASCII_MAX_CODE_POINT = 127
_ORDERED_LIST_LINE_START_RE = re.compile(r"^(\s*\d+)\.(.*)$")


PLACEHOLDER_PREFIXES = (
    "HSKMDFMTCODE",
    "HSKMDFMTREF",
    "HSKMDFMTIGN",
    "HSKMDFMTTASK",
)


def escape_markdown_text(text: str) -> str:
    """Escape emphasis-like ``*`` and ``_`` characters in plain text."""
    if any(text.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES):
        return text
    if text.startswith(PLACEHOLDER_PREFIX):
        return text

    parts: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            parts.append(char)
            parts.append(text[index + 1])
            index += 2
            continue
        if char == "*" and _should_escape_asterisk(text, index):
            parts.append("\\*")
        elif char == "_" and _should_escape_underscore(text, index):
            parts.append("\\_")
        else:
            parts.append(char)
        index += 1
    return "".join(parts)


def escape_ordered_list_like_line_starts(text: str) -> str:
    """Re-escape ``39.``-like line starts so they are not parsed as ordered lists."""
    if not text:
        return text
    return "\n".join(_escape_ordered_list_like_line_start(line) for line in text.split("\n"))


def _escape_ordered_list_like_line_start(line: str) -> str:
    match = _ORDERED_LIST_LINE_START_RE.match(line)
    if not match:
        return line
    after_period = match.group(2)
    if after_period and after_period[0].isdigit():
        return line
    return f"{match.group(1)}\\.{after_period}"


def _is_alphanumeric(char: str) -> bool:
    return char.isalnum()


def _is_failed_emphasis_underscore(text: str, index: int) -> bool:
    """Do not escape ``_`` in ``!_1_2``-style literals that are not emphasis."""
    if text[index] != "_":
        return False
    if index + 2 < len(text) and text[index + 2] == "_" and len(text[index + 1]) == 1:
        return True
    return index >= 2 and text[index - 2] == "_" and text[index - 1] != "_" and len(text[index - 1]) == 1


def _is_identifier_leading_underscore(text: str, index: int) -> bool:
    if text[index] != "_" or index + 1 >= len(text):
        return False

    next_char = text[index + 1]
    if next_char == "[":
        return False
    if not (next_char.isalnum() or next_char in _IDENTIFIER_UNDERSCORE_AFTER):
        return False

    if index == 0:
        return True

    previous = text[index - 1]
    if previous in _IDENTIFIER_UNDERSCORE_BEFORE:
        return True

    return index >= len(_ARROW_PREFIX) and text[index - len(_ARROW_PREFIX) : index] == _ARROW_PREFIX


def _is_left_flanking(text: str, index: int) -> bool:
    if index + 1 < len(text) and _is_whitespace(text[index + 1]):
        return False
    if (
        index + 1 < len(text)
        and not _is_punctuation(text[index + 1])
        and (index == 0 or _is_whitespace(text[index - 1]) or _is_punctuation(text[index - 1]))
    ):
        return True
    return index > 0 and (_is_whitespace(text[index - 1]) or _is_punctuation(text[index - 1]))


def _is_punctuation(char: str) -> bool:
    if char in _PUNCTUATION:
        return True
    return unicodedata.category(char).startswith("P")


def _is_right_flanking(text: str, index: int) -> bool:
    if index > 0 and _is_whitespace(text[index - 1]):
        return False
    if (
        index > 0
        and not _is_punctuation(text[index - 1])
        and (index + 1 >= len(text) or _is_whitespace(text[index + 1]) or _is_punctuation(text[index + 1]))
    ):
        return True
    return index + 1 < len(text) and (_is_whitespace(text[index + 1]) or _is_punctuation(text[index + 1]))


def _is_single_char_emphasis_underscore(text: str, index: int) -> bool:
    return _is_failed_emphasis_underscore(text, index)


def _is_whitespace(char: str) -> bool:
    return char.isspace()


def _should_escape_asterisk(text: str, index: int) -> bool:
    if _should_escape_intraword_asterisk(text, index):
        return True
    return _is_left_flanking(text, index) or _is_right_flanking(text, index)


def _should_escape_intraword_asterisk(text: str, index: int) -> bool:
    """Escape ``*`` between letters when at least one side is non-ASCII."""
    if index == 0 or index + 1 >= len(text):
        return False

    previous = text[index - 1]
    next_char = text[index + 1]
    if not (_is_alphanumeric(previous) and _is_alphanumeric(next_char)):
        return False

    return ord(previous) > _ASCII_MAX_CODE_POINT or ord(next_char) > _ASCII_MAX_CODE_POINT


def _should_escape_underscore(text: str, index: int) -> bool:
    if _is_single_char_emphasis_underscore(text, index):
        return False
    if index + 1 < len(text) and text[index + 1] == "[":
        return False
    if index > 0 and text[index - 1] == "[" and index + 1 < len(text) and _is_alphanumeric(text[index + 1]):
        return True
    if _is_identifier_leading_underscore(text, index):
        return True
    if index > 0 and text[index - 1] == "." and index + 1 < len(text) and _is_alphanumeric(text[index + 1]):
        return True
    if index > 0 and _is_alphanumeric(text[index - 1]) and index + 1 < len(text) and _is_punctuation(text[index + 1]):
        return True
    if index > 0 and _is_alphanumeric(text[index - 1]):
        return False

    left = _is_left_flanking(text, index)
    right = _is_right_flanking(text, index)
    can_open = left and (not right or (index > 0 and _is_punctuation(text[index - 1])))
    can_close = right and (not left or (index + 1 < len(text) and _is_punctuation(text[index + 1])))
    return can_open or can_close
