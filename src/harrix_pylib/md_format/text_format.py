"""Normalize inline Markdown text."""

from __future__ import annotations

import re

_MULTI_INLINE_SPACE_RE = re.compile(r"[ \t]+")


def normalize_inline_spaces(text: str) -> str:
    """Collapse consecutive spaces and tabs in phrasing text to a single space."""
    return _MULTI_INLINE_SPACE_RE.sub(" ", text)
