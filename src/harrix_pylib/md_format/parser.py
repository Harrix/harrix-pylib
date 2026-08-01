"""Markdown parser setup for `MdFormatter`.

Body syntax aligns with harrix-pyssg rendering (GFM tables/strikethrough/task
lists, footnotes, dollar math). Front matter is handled outside this parser via
custom extract/join in `front_matter.py`.

Uses `commonmark` + `gfm_plugin(dollarmath=True)` rather than the pyssg HTML
stack (`gfm-like` + individual plugins). Intentionally omitted vs pyssg render:

- `anchors` — HTML-only heading `id`s; printer ignores attrs
- `replacements` / `typographer` — would mutate source (`(c)`, `--`, `...`)
- `front_matter_plugin` — redundant with custom front-matter extract
- `tasklists_plugin` — injects `<input>` HTML; formatter uses built-in GFM
  tasklists plus placeholders

Formatter extras kept beyond pyssg: wiki links, GFM alerts, GFM autolink.

"""

from __future__ import annotations

from functools import lru_cache

from markdown_it import MarkdownIt
from mdit_py_plugins.gfm import gfm_plugin

from harrix_pylib.md_format.wiki_plugin import _wiki_link_plugin


@lru_cache(maxsize=1)
def _get_markdown_parser() -> MarkdownIt:
    """Return a configured `markdown-it` parser with GFM, math, and wiki-links."""
    md = MarkdownIt("commonmark")
    gfm_plugin(md, dollarmath=True)
    _wiki_link_plugin(md)
    return md
