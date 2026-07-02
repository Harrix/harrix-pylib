---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `code_fence.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `identify_code_blocks`](#-function-identify_code_blocks)
- [🔧 Function `identify_code_blocks_line`](#-function-identify_code_blocks_line)

</details>

## 🔧 Function `identify_code_blocks`

```python
def identify_code_blocks(lines: Sequence[str]) -> Iterator[tuple[str, bool]]
```

Yield each line with a flag indicating fenced code-block membership.

<details>
<summary>Code:</summary>

```python
def identify_code_blocks(lines: Sequence[str]) -> Iterator[tuple[str, bool]]:
    code_block_delimiter = None
    for line in lines:
        match = re.match(r"^\s*(`{3,})(.*)", line)
        if match:
            delimiter = match.group(1)
            if code_block_delimiter is None:
                code_block_delimiter = delimiter
            elif code_block_delimiter == delimiter:
                code_block_delimiter = None
            yield line, True
            continue
        if code_block_delimiter:
            yield line, True
        else:
            yield line, False
```

</details>

## 🔧 Function `identify_code_blocks_line`

```python
def identify_code_blocks_line(markdown_line: str) -> Iterator[tuple[str, bool]]
```

Parse a single Markdown line into text and inline-code segments.

<details>
<summary>Code:</summary>

```python
def identify_code_blocks_line(markdown_line: str) -> Iterator[tuple[str, bool]]:
    current_text = ""
    in_code = False
    backtick_count = 0

    index = 0
    while index < len(markdown_line):
        if markdown_line[index] == "`":
            count = 1
            while index + 1 < len(markdown_line) and markdown_line[index + 1] == "`":
                count += 1
                index += 1

            if not in_code:
                if current_text:
                    yield current_text, False
                    current_text = ""
                backtick_count = count
                current_text = "`" * count
                in_code = True
            elif count == backtick_count:
                current_text += "`" * count
                yield current_text, True
                current_text = ""
                in_code = False
            else:
                current_text += "`" * count
        else:
            current_text += markdown_line[index]

        index += 1

    if current_text:
        yield current_text, False
```

</details>
