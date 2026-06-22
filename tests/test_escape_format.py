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


def test_escape_markdown_text_keeps_prettier_literal_cases() -> None:
    assert escape_markdown_text(r"Oculus\Software\hyperbolic") == r"Oculus\Software\hyperbolic"
    assert escape_markdown_text("from _INCORRECT_WORD_PATTERNS.") == "from _INCORRECT_WORD_PATTERNS."
    assert escape_markdown_text("t._id, t.amount") == "t._id, t.amount"
    assert escape_markdown_text("2. _[directory_name].short.g.md") == "2. _[directory_name].short.g.md"
    assert escape_markdown_text("[_id, habit_name]") == r"[\_id, habit_name]"
    assert escape_markdown_text("_Fiction.g.md") == "_Fiction.g.md"


def test_escape_markdown_text_escapes_all_caps_macros() -> None:
    assert escape_markdown_text("определяют макрос _WIN32.") == "определяют макрос \\_WIN32."
    assert escape_markdown_text("use _DEBUG flag") == "use \\_DEBUG flag"
    assert escape_markdown_text(r"определяют макрос \_WIN32.") == "определяют макрос \\_WIN32."


def test_escape_markdown_text_skips_code_block_placeholder() -> None:
    assert escape_markdown_text("HSKMDFMTCODE0") == "HSKMDFMTCODE0"
