---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `math_spans.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `display_math_line_flags`](#-function-display_math_line_flags)
- [🔧 Function `iter_code_and_math_segments`](#-function-iter_code_and_math_segments)

</details>

## 🔧 Function `display_math_line_flags`

```python
def display_math_line_flags(lines: Sequence[str]) -> list[bool]
```

Return per-line flags for display-math `$$...$$` regions (including delimiters).

<details>
<summary>Code:</summary>

```python
def display_math_line_flags(lines: Sequence[str], *, in_code: Sequence[bool] | None = None) -> list[bool]:
    flags = [False] * len(lines)
    inside = False
    for index, line in enumerate(lines):
        if in_code is not None and in_code[index]:
            continue
        if _DISPLAY_MATH_DELIMITER_RE.match(line):
            flags[index] = True
            inside = not inside
            continue
        stripped = line.strip()
        if (
            stripped.startswith("$$")
            and stripped.endswith("$$")
            and len(stripped) > _EMPTY_SINGLE_LINE_DISPLAY_MATH_LEN
        ):
            flags[index] = True
            continue
        if inside:
            flags[index] = True
    return flags
```

</details>

## 🔧 Function `iter_code_and_math_segments`

```python
def iter_code_and_math_segments(code_segments: Iterator[tuple[str, bool]] | Sequence[tuple[str, bool]]) -> Iterator[tuple[str, bool]]
```

Yield `(segment, protected)` where protected is inline code or dollar-math.

<details>
<summary>Code:</summary>

```python
def iter_code_and_math_segments(
    code_segments: Iterator[tuple[str, bool]] | Sequence[tuple[str, bool]],
) -> Iterator[tuple[str, bool]]:
    for segment, in_code in code_segments:
        if in_code:
            yield segment, True
            continue
        yield from _split_math_segments(segment)
```

</details>
