---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimizer.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SvgOptimizer`](#️-class-svgoptimizer)
  - [⚙️ Method `__call__`](#️-method-__call__)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `optimize`](#️-method-optimize)

</details>

## 🏛️ Class `SvgOptimizer`

```python
class SvgOptimizer
```

Optimize SVG markup to a compact form similar to SVGO preset-default.

<details>
<summary>Code:</summary>

```python
class SvgOptimizer:

    MAX_MULTIPASS: ClassVar[int] = 3

    def __call__(self, svg_text: str, *, multipass: bool | None = None) -> str:
        """Optimize SVG markup.

        Args:

        - `svg_text` (`str`): Raw SVG content.
        - `multipass` (`bool | None`): Override instance multipass setting. Defaults to `None`.

        Returns:

        - `str`: Optimized SVG content.

        """
        return self.optimize(svg_text, multipass=multipass)

    def __init__(self, *, multipass: bool = True) -> None:
        """Initialize the SvgOptimizer.

        Args:

        - `multipass` (`bool`): Run multiple optimization passes by default. Defaults to `True`.

        """
        self.multipass = multipass

    def optimize(self, svg_text: str, *, multipass: bool | None = None) -> str:
        """Optimize SVG markup to a compact form similar to SVGO preset-default.

        Args:

        - `svg_text` (`str`): Raw SVG content.
        - `multipass` (`bool | None`): Override instance multipass setting. Defaults to `None`.

        Returns:

        - `str`: Optimized SVG content.

        """
        use_multipass = self.multipass if multipass is None else multipass
        parser = etree.XMLParser(remove_comments=True, remove_pis=True, recover=True)
        root = etree.fromstring(svg_text.encode("utf-8"), parser=parser)
        _cleanup(root)

        stylesheet = _StyleSheet()
        stylesheet.collect(root)

        passes = self.MAX_MULTIPASS if use_multipass else 1
        for _ in range(passes):
            changed = False
            changed |= _remove_hidden(root, stylesheet)
            stylesheet.inline_styles(root)
            stylesheet.minify_defs(root)
            changed |= _convert_shapes(root)
            changed |= _optimize_paths(root)
            changed |= _optimize_structure(root)
            if not changed:
                break
            stylesheet.collect(root)

        return _serialize(root)
```

</details>

### ⚙️ Method `__call__`

```python
def __call__(self, svg_text: str) -> str
```

Optimize SVG markup.

Args:

- `svg_text` (`str`): Raw SVG content.
- `multipass` (`bool | None`): Override instance multipass setting. Defaults to `None`.

Returns:

- `str`: Optimized SVG content.

<details>
<summary>Code:</summary>

```python
def __call__(self, svg_text: str, *, multipass: bool | None = None) -> str:
        return self.optimize(svg_text, multipass=multipass)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize the SvgOptimizer.

Args:

- `multipass` (`bool`): Run multiple optimization passes by default. Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, multipass: bool = True) -> None:
        self.multipass = multipass
```

</details>

### ⚙️ Method `optimize`

```python
def optimize(self, svg_text: str) -> str
```

Optimize SVG markup to a compact form similar to SVGO preset-default.

Args:

- `svg_text` (`str`): Raw SVG content.
- `multipass` (`bool | None`): Override instance multipass setting. Defaults to `None`.

Returns:

- `str`: Optimized SVG content.

<details>
<summary>Code:</summary>

```python
def optimize(self, svg_text: str, *, multipass: bool | None = None) -> str:
        use_multipass = self.multipass if multipass is None else multipass
        parser = etree.XMLParser(remove_comments=True, remove_pis=True, recover=True)
        root = etree.fromstring(svg_text.encode("utf-8"), parser=parser)
        _cleanup(root)

        stylesheet = _StyleSheet()
        stylesheet.collect(root)

        passes = self.MAX_MULTIPASS if use_multipass else 1
        for _ in range(passes):
            changed = False
            changed |= _remove_hidden(root, stylesheet)
            stylesheet.inline_styles(root)
            stylesheet.minify_defs(root)
            changed |= _convert_shapes(root)
            changed |= _optimize_paths(root)
            changed |= _optimize_structure(root)
            if not changed:
                break
            stylesheet.collect(root)

        return _serialize(root)
```

</details>
