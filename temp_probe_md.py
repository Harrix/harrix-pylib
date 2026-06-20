"""Probe markdown-it tokenization for GFM, math, and wiki-link samples."""

from markdown_it import MarkdownIt
from mdit_py_plugins.gfm import gfm_plugin

md = MarkdownIt("commonmark")
gfm_plugin(md, dollarmath=True)

samples = ["$$x$$", "# Hi", "[[wiki]]", "$a$", "|a|b|\n|---|---|\n|1|2|"]
for src in samples:
    tokens = md.parse(src)
    print(repr(src), "->", [t.type for t in tokens])
