---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `formatter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MdFormatter`](#%EF%B8%8F-class-mdformatter)
  - [⚙️ Method `__call__`](#%EF%B8%8F-method-__call__)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `format`](#%EF%B8%8F-method-format)
  - [⚙️ Method `format_file`](#%EF%B8%8F-method-format_file)
  - [⚙️ Method `format_folder`](#%EF%B8%8F-method-format_folder)
  - [⚙️ Method `normalize_line_endings (staticmethod)`](#%EF%B8%8F-method-normalize_line_endings-staticmethod)
  - [⚙️ Method `read_markdown_text (staticmethod)`](#%EF%B8%8F-method-read_markdown_text-staticmethod)

</details>

## 🏛️ Class `MdFormatter`

```python
class MdFormatter
```

Format Markdown text inspired by Prettier Markdown parser.

<details>
<summary>Code:</summary>

```python
class MdFormatter:

    def __call__(self, text: str) -> str:
        """Format Markdown text.

        Args:

        - `text` (`str`): Markdown source text.

        Returns:

        - `str`: Formatted Markdown text.

        """
        return self.format(text)

    def __init__(
        self,
        *,
        end_of_line: str = "crlf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
        format_math: bool = True,
        format_code_blocks: bool = True,
        promote_first_heading_to_h1: bool = True,
    ) -> None:
        """Initialize the MdFormatter.

        Args:

        - `end_of_line` (`str`): Line ending style (`crlf` or `lf`). Defaults to `crlf`.
        - `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`). Defaults to `preserve`.
        - `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.
        - `apply_prose_fixes` (`bool`): Apply mechanical MdChecker autofixes (typography,
          H006 — H062 subset, H071/H072/H075, H080 — H084, H088, H090 — H092; H063 bare
          filenames). Defaults to `True`. H064 — H066 are applied by the structural
          format pipeline regardless.
        - `format_math` (`bool`): Format TeX/LaTeX content inside `$...$` / `$$...$$`. Defaults to `True`.
        - `format_code_blocks` (`bool`): Format fenced code block bodies for supported languages
          (`latex` / `tex`, `md` / `markdown`). Defaults to `True`.
        - `promote_first_heading_to_h1` (`bool`): Apply H092 (first ATX heading → H1). Defaults to
          `True` for documents; docstring and nested Markdown fragments should pass `False`.

        """
        self.options = _FormatOptions(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
            format_math=format_math,
            format_code_blocks=format_code_blocks,
            promote_first_heading_to_h1=promote_first_heading_to_h1,
        )

    def format(self, text: str) -> str:
        """Format Markdown text.

        `prose_wrap` matches Prettier: `preserve` (default), `always`, or `never`.
        Line wrapping uses `print_width` only when `prose_wrap` is `always`.

        Args:

        - `text` (`str`): Markdown source text.

        Returns:

        - `str`: Formatted Markdown text.

        """
        from harrix_pylib.funcs_md import is_raw_markdown_enabled  # noqa: PLC0415

        if is_raw_markdown_enabled(text):
            return text
        return _format_with_options(text, self.options)

    def format_file(self, filename: Path | str) -> str:
        """Format a Markdown file in place when content or line endings change.

        Also organizes sibling note assets (`featured-image.*` in the note root,
        media under `img/`, other files under `files/`) and rewrites local links.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file.

        Returns:

        - `str`: Status message.

        """
        from harrix_pylib.funcs_md import is_raw_markdown_enabled  # noqa: PLC0415
        from harrix_pylib.md_assets import organize_note_folder_assets  # noqa: PLC0415

        path = Path(filename)
        organize_msg = organize_note_folder_assets(path.parent)
        raw = path.read_bytes()
        document = self.read_markdown_text(path)
        if is_raw_markdown_enabled(document):
            skip_msg = f"Skipped {path}: raw-markdown."
            return f"{organize_msg}\n{skip_msg}" if organize_msg else skip_msg
        document_new = self.format(document)
        if document != document_new or self._needs_end_of_line_rewrite(raw):
            path.write_text(document_new, encoding="utf-8", newline="")
            applied = f"✅ File {path} applied."
            return f"{organize_msg}\n{applied}" if organize_msg else applied
        if organize_msg:
            return organize_msg
        return "File is not changed."

    def format_folder(self, folder: Path | str) -> str:
        """Recursively format Markdown files in a folder.

        Organizes note-folder assets once per unique parent directory, then formats
        each Markdown file.

        Args:

        - `folder` (`Path | str`): Directory containing Markdown files.

        Returns:

        - `str`: Newline-separated status messages.

        """
        from harrix_pylib import funcs_file  # noqa: PLC0415
        from harrix_pylib.md_assets import organize_note_folder_assets  # noqa: PLC0415

        root = Path(folder).resolve()
        lines: list[str] = []
        organized_parents: set[Path] = set()
        for md_file in root.rglob("*.md"):
            if funcs_file.should_ignore_path(md_file):
                continue
            parent = md_file.parent.resolve()
            if parent in organized_parents:
                continue
            organized_parents.add(parent)
            organize_msg = organize_note_folder_assets(parent)
            if organize_msg:
                lines.append(organize_msg)

        format_msg = funcs_file.apply_func(folder, ".md", self.format_file)
        if format_msg:
            lines.append(format_msg)
        return "\n".join(lines)

    @staticmethod
    def normalize_line_endings(text: str) -> str:
        r"""Normalize mixed or corrupted line endings to LF.

        Handles CRLF applied twice (`\r\r\n`), which otherwise becomes a blank
        line between every source line after a two-step `\r` cleanup or
        after `pathlib.Path.read_text` universal-newline translation.

        Args:

        - `text` (`str`): Text with mixed line endings.

        Returns:

        - `str`: Text normalized to LF line endings.

        """
        return re.sub(r"\r+\n", "\n", text).replace("\r", "\n")

    @staticmethod
    def read_markdown_text(filename: Path | str) -> str:
        r"""Read Markdown from disk without universal-newline mangling of `\r\r\n`.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file.

        Returns:

        - `str`: File contents with normalized line endings.

        """
        path = Path(filename)
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            data = data[3:]
        return MdFormatter.normalize_line_endings(data.decode("utf-8"))

    def _needs_end_of_line_rewrite(self, raw: bytes) -> bool:
        """Return `True` when on-disk endings disagree with `end_of_line`."""
        if b"\n" not in raw:
            return False
        has_crlf = b"\r\n" in raw
        if self.options.end_of_line == "lf":
            return has_crlf
        if self.options.end_of_line == "crlf":
            return not has_crlf
        return False
```

</details>

### ⚙️ Method `__call__`

```python
def __call__(self, text: str) -> str
```

Format Markdown text.

Args:

- `text` (`str`): Markdown source text.

Returns:

- `str`: Formatted Markdown text.

<details>
<summary>Code:</summary>

```python
def __call__(self, text: str) -> str:
        return self.format(text)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, end_of_line: str = 'crlf', prose_wrap: str = 'preserve', print_width: int = 80, apply_prose_fixes: bool = True, format_math: bool = True, format_code_blocks: bool = True, promote_first_heading_to_h1: bool = True) -> None
```

Initialize the MdFormatter.

Args:

- `end_of_line` (`str`): Line ending style (`crlf` or `lf`). Defaults to `crlf`.
- `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`). Defaults to `preserve`.
- `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.
- `apply_prose_fixes` (`bool`): Apply mechanical MdChecker autofixes (typography,
  H006 — H062 subset, H071/H072/H075, H080 — H084, H088, H090 — H092; H063 bare
  filenames). Defaults to `True`. H064 — H066 are applied by the structural
  format pipeline regardless.
- `format_math` (`bool`): Format TeX/LaTeX content inside `$...$` / `$$...$$`. Defaults to `True`.
- `format_code_blocks` (`bool`): Format fenced code block bodies for supported languages
  (`latex` / `tex`, `md` / `markdown`). Defaults to `True`.
- `promote_first_heading_to_h1` (`bool`): Apply H092 (first ATX heading → H1). Defaults to
  `True` for documents; docstring and nested Markdown fragments should pass `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        end_of_line: str = "crlf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
        format_math: bool = True,
        format_code_blocks: bool = True,
        promote_first_heading_to_h1: bool = True,
    ) -> None:
        self.options = _FormatOptions(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
            format_math=format_math,
            format_code_blocks=format_code_blocks,
            promote_first_heading_to_h1=promote_first_heading_to_h1,
        )
```

</details>

### ⚙️ Method `format`

```python
def format(self, text: str) -> str
```

Format Markdown text.

`prose_wrap` matches Prettier: `preserve` (default), `always`, or `never`.
Line wrapping uses `print_width` only when `prose_wrap` is `always`.

Args:

- `text` (`str`): Markdown source text.

Returns:

- `str`: Formatted Markdown text.

<details>
<summary>Code:</summary>

```python
def format(self, text: str) -> str:
        from harrix_pylib.funcs_md import is_raw_markdown_enabled  # noqa: PLC0415

        if is_raw_markdown_enabled(text):
            return text
        return _format_with_options(text, self.options)
```

</details>

### ⚙️ Method `format_file`

```python
def format_file(self, filename: Path | str) -> str
```

Format a Markdown file in place when content or line endings change.

Also organizes sibling note assets (`featured-image.*` in the note root,
media under `img/`, other files under `files/`) and rewrites local links.

Args:

- `filename` (`Path | str`): Path to the Markdown file.

Returns:

- `str`: Status message.

<details>
<summary>Code:</summary>

```python
def format_file(self, filename: Path | str) -> str:
        from harrix_pylib.funcs_md import is_raw_markdown_enabled  # noqa: PLC0415
        from harrix_pylib.md_assets import organize_note_folder_assets  # noqa: PLC0415

        path = Path(filename)
        organize_msg = organize_note_folder_assets(path.parent)
        raw = path.read_bytes()
        document = self.read_markdown_text(path)
        if is_raw_markdown_enabled(document):
            skip_msg = f"Skipped {path}: raw-markdown."
            return f"{organize_msg}\n{skip_msg}" if organize_msg else skip_msg
        document_new = self.format(document)
        if document != document_new or self._needs_end_of_line_rewrite(raw):
            path.write_text(document_new, encoding="utf-8", newline="")
            applied = f"✅ File {path} applied."
            return f"{organize_msg}\n{applied}" if organize_msg else applied
        if organize_msg:
            return organize_msg
        return "File is not changed."
```

</details>

### ⚙️ Method `format_folder`

```python
def format_folder(self, folder: Path | str) -> str
```

Recursively format Markdown files in a folder.

Organizes note-folder assets once per unique parent directory, then formats
each Markdown file.

Args:

- `folder` (`Path | str`): Directory containing Markdown files.

Returns:

- `str`: Newline-separated status messages.

<details>
<summary>Code:</summary>

```python
def format_folder(self, folder: Path | str) -> str:
        from harrix_pylib import funcs_file  # noqa: PLC0415
        from harrix_pylib.md_assets import organize_note_folder_assets  # noqa: PLC0415

        root = Path(folder).resolve()
        lines: list[str] = []
        organized_parents: set[Path] = set()
        for md_file in root.rglob("*.md"):
            if funcs_file.should_ignore_path(md_file):
                continue
            parent = md_file.parent.resolve()
            if parent in organized_parents:
                continue
            organized_parents.add(parent)
            organize_msg = organize_note_folder_assets(parent)
            if organize_msg:
                lines.append(organize_msg)

        format_msg = funcs_file.apply_func(folder, ".md", self.format_file)
        if format_msg:
            lines.append(format_msg)
        return "\n".join(lines)
```

</details>

### ⚙️ Method `normalize_line_endings (staticmethod)`

```python
def normalize_line_endings(text: str) -> str
```

Normalize mixed or corrupted line endings to LF.

Handles CRLF applied twice (`\r\r\n`), which otherwise becomes a blank
line between every source line after a two-step `\r` cleanup or
after `pathlib.Path.read_text` universal-newline translation.

Args:

- `text` (`str`): Text with mixed line endings.

Returns:

- `str`: Text normalized to LF line endings.

<details>
<summary>Code:</summary>

```python
def normalize_line_endings(text: str) -> str:
        return re.sub(r"\r+\n", "\n", text).replace("\r", "\n")
```

</details>

### ⚙️ Method `read_markdown_text (staticmethod)`

```python
def read_markdown_text(filename: Path | str) -> str
```

Read Markdown from disk without universal-newline mangling of `\r\r\n`.

Args:

- `filename` (`Path | str`): Path to the Markdown file.

Returns:

- `str`: File contents with normalized line endings.

<details>
<summary>Code:</summary>

```python
def read_markdown_text(filename: Path | str) -> str:
        path = Path(filename)
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            data = data[3:]
        return MdFormatter.normalize_line_endings(data.decode("utf-8"))
```

</details>
