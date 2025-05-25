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

        # Test valid file with no errors
        valid_file = temp_path / "valid.md"
        valid_file.write_text("---\nlang: en\n---\n# Test Markdown content", encoding="utf-8")
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

        # Test file reading error (non-existent file)
        non_existent = temp_path / "does_not_exist.md"
        errors = checker.check(non_existent)
        assert any("Error reading or processing file" in error for error in errors)

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
