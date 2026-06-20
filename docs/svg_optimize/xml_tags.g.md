---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `xml_tags.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `tag_endswith`](#-function-tag_endswith)
- [🔧 Function `tag_local_name`](#-function-tag_local_name)

</details>

## 🔧 Function `tag_endswith`

```python
def tag_endswith(tag: str | bytes | bytearray | etree.QName, suffix: str) -> bool
```

Return whether the tag's local name ends with suffix.

<details>
<summary>Code:</summary>

```python
def tag_endswith(tag: str | bytes | bytearray | etree.QName, suffix: str) -> bool:
    return tag_local_name(tag).endswith(suffix)
```

</details>

## 🔧 Function `tag_local_name`

```python
def tag_local_name(tag: str | bytes | bytearray | etree.QName) -> str
```

Return the local part of an element tag.

<details>
<summary>Code:</summary>

```python
def tag_local_name(tag: str | bytes | bytearray | etree.QName) -> str:
    if isinstance(tag, etree.QName):
        return tag.localname
    if isinstance(tag, bytes):
        tag_str = tag.decode()
    elif isinstance(tag, bytearray):
        tag_str = tag.decode()
    else:
        tag_str = str(tag)
    if "}" in tag_str:
        return tag_str.rsplit("}", 1)[-1]
    return tag_str
```

</details>
