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
- [🔧 Function `format_reference_link_url`](#-function-format_reference_link_url)
- [🔧 Function `restore_reference_blocks`](#-function-restore_reference_blocks)

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
    lines, trailing = split_lines(body)
    code_block_info = list(identify_code_blocks(lines))
    result: list[str] = []
    blocks: list[ReferenceBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        if code_block_info[line_index][1]:
            result.append(lines[line_index])
            line_index += 1
            continue
        line, consumed = _merge_multiline_link_definition(lines, line_index)
        line_index += consumed
        link_match = _LINK_DEF_RE.match(line)
        footnote_match = _FOOTNOTE_DEF_RE.match(line)
        if not link_match and not footnote_match:
            result.append(line)
            continue

        kind = "footnote" if footnote_match else "link"
        block_lines = [line]
        while line_index < len(lines):
            next_line = lines[line_index]
            if _LINK_DEF_RE.match(next_line) or _FOOTNOTE_DEF_RE.match(next_line):
                break
            if not next_line.strip():
                if kind != "footnote":
                    break
                peek_index = line_index + 1
                while peek_index < len(lines) and not lines[peek_index].strip():
                    peek_index += 1
                if peek_index < len(lines) and lines[peek_index].startswith("    "):
                    line_index += 1
                    continue
                break
            if kind == "footnote" and next_line.startswith("    "):
                block_lines.append(next_line)
                line_index += 1
                continue
            break

        blocks.append(ReferenceBlock(index=index, lines=block_lines, kind=kind))
        placeholder = make_placeholder(PLACEHOLDER_PREFIX, index)
        previous_line = result[-1] if result else ""
        if (
            result
            and previous_line.strip()
            and PLACEHOLDER_PREFIX not in previous_line
            and not _LINK_DEF_RE.match(previous_line)
            and not _FOOTNOTE_DEF_RE.match(previous_line)
            and not _line_is_short_link_reference(previous_line)
        ):
            result[-1] = f"{result[-1]} {placeholder}"
        else:
            if result and _line_is_short_link_reference(result[-1]):
                result.append("")
            result.append(placeholder)
        index += 1
        if line_index < len(lines) and not lines[line_index].strip():
            next_index = line_index + 1
            if next_index < len(lines):
                next_line = lines[next_index]
                if _LINK_DEF_RE.match(next_line) or _FOOTNOTE_DEF_RE.match(next_line):
                    line_index += 1

    return join_lines(result, trailing_newline=trailing), blocks
```

</details>

## 🔧 Function `format_reference_link_url`

```python
def format_reference_link_url(url: str) -> str
```

Return canonical URL text for link-reference definitions.

<details>
<summary>Code:</summary>

```python
def format_reference_link_url(url: str) -> str:
    return format_link_url(url, wrap_parentheses=False)
```

</details>

## 🔧 Function `restore_reference_blocks`

```python
def restore_reference_blocks(text: str, blocks: list[ReferenceBlock]) -> str
```

Restore reference-definition blocks, optionally applying prose wrap.

<details>
<summary>Code:</summary>

```python
def restore_reference_blocks(
    text: str,
    blocks: list[ReferenceBlock],
    *,
    options: FormatOptions | None = None,
    print_width: int | None = None,
) -> str:
    fmt_options = options or FormatOptions()
    width = print_width if print_width is not None else fmt_options.print_width
    if not blocks:
        return text
    blocks_by_index = {block.index: block for block in blocks}
    lines, trailing = split_lines(text)
    restored: list[str] = []
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        if not _PLACEHOLDER_RE.search(line):
            restored.append(line)
            line_index += 1
            continue

        merged_line = line
        while line_index + 1 < len(lines):
            next_line = lines[line_index + 1]
            if not _PLACEHOLDER_RE.search(next_line):
                break
            next_match = _PLACEHOLDER_RE.search(next_line)
            if next_match is None or next_match.start() > 0:
                break
            if _PLACEHOLDER_RE.sub("", next_line).strip():
                break
            merged_line = f"{merged_line} {next_line.strip()}"
            line_index += 1

        first_match = _PLACEHOLDER_RE.search(merged_line)
        if first_match and first_match.start() > 0:
            restored.extend(_restore_inline_reference_line(merged_line, blocks_by_index, print_width=width))
            line_index += 1
            continue

        emitted_block = False
        for match in _PLACEHOLDER_RE.finditer(merged_line):
            block_index = int(match.group().removeprefix(PLACEHOLDER_PREFIX))
            block = blocks_by_index.get(block_index)
            if block is None:
                restored.append(match.group())
            else:
                if emitted_block and block.kind == "footnote":
                    restored.append("")
                restored.extend(_format_reference_block(block, options=fmt_options, print_width=width))
                emitted_block = True
        line_index += 1
    return join_lines(restored, trailing_newline=trailing)
```

</details>
