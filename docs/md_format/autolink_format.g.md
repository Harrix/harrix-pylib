---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `autolink_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `extract_angle_autolinks`](#-function-extract_angle_autolinks)
- [🔧 Function `restore_angle_autolinks`](#-function-restore_angle_autolinks)

</details>

## 🔧 Function `extract_angle_autolinks`

```python
def extract_angle_autolinks(body: str) -> tuple[str, list[str]]
```

Replace angle-bracket autolinks with placeholders before parsing.

<details>
<summary>Code:</summary>

```python
def extract_angle_autolinks(body: str) -> tuple[str, list[str]]:
    autolinks: list[str] = []

    def replace(match: re.Match[str]) -> str:
        autolinks.append(match.group(0))
        return f"{PLACEHOLDER_PREFIX}{len(autolinks) - 1}"

    return _ANGLE_AUTOLINK_RE.sub(replace, body), autolinks
```

</details>

## 🔧 Function `restore_angle_autolinks`

```python
def restore_angle_autolinks(text: str, autolinks: list[str]) -> str
```

Restore angle-bracket autolinks after rendering.

<details>
<summary>Code:</summary>

```python
def restore_angle_autolinks(text: str, autolinks: list[str]) -> str:
    if not autolinks:
        return text

    def replace(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if 0 <= index < len(autolinks):
            return autolinks[index]
        return match.group(0)

    return _PLACEHOLDER_RE.sub(replace, text)
```

</details>
