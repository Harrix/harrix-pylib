"""Tests for the PythonChecker class."""

from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h


def test_python_checker() -> None:
    """Test PythonChecker for all rules and scenarios."""
    checker = h.py_check.PythonChecker()

    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test HP001: Russian letters in code
        russian_file = temp_path / "russian.py"
        russian_file.write_text('print("Привет мир")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(russian_file)
        assert any("HP001" in error for error in errors)

        # Test HP001: Russian letters in different positions
        russian_var_file = temp_path / "russian_var.py"
        russian_var_file.write_text('имя = "test"\nprint(имя)\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(russian_var_file)
        count_errors = 2
        assert len([e for e in errors if "HP001" in e]) == count_errors  # Two lines with Russian

        # Test HP001: Russian letters in comments
        russian_comment_file = temp_path / "russian_comment.py"
        russian_comment_file.write_text('# Это комментарий\nprint("hello")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(russian_comment_file)
        assert any("HP001" in error for error in errors)

        # Test HP001: Mixed case Russian letters
        mixed_case_file = temp_path / "mixed_case.py"
        mixed_case_file.write_text('# БОЛЬШИЕ и малые буквы\nprint("test")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(mixed_case_file)
        assert any("HP001" in error for error in errors)

        # Test HP001: Russian letter 'ё' and 'Ё'  # ignore: HP001
        yo_file = temp_path / "yo.py"
        yo_file.write_text('# Ёлка и ёж\nprint("test")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(yo_file)
        assert any("HP001" in error for error in errors)

        # Test valid file with no Russian letters
        valid_file = temp_path / "valid.py"
        valid_file.write_text('print("Hello world")\n# English comment\n', encoding="utf-8")
        errors = checker.check(valid_file)
        assert len(errors) == 0

        # Test ignore directive - single rule
        ignored_single_file = temp_path / "ignored_single.py"
        ignored_single_file.write_text('print("Привет")  # ignore: HP001\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(ignored_single_file)
        assert len(errors) == 0

        # Test ignore directive - multiple rules
        ignored_multiple_file = temp_path / "ignored_multiple.py"
        ignored_multiple_file.write_text('print("Привет")  # ignore: HP001, HP002\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(ignored_multiple_file)
        assert len(errors) == 0

        # Test ignore directive - case insensitive
        ignored_case_file = temp_path / "ignored_case.py"
        ignored_case_file.write_text('print("Привет")  # ignore: hp001\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(ignored_case_file)
        assert len(errors) == 0

        # Test ignore directive - with spaces
        ignored_spaces_file = temp_path / "ignored_spaces.py"
        ignored_spaces_file.write_text('print("Вот")  # ignore: HP001 , HP002 \n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(ignored_spaces_file)
        assert len(errors) == 0

        # Test ignore directive - different format
        ignored_format_file = temp_path / "ignored_format.py"
        ignored_format_file.write_text('print("Привет")  #ignore:HP001\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(ignored_format_file)
        assert len(errors) == 0

        # Test line without ignore directive should still trigger error
        not_ignored_file = temp_path / "not_ignored.py"
        not_ignored_file.write_text('print("Вот")  # some comment\nprint("Мир")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(not_ignored_file)
        count_errors = 2
        assert len([e for e in errors if "HP001" in e]) == count_errors  # Two lines with Russian

        # Test mixed ignored and not ignored lines
        mixed_file = temp_path / "mixed.py"
        mixed_file.write_text('print("Привет")  # ignore: HP001\nprint("Мир")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(mixed_file)
        assert len([e for e in errors if "HP001" in e]) == 1  # Only second line

        # Test exclude_rules functionality
        file_with_issues = temp_path / "file_with_issues.py"
        file_with_issues.write_text('print("Привет мир")\n', encoding="utf-8")  # ignore: HP001

        # Check all errors
        all_errors = checker.check(file_with_issues)
        assert len(all_errors) > 0

        # Exclude HP001 rule
        excluded_errors = checker.check(file_with_issues, exclude_rules={"HP001"})
        assert len(excluded_errors) == 0

        # Test __call__ method
        call_errors = checker(file_with_issues)
        assert call_errors == all_errors

        # Test with exclude_rules in __call__
        call_excluded_errors = checker(file_with_issues, exclude_rules={"HP001"})
        assert len(call_excluded_errors) == 0

        # Test file reading error (permission denied simulation)
        # This is harder to test directly, but we can test the exception handling path
        # by creating a file and then trying to read it as if it doesn't exist
        nonexistent_file = temp_path / "nonexistent.py"
        errors = checker.check(nonexistent_file)
        assert any("P000" in error and "Exception error" in error for error in errors)

        # Test with Path object
        path_obj_errors = checker.check(Path(valid_file))
        assert len(path_obj_errors) == 0

        # Test with string path
        string_path_errors = checker.check(str(valid_file))
        assert len(string_path_errors) == 0

        # Test column position reporting
        column_test_file = temp_path / "column_test.py"
        column_test_file.write_text('x = "Привет"\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(column_test_file)
        assert len(errors) == 1
        assert ":1:6:" in errors[0]  # Should point to the 'П' character  # ignore: HP001

        # Test multiple Russian letters on same line - should report first occurrence
        multiple_russian_file = temp_path / "multiple_russian.py"
        multiple_russian_file.write_text('print("Привет", "Мир")\n', encoding="utf-8")  # ignore: HP001
        errors = checker.check(multiple_russian_file)
        assert len(errors) == 1
        assert ":1:8:" in errors[0]  # Should point to the first 'П' character  # ignore: HP001
