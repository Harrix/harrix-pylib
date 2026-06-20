---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `styles.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `StyleSheet`](#%EF%B8%8F-class-stylesheet)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `collect`](#%EF%B8%8F-method-collect)
  - [⚙️ Method `compute_style`](#%EF%B8%8F-method-compute_style)
  - [⚙️ Method `inline_styles`](#%EF%B8%8F-method-inline_styles)
  - [⚙️ Method `minify_defs`](#%EF%B8%8F-method-minify_defs)
  - [⚙️ Method `_parse_inline`](#%EF%B8%8F-method-_parse_inline)
- [🔧 Function `_format_style`](#-function-_format_style)

</details>

## 🏛️ Class `StyleSheet`

```python
class StyleSheet
```

Collected CSS class rules from SVG <style> elements.

<details>
<summary>Code:</summary>

```python
class StyleSheet:

    def __init__(self) -> None:
        """Initialize an empty stylesheet."""
        self.rules: dict[str, dict[str, str]] = defaultdict(dict)
        self.style_elements: list[etree._Element] = []

    def collect(self, root: etree._Element) -> None:
        """Parse class rules from all <style> elements."""
        self.rules.clear()
        self.style_elements.clear()
        for style_elem in root.iter(f"{{{SVG_NS}}}style"):
            self.style_elements.append(style_elem)
            css_text = "".join(style_elem.itertext())
            for match in RULE_RE.finditer(css_text):
                class_name = match.group(1)
                for decl_match in DECL_RE.finditer(match.group(2)):
                    prop = decl_match.group(1).strip()
                    value = decl_match.group(2).strip()
                    self.rules[class_name][prop] = value

    def compute_style(self, elem: etree._Element) -> dict[str, str]:
        """Compute effective style for an element from class and inline style."""
        result: dict[str, str] = {}
        class_attr = elem.get("class", "")
        for class_name in class_attr.split():
            result.update(self.rules.get(class_name, {}))
        inline = elem.get("style", "")
        if inline:
            for decl_match in DECL_RE.finditer(inline):
                prop = decl_match.group(1).strip()
                value = decl_match.group(2).strip()
                result[prop] = value
        return result

    def inline_styles(self, root: etree._Element) -> None:
        """Inline class-based styles into element style attributes."""
        class_usage: dict[str, int] = {}
        for elem in root.iter():
            class_attr = elem.get("class")
            if class_attr:
                for class_name in class_attr.split():
                    class_usage[class_name] = class_usage.get(class_name, 0) + 1

        for elem in root.iter():
            if tag_endswith(elem.tag, "style"):
                continue
            class_attr = elem.get("class")
            if not class_attr:
                continue
            classes = class_attr.split()
            remaining_classes: list[str] = []
            inline_props = dict(self._parse_inline(elem.get("style", "")))
            for class_name in classes:
                class_props = self.rules.get(class_name, {})
                if class_props and class_usage.get(class_name, 0) == 1:
                    for prop, value in class_props.items():
                        if prop not in inline_props:
                            inline_props[prop] = value
                else:
                    remaining_classes.append(class_name)
            if inline_props:
                elem.set("style", _format_style(inline_props))
            if remaining_classes:
                elem.set("class", " ".join(remaining_classes))
            elif "class" in elem.attrib:
                del elem.attrib["class"]

    def minify_defs(self, root: etree._Element) -> None:
        """Keep only class rules still referenced by elements."""
        used_classes: set[str] = set()
        for elem in root.iter():
            class_attr = elem.get("class")
            if class_attr:
                used_classes.update(class_attr.split())

        for style_elem in self.style_elements:
            css_parts: list[str] = []
            for class_name in sorted(used_classes):
                props = self.rules.get(class_name)
                if not props:
                    continue
                decls = ";".join(f"{prop}:{value}" for prop, value in props.items())
                css_parts.append(f".{class_name}{{{decls}}}")
            if css_parts:
                style_elem.text = "".join(css_parts)
                if "type" in style_elem.attrib:
                    del style_elem.attrib["type"]
            else:
                parent = style_elem.getparent()
                if parent is not None:
                    parent.remove(style_elem)

        empty_defs = [d for d in root.iter(f"{{{SVG_NS}}}defs") if len(d) == 0 and not (d.text and d.text.strip())]
        for defs in empty_defs:
            parent = defs.getparent()
            if parent is not None:
                parent.remove(defs)

    @staticmethod
    def _parse_inline(style: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for decl_match in DECL_RE.finditer(style):
            result[decl_match.group(1).strip()] = decl_match.group(2).strip()
        return result
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize an empty stylesheet.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        self.rules: dict[str, dict[str, str]] = defaultdict(dict)
        self.style_elements: list[etree._Element] = []
```

</details>

### ⚙️ Method `collect`

```python
def collect(self, root: etree._Element) -> None
```

Parse class rules from all <style> elements.

<details>
<summary>Code:</summary>

```python
def collect(self, root: etree._Element) -> None:
        self.rules.clear()
        self.style_elements.clear()
        for style_elem in root.iter(f"{{{SVG_NS}}}style"):
            self.style_elements.append(style_elem)
            css_text = "".join(style_elem.itertext())
            for match in RULE_RE.finditer(css_text):
                class_name = match.group(1)
                for decl_match in DECL_RE.finditer(match.group(2)):
                    prop = decl_match.group(1).strip()
                    value = decl_match.group(2).strip()
                    self.rules[class_name][prop] = value
```

</details>

### ⚙️ Method `compute_style`

```python
def compute_style(self, elem: etree._Element) -> dict[str, str]
```

Compute effective style for an element from class and inline style.

<details>
<summary>Code:</summary>

```python
def compute_style(self, elem: etree._Element) -> dict[str, str]:
        result: dict[str, str] = {}
        class_attr = elem.get("class", "")
        for class_name in class_attr.split():
            result.update(self.rules.get(class_name, {}))
        inline = elem.get("style", "")
        if inline:
            for decl_match in DECL_RE.finditer(inline):
                prop = decl_match.group(1).strip()
                value = decl_match.group(2).strip()
                result[prop] = value
        return result
```

</details>

### ⚙️ Method `inline_styles`

```python
def inline_styles(self, root: etree._Element) -> None
```

Inline class-based styles into element style attributes.

<details>
<summary>Code:</summary>

```python
def inline_styles(self, root: etree._Element) -> None:
        class_usage: dict[str, int] = {}
        for elem in root.iter():
            class_attr = elem.get("class")
            if class_attr:
                for class_name in class_attr.split():
                    class_usage[class_name] = class_usage.get(class_name, 0) + 1

        for elem in root.iter():
            if tag_endswith(elem.tag, "style"):
                continue
            class_attr = elem.get("class")
            if not class_attr:
                continue
            classes = class_attr.split()
            remaining_classes: list[str] = []
            inline_props = dict(self._parse_inline(elem.get("style", "")))
            for class_name in classes:
                class_props = self.rules.get(class_name, {})
                if class_props and class_usage.get(class_name, 0) == 1:
                    for prop, value in class_props.items():
                        if prop not in inline_props:
                            inline_props[prop] = value
                else:
                    remaining_classes.append(class_name)
            if inline_props:
                elem.set("style", _format_style(inline_props))
            if remaining_classes:
                elem.set("class", " ".join(remaining_classes))
            elif "class" in elem.attrib:
                del elem.attrib["class"]
```

</details>

### ⚙️ Method `minify_defs`

```python
def minify_defs(self, root: etree._Element) -> None
```

Keep only class rules still referenced by elements.

<details>
<summary>Code:</summary>

```python
def minify_defs(self, root: etree._Element) -> None:
        used_classes: set[str] = set()
        for elem in root.iter():
            class_attr = elem.get("class")
            if class_attr:
                used_classes.update(class_attr.split())

        for style_elem in self.style_elements:
            css_parts: list[str] = []
            for class_name in sorted(used_classes):
                props = self.rules.get(class_name)
                if not props:
                    continue
                decls = ";".join(f"{prop}:{value}" for prop, value in props.items())
                css_parts.append(f".{class_name}{{{decls}}}")
            if css_parts:
                style_elem.text = "".join(css_parts)
                if "type" in style_elem.attrib:
                    del style_elem.attrib["type"]
            else:
                parent = style_elem.getparent()
                if parent is not None:
                    parent.remove(style_elem)

        empty_defs = [d for d in root.iter(f"{{{SVG_NS}}}defs") if len(d) == 0 and not (d.text and d.text.strip())]
        for defs in empty_defs:
            parent = defs.getparent()
            if parent is not None:
                parent.remove(defs)
```

</details>

### ⚙️ Method `_parse_inline`

```python
def _parse_inline(style: str) -> dict[str, str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _parse_inline(style: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for decl_match in DECL_RE.finditer(style):
            result[decl_match.group(1).strip()] = decl_match.group(2).strip()
        return result
```

</details>

## 🔧 Function `_format_style`

```python
def _format_style(props: dict[str, str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_style(props: dict[str, str]) -> str:
    return ";".join(f"{prop}:{value}" for prop, value in props.items())
```

</details>
