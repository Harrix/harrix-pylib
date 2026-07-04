"""Shared printer constants and state."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harrix_pylib.md_format.options import FormatOptions

if TYPE_CHECKING:
    from harrix_pylib.md_format.link_destination_format import LinkDestination

DEFAULT_OPTIONS = FormatOptions()
SINGLE_TICK_INLINE_CODE_RE = re.compile(r"^`(?:[^`]|`(?!`))*`$")
EMPTY_IMAGE_REFERENCE_RE = re.compile(r"^(?P<prefix>.*?!\[)(?P<alt>.*?)(\]\[\])$")
LIST_ITEM_CONTENT_RE = re.compile(r"^(\s*)[-+*]\s+(.*)$")
ACTIVE_LINK_DESTINATIONS: dict[int, LinkDestination] | None = None
ACTIVE_ANGLE_AUTOLINKS: list[str] | None = None
