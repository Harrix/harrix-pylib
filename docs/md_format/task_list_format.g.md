---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `task_list_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TaskListMarker`](#%EF%B8%8F-class-tasklistmarker)
- [🔧 Function `extract_task_list_markers`](#-function-extract_task_list_markers)
- [🔧 Function `strip_task_placeholder`](#-function-strip_task_placeholder)
- [🔧 Function `task_list_entry_for_text`](#-function-task_list_entry_for_text)
- [🔧 Function `task_list_marker_for_text`](#-function-task_list_marker_for_text)

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
    marker_spaces: int = 1
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
    lines, trailing = split_lines(body)
    result: list[str] = []
    markers: list[TaskListMarker] = []
    index = 0
    for line in lines:
        match = _TASK_ITEM_RE.match(line)
        if not match:
            result.append(line)
            continue
        indent, marker, marker_spaces, checked_char, rest = match.groups()
        checked = checked_char.lower() == "x"
        markers.append(TaskListMarker(index=index, checked=checked, marker_spaces=len(marker_spaces)))
        result.append(f"{indent}{marker}{marker_spaces}{make_placeholder(PLACEHOLDER_PREFIX, index)} {rest}")
        index += 1
    return join_lines(result, trailing_newline=trailing), markers
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

## 🔧 Function `task_list_entry_for_text`

```python
def task_list_entry_for_text(text: str, markers: list[TaskListMarker]) -> tuple[str, TaskListMarker] | None
```

Return task marker text and metadata when paragraph text starts with a placeholder.

<details>
<summary>Code:</summary>

```python
def task_list_entry_for_text(text: str, markers: list[TaskListMarker]) -> tuple[str, TaskListMarker] | None:
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
            return ("[x] " if marker.checked else "[ ] ", marker)
    return None
```

</details>

## 🔧 Function `task_list_marker_for_text`

```python
def task_list_marker_for_text(text: str, markers: list[TaskListMarker]) -> str | None
```

Return ` [ ]  ` or ` [x]  ` when paragraph text starts with a task placeholder.

<details>
<summary>Code:</summary>

```python
def task_list_marker_for_text(text: str, markers: list[TaskListMarker]) -> str | None:
    entry = task_list_entry_for_text(text, markers)
    return entry[0] if entry else None
```

</details>
