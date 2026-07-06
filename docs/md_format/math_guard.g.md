---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `math_guard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `EmptyMathBlock`](#️-class-emptymathblock)
- [🔧 Function `extract_empty_math_blocks`](#-function-extract_empty_math_blocks)
- [🔧 Function `restore_empty_math_blocks`](#-function-restore_empty_math_blocks)

</details>

## 🏛️ Class `EmptyMathBlock`

```python
class EmptyMathBlock
```

Stored empty `$$` block extracted from Markdown body.

<details>
<summary>Code:</summary>

```python
class EmptyMathBlock:

    index: int
    lines: list[str]
```

</details>

## 🔧 Function `extract_empty_math_blocks`

```python
def extract_empty_math_blocks(body: str) -> tuple[str, list[EmptyMathBlock]]
```

Replace empty block-math regions with placeholders before parsing.

<details>
<summary>Code:</summary>

```python
def extract_empty_math_blocks(body: str) -> tuple[str, list[EmptyMathBlock]]:
    lines, has_trailing_newline = split_lines(body)
    in_code = [inside for _line, inside in identify_code_blocks(lines)]
    result: list[str] = []
    blocks: list[EmptyMathBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        if in_code[line_index]:
            result.append(lines[line_index])
            line_index += 1
            continue

        close_index = _find_empty_math_block_close(lines, line_index, in_code)
        if close_index is None:
            result.append(lines[line_index])
            line_index += 1
            continue

        block_lines = lines[line_index : close_index + 1]
        base_indent = _leading_whitespace(block_lines[0])
        placeholder_line = f"{base_indent}{make_placeholder(PLACEHOLDER_PREFIX, index)}"
        result.append(placeholder_line)
        blocks.append(EmptyMathBlock(index=index, lines=block_lines))
        index += 1
        line_index = close_index + 1

    return join_lines(result, trailing_newline=has_trailing_newline), blocks
```

</details>

## 🔧 Function `restore_empty_math_blocks`

```python
def restore_empty_math_blocks(text: str, blocks: list[EmptyMathBlock]) -> str
```

Restore empty block-math regions from placeholders.

<details>
<summary>Code:</summary>

```python
def restore_empty_math_blocks(text: str, blocks: list[EmptyMathBlock]) -> str:
    if not blocks:
        return text

    blocks_by_index = {block.index: block for block in blocks}
    lines, has_trailing_newline = split_lines(text)
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
            restored.extend(block.lines)
            continue
        restored.append(line)
    return join_lines(restored, trailing_newline=has_trailing_newline)
```

</details>
