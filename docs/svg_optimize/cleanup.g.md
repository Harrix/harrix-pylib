---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `cleanup.py`

## 🔧 Function `cleanup`

```python
def cleanup(root: etree._Element) -> None
```

Remove metadata elements and deprecated attributes from the SVG tree.

<details>
<summary>Code:</summary>

```python
def cleanup(root: etree._Element) -> None:
    for tag in REMOVE_TAGS:
        for elem in root.iter(tag):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

    for elem in root.iter():
        for attr in list(elem.attrib):
            local = attr.split("}")[-1] if "}" in attr else attr
            if local in DEPRECATED_ATTRS or any(
                attr.startswith(f"{{{prefix}") or prefix in attr.lower() for prefix in EDITOR_NS_PREFIXES
            ):
                del elem.attrib[attr]

    svg = root if tag_endswith(root.tag, "svg") else root.find(f"{{{SVG_NS}}}svg")
    if svg is not None and "version" in svg.attrib:
        del svg.attrib["version"]
```

</details>
