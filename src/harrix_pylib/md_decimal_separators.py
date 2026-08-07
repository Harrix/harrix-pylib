"""Locale-aware decimal separator checks and autofixes for Markdown prose (H062).

`lang: en` — decimal point; thousands commas allowed (`1,234`, `1,234.5`).
`lang: ru` — decimal comma; English thousands commas are not a special case;
European dot-grouped thousands (`1.234`, `1.234,5`) are left unchanged.

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterator

DecimalIssueKind = Literal["fix_en_comma_to_dot", "fix_ru_dot_to_comma"]

# Compact number with at least one `,` or `.` digit group; no space after separators.
_COMPACT_NUMBER_PATTERN = re.compile(r"(?<![\d.,])(-?\d+(?:[.,]\d+)+)(?![\d.,])")

# English thousands: 1,234 or 1,234.56
_EN_THOUSANDS_PATTERN = re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$")

# European thousands (allowed for ru, not autofixed): 1.234 or 1.234,56
_EU_THOUSANDS_PATTERN = re.compile(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$")

_SIMPLE_COMMA_DECIMAL_PATTERN = re.compile(r"^(-?)(\d+),(\d+)$")
_SIMPLE_DOT_DECIMAL_PATTERN = re.compile(r"^(-?)(\d+)\.(\d+)$")

# Two or more dots → version / dotted ID (3.12.1, 192.168.0.1), not a decimal
_MIN_DOTS_FOR_VERSION_OR_IP = 2


def classify_decimal_separator_issue(token: str, lang: str) -> DecimalIssueKind | None:
    """Return autofix kind for a compact numeric token, or `None` if allowed."""
    if lang not in {"en", "ru"}:
        return None
    if token.count(".") >= _MIN_DOTS_FOR_VERSION_OR_IP:
        return None
    if lang == "en":
        if _EN_THOUSANDS_PATTERN.fullmatch(token):
            return None
        if "," in token:
            return "fix_en_comma_to_dot"
        return None
    if lang == "ru":
        if _EU_THOUSANDS_PATTERN.fullmatch(token):
            return None
        if token.count(".") == 1 and "," not in token:
            return "fix_ru_dot_to_comma"
    return None


def fix_decimal_separators(segment: str, lang: str) -> str:
    """Rewrite wrong decimal separators in `segment` for `lang` (`en` / `ru`)."""
    if lang not in {"en", "ru"} or not segment:
        return segment

    def replacer(match: re.Match[str]) -> str:
        token = match.group(0)
        kind = classify_decimal_separator_issue(token, lang)
        if kind == "fix_en_comma_to_dot":
            simple = _SIMPLE_COMMA_DECIMAL_PATTERN.fullmatch(token)
            if simple:
                return f"{simple.group(1)}{simple.group(2)}.{simple.group(3)}"
            return token
        if kind == "fix_ru_dot_to_comma":
            simple = _SIMPLE_DOT_DECIMAL_PATTERN.fullmatch(token)
            if simple:
                return f"{simple.group(1)}{simple.group(2)},{simple.group(3)}"
            return token
        return token

    return _COMPACT_NUMBER_PATTERN.sub(replacer, segment)


def iter_decimal_separator_issues(segment: str, lang: str) -> Iterator[tuple[int, int, str, DecimalIssueKind]]:
    """Yield `(start, end, token, kind)` for wrong decimal separators in `segment`."""
    if lang not in {"en", "ru"}:
        return
    for match in _COMPACT_NUMBER_PATTERN.finditer(segment):
        token = match.group(0)
        kind = classify_decimal_separator_issue(token, lang)
        if kind is not None:
            yield match.start(), match.end(), token, kind
