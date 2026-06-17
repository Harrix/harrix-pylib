"""Functions for working with images."""

from __future__ import annotations

from pathlib import Path

from harrix_pylib import img_tools
from harrix_pylib.svg_optimize.optimizer import optimize_svg_content as _optimize_svg_content

EXE_RASTER_EXTENSIONS = img_tools.EXE_RASTER_EXTENSIONS


def optimize_image_with_tools(
    filename: Path | str,
    output_filename: Path | str,
    *,
    project_root: Path | str,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    """Optimize GIF, MP4, or AVIF using ffmpeg, avifenc, and avifdec.

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

    """
    return img_tools.optimize_image_with_tools(
        filename,
        output_filename,
        project_root=project_root,
        quality=quality,
        max_size=max_size,
    )


def optimize_svg(filename: Path | str, output_filename: Path | str | None = None) -> str:
    """Optimize an SVG file and write the result.

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

    """
    source = Path(filename)
    target = Path(output_filename) if output_filename is not None else source
    content = source.read_text(encoding="utf-8")
    optimized = _optimize_svg_content(content)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(optimized, encoding="utf-8")
    return f"✅ File {source.name} successfully optimized."


def optimize_svg_content(svg_text: str, *, multipass: bool = True) -> str:
    """Optimize SVG markup to a compact form similar to SVGO preset-default.

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

    """
    return _optimize_svg_content(svg_text, multipass=multipass)


def optimize_svg_folder(input_folder: Path | str, output_folder: Path | str) -> str:
    """Optimize all SVG files in a folder.

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

    """
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
