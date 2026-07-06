---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `hard_break_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HardBreakStyles`](#️-class-hardbreakstyles)
  - [⚙️ Method `next_is_backslash`](#️-method-next_is_backslash)

</details>

## 🏛️ Class `HardBreakStyles`

```python
class HardBreakStyles
```

Queue of hard-break render styles in document order.

<details>
<summary>Code:</summary>

```python
class HardBreakStyles:

    backslash_breaks: list[bool] = field(default_factory=list)

    def next_is_backslash(self) -> bool:
        """Return whether the next hard break should use a backslash."""
        if not self.backslash_breaks:
            return False
        return self.backslash_breaks.pop(0)
```

</details>

### ⚙️ Method `next_is_backslash`

```python
def next_is_backslash(self) -> bool
```

Return whether the next hard break should use a backslash.

<details>
<summary>Code:</summary>

```python
def next_is_backslash(self) -> bool:
        if not self.backslash_breaks:
            return False
        return self.backslash_breaks.pop(0)
```

</details>
