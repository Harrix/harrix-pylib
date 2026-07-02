---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ordered_list_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `extract_ordered_list_marker_groups`](#-function-extract_ordered_list_marker_groups)
- [🔧 Function `is_git_diff_friendly_ordered_list`](#-function-is_git_diff_friendly_ordered_list)
- [🔧 Function `ordered_list_item_number`](#-function-ordered_list_item_number)

</details>

## 🔧 Function `extract_ordered_list_marker_groups`

```python
def extract_ordered_list_marker_groups(body: str) -> tuple[str, list[list[int]]]
```

Collect source marker numbers for each contiguous ordered list.

<details>
<summary>Code:</summary>

```python
def extract_ordered_list_marker_groups(body: str) -> tuple[str, list[list[int]]]:
    lines, trailing = split_lines(body)
    groups: list[list[int]] = []
    current: list[int] = []
    current_indent: int | None = None
    pending_break = False  # encountered a non-list line since last item
    for line in lines:
        if line.startswith("    ") or line.startswith("\t"):
            continue
        match = _ORDERED_ITEM_RE.match(line)
        if match:
            indent = len(match.group(1))
            if current and current_indent is not None and indent == current_indent:
                # Continue same list (possibly after blank lines / continuation lines).
                current.append(int(match.group(2)))
                pending_break = False
            else:
                if current:
                    groups.append(current)
                current = [int(match.group(2))]
                current_indent = indent
                pending_break = False
            continue
        stripped = line.strip()
        if not stripped:
            # Blank line — may separate loose list items; keep current open.
            pending_break = True
            continue
        # A non-empty, non-list line: if it's indented deeper than current_indent,
        # it's a continuation of the current item; otherwise close the group.
        if current and current_indent is not None:
            line_indent = len(line) - len(line.lstrip())
            if line_indent > current_indent:
                # Continuation content — don't close the group.
                pending_break = False
                continue
        # Different content at same or lower indent — close the group.
        if current:
            groups.append(current)
            current = []
            current_indent = None
        pending_break = False
    if current:
        groups.append(current)
    return join_lines(lines, trailing_newline=trailing), groups
```

</details>

## 🔧 Function `is_git_diff_friendly_ordered_list`

```python
def is_git_diff_friendly_ordered_list(markers: list[int]) -> bool
```

Return whether ordered list markers should use git-diff-friendly `1.` suffixes.

<details>
<summary>Code:</summary>

```python
def is_git_diff_friendly_ordered_list(markers: list[int]) -> bool:
    if len(markers) < 2:
        return False
    if markers[1] != 1:
        return False
    if markers[0] != 0:
        return True
    return len(markers) > 2 and markers[2] == 1
```

</details>

## 🔧 Function `ordered_list_item_number`

```python
def ordered_list_item_number(markers: list[int], item_index: int) -> int
```

Compute the rendered marker number for an ordered-list item.

<details>
<summary>Code:</summary>

```python
def ordered_list_item_number(markers: list[int], item_index: int) -> int:
    if not markers:
        return item_index + 1
    if is_git_diff_friendly_ordered_list(markers):
        return markers[0] if item_index == 0 else 1
    return markers[0] + item_index
```

</details>
