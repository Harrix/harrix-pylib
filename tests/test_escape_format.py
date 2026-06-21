"""Tests for markdown text escaping."""

from __future__ import annotations

from harrix_pylib.md_format.escape_format import escape_markdown_text


def test_escape_markdown_text_escapes_user_examples() -> None:
    assert escape_markdown_text("Strelets A* center") == "Strelets A\\* center"
    assert escape_markdown_text("string type char* with") == "string type char\\* with"
    assert escape_markdown_text("prefix «t_»") == "prefix «t\\_»"


def test_escape_markdown_text_keeps_non_emphasis_like_characters() -> None:
    assert escape_markdown_text("5 * 2") == "5 * 2"
    assert escape_markdown_text("foo_bar_baz") == "foo_bar_baz"
    assert escape_markdown_text("a * b * c") == "a * b * c"
    assert escape_markdown_text("read:user") == "read:user"


def test_escape_markdown_text_skips_code_block_placeholder() -> None:
    assert escape_markdown_text("HSKMDFMTCODE0") == "HSKMDFMTCODE0"
