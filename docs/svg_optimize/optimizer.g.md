---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimizer.py`

## 🔧 Function `optimize_svg_content`

```python
def optimize_svg_content(svg_text: str) -> str
```

Optimize SVG markup to a compact form similar to SVGO preset-default.

Args:

- `svg_text` (`str`): Raw SVG content.
- `multipass` (`bool`): Run multiple optimization passes. Defaults to `True`.

Returns:

- `str`: Optimized SVG content.

<details>
<summary>Code:</summary>

```python
def optimize_svg_content(svg_text: str, *, multipass: bool = True) -> str:
    parser = etree.XMLParser(remove_comments=True, remove_pis=True, recover=True)
    root = etree.fromstring(svg_text.encode("utf-8"), parser=parser)
    cleanup(root)

    stylesheet = StyleSheet()
    stylesheet.collect(root)

    passes = MAX_MULTIPASS if multipass else 1
    for _ in range(passes):
        changed = False
        changed |= remove_hidden(root, stylesheet)
        stylesheet.inline_styles(root)
        stylesheet.minify_defs(root)
        changed |= convert_shapes(root)
        changed |= optimize_paths(root)
        changed |= optimize_structure(root)
        if not changed:
            break
        stylesheet.collect(root)

    return serialize(root)
```

</details>
