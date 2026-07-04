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
- [🔧 Function `_decode_unicode_percent_sequences`](#-function-_decode_unicode_percent_sequences)
- [🔧 Function `_encode_special_characters`](#-function-_encode_special_characters)
- [🔧 Function `_extract_link_destinations_from_text`](#-function-_extract_link_destinations_from_text)
- [🔧 Function `_format_link_url`](#-function-_format_link_url)
- [🔧 Function `_utf8_char_byte_length`](#-function-_utf8_char_byte_length)

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

## 🔧 Function `_decode_unicode_percent_sequences`

```python
def _decode_unicode_percent_sequences(text: str) -> str
```

Decode percent-encoded UTF-8 text while preserving ASCII encodings like `%3E`.

<details>
<summary>Code:</summary>

```python
def _decode_unicode_percent_sequences(text: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(text):
        if text[index] != "%" or index + 2 >= len(text):
            result.append(text[index])
            index += 1
            continue
        hex_part = text[index + 1 : index + 3]
        if not _HEX_BYTE_RE.fullmatch(hex_part):
            result.append(text[index])
            index += 1
            continue
        lead = int(hex_part, 16)
        if lead < 0x80:
            result.append(text[index : index + 3])
            index += 3
            continue
        char_len = _utf8_char_byte_length(lead)
        if char_len == 0:
            result.append(text[index : index + 3])
            index += 3
            continue
        encoded_len = char_len * 3
        chunk = text[index : index + encoded_len]
        if len(chunk) != encoded_len:
            result.append(text[index : index + 3])
            index += 3
            continue
        byte_values: list[int] = []
        valid = True
        for byte_index in range(char_len):
            pos = index + byte_index * 3
            if text[pos] != "%":
                valid = False
                break
            next_hex = text[pos + 1 : pos + 3]
            if not _HEX_BYTE_RE.fullmatch(next_hex):
                valid = False
                break
            byte_values.append(int(next_hex, 16))
        if not valid:
            result.append(text[index : index + 3])
            index += 3
            continue
        try:
            result.append(bytes(byte_values).decode("utf-8"))
        except UnicodeDecodeError:
            result.append(text[index : index + 3])
            index += 3
            continue
        index += encoded_len
    return "".join(result)
```

</details>

## 🔧 Function `_encode_special_characters`

```python
def _encode_special_characters(url: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _encode_special_characters(url: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(url):
        char = url[index]
        if char == "%" and index + 2 < len(url) and re.fullmatch(r"[0-9A-Fa-f]{2}", url[index + 1 : index + 3]):
            result.append(url[index : index + 3])
            index += 3
            continue
        if char == ">":
            result.append("%3E")
            index += 1
            continue
        result.append(char)
        index += 1
    return "".join(result)
```

</details>

## 🔧 Function `_extract_link_destinations_from_text`

```python
def _extract_link_destinations_from_text(body: str) -> tuple[str, list[LinkDestination]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _extract_link_destinations_from_text(body: str, *, start_index: int) -> tuple[str, list[LinkDestination]]:
    entries: list[LinkDestination] = []
    index = start_index

    def handler(prefix: str, destination: str, suffix: str) -> str:
        nonlocal index
        url, title = split_inline_destination(destination)
        display_title = format_link_title(_unescape_title(title)) if title is not None else None
        entries.append(LinkDestination(index=index, destination=url, title=display_title))
        title_suffix = f" {title}" if title is not None else ""
        replacement = f"{prefix}{make_placeholder(PLACEHOLDER_PREFIX, index)}{title_suffix}{suffix}"
        index += 1
        return replacement

    return scan_inline_links(body, handler), entries
```

</details>

## 🔧 Function `_format_link_url`

```python
def _format_link_url(url: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_link_url(url: str, *, wrap_parentheses: bool = True) -> str:
    url = decode_percent_encoded_url(url.replace("&amp;", "&"))
    if url.startswith("<") and url.endswith(">"):
        return url
    if wrap_parentheses and "()" in url:
        encoded = _encode_special_characters(url)
        return f"<{encoded}>"
    return url
```

</details>

## 🔧 Function `_utf8_char_byte_length`

```python
def _utf8_char_byte_length(lead_byte: int) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _utf8_char_byte_length(lead_byte: int) -> int:
    if lead_byte < 0x80:
        return 1
    if lead_byte < 0xE0:
        return 2
    if lead_byte < 0xF0:
        return 3
    if lead_byte < 0xF8:
        return 4
    return 0
```

</details>
