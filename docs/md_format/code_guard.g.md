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
    tight: bool = False
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
    lines, has_trailing_newline = split_lines(body)
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
        placeholder_line = f"{base_indent}{make_placeholder(PLACEHOLDER_PREFIX, index)}"

        inserted_blank = False
        if result and result[-1].strip():
            result.append("")
            inserted_blank = True
        result.append(placeholder_line)
        if line_index < len(lines) and lines[line_index].strip():
            result.append("")
            inserted_blank = True

        blocks.append(CodeBlock(index=index, lines=block_lines, base_indent=base_indent, tight=inserted_blank))
        index += 1

    return join_lines(result, trailing_newline=has_trailing_newline), blocks
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
def restore_code_blocks(text: str, blocks: list[CodeBlock], *, options: FormatOptions | None = None) -> str:
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
            block_lines = _format_markdown_fence_block(block.lines, _options=options)
            current_indent = _leading_whitespace(line)
            restored.extend(_reindent_line(block_line, block.base_indent, current_indent) for block_line in block_lines)
            continue
        restored.append(line)
    return join_lines(restored, trailing_newline=has_trailing_newline)
```

</details>
