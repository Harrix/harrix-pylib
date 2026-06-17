"""Remove metadata, comments, and deprecated SVG attributes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_pylib.svg_optimize.xml_tags import tag_endswith

if TYPE_CHECKING:
    from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"

REMOVE_TAGS = frozenset({"metadata", "desc", "title", "sodipodi:namedview", "namedview"})
DEPRECATED_ATTRS = frozenset({"version", "enable-background"})
EDITOR_NS_PREFIXES = ("adobe", "illustrator", "sodipodi", "inkscape", "sketch", "figma")


def cleanup(root: etree._Element) -> None:
    """Remove metadata elements and deprecated attributes from the SVG tree."""
    for tag in REMOVE_TAGS:
        for elem in root.iter(tag):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

    for elem in root.iter():
        for attr in list(elem.attrib):
            local = attr.split("}")[-1] if "}" in attr else attr
            if local in DEPRECATED_ATTRS or any(
                attr.startswith(f"{{{prefix}") or prefix in attr.lower() for prefix in EDITOR_NS_PREFIXES
            ):
                del elem.attrib[attr]

    svg = root if tag_endswith(root.tag, "svg") else root.find(f"{{{SVG_NS}}}svg")
    if svg is not None and "version" in svg.attrib:
        del svg.attrib["version"]
