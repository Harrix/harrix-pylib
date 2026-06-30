---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `formatter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_markdown_content`](#-function-format_markdown_content)
- [🔧 Function `normalize_line_endings`](#-function-normalize_line_endings)
- [🔧 Function `read_markdown_text`](#-function-read_markdown_text)
- [🔧 Function `_ensure_blank_line_in_empty_fences`](#-function-_ensure_blank_li
  ne_in_empty_fences)
- [🔧 Function `_format_with_options`](#-function-_format_with_options)
- [🔧 Function `_normalize_end_of_line`](#-function-_normalize_end_of_line)

</details>

## 🔧 Function `format_markdown_content`

```python
def format_markdown_content(text: str) -> str
```

Format Markdown text with Prettier-like defaults.

<details>
<summary>Code:</summary>

```python
def format_markdown_content(text: str, *, end_of_line: str = "crlf") -> str:
    options = FormatOptions(end_of_line=end_of_line, prose_wrap="always")
    return _format_with_options(text, options)
```

</details>

## 🔧 Function `normalize_line_endings`

```python
def normalize_line_endings(text: str) -> str
```

Normalize mixed or corrupted line endings to LF.

Handles CRLF applied twice (`\r\r\n`), which otherwise becomes a blank
line
between every source line after the legacy two-step `\r` cleanup or
after :func:
`pathlib.Path.read_text` universal-newline translation.

<details>
<summary>Code:</summary>

```python
def normalize_line_endings(text: str) -> str:
    return re.sub(r"\r+\n", "\n", text).replace("\r", "\n")
```

</details>

## 🔧 Function `read_markdown_text`

```python
def read_markdown_text(filename: Path | str) -> str
```

Read Markdown from disk without universal-newline mangling of `\r\r\n`.

<details>
<summary>Code:</summary>

```python
def read_markdown_text(filename: Path | str) -> str:
    path = Path(filename)
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return normalize_line_endings(data.decode("utf-8"))
```

</details>

## 🔧 Function `_ensure_blank_line_in_empty_fences`

```python
def _ensure_blank_line_in_empty_fences(body: str) -> str
```

Ensure empty fenced blocks are parsed as fences, not inline code.

<details>
<summary>Code:</summary>

```python
def _ensure_blank_line_in_empty_fences(body: str) -> str:
    return _EMPTY_FENCE_RE.sub(r"\g<indent>\g<fence>\n\n\g<indent>\g<fence>", body)
```

</details>

## 🔧 Function `_format_with_options`

```python
def _format_with_options(text: str, options: FormatOptions) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_with_options(text: str, options: FormatOptions) -> str:
    normalized = normalize_line_endings(text)
    front_matter, body = split_front_matter(normalized)
    if front_matter:
        front_matter = compact_front_matter(front_matter)
    body = _ensure_blank_line_in_empty_fences(body)
    body, ignore_blocks = extract_ignore_blocks(body)
    body, code_blocks = extract_code_blocks(body)
    body, reference_blocks = extract_reference_blocks(body)
    body, task_list_markers = extract_task_list_markers(body)
    body = collapse_extra_blank_lines(body)
    body = unwrap_spurious_table_rows(ensure_blank_line_after_tables(body))
    body = ensure_blank_line_after_lists(body)
    if not body.strip() and front_matter and not reference_blocks:
        result = front_matter.rstrip() + "\n"
    elif not body.strip() and not front_matter and reference_blocks:
        rendered_body = restore_reference_blocks("", reference_blocks, print_width=options.print_width)
        result = rendered_body
    else:
        parser = get_markdown_parser()
        tokens = parser.parse(body)
        rendered_body = render_tokens(tokens, options=options, task_list_markers=task_list_markers)
        rendered_body = restore_code_blocks(rendered_body, code_blocks)
        rendered_body = restore_reference_blocks(rendered_body, reference_blocks, print_width=options.print_width)
        rendered_body = restore_ignore_blocks(rendered_body, ignore_blocks)
        result = join_front_matter(front_matter, rendered_body) if front_matter else rendered_body
    result = trim_trailing_blank_lines(result)
    return _normalize_end_of_line(result, options.end_of_line)
```

</details>

## 🔧 Function `_normalize_end_of_line`

```python
def _normalize_end_of_line(text: str, end_of_line: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _normalize_end_of_line(text: str, end_of_line: str) -> str:
    normalized = normalize_line_endings(text)
    if end_of_line == "lf":
        return normalized
    if end_of_line == "crlf":
        return normalized.replace("\n", "\r\n")
    msg = f"Unsupported end_of_line value: {end_of_line}"
    raise ValueError(msg)
```

</details>
