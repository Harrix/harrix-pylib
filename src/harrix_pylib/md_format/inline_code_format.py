"""Preserve inline code span padding from source."""

from __future__ import annotations

import re

PLACEHOLDER_PREFIX = "HSKMDFMTIC"


def extract_inline_code_spans(body: str) -> tuple[str, list[str]]:
    """Replace inline code spans with placeholders, keeping source inner text."""
    spans: list[str] = []

    def replace(match: re.Match[str]) -> str:
        spans.append(match.group(2))
        return f"{match.group(1)}{_placeholder(len(spans) - 1)}{match.group(1)}"

    return _INLINE_CODE_RE.sub(replace, body), spans


def restore_inline_code_spans(text: str, spans: list[str]) -> str:
    """Restore inline code placeholders to their source inner text."""
    if not spans:
        return text
    for index, span in enumerate(spans):
        text = text.replace(_placeholder(index), span)
    return text


def format_inline_code_content(content: str, spans: list[str]) -> str:
    """Return source inner text when content is a preserved inline-code placeholder."""
    if content.startswith(PLACEHOLDER_PREFIX):
        try:
            index = int(content.removeprefix(PLACEHOLDER_PREFIX))
        except ValueError:
            return content
        if 0 <= index < len(spans):
            return spans[index]
    return content


def _placeholder(index: int) -> str:
    return f"{PLACEHOLDER_PREFIX}{index}"


_INLINE_CODE_RE = re.compile(r"(`+)([^`]+?)\1")
