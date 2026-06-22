---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_format.py`

## 🔧 Function `normalize_inline_spaces`

```python
def normalize_inline_spaces(text: str) -> str
```

Collapse consecutive spaces and tabs in phrasing text to a single space.

<details>
<summary>Code:</summary>

```python
def normalize_inline_spaces(text: str) -> str:
    return _MULTI_INLINE_SPACE_RE.sub(" ", text)
```

</details>
