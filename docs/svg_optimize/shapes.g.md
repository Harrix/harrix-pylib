---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `shapes.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `convert_shapes`](#-function-convert_shapes)
- [🔧 Function `_circle_to_path`](#-function-_circle_to_path)
- [🔧 Function `_ellipse_to_path`](#-function-_ellipse_to_path)
- [🔧 Function `_line_to_path`](#-function-_line_to_path)
- [🔧 Function `_num`](#-function-_num)
- [🔧 Function `_parse_points`](#-function-_parse_points)
- [🔧 Function `_polygon_to_path`](#-function-_polygon_to_path)
- [🔧 Function `_polyline_to_path`](#-function-_polyline_to_path)
- [🔧 Function `_rect_to_path`](#-function-_rect_to_path)
- [🔧 Function `_shape_to_path`](#-function-_shape_to_path)

</details>

## 🔧 Function `convert_shapes`

```python
def convert_shapes(root: etree._Element) -> bool
```

Convert basic shapes to paths. Returns True if any conversion happened.

<details>
<summary>Code:</summary>

```python
def convert_shapes(root: etree._Element) -> bool:
    changed = False
    for elem in list(root.iter()):
        if elem.tag not in CONVERTIBLE:
            continue
        path_d = _shape_to_path(elem)
        if path_d is None:
            continue
        elem.tag = f"{{{SVG_NS}}}path"
        elem.set("d", path_d)
        for attr in ("x", "y", "width", "height", "rx", "ry", "cx", "cy", "r", "points", "x1", "y1", "x2", "y2"):
            if attr in elem.attrib:
                del elem.attrib[attr]
        changed = True
    return changed
```

</details>

## 🔧 Function `_circle_to_path`

```python
def _circle_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _circle_to_path(elem: etree._Element) -> str | None:
    cx = _num(elem.get("cx", "0"))
    cy = _num(elem.get("cy", "0"))
    r = _num(elem.get("r", "0"))
    if r == 0:
        return None
    return format_path_data(
        [
            ("M", [cx - r, cy]),
            ("A", [r, r, 0, 1, 0, cx + r, cy]),
            ("A", [r, r, 0, 1, 0, cx - r, cy]),
            ("Z", []),
        ]
    )
```

</details>

## 🔧 Function `_ellipse_to_path`

```python
def _ellipse_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _ellipse_to_path(elem: etree._Element) -> str | None:
    cx = _num(elem.get("cx", "0"))
    cy = _num(elem.get("cy", "0"))
    rx = _num(elem.get("rx", "0"))
    ry = _num(elem.get("ry", "0"))
    if rx == 0 or ry == 0:
        return None
    return format_path_data(
        [
            ("M", [cx - rx, cy]),
            ("A", [rx, ry, 0, 1, 0, cx + rx, cy]),
            ("A", [rx, ry, 0, 1, 0, cx - rx, cy]),
            ("Z", []),
        ]
    )
```

</details>

## 🔧 Function `_line_to_path`

```python
def _line_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _line_to_path(elem: etree._Element) -> str | None:
    x1 = _num(elem.get("x1", "0"))
    y1 = _num(elem.get("y1", "0"))
    x2 = _num(elem.get("x2", "0"))
    y2 = _num(elem.get("y2", "0"))
    return format_path_data([("M", [x1, y1]), ("L", [x2, y2])])
```

</details>

## 🔧 Function `_num`

```python
def _num(value: str) -> float
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _num(value: str) -> float:
    return float(value.replace("px", "").strip())
```

</details>

## 🔧 Function `_parse_points`

```python
def _parse_points(points_str: str) -> list[tuple[float, float]]
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _parse_points(points_str: str) -> list[tuple[float, float]]:
    numbers = [_num(part) for part in points_str.replace(",", " ").split() if part.strip()]
    return [(numbers[i], numbers[i + 1]) for i in range(0, len(numbers) - 1, 2)]
```

</details>

## 🔧 Function `_polygon_to_path`

```python
def _polygon_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _polygon_to_path(elem: etree._Element) -> str | None:
    points = _parse_points(elem.get("points", ""))
    if len(points) < _MIN_POINTS:
        return None
    commands: list[tuple[str, list[float]]] = [("M", list(points[0]))]
    commands.extend(("L", list(point)) for point in points[1:])
    commands.append(("Z", []))
    return format_path_data(commands)
```

</details>

## 🔧 Function `_polyline_to_path`

```python
def _polyline_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _polyline_to_path(elem: etree._Element) -> str | None:
    points = _parse_points(elem.get("points", ""))
    if len(points) < _MIN_POINTS:
        return None
    commands: list[tuple[str, list[float]]] = [("M", list(points[0]))]
    commands.extend(("L", list(point)) for point in points[1:])
    return format_path_data(commands)
```

</details>

## 🔧 Function `_rect_to_path`

```python
def _rect_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _rect_to_path(elem: etree._Element) -> str | None:
    if elem.get("rx") or elem.get("ry"):
        return None
    x = _num(elem.get("x", "0"))
    y = _num(elem.get("y", "0"))
    width = _num(elem.get("width") or "0")
    height = _num(elem.get("height") or "0")
    if width == 0 or height == 0:
        return None
    return format_path_data(
        [
            ("M", [x, y]),
            ("H", [x + width]),
            ("V", [y + height]),
            ("H", [x]),
            ("Z", []),
        ]
    )
```

</details>

## 🔧 Function `_shape_to_path`

```python
def _shape_to_path(elem: etree._Element) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _shape_to_path(elem: etree._Element) -> str | None:
    tag = tag_local_name(elem.tag)
    if tag == "rect":
        return _rect_to_path(elem)
    if tag == "polygon":
        return _polygon_to_path(elem)
    if tag == "polyline":
        return _polyline_to_path(elem)
    if tag == "line":
        return _line_to_path(elem)
    if tag == "circle":
        return _circle_to_path(elem)
    if tag == "ellipse":
        return _ellipse_to_path(elem)
    return None
```

</details>
