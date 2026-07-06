"""Tests for markdown formatting."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pytest

from harrix_pylib.md_format import MarkdownFormatter
from harrix_pylib.md_format.front_matter import _prepend_markdown_header
from harrix_pylib.md_format.table_format import _text_display_width


def _read_fixture(name: str) -> str:
    path = Path(__file__).parent / "data" / "md_format" / name
    return path.read_text(encoding="utf-8")


def _fixture_pairs() -> list[tuple[str, str]]:
    root = Path(__file__).parent / "data" / "md_format"
    pairs: list[tuple[str, str]] = []
    for before_path in sorted(root.glob("*_before.md")):
        stem = before_path.name[: -len("_before.md")]
        after_name = f"{stem}_after.md"
        if (root / after_name).is_file():
            pairs.append((before_path.name, after_name))
    return pairs


_FIXTURE_PAIRS = _fixture_pairs()


# Upstream fixtures were extracted with Prettier proseWrap: always, printWidth: 80.
class _FixtureFormatKwargs(TypedDict):
    end_of_line: str
    prose_wrap: str
    print_width: int


_FIXTURE_FORMAT_KWARGS: _FixtureFormatKwargs = {
    "end_of_line": "lf",
    "prose_wrap": "always",
    "print_width": 80,
}


def _format_markdown(
    text: str,
    *,
    end_of_line: str = "crlf",
    prose_wrap: str = "preserve",
    print_width: int = 80,
) -> str:
    return MarkdownFormatter(
        end_of_line=end_of_line,
        prose_wrap=prose_wrap,
        print_width=print_width,
    ).format(text)


@pytest.mark.parametrize(
    ("before_name", "after_name"),
    _FIXTURE_PAIRS,
    ids=[before_name[: -len("_before.md")] for before_name, _ in _FIXTURE_PAIRS],
)
def test_format_markdown_content_matches_fixture(before_name: str, after_name: str) -> None:
    before = _read_fixture(before_name)
    expected = _read_fixture(after_name)
    result = _format_markdown(before, **_FIXTURE_FORMAT_KWARGS)
    assert result == expected


def test_format_markdown_content_does_not_wrap_long_list_links_by_default() -> None:
    source = "- [Не сохраняем сессию с открытыми файлами](#не-сохраняем-сессию-с-открытыми-файлами)\n"
    result = _format_markdown(source, end_of_line="lf")
    expected_link = source.strip().removeprefix("- ")
    assert expected_link in result
    assert "фай\n" not in result


def test_format_markdown_content_uses_crlf_by_default() -> None:
    result = _format_markdown("# Title\n\n")
    assert "\r\n" in result
    assert result.endswith("\r\n")


def test_format_markdown_content_preserves_wiki_link() -> None:
    result = _format_markdown("[[A simple wiki link]]\n")
    assert "[[A simple wiki link]]" in result


@pytest.mark.parametrize(
    ("source", "expected", "forbidden"),
    [
        (
            "GitHub: <https://github.com/Harrix/harrix-pylib>\n",
            "GitHub: <https://github.com/Harrix/harrix-pylib>",
            "[https://github.com/Harrix/harrix-pylib]",
        ),
        (
            "<https://en.wikipedia.org/wiki/Rod_(optical_phenomenon)>\n",
            "<https://en.wikipedia.org/wiki/Rod_(optical_phenomenon)>",
            "\\_",
        ),
        (
            "[Rod](https://en.wikipedia.org/wiki/Rod_(optical_phenomenon))\n",
            "[Rod](https://en.wikipedia.org/wiki/Rod_(optical_phenomenon))",
            "\\_",
        ),
        (
            "GitHub: [harrix-pylib](https://github.com/Harrix/harrix-pylib)\n",
            "[harrix-pylib](https://github.com/Harrix/harrix-pylib)",
            "",
        ),
        (
            "Email: <user@example.com>\n",
            "Email: <user@example.com>",
            "[user@example.com](mailto:user@example.com)",
        ),
        (
            "Site: [MSI website](http://www.msi.com)\n",
            "[MSI website](http://www.msi.com)",
            "<www.msi.com>",
        ),
    ],
)
def test_format_markdown_content_preserves_links(source: str, expected: str, forbidden: str) -> None:
    result = _format_markdown(source)
    assert expected in result
    if forbidden:
        assert forbidden not in result


def test_format_markdown_content_converts_self_referential_url_link_to_angle_autolink() -> None:
    url = "http://www.example.org/docs/report-1-7.pdf"
    source = f"[{url}]({url})\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == f"<{url}>\n"
    assert f"[{url}]({url})" not in result
    assert result.strip() != url


def test_format_markdown_content_preserves_many_angle_autolinks_without_placeholder_collision() -> None:
    """Placeholder restore must match full indices (AL1 must not corrupt AL10)."""
    links = [f"<https://example.com/{index}>" for index in range(12)]
    source = "\n".join(f"- {link}" for link in links) + "\n"
    result = _format_markdown(source, end_of_line="lf")
    for link in links:
        assert link in result
    assert result.count("<https://example.com/1>") == 1


def test_format_markdown_content_preserves_linkify_bare_domain_without_protocol() -> None:
    source = "| Site | www.msi.com |\n| --- | --- |\n"
    result = _format_markdown(source)
    assert "www.msi.com" in result
    assert "<www.msi.com>" not in result
    assert "[www.msi.com](http://www.msi.com)" not in result


def test_format_markdown_content_preserves_bare_domains_in_list() -> None:
    source = "- jsfiddle.net\n- drive.google.com\n- vimeo.com\n- www.youtube.com\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == source


def test_format_markdown_content_converts_explicit_bare_domain_link_to_angle_autolink() -> None:
    source = "[www.example.com](http://www.example.com)\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == "<www.example.com>\n"


def test_format_markdown_content_preserves_front_matter() -> None:
    source = "---\nhello: world\n---\n\n# Title\n"
    result = _format_markdown(source)
    assert "---\r\nhello: world\r\n---" in result
    assert "# Title" in result


def test_prepend_markdown_header_strips_existing_front_matter() -> None:
    header = "---\nlang: en\n---"
    source = "---\nlang: ru\n---\n\n# Title\n"
    result = _prepend_markdown_header(header, source)
    assert result.startswith("---\nlang: en\n---\n\n# Title")
    assert result.count("---") == 2  # noqa: PLR2004


def test_format_markdown_content_formats_lists() -> None:
    result = _format_markdown("- one\n- two\n")
    assert "- one" in result
    assert "- two" in result


def test_format_markdown_content_formats_italic_with_underscores() -> None:
    for source in ("*No docstring provided.*\n", "_No docstring provided._\n"):
        result = _format_markdown(source)
        assert "_No docstring provided._" in result
        assert "*No docstring provided.*" not in result


@pytest.mark.parametrize(
    "source",
    [
        (
            "- [Жареная картошка](#жареная-картошка)\n"
            "- [Заклинание «Соль-вода!» против ос и пчёл](#заклинание-соль-вода-против-ос-и-пчёл)\n"
        ),
        "![Настройки клавиатуры](Ноутбук__Gigabyte-Aero-15-OLED-XD/img/keyboard.png)\n",
    ],
)
def test_format_markdown_content_preserves_cyrillic_urls_without_encoding(source: str) -> None:
    result = _format_markdown(source)
    for line in source.strip().splitlines():
        assert line in result
    assert "%D0" not in result


def test_format_markdown_content_decodes_percent_encoded_unicode_in_link_url() -> None:
    source = (
        "[Видеоуроки по Arduino, 7-я серия - I2C и Processing]"
        "(http://wiki.amperka.ru/%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D1%83%D1%80%D0%BE%D0%BA%D0%B8:7-i2c-%D0%B8-processing)\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == (
        "[Видеоуроки по Arduino, 7-я серия - I2C и Processing](http://wiki.amperka.ru/видеоуроки:7-i2c-и-processing)\n"
    )
    assert "%D0" not in result


def test_format_markdown_content_decodes_percent_encoded_unicode_in_angle_autolink() -> None:
    source = "<http://wiki.amperka.ru/%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D1%83%D1%80%D0%BE%D0%BA%D0%B8>\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == "<http://wiki.amperka.ru/видеоуроки>\n"


def test_format_markdown_content_preserves_inline_code_with_backticks() -> None:
    source = "`` `\\n`$1`:` ``\n"
    result = _format_markdown(source)
    assert "`` `\\n`$1`:` ``" in result


def test_format_markdown_content_does_not_scan_links_inside_inline_code() -> None:
    source = (
        "Вот когда пришло время вступать в действие перегруженному оператору индексации. "
        "Теперь мы можем заменить функции `getElementAt()` и `setElementAt()` "
        "оператором `operator[]()`.\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert "`operator[]()`" in result
    assert "`getElementAt()`" in result
    assert "`setElementAt()`" in result
    assert "HSKMDFMTLD" not in result


def test_format_markdown_content_scans_real_links_but_not_inline_code_in_same_line() -> None:
    source = "Ссылка [harrix-pylib](https://github.com/Harrix/harrix-pylib) и код `operator[]()`.\n"
    result = _format_markdown(source, end_of_line="lf")
    assert "[harrix-pylib](https://github.com/Harrix/harrix-pylib)" in result
    assert "`operator[]()`" in result
    assert "HSKMDFMTLD" not in result


def test_format_markdown_content_preserves_escaped_pipe_in_table_inline_code() -> None:
    source = "| Col1 | Col2 |\n| --- | --- |\n| `a\\|b` | Соответствует a или b |\n"
    result = _format_markdown(source)
    assert "`a\\|b`" in result
    assert "| `a|b` |" not in result


def test_format_markdown_content_keeps_unescaped_pipe_in_inline_code_outside_table() -> None:
    source = "Use `a|b` in text.\n"
    result = _format_markdown(source)
    assert "`a|b`" in result
    assert "`a\\|b`" not in result


def test_format_markdown_content_formats_nested_lists() -> None:
    source = "- [List](#list)\n    - [File a](#a)\n    - [File b](#b)\n"
    result = _format_markdown(source)
    assert "  - [File a](#a)" in result
    assert "    - [File a]" not in result
    assert "  - [File b](#b)" in result


def test_format_markdown_content_inserts_blank_line_after_list() -> None:
    source = (
        "- Git discard commands — use `git` directly\n"
        "- Note titles, preview copy, drag-and-drop, folder expansion, etc.\n"
        "`NotesProvider._templateTargets` remain in `extension.js`.\n"
    )
    result = _format_markdown(source)
    assert "etc.\r\n\r\n`NotesProvider" in result


def test_format_markdown_content_preserves_blank_line_after_list() -> None:
    source = "- one\n- two\n\nParagraph after list.\n"
    result = _format_markdown(source)
    assert "- two\r\n\r\nParagraph after list." in result


def test_format_markdown_content_formats_tables() -> None:
    result = _format_markdown("|a|b|\n|---|---|\n|1|2|\n")
    assert "| a   | b   |" in result
    assert "| 1   | 2   |" in result
    assert "| --- | --- |" in result


def test_format_markdown_content_aligns_table_columns() -> None:
    source = (
        "| File                 | Config key                               | "
        "Purpose                                    |\n"
        "| -------------------- | ---------------------------------------- | "
        "------------------------------------------ |\n"
        "| `pypi-token.txt`     | `pypi_token` in `config/config.json`     | "
        "PyPI token for publishing Python libraries |\n"
        "| `bothub-api-key.txt` | `bothub_api_key` in `config/config.json` | "
        "BotHub access token for AI features        |\n"
    )
    result = _format_markdown(source)
    assert (
        "| File                 | Config key                               | "
        "Purpose                                    |" in result
    )
    assert (
        "| -------------------- | ---------------------------------------- | "
        "------------------------------------------ |" in result
    )


def test_format_markdown_content_aligns_table_columns_with_angle_autolinks() -> None:
    source = (
        "| Title            | Downloads oer week | Link                                             |\n"
        "| ---------------- | ------------------ | ------------------------------------------------ |\n"
        "| bootstrap        | 4 459 946          | <https://www.npmjs.com/package/bootstrap>        |\n"
        "| Bulma            | 199 847            | <https://www.npmjs.com/package/bulma>            |\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == source


def test_format_markdown_content_keeps_paragraph_after_table() -> None:
    source = (
        "| File | Config key | Purpose |\n"
        "| --- | --- | --- |\n"
        "| row1 | key1 | purpose1 |\n"
        "For school/corporate Wi-Fi, set optional `bothub.proxy`.\n"
        "Paths in `config.json` use the `snippet:api-keys/...` prefix.\n"
    )
    result = _format_markdown(source)
    assert "| row1 | key1" in result
    assert "purpose1 |" in result
    assert "For school/corporate Wi-Fi" in result
    assert "Paths in `config.json`" in result
    assert "| For school/corporate Wi-Fi" not in result


def test_format_markdown_content_unwraps_spurious_table_rows() -> None:
    source = (
        "| File | Config key | Purpose |\n"
        "| --- | --- | --- |\n"
        "| row1 | key1 | purpose1 |\n"
        "| For school/corporate Wi-Fi, set optional `bothub.proxy` in "
        "`config/config.json` (see [DEVELOPMENT.md](../DEVELOPMENT.md)). |  |  |\n"
    )
    result = _format_markdown(source)
    assert "| row1 | key1" in result
    assert "purpose1 |" in result
    assert "For school/corporate Wi-Fi" in result
    assert "| For school/corporate Wi-Fi" not in result


def test_format_markdown_content_keeps_table_row_with_empty_cell() -> None:
    source = (
        "| Function/Class | Description |\n"
        "|----------------|-------------|\n"
        "| 🏛️ Class [`StyleSheet`](https://github.com/Harrix/harrix-pylib/blob/main/docs/styles.g.md) | "
        "Collected CSS class rules from SVG <style> elements. |\n"
        "| 🔧 [`_format_style`](https://github.com/Harrix/harrix-pylib/blob/main/docs/styles.g.md) |  |\n"
    )
    result = _format_markdown(source)
    table_lines = [line for line in result.splitlines() if line.strip().startswith("|")]
    assert len(table_lines) == 4  # noqa: PLR2004
    assert any("_format_style" in line and line.strip().endswith("|") for line in table_lines)
    col1_widths = [_text_display_width(line.split("|")[1]) for line in table_lines]
    assert len(set(col1_widths)) == 1


def test_format_markdown_content_keeps_multiple_trailing_empty_table_cells() -> None:
    source = (
        "| Manufacturer | Boot Menu | BIOS Key | Type | Models |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| ACER | Esc, F12, F9 | Del, F2 | | |\n"
        "| ASUS | F8 | F9 | desktop | |\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    table_lines = [line for line in result.splitlines() if line.strip().startswith("|")]
    assert table_lines
    expected_pipes = table_lines[0].count("|")
    assert all(line.count("|") == expected_pipes for line in table_lines)
    assert "ACER" in result
    assert "Del, F2" in result
    assert "ASUS" in result
    assert "desktop" in result


def test_format_markdown_content_formats_math() -> None:
    result = _format_markdown("$E=mc^2$\n")
    assert "$E=mc^2$" in result
    block = _format_markdown("$$\nx + y\n$$\n")
    assert "$$" in block
    assert "x + y" in block


def test_format_markdown_content_preserves_block_math_inside_blockquote() -> None:
    source = "---\n\n> $$\n> x^{5+y}=\\frac{x+y_6}{\\sqrt{x+\\frac{1}{x}}}\n> $$\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == source
    assert "> >" not in result


def test_format_markdown_content_preserves_indentation_in_block_math() -> None:
    source = (
        "$$\n"
        "\\def\\arraystretch{1.5}\n"
        "   \\begin{array}{c:c:c}\n"
        "   a & b & c \\\\ \\hline\n"
        "   d & e & f \\\\\n"
        "   \\hdashline\n"
        "   g & h & i\n"
        "\\end{array}\n"
        "$$\n\n"
        "$$\n"
        "M=\\begin{bmatrix}\n"
        "  1 & 2 & 1 \\\\\n"
        "  3 & 0 & 1 \\\\\n"
        "  0 & 2 & 4\n"
        "\\end{bmatrix}\n"
        "$$\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == source


def test_format_markdown_content_preserves_empty_block_math() -> None:
    source = "$$\n\n$$\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == source


def test_format_markdown_content_preserves_tight_empty_block_math() -> None:
    source = "$$\n$$\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == source


def test_format_sample_fixture() -> None:
    before = _read_fixture("format_sample__before.md")
    result = _format_markdown(before)
    assert "[[wiki link]]" in result
    assert "$E=mc^2$" in result
    assert "| a   | b   |" in result
    assert "| 1   | 2   |" in result
    assert "# Title" in result


def test_format_markdown_content_repairs_double_crlf_line_endings() -> None:
    source = "---\r\r\nauthor: Anton Sergienko\r\r\nlang: en\r\r\n---\r\r\n\r\r\n# Title\r\r\n\r\r\n## Sub\r\r\n"
    result = _format_markdown(source)
    assert "author: Anton Sergienko" in result
    assert "mailto:" not in result
    assert "\n\n\n" not in result.replace("\r", "")
    assert "# Title\r\n\r\n## Sub" in result or "# Title\n\n## Sub" in result.replace("\r\n", "\n")


def test_format_markdown_content_preserves_paragraph_blank_lines() -> None:
    source = (
        "# The MIT License\n\n"
        "Copyright © 2024-present Sergienko Anton\n\n"
        "Permission is hereby granted, free of charge.\n\n"
        "The above copyright notice.\n\n"
        'THE SOFTWARE IS PROVIDED "AS IS".\n'
    )
    result = _format_markdown(source)
    assert "Anton\r\n\r\nPermission" in result
    assert "charge.\r\n\r\nThe above" in result
    assert "notice.\r\n\r\nTHE SOFTWARE" in result


def test_format_markdown_content_preserves_single_newline_paragraph() -> None:
    source = "Первый абзац.\nВторой абзац.\n"
    result = _format_markdown(source)
    assert "Первый абзац.\r\nВторой абзац." in result
    assert "Первый абзац.\r\n\r\nВторой абзац." not in result


def test_read_markdown_text_handles_r_double_crlf_on_disk(tmp_path: Path) -> None:
    source = "# Title\n\n## Sub\n"
    path = tmp_path / "note.md"
    path.write_bytes(source.replace("\n", "\r\r\n").encode("utf-8"))
    result = _format_markdown(MarkdownFormatter.read_markdown_text(path))
    assert result.count("\r\r\n") == 0
    assert "# Title\r\n\r\n## Sub" in result


def test_markdown_formatter_callable_reuses_options() -> None:
    formatter = MarkdownFormatter(end_of_line="lf")
    assert formatter("# One\n") == "# One\n"
    assert formatter("# Two\n") == "# Two\n"
    assert formatter("# Three\n") == formatter.format("# Three\n")


def test_format_markdown_file(tmp_path: Path) -> None:
    source = tmp_path / "note.md"
    source.write_text("# Title\n\n", encoding="utf-8")
    message = MarkdownFormatter().format_file(source)
    assert "applied" in message or "not changed" in message


def test_format_markdown_folder(tmp_path: Path) -> None:
    (tmp_path / "one.md").write_text("# One\n", encoding="utf-8")
    (tmp_path / "two.md").write_text("# Two\n", encoding="utf-8")
    result = MarkdownFormatter().format_folder(tmp_path)
    assert "one.md" in result or "applied" in result.lower() or "not changed" in result.lower()


def test_format_markdown_content_preserves_code_block_lines() -> None:
    source = (
        "```powershell\n"
        '$src = (Resolve-Path ".\\vscode\\harrix-notes-explorer-hsk").Path\n'
        '$dst = "$env:USERPROFILE\\.vscode-insiders\\extensions\\harrix-notes-explorer-hsk"\n'
        "if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }\n"
        "Copy-Item -LiteralPath $src -Destination $dst -Recurse\n"
        "```\n"
    )
    result = _format_markdown(source)
    assert '$src = (Resolve-Path ".\\vscode\\harrix-notes-explorer-hsk").Path' in result
    assert "Remove-Item -LiteralPath $dst -Force -Recurse }\r\nCopy-Item" in result
    assert "Remove-Item -LiteralPath $dst -Force -Recurse }\r\n\r\nCopy-Item" not in result


def test_format_markdown_content_preserves_blank_lines_inside_code_block() -> None:
    source = "```powershell\n$a = 1\n\n\n$b = 2\n```\n"
    result = _format_markdown(source)
    assert "$a = 1\r\n\r\n\r\n$b = 2" in result


def test_format_markdown_content_formats_loose_list_with_multiple_paragraphs() -> None:
    source = (
        "**How to run the `.ps1` file**\n\n- Первый абзац.\n\n  Второй абзац.\n\n- From `cmd.exe`: same `-File` line.\n"
    )
    result = _format_markdown(source)
    assert "Первый абзац.\r\n\r\n  Второй абзац." in result
    assert "Второй абзац.\r\n\r\n- From `cmd.exe`" in result


def test_format_markdown_content_formats_loose_list_with_code_block() -> None:
    source = (
        "**How to run the `.ps1` file**\n\n"
        "- From PowerShell in repo root (recommended if execution policy blocks scripts):\n\n"
        "  ```powershell\n"
        "  powershell -NoProfile -ExecutionPolicy Bypass -File .\\install\\harrix-swiss-knife.ps1\n"
        "  ```\n\n"
        "- From `cmd.exe`: same `-File` line.\n"
    )
    result = _format_markdown(source)
    assert "blocks scripts):\r\n\r\n  ```powershell" in result
    assert "harrix-swiss-knife.ps1\r\n  ```\r\n\r\n- From `cmd.exe`" in result
    assert "powershell -NoProfile -ExecutionPolicy Bypass -File .\\install\\harrix-swiss-knife.ps1" in result


def test_format_markdown_content_preserves_python_indentation_in_code_block() -> None:
    source = (
        "```python\n"
        "def tag_local_name(tag: str | bytes | bytearray | etree.QName) -> str:\n"
        "    if isinstance(tag, etree.QName):\n"
        "        return tag.localname\n"
        "    tag_str = tag.decode() if isinstance(tag, bytes | bytearray) else str(tag)\n"
        '    if "}" in tag_str:\n'
        '        return tag_str.rsplit("}", 1)[-1]\n'
        "    return tag_str\n"
        "```\n"
    )
    result = _format_markdown(source)
    assert "def tag_local_name(tag: str | bytes | bytearray | etree.QName) -> str:" in result
    assert "    if isinstance(tag, etree.QName):" in result
    assert "        return tag.localname" in result
    assert "if isinstance(tag, etree.QName):\r\nreturn tag.localname" not in result


def test_format_markdown_content_no_extra_trailing_blank_after_details() -> None:
    source = (
        "<details>\n"
        "<summary>Code:</summary>\n\n"
        "```python\n"
        "def tag_local_name() -> str:\n"
        "    return tag_str\n"
        "```\n\n"
        "</details>\n"
    )
    result = _format_markdown(source)
    assert result.endswith("</details>\r\n")
    assert not result.endswith("</details>\r\n\r\n")


def test_format_markdown_content_preserves_unindented_list_item_continuation() -> None:
    source = (
        "Args:\n\n"
        "- `project_root` (`Path | str | None`): Root directory of the project for relative path calculation.\n"
        "If `None`, will try to find git root or use current working directory. Defaults to `None`.\n"
    )
    result = _format_markdown(source)
    assert (
        "calculation.\r\n  If `None`, will try to find git root or use current working directory. Defaults to `None`."
        in result
    )
    assert "calculation.\r\n\r\nIf `None`" not in result


def test_format_markdown_content_indents_list_item_soft_break() -> None:
    source = (
        "2. Create a personal access token when it is generated — if you lose it, you will have to\n"
        "regenerate the token.\n"
    )
    result = _format_markdown(source)
    assert "you will have to\r\n   regenerate the token." in result

    long_source = (
        "224. Create a personal access token when it is generated — if you lose it, you will have to\n"
        "regenerate the token.\n"
    )
    long_result = _format_markdown(long_source)
    assert "you will have to\r\n     regenerate the token." in long_result

    bullet_source = "- Пример.\nПереод строки.\n"
    bullet_result = _format_markdown(bullet_source)
    assert "- Пример.\r\n  Переод строки." in bullet_result


def test_format_markdown_content_escapes_emphasis_like_characters() -> None:
    source = (
        "к сверхмассивной чёрной дыре Стрелец А* в центре Млечного Пути\n"
        "Все исключения поддерживают метод what() , который возвращает строку типа char* с описанием.\n"
        "Вариант 3: имена типов дополняются префиксом «t_»\n"
    )
    result = _format_markdown(source)
    assert "Стрелец А\\* в центре" in result
    assert "char\\* с описанием" in result
    assert "«t\\_»" in result


def test_format_markdown_content_does_not_escape_spaced_multiplication() -> None:
    source = "The result is 5 * 2 for simple math.\n"
    result = _format_markdown(source)
    assert "5 * 2" in result
    assert "5 \\* 2" not in result


def test_format_markdown_content_keeps_mid_word_underscores() -> None:
    source = "Use foo_bar_baz in code.\n"
    result = _format_markdown(source)
    assert "foo_bar_baz" in result
    assert "foo\\_bar" not in result


def test_format_markdown_content_keeps_prettier_literal_identifiers() -> None:
    source = (
        r"Oculus\Software\hyperbolic-magnetism-beat-saber\Beat Saber_Data" + "\n"
        r"- `list[list[Any]]`: List of process habits records [_id, habit_name, value, date]." + "\n"
        "2. _[directory_name].short.g.md\n"
        "Use foo_bar_baz in code.\n"
    )
    result = _format_markdown(source)
    assert r"Oculus\Software\hyperbolic-magnetism-beat-saber\Beat Saber_Data" in result
    assert r"[\_id, habit_name" in result
    assert "_[directory_name].short.g.md" in result
    assert "foo_bar_baz" in result
    assert "\\\\Software" not in result


def test_format_markdown_content_escapes_identifier_underscores() -> None:
    source = (
        "Table save handlers are provided by _get_save_handlers(); _auto_save_row\n"
        "- `table_name` (`str`): Name of the table to delete from. Must be in _SAFE_TABLES.\n"
        "- `monthly_data` (`list`): Monthly data from _get_monthly_data_for_exercise.\n"
        "Return a path in folder that does not exist, using base_name and suffix with _1, _2 if needed.\n"
        "If folder contains aggregated file _<FolderName>.g.md (e.g. Fiction -> _Fiction.g.md),\n"
        "Inline code keeps literals: `_<FolderName>.g.md` and `_Fiction.g.md`.\n"
        "В Windows все наборы инструментов определяют макрос _WIN32.\n"
        "t._id, t.amount\n"
    )
    result = _format_markdown(source)
    assert "\\_get_save_handlers" in result
    assert "\\_auto_save_row" in result
    assert "\\_SAFE_TABLES" in result
    assert "\\_get_monthly_data_for_exercise" in result
    assert "\\_1, \\_2" in result
    assert "\\_<FolderName>.g.md" in result
    assert "-> \\_Fiction.g.md" in result
    assert "`_<FolderName>.g.md`" in result
    assert "`_Fiction.g.md`" in result
    assert "\\_WIN32" in result
    assert "t.\\_id, t.amount" in result


def test_format_markdown_content_keeps_tight_list_with_nested_sublist() -> None:
    source = (
        "- [Class `StyleSheet`](#class)\n\n"
        "  - [Method `_init__`](#init)\n"
        "  - [Method `collect`](#collect)\n\n"
        "- [Function `_format_style`](#func)\n"
    )
    result = _format_markdown(source)
    assert "- [Class `StyleSheet`](#class)\r\n  - [Method `_init__`]" in result
    assert "collect`](#collect)\r\n- [Function `_format_style`]" in result
    assert "StyleSheet`](#class)\r\n\r\n  - [Method" not in result
    assert "collect]\r\n\r\n- [Function" not in result


def test_format_markdown_content_keeps_tight_simple_list() -> None:
    source = "- one\n- two\n"
    result = _format_markdown(source)
    assert "- one\r\n- two" in result
    assert "- one\r\n\r\n- two" not in result


def test_format_markdown_content_collapses_redundant_inline_spaces() -> None:
    source = (
        "- after opening guillemet « (direct speech, e.g. «Ваша задача);  # ignore: HP001\n"
        "- after dash at line start (dialogue, e.g. — Ваша работа хороша).  # ignore: HP001\n"
    )
    result = _format_markdown(source)
    assert ");  # ignore" not in result
    assert "); # ignore: HP001" in result
    assert ").  # ignore" not in result
    assert "). # ignore: HP001" in result


def test_format_markdown_content_preserves_table_cell_spacing() -> None:
    source = "| a  b | x |\n| --- | --- |\n"
    result = _format_markdown(source)
    assert "a  b" in result


def test_format_markdown_content_trims_trailing_blank_line_after_list() -> None:
    source = (
        "## CLI commands\n\n"
        "CLI commands after installation.\n\n"
        "- `uv self update` — update uv itself.\n"
        "- `uv sync --upgrade` — update all project libraries.\n\n"
    )
    result = _format_markdown(source).replace("\r\n", "\n")
    assert result.endswith("- `uv sync --upgrade` — update all project libraries.\n")
    assert not result.endswith("- `uv sync --upgrade` — update all project libraries.\n\n")


def test_format_markdown_content_trims_trailing_blank_line_inside_fenced_block() -> None:
    source = (
        "````markdown\n"
        "## CLI commands\n\n"
        "- `uv self update` — update uv itself.\n"
        "- `uv sync --upgrade` — update all project libraries.\n\n"
        "````\n"
    )
    result = _format_markdown(source).replace("\r\n", "\n")
    assert result.endswith("- `uv sync --upgrade` — update all project libraries.\n````\n")
    assert "libraries.\n\n````" not in result


def test_format_markdown_content_keeps_blank_line_in_empty_fenced_block() -> None:
    source = "```\n```\n"
    result = _format_markdown(source).replace("\r\n", "\n")
    assert result == "```\n\n```\n"


def test_format_markdown_content_preserves_reference_comment_inside_fenced_block() -> None:
    source = '```markdown\n[//]: # "Hidden comment"\n```\n'
    result = _format_markdown(source, end_of_line="lf")
    assert result == source
    assert "```markdown [//]:" not in result


def test_format_markdown_content_preserves_github_alerts() -> None:
    source = (
        "> [!NOTE]\n"
        "> Information the user should notice even if skimming.\n"
        "\n"
        "> [!TIP]\n"
        "> Optional information to help a user be more successful.\n"
        "\n"
        "> [!IMPORTANT]\n"
        "> Essential information required for user success.\n"
        "\n"
        "> [!CAUTION]\n"
        "> Negative potential consequences of an action.\n"
        "\n"
        "> [!WARNING]\n"
        "> Dangerous certain consequences of an action.\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == source
    assert "> [!NOTE] Information" not in result


def test_format_markdown_content_preserves_github_alerts_inside_fenced_markdown_block() -> None:
    source = (
        "```markdown\n"
        "> [!NOTE]\n"
        "> Information the user should notice even if skimming.\n"
        "\n"
        "> [!TIP]\n"
        "> Optional information to help a user be more successful.\n"
        "```\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == source
    assert "> [!NOTE] Information" not in result


def test_format_markdown_content_preserves_blank_line_between_blockquote_paragraphs() -> None:
    source = "> The first paragraph in the quote.\n>\n> The second paragraph in the quote.\n"
    result = _format_markdown(source).replace("\r\n", "\n")
    assert result == ("> The first paragraph in the quote.\n>\n> The second paragraph in the quote.\n")


def test_format_markdown_content_preserves_escaped_ordered_list_like_line_start_in_blockquote() -> None:
    source = (
        "> В этом абзаце 39. означает номер фрагмента, а не элемент списка.\n"
        ">\n"
        "> 39\\. Первый фрагмент текста. 40. Второй фрагмент. 41. Третий фрагмент.\n"
    )
    result = _format_markdown(source).replace("\r\n", "\n")
    assert "> 39\\. Первый фрагмент текста. 40. Второй фрагмент. 41. Третий фрагмент." in result
    assert "> 39. Первый фрагмент" not in result


def test_format_markdown_content_preserves_ordered_list_in_blockquote() -> None:
    source = (
        "> Вводный абзац перед списком.\n"
        ">\n"
        "> 1. Первый пункт списка.\n"
        "> 2. Второй пункт списка.\n"
        "> 3. Третий пункт списка.\n"
        ">\n"
        "> Заключительный абзац после списка.\n"
    )
    result = _format_markdown(source).replace("\r\n", "\n")
    assert "> 1. Первый пункт списка.\n" in result
    assert "> 2. Второй пункт списка.\n" in result
    assert "> 3. Третий пункт списка.\n" in result
    assert "> 1\\. Первый" not in result
    assert "> 2\\. Второй" not in result


def test_format_markdown_content_preserves_blank_line_before_attribution_after_blockquote_list() -> None:
    source = (
        "> 1. Ошибки репликации наследуются (проходят через циклы репликации).\n"
        "> 2. Существует обратная связь между генотипом и фенотипом: некоторые ошибки репликации "
        "влияют на эффективность и точность репликации как отрицательно, так и положительно.\n"
        ">\n"
        "> -- _Author Name, Book Title_\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == source
    assert ">\n> -- _Author Name" in result


def test_format_markdown_content_preserves_ordered_list_after_blockquote_item_continuation() -> None:
    source = (
        "> 1. First item.\n"
        "> 2. Second item.\n"
        "> 3. Third item.\n"
        "> 4. Fourth item.\n"
        "> 5. Fifth item.\n"
        "> 6. Sixth item.\n"
        "> 7. Seventh item starts here.\n"
        ">\n"
        ">    Seventh item continues on the next line.\n"
        "> 8. Eighth item.\n"
        "> 9. Ninth item.\n"
        "> 10. Tenth item.\n"
        ">\n"
        "> -- _Source A_\n"
        "\n"
        "---\n"
        "\n"
        "> Intro paragraph before the next list.\n"
        ">\n"
        "> Section title\n"
        ">\n"
        "> 1. Alpha point.\n"
        "> 2. Beta point.\n"
        "> 3. Gamma point.\n"
        ">\n"
        "> -- _Source B_\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert "> 10. Tenth item.\n" in result
    assert "> 1. Alpha point.\n" in result
    assert "> 2. Beta point.\n" in result
    assert "> 3. Gamma point.\n" in result
    assert "> 8. Alpha" not in result
    assert "> 9. Beta" not in result


def test_format_markdown_content_preserves_blank_lines_in_blockquote_list_item_paragraphs() -> None:
    source = (
        "> 1. Opening paragraph of the first item.\n"
        ">\n"
        ">    Indented continuation of the first item.\n"
        ">\n"
        "> 2. Second item paragraph.\n"
    )
    result = _format_markdown(source, end_of_line="lf")
    assert result == source


def test_format_markdown_content_keeps_decimal_ratings_in_bullet_list_items() -> None:
    source = "- 10 - Транс\n- 7,5 - Чудеса\n- 9.5 - Тихоокеанский рубеж\n- 9,5 - Воображариум\n"
    result = _format_markdown(source).replace("\r\n", "\n")
    assert "- 9.5 - Тихоокеанский рубеж\n" in result
    assert "- 9\\.5 -" not in result


def test_format_markdown_content_renders_hard_breaks_with_backslash() -> None:
    source = "У лукоморья дуб зелёный;\\\nЗлатая цепь на дубе том:\\\nИ днём и ночью кот учёный\\\n"
    result = _format_markdown(source).replace("\r\n", "\n")
    assert result == source
    assert "  \n" not in result

    two_space_source = "line one  \nline two\n"
    two_space_result = _format_markdown(two_space_source).replace("\r\n", "\n")
    assert two_space_result == "line one  \nline two\n"


def test_format_markdown_content_preserves_trailing_backslash_in_fenced_text_block() -> None:
    path_line = "C:\\Users\\Default\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\\n"
    source = "```text\n" + path_line + "```\n"
    result = _format_markdown(source).replace("\r\n", "\n")
    assert path_line in result
    assert "Programs  \n" not in result


def test_format_markdown_content_preserves_backslash_in_fenced_python_comments() -> None:
    source = (
        "```python\n"
        "from pathlib import Path\n"
        "\n"
        "p = Path('C:\\Program Files\\Internet Explorer\\iexplore.exe')\n"
        "print(p.name)  # iexplore.exe\n"
        "print(p.suffix)  # .exe\n"
        "print(p.suffixes)  # ['.exe']\n"
        "print(p.drive)  # C:\n"
        "print(p.stem)  # iexplore\n"
        "print(p.anchor)  # \\\n"
        "print(p.root)  # \\\n"
        "print(p.parts)  # ('C:\\\\', 'Program Files', 'Internet Explorer', 'iexplore.exe')\n"
        "```\n"
    )
    result = _format_markdown(source).replace("\r\n", "\n")
    assert "print(p.anchor)  # \\\n" in result
    assert "print(p.root)  # \\\n" in result
    assert "print(p.anchor)  #   \n" not in result
    assert "print(p.root)  #   \n" not in result


def test_format_markdown_content_preserves_trailing_space_in_inline_code_before_text() -> None:
    source = "`cd .. ` — go to parent folder\n"
    result = _format_markdown(source, end_of_line="lf")
    assert result == source
    assert "` cd ..  `" not in result
