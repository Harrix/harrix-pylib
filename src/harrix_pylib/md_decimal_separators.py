"""Decimal separator checks and autofixes for Markdown prose (H062).

Both `lang: en` and `lang: ru` require a decimal point (`.`). Thousands commas
are allowed (`1,234`, `1,234.5`). Comma used as a decimal (`0,5`, `-0,5`) is
flagged and rewritten to a point.

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterator

DecimalIssueKind = Literal["fix_comma_to_dot"]

# Compact number with at least one `,` or `.` digit group; no space after separators.
# Trailing sentence `.` / `!` / `?` are allowed; `.` + digit continues the number.
_COMPACT_NUMBER_PATTERN = re.compile(r"(?<![\d.,])(-?\d+(?:[.,]\d+)+)(?![,\d]|\.(?=\d))")

# English thousands: 1,234 or 1,234.56
_EN_THOUSANDS_PATTERN = re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$")

_SIMPLE_COMMA_DECIMAL_PATTERN = re.compile(r"^(-?)(\d+),(\d+)$")


def classify_decimal_separator_issue(token: str, lang: str) -> DecimalIssueKind | None:
    """Return autofix kind for a compact numeric token, or `None` if allowed."""
    if lang not in {"en", "ru"}:
        return None
    if _EN_THOUSANDS_PATTERN.fullmatch(token):
        return None
    if "," in token:
        return "fix_comma_to_dot"
    return None


def fix_decimal_separators(segment: str, lang: str) -> str:
    """Rewrite comma decimals to points in `segment` for `lang` (`en` / `ru`)."""
    if lang not in {"en", "ru"} or not segment:
        return segment

    def replacer(match: re.Match[str]) -> str:
        token = match.group(0)
        kind = classify_decimal_separator_issue(token, lang)
        if kind == "fix_comma_to_dot":
            simple = _SIMPLE_COMMA_DECIMAL_PATTERN.fullmatch(token)
            if simple:
                return f"{simple.group(1)}{simple.group(2)}.{simple.group(3)}"
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
