---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `reference_format.py`

## 🏛️ Class `ReferenceBlock`

```python
class ReferenceBlock
```

Stored reference-definition block.

<details>
<summary>Code:</summary>

```python
class ReferenceBlock:

    index: int
    lines: list[str]
    kind: str  # "link" or "footnote"
```

</details>
