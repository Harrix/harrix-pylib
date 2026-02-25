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
        # H001: Space in filename
        # =====================================================================
        file_with_space = temp_path / "file name.md"
        file_with_space.write_text("---\nlang: en\n---\n# Test", encoding="utf-8")
        errors = checker.check(file_with_space)
        assert any("H001" in error for error in errors)

        # =====================================================================
        # H002: Space in path
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

        # =====================================================================
        # H017: Three dots instead of ellipsis character
        # =====================================================================
        three_dots_file = temp_path / "three_dots.md"
        three_dots_file.write_text("---\nlang: en\n---\n\nWait for it...\n", encoding="utf-8")
        errors = checker.check(three_dots_file, select={"H017"})
        assert any("H017" in e for e in errors)

        # Correct ellipsis character should not trigger H017
        ellipsis_file = temp_path / "ellipsis.md"
        ellipsis_file.write_text("---\nlang: en\n---\n\nWait for it…\n", encoding="utf-8")
        errors = checker.check(ellipsis_file, select={"H017"})
        assert not errors

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
        # H023: Incorrect dash characters in code blocks
        # =====================================================================
        emdash_in_code_file = temp_path / "emdash_in_code.md"
        emdash_in_code_file.write_text(
            "---\nlang: en\n---\n\n```python\ntext = 'hello \u2014 world'\n```\n", encoding="utf-8"
        )
        errors = checker.check(emdash_in_code_file, select={"H023"})
        assert any("H023" in e for e in errors)

        # Check all incorrect dash types in code
        for dash_char in ["\u2015", "\u2014", "\u2012", "\u2212", "\u2010"]:
            dash_file = temp_path / f"dash_{ord(dash_char)}.md"
            dash_file.write_text(f"---\nlang: en\n---\n\n```shell\ncommand{dash_char}flag\n```\n", encoding="utf-8")
            errors = checker.check(dash_file, select={"H023"})
            assert any("H023" in e for e in errors), f"Expected H023 for dash U+{ord(dash_char):04X}"

        # Normal dash in code should not trigger H023
        normal_dash_code_file = temp_path / "normal_dash_code.md"
        normal_dash_code_file.write_text("---\nlang: en\n---\n\n```shell\ncommand --flag\n```\n", encoding="utf-8")
        errors = checker.check(normal_dash_code_file, select={"H023"})
        assert not errors
