"""SVG optimization pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from lxml import etree

from harrix_pylib.svg_optimize.cleanup import _cleanup
from harrix_pylib.svg_optimize.hidden import _remove_hidden
from harrix_pylib.svg_optimize.paths import _optimize_paths
from harrix_pylib.svg_optimize.serialize import _serialize
from harrix_pylib.svg_optimize.shapes import _convert_shapes
from harrix_pylib.svg_optimize.structure import _optimize_structure
from harrix_pylib.svg_optimize.styles import _StyleSheet


class SvgOptimizer:
    """Optimize SVG markup to a compact form similar to SVGO preset-default."""

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
