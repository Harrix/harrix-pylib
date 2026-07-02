---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_lines.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_blank_line_after_active_block`](#-function-ensure_blank_line_after_active_block)
- [🔧 Function `join_lines`](#-function-join_lines)
- [🔧 Function `make_placeholder`](#-function-make_placeholder)
- [🔧 Function `split_lines`](#-function-split_lines)

</details>

## 🔧 Function `ensure_blank_line_after_active_block`

```python
def ensure_blank_line_after_active_block(body: str) -> str
```

Insert a blank line after a block when the next non-empty line starts new content.

<details>
<summary>Code:</summary>

```python
def ensure_blank_line_after_active_block(
    body: str,
    *,
    is_block_line: Callable[[str], bool],
) -> str:
    lines = body.split("\n")
    result: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        is_block = is_block_line(line)
        if in_block and stripped and not is_block:
            result.append("")
            in_block = False
        if is_block:
            in_block = True
        elif stripped:
            in_block = False
        result.append(line)
    return "\n".join(result)
```

</details>

## 🔧 Function `join_lines`

```python
def join_lines(lines: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text
```

</details>

## 🔧 Function `make_placeholder`

```python
def make_placeholder(prefix: str, index: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def make_placeholder(prefix: str, index: int) -> str:
    return f"{prefix}{index}"
```

</details>

## 🔧 Function `split_lines`

```python
def split_lines(text: str) -> tuple[list[str], bool]
```

Split text into lines without the trailing split artifact from a final newline.

<details>
<summary>Code:</summary>

```python
def split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
```

</details>
