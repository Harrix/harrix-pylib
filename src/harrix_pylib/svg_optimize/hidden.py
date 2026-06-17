"""Remove hidden and zero-sized SVG elements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_pylib.svg_optimize.xml_tags import tag_endswith, tag_local_name

if TYPE_CHECKING:
    from lxml import etree

    from harrix_pylib.svg_optimize.styles import StyleSheet

SVG_NS = "http://www.w3.org/2000/svg"
SHAPE_TAGS = frozenset(
    {
        f"{{{SVG_NS}}}path",
        f"{{{SVG_NS}}}rect",
        f"{{{SVG_NS}}}circle",
        f"{{{SVG_NS}}}ellipse",
        f"{{{SVG_NS}}}polygon",
        f"{{{SVG_NS}}}polyline",
        f"{{{SVG_NS}}}line",
        f"{{{SVG_NS}}}g",
    }
)


def remove_hidden(root: etree._Element, stylesheet: StyleSheet) -> bool:
    """Remove elements that are not rendered. Returns True if any element was removed."""
    removed = False
    for elem in list(root.iter()):
        if elem.tag not in SHAPE_TAGS and not tag_endswith(elem.tag, "g"):
            continue
        style = stylesheet.compute_style(elem)
        if _is_hidden(style, elem):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
                removed = True
                continue
        if _is_zero_sized(elem):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
                removed = True
    return removed


def _float(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return float(value.replace("px", "").strip())
    except ValueError:
        return 0.0


def _is_hidden(style: dict[str, str], elem: etree._Element) -> bool:
    display = style.get("display", elem.get("display", ""))
    if display == "none":
        return True
    opacity = style.get("opacity", elem.get("opacity", ""))
    if opacity in {"0", "0.0", "0.00"}:
        return True
    visibility = style.get("visibility", elem.get("visibility", ""))
    return visibility == "hidden"


def _is_zero_sized(elem: etree._Element) -> bool:
    tag = tag_local_name(elem.tag)
    if tag == "rect":
        width = _float(elem.get("width"))
        height = _float(elem.get("height"))
        return width == 0 or height == 0
    if tag == "circle":
        return _float(elem.get("r")) == 0
    if tag == "ellipse":
        return _float(elem.get("rx")) == 0 or _float(elem.get("ry")) == 0
    if tag == "path":
        return elem.get("d", "").strip() == ""
    if tag in {"polygon", "polyline"}:
        return elem.get("points", "").strip() == ""
    return False
