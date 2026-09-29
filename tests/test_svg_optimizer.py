"""Tests for the SvgOptimizer class."""

from pathlib import Path

from lxml import etree

import harrix_pylib as h
from harrix_pylib.svg_optimize.paths import _is_valid_command_list, _optimize_path_data, _parse_path_data
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


def test_optimize_path_preserves_compact_arc_flags() -> None:
    """Lucide/SVGO pack arc flags as ``00-.314`` / ``002.3``; do not drop them."""
    broom_head = (
        "M14.734 13.841a2 2 0 00-.314-2.42L12.58 9.58a2 2 0 00-2.421-.314"
        "l-7.657 4.461A1 1 0 002.3 15.3l6.403 6.403a1 1 0 001.571-.204z"
    )
    commands = _parse_path_data(broom_head)
    assert _is_valid_command_list(commands)
    arcs = [args for cmd, args in commands if cmd in {"A", "a"}]
    assert arcs == [
        [2.0, 2.0, 0.0, 0.0, 0.0, -0.314, -2.42],
        [2.0, 2.0, 0.0, 0.0, 0.0, -2.421, -0.314],
        [1.0, 1.0, 0.0, 0.0, 0.0, 2.3, 15.3],
        [1.0, 1.0, 0.0, 0.0, 0.0, 1.571, -0.204],
    ]
    once = _optimize_path_data(broom_head)
    twice = _optimize_path_data(once)
    assert once == twice
    assert _is_valid_command_list(_parse_path_data(once))
    assert "0 0 0" in once
    assert "2.3 15.3" in once


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
