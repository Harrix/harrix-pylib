"""Tests for external-tool image optimization."""

from __future__ import annotations

import subprocess
import sys
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


def test_hidden_subprocess_kwargs_hides_console_on_windows() -> None:
    kwargs = img_tools._hidden_subprocess_kwargs()
    if sys.platform != "win32":
        assert kwargs == {}
        return
    assert kwargs["creationflags"] == subprocess.CREATE_NO_WINDOW
    startupinfo = kwargs["startupinfo"]
    assert isinstance(startupinfo, subprocess.STARTUPINFO)
    assert startupinfo.dwFlags & subprocess.STARTF_USESHOWWINDOW
    assert startupinfo.wShowWindow == subprocess.SW_HIDE


def test_run_checked_passes_hidden_console_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(img_tools.subprocess, "run", fake_run)
    img_tools._run_checked(["ffmpeg"])
    if sys.platform == "win32":
        assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW
        assert "startupinfo" in captured
    else:
        assert "creationflags" not in captured


def test_optimize_image_with_tools_rejects_unknown_extension(tmp_path: Path) -> None:
    source = tmp_path / "image.bmp"
    source.write_bytes(b"fake")
    with pytest.raises(ValueError, match="not supported"):
        img_tools.optimize_image_with_tools(
            source,
            tmp_path / "out.bmp",
            project_root=tmp_path,
        )
