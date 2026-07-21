---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `py_docstring_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PyDocstringFormatter`](#️-class-pydocstringformatter)
  - [⚙️ Method `__call__`](#️-method-__call__)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `format`](#️-method-format)
  - [⚙️ Method `format_file`](#️-method-format_file)
  - [⚙️ Method `format_folder`](#️-method-format_folder)
  - [⚙️ Method `iter_code_span_issues`](#️-method-iter_code_span_issues)
  - [⚙️ Method `normalize_code_spans`](#️-method-normalize_code_spans)

</details>

## 🏛️ Class `PyDocstringFormatter`

```python
class PyDocstringFormatter
```

Format Markdown inside Python docstrings, similar to `MdFormatter` for `.md` files.

<details>
<summary>Code:</summary>

```python
class PyDocstringFormatter:

    def __call__(self, filename: Path | str) -> str:
        """Format docstrings in a Python file in place."""
        return self.format_file(filename)

    def __init__(
        self,
        *,
        end_of_line: str = "lf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
    ) -> None:
        """Initialize the docstring formatter.

        Args:

        - `end_of_line` (`str`): Line ending style passed to `MdFormatter` for docstring
          bodies (`crlf` or `lf`). Defaults to `lf` (matches typical Python sources).
        - `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`).
          Defaults to `preserve`.
        - `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.
        - `apply_prose_fixes` (`bool`): Apply mechanical MdChecker autofixes inside docstring
          Markdown. Defaults to `True`.

        """
        self.md_formatter = MdFormatter(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
        )

    def format(self, source: str) -> str:
        """Format Markdown inside docstrings in Python source text.

        Args:

        - `source` (`str`): Python source code.

        Returns:

        - `str`: Source with formatted docstrings (unchanged when nothing applies).

        """
        module = cst.parse_module(source)
        transformer = _DocstringMdFormatTransformer(self)
        return module.visit(transformer).code

    def format_file(self, filename: Path | str) -> str:
        r"""Format Markdown inside Python docstrings in a file.

        Uses `MdFormatter` on multiline docstring bodies, then writes them back so that:

        - Multiline docstrings keep a blank line before the closing quotes
        - When the formatted body contains backslashes, the literal gets an `r`
          prefix (D301) and Markdown escapes are written as single `\` in source
        - Code tokens in prose (`True` / `False` / `None`, and quoted identifiers) use
          backticks; fenced and inline code are left unchanged
        - One-line docstrings get the same prose fixes and code-span normalization, but
          stay on a single physical line between the opening and closing quotes

        Args:

        - `filename` (`Path | str`): Path to the Python file to update.

        Returns:

        - `str`: Status message.

        """
        path = Path(filename)
        raw = path.read_bytes()
        original = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

        # Cheap ast precheck: skip libcst when no docstring would change.
        needs_format = _source_needs_docstring_format(original, md_formatter=self.md_formatter)
        if needs_format is False:
            return "File is not changed."

        try:
            module = cst.parse_module(original)
        except Exception as e:
            return f"⚠️ Skip {path}: parse error: {e}"

        transformer = _DocstringMdFormatTransformer(self)
        updated = module.visit(transformer)
        new_code = updated.code
        if new_code == original:
            if transformer.skipped:
                return f"⚠️ File {path}: skipped {transformer.skipped} docstring(s); unchanged."
            return "File is not changed."
        path.write_text(new_code, encoding="utf-8", newline="\n")
        skip_note = f" (skipped {transformer.skipped})" if transformer.skipped else ""
        return f"✅ File {path} docstring Markdown formatted.{skip_note}"

    def format_folder(self, folder: Path | str) -> str:
        """Recursively format docstrings in Python files in a folder.

        Args:

        - `folder` (`Path | str`): Directory containing Python files.

        Returns:

        - `str`: Newline-separated status messages.

        """
        from harrix_pylib import funcs_file  # noqa: PLC0415

        return funcs_file.apply_func(folder, ".py", self.format_file)

    @staticmethod
    def iter_code_span_issues(text: str) -> Iterator[tuple[int, int, str]]:
        """Yield `(line_index, col_1based, token)` for prose tokens that should use backticks."""
        lines = text.split("\n")
        for line_index, (line, in_fence) in enumerate(_identify_code_blocks(lines)):
            if in_fence:
                continue
            offset = 0
            for segment, in_code in _identify_code_blocks_line(line):
                if not in_code:
                    for match in _QUOTED_CODE_RE.finditer(segment):
                        yield line_index, offset + match.start() + 1, match.group(0)
                    for match in _BARE_LITERAL_RE.finditer(segment):
                        yield line_index, offset + match.start() + 1, match.group(1)
                offset += len(segment)

    @staticmethod
    def normalize_code_spans(text: str) -> str:
        """Wrap code tokens in backticks in docstring Markdown prose.

        Outside fenced and inline code:

        - Bare `True`, `False`, and `None` become `` `True` `` / `` `False` `` / `` `None` ``
        - Quoted identifiers like `'name'` or `"HP001"` become `` `name` `` / `` `HP001` ``

        """
        lines = text.split("\n")
        out_lines: list[str] = []
        for line, in_fence in _identify_code_blocks(lines):
            if in_fence:
                out_lines.append(line)
                continue
            parts: list[str] = []
            for segment, in_code in _identify_code_blocks_line(line):
                if in_code:
                    parts.append(segment)
                else:
                    parts.append(_normalize_prose_segment(segment))
            out_lines.append("".join(parts))
        result = "\n".join(out_lines)
        if text.endswith("\n") and not result.endswith("\n"):
            result += "\n"
        return result
```

</details>

### ⚙️ Method `__call__`

```python
def __call__(self, filename: Path | str) -> str
```

Format docstrings in a Python file in place.

<details>
<summary>Code:</summary>

```python
def __call__(self, filename: Path | str) -> str:
        return self.format_file(filename)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize the docstring formatter.

Args:

- `end_of_line` (`str`): Line ending style passed to `MdFormatter` for docstring
  bodies (`crlf` or `lf`). Defaults to `lf` (matches typical Python sources).
- `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`).
  Defaults to `preserve`.
- `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.
- `apply_prose_fixes` (`bool`): Apply mechanical MdChecker autofixes inside docstring
  Markdown. Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        end_of_line: str = "lf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
    ) -> None:
        self.md_formatter = MdFormatter(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
        )
```

</details>

### ⚙️ Method `format`

```python
def format(self, source: str) -> str
```

Format Markdown inside docstrings in Python source text.

Args:

- `source` (`str`): Python source code.

Returns:

- `str`: Source with formatted docstrings (unchanged when nothing applies).

<details>
<summary>Code:</summary>

```python
def format(self, source: str) -> str:
        module = cst.parse_module(source)
        transformer = _DocstringMdFormatTransformer(self)
        return module.visit(transformer).code
```

</details>

### ⚙️ Method `format_file`

```python
def format_file(self, filename: Path | str) -> str
```

Format Markdown inside Python docstrings in a file.

Uses `MdFormatter` on multiline docstring bodies, then writes them back so that:

- Multiline docstrings keep a blank line before the closing quotes
- When the formatted body contains backslashes, the literal gets an `r`
  prefix (D301) and Markdown escapes are written as single `\` in source
- Code tokens in prose (`True` / `False` / `None`, and quoted identifiers) use
  backticks; fenced and inline code are left unchanged
- One-line docstrings get the same prose fixes and code-span normalization, but
  stay on a single physical line between the opening and closing quotes

Args:

- `filename` (`Path | str`): Path to the Python file to update.

Returns:

- `str`: Status message.

<details>
<summary>Code:</summary>

```python
def format_file(self, filename: Path | str) -> str:
        path = Path(filename)
        raw = path.read_bytes()
        original = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

        # Cheap ast precheck: skip libcst when no docstring would change.
        needs_format = _source_needs_docstring_format(original, md_formatter=self.md_formatter)
        if needs_format is False:
            return "File is not changed."

        try:
            module = cst.parse_module(original)
        except Exception as e:
            return f"⚠️ Skip {path}: parse error: {e}"

        transformer = _DocstringMdFormatTransformer(self)
        updated = module.visit(transformer)
        new_code = updated.code
        if new_code == original:
            if transformer.skipped:
                return f"⚠️ File {path}: skipped {transformer.skipped} docstring(s); unchanged."
            return "File is not changed."
        path.write_text(new_code, encoding="utf-8", newline="\n")
        skip_note = f" (skipped {transformer.skipped})" if transformer.skipped else ""
        return f"✅ File {path} docstring Markdown formatted.{skip_note}"
```

</details>

### ⚙️ Method `format_folder`

```python
def format_folder(self, folder: Path | str) -> str
```

Recursively format docstrings in Python files in a folder.

Args:

- `folder` (`Path | str`): Directory containing Python files.

Returns:

- `str`: Newline-separated status messages.

<details>
<summary>Code:</summary>

```python
def format_folder(self, folder: Path | str) -> str:
        from harrix_pylib import funcs_file  # noqa: PLC0415

        return funcs_file.apply_func(folder, ".py", self.format_file)
```

</details>

### ⚙️ Method `iter_code_span_issues`

```python
def iter_code_span_issues(text: str) -> Iterator[tuple[int, int, str]]
```

Yield `(line_index, col_1based, token)` for prose tokens that should use backticks.

<details>
<summary>Code:</summary>

```python
def iter_code_span_issues(text: str) -> Iterator[tuple[int, int, str]]:
        lines = text.split("\n")
        for line_index, (line, in_fence) in enumerate(_identify_code_blocks(lines)):
            if in_fence:
                continue
            offset = 0
            for segment, in_code in _identify_code_blocks_line(line):
                if not in_code:
                    for match in _QUOTED_CODE_RE.finditer(segment):
                        yield line_index, offset + match.start() + 1, match.group(0)
                    for match in _BARE_LITERAL_RE.finditer(segment):
                        yield line_index, offset + match.start() + 1, match.group(1)
                offset += len(segment)
```

</details>

### ⚙️ Method `normalize_code_spans`

```python
def normalize_code_spans(text: str) -> str
```

Wrap code tokens in backticks in docstring Markdown prose.

Outside fenced and inline code:

- Bare `True`, `False`, and `None` become `` `True` `` / `` `False` `` / `` `None` ``
- Quoted identifiers like `'name'` or `"HP001"` become `` `name` `` / `` `HP001` ``

<details>
<summary>Code:</summary>

```python
def normalize_code_spans(text: str) -> str:
        lines = text.split("\n")
        out_lines: list[str] = []
        for line, in_fence in _identify_code_blocks(lines):
            if in_fence:
                out_lines.append(line)
                continue
            parts: list[str] = []
            for segment, in_code in _identify_code_blocks_line(line):
                if in_code:
                    parts.append(segment)
                else:
                    parts.append(_normalize_prose_segment(segment))
            out_lines.append("".join(parts))
        result = "\n".join(out_lines)
        if text.endswith("\n") and not result.endswith("\n"):
            result += "\n"
        return result
```

</details>
