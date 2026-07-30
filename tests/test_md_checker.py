"""Tests for the MdChecker class."""

from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h

EXPECTED_H007_ERRORS = 2


def test_md_checker() -> None:
    """Test MdChecker for all rules and scenarios."""
    checker = h.md_check.MdChecker()

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # =====================================================================
        # H001: Space in filename  # noqa: ERA001
        # =====================================================================
        file_with_space = temp_path / "file name.md"
        file_with_space.write_text("---\nlang: en\n---\n# Test", encoding="utf-8")
        errors = checker.check(file_with_space)
        assert any("H001" in error for error in errors)

        # =====================================================================
        # H002: Space in path  # noqa: ERA001
        # =====================================================================
        space_dir = temp_path / "folder with space"
        space_dir.mkdir()
        file_in_space_path = space_dir / "file.md"
        file_in_space_path.write_text("---\nlang: en\n---\n# Test", encoding="utf-8")
        errors = checker.check(file_in_space_path)
        assert any("H002" in error for error in errors)

        # =====================================================================
        # H003: Missing YAML
        # =====================================================================
        no_yaml_file = temp_path / "no_yaml.md"
        no_yaml_file.write_text("# Just content without YAML", encoding="utf-8")
        errors = checker.check(no_yaml_file)
        assert any("H003" in error for error in errors)

        # H003 is ignored for README.md and LICENSE.md
        readme_file = temp_path / "README.md"
        readme_file.write_text("# Project README", encoding="utf-8")
        errors = checker.check(readme_file, select={"H003"})
        assert not any("H003" in error for error in errors)

        license_file = temp_path / "LICENSE.md"
        license_file.write_text("# The MIT License", encoding="utf-8")
        errors = checker.check(license_file, select={"H003"})
        assert not any("H003" in error for error in errors)

        # =====================================================================
        # H004: Missing lang field in YAML
        # =====================================================================
        no_lang_file = temp_path / "no_lang.md"
        no_lang_file.write_text("---\ntitle: Test\n---\n# Content", encoding="utf-8")
        errors = checker.check(no_lang_file)
        assert any("H004" in error for error in errors)

        # =====================================================================
        # H005: Invalid lang value
        # =====================================================================
        invalid_lang_file = temp_path / "invalid_lang.md"
        invalid_lang_file.write_text("---\nlang: fr\n---\n# Content", encoding="utf-8")
        errors = checker.check(invalid_lang_file)
        assert any("H005" in error for error in errors)

        # =====================================================================
        # H006: Incorrect word forms
        # =====================================================================

        # Test lowercase markdown
        lowercase_md_file = temp_path / "lowercase.md"
        lowercase_md_file.write_text("---\nlang: en\n---\n# Test markdown content", encoding="utf-8")
        errors = checker.check(lowercase_md_file)
        assert any("H006" in error for error in errors)
        assert any("Markdown" in error for error in errors)

        # Test LaTeX variations
        latex_file = temp_path / "latex_test.md"
        latex_file.write_text("---\nlang: en\n---\n# Using latex and Latex", encoding="utf-8")
        errors = checker.check(latex_file)
        assert any("H006" in error and "latex" in error for error in errors)

        # Test tech terms (HTML, CSS, PHP, etc.)
        tech_file = temp_path / "tech_test.md"
        tech_file.write_text("---\nlang: en\n---\nFile formats: html, css, pdf, svg, xml", encoding="utf-8")
        errors = checker.check(tech_file)
        assert any("H006" in error for error in errors)
        assert len([e for e in errors if "H006" in e]) >= 5  # noqa: PLR2004

        # Test programming languages
        lang_file = temp_path / "lang_test.md"
        lang_file.write_text("---\nlang: en\n---\nLanguages: c++, java, javascript, pascal", encoding="utf-8")
        errors = checker.check(lang_file)
        assert any("H006" in error and "c++" in error for error in errors)
        assert any("H006" in error and "java" in error for error in errors)

        # Test GitHub and Git
        git_file = temp_path / "git_test.md"
        git_file.write_text("---\nlang: en\n---\nUse Github and git", encoding="utf-8")
        errors = checker.check(git_file)
        assert any("H006" in error and "Github" in error for error in errors)
        assert any("H006" in error and "git" in error for error in errors)

        # Test Russian phrases
        ru_file = temp_path / "ru_test.md"
        ru_file.write_text("---\nlang: ru\n---\nЭто web приложение и web документ", encoding="utf-8")
        errors = checker.check(ru_file)
        assert any("H006" in error for error in errors)

        # Test Russian abbreviations without spaces (т.е., т.д., т.ч., т.п.)  # noqa: RUF003
        ru_abbrev_file = temp_path / "ru_abbrev.md"
        ru_abbrev_file.write_text(
            "---\nlang: ru\n---\n\nТо есть т.е. и т.д. правильно писать т. е. и т. д.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_abbrev_file, select={"H006"})
        assert any("H006" in e and "т.е." in e for e in errors)
        assert any("H006" in e and "т.д." in e for e in errors)

        # Multi-part spaced abbreviations from JSON database (H006)
        ru_abbrev_multipart_file = temp_path / "ru_abbrev_multipart.md"
        ru_abbrev_multipart_file.write_text(
            "---\nlang: ru\n---\n\nВключая в т.ч. единицы а.е.м. и форму г.н.с.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_abbrev_multipart_file, select={"H006"})
        assert any("H006" in e and "в т.ч." in e for e in errors)
        assert any("H006" in e and "а.е.м." in e for e in errors)

        # Spaced canonical forms should not trigger H006; lang must not gate abbrev checks
        ru_abbrev_ok_file = temp_path / "ru_abbrev_ok.md"
        ru_abbrev_ok_file.write_text(
            "---\nlang: en\n---\n\nПишем т. е., в т. ч. и а. е. м. правильно.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_abbrev_ok_file, select={"H006"})
        assert not errors

        # Test that code blocks are ignored
        code_block_file = temp_path / "code_block_test.md"
        code_block_file.write_text(
            "---\nlang: en\n---\n# Test\n```python\nmarkdown = 'test'\nhtml = 'code'\n```\nOutside code",
            encoding="utf-8",
        )
        errors = checker.check(code_block_file)
        assert not any("markdown" in error and "```" in str(code_block_file.read_text()) for error in errors)

        # Test that indented code blocks inside list items are ignored (H006)
        indented_code_block_file = temp_path / "indented_code_block_test.md"
        indented_code_block_file.write_text(
            "---\nlang: en\n---\n"
            "2. Restart PowerShell and clone projects:\n\n"
            "   ```shell\n"
            "   git clone https://github.com/Harrix/harrix-pylib.git\n"
            "   ```\n",
            encoding="utf-8",
        )
        errors = checker.check(indented_code_block_file, select={"H006"})
        assert not any("H006" in error for error in errors)

        # Test that inline code is ignored
        inline_code_file = temp_path / "inline_code_test.md"
        inline_code_file.write_text(
            "---\nlang: en\n---\nUse `markdown` in code, but markdown outside", encoding="utf-8"
        )
        errors = checker.check(inline_code_file)
        markdown_errors = [e for e in errors if "H006" in e and "markdown" in e]
        assert len(markdown_errors) == 1

        # Test that URLs in markdown links and angle brackets are ignored
        url_test_file = temp_path / "url_test.md"
        url_test_file.write_text(
            "---\nlang: en\n---\n"
            "[GnuPG](https://gpg4win.org/download.html) and <https://example.com/test.html>\n"
            "But html outside URL should be caught",
            encoding="utf-8",
        )
        errors = checker.check(url_test_file)
        html_errors = [e for e in errors if "H006" in e and "html" in e]
        assert len(html_errors) == 1
        assert any(":5:" in e for e in html_errors)

        # Test that identifier-like link labels are ignored (e.g. package names)
        package_link_file = temp_path / "package_link_test.md"
        package_link_file.write_text(
            "---\nlang: en\n---\n"
            "Markdown processor: [markdown-it-py](https://pypi.org/project/markdown-it-py) "
            "<https://pypistats.org/packages/markdown-it-py>.\n",
            encoding="utf-8",
        )
        errors = checker.check(package_link_file, select={"H006"})
        assert not any("H006" in error for error in errors)

        # Test that prose link text is still checked
        prose_link_file = temp_path / "prose_link_test.md"
        prose_link_file.write_text(
            "---\nlang: en\n---\n[see markdown guide](https://example.com)\n",
            encoding="utf-8",
        )
        errors = checker.check(prose_link_file, select={"H006"})
        assert any("H006" in error and "markdown" in error for error in errors)

        # Test that hyphenated identifiers are ignored (e.g. markdown-it, git-diff-friendly)
        hyphenated_id_file = temp_path / "hyphenated_id_test.md"
        hyphenated_id_file.write_text(
            "---\nlang: en\n---\n"
            "Return a quoted title that markdown-it can parse before rendering.\n"
            "Return whether ordered list markers should use git-diff-friendly `1.` suffixes.\n",
            encoding="utf-8",
        )
        errors = checker.check(hyphenated_id_file, select={"H006"})
        assert not any("H006" in error for error in errors)

        # Test valid file with no errors
        valid_file = temp_path / "valid.md"
        valid_file.write_text(
            "---\nlang: en\n---\n# Test Markdown content with HTML, CSS, PDF, JavaScript, C++, GitHub, Git\n",
            encoding="utf-8",
        )
        errors = checker.check(valid_file)
        assert len(errors) == 0

        # Test exclude_rules functionality
        file_with_issues = temp_path / "file with issues.md"
        file_with_issues.write_text("---\nlang: fr\n---\n# Test markdown", encoding="utf-8")

        all_errors = checker.check(file_with_issues)
        assert len(all_errors) > 0

        excluded_errors = checker.check(file_with_issues, exclude_rules={"H001", "H005", "H006"})
        assert len(excluded_errors) < len(all_errors)

        # Test __call__ method
        call_errors = checker(file_with_issues)
        assert call_errors == all_errors

        call_excluded_errors = checker(file_with_issues, exclude_rules={"H001"})
        assert len(call_excluded_errors) < len(all_errors)

        select_errors = checker.check(file_with_issues, select={"H001", "H002"})
        assert all("H001" in e or "H002" in e for e in select_errors)
        assert not any("H005" in e or "H006" in e for e in select_errors)

        only_h001 = checker.check(file_with_issues, select={"H001"})
        assert all("H001" in e for e in only_h001)
        assert len(only_h001) > 0

        select_with_invalid = checker.check(file_with_issues, select={"H001", "H999"})
        assert all("H001" in e for e in select_with_invalid)
        assert not any("H999" in e for e in select_with_invalid)

        combined_errors = checker.check(file_with_issues, select={"H001", "H002", "H005"}, exclude_rules={"H005"})
        assert all("H001" in e or "H002" in e for e in combined_errors)
        assert not any("H005" in e or "H006" in e for e in combined_errors)

        call_select_errors = checker(file_with_issues, select={"H001"})
        assert all("H001" in e for e in call_select_errors)

        # Test YAML parsing error
        invalid_yaml_file = temp_path / "invalid_yaml.md"
        invalid_yaml_file.write_text("---\nlang: en\ninvalid: yaml: content\n---\n# Content", encoding="utf-8")
        errors = checker.check(invalid_yaml_file)
        assert any("YAML" in error for error in errors)

        # Test with Path object
        path_obj_errors = checker.check(Path(valid_file))
        assert len(path_obj_errors) == 0

        # Test with string path
        string_path_errors = checker.check(str(valid_file))
        assert len(string_path_errors) == 0

        # =====================================================================
        # H007: Incorrect code block language identifiers
        # =====================================================================
        code_lang_file = temp_path / "code_lang_test.md"
        code_lang_file.write_text(
            (
                "---\nlang: en\n---\n"
                "# Code blocks\n"
                "```console\n$ echo test\n```\n"
                "```py\nprint('test')\n```\n"
                "```shell\n$ echo correct\n```\n"
                "```python\nprint('correct')\n```"
            ),
            encoding="utf-8",
        )
        errors = checker.check(code_lang_file)
        h007_errors = [e for e in errors if "H007" in e]
        assert len(h007_errors) == EXPECTED_H007_ERRORS
        assert any("console" in error and "shell" in error for error in h007_errors)
        assert any("py" in error and "python" in error for error in h007_errors)

        h007_only_errors = checker.check(code_lang_file, select={"H007"})
        assert len(h007_only_errors) == EXPECTED_H007_ERRORS
        assert all("H007" in error for error in h007_only_errors)

        no_h007_errors = checker.check(code_lang_file, exclude_rules={"H007"})
        assert not any("H007" in error for error in no_h007_errors)

        # Code blocks without language should not trigger H007
        no_lang_code_file = temp_path / "no_lang_code.md"
        no_lang_code_file.write_text(
            "---\nlang: en\n---\n# Code without language\n```\nJust text\n```", encoding="utf-8"
        )
        errors = checker.check(no_lang_code_file, select={"H007"})
        assert len(errors) == 0

        # =====================================================================
        # H008: Trailing whitespace
        # =====================================================================
        trailing_ws_file = temp_path / "trailing_ws.md"
        trailing_ws_file.write_text(
            "---\nlang: en\n---\n\nLine with trailing space   \nNormal line\n", encoding="utf-8"
        )
        errors = checker.check(trailing_ws_file, select={"H008"})
        assert any("H008" in e for e in errors)

        # No trailing whitespace — no error
        clean_ws_file = temp_path / "clean_ws.md"
        clean_ws_file.write_text("---\nlang: en\n---\n\nClean line\n", encoding="utf-8")
        errors = checker.check(clean_ws_file, select={"H008"})
        assert not errors

        # =====================================================================
        # H009: Double spaces
        # =====================================================================
        double_space_file = temp_path / "double_space.md"
        double_space_file.write_text("---\nlang: en\n---\n\nLine with  double spaces.\n", encoding="utf-8")
        errors = checker.check(double_space_file, select={"H009"})
        assert any("H009" in e for e in errors)

        # List indentation with two spaces should not trigger H009
        list_indent_file = temp_path / "list_indent.md"
        list_indent_file.write_text("---\nlang: en\n---\n\n* Item\n  * Nested item\n", encoding="utf-8")
        errors = checker.check(list_indent_file, select={"H009"})
        assert not errors

        # Inline code must not create false H009 (clean_line would have "  " at junction)
        inline_code_no_double_file = temp_path / "inline_code_no_double.md"
        inline_code_no_double_file.write_text(
            "---\nlang: en\n---\n\nWe select the layout of the screen `Free` and form it ourselves as we need.:\n",
            encoding="utf-8",
        )
        errors = checker.check(inline_code_no_double_file, select={"H009"})
        assert not [e for e in errors if "H009" in e], "H009 must not fire for line with inline code only"

        # Double spaces only inside inline code must not trigger H009
        double_inside_code_file = temp_path / "double_inside_code.md"
        double_inside_code_file.write_text(
            "---\nlang: en\n---\n\nStacked tails (`# noqa: RUF001  # ignore: HP001`) are removed.\n",
            encoding="utf-8",
        )
        errors = checker.check(double_inside_code_file, select={"H009"})
        assert not [e for e in errors if "H009" in e], "H009 must ignore double spaces inside inline code"

        # =====================================================================
        # H010: Tab character
        # =====================================================================
        tab_file = temp_path / "tab_test.md"
        tab_file.write_text("---\nlang: en\n---\n\nLine with\ttab.\n", encoding="utf-8")
        errors = checker.check(tab_file, select={"H010"})
        assert any("H010" in e for e in errors)

        # Tab inside code block (e.g. TSV/CSV example) should not trigger H010
        tab_in_code_file = temp_path / "tab_in_code.md"
        tab_in_code_file.write_text(
            "---\nlang: ru\n---\n\n```text\nМороженое\tFood\t494 ₽\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(tab_in_code_file, select={"H010"})
        assert not errors

        # =====================================================================
        # H011: No empty line at end of file
        # =====================================================================
        no_newline_file = temp_path / "no_newline.md"
        no_newline_file.write_text("---\nlang: en\n---\n\nContent without newline at end", encoding="utf-8")
        errors = checker.check(no_newline_file, select={"H011"})
        assert any("H011" in e for e in errors)

        # File with empty line at end should not trigger H011
        with_newline_file = temp_path / "with_newline.md"
        with_newline_file.write_text("---\nlang: en\n---\n\nContent with newline at end\n", encoding="utf-8")
        errors = checker.check(with_newline_file, select={"H011"})
        assert not errors

        # =====================================================================
        # H012: Two consecutive empty lines
        # =====================================================================
        double_empty_file = temp_path / "double_empty.md"
        double_empty_file.write_text("---\nlang: en\n---\n\nParagraph 1\n\n\nParagraph 2\n", encoding="utf-8")
        errors = checker.check(double_empty_file, select={"H012"})
        assert any("H012" in e for e in errors)

        # Single empty line should not trigger H012
        single_empty_file = temp_path / "single_empty.md"
        single_empty_file.write_text("---\nlang: en\n---\n\nParagraph 1\n\nParagraph 2\n", encoding="utf-8")
        errors = checker.check(single_empty_file, select={"H012"})
        assert not errors

        # Two consecutive empty lines inside code block should not trigger H012
        code_block_double_empty_file = temp_path / "code_block_double_empty.md"
        code_block_double_empty_file.write_text(
            "---\nlang: en\n---\n\nText\n\n```python\ndef a():\n    pass\n\n\ndef b():\n    pass\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(code_block_double_empty_file, select={"H012"})
        assert not errors

        # =====================================================================
        # H013: Missing colon before code block
        # =====================================================================
        no_colon_code_file = temp_path / "no_colon_code.md"
        no_colon_code_file.write_text(
            "---\nlang: en\n---\n\nHere is the code.\n\n```python\nprint('hello')\n```\n", encoding="utf-8"
        )
        errors = checker.check(no_colon_code_file, select={"H013"})
        assert any("H013" in e for e in errors)

        # Colon before code block should not trigger H013
        colon_code_file = temp_path / "colon_code.md"
        colon_code_file.write_text(
            "---\nlang: en\n---\n\nHere is the code:\n\n```python\nprint('hello')\n```\n", encoding="utf-8"
        )
        errors = checker.check(colon_code_file, select={"H013"})
        assert not errors

        # Admonition before code block should not trigger H013
        admonition_code_file = temp_path / "admonition_code.md"
        admonition_code_file.write_text(
            "---\nlang: en\n---\n\nText [!NOTE]\n\n```python\nprint('hello')\n```\n", encoding="utf-8"
        )
        errors = checker.check(admonition_code_file, select={"H013"})
        assert not errors

        # Bold heading with colon before code block should not trigger H013
        bold_colon_code_file = temp_path / "bold_colon_code.md"
        bold_colon_code_file.write_text(
            "---\nlang: en\n---\n\n**From an already-cloned repo:**\n\n```powershell\n.\\install\\script.ps1\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(bold_colon_code_file, select={"H013"})
        assert not errors

        # Display math block before code block should not trigger H013
        math_before_code_file = temp_path / "math_before_code.md"
        math_before_code_file.write_text(
            "---\nlang: en\n---\n\n"
            "```latex\n"
            "\\left( \\begin{array}{ccc}\n"
            "a & b & c \\\\\n"
            "d & e & f \\\\\n"
            "g & h & i\n"
            "\\end{array} \\right)\n"
            "```\n\n"
            "$$\n"
            "\\left( \\begin{array}{ccc}\n"
            "a & b & c \\\\\n"
            "d & e & f \\\\\n"
            "g & h & i\n"
            "\\end{array} \\right)\n"
            "$$\n\n"
            "```latex\n"
            "\\begin{Bmatrix}\n"
            "2\\\\\n"
            "3\\\\\n"
            "\\end{Bmatrix}\n"
            "```\n",
            encoding="utf-8",
        )
        errors = checker.check(math_before_code_file, select={"H013"})
        assert not errors

        # Single-line display math before code block should not trigger H013
        single_line_math_code_file = temp_path / "single_line_math_code.md"
        single_line_math_code_file.write_text(
            "---\nlang: en\n---\n\n$$x = 1$$\n\n```python\nprint(x)\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(single_line_math_code_file, select={"H013"})
        assert not errors

        # Horizontal rule before code block should not trigger H013
        hr_before_code_file = temp_path / "hr_before_code.md"
        hr_before_code_file.write_text(
            "---\nlang: en\n---\n\n---\n\n```cpp\nbool value = true;\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(hr_before_code_file, select={"H013"})
        assert not errors

        # Alternative horizontal rule markers before code block should not trigger H013
        hr_stars_before_code_file = temp_path / "hr_stars_before_code.md"
        hr_stars_before_code_file.write_text(
            "---\nlang: en\n---\n\n***\n\n```cpp\nbool value = true;\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(hr_stars_before_code_file, select={"H013"})
        assert not errors

        # Figure caption before next code sample must not require colon (H013)
        caption_before_code_file = temp_path / "caption_before_code.md"
        caption_before_code_file.write_text(
            "---\nlang: ru\n---\n\n"
            "Пример кнопки:\n\n"
            "```html\n[button]Кнопка[/button]\n```\n\n"
            "![Кнопка маленькая](img/button-small.png)\n\n"
            "_Рисунок 26 — Кнопка маленькая_\n\n"
            '```html\n[button size="medium"]Кнопка[/button]\n```\n',
            encoding="utf-8",
        )
        errors = checker.check(caption_before_code_file, select={"H013"})
        assert not [e for e in errors if "H013" in e], "H013 must not fire on figure captions before code"

        # List item before code block must not require colon (H013)
        list_before_code_file = temp_path / "list_before_code.md"
        list_before_code_file.write_text(
            "---\nlang: ru\n---\n\n"
            "Пример ненумерованного списка:\n\n"
            "- Пункт 1\n"
            "- Пункт 2\n"
            "- Пункт 3\n\n"
            "```markdown\n"
            "Пример нумерованного списка:\n\n"
            "1. Пункт 1\n"
            "2. Пункт 2\n"
            "3. Пункт 3\n"
            "```\n",
            encoding="utf-8",
        )
        errors = checker.check(list_before_code_file, select={"H013"})
        assert not [e for e in errors if "H013" in e], "H013 must not require colon after list before code"

        ordered_list_before_code_file = temp_path / "ordered_list_before_code.md"
        ordered_list_before_code_file.write_text(
            "---\nlang: en\n---\n\n1. First\n2. Second\n\n```python\nprint(1)\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(ordered_list_before_code_file, select={"H013"})
        assert not [e for e in errors if "H013" in e], "H013 must not require colon after ordered list"

        # =====================================================================
        # H014: Missing colon before image
        # =====================================================================
        no_colon_img_file = temp_path / "no_colon_img.md"
        no_colon_img_file.write_text(
            "---\nlang: en\n---\n\nHere is the image.\n\n![Alt](image.png)\n", encoding="utf-8"
        )
        errors = checker.check(no_colon_img_file, select={"H014"})
        assert any("H014" in e for e in errors)

        # Colon before image should not trigger H014
        colon_img_file = temp_path / "colon_img.md"
        colon_img_file.write_text("---\nlang: en\n---\n\nHere is the image:\n\n![Alt](image.png)\n", encoding="utf-8")
        errors = checker.check(colon_img_file, select={"H014"})
        assert not errors

        # Italic caption line before next image must not trigger H014 (caption belongs to previous image)
        caption_before_img_file = temp_path / "caption_before_img.md"
        caption_before_img_file.write_text(
            "---\nlang: en\n---\n\nText:\n\n![First](a.png)\n\n_Рисунок 1 — First_\n\n![Second](b.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(caption_before_img_file, select={"H014"})
        assert not [e for e in errors if "H014" in e], "H014 must not fire for italic caption line before image"

        # List item before image must not require colon (H014)
        list_before_img_file = temp_path / "list_before_img.md"
        list_before_img_file.write_text(
            "---\nlang: en\n---\n\n- Item one\n- Item two with `code` at end\n\n![Caption](img.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(list_before_img_file, select={"H014"})
        assert not [e for e in errors if "H014" in e], "H014 must not fire when line before image is list item (- )"

        # Badge/decorative images should not require colon before them (H014)
        badge_img_file = temp_path / "badge_img.md"
        badge_img_file.write_text(
            "---\nlang: en\n---\n\n"
            "This is a personal project.\n\n"
            "![GitHub](https://img.shields.io/badge/GitHub-repo-blue?logo=github)\n",
            encoding="utf-8",
        )
        errors = checker.check(badge_img_file, select={"H014"})
        assert not [e for e in errors if "H014" in e], "H014 must not fire before shields.io badge"

        multi_badge_file = temp_path / "multi_badge_img.md"
        multi_badge_file.write_text("---\nlang: en\n---\n\nText.\n\n![A](u1.png) ![B](u2.png)\n", encoding="utf-8")
        errors = checker.check(multi_badge_file, select={"H014"})
        assert not [e for e in errors if "H014" in e], "H014 must not fire before multi-badge row"

        # =====================================================================
        # H059: Missing colon before list
        # =====================================================================
        no_colon_list_file = temp_path / "no_colon_list.md"
        no_colon_list_file.write_text(
            "---\nlang: ru\n---\n\nМедицинские изделия и принадлежности\n\n- Вата\n",
            encoding="utf-8",
        )
        errors = checker.check(no_colon_list_file, select={"H059"})
        assert any("H059" in e for e in errors)

        colon_list_file = temp_path / "colon_list.md"
        colon_list_file.write_text(
            "---\nlang: ru\n---\n\nМедицинские изделия и принадлежности:\n\n- Вата\n",
            encoding="utf-8",
        )
        errors = checker.check(colon_list_file, select={"H059"})
        assert not errors

        heading_before_list_file = temp_path / "heading_before_list.md"
        heading_before_list_file.write_text(
            "---\nlang: en\n---\n\n## Supplies\n\n- Cotton\n",
            encoding="utf-8",
        )
        errors = checker.check(heading_before_list_file, select={"H059"})
        assert not errors

        image_before_list_file = temp_path / "image_before_list.md"
        image_before_list_file.write_text(
            "---\nlang: en\n---\n\n![Alt](image.png)\n\n- Item\n",
            encoding="utf-8",
        )
        errors = checker.check(image_before_list_file, select={"H059"})
        assert not errors

        # Table row before list must not require colon (H059)
        table_before_list_file = temp_path / "table_before_list.md"
        table_before_list_file.write_text(
            "---\nlang: en\n---\n\n| Name | Value |\n| ---- | ----- |\n| CPU  | i7    |\n\n- Item\n",
            encoding="utf-8",
        )
        errors = checker.check(table_before_list_file, select={"H059"})
        assert not [e for e in errors if "H059" in e], "H059 must not fire when line before list is table row"

        admonition_before_list_file = temp_path / "admonition_before_list.md"
        admonition_before_list_file.write_text(
            "---\nlang: en\n---\n\nText [!NOTE]\n\n- Item\n",
            encoding="utf-8",
        )
        errors = checker.check(admonition_before_list_file, select={"H059"})
        assert not errors

        list_before_list_file = temp_path / "list_before_list.md"
        list_before_list_file.write_text(
            "---\nlang: en\n---\n\n- Item one\n\n- Item two\n\n- Item three\n",
            encoding="utf-8",
        )
        errors = checker.check(list_before_list_file, select={"H059"})
        assert not [e for e in errors if "H059" in e], "H059 must not fire between blank-separated list items"

        # Multi-line list item (indented continuation) before blank + next item
        list_continuation_file = temp_path / "list_continuation.md"
        list_continuation_file.write_text(
            "---\nlang: en\n---\n\n- First item with\n  continuation text\n\n- Second item\n",
            encoding="utf-8",
        )
        errors = checker.check(list_continuation_file, select={"H059"})
        assert not [e for e in errors if "H059" in e], "H059 must not fire on list item continuations"

        # Figure caption before next list item must not trigger H059 (belongs to previous image)
        caption_before_list_file = temp_path / "caption_before_list.md"
        caption_before_list_file.write_text(
            "---\nlang: ru\n---\n\n"
            "- [minimap](https://example.com) — карта:\n\n"
            "![Пакет minimap](img/minimap.png)\n\n"
            "_Рисунок 1 — Пакет minimap_\n\n"
            "- [pigments](https://example.com) — цвета:\n",
            encoding="utf-8",
        )
        errors = checker.check(caption_before_list_file, select={"H059"})
        assert not [e for e in errors if "H059" in e], "H059 must not fire on figure captions before list"

        indented_caption_before_list_file = temp_path / "indented_caption_before_list.md"
        indented_caption_before_list_file.write_text(
            "---\nlang: ru\n---\n\n"
            "- [minimap](https://example.com) — карта:\n\n"
            "  ![Пакет minimap](img/minimap.png)\n\n"
            "  _Рисунок 1 — Пакет minimap_\n\n"
            "- [pigments](https://example.com) — цвета:\n",
            encoding="utf-8",
        )
        errors = checker.check(indented_caption_before_list_file, select={"H059"})
        assert not [e for e in errors if "H059" in e], "H059 must not fire on indented figure captions before list"

        # Sentence-ending period before list (docstring summary / D400) must not require colon
        period_before_list_file = temp_path / "period_before_list.md"
        period_before_list_file.write_text(
            "---\nlang: en\n---\n\n"
            "Generate two summary files for a directory of year-based Markdown files.\n"
            "\n"
            "1. `table.include.g.md` - A statistical table\n"
            "2. `_[directory_name].short.g.md` - A hierarchical list\n",
            encoding="utf-8",
        )
        errors = checker.check(period_before_list_file, select={"H059"})
        assert not [e for e in errors if "H059" in e], "H059 must allow period before list (D400)"

        no_colon_ordered_list_file = temp_path / "no_colon_ordered_list.md"
        no_colon_ordered_list_file.write_text(
            "---\nlang: en\n---\n\nHere are the steps\n\n1. First\n",
            encoding="utf-8",
        )
        errors = checker.check(no_colon_ordered_list_file, select={"H059"})
        assert any("H059" in e for e in errors)

        bold_colon_list_file = temp_path / "bold_colon_list.md"
        bold_colon_list_file.write_text(
            "---\nlang: en\n---\n\n**Supplies:**\n\n- Cotton\n",
            encoding="utf-8",
        )
        errors = checker.check(bold_colon_list_file, select={"H059"})
        assert not errors

        # =====================================================================
        # H015: Space before punctuation
        # =====================================================================
        space_punct_file = temp_path / "space_punct.md"
        space_punct_file.write_text(
            "---\nlang: en\n---\n\nThis is wrong .\nThis is also wrong ,here.\n", encoding="utf-8"
        )
        errors = checker.check(space_punct_file, select={"H015"})
        assert any("H015" in e for e in errors)
        assert len([e for e in errors if "H015" in e]) >= 2  # noqa: PLR2004

        # Check each punctuation case
        for i, (punct, content) in enumerate(
            [
                (" ,", "---\nlang: en\n---\n\nWrong ,comma.\n"),
                (" ;", "---\nlang: en\n---\n\nWrong ;semicolon.\n"),
                (" :", "---\nlang: en\n---\n\nWrong :colon.\n"),
                (" ?", "---\nlang: en\n---\n\nWrong ?question.\n"),
            ]
        ):
            p_file = temp_path / f"punct_{i}.md"
            p_file.write_text(content, encoding="utf-8")
            errors = checker.check(p_file, select={"H015"})
            assert any("H015" in e for e in errors), f"Expected H015 for '{punct}'"

        # Colon immediately after inline code must not trigger H015 (no real space in source)
        inline_code_colon_file = temp_path / "inline_code_colon.md"
        inline_code_colon_file.write_text("---\nlang: en\n---\n\nIn `Categories`:\n", encoding="utf-8")
        errors = checker.check(inline_code_colon_file, select={"H015"})
        assert not [e for e in errors if "H015" in e], "H015 must not fire for `code`: (colon after backtick)"

        # Space before punctuation inside inline code must not trigger H015
        inline_code_dot_file = temp_path / "inline_code_dot.md"
        inline_code_dot_file.write_text("---\nlang: en\n---\n\n- `cd ..`: go\n", encoding="utf-8")
        errors = checker.check(inline_code_dot_file, select={"H015"})
        assert not [e for e in errors if "H015" in e], "H015 must not fire for space+dot inside `code`"

        # Space before dot in file extension should not trigger H015
        file_ext_file = temp_path / "file_ext_dot.md"
        file_ext_file.write_text(
            "---\nlang: en\n---\n\n  - 💎 ★ Beautify MD and regenerate .g.md in … ꟲᴸᴵ\n",
            encoding="utf-8",
        )
        errors = checker.check(file_ext_file, select={"H015"})
        assert not [e for e in errors if "H015" in e], "H015 must not fire for regenerate .g.md"

        # Space before dot at end of sentence should still trigger H015
        wrong_dot_file = temp_path / "wrong_dot.md"
        wrong_dot_file.write_text("---\nlang: en\n---\n\nThis is wrong .\n", encoding="utf-8")
        errors = checker.check(wrong_dot_file, select={"H015"})
        assert any("H015" in e and " ." in e for e in errors)

        # Space before text emoticons must not trigger H015
        for i, content in enumerate(
            [
                "---\nlang: ru\n---\n\nВ этом :) Вообще.\n",
                "---\nlang: en\n---\n\nHello ;) world.\n",
                "---\nlang: en\n---\n\nGreat :-D news.\n",
                "---\nlang: en\n---\n\nSad :( day.\n",
                "---\nlang: en\n---\n\nWink ;-P now.\n",
            ]
        ):
            emoticon_file = temp_path / f"emoticon_{i}.md"
            emoticon_file.write_text(content, encoding="utf-8")
            errors = checker.check(emoticon_file, select={"H015"})
            assert not [e for e in errors if "H015" in e], f"H015 must not fire for emoticon in: {content!r}"

        # Real space before colon/semicolon punctuation must still trigger H015
        wrong_colon_still_file = temp_path / "wrong_colon_still.md"
        wrong_colon_still_file.write_text("---\nlang: en\n---\n\nWrong :colon.\n", encoding="utf-8")
        errors = checker.check(wrong_colon_still_file, select={"H015"})
        assert any("H015" in e for e in errors)

        # GFM table alignment colons must not trigger H015
        table_align_file = temp_path / "table_align.md"
        table_align_file.write_text(
            "---\nlang: ru\n---\n\n"
            "| Слева   |    По центру     | Справа |\n"
            "| ------- | :--------------: | -----: |\n"
            "| Телефон | Длинное значение |  $1600 |\n",
            encoding="utf-8",
        )
        errors = checker.check(table_align_file, select={"H015"})
        assert not [e for e in errors if "H015" in e], "H015 must not fire for GFM table alignment"

        # =====================================================================
        # H016: Incorrect dash/hyphen usage
        # =====================================================================
        hyphen_file = temp_path / "hyphen_test.md"
        hyphen_file.write_text("---\nlang: en\n---\n\nThis - is wrong hyphen.\n", encoding="utf-8")
        errors = checker.check(hyphen_file, select={"H016"})
        assert any("H016" in e for e in errors)

        # Correct em dash with spaces should not trigger H016
        emdash_file = temp_path / "emdash_test.md"
        emdash_file.write_text("---\nlang: en\n---\n\nThis — is correct.\n", encoding="utf-8")
        errors = checker.check(emdash_file, select={"H016"})
        assert not errors

        # En dash between digits should not trigger H016
        endash_digits_file = temp_path / "endash_digits.md"
        endash_digits_file.write_text("---\nlang: en\n---\n\nRange is 1–10 pages.\n", encoding="utf-8")
        errors = checker.check(endash_digits_file, select={"H016"})
        assert not errors

        # En dash NOT between digits should trigger H016
        endash_wrong_file = temp_path / "endash_wrong.md"
        endash_wrong_file.write_text("---\nlang: en\n---\n\nWord–word is wrong.\n", encoding="utf-8")
        errors = checker.check(endash_wrong_file, select={"H016"})
        assert any("H016" in e for e in errors)

        # H016 must NOT trigger in YAML front matter
        yaml_hyphen_file = temp_path / "yaml_hyphen.md"
        yaml_hyphen_file.write_text(
            "---\ntags: notebook - ноутбук\nauthor: Anton\n---\n\nBody text here.\n",
            encoding="utf-8",
        )
        errors = checker.check(yaml_hyphen_file, select={"H016"})
        assert not any("H016" in e for e in errors), "H016 must not apply to YAML lines"

        # H016 must NOT trigger inside code blocks
        code_hyphen_file = temp_path / "code_hyphen.md"
        code_hyphen_file.write_text(
            "---\nlang: en\n---\n\nParagraph.\n\n```\noption - value\n```\n\nMore text.\n",
            encoding="utf-8",
        )
        errors = checker.check(code_hyphen_file, select={"H016"})
        assert not any("H016" in e for e in errors), "H016 must not apply to code block lines"

        # H016 must NOT trigger inside inline code
        inline_code_hyphen_file = temp_path / "inline_code_hyphen.md"
        inline_code_hyphen_file.write_text(
            "---\nlang: en\n---\n\nUse `cmd - flag` in shell.\n",
            encoding="utf-8",
        )
        errors = checker.check(inline_code_hyphen_file, select={"H016"})
        assert not any("H016" in e for e in errors), "H016 must not apply to inline code"

        # H016 must NOT trigger inside LaTeX math
        math_hyphen_file = temp_path / "math_hyphen.md"
        math_hyphen_file.write_text(
            "---\nlang: en\n---\n\n$$\n1 - x^{2}\n$$\n\nInline $a - b$.\n",
            encoding="utf-8",
        )
        errors = checker.check(math_hyphen_file, select={"H016"})
        assert not any("H016" in e for e in errors), "H016 must not apply inside LaTeX math"

        # H016 must NOT trigger for " - " inside table cell that is only hyphen (e.g. | - |)
        table_dash_cell_file = temp_path / "table_dash_cell.md"
        table_dash_cell_file.write_text(
            "---\nlang: en\n---\n\n| A | B |\n| --- | --- |\n| foo | - |\n",
            encoding="utf-8",
        )
        errors = checker.check(table_dash_cell_file, select={"H016"})
        assert not any("H016" in e for e in errors), "H016 must not fire for hyphen-only table cell"

        # Double hyphen " -- " should trigger H016
        double_hyphen_file = temp_path / "double_hyphen.md"
        double_hyphen_file.write_text("---\nlang: en\n---\n\nDash -- here.\n", encoding="utf-8")
        errors = checker.check(double_hyphen_file, select={"H016"})
        assert any("H016" in e and " -- " in e for e in errors)

        # Blockquote attribution "--" should not trigger H016
        blockquote_attribution_file = temp_path / "blockquote_attribution.md"
        blockquote_attribution_file.write_text(
            "---\nlang: ru\n---\n\n"
            "> Более того, нельзя запретить пытливым умам думать.\n"
            ">\n"
            "> -- _Хокинг Стивен, Черные дыры и молодые вселенные_\n",
            encoding="utf-8",
        )
        errors = checker.check(blockquote_attribution_file, select={"H016"})
        assert not any("H016" in e for e in errors), "H016 must not fire for blockquote attribution --"

        # Unicode minus " − " should trigger H016  # noqa: RUF003
        minus_sign_file = temp_path / "minus_sign.md"
        minus_sign_file.write_text("---\nlang: en\n---\n\nValue \u2212 5.\n", encoding="utf-8")
        errors = checker.check(minus_sign_file, select={"H016"})
        assert any("H016" in e for e in errors)

        # =====================================================================
        # H017: Three dots instead of ellipsis character
        # =====================================================================
        three_dots_file = temp_path / "three_dots.md"
        three_dots_file.write_text("---\nlang: en\n---\n\nWait for it...\n", encoding="utf-8")
        errors = checker.check(three_dots_file, select={"H017"})
        assert any("H017" in e for e in errors)

        # Correct ellipsis character should not trigger H017
        ellipsis_file = temp_path / "ellipsis.md"
        ellipsis_file.write_text("---\nlang: en\n---\n\nWait for it… and more.\n", encoding="utf-8")
        errors = checker.check(ellipsis_file, select={"H017"})
        assert not errors

        # Ellipsis at end of line is allowed
        ellipsis_eol_file = temp_path / "ellipsis_eol.md"
        ellipsis_eol_file.write_text("---\nlang: en\n---\n\n  - 🐍 New uv library in …\n", encoding="utf-8")
        errors = checker.check(ellipsis_eol_file, select={"H017"})
        assert not errors

        # Three dots inside code block should not trigger H017
        dots_in_code_file = temp_path / "dots_in_code.md"
        dots_in_code_file.write_text("---\nlang: en\n---\n\n```python\nresult = [...]\n```\n", encoding="utf-8")
        errors = checker.check(dots_in_code_file, select={"H017"})
        assert not errors

        # =====================================================================
        # H032: Two consecutive dots
        # =====================================================================
        two_dots_file = temp_path / "two_dots.md"
        two_dots_file.write_text("---\nlang: en\n---\n\nWait for it..\n", encoding="utf-8")
        errors = checker.check(two_dots_file, select={"H032"})
        assert any("H032" in e for e in errors)

        two_dots_mid_file = temp_path / "two_dots_mid.md"
        two_dots_mid_file.write_text("---\nlang: en\n---\n\nEnd of sentence.. Next sentence.\n", encoding="utf-8")
        errors = checker.check(two_dots_mid_file, select={"H032"})
        assert any("H032" in e for e in errors)

        # Three dots should trigger H017, not H032
        three_not_two_file = temp_path / "three_not_two.md"
        three_not_two_file.write_text("---\nlang: en\n---\n\nWait for it...\n", encoding="utf-8")
        errors = checker.check(three_not_two_file, select={"H032"})
        assert not errors

        # Rare Russian ?.. / !.. (H028) should not trigger H032
        qmark_two_dots_h032 = temp_path / "qmark_two_dots_h032.md"
        qmark_two_dots_h032.write_text(
            "---\nlang: ru\n---\n\n— Вот как?.. Ну и чему он у него учился?\n",
            encoding="utf-8",
        )
        errors = checker.check(qmark_two_dots_h032, select={"H032"})
        assert not errors

        bang_two_dots_h032 = temp_path / "bang_two_dots_h032.md"
        bang_two_dots_h032.write_text(
            "---\nlang: ru\n---\n\n— Вот так!.. И всё.\n",
            encoding="utf-8",
        )
        errors = checker.check(bang_two_dots_h032, select={"H032"})
        assert not errors

        # Parent-directory path ../ should not trigger H032
        parent_path_file = temp_path / "parent_path.md"
        parent_path_file.write_text("---\nlang: en\n---\n\nSee ../docs for details.\n", encoding="utf-8")
        errors = checker.check(parent_path_file, select={"H032"})
        assert not errors

        # Correct ellipsis should not trigger H032
        ellipsis_ok_file = temp_path / "ellipsis_ok_h032.md"
        ellipsis_ok_file.write_text("---\nlang: en\n---\n\nWait for it… and more.\n", encoding="utf-8")
        errors = checker.check(ellipsis_ok_file, select={"H032"})
        assert not errors

        # Two dots inside code / inline code should not trigger H032
        two_dots_code_file = temp_path / "two_dots_code.md"
        two_dots_code_file.write_text("---\nlang: en\n---\n\n```python\nx = range(1..10)\n```\n", encoding="utf-8")
        errors = checker.check(two_dots_code_file, select={"H032"})
        assert not errors

        two_dots_inline_file = temp_path / "two_dots_inline.md"
        two_dots_inline_file.write_text("---\nlang: en\n---\n\nUse `1..10` in code.\n", encoding="utf-8")
        errors = checker.check(two_dots_inline_file, select={"H032"})
        assert not errors

        # =====================================================================
        # H018: Curly/straight quotes instead of angle quotes
        # =====================================================================
        straight_quote_file = temp_path / "straight_quote.md"
        straight_quote_file.write_text(
            '---\nlang: ru\n---\n\nОн сказал "привет".\n',  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(straight_quote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        curly_quote_file = temp_path / "curly_quote.md"
        curly_quote_file.write_text(
            "---\nlang: ru\n---\n\nОн сказал \u201cпривет\u201d.\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(curly_quote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        # Space after « should trigger H018
        space_after_lquote_file = temp_path / "space_lquote.md"
        space_after_lquote_file.write_text(
            "---\nlang: ru\n---\n\nСказал « привет».\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(space_after_lquote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        # Space before » should trigger H018
        space_before_rquote_file = temp_path / "space_rquote.md"
        space_before_rquote_file.write_text(
            "---\nlang: ru\n---\n\nСказал «привет ».\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(space_before_rquote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        # Correct angle quotes should not trigger H018
        angle_quote_file = temp_path / "angle_quote.md"
        angle_quote_file.write_text("---\nlang: en\n---\n\nHe said «hello».\n", encoding="utf-8")
        errors = checker.check(angle_quote_file, select={"H018"})
        assert not errors

        # Straight quotes in line without Russian letters should not trigger H018
        straight_quote_en_file = temp_path / "straight_quote_en.md"
        straight_quote_en_file.write_text(
            '---\nlang: en\n---\n\nUse the one without "old" in the filename.\n',
            encoding="utf-8",
        )
        errors = checker.check(straight_quote_en_file, select={"H018"})
        assert not errors

        # Inch notation (e.g. 14", 15.6") should not trigger H018
        inch_quote_file = temp_path / "inch_quote.md"
        inch_quote_file.write_text(
            '---\nlang: ru\n---\n\n| ДИСПЛЕЙ | 14" FHD (1920×1080), IPS |\n',
            encoding="utf-8",
        )
        errors = checker.check(inch_quote_file, select={"H018"})
        assert not errors

        # =====================================================================
        # H019: HTML tags in markdown content
        # =====================================================================
        html_tag_file = temp_path / "html_tag.md"
        html_tag_file.write_text("---\nlang: en\n---\n\nThis is <strong>bold</strong> text.\n", encoding="utf-8")
        errors = checker.check(html_tag_file, select={"H019"})
        assert any("H019" in e for e in errors)

        # HTML in code block should not trigger H019
        html_in_code_file = temp_path / "html_in_code.md"
        html_in_code_file.write_text("---\nlang: en\n---\n\n```html\n<strong>Bold</strong>\n```\n", encoding="utf-8")
        errors = checker.check(html_in_code_file, select={"H019"})
        assert not errors

        # HTML-like content inside inline code should not trigger H019
        html_in_inline_code_file = temp_path / "html_in_inline_code.md"
        html_in_inline_code_file.write_text(
            "---\nlang: en\n---\n\nIn the file `resources.qrc` add line for example `<file>assets/logo.svg</file>`:\n",
            encoding="utf-8",
        )
        errors = checker.check(html_in_inline_code_file, select={"H019"})
        assert not errors

        # Check various forbidden HTML tags
        for tag in ["<table", "<h1", "<h2", "<h3", "<p>"]:
            html_file = temp_path / f"html_{tag.strip('<>').replace(' ', '_')}.md"
            html_file.write_text(f"---\nlang: en\n---\n\nContent {tag} here.\n", encoding="utf-8")
            errors = checker.check(html_file, select={"H019"})
            assert any("H019" in e for e in errors), f"Expected H019 for tag '{tag}'"

        # H019 exception: <details> and <summary> are allowed
        details_summary_file = temp_path / "details_summary.md"
        details_summary_file.write_text(
            "---\nlang: en\n---\n\n<details>\n<summary>Click to expand</summary>\n\nContent here.\n</details>\n",
            encoding="utf-8",
        )
        errors = checker.check(details_summary_file, select={"H019"})
        assert not any("H019" in e for e in errors), "H019 must not flag <details> and <summary>"

        # =====================================================================
        # H020: Image caption starts with lowercase
        # =====================================================================
        lower_caption_file = temp_path / "lower_caption.md"
        lower_caption_file.write_text("---\nlang: en\n---\n\n![lowercase caption](image.png)\n", encoding="utf-8")
        errors = checker.check(lower_caption_file, select={"H020"})
        assert any("H020" in e for e in errors)

        # Uppercase caption should not trigger H020
        upper_caption_file = temp_path / "upper_caption.md"
        upper_caption_file.write_text("---\nlang: en\n---\n\n![Uppercase caption](image.png)\n", encoding="utf-8")
        errors = checker.check(upper_caption_file, select={"H020"})
        assert not errors

        # Empty caption should not trigger H020
        empty_caption_file = temp_path / "empty_caption.md"
        empty_caption_file.write_text("---\nlang: en\n---\n\n![](image.png)\n", encoding="utf-8")
        errors = checker.check(empty_caption_file, select={"H020"})
        assert not errors

        # =====================================================================
        # H021: Lowercase letter after sentence-ending punctuation
        # =====================================================================
        lower_after_dot_file = temp_path / "lower_after_dot.md"
        lower_after_dot_file.write_text("---\nlang: en\n---\n\nFirst sentence. second sentence.\n", encoding="utf-8")
        errors = checker.check(lower_after_dot_file, select={"H021"})
        assert any("H021" in e for e in errors)

        # Uppercase after period should not trigger H021
        upper_after_dot_file = temp_path / "upper_after_dot.md"
        upper_after_dot_file.write_text("---\nlang: en\n---\n\nFirst sentence. Second sentence.\n", encoding="utf-8")
        errors = checker.check(upper_after_dot_file, select={"H021"})
        assert not errors

        # Abbreviation "e.g." should not trigger H021
        abbrev_file = temp_path / "abbrev_test.md"
        abbrev_file.write_text("---\nlang: en\n---\n\nFor example, e.g. this case.\n", encoding="utf-8")
        errors = checker.check(abbrev_file, select={"H021"})
        assert not errors

        # Russian abbreviations "т. д.", "т. е." should not trigger H021  # noqa: RUF003
        ru_abbrev_file = temp_path / "ru_abbrev_td_te.md"
        ru_abbrev_file.write_text(
            "---\nlang: ru\n---\n\nНачинкой (капустной, крапивной и т. д.) заливают. Используют т. е. так.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_abbrev_file, select={"H021"})
        assert not errors

        # Inline code between period and next word should not trigger H021
        inline_code_after_period_file = temp_path / "inline_code_after_period.md"
        inline_code_after_period_file.write_text(
            '---\nlang: en\n---\n\n- `path_layout` — Optional. `"city_note"` stores each entry.\n',
            encoding="utf-8",
        )
        errors = checker.check(inline_code_after_period_file, select={"H021"})
        assert not errors

        # Ordered list marker and section number should not trigger H021
        ordered_list_file = temp_path / "ordered_list_h021.md"
        ordered_list_file.write_text(
            "---\nlang: ru\n---\n\n1. код\n2. файл\n3. описание\n",
            encoding="utf-8",
        )
        errors = checker.check(ordered_list_file, select={"H021"})
        assert not errors

        section_number_file = temp_path / "section_number_h021.md"
        section_number_file.write_text(
            "---\nlang: ru\n---\n\nВ пункте 3.1. сказано, что нужно найти инструменты.\n",
            encoding="utf-8",
        )
        errors = checker.check(section_number_file, select={"H021"})
        assert not errors

        # Lowercase after a real sentence-ending period inside list item should trigger H021
        list_sentence_error_file = temp_path / "list_sentence_h021.md"
        list_sentence_error_file.write_text(
            "---\nlang: ru\n---\n\n1. Первое предложение. второе предложение.\n",
            encoding="utf-8",
        )
        errors = checker.check(list_sentence_error_file, select={"H021"})
        assert any("H021" in e for e in errors)

        # Language abbreviations should not trigger H021
        lang_abbrev_file = temp_path / "lang_abbrev_h021.md"
        lang_abbrev_file.write_text(
            "---\nlang: ru\n---\n\n"
            "Систематическая ошибка выжившего (англ. survivorship bias) — разновидность.\n"
            "(лат. аргумент к народу)\n"
            "см. также раздел ниже\n",
            encoding="utf-8",
        )
        errors = checker.check(lang_abbrev_file, select={"H021"})
        assert not errors

        # Expanded JSON abbreviations and English forms; lang must not gate checks
        expanded_abbrev_file = temp_path / "expanded_abbrev_h021.md"
        expanded_abbrev_file.write_text(
            "---\nlang: en\n---\n\nНапример напр. так. Работает г. н. с. сегодня. Also et al. said.\n",
            encoding="utf-8",
        )
        errors = checker.check(expanded_abbrev_file, select={"H021"})
        assert not errors

        # =====================================================================
        # H022: Non-breaking space
        # =====================================================================
        nbsp_file = temp_path / "nbsp_test.md"
        nbsp_file.write_text("---\nlang: en\n---\n\nText with\u00a0non-breaking space.\n", encoding="utf-8")
        errors = checker.check(nbsp_file, select={"H022"})
        assert any("H022" in e for e in errors)

        # Regular space should not trigger H022
        normal_space_file = temp_path / "normal_space.md"
        normal_space_file.write_text("---\nlang: en\n---\n\nText with normal space.\n", encoding="utf-8")
        errors = checker.check(normal_space_file, select={"H022"})
        assert not errors
        # =====================================================================
        # H023: Capitalized Russian polite pronoun (ru only)
        # =====================================================================
        ru_vy_file = temp_path / "ru_vy.md"
        ru_vy_file.write_text(
            "---\nlang: ru\n---\n\nОбращаемся к Вам с предложением.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_file, select={"H023"})
        assert any("H023" in e for e in errors)

        # "Вы" at sentence start is allowed (only flag mid-sentence)
        ru_vy_sentence_start_file = temp_path / "ru_vy_sentence_start.md"
        ru_vy_sentence_start_file.write_text(
            "---\nlang: ru\n---\n\nВы можете это увидеть.\n\nТут Вам не рады.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_sentence_start_file, select={"H023"})
        h023_errors = [e for e in errors if "H023" in e]
        assert len(h023_errors) == 1, "Exactly one H023 (Вам in middle), not Вы at start"
        assert "вам" in h023_errors[0].lower()

        # Lowercase "вы" should not trigger H023
        ru_vy_lower_file = temp_path / "ru_vy_lower.md"
        ru_vy_lower_file.write_text(
            "---\nlang: ru\n---\n\nОбращаемся к вам с предложением.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_lower_file, select={"H023"})
        assert not errors

        # lang: en with "Вы" should not trigger H023 (rule only for ru)
        en_vy_file = temp_path / "en_vy.md"
        en_vy_file.write_text("---\nlang: en\n---\n\nSome text with Вы.\n", encoding="utf-8")
        errors = checker.check(en_vy_file, select={"H023"})
        assert not errors

        # "Вы" inside inline code should not trigger H023
        ru_vy_code_file = temp_path / "ru_vy_code.md"
        ru_vy_code_file.write_text(
            "---\nlang: ru\n---\n\nUse variable `Вы` in code.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_code_file, select={"H023"})
        assert not errors

        # "Ваша" after « (direct speech) is sentence start — no H023
        ru_vy_guillemet_file = temp_path / "ru_vy_guillemet.md"
        ru_vy_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nВедущий говорит: «Ваша задача определить, сколько я показываю гаражей».\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_guillemet_file, select={"H023"})
        assert not errors

        # "Ваша" after dash at line start (dialogue) is sentence start — no H023
        ru_vy_dash_dialogue_file = temp_path / "ru_vy_dash_dialogue.md"
        ru_vy_dash_dialogue_file.write_text(
            "---\nlang: ru\n---\n\n— Ваша работа хороша.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_dash_dialogue_file, select={"H023"})
        assert not errors

        # Blockquote dialogue must not trigger H023
        ru_vy_blockquote_file = temp_path / "ru_vy_blockquote.md"
        ru_vy_blockquote_file.write_text(
            "---\nlang: ru\n---\n\n> — Вы в состоянии объяснить этот невероятный результат?\n>\n> -- _Лю Цысинь_\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_blockquote_file, select={"H023"})
        assert not errors

        # Pronoun inside «…» mid-speech must not trigger H023
        ru_vy_inside_guillemets_file = temp_path / "ru_vy_inside_guillemets.md"
        ru_vy_inside_guillemets_file.write_text(
            "---\nlang: ru\n---\n\nОн сказал: «Спасибо Вам за помощь».\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_inside_guillemets_file, select={"H023"})
        assert not errors

        # Pronoun at list-link / heading title start must not trigger H023
        ru_vy_toc_title_file = temp_path / "ru_vy_toc_title.md"
        ru_vy_toc_title_file.write_text(
            "---\nlang: ru\n---\n\n  - [Вам и не снилось...: 10](#вам-и-не-снилось-10)\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_toc_title_file, select={"H023"})
        assert not errors

        ru_vy_heading_file = temp_path / "ru_vy_heading.md"
        ru_vy_heading_file.write_text(
            "---\nlang: ru\n---\n\n## Вам сюда\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_heading_file, select={"H023"})
        assert not errors

        # Mid-sentence link text is still an address → H023
        ru_vy_mid_link_file = temp_path / "ru_vy_mid_link.md"
        ru_vy_mid_link_file.write_text(
            "---\nlang: ru\n---\n\nСмотрите [Ваш вариант](https://example.com).\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_mid_link_file, select={"H023"})
        assert any("H023" in e for e in errors)

        # =====================================================================
        # H024: Latin x or Cyrillic x instead of ×  # noqa: RUF003
        # =====================================================================
        x_instead_file = temp_path / "x_instead.md"
        x_instead_file.write_text(
            "---\nlang: ru\n---\n\nSize 5 x 10 cm.\n",
            encoding="utf-8",
        )
        errors = checker.check(x_instead_file, select={"H024"})
        assert any("H024" in e for e in errors)

        # x86 and x64 should not trigger H024
        x86_file = temp_path / "x86.md"
        x86_file.write_text("---\nlang: en\n---\n\nSupport x86 and x64.\n", encoding="utf-8")
        errors = checker.check(x86_file, select={"H024"})
        assert not errors

        # "2x Type-C", "1x USB" (digit + x + space) should not trigger H024
        digit_x_file = temp_path / "digit_x.md"
        digit_x_file.write_text(
            "---\nlang: en\n---\n\n2x Type-C, 1x USB, 1x Micro SD.\n",
            encoding="utf-8",
        )
        errors = checker.check(digit_x_file, select={"H024"})
        assert not errors

        # x inside inline code should not trigger H024
        x_code_file = temp_path / "x_code.md"
        x_code_file.write_text("---\nlang: en\n---\n\nUse `x` variable.\n", encoding="utf-8")
        errors = checker.check(x_code_file, select={"H024"})
        assert not errors

        # x inside link URL (e.g. resolution 3840x2160) should not trigger H024
        x_link_file = temp_path / "x_link.md"
        x_link_file.write_text(
            "---\nlang: ru\n---\n\n[Отзывы](https://market.yandex.ru/product--noutbuk-15-6-3840x2160/123).\n",
            encoding="utf-8",
        )
        errors = checker.check(x_link_file, select={"H024"})
        assert not errors

        # x followed by digit (e.g. PCIe x4, x16) should not trigger H024
        x4_file = temp_path / "x4.md"
        x4_file.write_text(
            "---\nlang: ru\n---\n\nNVMe, PCIe 4.0 x4.\n",
            encoding="utf-8",
        )
        errors = checker.check(x4_file, select={"H024"})
        assert not errors

        # x inside display/inline LaTeX math should not trigger H024
        x_math_file = temp_path / "x_math.md"
        x_math_file.write_text(
            "---\nlang: ru\n---\n\n$$\nz = x + y^{2x} \\tag{1}\n$$\n\nInline $z = x + y$ and $$a = x + b$$.\n",
            encoding="utf-8",
        )
        errors = checker.check(x_math_file, select={"H024"})
        assert not [e for e in errors if "H024" in e], "H024 must skip LaTeX math"

        # =====================================================================
        # H025: Image ![ not at start of line
        # =====================================================================
        image_not_start_file = temp_path / "image_not_start.md"
        image_not_start_file.write_text(
            "---\nlang: en\n---\n\nText ![alt](img.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(image_not_start_file, select={"H025"})
        assert any("H025" in e for e in errors)

        # Image at start of line should not trigger H025
        image_start_file = temp_path / "image_start.md"
        image_start_file.write_text("---\nlang: en\n---\n\n![Alt](img.png)\n", encoding="utf-8")
        errors = checker.check(image_start_file, select={"H025"})
        assert not errors

        # `![` mentioned inside inline code must not trigger H025
        image_in_code_file = temp_path / "image_in_code.md"
        image_in_code_file.write_text(
            "---\nlang: en\n---\n\nCheck that image Markdown `![` is at the start of the line.\n",
            encoding="utf-8",
        )
        errors = checker.check(image_in_code_file, select={"H025"})
        assert not errors, "H025 must ignore ![ inside inline code"

        # Several images in a row (badge line) must not trigger H025
        image_row_file = temp_path / "image_row.md"
        image_row_file.write_text(
            "---\nlang: en\n---\n\n"
            "![GitHub](https://img.shields.io/badge/GitHub-x-blue) "
            "![License](https://img.shields.io/github/license/Harrix/x) "
            "![PyPI](https://img.shields.io/pypi/v/x)\n",
            encoding="utf-8",
        )
        errors = checker.check(image_row_file, select={"H025"})
        assert not errors, "H025 must allow several images in a row"

        # Image after prose must still trigger H025
        image_after_prose_file = temp_path / "image_after_prose.md"
        image_after_prose_file.write_text(
            "---\nlang: en\n---\n\n![One](a.png) and ![Two](b.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(image_after_prose_file, select={"H025"})
        assert any("H025" in e for e in errors)

        # Linked thumbnail image at line start is allowed
        linked_image_file = temp_path / "linked_image.md"
        linked_image_file.write_text(
            "---\nlang: en\n---\n\n[![Wallpaper](gallery-thumb/a.jpg)](gallery/a.jpg)\n",
            encoding="utf-8",
        )
        errors = checker.check(linked_image_file, select={"H025"})
        assert not errors, "H025 must allow [![…](…)](…) at line start"

        # List item with linked image is allowed
        list_linked_image_file = temp_path / "list_linked_image.md"
        list_linked_image_file.write_text(
            "---\nlang: en\n---\n\n- [![Wallpaper](gallery-thumb/a.jpg)](gallery/a.jpg)\n",
            encoding="utf-8",
        )
        errors = checker.check(list_linked_image_file, select={"H025"})
        assert not errors, "H025 must allow linked images in list items"

        # List item with bare image is allowed
        list_image_file = temp_path / "list_image.md"
        list_image_file.write_text(
            "---\nlang: en\n---\n\n- ![Wallpaper](gallery/a.jpg)\n",
            encoding="utf-8",
        )
        errors = checker.check(list_image_file, select={"H025"})
        assert not errors, "H025 must allow images in list items"

        # Indented continuation image under a list item is allowed
        indented_list_image_file = temp_path / "indented_list_image.md"
        indented_list_image_file.write_text(
            "---\nlang: en\n---\n\n- Item:\n\n  ![Wallpaper](gallery/a.jpg)\n",
            encoding="utf-8",
        )
        errors = checker.check(indented_list_image_file, select={"H025"})
        assert not errors, "H025 must allow indented images under list items"

        # Prose before a linked image must still trigger H025
        prose_linked_image_file = temp_path / "prose_linked_image.md"
        prose_linked_image_file.write_text(
            "---\nlang: en\n---\n\nSee [![Wallpaper](t.jpg)](f.jpg)\n",
            encoding="utf-8",
        )
        errors = checker.check(prose_linked_image_file, select={"H025"})
        assert any("H025" in e for e in errors), "H025 must still fire for prose before linked image"

        # =====================================================================
        # H031: Invalid or placeholder image alt text
        # =====================================================================
        invalid_alt_cases = [
            "![](img/image.png)\n",
            "![alt](img/image.png)\n",
            "![Alt](img/image.png)\n",
            "![ALT](img/image.png)\n",
            "![alt text](img/image.png)\n",
            "![Alt text](img/image.png)\n",
            "![ALT TEXT](img/image.png)\n",
            "![Alt Text](img/image.png)\n",
            "![lowercase caption](img/image.png)\n",
        ]
        for index, body in enumerate(invalid_alt_cases):
            invalid_alt_file = temp_path / f"invalid_alt_{index}.md"
            invalid_alt_file.write_text(f"---\nlang: en\n---\n\n{body}", encoding="utf-8")
            errors = checker.check(invalid_alt_file, select={"H031"})
            assert any("H031" in e for e in errors), f"H031 must fire for invalid alt text: {body.strip()}"

        valid_alt_cases = [
            "![Возвращение функционала PrintScreen](img/image.png)\n",
            "![GitHub repo](img/image.png)\n",
            "![Alt text 2](img/image2.png)\n",
            "![Uppercase caption](img/image.png)\n",
        ]
        for index, body in enumerate(valid_alt_cases):
            valid_alt_file = temp_path / f"valid_alt_{index}.md"
            valid_alt_file.write_text(f"---\nlang: en\n---\n\n{body}", encoding="utf-8")
            errors = checker.check(valid_alt_file, select={"H031"})
            assert not errors, f"H031 must not fire for valid alt text: {body.strip()}"

        badge_alt_file = temp_path / "badge_alt.md"
        badge_alt_file.write_text(
            "---\nlang: en\n---\n\n![GitHub](https://img.shields.io/badge/GitHub-repo-blue)\n",
            encoding="utf-8",
        )
        errors = checker.check(badge_alt_file, select={"H031"})
        assert not errors

        # =====================================================================
        # H026: Horizontal bar ―
        # =====================================================================
        horizontal_bar_file = temp_path / "horizontal_bar.md"
        horizontal_bar_file.write_text(
            "---\nlang: ru\n---\n\n— Привет!\n― Как дела?\n",
            encoding="utf-8",
        )
        errors = checker.check(horizontal_bar_file, select={"H026"})
        assert any("H026" in e for e in errors)

        # =====================================================================
        # H027: Space after №
        # =====================================================================
        numero_no_space_file = temp_path / "numero_no_space.md"
        numero_no_space_file.write_text(
            "---\nlang: ru\n---\n\n№1 и №2.\n",
            encoding="utf-8",
        )
        errors = checker.check(numero_no_space_file, select={"H027"})
        assert any("H027" in e for e in errors)

        # № with space should not trigger H027
        numero_space_ok_file = temp_path / "numero_space_ok.md"
        numero_space_ok_file.write_text(
            "---\nlang: ru\n---\n\n№ 1 и № 2.\n",
            encoding="utf-8",
        )
        errors = checker.check(numero_space_ok_file, select={"H027"})
        assert not errors

        # `№` inside inline code must not trigger H027
        numero_in_code_file = temp_path / "numero_in_code.md"
        numero_in_code_file.write_text(
            "---\nlang: ru\n---\n\nCheck that `№` is followed by a space, e.g. exclude `№` at EOL.\n",
            encoding="utf-8",
        )
        errors = checker.check(numero_in_code_file, select={"H027"})
        assert not errors, "H027 must ignore № inside inline code"

        # =====================================================================
        # H028: Incorrect ?./!. / ?.../!... (use ?.. / !..)
        # =====================================================================
        qmark_period_file = temp_path / "qmark_period.md"
        qmark_period_file.write_text("---\nlang: en\n---\n\nReally?.\n", encoding="utf-8")
        errors = checker.check(qmark_period_file, select={"H028"})
        assert any("H028" in e for e in errors)

        qmark_three_dots_file = temp_path / "qmark_three_dots.md"
        qmark_three_dots_file.write_text("---\nlang: ru\n---\n\nВот как?... Ну да.\n", encoding="utf-8")
        errors = checker.check(qmark_three_dots_file, select={"H028"})
        assert any("H028" in e for e in errors)

        bang_period_file = temp_path / "bang_period.md"
        bang_period_file.write_text("---\nlang: ru\n---\n\nНеужели!.\n", encoding="utf-8")
        errors = checker.check(bang_period_file, select={"H028"})
        assert any("H028" in e for e in errors)

        bang_three_dots_file = temp_path / "bang_three_dots.md"
        bang_three_dots_file.write_text("---\nlang: ru\n---\n\nНеужели!... Ну да.\n", encoding="utf-8")
        errors = checker.check(bang_three_dots_file, select={"H028"})
        assert any("H028" in e for e in errors)

        # Correct rare forms ?.. / !.. must not trigger H028
        qmark_two_dots_file = temp_path / "qmark_two_dots.md"
        qmark_two_dots_file.write_text(
            "---\nlang: ru\n---\n\n— Вот как?.. Ну и чему он у него учился?\n",
            encoding="utf-8",
        )
        errors = checker.check(qmark_two_dots_file, select={"H028"})
        assert not errors

        bang_two_dots_file = temp_path / "bang_two_dots.md"
        bang_two_dots_file.write_text(
            "---\nlang: ru\n---\n\n— Вот это да!.. Ну и ну.\n",
            encoding="utf-8",
        )
        errors = checker.check(bang_two_dots_file, select={"H028"})
        assert not errors

        # Normal "?" / "!" or "." should not trigger H028
        normal_punct_file = temp_path / "normal_punct.md"
        normal_punct_file.write_text("---\nlang: en\n---\n\nReally? Yes!\n", encoding="utf-8")
        errors = checker.check(normal_punct_file, select={"H028"})
        assert not errors

        # =====================================================================
        # H029: Space required after colon in inline emphasis
        # =====================================================================
        emphasis_colon_no_space_file = temp_path / "emphasis_colon_no_space.md"
        emphasis_colon_no_space_file.write_text(
            "---\nlang: ru\n---\n\n"
            "- **Annotation:**Хвалился Комар, что никому его не одолеть.\n"
            "*Note:*text\n"
            "__Label:__value\n"
            "~~Strike:~~word\n"
            "**URL**:<https://example.com>\n",
            encoding="utf-8",
        )
        errors = checker.check(emphasis_colon_no_space_file, select={"H029"})
        assert len([e for e in errors if "H029" in e]) >= 5  # noqa: PLR2004

        emphasis_colon_ok_file = temp_path / "emphasis_colon_ok.md"
        emphasis_colon_ok_file.write_text(
            "---\nlang: ru\n---\n\n"
            "- **Author's name in English:** Vitaly Bianki\n"
            "- **URL**: <https://fantlab.ru/work483028>\n"
            "Label: value\n"
            "Use `**Bold:**text` in code.\n",
            encoding="utf-8",
        )
        errors = checker.check(emphasis_colon_ok_file, select={"H029"})
        assert not errors

        # =====================================================================
        # H030: Colon outside inline emphasis (should be inside)
        # =====================================================================
        colon_outside_emphasis_file = temp_path / "colon_outside_emphasis.md"
        colon_outside_emphasis_file.write_text(
            "---\nlang: ru\n---\n\n"
            "- **Date reading**: 2015\n"
            "**URL**: <https://example.com>\n"
            "*Note*: text\n"
            "__Label__: value\n"
            "~~Strike~~: word\n",
            encoding="utf-8",
        )
        errors = checker.check(colon_outside_emphasis_file, select={"H030"})
        assert len([e for e in errors if "H030" in e]) >= 5  # noqa: PLR2004

        colon_inside_emphasis_ok_file = temp_path / "colon_inside_emphasis_ok.md"
        colon_inside_emphasis_ok_file.write_text(
            "---\nlang: ru\n---\n\n"
            "- **Date reading:** 2015\n"
            "- **Author's name in English:** Vitaly Bianki\n"
            "- **URL:** <https://fantlab.ru/work483028>\n"
            "Label: value\n"
            "Use `**Bold**: text` in code.\n",
            encoding="utf-8",
        )
        errors = checker.check(colon_inside_emphasis_ok_file, select={"H030"})
        assert not errors

        # Trailing colon after emphasis at end of line should not trigger H030
        trailing_colon_emphasis_file = temp_path / "trailing_colon_emphasis.md"
        trailing_colon_emphasis_file.write_text(
            "---\nlang: ru\n---\n\nЗамена видеокодека на **madVR**:\n\n![Первоначальный кодек](img/mpc-hc_02.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(trailing_colon_emphasis_file, select={"H030"})
        assert not errors

        # =====================================================================
        # H033: Unclosed fenced code block
        # =====================================================================
        unclosed_fence_file = temp_path / "unclosed_fence.md"
        unclosed_fence_file.write_text(
            "---\nlang: en\n---\n\nExample:\n\n```python\nprint('hello')\n",
            encoding="utf-8",
        )
        errors = checker.check(unclosed_fence_file, select={"H033"})
        assert any("H033" in e for e in errors)

        closed_fence_file = temp_path / "closed_fence.md"
        closed_fence_file.write_text(
            "---\nlang: en\n---\n\nExample:\n\n```python\nprint('hello')\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(closed_fence_file, select={"H033"})
        assert not errors

        # =====================================================================
        # H034: Code fence without language identifier
        # =====================================================================
        no_lang_fence_file = temp_path / "no_lang_fence.md"
        no_lang_fence_file.write_text("---\nlang: en\n---\n\nExample:\n\n```\ncode\n```\n", encoding="utf-8")
        errors = checker.check(no_lang_fence_file, select={"H034"})
        assert any("H034" in e for e in errors)

        lang_fence_ok_file = temp_path / "lang_fence_ok.md"
        lang_fence_ok_file.write_text(
            "---\nlang: en\n---\n\nExample:\n\n```python\ncode\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(lang_fence_ok_file, select={"H034"})
        assert not errors

        nested_fence_file = temp_path / "nested_fence.md"
        nested_fence_file.write_text(
            "---\nlang: ru\n---\n\n"
            "````markdown\n"
            "Пример:\n\n"
            "```text\n"
            "line one\n"
            "```\n\n"
            "Ещё пример:\n\n"
            "```\n"
            "line two\n"
            "```\n"
            "````\n",
            encoding="utf-8",
        )
        errors = checker.check(nested_fence_file, select={"H034"})
        assert not errors

        # =====================================================================
        # H035: Missing figure caption after image
        # =====================================================================
        no_caption_file = temp_path / "no_caption.md"
        no_caption_file.write_text(
            "---\nlang: en\n---\n\nExample:\n\n![Alt text](img/image.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(no_caption_file, select={"H035"})
        assert any("H035" in e for e in errors)

        with_caption_file = temp_path / "with_caption.md"
        with_caption_file.write_text(
            "---\nlang: en\n---\n\nExample:\n\n![Alt text](img/image.png)\n\n_Figure 1: Alt text_\n",
            encoding="utf-8",
        )
        errors = checker.check(with_caption_file, select={"H035"})
        assert not errors

        ru_caption_file = temp_path / "ru_caption.md"
        ru_caption_file.write_text(
            "---\nlang: ru\n---\n\nПример:\n\n![Подпись](img/image.png)\n\n_Рисунок 1 — Подпись_\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(ru_caption_file, select={"H035"})
        assert not errors

        # =====================================================================
        # H036: Missing space after # in ATX heading
        # =====================================================================
        heading_no_space_file = temp_path / "heading_no_space.md"
        heading_no_space_file.write_text("---\nlang: en\n---\n\n#Title\n", encoding="utf-8")
        errors = checker.check(heading_no_space_file, select={"H036"})
        assert any("H036" in e for e in errors)

        heading_space_ok_file = temp_path / "heading_space_ok.md"
        heading_space_ok_file.write_text("---\nlang: en\n---\n\n# Title\n", encoding="utf-8")
        errors = checker.check(heading_space_ok_file, select={"H036"})
        assert not errors

        # =====================================================================
        # H037: Skipped heading level
        # =====================================================================
        skipped_heading_file = temp_path / "skipped_heading.md"
        skipped_heading_file.write_text("---\nlang: en\n---\n\n# Title\n\n### Subtitle\n", encoding="utf-8")
        errors = checker.check(skipped_heading_file, select={"H037"})
        assert any("H037" in e for e in errors)

        # =====================================================================
        # H038: Multiple H1 headings
        # =====================================================================
        multiple_h1_file = temp_path / "multiple_h1.md"
        multiple_h1_file.write_text("---\nlang: en\n---\n\n# One\n\n# Two\n", encoding="utf-8")
        errors = checker.check(multiple_h1_file, select={"H038"})
        assert any("H038" in e for e in errors)

        # =====================================================================
        # H039: Backslash in local Markdown path
        # =====================================================================
        backslash_path_file = temp_path / "backslash_path.md"
        backslash_path_file.write_text(
            "---\nlang: en\n---\n\n![Alt](img\\image.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(backslash_path_file, select={"H039"})
        assert any("H039" in e for e in errors)

        # =====================================================================
        # H006 extension: Expanded incorrect words
        # =====================================================================
        typescript_file = temp_path / "typescript.md"
        typescript_file.write_text("---\nlang: en\n---\n\nUse typescript and json.\n", encoding="utf-8")
        errors = checker.check(typescript_file, select={"H006"})
        assert any("H006" in e and "typescript" in e for e in errors)
        assert any("H006" in e and "json" in e for e in errors)

        node_js_file = temp_path / "node_js.md"
        node_js_file.write_text("---\nlang: en\n---\n\nInstall node.js today.\n", encoding="utf-8")
        errors = checker.check(node_js_file, select={"H006"})
        assert any("H006" in e and "node.js" in e for e in errors)

        # =====================================================================
        # H040: lang field does not match document language
        # =====================================================================
        lang_mismatch_en_file = temp_path / "lang_mismatch_en.md"
        lang_mismatch_en_file.write_text(
            "---\nlang: en\n---\n\nЭто русский текст.\nЕщё одна строка.\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(lang_mismatch_en_file, select={"H040"})
        assert any("H040" in e for e in errors)

        lang_mismatch_ru_file = temp_path / "lang_mismatch_ru.md"
        lang_mismatch_ru_file.write_text("---\nlang: ru\n---\n\nOnly English text here.\n", encoding="utf-8")
        errors = checker.check(lang_mismatch_ru_file, select={"H040"})
        assert any("H040" in e for e in errors)

        # =====================================================================
        # H041: Bare URL in text
        # =====================================================================
        bare_url_file = temp_path / "bare_url.md"
        bare_url_file.write_text("---\nlang: en\n---\n\nSee https://example.com for details.\n", encoding="utf-8")
        errors = checker.check(bare_url_file, select={"H041"})
        assert any("H041" in e for e in errors)

        wrapped_url_file = temp_path / "wrapped_url.md"
        wrapped_url_file.write_text(
            "---\nlang: en\n---\n\nSee <https://example.com> for details.\n",
            encoding="utf-8",
        )
        errors = checker.check(wrapped_url_file, select={"H041"})
        assert not errors

        # =====================================================================
        # H019 extension: Additional forbidden HTML tags
        # =====================================================================
        br_tag_file = temp_path / "br_tag.md"
        br_tag_file.write_text("---\nlang: en\n---\n\nLine<br>break\n", encoding="utf-8")
        errors = checker.check(br_tag_file, select={"H019"})
        assert any("H019" in e for e in errors)

        # =====================================================================
        # H042: Invisible Unicode character
        # =====================================================================
        invisible_char_file = temp_path / "invisible_char.md"
        invisible_char_file.write_text("---\nlang: en\n---\n\nWord\u200bbreak\n", encoding="utf-8")
        errors = checker.check(invisible_char_file, select={"H042"})
        assert any("H042" in e for e in errors)

        # =====================================================================
        # H043: Unmatched guillemets
        # =====================================================================
        unmatched_guillemet_file = temp_path / "unmatched_guillemet.md"
        unmatched_guillemet_file.write_text(
            "---\nlang: ru\n---\n\n«Незакрытая цитата\n", encoding="utf-8"
        )  # ignore: HP001
        errors = checker.check(unmatched_guillemet_file, select={"H043"})
        assert any("H043" in e for e in errors)

        # Guillemets only inside inline code must not trigger H043
        guillemet_in_code_file = temp_path / "guillemet_in_code.md"
        guillemet_in_code_file.write_text(
            "---\nlang: ru\n---\n\nAfter opening guillemet `«` (e.g. `«Ваша задача»`).\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(guillemet_in_code_file, select={"H043"})
        assert not errors, "H043 must ignore guillemets inside inline code"

        # Soft-wrapped blockquote: open « on one line, close » on another
        multiline_guillemet_file = temp_path / "multiline_guillemet.md"
        multiline_guillemet_file.write_text(
            "---\nlang: ru\n---\n\n"
            "> Но Лут сказал им: «Это — мои гости,\\\n"
            "> И вы меня пред ними не бесславьте,\\\n"
            "> Побойтесь Бога и меня не опозорьте».\\\n"
            ">\n"
            "> -- _Коран, Сура 15_\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(multiline_guillemet_file, select={"H043"})
        assert not [e for e in errors if "H043" in e], "H043 must allow «…» across soft-wrapped lines"

        # Still unmatched when close never appears in the same prose block
        multiline_unmatched_file = temp_path / "multiline_unmatched_guillemet.md"
        multiline_unmatched_file.write_text(
            "---\nlang: ru\n---\n\n"
            "> Он сказал: «Первая строка,\\\n"
            "> Вторая строка без закрытия.\n\n"
            "Другой абзац.\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(multiline_unmatched_file, select={"H043"})
        assert any("H043" in e for e in errors), "H043 must still catch unclosed « across lines"

        # =====================================================================
        # H044: Missing space before % or °
        # =====================================================================
        percent_no_space_file = temp_path / "percent_no_space.md"
        percent_no_space_file.write_text("---\nlang: ru\n---\n\nЗагрузка 50%.\n", encoding="utf-8")
        errors = checker.check(percent_no_space_file, select={"H044"})
        assert any("H044" in e for e in errors)

        # =====================================================================
        # H045: Broken relative Markdown link (default)
        # =====================================================================
        broken_link_file = temp_path / "broken_link.md"
        broken_link_file.write_text(
            "---\nlang: en\n---\n\n[Missing](./missing-file.md)\n",
            encoding="utf-8",
        )
        errors = checker.check(broken_link_file, select={"H045"})
        assert any("H045" in e for e in errors)

        existing_target = temp_path / "existing-target.md"
        existing_target.write_text("---\nlang: en\n---\n\n# Target\n", encoding="utf-8")
        valid_link_file = temp_path / "valid_link.md"
        valid_link_file.write_text(
            "---\nlang: en\n---\n\n[Existing](./existing-target.md)\n",
            encoding="utf-8",
        )
        errors = checker.check(valid_link_file, select={"H045"})
        assert not errors

        # Inline code with ](...) must not trigger H045 (false positive for operator[])
        inline_code_link_file = temp_path / "inline_code_link.md"
        inline_code_link_file.write_text(
            "---\nlang: en\n---\n\nUse `E& operator[](int)` in C++.\n",
            encoding="utf-8",
        )
        errors = checker.check(inline_code_link_file, select={"H045"})
        assert not errors

        # Percent-encoded path and optional title must resolve correctly
        encoded_target = temp_path / "encoded target.md"
        encoded_target.write_text("---\nlang: en\n---\n\n# Encoded\n", encoding="utf-8")
        encoded_link_file = temp_path / "encoded_link.md"
        encoded_link_file.write_text(
            '---\nlang: en\n---\n\n[Encoded](./encoded%20target.md "Title")\n',
            encoding="utf-8",
        )
        errors = checker.check(encoded_link_file, select={"H045"})
        assert not errors

        # =====================================================================
        # H060: Orphan asset files under sibling img/ and files/
        # =====================================================================
        orphan_article = temp_path / "orphan_article"
        orphan_article.mkdir()
        (orphan_article / "img").mkdir()
        (orphan_article / "img" / "a.png").write_bytes(b"png")
        orphan_md = orphan_article / "note.md"
        orphan_md.write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(orphan_md, select={"H060"})
        assert any("H060" in e and str((orphan_article / "img" / "a.png").resolve()) in e for e in errors)

        referenced_img_dir = temp_path / "referenced_img_article"
        referenced_img_dir.mkdir()
        (referenced_img_dir / "img").mkdir()
        (referenced_img_dir / "img" / "a.png").write_bytes(b"png")
        referenced_img_md = referenced_img_dir / "note_img.md"
        referenced_img_md.write_text(
            "---\nlang: en\n---\n\n![Alt](img/a.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(referenced_img_md, select={"H060"})
        assert not [e for e in errors if "H060" in e]

        # Backticks in alt/label must not split the image/link and miss the asset
        backtick_alt_dir = temp_path / "backtick_alt_article"
        backtick_alt_dir.mkdir()
        (backtick_alt_dir / "img").mkdir()
        (backtick_alt_dir / "img" / "xml_01.png").write_bytes(b"png")
        (backtick_alt_dir / "files").mkdir()
        (backtick_alt_dir / "files" / "doc.pdf").write_bytes(b"%PDF")
        backtick_alt_md = backtick_alt_dir / "note_backtick_alt.md"
        backtick_alt_md.write_text(
            "---\nlang: en\n---\n\n"
            "![Переход к `activity_main.xml`](img/xml_01.png)\n"
            "[Download `doc.pdf`](files/doc.pdf)\n",
            encoding="utf-8",
        )
        errors = checker.check(backtick_alt_md, select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept backticks in alt/label"

        # Basename match allows a “broken” folder prefix (img file linked as files/...)
        broken_path_dir = temp_path / "broken_path_article"
        broken_path_dir.mkdir()
        (broken_path_dir / "img").mkdir()
        (broken_path_dir / "img" / "a.png").write_bytes(b"png")
        broken_path_img_md = broken_path_dir / "note_broken_path.md"
        broken_path_img_md.write_text(
            "---\nlang: en\n---\n\n![Alt](files/a.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(broken_path_img_md, select={"H060"})
        assert not [e for e in errors if "H060" in e]

        files_article = temp_path / "files_article"
        files_article.mkdir()
        (files_article / "files").mkdir()
        (files_article / "files" / "doc.pdf").write_bytes(b"%PDF")
        orphan_files_md = files_article / "note.md"
        orphan_files_md.write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(orphan_files_md, select={"H060"})
        assert any("H060" in e and str((files_article / "files" / "doc.pdf").resolve()) in e for e in errors)

        linked_files_dir = temp_path / "linked_files_article"
        linked_files_dir.mkdir()
        (linked_files_dir / "files").mkdir()
        (linked_files_dir / "files" / "doc.pdf").write_bytes(b"%PDF")
        linked_files_md = linked_files_dir / "note_link.md"
        linked_files_md.write_text(
            "---\nlang: en\n---\n\n[Download](files/doc.pdf)\n",
            encoding="utf-8",
        )
        errors = checker.check(linked_files_md, select={"H060"})
        assert not [e for e in errors if "H060" in e]

        # files/ asset mentioned only as an image does not count
        image_only_files_dir = temp_path / "image_only_files_article"
        image_only_files_dir.mkdir()
        (image_only_files_dir / "files").mkdir()
        (image_only_files_dir / "files" / "doc.pdf").write_bytes(b"%PDF")
        image_only_files_md = image_only_files_dir / "note_image_only.md"
        image_only_files_md.write_text(
            "---\nlang: en\n---\n\n![Doc](files/doc.pdf)\n",
            encoding="utf-8",
        )
        errors = checker.check(image_only_files_md, select={"H060"})
        assert any("H060" in e and str((image_only_files_dir / "files" / "doc.pdf").resolve()) in e for e in errors)

        # img/ asset mentioned only as a non-image link does not count
        link_only_img_dir = temp_path / "link_only_img_article"
        link_only_img_dir.mkdir()
        (link_only_img_dir / "img").mkdir()
        (link_only_img_dir / "img" / "a.png").write_bytes(b"png")
        link_only_img_md = link_only_img_dir / "note_link_only.md"
        link_only_img_md.write_text(
            "---\nlang: en\n---\n\n[Alt](img/a.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(link_only_img_md, select={"H060"})
        assert any("H060" in e and str((link_only_img_dir / "img" / "a.png").resolve()) in e for e in errors)

        # Mention only inside a fenced code block does not count
        code_only_dir = temp_path / "code_only_article"
        code_only_dir.mkdir()
        (code_only_dir / "img").mkdir()
        (code_only_dir / "img" / "a.png").write_bytes(b"png")
        code_only_md = code_only_dir / "note_code_only.md"
        code_only_md.write_text(
            "---\nlang: en\n---\n\n```md\n![Alt](img/a.png)\n```\n",
            encoding="utf-8",
        )
        errors = checker.check(code_only_md, select={"H060"})
        assert any("H060" in e and str((code_only_dir / "img" / "a.png").resolve()) in e for e in errors)

        # Reference in one sibling Markdown file covers the whole folder
        shared_dir = temp_path / "shared_assets_article"
        shared_dir.mkdir()
        (shared_dir / "img").mkdir()
        (shared_dir / "img" / "shared.png").write_bytes(b"png")
        (shared_dir / "README.md").write_text(
            "---\nlang: en\n---\n\n![Shared](img/shared.png)\n",
            encoding="utf-8",
        )
        (shared_dir / "DEVELOPMENT.md").write_text(
            "---\nlang: en\n---\n\n# Development\n",
            encoding="utf-8",
        )
        (shared_dir / "_Notes.g.md").write_text(
            "---\nlang: en\n---\n\n# Generated\n",
            encoding="utf-8",
        )
        errors = checker.check(shared_dir / "DEVELOPMENT.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept refs from sibling Markdown files"
        errors = checker.check(shared_dir / "README.md", select={"H060"})
        assert not [e for e in errors if "H060" in e]

        # Generated *.g.md references must not count
        g_md_only_dir = temp_path / "g_md_only_article"
        g_md_only_dir.mkdir()
        (g_md_only_dir / "img").mkdir()
        (g_md_only_dir / "img" / "only-in-g.png").write_bytes(b"png")
        (g_md_only_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        (g_md_only_dir / "_Dump.g.md").write_text(
            "---\nlang: en\n---\n\n![Only](img/only-in-g.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(g_md_only_dir / "note.md", select={"H060"})
        assert any("H060" in e and str((g_md_only_dir / "img" / "only-in-g.png").resolve()) in e for e in errors)

        # GitHub raw URL in README covers sibling THIRD_PARTY_NOTICES.md
        github_raw_dir = temp_path / "github_raw_article"
        github_raw_dir.mkdir()
        (github_raw_dir / "img").mkdir()
        (github_raw_dir / "img" / "screenshot.png").write_bytes(b"png")
        (github_raw_dir / "README.md").write_text(
            "---\nlang: en\n---\n\n"
            "![Screenshot](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/"
            "refs/heads/main/img/screenshot.png)\n",
            encoding="utf-8",
        )
        (github_raw_dir / "THIRD_PARTY_NOTICES.md").write_text(
            "---\nlang: en\n---\n\n# Notices\n",
            encoding="utf-8",
        )
        errors = checker.check(github_raw_dir / "THIRD_PARTY_NOTICES.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept GitHub raw.githubusercontent.com URLs"
        errors = checker.check(github_raw_dir / "README.md", select={"H060"})
        assert not [e for e in errors if "H060" in e]

        # github.com blob URL also counts
        github_blob_dir = temp_path / "github_blob_article"
        github_blob_dir.mkdir()
        (github_blob_dir / "img").mkdir()
        (github_blob_dir / "img" / "featured.png").write_bytes(b"png")
        (github_blob_dir / "README.md").write_text(
            "---\nlang: en\n---\n\n![Featured](https://github.com/Harrix/demo/blob/main/img/featured.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(github_blob_dir / "README.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept github.com blob URLs"

        # YAML download: GitHub raw URL counts as a files/ link reference
        yaml_download_dir = temp_path / "yaml_download_article"
        yaml_download_dir.mkdir()
        (yaml_download_dir / "files").mkdir()
        (yaml_download_dir / "files" / "test-uv.zip").write_bytes(b"PK")
        (yaml_download_dir / "article.md").write_text(
            "---\nlang: en\n"
            "download: https://github.com/Harrix/harrix.dev-articles-2025-en/raw/main/"
            "uv-vscode-python/files/test-uv.zip\n"
            "---\n\n# Article\n",
            encoding="utf-8",
        )
        errors = checker.check(yaml_download_dir / "article.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept download URLs in YAML"

        # YAML relative files/ path also counts
        yaml_rel_dir = temp_path / "yaml_relative_files_article"
        yaml_rel_dir.mkdir()
        (yaml_rel_dir / "files").mkdir()
        (yaml_rel_dir / "files" / "doc.pdf").write_bytes(b"%PDF")
        (yaml_rel_dir / "article.md").write_text(
            "---\nlang: en\ndownload: files/doc.pdf\n---\n\n# Article\n",
            encoding="utf-8",
        )
        errors = checker.check(yaml_rel_dir / "article.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept relative files/ paths in YAML"

        # YAML img/ GitHub URL counts as an image reference
        yaml_img_dir = temp_path / "yaml_img_article"
        yaml_img_dir.mkdir()
        (yaml_img_dir / "img").mkdir()
        (yaml_img_dir / "img" / "cover.png").write_bytes(b"png")
        (yaml_img_dir / "article.md").write_text(
            "---\nlang: en\n"
            "cover: https://raw.githubusercontent.com/Harrix/demo/main/img/cover.png\n"
            "---\n\n# Article\n",
            encoding="utf-8",
        )
        errors = checker.check(yaml_img_dir / "article.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must accept img/ URLs in YAML"

        # Non-GitHub absolute URL must not count
        foreign_host_dir = temp_path / "foreign_host_article"
        foreign_host_dir.mkdir()
        (foreign_host_dir / "img").mkdir()
        (foreign_host_dir / "img" / "screenshot.png").write_bytes(b"png")
        (foreign_host_dir / "README.md").write_text(
            "---\nlang: en\n---\n\n![Screenshot](https://example.com/img/screenshot.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(foreign_host_dir / "README.md", select={"H060"})
        assert any("H060" in e and str((foreign_host_dir / "img" / "screenshot.png").resolve()) in e for e in errors)

        # docs/actions-style: sibling files/*.g.md is a docs category, not assets
        category_files_dir = temp_path / "category_files_article"
        category_files_dir.mkdir()
        (category_files_dir / "files").mkdir()
        (category_files_dir / "files" / "extract_zip_archives.g.md").write_text(
            "---\nlang: en\n---\n\n# Extract\n",
            encoding="utf-8",
        )
        (category_files_dir / "files" / "note.md").write_text(
            "---\nlang: en\n---\n\n# Note\n",
            encoding="utf-8",
        )
        (category_files_dir / "dialog_widgets.g.md").write_text(
            "---\nlang: en\n---\n\n# Dialog widgets\n",
            encoding="utf-8",
        )
        errors = checker.check(category_files_dir / "dialog_widgets.g.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must ignore Markdown under files/"

        # PDF under files/ remains an orphan asset
        mixed_files_dir = temp_path / "mixed_files_article"
        mixed_files_dir.mkdir()
        (mixed_files_dir / "files").mkdir()
        (mixed_files_dir / "files" / "readme.md").write_text("# Docs\n", encoding="utf-8")
        (mixed_files_dir / "files" / "doc.pdf").write_bytes(b"%PDF")
        (mixed_files_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(mixed_files_dir / "note.md", select={"H060"})
        assert any("H060" in e and str((mixed_files_dir / "files" / "doc.pdf").resolve()) in e for e in errors)
        assert not any("readme.md" in e for e in errors if "H060" in e)

        # Nested note assets under category files/ must not affect parent Markdown
        nested_note_dir = temp_path / "nested_note_under_files"
        nested_note_dir.mkdir()
        (nested_note_dir / "files").mkdir()
        note_subdir = nested_note_dir / "files" / "my-note"
        note_subdir.mkdir()
        (note_subdir / "img").mkdir()
        (note_subdir / "files").mkdir()
        (note_subdir / "img" / "nested.png").write_bytes(b"png")
        (note_subdir / "files" / "nested.pdf").write_bytes(b"%PDF")
        (note_subdir / "note.md").write_text(
            "---\nlang: en\n---\n\n![Nested](img/nested.png)\n\n[PDF](files/nested.pdf)\n",
            encoding="utf-8",
        )
        (nested_note_dir / "dialog_widgets.g.md").write_text(
            "---\nlang: en\n---\n\n# Dialog widgets\n",
            encoding="utf-8",
        )
        errors = checker.check(nested_note_dir / "dialog_widgets.g.md", select={"H060"})
        assert not [e for e in errors if "H060" in e], "H060 must not recurse into nested note assets"
        errors = checker.check(note_subdir / "note.md", select={"H060"})
        assert not [e for e in errors if "H060" in e]

        # Nested file under img/subdir is not checked at parent level
        deep_img_dir = temp_path / "deep_img_article"
        deep_img_dir.mkdir()
        (deep_img_dir / "img").mkdir()
        (deep_img_dir / "img" / "chapter").mkdir()
        (deep_img_dir / "img" / "chapter" / "deep.png").write_bytes(b"png")
        (deep_img_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(deep_img_dir / "note.md", select={"H060"})
        assert not [e for e in errors if "H060" in e]

        # No sibling asset folders → no H060
        plain_md = temp_path / "plain_no_assets.md"
        plain_md.write_text("---\nlang: en\n---\n\n# Plain\n", encoding="utf-8")
        errors = checker.check(plain_md, select={"H060"})
        assert not errors

        # =====================================================================
        # H061: Misplaced note asset files
        # =====================================================================
        loose_png_dir = temp_path / "h061_loose_png"
        loose_png_dir.mkdir()
        (loose_png_dir / "photo.png").write_bytes(b"png")
        (loose_png_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(loose_png_dir / "note.md", select={"H061"})
        assert any("H061" in e and "photo.png" in e and "img/" in e for e in errors)

        loose_pdf_dir = temp_path / "h061_loose_pdf"
        loose_pdf_dir.mkdir()
        (loose_pdf_dir / "doc.pdf").write_bytes(b"%PDF")
        (loose_pdf_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(loose_pdf_dir / "note.md", select={"H061"})
        assert any("H061" in e and "doc.pdf" in e and "files/" in e for e in errors)

        media_in_files_dir = temp_path / "h061_media_in_files"
        media_in_files_dir.mkdir()
        (media_in_files_dir / "files").mkdir()
        (media_in_files_dir / "files" / "shot.gif").write_bytes(b"gif")
        (media_in_files_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(media_in_files_dir / "note.md", select={"H061"})
        assert any("H061" in e and "shot.gif" in e and "img/" in e for e in errors)

        pdf_in_img_dir = temp_path / "h061_pdf_in_img"
        pdf_in_img_dir.mkdir()
        (pdf_in_img_dir / "img").mkdir()
        (pdf_in_img_dir / "img" / "doc.pdf").write_bytes(b"%PDF")
        (pdf_in_img_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(pdf_in_img_dir / "note.md", select={"H061"})
        assert any("H061" in e and "doc.pdf" in e and "files/" in e for e in errors)

        featured_root_dir = temp_path / "h061_featured_root"
        featured_root_dir.mkdir()
        (featured_root_dir / "featured-image.png").write_bytes(b"png")
        (featured_root_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(featured_root_dir / "note.md", select={"H061"})
        assert not [e for e in errors if "H061" in e]

        featured_img_dir = temp_path / "h061_featured_img"
        featured_img_dir.mkdir()
        (featured_img_dir / "img").mkdir()
        (featured_img_dir / "img" / "featured-image.svg").write_bytes(b"<svg/>")
        (featured_img_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(featured_img_dir / "note.md", select={"H061"})
        assert not [e for e in errors if "H061" in e]

        nested_ignored_dir = temp_path / "h061_nested_ignored"
        nested_ignored_dir.mkdir()
        (nested_ignored_dir / "other").mkdir()
        (nested_ignored_dir / "other" / "a.png").write_bytes(b"png")
        (nested_ignored_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(nested_ignored_dir / "note.md", select={"H061"})
        assert not [e for e in errors if "H061" in e]

        media_ext_dir = temp_path / "h061_media_ext"
        media_ext_dir.mkdir()
        (media_ext_dir / "icon.ico").write_bytes(b"ico")
        (media_ext_dir / "vector.svg").write_bytes(b"<svg/>")
        (media_ext_dir / "note.md").write_text("---\nlang: en\n---\n\n# Note\n", encoding="utf-8")
        errors = checker.check(media_ext_dir / "note.md", select={"H061"})
        assert any("H061" in e and "icon.ico" in e and "img/" in e for e in errors)
        assert any("H061" in e and "vector.svg" in e and "img/" in e for e in errors)

        project_root_dir = temp_path / "h061_project_root"
        project_root_dir.mkdir()
        (project_root_dir / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        (project_root_dir / "photo.png").write_bytes(b"png")
        (project_root_dir / "README.md").write_text("---\nlang: en\n---\n\n# Repo\n", encoding="utf-8")
        errors = checker.check(project_root_dir / "README.md", select={"H061"})
        assert not [e for e in errors if "H061" in e]

        # =====================================================================
        # H046: Wrong line endings (respect .gitattributes eol=)
        # =====================================================================
        lf_endings_file = temp_path / "lf_endings.md"
        lf_endings_file.write_text("---\nlang: en\n---\n\n# Title\n", encoding="utf-8", newline="\n")
        errors = checker.check(lf_endings_file, select={"H046"})
        assert any("H046" in e for e in errors)
        assert any("LF line endings instead of CRLF" in e for e in errors)

        crlf_endings_file = temp_path / "crlf_endings.md"
        crlf_endings_file.write_bytes(b"---\r\nlang: en\r\n---\r\n\r\n# Title\r\n")
        errors = checker.check(crlf_endings_file, select={"H046"})
        assert not errors

        lf_repo = temp_path / "lf_repo"
        lf_repo.mkdir()
        (lf_repo / ".gitattributes").write_text("* text=auto eol=lf\n", encoding="utf-8")
        lf_ok = lf_repo / "lf_ok.md"
        lf_ok.write_text("---\nlang: en\n---\n\n# Title\n", encoding="utf-8", newline="\n")
        errors = checker.check(lf_ok, select={"H046"})
        assert not errors

        lf_bad = lf_repo / "lf_bad.md"
        lf_bad.write_bytes(b"---\r\nlang: en\r\n---\r\n\r\n# Title\r\n")
        errors = checker.check(lf_bad, select={"H046"})
        assert any("H046" in e for e in errors)
        assert any("CRLF line endings instead of LF" in e for e in errors)

        # =====================================================================
        # H047: BOM at start of file
        # =====================================================================
        bom_file = temp_path / "bom.md"
        bom_file.write_bytes("\ufeff---\nlang: en\n---\n\n# Title\n".encode())
        errors = checker.check(bom_file, select={"H047"})
        assert any("H047" in e for e in errors)

        # =====================================================================
        # H048: Unicode replacement character
        # =====================================================================
        replacement_file = temp_path / "replacement_char.md"
        replacement_file.write_text("---\nlang: ru\n---\n\nтекст с \ufffd символом\n", encoding="utf-8")
        errors = checker.check(replacement_file, select={"H048"})
        assert any("H048" in e for e in errors)

        # =====================================================================
        # H049: Mixed Latin and Cyrillic letters
        # =====================================================================
        mixed_script_file = temp_path / "mixed_script.md"
        mixed_script_file.write_text("---\nlang: ru\n---\n\nCистемы с обратной связью\n", encoding="utf-8")
        errors = checker.check(mixed_script_file, select={"H049"})
        assert any("H049" in e for e in errors)

        allowlisted_mixed_file = temp_path / "allowlisted_mixed.md"
        allowlisted_mixed_file.write_text("---\nlang: ru\n---\n\nФильм Духless\n", encoding="utf-8")
        errors = checker.check(allowlisted_mixed_file, select={"H049"})
        assert not errors

        # =====================================================================
        # H050: Missing space after punctuation
        # =====================================================================
        missing_space_punct_file = temp_path / "missing_space_punct.md"
        missing_space_punct_file.write_text(
            "---\nlang: ru\n---\n\nСлово,другое слово\n",
            encoding="utf-8",
        )
        errors = checker.check(missing_space_punct_file, select={"H050"})
        assert any("H050" in e for e in errors)

        ascii_csv_like_file = temp_path / "ascii_csv_like.md"
        ascii_csv_like_file.write_text("---\nlang: en\n---\n\nSee items a,b and 1979a,b.\n", encoding="utf-8")
        errors = checker.check(ascii_csv_like_file, select={"H050"})
        assert not errors

        admonition_file = temp_path / "admonition_h050.md"
        admonition_file.write_text("---\nlang: en\n---\n\n[!NOTE]\n\nText\n", encoding="utf-8")
        errors = checker.check(admonition_file, select={"H050"})
        assert not errors

        # =====================================================================
        # H051: Malformed punctuation sequence
        # =====================================================================
        malformed_punct_file = temp_path / "malformed_punct.md"
        malformed_punct_file.write_text(
            "---\nlang: ru\n---\n\nЭто постулат:. Далее текст.\n",
            encoding="utf-8",
        )
        errors = checker.check(malformed_punct_file, select={"H051"})
        assert any("H051" in e for e in errors)

        malformed_time_file = temp_path / "malformed_time.md"
        malformed_time_file.write_text("---\nlang: ru\n---\n\n### 16;:34\n", encoding="utf-8")
        errors = checker.check(malformed_time_file, select={"H051"})
        assert any("H051" in e for e in errors)

        abbrev_comma_file = temp_path / "abbrev_comma.md"
        abbrev_comma_file.write_text(
            "---\nlang: ru\n---\n\nЭлектрозаводская ул., 21, Москва\n",
            encoding="utf-8",
        )
        errors = checker.check(abbrev_comma_file, select={"H051"})
        assert not errors

        word_dot_comma_file = temp_path / "word_dot_comma.md"
        word_dot_comma_file.write_text(
            "---\nlang: ru\n---\n\nЖил в гостинице., потом уехал.\n",
            encoding="utf-8",
        )
        errors = checker.check(word_dot_comma_file, select={"H051"})
        assert any("H051" in e for e in errors)

        # =====================================================================
        # H052: Heading deeper than H6
        # =====================================================================
        deep_heading_file = temp_path / "deep_heading.md"
        deep_heading_file.write_text(
            "---\nlang: en\n---\n\n# Title\n\n####### Too deep\n",
            encoding="utf-8",
        )
        errors = checker.check(deep_heading_file, select={"H052"})
        assert any("H052" in e for e in errors)

        # =====================================================================
        # H057: Trailing period at end of ATX heading
        # =====================================================================
        heading_period_file = temp_path / "heading_period.md"
        heading_period_file.write_text(
            "---\nlang: ru\n---\n\n## Никогда не разговаривайте с неизвестными.\n",
            encoding="utf-8",
        )
        errors = checker.check(heading_period_file, select={"H057"})
        assert any("H057" in e for e in errors)

        heading_ok_file = temp_path / "heading_ok.md"
        heading_ok_file.write_text(
            "---\nlang: ru\n---\n\n"
            "## Исповедь горячего сердца. В стихах\n\n"
            "## Глава 5. Буди, буди!\n\n"
            "## Что дальше?\n",
            encoding="utf-8",
        )
        errors = checker.check(heading_ok_file, select={"H057"})
        assert not errors

        # =====================================================================
        # H058: Punctuation before closing guillemet
        # =====================================================================
        period_inside_guillemet_file = temp_path / "period_inside_guillemet.md"
        period_inside_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nСон по мотивам «Очень странных дел.»\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(period_inside_guillemet_file, select={"H058"})
        assert any("H058" in e for e in errors)

        period_after_guillemet_file = temp_path / "period_after_guillemet.md"
        period_after_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nСон по мотивам «Очень странных дел».\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(period_after_guillemet_file, select={"H058"})
        assert not errors

        exclamation_inside_guillemet_file = temp_path / "exclamation_inside_guillemet.md"
        exclamation_inside_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nОн сказал: «Как хорошо!»\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(exclamation_inside_guillemet_file, select={"H058"})
        assert not errors

        question_inside_guillemet_file = temp_path / "question_inside_guillemet.md"
        question_inside_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nСпросили: «Где?»\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(question_inside_guillemet_file, select={"H058"})
        assert not errors

        abbrev_inside_guillemet_file = temp_path / "abbrev_inside_guillemet.md"
        abbrev_inside_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nСмотри список «и т. д.» в конце.\n",  # ignore: HP001
            encoding="utf-8",
        )
        errors = checker.check(abbrev_inside_guillemet_file, select={"H058"})
        assert not errors

        period_inside_guillemet_en_file = temp_path / "period_inside_guillemet_en.md"
        period_inside_guillemet_en_file.write_text(
            "---\nlang: en\n---\n\nHe watched «Stranger Things.»\n",
            encoding="utf-8",
        )
        errors = checker.check(period_inside_guillemet_en_file, select={"H058"})
        assert not errors

        # =====================================================================
        # H006: Интернет / онлайн / вуз  # noqa: ERA001
        # =====================================================================
        internet_file = temp_path / "internet_word.md"
        internet_file.write_text(
            "---\nlang: ru\n---\n\nНашёл в интернете пример.\n",
            encoding="utf-8",
        )
        errors = checker.check(internet_file, select={"H006"})
        assert any("H006" in e and "интернете" in e for e in errors)

        internet_compound_file = temp_path / "internet_compound.md"
        internet_compound_file.write_text(
            "---\nlang: ru\n---\n\nСистема интернет-оповещения работает.\n",
            encoding="utf-8",
        )
        errors = checker.check(internet_compound_file, select={"H006"})
        assert not any("H006" in e and "интернет" in e for e in errors)

        online_file = temp_path / "online_word.md"
        online_file.write_text(
            "---\nlang: ru\n---\n\nВсе должны быть он-лайн.\n",
            encoding="utf-8",
        )
        errors = checker.check(online_file, select={"H006"})
        assert any("H006" in e and "он-лайн" in e for e in errors)

        vuz_file = temp_path / "vuz_word.md"
        vuz_file.write_text(
            "---\nlang: ru\n---\n\nПять ВУЗов из России.\n",
            encoding="utf-8",
        )
        errors = checker.check(vuz_file, select={"H006"})
        assert any("H006" in e and "ВУЗов" in e for e in errors)

        # =====================================================================
        # H053: Unbalanced details/summary
        # =====================================================================
        unbalanced_details_file = temp_path / "unbalanced_details.md"
        unbalanced_details_file.write_text(
            "---\nlang: en\n---\n\n<details>\n<details>\n\nText\n",
            encoding="utf-8",
        )
        errors = checker.check(unbalanced_details_file, select={"H053"})
        assert any("H053" in e for e in errors)

        balanced_details_file = temp_path / "balanced_details.md"
        balanced_details_file.write_text(
            "---\nlang: en\n---\n\n<details>\n<summary>More</summary>\n\nText\n\n</details>\n",
            encoding="utf-8",
        )
        errors = checker.check(balanced_details_file, select={"H053"})
        assert not errors

        # =====================================================================
        # H054: Repeated adjacent word
        # =====================================================================
        repeated_word_file = temp_path / "repeated_word.md"
        repeated_word_file.write_text(
            "---\nlang: en\n---\n\nCorrect code code here\n",
            encoding="utf-8",
        )
        errors = checker.check(repeated_word_file, select={"H054"})
        assert any("H054" in e for e in errors)

        hyphenated_repeat_file = temp_path / "hyphenated_repeat.md"
        hyphenated_repeat_file.write_text(
            "---\nlang: en\n---\n\nFolder Notes-Notes example\n",
            encoding="utf-8",
        )
        errors = checker.check(hyphenated_repeat_file, select={"H054"})
        assert not errors

        # `что что-то`: second token is a hyphenated compound, not a repeat
        compound_after_word_file = temp_path / "compound_after_word.md"
        compound_after_word_file.write_text(
            "---\nlang: ru\n---\n\nОзначает ли это, что что-то имеет статус?\n",
            encoding="utf-8",
        )
        errors = checker.check(compound_after_word_file, select={"H054"})
        assert not errors

        # Real adjacent repeat of a hyphenated compound must still fail
        repeated_compound_file = temp_path / "repeated_compound.md"
        repeated_compound_file.write_text(
            "---\nlang: en\n---\n\nThis is well-known well-known case\n",
            encoding="utf-8",
        )
        errors = checker.check(repeated_compound_file, select={"H054"})
        assert any("H054" in e for e in errors)

        # Title-Case doubles (names / titles) are allowed
        title_case_double_file = temp_path / "title_case_double.md"
        title_case_double_file.write_text(
            "---\nlang: en\n---\n\nKnock Knock is a movie. Humbert Humbert is a character.\n",
            encoding="utf-8",
        )
        errors = checker.check(title_case_double_file, select={"H054"})
        assert not errors

        # Runs of 3+ identical words are intentional emphasis / hyperbole
        triple_repeat_en_file = temp_path / "triple_repeat_en.md"
        triple_repeat_en_file.write_text(
            "---\nlang: en\n---\n\nThis is very very very unlikely.\n",
            encoding="utf-8",
        )
        errors = checker.check(triple_repeat_en_file, select={"H054"})
        assert not errors

        hyperbole_ru_file = temp_path / "hyperbole_millions.md"
        hyperbole_ru_file.write_text(
            "---\nlang: ru\n---\n\nпримерно 1 из 10000 миллионов миллионов миллионов миллионов миллионов миллионов.\n",
            encoding="utf-8",
        )
        errors = checker.check(hyperbole_ru_file, select={"H054"})
        assert not errors

        # Same word around inline code is not an adjacent repeat
        word_around_code_file = temp_path / "word_around_code.md"
        word_around_code_file.write_text(
            "---\nlang: ru\n---\n\n`ma#тет` или `ma@fc` или `ma:10` — пример.\n",
            encoding="utf-8",
        )
        errors = checker.check(word_around_code_file, select={"H054"})
        assert not [e for e in errors if "H054" in e], "H054 must not join words across inline code"

        # =====================================================================
        # H055: Broken internal fragment link
        # =====================================================================
        broken_fragment_file = temp_path / "broken_fragment.md"
        broken_fragment_file.write_text(
            "---\nlang: en\n---\n\n# Title\n\n[Bad](#missing-anchor)\n\n## Real Section\n",
            encoding="utf-8",
        )
        errors = checker.check(broken_fragment_file, select={"H055"})
        assert any("H055" in e for e in errors)

        valid_fragment_file = temp_path / "valid_fragment.md"
        valid_fragment_file.write_text(
            "---\nlang: en\n---\n\n# Title\n\n[Good](#real-section)\n\n## Real Section\n",
            encoding="utf-8",
        )
        errors = checker.check(valid_fragment_file, select={"H055"})
        assert not errors

        # Emoji with VS16 (U+FE0F): raw and percent-encoded fragments must match
        vs16_raw_file = temp_path / "vs16_raw_fragment.md"
        vs16_raw_file.write_text(
            "---\nlang: en\n---\n\n# Title\n\n[Tech](#️-technologies)\n\n## 🛠️ Technologies\n",
            encoding="utf-8",
        )
        errors = checker.check(vs16_raw_file, select={"H055"})
        assert not errors

        vs16_encoded_file = temp_path / "vs16_encoded_fragment.md"
        vs16_encoded_file.write_text(
            "---\nlang: en\n---\n\n# Title\n\n[Tech](#%EF%B8%8F-technologies)\n\n## 🛠️ Technologies\n",
            encoding="utf-8",
        )
        errors = checker.check(vs16_encoded_file, select={"H055"})
        assert not errors

        # Emoji without VS16: leading hyphen after emoji strip
        plain_emoji_file = temp_path / "plain_emoji_fragment.md"
        plain_emoji_file.write_text(
            "---\nlang: en\n---\n\n# Title\n\n[Install](#-installation)\n\n## 📦 Installation\n",
            encoding="utf-8",
        )
        errors = checker.check(plain_emoji_file, select={"H055"})
        assert not errors

        # =====================================================================
        # H056: Unbalanced inline code in table cell
        # =====================================================================
        unbalanced_table_code_file = temp_path / "unbalanced_table_code.md"
        unbalanced_table_code_file.write_text(
            "---\nlang: en\n---\n\n| A | B |\n| --- | --- |\n| `operator | ` |\n",
            encoding="utf-8",
        )
        errors = checker.check(unbalanced_table_code_file, select={"H056"})
        assert any("H056" in e for e in errors)

        # Escaped pipes inside inline code are not cell separators
        escaped_pipe_table_file = temp_path / "escaped_pipe_table.md"
        escaped_pipe_table_file.write_text(
            "---\nlang: en\n---\n\n"
            "| A | B |\n"
            "| --- | --- |\n"
            "| `a \\| b` | ok |\n"
            "| `operator\\|`, `operator^` | bitwise |\n"
            "| `operator\\|\\|` | or |\n",
            encoding="utf-8",
        )
        errors = checker.check(escaped_pipe_table_file, select={"H056"})
        assert not errors

        # =====================================================================
        # raw-markdown: true — skip body after first ATX H1
        # =====================================================================
        raw_md_file = temp_path / "raw_markdown_note.md"
        raw_md_file.write_text(
            "---\nlang: en\nraw-markdown: true\n---\n\n"
            "# Experiment\n\n"
            "Custom syntax with markdown and Hello , world.\n"
            "Bad dash - here and https://example.com/bare\n",
            encoding="utf-8",
        )
        errors = checker.check(raw_md_file)
        assert not any(code in error for error in errors for code in ("H006", "H015", "H016", "H041", "H050")), errors

        # Without the flag, the same body is flagged
        normal_md_file = temp_path / "normal_markdown_note.md"
        normal_md_file.write_text(
            "---\nlang: en\n---\n\n# Experiment\n\nCustom syntax with markdown and Hello , world.\n",
            encoding="utf-8",
        )
        errors = checker.check(normal_md_file, select={"H006", "H015"})
        assert any("H006" in error for error in errors)
        assert any("H015" in error for error in errors)

        # YAML / filename rules still apply with raw-markdown
        raw_no_lang = temp_path / "raw_no_lang.md"
        raw_no_lang.write_text(
            "---\nraw-markdown: true\n---\n\n# Title\n\nbad markdown body\n",
            encoding="utf-8",
        )
        errors = checker.check(raw_no_lang, select={"H004", "H006"})
        assert any("H004" in error for error in errors)
        assert not any("H006" in error for error in errors)

        # All registered rules are enabled by default
        assert "H045" in checker.all_rules
        assert "H046" in checker.all_rules
        assert "H047" in checker.all_rules
        assert "H048" in checker.all_rules
        assert "H054" in checker.all_rules
        assert "H055" in checker.all_rules
        assert "H056" in checker.all_rules
        assert "H057" in checker.all_rules
        assert "H059" in checker.all_rules
        assert "H060" in checker.all_rules
        assert "H033" in checker.all_rules
        assert checker.all_rules == set(checker.RULES.keys())
