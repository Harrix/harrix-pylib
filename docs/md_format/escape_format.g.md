---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `escape_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `escape_markdown_text`](#-function-escape_markdown_text)
- [🔧 Function `escape_ordered_list_like_line_starts`](#-function-escape_ordered_list_like_line_starts)

</details>

## 🔧 Function `escape_markdown_text`

```python
def escape_markdown_text(text: str) -> str
```

Escape emphasis-like `*` and `_` characters in plain text.

<details>
<summary>Code:</summary>

```python
def escape_markdown_text(text: str) -> str:
    if any(text.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES):
        return text
    if text.startswith(PLACEHOLDER_PREFIX):
        return text

    parts: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            next_char = text[index + 1]
            if next_char in _ASCII_PUNCTUATION:
                parts.append(char + char)
            else:
                parts.append(char)
            parts.append(next_char)
            index += 2
            continue
        if char == "*" and _should_escape_asterisk(text, index):
            parts.append("\\*")
        elif char == "_" and _should_escape_underscore(text, index):
            parts.append("\\_")
        else:
            parts.append(char)
        index += 1
    return "".join(parts)
```

</details>

## 🔧 Function `escape_ordered_list_like_line_starts`

```python
def escape_ordered_list_like_line_starts(text: str) -> str
```

Re-escape `39.`-like line starts so they are not parsed as ordered lists.

<details>
<summary>Code:</summary>

```python
def escape_ordered_list_like_line_starts(text: str) -> str:
    if not text:
        return text
    return "\n".join(_escape_ordered_list_like_line_start(line) for line in text.split("\n"))
```

</details>
