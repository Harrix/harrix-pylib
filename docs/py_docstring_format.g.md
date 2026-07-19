---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `py_docstring_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_python_docstrings`](#-function-format_python_docstrings)
- [🔧 Function `iter_docstring_code_span_issues`](#-function-iter_docstring_code_span_issues)
- [🔧 Function `normalize_docstring_code_spans`](#-function-normalize_docstring_code_spans)

</details>

## 🔧 Function `format_python_docstrings`

```python
def format_python_docstrings(filename: Path | str) -> str
```

Format Markdown inside Python docstrings in a file.

Uses `MdFormatter` on multiline docstring bodies, then writes them back so that:

- Multiline docstrings keep a blank line before the closing quotes
- When the formatted body contains backslashes, the literal gets an `r`
  prefix (D301) and Markdown escapes are written as single `\` in source
- Code tokens in prose (`True` / `False` / `None`, and quoted identifiers) use
  backticks; fenced and inline code are left unchanged
- One-line docstrings only get code-token backtick normalization

Args:

- `filename` (`Path | str`): Path to the Python file to update.

Returns:

- `str`: Status message.

<details>
<summary>Code:</summary>

```python
def format_python_docstrings(filename: Path | str) -> str:
    path = Path(filename)
    original = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(original)
    except Exception as e:
        return f"⚠️ Skip {path}: parse error: {e}"

    transformer = _DocstringMdFormatTransformer()
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

## 🔧 Function `iter_docstring_code_span_issues`

```python
def iter_docstring_code_span_issues(text: str) -> Iterator[tuple[int, int, str]]
```

Yield `(line_index, col_1based, token)` for prose tokens that should use backticks.

<details>
<summary>Code:</summary>

```python
def iter_docstring_code_span_issues(text: str) -> Iterator[tuple[int, int, str]]:
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

## 🔧 Function `normalize_docstring_code_spans`

```python
def normalize_docstring_code_spans(text: str) -> str
```

Wrap code tokens in backticks in docstring Markdown prose.

Outside fenced and inline code:

- Bare `True`, `False`, and `None` become `` `True` `` / `` `False` `` / `` `None` ``
- Quoted identifiers like `'name'` or `"HP001"` become `` `name` `` / `` `HP001` ``

<details>
<summary>Code:</summary>

```python
def normalize_docstring_code_spans(text: str) -> str:
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
