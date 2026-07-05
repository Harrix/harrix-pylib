"""Tests for the SvgOptimizer class."""

from pathlib import Path

import harrix_pylib as h


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
