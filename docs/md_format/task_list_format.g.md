---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `task_list_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TaskListMarker`](#️-class-tasklistmarker)
- [🔧 Function `extract_task_list_markers`](#-function-extract_task_list_markers
  )
- [🔧 Function `strip_task_placeholder`](#-function-strip_task_placeholder)
- [🔧 Function `task_list_marker_for_text`](#-function-task_list_marker_for_text
  )
- [🔧 Function `_join_lines`](#-function-_join_lines)
- [🔧 Function `_placeholder`](#-function-_placeholder)
- [🔧 Function `_split_lines`](#-function-_split_lines)

</details>

## 🏛️ Class `TaskListMarker`

```python
class TaskListMarker
```

Stored checkbox marker for a task list item.

<details>
<summary>Code:</summary>

```python
class TaskListMarker:

    index: int
    checked: bool
```

</details>

## 🔧 Function `extract_task_list_markers`

```python
def extract_task_list_markers(body: str) -> tuple[str, list[TaskListMarker]]
```

Replace task-list markers with placeholders the parser will keep in text.

<details>
<summary>Code:</summary>

```python
def extract_task_list_markers(body: str) -> tuple[str, list[TaskListMarker]]:
    lines, trailing = _split_lines(body)
    result: list[str] = []
    markers: list[TaskListMarker] = []
    index = 0
    for line in lines:
        match = _TASK_ITEM_RE.match(line)
        if not match:
            result.append(line)
            continue
        indent, bullet, checked_char, rest = match.groups()
        checked = checked_char.lower() == "x"
        markers.append(TaskListMarker(index=index, checked=checked))
        result.append(f"{indent}{bullet} {_placeholder(index)} {rest}")
        index += 1
    return _join_lines(result, trailing_newline=trailing), markers
```

</details>

## 🔧 Function `strip_task_placeholder`

```python
def strip_task_placeholder(text: str) -> str
```

Remove the task-list placeholder token from item text.

<details>
<summary>Code:</summary>

```python
def strip_task_placeholder(text: str) -> str:
    stripped = text.lstrip()
    if not stripped.startswith(PLACEHOLDER_PREFIX):
        return text
    _, _, rest = stripped.partition(" ")
    return rest.lstrip()
```

</details>

## 🔧 Function `task_list_marker_for_text`

```python
def task_list_marker_for_text(text: str, markers: list[TaskListMarker]) -> str | None
```

Return `[ ] ` or `[x] ` when paragraph text starts with a task placeholder.

<details>
<summary>Code:</summary>

```python
def task_list_marker_for_text(text: str, markers: list[TaskListMarker]) -> str | None:
    stripped = text.lstrip()
    if not stripped.startswith(PLACEHOLDER_PREFIX):
        return None
    token, _, _ = stripped.partition(" ")
    try:
        marker_index = int(token.removeprefix(PLACEHOLDER_PREFIX))
    except ValueError:
        return None
    for marker in markers:
        if marker.index == marker_index:
            return "[x] " if marker.checked else "[ ] "
    return None
```

</details>

## 🔧 Function `_join_lines`

```python
def _join_lines(lines: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text
```

</details>

## 🔧 Function `_placeholder`

```python
def _placeholder(index: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _placeholder(index: int) -> str:
    return f"{PLACEHOLDER_PREFIX}{index}"
```

</details>

## 🔧 Function `_split_lines`

```python
def _split_lines(text: str) -> tuple[list[str], bool]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
```

</details>
