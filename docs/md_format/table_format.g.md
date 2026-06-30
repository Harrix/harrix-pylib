---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `table_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_blank_line_after_tables`](#-function-ensure_blank_line_af
  ter_tables)
- [🔧 Function `is_table_line`](#-function-is_table_line)
- [🔧 Function `looks_like_prose_table_row`](#-function-looks_like_prose_table_r
  ow)
- [🔧 Function `parse_table_cells`](#-function-parse_table_cells)
- [🔧 Function `text_display_width`](#-function-text_display_width)
- [🔧 Function `unwrap_spurious_table_rows`](#-function-unwrap_spurious_table_ro
  ws)
- [🔧 Function `_is_emoji_base`](#-function-_is_emoji_base)

</details>

## 🔧 Function `ensure_blank_line_after_tables`

```python
def ensure_blank_line_after_tables(body: str) -> str
```

Insert a blank line after a GFM table when the next line is not a table row.

<details>
<summary>Code:</summary>

```python
def ensure_blank_line_after_tables(body: str) -> str:
    lines = body.split("\n")
    result: list[str] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        is_table = is_table_line(line)
        if in_table and stripped and not is_table:
            result.append("")
            in_table = False
        if is_table:
            in_table = True
        elif stripped:
            in_table = False
        result.append(line)
    return "\n".join(result)
```

</details>

## 🔧 Function `is_table_line`

```python
def is_table_line(line: str) -> bool
```

Return whether the line is a GFM table row.

<details>
<summary>Code:</summary>

```python
def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and stripped.startswith("|") and stripped.endswith("|")
```

</details>

## 🔧 Function `looks_like_prose_table_row`

```python
def looks_like_prose_table_row(text: str) -> bool
```

Return whether a single table cell looks like a misparsed paragraph.

<details>
<summary>Code:</summary>

```python
def looks_like_prose_table_row(text: str) -> bool:
    min_prose_length = 60
    min_word_count = 5
    return len(text) > min_prose_length or (text.count(" ") >= min_word_count and "." in text)
```

</details>

## 🔧 Function `parse_table_cells`

```python
def parse_table_cells(line: str) -> list[str] | None
```

Split a table row into cell values.

<details>
<summary>Code:</summary>

```python
def parse_table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not is_table_line(line):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]
```

</details>

## 🔧 Function `text_display_width`

```python
def text_display_width(text: str) -> int
```

Return the terminal display width of text (emoji and CJK count as 2 columns).

<details>
<summary>Code:</summary>

```python
def text_display_width(text: str) -> int:
    width = 0
    for char in text:
        category = unicodedata.category(char)
        if category in {"Mn", "Me", "Cf"}:
            continue
        if unicodedata.east_asian_width(char) in {"F", "W"} or _is_emoji_base(char):
            width += 2
        else:
            width += 1
    return width
```

</details>

## 🔧 Function `unwrap_spurious_table_rows`

```python
def unwrap_spurious_table_rows(body: str) -> str
```

Turn `| long prose | | |` rows back into plain paragraphs.

<details>
<summary>Code:</summary>

```python
def unwrap_spurious_table_rows(body: str) -> str:
    min_spurious_width = 3
    lines = body.split("\n")
    result: list[str] = []
    for line in lines:
        cells = parse_table_cells(line)
        if (
            cells
            and len(cells) >= min_spurious_width
            and cells[0]
            and not any(cells[1:])
            and looks_like_prose_table_row(cells[0])
        ):
            if result and is_table_line(result[-1]):
                result.append("")
            result.append(cells[0])
            continue
        result.append(line)
    return "\n".join(result)
```

</details>

## 🔧 Function `_is_emoji_base`

```python
def _is_emoji_base(char: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_emoji_base(char: str) -> bool:
    code = ord(char)
    return any(start <= code <= end for start, end in _EMOJI_CODE_POINT_RANGES)
```

</details>
