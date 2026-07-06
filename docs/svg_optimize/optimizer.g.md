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
  - [⚙️ Method `optimize_file`](#️-method-optimize_file)
  - [⚙️ Method `optimize_folder`](#️-method-optimize_folder)

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

    def optimize_file(self, filename: Path | str, output_filename: Path | str | None = None) -> str:
        """Optimize an SVG file and write the result.

        Args:

        - `filename` (`Path | str`): Source SVG file path.
        - `output_filename` (`Path | str | None`): Destination path. If omitted, overwrites source.

        Returns:

        - `str`: Status message.

        """
        source = Path(filename)
        target = Path(output_filename) if output_filename is not None else source
        content = source.read_text(encoding="utf-8")
        optimized = self.optimize(content)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(optimized, encoding="utf-8")
        return f"✅ File {source.name} successfully optimized."

    def optimize_folder(self, input_folder: Path | str, output_folder: Path | str) -> str:
        """Optimize all SVG files in a folder.

        Args:

        - `input_folder` (`Path | str`): Folder with source SVG files.
        - `output_folder` (`Path | str`): Folder for optimized SVG files.

        Returns:

        - `str`: Newline-separated status messages.

        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        for file in sorted(input_path.iterdir()):
            if not file.is_file() or file.suffix.lower() != ".svg":
                continue
            lines.append(self.optimize_file(file, output_path / file.name))
        if not lines:
            lines.append("🔵 No SVG files found.")
        return "\n".join(lines)
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

### ⚙️ Method `optimize_file`

```python
def optimize_file(self, filename: Path | str, output_filename: Path | str | None = None) -> str
```

Optimize an SVG file and write the result.

Args:

- `filename` (`Path | str`): Source SVG file path.
- `output_filename` (`Path | str | None`): Destination path. If omitted, overwrites source.

Returns:

- `str`: Status message.

<details>
<summary>Code:</summary>

```python
def optimize_file(self, filename: Path | str, output_filename: Path | str | None = None) -> str:
        source = Path(filename)
        target = Path(output_filename) if output_filename is not None else source
        content = source.read_text(encoding="utf-8")
        optimized = self.optimize(content)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(optimized, encoding="utf-8")
        return f"✅ File {source.name} successfully optimized."
```

</details>

### ⚙️ Method `optimize_folder`

```python
def optimize_folder(self, input_folder: Path | str, output_folder: Path | str) -> str
```

Optimize all SVG files in a folder.

Args:

- `input_folder` (`Path | str`): Folder with source SVG files.
- `output_folder` (`Path | str`): Folder for optimized SVG files.

Returns:

- `str`: Newline-separated status messages.

<details>
<summary>Code:</summary>

```python
def optimize_folder(self, input_folder: Path | str, output_folder: Path | str) -> str:
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        for file in sorted(input_path.iterdir()):
            if not file.is_file() or file.suffix.lower() != ".svg":
                continue
            lines.append(self.optimize_file(file, output_path / file.name))
        if not lines:
            lines.append("🔵 No SVG files found.")
        return "\n".join(lines)
```

</details>
