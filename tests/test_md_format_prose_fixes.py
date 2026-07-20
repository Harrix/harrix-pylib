"""Tests for MdChecker autofixes applied by MdFormatter prose pass."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from harrix_pylib.md_checker import MdChecker
from harrix_pylib.md_format import MdFormatter
from harrix_pylib.py_docstring_format import PyDocstringFormatter

if TYPE_CHECKING:
    from pathlib import Path


def _format(text: str) -> str:
    return MdFormatter(end_of_line="lf", prose_wrap="preserve").format(text)


def _checker_errors(tmp_path: Path, text: str, rules: set[str]) -> list[str]:
    path = tmp_path / "prose_fixes_test.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    return list(MdChecker().check(path, select=rules))


@pytest.mark.parametrize(
    ("source", "rules", "expected_snippet"),
    [
        ("Use markdown daily.\n", {"H006"}, "Markdown"),
        ("```py\nprint(1)\n```\n", {"H007"}, "```python"),
        ("Hello , world.\n", {"H015"}, "Hello, world."),
        ("Yes - no.\n", {"H016"}, "Yes — no."),
        ("Wait...\n", {"H017"}, "Wait…"),
        ("![photo](a.png)\n", {"H020"}, "![Photo](a.png)"),
        ("End. next\n", {"H021"}, "End. Next"),
        ("a\u00a0b\n", {"H022"}, "a b"),
        ("2 x 3\n", {"H024"}, "2 \u00d7 3"),
        ("Dialogue \u2015 line.\n", {"H026"}, "Dialogue — line."),
        ("See №1.\n", {"H027"}, "See № 1."),
        ("Really?.\n", {"H028"}, "Really?"),
        ("**Note:**text\n", {"H029"}, "**Note:** text"),
        ("**Note**: text\n", {"H030"}, "**Note:** text"),
        ("##Title\n", {"H036"}, "## Title"),
        ("[Link](folder\\file.md)\n", {"H039"}, "[Link](folder/file.md)"),
        ("a\u200bb\n", {"H042"}, "ab"),
        ("Привет,мир\n", {"H050"}, "Привет, мир"),  # ignore: HP001
        ("## Title.\n", {"H057"}, "## Title\n"),
        ("Слово.»\n", {"H058"}, "Слово»."),  # ignore: HP001
    ],
)
def test_formatter_fixes_checker_rules(tmp_path: Path, source: str, rules: set[str], expected_snippet: str) -> None:
    assert _checker_errors(tmp_path, source, rules), f"expected MdChecker to flag {rules} on {source!r}"
    result = _format(source)
    assert expected_snippet in result
    assert not _checker_errors(tmp_path, result, rules), result


def test_formatter_fixes_russian_lang_gated_rules(tmp_path: Path) -> None:
    source = "---\nlang: ru\n---\n\nСпасибо Вам за 50%.\n"  # ignore: HP001
    rules = {"H023", "H044"}
    assert _checker_errors(tmp_path, source, rules)
    result = _format(source)
    assert "вам" in result  # ignore: HP001
    assert "50 %" in result
    assert not _checker_errors(tmp_path, result, rules), result


def test_formatter_skips_inline_and_fenced_code() -> None:
    source = "Use `markdown` and:\n\n```text\n2 x 3\n```\n"
    result = _format(source)
    assert "`markdown`" in result
    assert "2 x 3" in result


def test_formatter_preserves_blockquote_attribution_double_dash() -> None:
    source = "> -- Author\n"
    result = _format(source)
    assert "-- Author" in result


def test_formatter_preserves_digit_en_dash_range() -> None:
    source = "See 2019\u20132020.\n"
    result = _format(source)
    assert "2019\u20132020" in result


def test_formatter_can_disable_prose_fixes() -> None:
    source = "Use markdown daily.\n"
    result = MdFormatter(end_of_line="lf", apply_prose_fixes=False).format(source)
    assert "markdown" in result
    assert "Markdown" not in result


def test_py_docstring_formatter_inherits_prose_fixes() -> None:
    source = 'def f():\n    """Yes - no. Wait...\n\n    """\n'
    result = PyDocstringFormatter().format(source)
    assert "—" in result
    assert "…" in result


def test_formatter_preserves_shields_io_query_string() -> None:
    """H050 must not insert a space after `?` inside link destinations."""
    source = (
        "![GitHub](https://img.shields.io/badge/GitHub-harrix--pyssg-blue?logo=github) "
        "![GitHub](https://img.shields.io/github/license/Harrix/harrix-pyssg) "
        "![PyPI](https://img.shields.io/pypi/v/harrix-pyssg)\n"
    )
    result = _format(source)
    assert "?logo=github" in result
    assert "? logo=" not in result
    assert "? Logo=" not in result


def test_formatter_wraps_bare_filenames_before_h006(tmp_path: Path) -> None:
    """Bare filenames/paths become inline code so H006 does not uppercase extensions."""
    source = (
        "Quick launcher settings from config.json.\n\n"
        "Open recover.sql if missing.\n\n"
        "See src/app/config.json for details.\n\n"
        "Keep `already.sql` as is.\n\n"
        "already combined .g.md files from subfolders.\n\n"
        "Use sql and json in prose.\n"
    )
    result = _format(source)
    assert "`config.json`" in result
    assert "`recover.sql`" in result
    assert "`src/app/config.json`" in result
    assert "`already.sql`" in result
    assert "combined `g.md` files" in result
    assert "combined.`g.md`" not in result
    assert "recover.SQL" not in result
    assert "config.JSON" not in result
    assert "SQL" in result
    assert "JSON" in result
    assert not _checker_errors(tmp_path, result, {"H006"}), result


def test_checker_skips_file_extension_fragments(tmp_path: Path) -> None:
    """H006 must not flag extensions inside bare filenames before formatting."""
    source = "Create from recover.sql if missing.\n"
    assert not _checker_errors(tmp_path, source, {"H006"}), source


def test_py_docstring_formatter_wraps_filenames() -> None:
    """Docstring prose wraps filenames before H006 uppercase."""
    source = (
        "def f():\n"
        '    """Quick launcher settings from config.json."""\n\n'
        "def g():\n"
        '    """Open the SQLite file from app config (create from recover.sql if missing)."""\n\n'
        "def h():\n"
        '    """already combined .g.md files from subfolders."""\n'
    )
    result = PyDocstringFormatter().format(source)
    assert "`config.json`" in result
    assert "`recover.sql`" in result
    assert "combined `g.md` files" in result
    assert "combined.`g.md`" not in result
    assert "recover.SQL" not in result
    assert "config.JSON" not in result
