---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `prose_wrap.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `should_omit_space_between`](#-function-should_omit_space_between)
- [🔧 Function `wrap_paragraph_prose`](#-function-wrap_paragraph_prose)
- [🔧 Function `wrap_prose`](#-function-wrap_prose)

</details>

## 🔧 Function `should_omit_space_between`

```python
def should_omit_space_between(left: str, right: str) -> bool
```

Return whether phrasing text on both sides of a break should be joined without a space.

<details>
<summary>Code:</summary>

```python
def should_omit_space_between(left: str, right: str) -> bool:
    if not left or not right:
        return False
    if _is_hangul(left[-1]) or _is_hangul(right[0]):
        return False
    last, first = left[-1], right[0]
    if last == "・" or first == "・":
        return True
    if _kana_continuation_join(left, right):
        return True
    if _is_katakana(last) or _is_katakana(first):
        return False
    if last in "」』）】" and first == "(":
        return True
    if _is_cjk(last) and _is_cjk(first):
        return True
    if _is_cjk(last) and first.isascii() and first.isalnum():
        return True
    if first in "、。，．！？）】」〉》〕〗〙〛":
        return True
    if last in "（【「〈《〔〖〘〚":
        return True
    if last in ",.!?:;":
        return False
    if first in ",.!?:;":
        return False
    return False
```

</details>

## 🔧 Function `wrap_paragraph_prose`

```python
def wrap_paragraph_prose(text: str) -> str
```

Wrap paragraph text, preserving hard breaks and backslash-only lead lines.

<details>
<summary>Code:</summary>

```python
def wrap_paragraph_prose(text: str, *, width: int) -> str:
    if not text or width <= 0:
        return text
    if text.startswith("\\") and "\n" in text:
        lead, _, rest = text.partition("\n")
        if lead and set(lead) <= {"\\"}:
            wrapped_rest = wrap_prose(rest.lstrip(), width=width) if rest.strip() else rest
            return f"{lead}\n{wrapped_rest}" if wrapped_rest else lead
    hard_break = "  \n"
    if hard_break not in text:
        return wrap_prose(text, width=width)
    head, tail = text.split(hard_break, 1)
    wrapped_tail = _wrap_prose_after_hard_break(tail.lstrip(), width=width)
    return f"{head}{hard_break}{wrapped_tail}"
```

</details>

## 🔧 Function `wrap_prose`

```python
def wrap_prose(text: str) -> str
```

Wrap phrasing Markdown text to the given display width.

<details>
<summary>Code:</summary>

```python
def wrap_prose(text: str, *, width: int, prefix: str = "", continuation: str | None = None) -> str:
    if not text or width <= 0:
        return text
    continuation = continuation if continuation is not None else prefix
    lines = _wrap_text_lines(text, width=width, first_prefix=prefix, next_prefix=continuation)
    return "\n".join(_avoid_list_marker_line_starts(lines))
```

</details>
