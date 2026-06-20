"""Helpers for lxml element tag names."""

from __future__ import annotations

from lxml import etree


def tag_endswith(tag: str | bytes | bytearray | etree.QName, suffix: str) -> bool:
    """Return whether the tag's local name ends with suffix."""
    return tag_local_name(tag).endswith(suffix)


def tag_local_name(tag: str | bytes | bytearray | etree.QName) -> str:
    """Return the local part of an element tag."""
    if isinstance(tag, etree.QName):
        return tag.localname
    if isinstance(tag, bytes):
        tag_str = tag.decode()
    elif isinstance(tag, bytearray):
        tag_str = tag.decode()
    else:
        tag_str = str(tag)
    if "}" in tag_str:
        return tag_str.rsplit("}", 1)[-1]
    return tag_str
