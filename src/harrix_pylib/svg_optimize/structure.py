"""Collapse groups and remove empty attributes and containers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harrix_pylib.svg_optimize.xml_tags import tag_endswith

if TYPE_CHECKING:
    from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
DEFAULT_ATTRS = {
    "fill": "#000",
    "stroke": "none",
    "stroke-width": "1",
    "opacity": "1",
}
URL_REF_RE = re.compile(r"url\(#([^)]+)\)")


def optimize_structure(root: etree._Element) -> bool:
    """Collapse groups and strip empty attributes. Returns True if anything changed."""
    changed = False
    changed |= _shorten_ids(root)
    changed |= _collapse_single_child_groups(root)
    changed |= _remove_empty_containers(root)
    changed |= _strip_default_attrs(root)
    changed |= _cleanup_numeric_values(root)
    changed |= _cleanup_root_attrs(root)
    return changed


def _clean_number(value: str) -> str:
    text = value.replace("px", "").strip()
    try:
        number = float(text)
    except ValueError:
        return value
    if number == int(number):
        return str(int(number))
    return f"{number:.4f}".rstrip("0").rstrip(".")


def _cleanup_numeric_values(root: etree._Element) -> bool:
    changed = False
    numeric_attrs = ("x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2")
    for elem in root.iter():
        for attr in numeric_attrs:
            value = elem.get(attr)
            if value is None:
                continue
            cleaned = _clean_number(value)
            if cleaned != value:
                elem.set(attr, cleaned)
                changed = True
    return changed


def _cleanup_root_attrs(root: etree._Element) -> bool:
    changed = False
    svg = root if tag_endswith(root.tag, "svg") else root.find(f"{{{SVG_NS}}}svg")
    if svg is None:
        return False

    xlink_key = f"{{{XLINK_NS}}}href"
    uses_xlink = any(elem.get(xlink_key) for elem in root.iter())
    if not uses_xlink:
        for attr in list(svg.attrib):
            if "xlink" in attr:
                del svg.attrib[attr]
                changed = True

    svg_id = svg.get("id")
    if svg_id and not _is_id_referenced(root, svg_id):
        del svg.attrib["id"]
        changed = True
    return changed


def _collapse_single_child_groups(root: etree._Element) -> bool:
    changed = False
    for group in list(root.iter(f"{{{SVG_NS}}}g")):
        if len(group) != 1:
            continue
        child = group[0]
        if child.tag == f"{{{SVG_NS}}}g":
            continue
        _merge_element_attrs(group, child)
        parent = group.getparent()
        if parent is not None:
            parent.replace(group, child)
            changed = True
    return changed


def _index_to_short_id(index: int) -> str:
    chars = []
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        chars.append(chr(ord("a") + remainder))
    return "".join(reversed(chars)) or "a"


def _is_id_referenced(root: etree._Element, elem_id: str) -> bool:
    needle = f"#{elem_id}"
    for elem in root.iter():
        for value in elem.attrib.values():
            if needle in value:
                return True
    return False


def _merge_element_attrs(source: etree._Element, target: etree._Element) -> None:
    for attr, value in source.attrib.items():
        if attr == "class":
            existing = target.get("class", "")
            merged = f"{value} {existing}".strip() if existing else value
            target.set("class", merged)
        elif attr == "style":
            existing = target.get("style", "")
            target.set("style", f"{value};{existing}" if existing else value)
        elif attr not in target.attrib:
            target.set(attr, value)


def _remove_empty_containers(root: etree._Element) -> bool:
    removed = False
    for elem in list(root.iter(f"{{{SVG_NS}}}g")):
        if len(elem) == 0 and not (elem.text and elem.text.strip()) and not elem.get("id"):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
                removed = True
    return removed


def _shorten_ids(root: etree._Element) -> bool:
    id_map: dict[str, str] = {}
    counter = 0
    for elem in root.iter(f"{{{SVG_NS}}}defs"):
        for child in elem.iter():
            elem_id = child.get("id")
            if not elem_id or len(elem_id) <= 1:
                continue
            counter += 1
            id_map[elem_id] = _index_to_short_id(counter)

    if not id_map:
        return False

    for elem in root.iter():
        if elem.get("id") in id_map:
            elem.set("id", id_map[elem.get("id", "")])
        for attr, value in list(elem.attrib.items()):
            if "url(#" not in value:
                continue
            elem.set(attr, URL_REF_RE.sub(lambda match: f"url(#{id_map.get(match.group(1), match.group(1))})", value))
        style = elem.get("style")
        if style and "url(#" in style:
            elem.set(
                "style",
                URL_REF_RE.sub(lambda match: f"url(#{id_map.get(match.group(1), match.group(1))})", style),
            )

    return True


def _strip_default_attrs(root: etree._Element) -> bool:
    changed = False
    for elem in root.iter():
        for attr, default in DEFAULT_ATTRS.items():
            if elem.get(attr) == default:
                del elem.attrib[attr]
                changed = True
        if elem.get("fill-opacity") == "1":
            del elem.attrib["fill-opacity"]
            changed = True
    return changed
