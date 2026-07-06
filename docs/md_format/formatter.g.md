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

</details>

## 🔧 Function `format_markdown_content`

```python
def format_markdown_content(text: str) -> str
```

Format Markdown text.

`prose_wrap` matches Prettier: `preserve` (default), `always`, or `never`.
Line wrapping uses `print_width` only when `prose_wrap` is `always`.

<details>
<summary>Code:</summary>

```python
def format_markdown_content(
    text: str,
    *,
    end_of_line: str = "crlf",
    prose_wrap: str = "preserve",
    print_width: int = 80,
) -> str:
    options = FormatOptions(end_of_line=end_of_line, prose_wrap=prose_wrap, print_width=print_width)
    return _format_with_options(text, options)
```

</details>

## 🔧 Function `normalize_line_endings`

```python
def normalize_line_endings(text: str) -> str
```

Normalize mixed or corrupted line endings to LF.

Handles CRLF applied twice (`\r\r\n`), which otherwise becomes a blank
line between every source line after the legacy two-step `\r` cleanup or
after :func:`pathlib.Path.read_text` universal-newline translation.

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
