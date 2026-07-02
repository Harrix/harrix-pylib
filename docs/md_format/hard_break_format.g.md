---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `hard_break_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HardBreakStyles`](#%EF%B8%8F-class-hardbreakstyles)
  - [⚙️ Method `next_is_backslash`](#%EF%B8%8F-method-next_is_backslash)
- [🔧 Function `extract_backslash_hard_breaks`](#-function-extract_backslash_hard_breaks)
- [🔧 Function `_line_has_single_backslash_hard_break`](#-function-_line_has_single_backslash_hard_break)
- [🔧 Function `_line_has_space_hard_break`](#-function-_line_has_space_hard_break)

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
        if not self.backslash_breaks:
            return False
        return self.backslash_breaks.pop(0)
```

</details>

### ⚙️ Method `next_is_backslash`

```python
def next_is_backslash(self) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def next_is_backslash(self) -> bool:
        if not self.backslash_breaks:
            return False
        return self.backslash_breaks.pop(0)
```

</details>

## 🔧 Function `extract_backslash_hard_breaks`

```python
def extract_backslash_hard_breaks(body: str) -> tuple[str, HardBreakStyles]
```

Record hard-break styles and normalize single trailing backslashes for parsing.

<details>
<summary>Code:</summary>

```python
def extract_backslash_hard_breaks(body: str) -> tuple[str, HardBreakStyles]:
    lines, trailing = split_lines(body)
    styles = HardBreakStyles()
    converted: list[str] = []
    for index, line in enumerate(lines):
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if _line_has_single_backslash_hard_break(line, next_line=next_line):
            styles.backslash_breaks.append(True)
            converted.append(line[:-1] + "  ")
            continue
        if _line_has_space_hard_break(line, next_line=next_line):
            styles.backslash_breaks.append(False)
        converted.append(line)
    return join_lines(converted, trailing_newline=trailing), styles
```

</details>

## 🔧 Function `_line_has_single_backslash_hard_break`

```python
def _line_has_single_backslash_hard_break(line: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _line_has_single_backslash_hard_break(line: str, *, next_line: str) -> bool:
    if not next_line.strip():
        return False
    if not line.endswith("\\"):
        return False
    return not line.endswith("\\\\")
```

</details>

## 🔧 Function `_line_has_space_hard_break`

```python
def _line_has_space_hard_break(line: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _line_has_space_hard_break(line: str, *, next_line: str) -> bool:
    if not next_line.strip():
        return False
    return line.endswith("  ") or line.endswith("\t")
```

</details>
