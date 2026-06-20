---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `wiki_plugin.py`

## 🔧 Function `wiki_link_plugin`

```python
def wiki_link_plugin(md: MarkdownIt) -> None
```

Register wiki-link parsing before standard links.

<details>
<summary>Code:</summary>

```python
def wiki_link_plugin(md: MarkdownIt) -> None:

    def wiki_rule(state: StateInline, silent: bool) -> bool:  # noqa: FBT001
        if state.pos + 4 > len(state.src):
            return False
        if state.src[state.pos : state.pos + 2] != "[[":
            return False
        match = _WIKI_PATTERN.match(state.src, state.pos)
        if not match:
            return False
        if silent:
            return True
        token = state.push("wiki_link", "", 0)
        token.content = match.group(1)
        state.pos = match.end()
        return True

    md.inline.ruler.before("link", "wiki_link", wiki_rule)
```

</details>
