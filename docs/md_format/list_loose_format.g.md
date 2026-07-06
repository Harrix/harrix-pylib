---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `list_loose_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ListLayout`](#️-class-listlayout)
- [🔧 Function `extract_list_layouts`](#-function-extract_list_layouts)

</details>

## 🏛️ Class `ListLayout`

```python
class ListLayout
```

Loose-list spacing for one list in source order.

<details>
<summary>Code:</summary>

```python
class ListLayout:

    gaps_before_item: list[bool]
    loose_items: list[bool]
```

</details>

## 🔧 Function `extract_list_layouts`

```python
def extract_list_layouts(body: str, tight_code_indices: set[int] | None = None) -> tuple[str, list[ListLayout]]
```

Collect loose-list layout metadata for each list in the document.

<details>
<summary>Code:</summary>

```python
def extract_list_layouts(body: str, tight_code_indices: set[int] | None = None) -> tuple[str, list[ListLayout]]:
    lines, trailing = split_lines(body)
    scan_lines = _drop_code_placeholder_blanks(lines, tight_code_indices or set())
    layouts: list[ListLayout] = []
    index = 0
    while index < len(scan_lines):
        if not is_list_line(scan_lines[index]):
            index += 1
            continue
        index = _scan_list(scan_lines, index, layouts)
    return join_lines(lines, trailing_newline=trailing), layouts
```

</details>
