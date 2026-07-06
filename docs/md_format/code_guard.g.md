---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `code_guard.py`

## 🏛️ Class `CodeBlock`

```python
class CodeBlock
```

Stored fenced code block extracted from Markdown body.

<details>
<summary>Code:</summary>

```python
class CodeBlock:

    index: int
    lines: list[str]
    base_indent: str
    tight: bool = False
```

</details>
