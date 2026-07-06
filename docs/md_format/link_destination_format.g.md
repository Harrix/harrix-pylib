---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `link_destination_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LinkDestination`](#️-class-linkdestination)
- [🔧 Function `decode_percent_encoded_url`](#-function-decode_percent_encoded_url)
- [🔧 Function `extract_link_destinations`](#-function-extract_link_destinations)
- [🔧 Function `format_inline_link_destination`](#-function-format_inline_link_destination)
- [🔧 Function `format_link_url`](#-function-format_link_url)
- [🔧 Function `formatted_href_from_placeholder`](#-function-formatted_href_from_placeholder)
- [🔧 Function `formatted_title_from_placeholder`](#-function-formatted_title_from_placeholder)

</details>

## 🏛️ Class `LinkDestination`

```python
class LinkDestination
```

Stored original link destination text.

<details>
<summary>Code:</summary>

```python
class LinkDestination:

    index: int
    destination: str
    title: str | None = None
```

</details>

## 🔧 Function `decode_percent_encoded_url`

```python
def decode_percent_encoded_url(url: str) -> str
```

Decode percent-encoded Unicode in URL paths and fragments for readable Markdown.

<details>
<summary>Code:</summary>

```python
def decode_percent_encoded_url(url: str) -> str:
    if not url or "%" not in url:
        return url
    if url.startswith("#"):
        return _decode_unicode_percent_sequences(url)
    parts = urlsplit(url)
    if not parts.scheme and not parts.netloc:
        return _decode_unicode_percent_sequences(url)
    decoded_path = _decode_unicode_percent_sequences(parts.path) if parts.path else parts.path
    decoded_query = _decode_unicode_percent_sequences(parts.query) if parts.query else parts.query
    decoded_fragment = _decode_unicode_percent_sequences(parts.fragment) if parts.fragment else parts.fragment
    return urlunsplit((parts.scheme, parts.netloc, decoded_path, decoded_query, decoded_fragment))
```

</details>

## 🔧 Function `extract_link_destinations`

```python
def extract_link_destinations(body: str) -> tuple[str, list[LinkDestination]]
```

Replace link destinations with placeholders before parsing.

<details>
<summary>Code:</summary>

```python
def extract_link_destinations(body: str) -> tuple[str, list[LinkDestination]]:
    from harrix_pylib.md_format.inline_link_format import prepare_inline_links  # noqa: PLC0415

    return prepare_inline_links(body)
```

</details>

## 🔧 Function `format_inline_link_destination`

```python
def format_inline_link_destination(destination: str) -> str
```

Return canonical destination text for inline links and images.

<details>
<summary>Code:</summary>

```python
def format_inline_link_destination(destination: str) -> str:
    url, title = split_inline_destination(destination.strip())
    formatted_url = _format_link_url(url)
    if title is None:
        return formatted_url
    return f"{formatted_url} {title}"
```

</details>

## 🔧 Function `format_link_url`

```python
def format_link_url(url: str) -> str
```

Return canonical URL text for links and reference definitions.

<details>
<summary>Code:</summary>

```python
def format_link_url(url: str, *, wrap_parentheses: bool = True) -> str:
    return _format_link_url(url, wrap_parentheses=wrap_parentheses)
```

</details>

## 🔧 Function `formatted_href_from_placeholder`

```python
def formatted_href_from_placeholder(href: str, entries_by_index: dict[int, LinkDestination]) -> str | None
```

Return formatted URL for a placeholder href.

<details>
<summary>Code:</summary>

```python
def formatted_href_from_placeholder(href: str, entries_by_index: dict[int, LinkDestination]) -> str | None:
    if not href.startswith(PLACEHOLDER_PREFIX):
        return None
    try:
        index = int(href.removeprefix(PLACEHOLDER_PREFIX))
    except ValueError:
        return None
    entry = entries_by_index.get(index)
    if entry is None:
        return None
    url, _title = split_inline_destination(format_inline_link_destination(entry.destination))
    return url
```

</details>

## 🔧 Function `formatted_title_from_placeholder`

```python
def formatted_title_from_placeholder(href: str, entries_by_index: dict[int, LinkDestination]) -> str | None
```

Return pre-normalized title suffix for a placeholder href.

<details>
<summary>Code:</summary>

```python
def formatted_title_from_placeholder(href: str, entries_by_index: dict[int, LinkDestination]) -> str | None:
    if not href.startswith(PLACEHOLDER_PREFIX):
        return None
    try:
        index = int(href.removeprefix(PLACEHOLDER_PREFIX))
    except ValueError:
        return None
    entry = entries_by_index.get(index)
    if entry is None:
        return None
    return entry.title
```

</details>
