"""Formatting options."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FormatOptions:
    """Markdown formatting options."""

    end_of_line: str = "crlf"
    prose_wrap: str = "preserve"
    print_width: int = 80
