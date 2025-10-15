"""Tests for the MarkdownChecker class."""

from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h


def test_markdown_checker() -> None:
    """Test MarkdownChecker for all rules and scenarios."""
    checker = h.md_check.MarkdownChecker()

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test H001: Space in filename
        file_with_space = temp_path / "file name.md"
        file_with_space.write_text("---\nlang: en\n---\n# Test", encoding="utf-8")
        errors = checker.check(file_with_space)
        assert any("H001" in error for error in errors)

        # Test H002: Space in path
        space_dir = temp_path / "folder with space"
        space_dir.mkdir()
        file_in_space_path = space_dir / "file.md"
        file_in_space_path.write_text("---\nlang: en\n---\n# Test", encoding="utf-8")
        errors = checker.check(file_in_space_path)
        assert any("H002" in error for error in errors)

        # Test H003: Missing YAML
        no_yaml_file = temp_path / "no_yaml.md"
        no_yaml_file.write_text("# Just content without YAML", encoding="utf-8")
        errors = checker.check(no_yaml_file)
        assert any("H003" in error for error in errors)

        # Test H004: Missing lang field in YAML
        no_lang_file = temp_path / "no_lang.md"
        no_lang_file.write_text("---\ntitle: Test\n---\n# Content", encoding="utf-8")
        errors = checker.check(no_lang_file)
        assert any("H004" in error for error in errors)

        # Test H005: Invalid lang value
        invalid_lang_file = temp_path / "invalid_lang.md"
        invalid_lang_file.write_text("---\nlang: fr\n---\n# Content", encoding="utf-8")
        errors = checker.check(invalid_lang_file)
        assert any("H005" in error for error in errors)

        # Test H006: Lowercase markdown
        lowercase_md_file = temp_path / "lowercase.md"
        lowercase_md_file.write_text("---\nlang: en\n---\n# Test markdown content", encoding="utf-8")
        errors = checker.check(lowercase_md_file)
        assert any("H006" in error for error in errors)
        assert any("Markdown" in error for error in errors)

        # Test H006: Various incorrect word forms
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
        # Should not flag markdown and html inside code blocks
        assert not any("markdown" in error and "```" in str(code_block_file.read_text()) for error in errors)

        # Test that inline code is ignored
        inline_code_file = temp_path / "inline_code_test.md"
        inline_code_file.write_text(
            "---\nlang: en\n---\nUse `markdown` in code, but markdown outside", encoding="utf-8"
        )
        errors = checker.check(inline_code_file)
        # Should find only one error (the one outside backticks)
        markdown_errors = [e for e in errors if "H006" in e and "markdown" in e]
        assert len(markdown_errors) == 1

        # Test valid file with no errors
        valid_file = temp_path / "valid.md"
        valid_file.write_text(
            "---\nlang: en\n---\n# Test Markdown content with HTML, CSS, PDF, JavaScript, C++, GitHub, Git",
            encoding="utf-8",
        )
        errors = checker.check(valid_file)
        assert len(errors) == 0

        # Test exclude_rules functionality
        file_with_issues = temp_path / "file with issues.md"
        file_with_issues.write_text("---\nlang: fr\n---\n# Test markdown", encoding="utf-8")

        # Check all errors
        all_errors = checker.check(file_with_issues)
        assert len(all_errors) > 0

        # Exclude some rules
        excluded_errors = checker.check(file_with_issues, exclude_rules={"H001", "H005", "H006"})
        assert len(excluded_errors) < len(all_errors)

        # Test __call__ method
        call_errors = checker(file_with_issues)
        assert call_errors == all_errors

        # Test with exclude_rules in __call__
        call_excluded_errors = checker(file_with_issues, exclude_rules={"H001"})
        assert len(call_excluded_errors) < len(all_errors)

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
