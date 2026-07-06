---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `inline_link_format.py`

## 🔧 Function `prepare_inline_links`

```python
def prepare_inline_links(body: str) -> tuple[str, list[LinkDestination]]
```

Normalize link titles and extract destinations in a single pass.

<details>
<summary>Code:</summary>

```python
def prepare_inline_links(body: str) -> tuple[str, list[LinkDestination]]:
    lines, trailing = split_lines(body)
    result_lines: list[str] = []
    entries: list[LinkDestination] = []
    index = 0
    for line in lines:
        if _should_skip_link_line(line):
            result_lines.append(line)
            continue
        processed, line_entries, index = _prepare_inline_links_in_text(line, start_index=index)
        result_lines.append(processed)
        entries.extend(line_entries)
    return join_lines(result_lines, trailing_newline=trailing), entries
```

</details>
