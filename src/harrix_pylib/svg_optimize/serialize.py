"""Serialize SVG to minified single-line XML."""

from __future__ import annotations

import re
from typing import cast

from lxml import etree


def serialize(root: etree._Element) -> str:
    """Serialize SVG element tree to a minified single-line string."""
    xlink_key = "{http://www.w3.org/1999/xlink}href"
    uses_xlink = any(elem.get(xlink_key) for elem in root.iter())
    data = cast(
        "str",
        etree.tostring(root, encoding="unicode", xml_declaration=False, pretty_print=False),
    )
    data = data.replace("\n", "").replace("\r", "")
    data = re.sub(r">\s+<", "><", data)
    if not uses_xlink:
        data = re.sub(r'\sxmlns:xlink="[^"]*"', "", data)
    return data.strip()
