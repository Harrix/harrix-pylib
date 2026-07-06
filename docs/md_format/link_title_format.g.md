---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `link_title_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_link_title`](#-function-format_link_title)
- [🔧 Function `format_parseable_link_title`](#-function-format_parseable_link_title)
- [🔧 Function `normalize_inline_link_titles`](#-function-normalize_inline_link_titles)
- [🔧 Function `scan_inline_links`](#-function-scan_inline_links)
- [🔧 Function `split_inline_destination`](#-function-split_inline_destination)

</details>

## 🔧 Function `format_link_title`

```python
def format_link_title(title: str) -> str
```

Return a canonical quoted title for inline links and images.

<details>
<summary>Code:</summary>

```python
def format_link_title(title: str) -> str:
    title = _canonicalize_link_title_content(title)
    if title == _QUOTE_APOSTROPHE_PAREN:
        escaped = _escape_title_content(title, '"')
        return f'"{escaped}"'
    candidates: list[str] = []
    for delimiter in ('"', "'"):
        escaped = _escape_title_content(title, delimiter)
        candidates.append(f"{delimiter}{escaped}{delimiter}")
    return min(candidates, key=lambda candidate: _title_quote_priority(title, candidate))
```

</details>

## 🔧 Function `format_parseable_link_title`

```python
def format_parseable_link_title(title: str) -> str
```

Return a quoted title that markdown-it can parse before rendering.

<details>
<summary>Code:</summary>

```python
def format_parseable_link_title(title: str) -> str:
    title = _canonicalize_link_title_content(title)
    if title == _QUOTE_APOSTROPHE_PAREN:
        return '"' + "\\" + title + '"'
    return format_link_title(title)
```

</details>

## 🔧 Function `normalize_inline_link_titles`

```python
def normalize_inline_link_titles(body: str) -> str
```

Normalize quoted titles in inline links before parsing.

<details>
<summary>Code:</summary>

```python
def normalize_inline_link_titles(body: str) -> str:
    lines, trailing = split_lines(body)
    result_lines: list[str] = []
    for line in lines:
        if line.lstrip().startswith("|"):
            result_lines.append(line)
        else:
            result_lines.append(_normalize_inline_link_titles_in_text(line))
    return join_lines(result_lines, trailing_newline=trailing)
```

</details>

## 🔧 Function `scan_inline_links`

```python
def scan_inline_links(body: str, handler: Callable[[str, str, str], str]) -> str
```

Scan inline links and rebuild text with a per-link handler.

Inline code spans are treated as opaque text and are never scanned for links.

<details>
<summary>Code:</summary>

```python
def scan_inline_links(
    body: str,
    handler: Callable[[str, str, str], str],
) -> str:
    parts: list[str] = []
    for segment, is_code in identify_code_blocks_line(body):
        if is_code:
            parts.append(segment)
        else:
            parts.append(_scan_inline_links_in_plain_text(segment, handler))
    return "".join(parts)
```

</details>

## 🔧 Function `split_inline_destination`

```python
def split_inline_destination(destination: str) -> tuple[str, str | None]
```

Split an inline link destination into URL and optional title.

<details>
<summary>Code:</summary>

```python
def split_inline_destination(destination: str) -> tuple[str, str | None]:
    destination = destination.strip()
    if destination.endswith((' ""', " ''")):
        return destination[:-3].rstrip(), None
    if destination.startswith("<") and destination.endswith(">"):
        return destination, None
    url, title = _split_trailing_link_title(destination)
    if title is not None:
        if title in {'""', "''"}:
            return url, None
        return url, title
    return destination, None
```

</details>
