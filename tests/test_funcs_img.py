"""Tests for image optimization functions."""

from __future__ import annotations

from pathlib import Path

import harrix_pylib as h


def test_optimize_svg_content_removes_hidden_group() -> None:
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg__before.svg").read_text(encoding="utf-8")
    result = h.img.optimize_svg_content(before)
    assert "icon_x5F_source" not in result
    assert "rect" not in result
    assert "polygon" not in result
    assert len(result) < len(before)


def test_optimize_svg_content_structure() -> None:
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg__before.svg").read_text(encoding="utf-8")
    after = Path(current_folder / "tests/data/optimize_svg__after.svg").read_text(encoding="utf-8")
    result = h.img.optimize_svg_content(before)
    assert 'id="icon"' in result
    assert ".st1" in result
    assert ".st3" in result
    assert ".st5" in result
    assert 'style="fill:#444;opacity:.15"' in result or "opacity:.15" in result
    assert len(result) < len(before)
    assert len(result) <= len(after) * 1.4


def test_optimize_svg_file(tmp_path: Path) -> None:
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg__before.svg").read_text(encoding="utf-8")
    source = tmp_path / "icon.svg"
    target = tmp_path / "icon.min.svg"
    source.write_text(before, encoding="utf-8")
    message = h.img.optimize_svg(source, target)
    assert "successfully optimized" in message
    assert target.exists()
    assert len(target.read_text(encoding="utf-8")) < len(before)


def test_optimize_svg_github_icon() -> None:
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg_github__before.svg").read_text(encoding="utf-8")
    result = h.img.optimize_svg_content(before)
    assert "Layer_1" not in result
    assert "xmlns:xlink" not in result
    assert "<g " not in result
    assert "clip-path:url(#a)" in result
    assert "C512" in result or "C512 120.72" in result
    assert "c512 120.72" not in result
    assert "clipPath" in result
    assert len(result) < len(before)


def test_optimize_svg_folder(tmp_path: Path) -> None:
    current_folder = h.dev.get_project_root()
    before = Path(current_folder / "tests/data/optimize_svg__before.svg").read_text(encoding="utf-8")
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    (input_folder / "icon.svg").write_text(before, encoding="utf-8")
    result = h.img.optimize_svg_folder(input_folder, output_folder)
    assert "successfully optimized" in result
    assert (output_folder / "icon.svg").exists()
