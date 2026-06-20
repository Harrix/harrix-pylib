---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `front_matter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `collapse_extra_blank_lines`](#-function-collapse_extra_blank_lines)
- [🔧 Function `compact_front_matter`](#-function-compact_front_matter)
- [🔧 Function `join_front_matter`](#-function-join_front_matter)
- [🔧 Function `split_front_matter`](#-function-split_front_matter)

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
