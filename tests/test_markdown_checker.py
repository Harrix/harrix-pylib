"""Tests for the MarkdownChecker class."""

from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h

EXPECTED_H007_ERRORS = 2


def test_markdown_checker() -> None:
    """Test MarkdownChecker for all rules and scenarios."""
    checker = h.md_check.MarkdownChecker()

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
        ru_file.write_text("---\nlang: ru\n---\nЭто web приложение и web документ", encoding="utf-8")  # noqa: RUF001
        errors = checker.check(ru_file)
        assert any("H006" in error for error in errors)

        # Test Russian abbreviations without spaces (т.е., т.д., т.ч., т.п.)  # noqa: RUF003
        ru_abbrev_file = temp_path / "ru_abbrev.md"
        ru_abbrev_file.write_text(
            "---\nlang: ru\n---\n\nТо есть т.е. и т.д. правильно писать т. е. и т. д.\n",  # noqa: RUF001
            encoding="utf-8",
        )
        errors = checker.check(ru_abbrev_file, select={"H006"})
        assert any("H006" in e and "т.е." in e for e in errors)  # noqa: RUF001
        assert any("H006" in e and "т.д." in e for e in errors)

        # Test that code blocks are ignored
        code_block_file = temp_path / "code_block_test.md"
        code_block_file.write_text(
            "---\nlang: en\n---\n# Test\n```python\nmarkdown = 'test'\nhtml = 'code'\n```\nOutside code",
            encoding="utf-8",
        )
        errors = checker.check(code_block_file)
        assert not any("markdown" in error and "```" in str(code_block_file.read_text()) for error in errors)

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

        # =====================================================================
        # H010: Tab character
        # =====================================================================
        tab_file = temp_path / "tab_test.md"
        tab_file.write_text("---\nlang: en\n---\n\nLine with\ttab.\n", encoding="utf-8")
        errors = checker.check(tab_file, select={"H010"})
        assert any("H010" in e for e in errors)

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
        # H023: No empty line between paragraphs
        # =====================================================================
        no_empty_between_file = temp_path / "no_empty_between.md"
        no_empty_between_file.write_text(
            "---\nlang: en\n---\n\nFirst paragraph.\nSecond paragraph.\n",
            encoding="utf-8",
        )
        errors = checker.check(no_empty_between_file, select={"H023"})
        assert any("H023" in e for e in errors)

        # With empty line between paragraphs — no error
        with_empty_between_file = temp_path / "with_empty_between.md"
        with_empty_between_file.write_text(
            "---\nlang: en\n---\n\nFirst paragraph.\n\nSecond paragraph.\n",
            encoding="utf-8",
        )
        errors = checker.check(with_empty_between_file, select={"H023"})
        assert not errors

        # List items without empty line — no H023 (list context)
        list_file = temp_path / "list_no_empty.md"
        list_file.write_text("---\nlang: en\n---\n\n* Item one\n* Item two\n", encoding="utf-8")
        errors = checker.check(list_file, select={"H023"})
        assert not errors

        # Content inside <details> block — no H023 (details/summary are exceptions)
        details_block_file = temp_path / "details_block.md"
        details_block_file.write_text(
            "---\nlang: en\n---\n\n<details>\n<summary>📖 Содержание</summary>\n\n## Содержание\n\n</details>\n",
            encoding="utf-8",
        )
        errors = checker.check(details_block_file, select={"H023"})
        assert not errors, "H023 must not flag content inside <details> block"

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
        endash_digits_file.write_text("---\nlang: en\n---\n\nRange is 1–10 pages.\n", encoding="utf-8")  # noqa: RUF001
        errors = checker.check(endash_digits_file, select={"H016"})
        assert not errors

        # En dash NOT between digits should trigger H016
        endash_wrong_file = temp_path / "endash_wrong.md"
        endash_wrong_file.write_text("---\nlang: en\n---\n\nWord–word is wrong.\n", encoding="utf-8")  # noqa: RUF001
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

        # Correct ellipsis character (in middle of line) should not trigger H017
        ellipsis_file = temp_path / "ellipsis.md"
        ellipsis_file.write_text("---\nlang: en\n---\n\nWait for it… and more.\n", encoding="utf-8")
        errors = checker.check(ellipsis_file, select={"H017"})
        assert not errors

        # Ellipsis at end of line should trigger H017
        ellipsis_eol_file = temp_path / "ellipsis_eol.md"
        ellipsis_eol_file.write_text("---\nlang: en\n---\n\nWait for it…\n", encoding="utf-8")
        errors = checker.check(ellipsis_eol_file, select={"H017"})
        assert any("H017" in e and "end of line" in e for e in errors)

        # Three dots inside code block should not trigger H017
        dots_in_code_file = temp_path / "dots_in_code.md"
        dots_in_code_file.write_text("---\nlang: en\n---\n\n```python\nresult = [...]\n```\n", encoding="utf-8")
        errors = checker.check(dots_in_code_file, select={"H017"})
        assert not errors

        # =====================================================================
        # H018: Curly/straight quotes instead of angle quotes
        # =====================================================================
        straight_quote_file = temp_path / "straight_quote.md"
        straight_quote_file.write_text('---\nlang: en\n---\n\nHe said "hello".\n', encoding="utf-8")
        errors = checker.check(straight_quote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        curly_quote_file = temp_path / "curly_quote.md"
        curly_quote_file.write_text("---\nlang: en\n---\n\nHe said \u201chello\u201d.\n", encoding="utf-8")
        errors = checker.check(curly_quote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        # Space after « should trigger H018
        space_after_lquote_file = temp_path / "space_lquote.md"
        space_after_lquote_file.write_text("---\nlang: en\n---\n\nSaid « hello».\n", encoding="utf-8")
        errors = checker.check(space_after_lquote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        # Space before » should trigger H018
        space_before_rquote_file = temp_path / "space_rquote.md"
        space_before_rquote_file.write_text("---\nlang: en\n---\n\nSaid «hello ».\n", encoding="utf-8")
        errors = checker.check(space_before_rquote_file, select={"H018"})
        assert any("H018" in e for e in errors)

        # Correct angle quotes should not trigger H018
        angle_quote_file = temp_path / "angle_quote.md"
        angle_quote_file.write_text("---\nlang: en\n---\n\nHe said «hello».\n", encoding="utf-8")
        errors = checker.check(angle_quote_file, select={"H018"})
        assert not errors

        # Inch notation (e.g. 14", 15.6") should not trigger H018
        inch_quote_file = temp_path / "inch_quote.md"
        inch_quote_file.write_text(
            "---\nlang: ru\n---\n\n| ДИСПЛЕЙ | 14\" FHD (1920×1080), IPS |\n",
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
            "---\nlang: ru\n---\n\nНачинкой (капустной, крапивной и т. д.) заливают. Используют т. е. так.\n",  # noqa: RUF001
            encoding="utf-8",
        )
        errors = checker.check(ru_abbrev_file, select={"H021"})
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
        # H024: Capitalized Russian polite pronoun (ru only)
        # =====================================================================
        ru_vy_file = temp_path / "ru_vy.md"
        ru_vy_file.write_text(
            "---\nlang: ru\n---\n\nОбращаемся к Вам с предложением.\n",  # noqa: RUF001
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_file, select={"H024"})
        assert any("H024" in e for e in errors)

        # "Вы" at sentence start is allowed (only flag mid-sentence)
        ru_vy_sentence_start_file = temp_path / "ru_vy_sentence_start.md"
        ru_vy_sentence_start_file.write_text(
            "---\nlang: ru\n---\n\nВы можете это увидеть.\n\nТут Вам не рады.\n",  # noqa: RUF001
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_sentence_start_file, select={"H024"})
        h024_errors = [e for e in errors if "H024" in e]
        assert len(h024_errors) == 1, "Exactly one H024 (Вам in middle), not Вы at start"
        assert "вам" in h024_errors[0].lower()

        # Lowercase "вы" should not trigger H024
        ru_vy_lower_file = temp_path / "ru_vy_lower.md"
        ru_vy_lower_file.write_text(
            "---\nlang: ru\n---\n\nОбращаемся к вам с предложением.\n",  # noqa: RUF001
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_lower_file, select={"H024"})
        assert not errors

        # lang: en with "Вы" should not trigger H024 (rule only for ru)
        en_vy_file = temp_path / "en_vy.md"
        en_vy_file.write_text("---\nlang: en\n---\n\nSome text with Вы.\n", encoding="utf-8")
        errors = checker.check(en_vy_file, select={"H024"})
        assert not errors

        # "Вы" inside inline code should not trigger H024
        ru_vy_code_file = temp_path / "ru_vy_code.md"
        ru_vy_code_file.write_text(
            "---\nlang: ru\n---\n\nUse variable `Вы` in code.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_code_file, select={"H024"})
        assert not errors

        # "Ваша" after « (direct speech) is sentence start — no H024
        ru_vy_guillemet_file = temp_path / "ru_vy_guillemet.md"
        ru_vy_guillemet_file.write_text(
            "---\nlang: ru\n---\n\nВедущий говорит: «Ваша задача определить, сколько я показываю гаражей».\n",  # noqa: RUF001
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_guillemet_file, select={"H024"})
        assert not errors

        # "Ваша" after dash at line start (dialogue) is sentence start — no H024
        ru_vy_dash_dialogue_file = temp_path / "ru_vy_dash_dialogue.md"
        ru_vy_dash_dialogue_file.write_text(
            "---\nlang: ru\n---\n\n— Ваша работа хороша.\n",
            encoding="utf-8",
        )
        errors = checker.check(ru_vy_dash_dialogue_file, select={"H024"})
        assert not errors

        # =====================================================================
        # H025: Latin x or Cyrillic x instead of ×  # noqa: RUF003
        # =====================================================================
        x_instead_file = temp_path / "x_instead.md"
        x_instead_file.write_text(
            "---\nlang: ru\n---\n\nSize 5 x 10 cm.\n",
            encoding="utf-8",
        )
        errors = checker.check(x_instead_file, select={"H025"})
        assert any("H025" in e for e in errors)

        # x86 and x64 should not trigger H025
        x86_file = temp_path / "x86.md"
        x86_file.write_text("---\nlang: en\n---\n\nSupport x86 and x64.\n", encoding="utf-8")
        errors = checker.check(x86_file, select={"H025"})
        assert not errors

        # "2x Type-C", "1x USB" (digit + x + space) should not trigger H025
        digit_x_file = temp_path / "digit_x.md"
        digit_x_file.write_text(
            "---\nlang: en\n---\n\n2x Type-C, 1x USB, 1x Micro SD.\n",
            encoding="utf-8",
        )
        errors = checker.check(digit_x_file, select={"H025"})
        assert not errors

        # x inside inline code should not trigger H025
        x_code_file = temp_path / "x_code.md"
        x_code_file.write_text("---\nlang: en\n---\n\nUse `x` variable.\n", encoding="utf-8")
        errors = checker.check(x_code_file, select={"H025"})
        assert not errors

        # =====================================================================
        # H026: Image ![ not at start of line
        # =====================================================================
        image_not_start_file = temp_path / "image_not_start.md"
        image_not_start_file.write_text(
            "---\nlang: en\n---\n\nText ![alt](img.png)\n",
            encoding="utf-8",
        )
        errors = checker.check(image_not_start_file, select={"H026"})
        assert any("H026" in e for e in errors)

        # Image at start of line should not trigger H026
        image_start_file = temp_path / "image_start.md"
        image_start_file.write_text("---\nlang: en\n---\n\n![Alt](img.png)\n", encoding="utf-8")
        errors = checker.check(image_start_file, select={"H026"})
        assert not errors

        # =====================================================================
        # H028: Horizontal bar ―
        # =====================================================================
        horizontal_bar_file = temp_path / "horizontal_bar.md"
        horizontal_bar_file.write_text(
            "---\nlang: ru\n---\n\n— Привет!\n― Как дела?\n",
            encoding="utf-8",
        )
        errors = checker.check(horizontal_bar_file, select={"H028"})
        assert any("H028" in e for e in errors)

        # =====================================================================
        # H029: Space after №
        # =====================================================================
        numero_no_space_file = temp_path / "numero_no_space.md"
        numero_no_space_file.write_text(
            "---\nlang: ru\n---\n\n№1 и №2.\n",
            encoding="utf-8",
        )
        errors = checker.check(numero_no_space_file, select={"H029"})
        assert any("H029" in e for e in errors)

        # № with space should not trigger H029
        numero_space_ok_file = temp_path / "numero_space_ok.md"
        numero_space_ok_file.write_text(
            "---\nlang: ru\n---\n\n№ 1 и № 2.\n",
            encoding="utf-8",
        )
        errors = checker.check(numero_space_ok_file, select={"H029"})
        assert not errors

        # =====================================================================
        # H030: Question mark followed by period
        # =====================================================================
        qmark_period_file = temp_path / "qmark_period.md"
        qmark_period_file.write_text("---\nlang: en\n---\n\nReally?.\n", encoding="utf-8")
        errors = checker.check(qmark_period_file, select={"H030"})
        assert any("H030" in e for e in errors)

        # Normal "?" or "." should not trigger H030
        normal_punct_file = temp_path / "normal_punct.md"
        normal_punct_file.write_text("---\nlang: en\n---\n\nReally? Yes.\n", encoding="utf-8")
        errors = checker.check(normal_punct_file, select={"H030"})
        assert not errors
