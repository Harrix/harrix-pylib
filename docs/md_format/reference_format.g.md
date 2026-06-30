---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `reference_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReferenceBlock`](#️-class-referenceblock)
- [🔧 Function `extract_reference_blocks`](#-function-extract_reference_blocks)
- [🔧 Function `restore_reference_blocks`](#-function-restore_reference_blocks)
- [🔧 Function `_format_footnote_block`](#-function-_format_footnote_block)
- [🔧 Function `_format_link_definition`](#-function-_format_link_definition)
- [🔧 Function `_format_reference_block`](#-function-_format_reference_block)
- [🔧 Function `_join_lines`](#-function-_join_lines)
- [🔧 Function `_placeholder`](#-function-_placeholder)
- [🔧 Function `_split_lines`](#-function-_split_lines)

</details>

## 🏛️ Class `ReferenceBlock`

```python
class ReferenceBlock
```

Stored reference-definition block.

<details>
<summary>Code:</summary>

```python
class ReferenceBlock:

    index: int
    lines: list[str]
    kind: str  # "link" or "footnote"
```

</details>

## 🔧 Function `extract_reference_blocks`

```python
def extract_reference_blocks(body: str) -> tuple[str, list[ReferenceBlock]]
```

Replace link/footnote definitions with placeholders.

<details>
<summary>Code:</summary>

```python
def extract_reference_blocks(body: str) -> tuple[str, list[ReferenceBlock]]:
    lines, trailing = _split_lines(body)
    result: list[str] = []
    blocks: list[ReferenceBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        link_match = _LINK_DEF_RE.match(line)
        footnote_match = _FOOTNOTE_DEF_RE.match(line)
        if not link_match and not footnote_match:
            result.append(line)
            line_index += 1
            continue

        kind = "footnote" if footnote_match else "link"
        block_lines = [line]
        line_index += 1
        while line_index < len(lines):
            next_line = lines[line_index]
            if not next_line.strip():
                break
            if _LINK_DEF_RE.match(next_line) or _FOOTNOTE_DEF_RE.match(next_line):
                break
            if kind == "footnote" and next_line.startswith("    "):
                block_lines.append(next_line)
                line_index += 1
                continue
            break

        blocks.append(ReferenceBlock(index=index, lines=block_lines, kind=kind))
        result.append(_placeholder(index))
        index += 1

    return _join_lines(result, trailing_newline=trailing), blocks
```

</details>

## 🔧 Function `restore_reference_blocks`

```python
def restore_reference_blocks(text: str, blocks: list[ReferenceBlock]) -> str
```

Restore reference-definition blocks, applying prose wrap to footnotes.

<details>
<summary>Code:</summary>

```python
def restore_reference_blocks(text: str, blocks: list[ReferenceBlock], *, print_width: int = 80) -> str:
    if not blocks:
        return text
    blocks_by_index = {block.index: block for block in blocks}
    lines, trailing = _split_lines(text)
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
            restored.extend(_format_reference_block(block, print_width=print_width))
            continue
        restored.append(line)
    return _join_lines(restored, trailing_newline=trailing)
```

</details>

## 🔧 Function `_format_footnote_block`

```python
def _format_footnote_block(lines: list[str]) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_footnote_block(lines: list[str], *, print_width: int) -> list[str]:
    first = lines[0]
    match = _FOOTNOTE_DEF_RE.match(first)
    if not match:
        return lines
    indent, label, first_text = match.group(1), match.group(2), match.group(3)
    prefix = f"{indent}[^{label}]: "
    continuation = indent + "    "
    body_parts = [first_text, *[line[4:] if line.startswith("    ") else line for line in lines[1:]]]
    body = " ".join(part.strip() for part in body_parts if part.strip())
    wrapped = wrap_prose(body, width=print_width, prefix=prefix, continuation=continuation)
    return wrapped.split("\n")
```

</details>

## 🔧 Function `_format_link_definition`

```python
def _format_link_definition(line: str) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_link_definition(line: str, *, print_width: int) -> list[str]:
    match = _LINK_DEF_RE.match(line)
    if not match:
        return [line]
    indent, label, rest = match.group(1), match.group(2), match.group(3)
    prefix = f"{indent}[{label}]: "
    wrapped = wrap_prose(rest, width=print_width, prefix=prefix, continuation=indent + " " * 4)
    return wrapped.split("\n")
```

</details>

## 🔧 Function `_format_reference_block`

```python
def _format_reference_block(block: ReferenceBlock) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_reference_block(block: ReferenceBlock, *, print_width: int) -> list[str]:
    if block.kind == "footnote":
        return _format_footnote_block(block.lines, print_width=print_width)
    formatted: list[str] = []
    for line in block.lines:
        formatted.extend(_format_link_definition(line, print_width=print_width))
    return formatted
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

## 🔧 Function `_split_lines`

```python
def _split_lines(text: str) -> tuple[list[str], bool]
```

_No docstring provided._

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
