---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `list_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_blank_line_after_lists`](#-function-ensure_blank_line_after_lists)
- [🔧 Function `is_list_continuation`](#-function-is_list_continuation)
- [🔧 Function `is_list_item_continuation_line`](#-function-is_list_item_continuation_line)
- [🔧 Function `is_list_line`](#-function-is_list_line)

</details>

## 🔧 Function `ensure_blank_line_after_lists`

```python
def ensure_blank_line_after_lists(body: str) -> str
```

Insert a blank line after a list when the next line starts a new block.

<details>
<summary>Code:</summary>

```python
def ensure_blank_line_after_lists(body: str) -> str:
    lines = body.split("\n")
    result: list[str] = []
    in_list_context = False
    for line in lines:
        stripped = line.strip()
        if is_list_line(line):
            in_list_context = True
            result.append(line)
            continue
        if not stripped:
            in_list_context = False
            result.append(line)
            continue
        if in_list_context and result and is_list_item_continuation_line(result[-1], line):
            result.append(line)
            continue
        if in_list_context and not is_table_line(line) and not is_list_continuation(line):
            result.append("")
            in_list_context = False
        if not is_list_continuation(line):
            in_list_context = False
        result.append(line)
    return "\n".join(result)
```

</details>

## 🔧 Function `is_list_continuation`

```python
def is_list_continuation(line: str) -> bool
```

Return whether the line continues the previous list item paragraph.

<details>
<summary>Code:</summary>

```python
def is_list_continuation(line: str) -> bool:
    return bool(line.strip() and not is_list_line(line) and line[:1] in {" ", "\t"})
```

</details>

## 🔧 Function `is_list_item_continuation_line`

```python
def is_list_item_continuation_line(previous_line: str, line: str) -> bool
```

Return whether an unindented line continues the previous list item text.

<details>
<summary>Code:</summary>

````python
def is_list_item_continuation_line(previous_line: str, line: str) -> bool:
    if not previous_line.strip() or not line.strip():
        return False
    if is_list_line(line) or is_table_line(line):
        return False
    stripped = line.lstrip()
    if stripped.startswith(">") and line[:1] in {" ", "\t"}:
        return is_list_line(previous_line) or is_list_continuation(previous_line)
    if stripped.startswith(("#", "```", "$$", "<details", "</details>", "<summary", "</summary>", "`", "![", "|")):
        return False
    if stripped.startswith(">") and line[:1] not in {" ", "\t"}:
        return False
    if is_list_line(previous_line):
        return True
    if is_list_continuation(previous_line):
        return True
    return bool(previous_line.startswith(" ") and not is_list_line(previous_line))
````

</details>

## 🔧 Function `is_list_line`

```python
def is_list_line(line: str) -> bool
```

Return whether the line is a bullet or ordered list item.

<details>
<summary>Code:</summary>

```python
def is_list_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return bool(_LIST_ITEM_PATTERN.match(stripped)) or bool(_ORDERED_LIST_ITEM_PATTERN.match(stripped))
```

</details>
