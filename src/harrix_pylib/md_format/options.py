"""Formatting options."""

from __future__ import annotations

from dataclasses import dataclass

PROSE_WRAP_CHOICES = frozenset({"always", "never", "preserve"})
DEFAULT_PRINT_WIDTH = 80


@dataclass(frozen=True, slots=True)
class FormatOptions:
    """Markdown formatting options."""

    end_of_line: str = "crlf"
    prose_wrap: str = "preserve"
    print_width: int = DEFAULT_PRINT_WIDTH

    def __post_init__(self) -> None:
        if self.prose_wrap not in PROSE_WRAP_CHOICES:
            msg = f"Unsupported prose_wrap value: {self.prose_wrap}"
            raise ValueError(msg)
        if self.print_width <= 0:
            msg = f"print_width must be positive: {self.print_width}"
            raise ValueError(msg)
