---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `formatter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MarkdownFormatter`](#️-class-markdownformatter)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `__call__`](#️-method-__call__)
  - [⚙️ Method `format`](#️-method-format)
  - [⚙️ Method `format_file`](#️-method-format_file)
  - [⚙️ Method `format_folder`](#️-method-format_folder)
  - [⚙️ Method `normalize_line_endings`](#️-method-normalize_line_endings)
  - [⚙️ Method `read_markdown_text`](#️-method-read_markdown_text)

</details>

## 🏛️ Class `MarkdownFormatter`

```python
class MarkdownFormatter
```

Format Markdown text inspired by Prettier markdown parser.

<details>
<summary>Code:</summary>

```python
class MarkdownFormatter:
    """Format Markdown text inspired by Prettier markdown parser."""

    def __init__(
        self,
        *,
        end_of_line: str = "crlf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
    ) -> None:
        self.options = FormatOptions(end_of_line=end_of_line, prose_wrap=prose_wrap, print_width=print_width)

    def __call__(self, text: str) -> str:
        return self.format(text)

    def format(self, text: str) -> str:
        return _format_with_options(text, self.options)

    def format_file(self, filename: Path | str) -> str:
        path = Path(filename)
        document = self.read_markdown_text(path)
        document_new = self.format(document)
        if document != document_new:
            path.write_text(document_new, encoding="utf-8", newline="")
            return f"✅ File {path} applied."
        return "File is not changed."

    def format_folder(self, folder: Path | str) -> str:
        from harrix_pylib import funcs_file
        return funcs_file.apply_func(folder, ".md", self.format_file)

    @staticmethod
    def normalize_line_endings(text: str) -> str:
        return re.sub(r"\r+\n", "\n", text).replace("\r", "\n")

    @staticmethod
    def read_markdown_text(filename: Path | str) -> str:
        path = Path(filename)
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            data = data[3:]
        return MarkdownFormatter.normalize_line_endings(data.decode("utf-8"))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize the MarkdownFormatter.

Args:

- `end_of_line` (`str`): Line ending style (`crlf` or `lf`). Defaults to `crlf`.
- `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`). Defaults to `preserve`.
- `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.

### ⚙️ Method `__call__`

```python
def __call__(self, text: str) -> str
```

Format Markdown text.

### ⚙️ Method `format`

```python
def format(self, text: str) -> str
```

Format Markdown text.

``prose_wrap`` matches Prettier: ``preserve`` (default), ``always``, or ``never``.
Line wrapping uses ``print_width`` only when ``prose_wrap`` is ``always``.

### ⚙️ Method `format_file`

```python
def format_file(self, filename: Path | str) -> str
```

Format a Markdown file in place when content changes.

### ⚙️ Method `format_folder`

```python
def format_folder(self, folder: Path | str) -> str
```

Recursively format Markdown files in a folder.

### ⚙️ Method `normalize_line_endings`

```python
def normalize_line_endings(text: str) -> str
```

Normalize mixed or corrupted line endings to LF.

### ⚙️ Method `read_markdown_text`

```python
def read_markdown_text(filename: Path | str) -> str
```

Read Markdown from disk without universal-newline mangling of `\r\r\n`.
