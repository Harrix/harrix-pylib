"""Tests for front matter helpers."""

from __future__ import annotations

from harrix_pylib.md_format.front_matter import _trim_trailing_blank_lines


def test_trim_trailing_blank_lines_keeps_single_final_newline() -> None:
    assert _trim_trailing_blank_lines("line one\nline two\n\n") == "line one\nline two\n"
    assert _trim_trailing_blank_lines("line one\nline two\n") == "line one\nline two\n"
