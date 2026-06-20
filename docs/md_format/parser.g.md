---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `parser.py`

## 🔧 Function `get_markdown_parser`

```python
def get_markdown_parser() -> MarkdownIt
```

Return a configured markdown-it parser with GFM, math, and wiki-links.

<details>
<summary>Code:</summary>

```python
def get_markdown_parser() -> MarkdownIt:
    md = MarkdownIt("commonmark")
    gfm_plugin(md, dollarmath=True)
    wiki_link_plugin(md)
    return md
```

</details>
