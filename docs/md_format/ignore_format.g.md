---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ignore_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IgnoreBlock`](#️-class-ignoreblock)
- [🔧 Function `extract_ignore_blocks`](#-function-extract_ignore_blocks)
- [🔧 Function `restore_ignore_blocks`](#-function-restore_ignore_blocks)
- [🔧 Function `_join_lines`](#-function-_join_lines)
- [🔧 Function `_placeholder`](#-function-_placeholder)
- [🔧 Function `_split_lines`](#-function-_split_lines)

</details>

## 🏛️ Class `IgnoreBlock`

```python
class IgnoreBlock
```

Stored ignored Markdown region.

<details>
<summary>Code:</summary>

```python
class IgnoreBlock:

    index: int
    text: str
```

</details>

## 🔧 Function `extract_ignore_blocks`

```python
def extract_ignore_blocks(body: str) -> tuple[str, list[IgnoreBlock]]
```

Replace ignored regions with placeholders.

<details>
<summary>Code:</summary>

```python
def extract_ignore_blocks(body: str) -> tuple[str, list[IgnoreBlock]]:
    lines, trailing = _split_lines(body)
    result: list[str] = []
    blocks: list[IgnoreBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        start_match = _IGNORE_START_RE.search(line)
        if start_match:
            block_lines = [line]
            line_index += 1
            while line_index < len(lines):
                block_lines.append(lines[line_index])
                if _IGNORE_END_RE.search(lines[line_index]):
                    line_index += 1
                    break
                line_index += 1
            blocks.append(IgnoreBlock(index=index, text=_join_lines(block_lines, trailing_newline=False)))
            result.append(_placeholder(index))
            index += 1
            continue

        if _IGNORE_LINE_RE.search(line):
            block_lines = [line]
            line_index += 1
            while line_index < len(lines):
                if lines[line_index].strip() == "":
                    break
                if _IGNORE_LINE_RE.search(lines[line_index]) or _IGNORE_START_RE.search(lines[line_index]):
                    break
                block_lines.append(lines[line_index])
                line_index += 1
            blocks.append(IgnoreBlock(index=index, text=_join_lines(block_lines, trailing_newline=False)))
            result.append(_placeholder(index))
            index += 1
            continue

        result.append(line)
        line_index += 1

    return _join_lines(result, trailing_newline=trailing), blocks
```

</details>

## 🔧 Function `restore_ignore_blocks`

```python
def restore_ignore_blocks(text: str, blocks: list[IgnoreBlock]) -> str
```

Restore ignored regions verbatim.

<details>
<summary>Code:</summary>

```python
def restore_ignore_blocks(text: str, blocks: list[IgnoreBlock]) -> str:
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
            restored.extend(block.text.split("\n"))
            continue
        restored.append(line)
    return _join_lines(restored, trailing_newline=trailing)
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
