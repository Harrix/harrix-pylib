"""Tests for markdown formatting."""

from __future__ import annotations

from pathlib import Path

import harrix_pylib as h
from harrix_pylib.md_format.formatter import format_markdown_content, read_markdown_text
from harrix_pylib.md_format.front_matter import prepend_markdown_header
from harrix_pylib.md_format.table_format import text_display_width


def _read_fixture(name: str) -> str:
    path = Path(__file__).parent / "data" / "md_format" / name
    return path.read_text(encoding="utf-8")


def test_format_markdown_content_uses_crlf_by_default() -> None:
    result = format_markdown_content("# Title\n\n")
    assert "\r\n" in result
    assert result.endswith("\r\n")


def test_format_markdown_content_preserves_wiki_link() -> None:
    result = format_markdown_content("[[A simple wiki link]]\n")
    assert "[[A simple wiki link]]" in result


def test_format_markdown_content_preserves_angle_autolink() -> None:
    source = "GitHub: <https://github.com/Harrix/harrix-pylib>\n"
    result = format_markdown_content(source)
    assert "GitHub: <https://github.com/Harrix/harrix-pylib>" in result
    assert "[https://github.com/Harrix/harrix-pylib]" not in result


def test_format_markdown_content_preserves_named_link() -> None:
    source = "GitHub: [harrix-pylib](https://github.com/Harrix/harrix-pylib)\n"
    result = format_markdown_content(source)
    assert "[harrix-pylib](https://github.com/Harrix/harrix-pylib)" in result


def test_format_markdown_content_preserves_email_autolink() -> None:
    source = "Email: <user@example.com>\n"
    result = format_markdown_content(source)
    assert "Email: <user@example.com>" in result
    assert "[user@example.com](mailto:user@example.com)" not in result


def test_format_markdown_content_formats_bare_domain_as_angle_autolink() -> None:
    source = "| Site | www.msi.com |\n| --- | --- |\n"
    result = format_markdown_content(source)
    assert "<www.msi.com>" in result
    assert "[www.msi.com](http://www.msi.com)" not in result


def test_format_markdown_content_preserves_named_link_with_different_text() -> None:
    source = "Site: [MSI website](http://www.msi.com)\n"
    result = format_markdown_content(source)
    assert "[MSI website](http://www.msi.com)" in result
    assert "<www.msi.com>" not in result


def test_format_markdown_content_preserves_front_matter() -> None:
    source = "---\nhello: world\n---\n\n# Title\n"
    result = format_markdown_content(source)
    assert "---\r\nhello: world\r\n---" in result
    assert "# Title" in result


def test_prepend_markdown_header_strips_existing_front_matter() -> None:
    header = "---\nlang: en\n---"
    source = "---\nlang: ru\n---\n\n# Title\n"
    result = prepend_markdown_header(header, source)
    assert result.startswith("---\nlang: en\n---\n\n# Title")
    assert result.count("---") == 2  # noqa: PLR2004


def test_format_markdown_content_formats_lists() -> None:
    result = format_markdown_content("- one\n- two\n")
    assert "- one" in result
    assert "- two" in result


def test_format_markdown_content_formats_italic_with_underscores() -> None:
    for source in ("*No docstring provided.*\n", "_No docstring provided._\n"):
        result = format_markdown_content(source)
        assert "_No docstring provided._" in result
        assert "*No docstring provided.*" not in result


def test_format_markdown_content_preserves_cyrillic_link_fragments() -> None:
    source = (
        "- [Жареная картошка](#жареная-картошка)\n"
        "- [Заклинание «Соль-вода!» против ос и пчёл](#заклинание-соль-вода-против-ос-и-пчёл)\n"  # noqa: RUF001
    )
    result = format_markdown_content(source)
    assert "[Жареная картошка](#жареная-картошка)" in result
    assert (
        "[Заклинание «Соль-вода!» против ос и пчёл](#заклинание-соль-вода-против-ос-и-пчёл)"  # noqa: RUF001
        in result
    )
    assert "%D0" not in result


