---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `options.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FormatOptions`](#%EF%B8%8F-class-formatoptions)
  - [⚙️ Method `__post_init__`](#%EF%B8%8F-method-__post_init__)

</details>

## 🏛️ Class `FormatOptions`

```python
class FormatOptions
```

Markdown formatting options.

<details>
<summary>Code:</summary>

```python
class FormatOptions:

    end_of_line: str = "crlf"
    prose_wrap: str = "preserve"
    print_width: int = DEFAULT_PRINT_WIDTH

    def __post_init__(self) -> None:
        if self.prose_wrap not in PROSE_WRAP_CHOICES:
            msg = f"Unsupported prose_wrap value: {self.prose_wrap}"
            raise ValueError(msg)
        if self.print_width <= 0:
            msg = f"print_width must be positive: {self.print_width}"
            raise ValueError(msg)
```

</details>

### ⚙️ Method `__post_init__`

```python
def __post_init__(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __post_init__(self) -> None:
        if self.prose_wrap not in PROSE_WRAP_CHOICES:
            msg = f"Unsupported prose_wrap value: {self.prose_wrap}"
            raise ValueError(msg)
        if self.print_width <= 0:
            msg = f"print_width must be positive: {self.print_width}"
            raise ValueError(msg)
```

</details>
