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
- [🔧 Function `_is_all_caps_macro_underscore`](#-function-_is_all_caps_macro_underscore)
- [🔧 Function `_is_alphanumeric`](#-function-_is_alphanumeric)
- [🔧 Function `_is_left_flanking`](#-function-_is_left_flanking)
- [🔧 Function `_is_punctuation`](#-function-_is_punctuation)
- [🔧 Function `_is_right_flanking`](#-function-_is_right_flanking)
- [🔧 Function `_is_whitespace`](#-function-_is_whitespace)
- [🔧 Function `_should_escape_asterisk`](#-function-_should_escape_asterisk)
- [🔧 Function `_should_escape_underscore`](#-function-_should_escape_underscore)

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
    if text.startswith(PLACEHOLDER_PREFIX):
        return text

    parts: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            parts.append(char)
            parts.append(text[index + 1])
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

## 🔧 Function `_is_all_caps_macro_underscore`

```python
def _is_all_caps_macro_underscore(text: str, index: int) -> bool
```

Match C-style macros like `_WIN32` and `_DEBUG`.

<details>
<summary>Code:</summary>

```python
def _is_all_caps_macro_underscore(text: str, index: int) -> bool:
    if text[index] != "_" or index + 1 >= len(text):
        return False
    if index > 0 and (text[index - 1].isalnum() or text[index - 1] == "_"):
        return False

    end = index + 1
    while end < len(text) and (text[end].isalnum() or text[end] == "_"):
        end += 1

    token = text[index:end]
    if len(token) < _MIN_MACRO_TOKEN_LEN or "_" in token[1:]:
        return False

    suffix = token[1:]
    return any(char.isalpha() for char in suffix) and suffix.isupper()
```

</details>

## 🔧 Function `_is_alphanumeric`

```python
def _is_alphanumeric(char: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_alphanumeric(char: str) -> bool:
    return char.isalnum()
```

</details>

## 🔧 Function `_is_left_flanking`

```python
def _is_left_flanking(text: str, index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_left_flanking(text: str, index: int) -> bool:
    if index + 1 < len(text) and _is_whitespace(text[index + 1]):
        return False
    if (
        index + 1 < len(text)
        and not _is_punctuation(text[index + 1])
        and (index == 0 or _is_whitespace(text[index - 1]) or _is_punctuation(text[index - 1]))
    ):
        return True
    return index > 0 and (_is_whitespace(text[index - 1]) or _is_punctuation(text[index - 1]))
```

</details>

## 🔧 Function `_is_punctuation`

```python
def _is_punctuation(char: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_punctuation(char: str) -> bool:
    if char in _PUNCTUATION:
        return True
    return unicodedata.category(char).startswith("P")
```

</details>

## 🔧 Function `_is_right_flanking`

```python
def _is_right_flanking(text: str, index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_right_flanking(text: str, index: int) -> bool:
    if index > 0 and _is_whitespace(text[index - 1]):
        return False
    if (
        index > 0
        and not _is_punctuation(text[index - 1])
        and (index + 1 >= len(text) or _is_whitespace(text[index + 1]) or _is_punctuation(text[index + 1]))
    ):
        return True
    return index + 1 < len(text) and (_is_whitespace(text[index + 1]) or _is_punctuation(text[index + 1]))
```

</details>

## 🔧 Function `_is_whitespace`

```python
def _is_whitespace(char: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_whitespace(char: str) -> bool:
    return char.isspace()
```

</details>

## 🔧 Function `_should_escape_asterisk`

```python
def _should_escape_asterisk(text: str, index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _should_escape_asterisk(text: str, index: int) -> bool:
    return _is_left_flanking(text, index) or _is_right_flanking(text, index)
```

</details>

## 🔧 Function `_should_escape_underscore`

```python
def _should_escape_underscore(text: str, index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _should_escape_underscore(text: str, index: int) -> bool:
    if index > 0 and text[index - 1] == "[" and index + 1 < len(text) and _is_alphanumeric(text[index + 1]):
        return True
    if _is_all_caps_macro_underscore(text, index):
        return True
    if index + 1 < len(text) and _is_alphanumeric(text[index + 1]):
        return False
    if index + 1 < len(text) and text[index + 1] in _UNDERSCORE_LITERAL_PREFIXES:
        return False
    if index > 0 and _is_alphanumeric(text[index - 1]) and index + 1 < len(text) and _is_punctuation(text[index + 1]):
        return True
    if index > 0 and _is_alphanumeric(text[index - 1]):
        return False

    left = _is_left_flanking(text, index)
    right = _is_right_flanking(text, index)
    can_open = left and (not right or (index > 0 and _is_punctuation(text[index - 1])))
    can_close = right and (not left or (index + 1 < len(text) and _is_punctuation(text[index + 1])))
    return can_open or can_close
```

</details>
