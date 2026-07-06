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
