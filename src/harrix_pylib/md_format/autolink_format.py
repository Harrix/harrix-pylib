"""Preserve angle-bracket autolinks from source."""

from __future__ import annotations

import re

PLACEHOLDER_PREFIX = "HSKMDFMTAL"
_ANGLE_AUTOLINK_RE = re.compile(
    r"<("
    r"https?://[^<>\s]+"
    r"|mailto:[^<>\s]+"
    r"|[^<>\s]+@[^<>\s]+\.[^<>\s]+"
    r")>"
)


def extract_angle_autolinks(body: str) -> tuple[str, list[str]]:
    """Replace angle-bracket autolinks with placeholders before parsing."""
    autolinks: list[str] = []

    def replace(match: re.Match[str]) -> str:
        autolinks.append(match.group(0))
        return f"{PLACEHOLDER_PREFIX}{len(autolinks) - 1}"

    return _ANGLE_AUTOLINK_RE.sub(replace, body), autolinks


def restore_angle_autolinks(text: str, autolinks: list[str]) -> str:
    """Restore angle-bracket autolinks after rendering."""
    if not autolinks:
        return text
    for index, autolink in enumerate(autolinks):
        text = text.replace(f"{PLACEHOLDER_PREFIX}{index}", autolink)
    return text
