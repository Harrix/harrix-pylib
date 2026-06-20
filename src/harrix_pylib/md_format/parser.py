"""Markdown parser setup."""

from __future__ import annotations

from functools import lru_cache

from markdown_it import MarkdownIt
from mdit_py_plugins.gfm import gfm_plugin

from harrix_pylib.md_format.wiki_plugin import wiki_link_plugin


@lru_cache(maxsize=1)
def get_markdown_parser() -> MarkdownIt:
    """Return a configured `markdown-it` parser with GFM, math, and wiki-links."""
    md = MarkdownIt("commonmark")
    gfm_plugin(md, dollarmath=True)
    wiki_link_plugin(md)
    return md
