"""Preserve angle-bracket autolinks from source."""

from __future__ import annotations

import re

from harrix_pylib.md_format.link_destination_format import _decode_percent_encoded_url

PLACEHOLDER_PREFIX = "HSKMDFMTAL"
_PLACEHOLDER_RE = re.compile(rf"{re.escape(PLACEHOLDER_PREFIX)}(\d+)")
_ANGLE_AUTOLINK_RE = re.compile(
    r"<("
    r"https?://[^<>\s]+"
    r"|mailto:[^<>\s]+"
    r"|[^<>\s]+@[^<>\s]+\.[^<>\s]+"
    r")>"
)


def _decode_angle_autolink(autolink: str) -> str:
    """Decode percent-encoded characters inside an angle-bracket autolink."""
    if not autolink.startswith("<") or not autolink.endswith(">"):
        return autolink
    return f"<{_decode_percent_encoded_url(autolink[1:-1])}>"


def _extract_angle_autolinks(body: str) -> tuple[str, list[str]]:
    """Replace angle-bracket autolinks with placeholders before parsing."""
    autolinks: list[str] = []

    def replace(match: re.Match[str]) -> str:
        """``re.sub`` callback that stores an autolink and returns its placeholder."""
        autolinks.append(_decode_angle_autolink(match.group(0)))
        return f"{PLACEHOLDER_PREFIX}{len(autolinks) - 1}"

    return _ANGLE_AUTOLINK_RE.sub(replace, body), autolinks


def _restore_angle_autolinks(text: str, autolinks: list[str]) -> str:
    """Restore angle-bracket autolinks after rendering."""
    if not autolinks:
        return text

    def replace(match: re.Match[str]) -> str:
        """``re.sub`` callback that restores a stored autolink from its placeholder."""
        index = int(match.group(1))
        if 0 <= index < len(autolinks):
            return autolinks[index]
        return match.group(0)

    return _PLACEHOLDER_RE.sub(replace, text)
