"""SVG optimization pipeline."""

from __future__ import annotations

from lxml import etree

from harrix_pylib.svg_optimize.cleanup import cleanup
from harrix_pylib.svg_optimize.hidden import remove_hidden
from harrix_pylib.svg_optimize.paths import optimize_paths
from harrix_pylib.svg_optimize.serialize import serialize
from harrix_pylib.svg_optimize.shapes import convert_shapes
from harrix_pylib.svg_optimize.structure import optimize_structure
from harrix_pylib.svg_optimize.styles import StyleSheet

MAX_MULTIPASS = 3


def optimize_svg_content(svg_text: str, *, multipass: bool = True) -> str:
    """Optimize SVG markup to a compact form similar to SVGO preset-default.

    Args:

    - `svg_text` (`str`): Raw SVG content.
    - `multipass` (`bool`): Run multiple optimization passes. Defaults to `True`.

    Returns:

    - `str`: Optimized SVG content.

    """
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