def test_format_markdown_content_preserves_inline_code_with_backticks() -> None:
    source = "`` `\\n`$1`:` ``\n"
    result = format_markdown_content(source)
    assert "`` `\\n`$1`:` ``" in result


def test_format_markdown_content_preserves_escaped_pipe_in_table_inline_code() -> None:
    source = "| Col1 | Col2 |\n| --- | --- |\n| `a\\|b` | Соответствует a или b |\n"
    result = format_markdown_content(source)
    assert "`a\\|b`" in result
    assert "| `a|b` |" not in result


def test_format_markdown_content_keeps_unescaped_pipe_in_inline_code_outside_table() -> None:
    source = "Use `a|b` in text.\n"
    result = format_markdown_content(source)
    assert "`a|b`" in result
    assert "`a\\|b`" not in result


def test_format_markdown_content_formats_nested_lists() -> None:
    source = "- [List](#list)\n    - [File a](#a)\n    - [File b](#b)\n"
    result = format_markdown_content(source)
    assert "  - [File a](#a)" in result
    assert "    - [File a]" not in result
    assert "  - [File b](#b)" in result


def test_format_markdown_content_inserts_blank_line_after_list() -> None:
    source = (
        "- Git discard commands — use `git` directly\n"
        "- Note titles, preview copy, drag-and-drop, folder expansion, etc.\n"
        "`NotesProvider._templateTargets` remain in `extension.js`.\n"
    )
    result = format_markdown_content(source)
    assert "etc.\r\n\r\n`NotesProvider" in result


def test_format_markdown_content_preserves_blank_line_after_list() -> None:
    source = "- one\n- two\n\nParagraph after list.\n"
    result = format_markdown_content(source)
    assert "- two\r\n\r\nParagraph after list." in result


def test_format_markdown_content_formats_tables() -> None:
    result = format_markdown_content("|a|b|\n|---|---|\n|1|2|\n")
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
    result = format_markdown_content(source)
    assert (
        "| File                 | Config key                               | "
        "Purpose                                    |" in result
    )
    assert (
        "| -------------------- | ---------------------------------------- | "
        "------------------------------------------ |" in result
    )


def test_format_markdown_content_keeps_paragraph_after_table() -> None:
    source = (
        "| File | Config key | Purpose |\n"
        "| --- | --- | --- |\n"
        "| row1 | key1 | purpose1 |\n"
        "For school/corporate Wi-Fi, set optional `bothub.proxy`.\n"
        "Paths in `config.json` use the `snippet:api-keys/...` prefix.\n"
    )
    result = format_markdown_content(source)
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
    result = format_markdown_content(source)
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
    result = format_markdown_content(source)
    table_lines = [line for line in result.splitlines() if line.strip().startswith("|")]
    assert len(table_lines) == 4  # noqa: PLR2004
    assert any("_format_style" in line and line.strip().endswith("|") for line in table_lines)
    col1_widths = [text_display_width(line.split("|")[1]) for line in table_lines]
    assert len(set(col1_widths)) == 1


def test_format_markdown_content_formats_math() -> None:
    result = format_markdown_content("$E=mc^2$\n")
    assert "$E=mc^2$" in result
    block = format_markdown_content("$$\nx + y\n$$\n")
    assert "$$" in block
    assert "x + y" in block


def test_format_sample_fixture() -> None:
    before = _read_fixture("format_sample__before.md")
    result = format_markdown_content(before)
    assert "[[wiki link]]" in result
    assert "$E=mc^2$" in result
    assert "| a   | b   |" in result
    assert "| 1   | 2   |" in result
    assert "# Title" in result


def test_format_markdown_content_repairs_double_crlf_line_endings() -> None:
    source = "---\r\r\nauthor: Anton Sergienko\r\r\nlang: en\r\r\n---\r\r\n\r\r\n# Title\r\r\n\r\r\n## Sub\r\r\n"
    result = format_markdown_content(source)
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
    result = format_markdown_content(source)
    assert "Anton\r\n\r\nPermission" in result
    assert "charge.\r\n\r\nThe above" in result
    assert "notice.\r\n\r\nTHE SOFTWARE" in result


