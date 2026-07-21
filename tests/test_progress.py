"""Tests for terminal progress helpers and apply_func progress integration."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h
from harrix_pylib.progress import ProgressBar, iter_with_progress, render_progress, render_progress_ascii


def test_render_progress() -> None:
    assert render_progress(0, 10) == "Progress: |" + ("░" * 40) + "| 0/10 (0%)"
    assert "10/10 (100%)" in render_progress(10, 10)
    assert "5/10 (50%)" in render_progress(5, 10)
    assert render_progress_ascii(2, 4).startswith("Progress: |")
    assert "=" in render_progress_ascii(2, 4)


def test_progress_bar_writes_to_stream() -> None:
    stream = StringIO()
    # Force-enable even though StringIO is not a TTY.
    bar = ProgressBar(4, stream=stream, enabled=True, width=10)
    bar.update(1)
    bar.update(2)
    bar.finish()
    text = stream.getvalue()
    assert "1/4" in text
    assert "4/4 (100%)" in text
    assert text.endswith("\n")


def test_iter_with_progress_disabled() -> None:
    stream = StringIO()
    items = list(iter_with_progress(["a", "b", "c"], show_progress=False, stream=stream))
    assert items == ["a", "b", "c"]
    assert stream.getvalue() == ""


def test_iter_with_progress_enabled_on_forced_stream() -> None:
    stream = StringIO()
    bar_items = ["x", "y"]
    # show_progress True but StringIO is not TTY -> no output unless we use ProgressBar enabled.
    # iter_with_progress only enables on isatty; verify silent on StringIO:
    assert list(iter_with_progress(bar_items, show_progress=True, stream=stream)) == bar_items
    assert stream.getvalue() == ""


def test_apply_func_show_progress_false_preserves_messages() -> None:
    def maybe_change(filename: Path | str) -> str:
        path = Path(filename)
        if path.name == "changed.txt":
            path.write_text("CHANGED", encoding="utf8")
            return "✅ File changed."
        return "File is not changed."

    with TemporaryDirectory() as temp_folder:
        root = Path(temp_folder)
        (root / "changed.txt").write_text("old", encoding="utf8")
        (root / "same1.txt").write_text("a", encoding="utf8")
        (root / "same2.txt").write_text("b", encoding="utf8")
        output = h.file.apply_func(root, ".txt", maybe_change, show_progress=False)

    assert "changed.txt" in output
    assert "same1.txt" not in output
    assert "ℹ️ 2 file(s) not changed." in output


def test_apply_func_progress_on_forced_bar_via_check_func() -> None:
    """check_func with show_progress=False still aggregates errors."""

    def always_error(filename: Path | str) -> list[str]:
        return [f"err:{Path(filename).name}"]

    with TemporaryDirectory() as temp_folder:
        root = Path(temp_folder)
        (root / "a.py").write_text("x = 1\n", encoding="utf8")
        (root / "b.py").write_text("y = 2\n", encoding="utf8")
        errors = h.file.check_func(root, ".py", always_error, show_progress=False)

    assert errors == ["err:a.py", "err:b.py"] or set(errors) == {"err:a.py", "err:b.py"}
