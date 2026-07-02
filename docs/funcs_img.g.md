---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `funcs_img.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `optimize_image_with_tools`](#-function-optimize_image_with_tools)
- [🔧 Function `optimize_svg`](#-function-optimize_svg)
- [🔧 Function `optimize_svg_content`](#-function-optimize_svg_content)
- [🔧 Function `optimize_svg_folder`](#-function-optimize_svg_folder)

</details>

## 🔧 Function `optimize_image_with_tools`

```python
def optimize_image_with_tools(filename: Path | str, output_filename: Path | str) -> str
```

Optimize GIF, MP4, or AVIF using ffmpeg, avifenc, and avifdec.

Args:

- `filename` (`Path | str`): Source image path.
- `output_filename` (`Path | str`): Destination path.
- `project_root` (`Path | str`): Folder containing external tool executables.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.

Returns:

- `str`: Status message.

Example:

```python
import harrix_pylib as h

message = h.img.optimize_image_with_tools(
    "video.gif",
    "video.avif",
    project_root=".",
)
```

<details>
<summary>Code:</summary>

```python
def optimize_image_with_tools(
    filename: Path | str,
    output_filename: Path | str,
    *,
    project_root: Path | str,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    return img_tools.optimize_image_with_tools(
        filename,
        output_filename,
        project_root=project_root,
        quality=quality,
        max_size=max_size,
    )
```

</details>

## 🔧 Function `optimize_svg`

```python
def optimize_svg(filename: Path | str, output_filename: Path | str | None = None) -> str
```

Optimize an SVG file and write the result.

Args:

- `filename` (`Path | str`): Source SVG file path.
- `output_filename` (`Path | str | None`): Destination path. If omitted, overwrites source.

Returns:

- `str`: Status message.

Example:

```python
import harrix_pylib as h

message = h.img.optimize_svg("icon.svg", "icon.min.svg")
```

<details>
<summary>Code:</summary>

```python
def optimize_svg(filename: Path | str, output_filename: Path | str | None = None) -> str:
    source = Path(filename)
    target = Path(output_filename) if output_filename is not None else source
    content = source.read_text(encoding="utf-8")
    optimized = _optimize_svg_content(content)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(optimized, encoding="utf-8")
    return f"✅ File {source.name} successfully optimized."
```

</details>

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

Example:

```python
import harrix_pylib as h

optimized = h.img.optimize_svg_content(svg_text)
```

<details>
<summary>Code:</summary>

```python
def optimize_svg_content(svg_text: str, *, multipass: bool = True) -> str:
    return _optimize_svg_content(svg_text, multipass=multipass)
```

</details>

## 🔧 Function `optimize_svg_folder`

```python
def optimize_svg_folder(input_folder: Path | str, output_folder: Path | str) -> str
```

Optimize all SVG files in a folder.

Args:

- `input_folder` (`Path | str`): Folder with source SVG files.
- `output_folder` (`Path | str`): Folder for optimized SVG files.

Returns:

- `str`: Newline-separated status messages.

Example:

```python
import harrix_pylib as h

result = h.img.optimize_svg_folder("temp/images", "temp/optimized_images")
```

<details>
<summary>Code:</summary>

```python
def optimize_svg_folder(input_folder: Path | str, output_folder: Path | str) -> str:
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for file in sorted(input_path.iterdir()):
        if not file.is_file() or file.suffix.lower() != ".svg":
            continue
        lines.append(optimize_svg(file, output_path / file.name))
    if not lines:
        lines.append("🔵 No SVG files found.")
    return "\n".join(lines)
```

</details>