def test_format_markdown_content_preserves_single_newline_paragraph() -> None:
    source = "Первый абзац.\nВторой абзац.\n"  # noqa: RUF001
    result = format_markdown_content(source)
    assert "Первый абзац.\r\nВторой абзац." in result  # noqa: RUF001
    assert "Первый абзац.\r\n\r\nВторой абзац." not in result  # noqa: RUF001


def test_read_markdown_text_handles_r_double_crlf_on_disk(tmp_path: Path) -> None:
    source = "# Title\n\n## Sub\n"
    path = tmp_path / "note.md"
    path.write_bytes(source.replace("\n", "\r\r\n").encode("utf-8"))
    result = format_markdown_content(read_markdown_text(path))
    assert result.count("\r\r\n") == 0
    assert "# Title\r\n\r\n## Sub" in result


def test_format_markdown_file(tmp_path: Path) -> None:
    source = tmp_path / "note.md"
    source.write_text("# Title\n\n", encoding="utf-8")
    message = h.md.format_markdown(source)
    assert "applied" in message or "not changed" in message


def test_format_markdown_folder(tmp_path: Path) -> None:
    (tmp_path / "one.md").write_text("# One\n", encoding="utf-8")
    (tmp_path / "two.md").write_text("# Two\n", encoding="utf-8")
    result = h.md.format_markdown_folder(tmp_path)
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
    result = format_markdown_content(source)
    assert '$src = (Resolve-Path ".\\vscode\\harrix-notes-explorer-hsk").Path' in result
    assert "Remove-Item -LiteralPath $dst -Force -Recurse }\r\nCopy-Item" in result
    assert "Remove-Item -LiteralPath $dst -Force -Recurse }\r\n\r\nCopy-Item" not in result


def test_format_markdown_content_preserves_blank_lines_inside_code_block() -> None:
    source = "```powershell\n$a = 1\n\n\n$b = 2\n```\n"
    result = format_markdown_content(source)
    assert "$a = 1\r\n\r\n\r\n$b = 2" in result


def test_format_markdown_content_formats_loose_list_with_multiple_paragraphs() -> None:
    source = (
        "**How to run the `.ps1` file**\n\n- Первый абзац.\n\n  Второй абзац.\n\n- From `cmd.exe`: same `-File` line.\n"
    )
    result = format_markdown_content(source)
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
    result = format_markdown_content(source)
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
    result = format_markdown_content(source)
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
    result = format_markdown_content(source)
    assert result.endswith("</details>\r\n")
    assert not result.endswith("</details>\r\n\r\n")


def test_format_markdown_content_preserves_unindented_list_item_continuation() -> None:
    source = (
        "Args:\n\n"
        "- `project_root` (`Path | str | None`): Root directory of the project for relative path calculation.\n"
        "If `None`, will try to find git root or use current working directory. Defaults to `None`.\n"
    )
    result = format_markdown_content(source)
    assert (
        "calculation.\r\nIf `None`, will try to find git root or use current working directory. Defaults to `None`."
        in result
    )
    assert "calculation.\r\n\r\nIf `None`" not in result
    assert "calculation.\r\n  If `None`" not in result


def test_format_markdown_content_keeps_tight_list_with_nested_sublist() -> None:
    source = (
        "- [Class `StyleSheet`](#class)\n\n"
        "  - [Method `__init__`](#init)\n"
        "  - [Method `collect`](#collect)\n\n"
        "- [Function `_format_style`](#func)\n"
    )
    result = format_markdown_content(source)
    assert "- [Class `StyleSheet`](#class)\r\n  - [Method `__init__`]" in result
    assert "collect`](#collect)\r\n- [Function `_format_style`]" in result
    assert "StyleSheet`](#class)\r\n\r\n  - [Method" not in result
    assert "collect]\r\n\r\n- [Function" not in result


def test_format_markdown_content_keeps_tight_simple_list() -> None:
    source = "- one\n- two\n"
    result = format_markdown_content(source)
    assert "- one\r\n- two" in result
    assert "- one\r\n\r\n- two" not in result
