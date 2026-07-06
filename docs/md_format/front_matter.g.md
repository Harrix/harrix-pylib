---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `front_matter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TomlBlock`](#️-class-tomlblock)
- [🏛️ Class `YamlBlock`](#️-class-yamlblock)
- [🔧 Function `collapse_extra_blank_lines`](#-function-collapse_extra_blank_lines)
- [🔧 Function `compact_front_matter`](#-function-compact_front_matter)
- [🔧 Function `extract_toml_blocks`](#-function-extract_toml_blocks)
- [🔧 Function `extract_yaml_blocks`](#-function-extract_yaml_blocks)
- [🔧 Function `join_front_matter`](#-function-join_front_matter)
- [🔧 Function `prepend_markdown_header`](#-function-prepend_markdown_header)
- [🔧 Function `restore_toml_blocks`](#-function-restore_toml_blocks)
- [🔧 Function `restore_yaml_blocks`](#-function-restore_yaml_blocks)
- [🔧 Function `split_front_matter`](#-function-split_front_matter)
- [🔧 Function `trim_trailing_blank_lines`](#-function-trim_trailing_blank_lines)

</details>

## 🏛️ Class `TomlBlock`

```python
class TomlBlock
```

Stored TOML front matter style block from the Markdown body.

<details>
<summary>Code:</summary>

```python
class TomlBlock:

    index: int
    lines: list[str]
```

</details>

## 🏛️ Class `YamlBlock`

```python
class YamlBlock
```

Stored YAML block from the Markdown body.

<details>
<summary>Code:</summary>

```python
class YamlBlock:

    index: int
    lines: list[str]
```

</details>

## 🔧 Function `collapse_extra_blank_lines`

```python
def collapse_extra_blank_lines(text: str) -> str
```

Collapse consecutive blank lines to a single blank line.

<details>
<summary>Code:</summary>

```python
def collapse_extra_blank_lines(text: str) -> str:
    lines = text.split("\n")
    collapsed: list[str] = []
    for line in lines:
        if line == "":
            if collapsed and collapsed[-1] != "":
                collapsed.append("")
            continue
        collapsed.append(line)
    return "\n".join(collapsed)
```

</details>

## 🔧 Function `compact_front_matter`

```python
def compact_front_matter(front_matter: str) -> str
```

Remove blank lines inside YAML front matter while keeping delimiters.

<details>
<summary>Code:</summary>

```python
def compact_front_matter(front_matter: str) -> str:
    parts = front_matter.split("---", 2)
    if len(parts) < _MIN_FRONT_MATTER_PARTS:
        return front_matter
    yaml_lines = [line for line in parts[1].splitlines() if line.strip()]
    if not yaml_lines:
        return front_matter
    yaml_body = "\n".join(yaml_lines)
    return f"---\n{yaml_body}\n---"
```

</details>

## 🔧 Function `extract_toml_blocks`

```python
def extract_toml_blocks(body: str) -> tuple[str, list[TomlBlock]]
```

Replace standalone TOML blocks in the Markdown body with placeholders.

<details>
<summary>Code:</summary>

```python
def extract_toml_blocks(body: str) -> tuple[str, list[TomlBlock]]:
    return _extract_delimited_blocks(body, delimiter="+++", prefix=_TOML_BLOCK_PREFIX, block_class=TomlBlock)
```

</details>

## 🔧 Function `extract_yaml_blocks`

```python
def extract_yaml_blocks(body: str) -> tuple[str, list[YamlBlock]]
```

Replace standalone YAML blocks in the Markdown body with placeholders.

<details>
<summary>Code:</summary>

```python
def extract_yaml_blocks(body: str) -> tuple[str, list[YamlBlock]]:
    return _extract_delimited_blocks(body, delimiter="---", prefix=_YAML_BLOCK_PREFIX, block_class=YamlBlock)
```

</details>

## 🔧 Function `join_front_matter`

```python
def join_front_matter(front_matter: str, body: str) -> str
```

Join front matter and formatted body.

<details>
<summary>Code:</summary>

```python
def join_front_matter(front_matter: str, body: str) -> str:
    if not front_matter:
        return body
    body = body.lstrip("\n")
    if body:
        return f"{front_matter.rstrip()}\n\n{body}"
    return f"{front_matter.rstrip()}\n"
```

</details>

## 🔧 Function `prepend_markdown_header`

```python
def prepend_markdown_header(header: str, markdown_text: str) -> str
```

Prepend YAML or Markdown prefix without duplicating existing front matter.

<details>
<summary>Code:</summary>

```python
def prepend_markdown_header(header: str, markdown_text: str) -> str:
    _, body = split_front_matter(markdown_text)
    header = header.rstrip("\n")
    if not header:
        return body or markdown_text
    if not body:
        return f"{header}\n"
    return f"{header}\n\n{body}"
```

</details>

## 🔧 Function `restore_toml_blocks`

```python
def restore_toml_blocks(text: str, blocks: list[TomlBlock]) -> str
```

Restore TOML body blocks.

<details>
<summary>Code:</summary>

```python
def restore_toml_blocks(text: str, blocks: list[TomlBlock]) -> str:
    return _restore_delimited_blocks(
        text,
        blocks,
        prefix=_TOML_BLOCK_PREFIX,
        pattern=_TOML_BLOCK_RE,
        formatter=lambda block: "\n".join(line.rstrip() for line in block.lines),
    )
```

</details>

## 🔧 Function `restore_yaml_blocks`

```python
def restore_yaml_blocks(text: str, blocks: list[YamlBlock]) -> str
```

Restore YAML body blocks.

<details>
<summary>Code:</summary>

```python
def restore_yaml_blocks(text: str, blocks: list[YamlBlock]) -> str:
    return _restore_delimited_blocks(
        text, blocks, prefix=_YAML_BLOCK_PREFIX, pattern=_YAML_BLOCK_RE, formatter=_format_yaml_block
    )
```

</details>

## 🔧 Function `split_front_matter`

```python
def split_front_matter(markdown_text: str) -> tuple[str, str]
```

Split YAML front matter from Markdown body.

Returns front matter including `---` delimiters and the remaining body.

<details>
<summary>Code:</summary>

```python
def split_front_matter(markdown_text: str) -> tuple[str, str]:
    markdown_text = markdown_text.lstrip("\ufeff")
    if not markdown_text.startswith("---"):
        return "", markdown_text
    parts = markdown_text.split("---", 2)
    if len(parts) < _MIN_FRONT_MATTER_PARTS:
        return "", markdown_text
    return f"---{parts[1]}---", parts[2].lstrip()
```

</details>

## 🔧 Function `trim_trailing_blank_lines`

```python
def trim_trailing_blank_lines(text: str) -> str
```

Remove trailing blank lines while keeping a single final newline.

<details>
<summary>Code:</summary>

```python
def trim_trailing_blank_lines(text: str) -> str:
    lines = text.split("\n")
    has_trailing_newline = text.endswith("\n")
    if has_trailing_newline and lines:
        lines.pop()
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return "\n"
    return "\n".join(lines) + "\n"
```

</details>
