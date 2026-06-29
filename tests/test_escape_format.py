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
    assert escape_markdown_text("foo*bar") == "foo*bar"


def test_escape_markdown_text_escapes_intraword_asterisk_with_non_ascii_letters() -> None:
    assert (
        escape_markdown_text("Двигатель. Его мощность ток*напражение")  # noqa: RUF001
        == "Двигатель. Его мощность ток\\*напражение"
    )
    assert escape_markdown_text("ток*напражение") == "ток\\*напражение"  # noqa: RUF001


def test_escape_markdown_text_keeps_prettier_literal_cases() -> None:
    assert escape_markdown_text(r"Oculus\Software\hyperbolic") == r"Oculus\Software\hyperbolic"
    assert escape_markdown_text("t._id, t.amount") == "t.\\_id, t.amount"
    assert escape_markdown_text("2. _[directory_name].short.g.md") == "2. _[directory_name].short.g.md"
    assert escape_markdown_text("[_id, habit_name]") == r"[\_id, habit_name]"


def test_escape_markdown_text_escapes_identifier_underscores() -> None:
    assert (
        escape_markdown_text("Table save handlers are provided by _get_save_handlers(); _auto_save_row")
        == "Table save handlers are provided by \\_get_save_handlers(); \\_auto_save_row"
    )
    assert escape_markdown_text("Must be in _SAFE_TABLES.") == "Must be in \\_SAFE_TABLES."
    assert (
        escape_markdown_text("Monthly data from _get_monthly_data_for_exercise.")
        == "Monthly data from \\_get_monthly_data_for_exercise."
    )
    assert escape_markdown_text("suffix with _1, _2 if needed.") == "suffix with \\_1, \\_2 if needed."
    assert (
        escape_markdown_text("aggregated file _<FolderName>.g.md (e.g. Fiction -> _Fiction.g.md),")
        == "aggregated file \\_<FolderName>.g.md (e.g. Fiction -> \\_Fiction.g.md),"
    )
    assert escape_markdown_text("from _INCORRECT_WORD_PATTERNS.") == "from \\_INCORRECT_WORD_PATTERNS."
    assert escape_markdown_text("определяют макрос _WIN32.") == "определяют макрос \\_WIN32."


def test_escape_markdown_text_skips_code_block_placeholder() -> None:
    assert escape_markdown_text("HSKMDFMTCODE0") == "HSKMDFMTCODE0"
