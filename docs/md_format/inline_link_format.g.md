---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `inline_link_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `prepare_inline_links`](#-function-prepare_inline_links)
- [🔧 Function `_prepare_inline_links_in_text`](#-function-_prepare_inline_links_in_text)
- [🔧 Function `_should_skip_link_line`](#-function-_should_skip_link_line)

</details>

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

## 🔧 Function `_prepare_inline_links_in_text`

```python
def _prepare_inline_links_in_text(body: str) -> tuple[str, list[LinkDestination], int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _prepare_inline_links_in_text(body: str, *, start_index: int) -> tuple[str, list[LinkDestination], int]:
    entries: list[LinkDestination] = []
    index = start_index

    def handler(prefix: str, destination: str, suffix: str) -> str:
        nonlocal index
        url, title = split_inline_destination(destination)
        if title is not None:
            normalized_destination = f"{url} {format_parseable_link_title(_unescape_title(title))}"
        else:
            normalized_destination = destination
        url, title = split_inline_destination(normalized_destination.strip())
        display_title = format_link_title(_unescape_title(title)) if title is not None else None
        entries.append(LinkDestination(index=index, destination=url, title=display_title))
        title_suffix = f" {title}" if title is not None else ""
        replacement = f"{prefix}{make_placeholder(PLACEHOLDER_PREFIX, index)}{title_suffix}{suffix}"
        index += 1
        return replacement

    return scan_inline_links(body, handler), entries, index
```

</details>

## 🔧 Function `_should_skip_link_line`

```python
def _should_skip_link_line(line: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _should_skip_link_line(line: str) -> bool:
    return line.lstrip().startswith("|") or line.startswith("    ") or line.startswith("\t")
```

</details>
