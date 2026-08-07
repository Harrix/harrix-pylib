"""Tests for MdChecker autofixes applied by MdFormatter prose pass."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from harrix_pylib.md_checker import MdChecker
from harrix_pylib.md_format import MdFormatter
from harrix_pylib.md_format.prose_fixes import _apply_checker_prose_fixes
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
        ("Wrong :colon.\n", {"H015"}, "Wrong:colon."),
        ("Yes - no.\n", {"H016"}, "Yes — no."),
        ("Wait...\n", {"H017"}, "Wait…"),
        ("![photo](a.png)\n", {"H020"}, "![Photo](a.png)"),
        ("End. next\n", {"H021"}, "End. Next"),
        ("a\u00a0b\n", {"H022"}, "a b"),
        ("2 x 3\n", {"H024"}, "2 \u00d7 3"),
        ("Dialogue \u2015 line.\n", {"H026"}, "Dialogue — line."),
        ("See №1.\n", {"H027"}, "See № 1."),
        ("Really?.\n", {"H028"}, "Really?.."),
        ("Вот как?... Ну.\n", {"H028"}, "Вот как?.. Ну."),
        ("Неужели!.\n", {"H028"}, "Неужели!.."),
        ("Неужели!... Ну.\n", {"H028"}, "Неужели!.. Ну."),
        ("**Note:**text\n", {"H029"}, "**Note:** text"),
        ("**Note**: text\n", {"H030"}, "**Note:** text"),
        ("##Title\n", {"H036"}, "## Title"),
        ("[Link](folder\\file.md)\n", {"H039"}, "[Link](folder/file.md)"),
        ("[jsfiddle.net](https:\\jsfiddle.net)\n", {"H039"}, "<https://jsfiddle.net>"),
        ("a\u200bb\n", {"H042"}, "ab"),
        ("Привет,мир\n", {"H050"}, "Привет, мир"),  # ignore: HP001
        ("## Title.\n", {"H057"}, "## Title\n"),
        ("Слово.»\n", {"H058"}, "Слово»."),  # ignore: HP001
        ("- a\n* b\n", {"H071"}, "- a\n- b\n"),
        ("Title\n=====\n", {"H072"}, "# Title\n"),
        ("Subtitle\n-------\n", {"H072"}, "## Subtitle\n"),
        ("line one\\\nline two  \nline three\n", {"H075"}, "line one  \nline two  \n"),
    ],
)
def test_formatter_fixes_checker_rules(tmp_path: Path, source: str, rules: set[str], expected_snippet: str) -> None:
    assert _checker_errors(tmp_path, source, rules), f"expected MdChecker to flag {rules} on {source!r}"
    result = _format(source)
    assert expected_snippet in result
    assert not _checker_errors(tmp_path, result, rules), result


def test_formatter_preserves_single_hard_break_style(tmp_path: Path) -> None:
    """H075 autofix must not rewrite a file that uses only backslash hard breaks."""
    source = "line one\\\nline two\n"
    assert not _checker_errors(tmp_path, source, {"H075"})
    result = _format(source)
    assert "line one\\" in result or "line one\\\n" in result.replace("\r\n", "\n")
    assert not _checker_errors(tmp_path, result, {"H075"}), result


def test_formatter_structural_pipeline_clears_h063_h064_h065_h066(tmp_path: Path) -> None:
    """H063-H066 are cleared by prose wrap / blank-line / compact-YAML format steps."""
    bare = "See config.json here.\n"
    assert _checker_errors(tmp_path, bare, {"H063"})
    bare_fixed = _format(bare)
    assert "`config.json`" in bare_fixed
    assert not _checker_errors(tmp_path, bare_fixed, {"H063"}), bare_fixed

    list_gap = "- a\n- b\n# Next\n"
    assert _checker_errors(tmp_path, list_gap, {"H064"})
    list_fixed = _format(list_gap)
    assert not _checker_errors(tmp_path, list_fixed, {"H064"}), list_fixed

    table_gap = "| a | b |\n| --- | --- |\n| 1 | 2 |\nNext.\n"
    assert _checker_errors(tmp_path, table_gap, {"H065"})
    table_fixed = _format(table_gap)
    assert not _checker_errors(tmp_path, table_fixed, {"H065"}), table_fixed

    yaml_gap = "---\nlang: en\n\ntitle: x\n---\n\n# T\n"
    assert _checker_errors(tmp_path, yaml_gap, {"H066"})
    yaml_fixed = _format(yaml_gap)
    assert "lang: en\ntitle: x" in yaml_fixed.replace("\r\n", "\n")
    assert not _checker_errors(tmp_path, yaml_fixed, {"H066"}), yaml_fixed


def test_formatter_preserves_gfm_table_alignment(tmp_path: Path) -> None:
    source = "| Left | Center | Right |\n| ---- | :----: | ----: |\n| a | b | c |\n"
    assert not _checker_errors(tmp_path, source, {"H015"})
    result = _format(source)
    assert ":----:" in result
    assert not _checker_errors(tmp_path, result, {"H015"}), result


def test_formatter_fixes_russian_lang_gated_rules(tmp_path: Path) -> None:
    source = "---\nlang: ru\n---\n\nСпасибо Вам за 50%.\n"  # ignore: HP001
    rules = {"H023", "H044"}
    assert _checker_errors(tmp_path, source, rules)
    result = _format(source)
    assert "вам" in result  # ignore: HP001
    assert "50 %" in result
    assert not _checker_errors(tmp_path, result, rules), result


def test_formatter_fixes_decimal_separators_by_lang(tmp_path: Path) -> None:
    for lang in ("en", "ru"):
        source = (
            f"---\nlang: {lang}\n---\n\n"
            "Scale -0,5 to 0,5. Keep 1,234 and 1,234.5. Lists 1, 2 stay. "
            "USB 2.0 and version 3.12.1 stay dotted.\n"
        )
        assert _checker_errors(tmp_path, source, {"H062"})
        result = _format(source)
        assert "-0.5" in result
        assert "0.5" in result
        assert "1,234" in result
        assert "1,234.5" in result
        assert "1, 2" in result
        assert "USB 2.0" in result
        assert "3.12.1" in result
        assert "-0,5" not in result
        assert not _checker_errors(tmp_path, result, {"H062"}), result

    # lang: ru must not convert decimal points to commas
    ru_dots = "---\nlang: ru\n---\n\nЗначения -0.5 и 0.5.\n"  # ignore: HP001
    ru_dots_result = _format(ru_dots)
    assert "-0.5" in ru_dots_result
    assert "0.5" in ru_dots_result
    assert "-0,5" not in ru_dots_result
    assert not _checker_errors(tmp_path, ru_dots_result, {"H062"}), ru_dots_result


def test_formatter_preserves_russian_polite_pronouns_in_quotes() -> None:
    blockquote = (
        "---\nlang: ru\n---\n\n"
        "> — Вы в состоянии объяснить этот невероятный результат? "
        "Будьте добры, воспользуйтесь языком физики.\n>\n"
        "> -- _Лю Цысинь, Задача трех тел_\n"
    )
    result = _format(blockquote)
    assert "— Вы в состоянии" in result
    assert "— вы в состоянии" not in result

    speech = "---\nlang: ru\n---\n\nОн сказал: «Спасибо Вам за помощь».\n"
    result = _format(speech)
    assert "«Спасибо Вам за помощь»" in result
    assert "вам" not in result

    # Still lowercase mid-sentence address outside quotes.
    prose = "---\nlang: ru\n---\n\nОбращаемся к Вам с предложением.\n"
    result = _format(prose)
    assert "к вам с предложением" in result


def test_formatter_preserves_russian_polite_pronouns_at_markdown_title_start() -> None:
    """H023 must not lowercase Вы/Вам at list-link / heading title start."""
    toc_line = "  - [Вам и не снилось...: 10](#вам-и-не-снилось-10)\n"  # ignore: HP001
    toc_fixed = _apply_checker_prose_fixes(toc_line, lang="ru")
    assert "[Вам и не снилось" in toc_fixed  # ignore: HP001
    assert "[вам и не снилось" not in toc_fixed  # ignore: HP001

    heading_fixed = _apply_checker_prose_fixes("## Вам сюда\n", lang="ru")  # ignore: HP001
    assert "## Вам сюда" in heading_fixed  # ignore: HP001
    assert "## вам сюда" not in heading_fixed  # ignore: HP001

    # Mid-sentence link text is still an address → lowercase.
    mid_fixed = _apply_checker_prose_fixes(
        "Смотрите [Ваш вариант](https://example.com).\n",  # ignore: HP001
        lang="ru",
    )
    assert "[ваш вариант]" in mid_fixed  # ignore: HP001

    # Full formatter path keeps title capitalization too.
    toc = "---\nlang: ru\n---\n\n" + toc_line
    result = _format(toc)
    assert "[Вам и не снилось" in result  # ignore: HP001


def test_formatter_preserves_question_mark_two_dots() -> None:
    source = "— Вот как?.. Ну и чему он у него учился?\n"
    result = _format(source)
    assert "?.." in result
    assert "?." not in result.replace("?..", "")
    assert "?..." not in result


def test_formatter_preserves_exclamation_mark_two_dots() -> None:
    source = "— Вот это да!.. Ну и ну.\n"
    result = _format(source)
    assert "!.." in result
    assert "!." not in result.replace("!..", "")
    assert "!..." not in result


def test_formatter_preserves_space_before_text_emoticons() -> None:
    cases = (
        "этом :) Вообще",
        "Hello ;) world.",
        "Great :-D news.",
        "Sad :( day.",
        "Wink ;-P now.",
    )
    for snippet in cases:
        result = _format(f"{snippet}\n")
        assert snippet in result, result


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


def test_formatter_preserves_hyphens_inside_latex_math(tmp_path: Path) -> None:
    """H016 must not turn LaTeX minus hyphens into em dashes inside `$` / `$$` math."""
    source = (
        "Prose uses 1 - 2.\n\n"
        "$$\n"
        "5\\left(-\\sqrt{1 - x^{2} - \\left(y - \\lvert x\\rvert\\right)^{2}}\\right),"
        "\n"
        "$$\n\n"
        "Inline $a - b$ stays.\n"
    )
    result = _format(source)
    assert "1 — 2" in result
    assert "1 - x^{2} - \\left(y - \\lvert x\\rvert\\right)^{2}" in result
    assert "$a - b$" in result
    assert "\u2014" not in result.split("$$")[1]
    assert not _checker_errors(tmp_path, result, {"H016"}), result


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


def test_formatter_preserves_query_string_in_link_label(tmp_path: Path) -> None:
    """H050 must not insert a space after `?` in labels like `[demo?a=2&b=3]`."""
    source = "При вызове [demo?a=2&b=3](https://example.com/demo?a=2&b=3) мы получим `5`.\n"
    assert _checker_errors(tmp_path, source, {"H050"}) == []
    result = _format(source)
    assert "[demo?a=2&b=3]" in result
    assert "[demo? a=2&b=3]" not in result
    assert "?a=2&b=3" in result
    assert not _checker_errors(tmp_path, result, {"H050"}), result


def test_formatter_preserves_lowercase_after_incl_abbrev(tmp_path: Path) -> None:
    """H021 must not capitalize after English abbreviations like `incl.`."""
    source = "Harrix PY rules and docstring Markdown check (incl. private; errors point at file).\n"
    assert _checker_errors(tmp_path, source, {"H021"}) == []
    result = _format(source)
    assert "incl. private" in result
    assert "incl. Private" not in result
    assert not _checker_errors(tmp_path, result, {"H021"}), result


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


def test_formatter_wraps_vscode_code_snippets_filename() -> None:
    """VS Code `*.code-snippets` files are wrapped like other bare filenames."""
    source = "**markdown.json**:\n**common.code-snippets**:\n"
    result = _format(source)
    assert "**`markdown.json`**:" in result
    assert "**`common.code-snippets`**:" in result


def test_formatter_wraps_bare_leading_dot_extensions(tmp_path: Path) -> None:
    """Bare `.exe` / `.pdf` become inline code; H006 must not rewrite to `.EXE`."""
    source = (
        "Для версии Qt под компилятор Visual Studio статья "
        "[Запуск Qt приложений под Visual Studio .exe вне Qt Creator]"
        "(https://example.com/run-qt).\n\n"
        "Откройте .pdf или .DLL вручную.\n"
    )
    result = _format(source)
    assert "Visual Studio `.exe` вне Qt Creator" in result
    assert "`.pdf`" in result
    assert "`.DLL`" not in result
    assert "`.dll`" in result
    assert ".EXE" not in result
    assert not _checker_errors(tmp_path, result, {"H006"}), result
    assert not _checker_errors(tmp_path, "Visual Studio .exe вне Qt Creator.\n", {"H006"})


def test_formatter_fixes_mistyped_http_scheme_separators(tmp_path: Path) -> None:
    r"""`https:\host` / `https:/host` become real `https://` URLs (H039)."""
    source = (
        "В том же [jsfiddle.net](https:\\jsfiddle.net) код.\n\n"
        "Already broken [x](https:/example.com/path).\n\n"
        "Local [Link](folder\\file.md).\n"
    )
    result = _format(source)
    # Domain label + fixed https URL collapses to a full-URI angle autolink.
    assert "В том же <https://jsfiddle.net> код." in result
    assert "<jsfiddle.net>" not in result
    assert "[x](https://example.com/path)" in result
    assert "[Link](folder/file.md)" in result
    assert "https:/jsfiddle.net" not in result
    assert "https:\\" not in result
    assert not _checker_errors(tmp_path, result, {"H039"}), result


def test_formatter_keeps_node_js_as_product_name(tmp_path: Path) -> None:
    """Node.js is a product name: do not wrap; rewrite bare node.js via H006."""
    source = "Install Node.js first.\n\nAlso support node.js on Windows.\n\nOpen src/node.js for the script.\n"
    result = _format(source)
    assert "Install Node.js first." in result
    assert "Also support Node.js on Windows." in result
    assert "`Node.js`" not in result
    assert "`src/node.js`" in result
    assert not _checker_errors(tmp_path, result, {"H006"}), result


def test_checker_skips_file_extension_fragments(tmp_path: Path) -> None:
    """H006 must not flag extensions inside bare filenames before formatting."""
    source = "Create from recover.sql if missing.\n"
    assert not _checker_errors(tmp_path, source, {"H006"}), source


def test_h006_longest_wins_and_multiple_replacements() -> None:
    """Single-pass H006: several dictionary hits on one line; abbrev spacing."""
    source = "Use latex and html together with markdown notes.\n"
    result = _format(source)
    assert "LaTeX" in result
    assert "HTML" in result
    assert "Markdown" in result

    abbrev_source = "Это, т.е. срочно.\n"  # ignore: HP001
    abbrev_result = _format(abbrev_source)
    assert "т. е." in abbrev_result  # ignore: HP001
    assert "т.е." not in abbrev_result  # ignore: HP001


def test_h006_skips_urls_and_html() -> None:
    """H006 must not rewrite tokens inside link destinations or HTML tags."""
    source = "See [docs](https://example.com/markdown) and <span class='markdown'>x</span>.\n"
    result = _format(source)
    assert "](https://example.com/markdown)" in result
    assert "<span class='markdown'>" in result


def test_format_folder_formats_all_md_including_g_md(tmp_path: Path) -> None:
    """format_folder formats normal .md and generated *.g.md files alike."""
    note = tmp_path / "note.md"
    docs_dump = tmp_path / "action_output_bus.g.md"
    combine_dump = tmp_path / "_Notes.g.md"
    short_generated = tmp_path / "notes.short.g.md"

    note.write_text("Use markdown daily.\n", encoding="utf-8", newline="\n")
    docs_dump.write_text(
        "- [🏛️ Class `X`](#%EF%B8%8F-class-x)\n",
        encoding="utf-8",
        newline="\n",
    )
    combine_dump.write_text("Use markdown daily.\n", encoding="utf-8", newline="\n")
    short_generated.write_text("Use markdown daily.\n", encoding="utf-8", newline="\n")

    result = MdFormatter(end_of_line="lf").format_folder(tmp_path)

    assert "Markdown" in note.read_text(encoding="utf-8")
    docs_text = docs_dump.read_text(encoding="utf-8")
    assert "%EF%B8%8F" not in docs_text
    assert "\ufe0f" in docs_text
    assert "Markdown" in combine_dump.read_text(encoding="utf-8")
    assert "Markdown" in short_generated.read_text(encoding="utf-8")
    assert "action_output_bus.g.md" in result
    assert "_Notes.g.md" in result
    assert "notes.short.g.md" in result


def test_format_file_still_formats_explicit_g_md(tmp_path: Path) -> None:
    """Explicit format_file on a .g.md path still applies prose fixes."""
    generated = tmp_path / "_Notes.g.md"
    generated.write_text("Use markdown daily.\n", encoding="utf-8", newline="\n")
    MdFormatter(end_of_line="lf").format_file(generated)
    assert "Markdown" in generated.read_text(encoding="utf-8")


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
