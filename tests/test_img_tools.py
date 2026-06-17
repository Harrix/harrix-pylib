"""Tests for external-tool image optimization."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_pylib import img_tools


def test_scale_vf_empty_when_no_max_size() -> None:
    assert img_tools._scale_vf(None) is None


def test_scale_vf_includes_max_size() -> None:
    result = img_tools._scale_vf(800)
    assert result is not None
    assert "800" in result


def test_sequence_pattern_replaces_digits() -> None:
    frame = Path("frame-000042.png")
    pattern = img_tools._sequence_pattern(frame)
    assert pattern.name == "frame-%06d.png"


def test_optimize_image_with_tools_rejects_unknown_extension(tmp_path: Path) -> None:
    source = tmp_path / "image.bmp"
    source.write_bytes(b"fake")
    with pytest.raises(ValueError, match="not supported"):
        img_tools.optimize_image_with_tools(
            source,
            tmp_path / "out.bmp",
            project_root=tmp_path,
        )
