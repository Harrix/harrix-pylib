"""Tests for inline text normalization."""

from __future__ import annotations

from harrix_pylib.md_format.text_format import normalize_inline_spaces


def test_normalize_inline_spaces_collapses_runs() -> None:
    assert normalize_inline_spaces("foo  bar") == "foo bar"
    assert normalize_inline_spaces(");  # ignore") == "); # ignore"
    assert normalize_inline_spaces("a\t\tb") == "a b"
