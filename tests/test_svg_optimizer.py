"""Tests for the SvgOptimizer class."""

from pathlib import Path

from lxml import etree

import harrix_pylib as h
from harrix_pylib.svg_optimize.styles import _StyleSheet


def test_svg_optimizer() -> None:
    """Test SvgOptimizer for callable interface and optimization results."""
    optimizer = h.svg_opt.SvgOptimizer()
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg__before.svg").read_text(encoding="utf-8")
    after = Path(current_folder / "tests/data/optimize_svg__after.svg").read_text(encoding="utf-8")

    result = optimizer(before)
    assert "icon_x5F_source" not in result
    assert "rect" not in result
    assert "polygon" not in result
    assert 'id="icon"' in result
    assert len(result) < len(before)
    assert len(result) <= len(after) * 1.4

    single_pass = h.svg_opt.SvgOptimizer(multipass=False).optimize(before)
    assert len(single_pass) < len(before)

    assert optimizer.optimize(before, multipass=False) == single_pass


def test_svg_optimizer_optimize_file(tmp_path: Path) -> None:
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg__before.svg").read_text(encoding="utf-8")
    source = tmp_path / "icon.svg"
    source.write_text(before, encoding="utf-8")
    message = h.svg_opt.SvgOptimizer().optimize_file(source)
    assert "successfully optimized" in message
    assert len(source.read_text(encoding="utf-8")) < len(before)


def test_stylesheet_parses_grouped_class_selectors() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<style>.st4,.st5{opacity:.15;fill:#444;enable-background:new}.st5{opacity:.3}</style>"
        "</svg>"
    )
    sheet = _StyleSheet()
    sheet.collect(etree.fromstring(svg.encode("utf-8")))
    assert sheet.rules["st4"] == {"opacity": ".15", "fill": "#444", "enable-background": "new"}
    assert sheet.rules["st5"] == {"opacity": ".3", "fill": "#444", "enable-background": "new"}

    spaced = '<svg xmlns="http://www.w3.org/2000/svg"><style>.st1, .st2 { opacity: .15; fill: #444 }</style></svg>'
    sheet.collect(etree.fromstring(spaced.encode("utf-8")))
    assert sheet.rules["st1"] == {"opacity": ".15", "fill": "#444"}
    assert sheet.rules["st2"] == {"opacity": ".15", "fill": "#444"}


def test_optimize_svg_keeps_grouped_shadow_class() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
        "<style>.st4,.st5{opacity:.15;fill:#444}.st5{opacity:.3}</style>"
        '<path class="st4" d="M0 0h4v4H0z"/>'
        '<path class="st4" d="M0 5h4v4H0z"/>'
        '<path class="st5" d="M5 0h4v4H5z"/>'
        '<path class="st5" d="M5 5h4v4H5z"/>'
        "</svg>"
    )
    result = h.svg_opt.SvgOptimizer().optimize(svg)
    assert ".st4{opacity:.15;fill:#444}" in result
    assert ".st5{opacity:.3;fill:#444}" in result
    assert 'class="st4"' in result
    assert 'class="st5"' in result
