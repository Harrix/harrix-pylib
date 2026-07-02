---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ignore_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IgnoreBlock`](#%EF%B8%8F-class-ignoreblock)
- [🔧 Function `extract_ignore_blocks`](#-function-extract_ignore_blocks)
- [🔧 Function `restore_ignore_blocks`](#-function-restore_ignore_blocks)

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
    lines, trailing = split_lines(body)
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
            if any(block_line.lstrip().startswith(">") for block_line in block_lines):
                result.extend(block_lines)
                continue
            blocks.append(IgnoreBlock(index=index, text=join_lines(block_lines, trailing_newline=False)))
            result.append(make_placeholder(PLACEHOLDER_PREFIX, index))
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
            blocks.append(IgnoreBlock(index=index, text=join_lines(block_lines, trailing_newline=False)))
            result.append(make_placeholder(PLACEHOLDER_PREFIX, index))
            index += 1
            continue

        result.append(line)
        line_index += 1

    return join_lines(result, trailing_newline=trailing), blocks
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
    lines, trailing = split_lines(text)
    restored: list[str] = []
    for line in lines:
        stripped = line.strip()
        inline_match = _PLACEHOLDER_RE.search(line)
        if inline_match and inline_match.start() > 0:
            prefix = line[: inline_match.start()].rstrip()
            if prefix:
                restored.append(prefix)
            block_index = int(inline_match.group().removeprefix(PLACEHOLDER_PREFIX))
            block = blocks_by_index.get(block_index)
            if block is not None:
                restored.extend(block.text.split("\n"))
                continue
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
    return join_lines(restored, trailing_newline=trailing)
```

</details>
