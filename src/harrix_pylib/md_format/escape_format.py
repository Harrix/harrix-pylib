"""Escape literal Markdown syntax in plain text."""

from __future__ import annotations

import unicodedata

from harrix_pylib.md_format.code_guard import PLACEHOLDER_PREFIX

_PUNCTUATION = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\u3000\uff5e")
_UNDERSCORE_LITERAL_PREFIXES = frozenset("[.<")
_MIN_MACRO_TOKEN_LEN = 2


def escape_markdown_text(text: str) -> str:
    """Escape emphasis-like ``*`` and ``_`` characters in plain text."""
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


def _is_all_caps_macro_underscore(text: str, index: int) -> bool:
    """Match C-style macros like ``_WIN32`` and ``_DEBUG``."""
    if text[index] != "_" or index + 1 >= len(text):
        return False
    if index > 0 and (text[index - 1].isalnum() or text[index - 1] == "_"):
        return False

    end = index + 1
    while end < len(text) and (text[end].isalnum() or text[end] == "_"):
        end += 1

    token = text[index:end]
    if len(token) < _MIN_MACRO_TOKEN_LEN or "_" in token[1:]:
        return False

    suffix = token[1:]
    return any(char.isalpha() for char in suffix) and suffix.isupper()


def _is_alphanumeric(char: str) -> bool:
    return char.isalnum()


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


def _is_whitespace(char: str) -> bool:
    return char.isspace()


def _should_escape_asterisk(text: str, index: int) -> bool:
    return _is_left_flanking(text, index) or _is_right_flanking(text, index)


def _should_escape_underscore(text: str, index: int) -> bool:
    if index > 0 and text[index - 1] == "[" and index + 1 < len(text) and _is_alphanumeric(text[index + 1]):
        return True
    if _is_all_caps_macro_underscore(text, index):
        return True
    if index + 1 < len(text) and _is_alphanumeric(text[index + 1]):
        return False
    if index + 1 < len(text) and text[index + 1] in _UNDERSCORE_LITERAL_PREFIXES:
        return False
    if index > 0 and _is_alphanumeric(text[index - 1]) and index + 1 < len(text) and _is_punctuation(text[index + 1]):
        return True
    if index > 0 and _is_alphanumeric(text[index - 1]):
        return False

    left = _is_left_flanking(text, index)
    right = _is_right_flanking(text, index)
    can_open = left and (not right or (index > 0 and _is_punctuation(text[index - 1])))
    can_close = right and (not left or (index + 1 < len(text) and _is_punctuation(text[index + 1])))
    return can_open or can_close
