---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `hidden.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `remove_hidden`](#-function-remove_hidden)
- [🔧 Function `_float`](#-function-_float)
- [🔧 Function `_is_hidden`](#-function-_is_hidden)
- [🔧 Function `_is_zero_sized`](#-function-_is_zero_sized)

</details>

## 🔧 Function `remove_hidden`

```python
def remove_hidden(root: etree._Element, stylesheet: StyleSheet) -> bool
```

Remove elements that are not rendered. Returns True if any element was removed.

<details>
<summary>Code:</summary>

```python
def remove_hidden(root: etree._Element, stylesheet: StyleSheet) -> bool:
    removed = False
    for elem in list(root.iter()):
        if elem.tag not in SHAPE_TAGS and not tag_endswith(elem.tag, "g"):
            continue
        style = stylesheet.compute_style(elem)
        if _is_hidden(style, elem):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
                removed = True
                continue
        if _is_zero_sized(elem):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
                removed = True
    return removed
```

</details>

## 🔧 Function `_float`

```python
def _float(value: str | None) -> float
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _float(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return float(value.replace("px", "").strip())
    except ValueError:
        return 0.0
```

</details>

## 🔧 Function `_is_hidden`

```python
def _is_hidden(style: dict[str, str], elem: etree._Element) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _is_hidden(style: dict[str, str], elem: etree._Element) -> bool:
    display = style.get("display", elem.get("display", ""))
    if display == "none":
        return True
    opacity = style.get("opacity", elem.get("opacity", ""))
    if opacity in {"0", "0.0", "0.00"}:
        return True
    visibility = style.get("visibility", elem.get("visibility", ""))
    return visibility == "hidden"
```

</details>

## 🔧 Function `_is_zero_sized`

```python
def _is_zero_sized(elem: etree._Element) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _is_zero_sized(elem: etree._Element) -> bool:
    tag = tag_local_name(elem.tag)
    if tag == "rect":
        width = _float(elem.get("width"))
        height = _float(elem.get("height"))
        return width == 0 or height == 0
    if tag == "circle":
        return _float(elem.get("r")) == 0
    if tag == "ellipse":
        return _float(elem.get("rx")) == 0 or _float(elem.get("ry")) == 0
    if tag == "path":
        return elem.get("d", "").strip() == ""
    if tag in {"polygon", "polyline"}:
        return elem.get("points", "").strip() == ""
    return False
```

</details>
