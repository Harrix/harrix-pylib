---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `code_guard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CodeBlock`](#️-class-codeblock)
- [🔧 Function `extract_code_blocks`](#-function-extract_code_blocks)
- [🔧 Function `restore_code_blocks`](#-function-restore_code_blocks)
- [🔧 Function `_join_lines`](#-function-_join_lines)
- [🔧 Function `_leading_whitespace`](#-function-_leading_whitespace)
- [🔧 Function `_placeholder`](#-function-_placeholder)
- [🔧 Function `_reindent_line`](#-function-_reindent_line)
- [🔧 Function `_split_lines`](#-function-_split_lines)
- [🔧 Function `_trim_trailing_blank_lines_before_closing_fence`](#-function-_trim_trailing_blank_lines_before_closing_fence)

</details>

## 🏛️ Class `CodeBlock`

```python
class CodeBlock
```

Stored fenced code block extracted from Markdown body.

<details>
<summary>Code:</summary>

```python
class CodeBlock:

    index: int
    lines: list[str]
    base_indent: str
```

</details>

## 🔧 Function `extract_code_blocks`

```python
def extract_code_blocks(body: str) -> tuple[str, list[CodeBlock]]
```

Replace fenced code blocks with placeholders and store originals verbatim.

<details>
<summary>Code:</summary>

```python
def extract_code_blocks(body: str) -> tuple[str, list[CodeBlock]]:
    from harrix_pylib.funcs_md import identify_code_blocks  # noqa: PLC0415

    lines, has_trailing_newline = _split_lines(body)
    code_block_info = list(identify_code_blocks(lines))
    result: list[str] = []
    blocks: list[CodeBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        if not code_block_info[line_index][1]:
            result.append(line)
            line_index += 1
            continue

        block_lines: list[str] = []
        while line_index < len(lines) and code_block_info[line_index][1]:
            block_lines.append(lines[line_index])
            line_index += 1

        block_lines = _trim_trailing_blank_lines_before_closing_fence(block_lines)
        base_indent = _leading_whitespace(block_lines[0])
        blocks.append(CodeBlock(index=index, lines=block_lines, base_indent=base_indent))
        placeholder_line = f"{base_indent}{_placeholder(index)}"

        if result and result[-1].strip():
            result.append("")
        result.append(placeholder_line)
        if line_index < len(lines) and lines[line_index].strip():
            result.append("")

        index += 1

    return _join_lines(result, trailing_newline=has_trailing_newline), blocks
```

</details>

## 🔧 Function `restore_code_blocks`

```python
def restore_code_blocks(text: str, blocks: list[CodeBlock]) -> str
```

Restore fenced code blocks from placeholders.

<details>
<summary>Code:</summary>

```python
def restore_code_blocks(text: str, blocks: list[CodeBlock]) -> str:
    if not blocks:
        return text

    blocks_by_index = {block.index: block for block in blocks}
    lines, has_trailing_newline = _split_lines(text)
    restored: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(PLACEHOLDER_PREFIX):
            try:
                block_index = int(stripped.removeprefix(PLACEHOLDER_PREFIX))
            except ValueError:
                restored.append(line)
                continue
            block = blocks_by_index.get(block_index)
            if block is None:
                restored.append(line)
                continue
            current_indent = _leading_whitespace(line)
            restored.extend(_reindent_line(block_line, block.base_indent, current_indent) for block_line in block.lines)
            continue
        restored.append(line)
    return _join_lines(restored, trailing_newline=has_trailing_newline)
```

</details>

## 🔧 Function `_join_lines`

```python
def _join_lines(lines: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text
```

</details>

## 🔧 Function `_leading_whitespace`

```python
def _leading_whitespace(line: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _leading_whitespace(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]
```

</details>

## 🔧 Function `_placeholder`

```python
def _placeholder(index: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _placeholder(index: int) -> str:
    return f"{PLACEHOLDER_PREFIX}{index}"
```

</details>

## 🔧 Function `_reindent_line`

```python
def _reindent_line(line: str, base_indent: str, current_indent: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _reindent_line(line: str, base_indent: str, current_indent: str) -> str:
    if not line.strip():
        return line
    if base_indent and line.startswith(base_indent):
        return current_indent + line[len(base_indent) :]
    if base_indent:
        return current_indent + line
    return line
```

</details>

## 🔧 Function `_split_lines`

```python
def _split_lines(text: str) -> tuple[list[str], bool]
```

Split text into lines without the trailing split artifact from a final newline.

<details>
<summary>Code:</summary>

```python
def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline
```

</details>

## 🔧 Function `_trim_trailing_blank_lines_before_closing_fence`

```python
def _trim_trailing_blank_lines_before_closing_fence(block_lines: list[str]) -> list[str]
```

Drop blank lines immediately before the closing fence line.

<details>
<summary>Code:</summary>

```python
def _trim_trailing_blank_lines_before_closing_fence(block_lines: list[str]) -> list[str]:
    if len(block_lines) < _MIN_FENCED_BLOCK_LINES:
        return block_lines

    trimmed = list(block_lines)
    closing_index = len(trimmed) - 1
    while closing_index >= _MIN_FENCED_BLOCK_LINES and trimmed[closing_index - 1].strip() == "":
        trimmed.pop(closing_index - 1)
        closing_index -= 1
    return trimmed
```

</details>
