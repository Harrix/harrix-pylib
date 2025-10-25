"""Module providing functionality for checking Markdown files for compliance with specified rules."""

import re
from collections.abc import Generator
from pathlib import Path
from typing import ClassVar

import yaml

import harrix_pylib as h


class MarkdownChecker:
    """Class for checking Markdown files for compliance with specified rules.

    Rules:

    - **H001** - Presence of a space in the Markdown file name.
    - **H002** - Presence of a space in the path to the Markdown file.
    - **H003** - YAML is missing.
    - **H004** - The lang field is missing in YAML.
    - **H005** - In YAML, lang is not set to `en` or `ru`.
    - **H006** - Incorrect word form used (e.g., "markdown" instead of "Markdown", "latex" instead of "LaTeX").
    - **H007** - Incorrect code block language identifier
      (e.g., "console" instead of "shell", "py" instead of "python").

    """

    # Rule constants for easier maintenance
    RULES: ClassVar[dict[str, str]] = {
        "H001": "Presence of a space in the Markdown file name",
        "H002": "Presence of a space in the path to the Markdown file",
        "H003": "YAML is missing",
        "H004": "The lang field is missing in YAML",
        "H005": "In YAML, lang is not set to en or ru",
        "H006": "Incorrect word form used",
        "H007": "Incorrect code block language identifier",
    }

    # Dictionary of incorrect word forms that should be flagged
    # Key: incorrect form, Value: suggested correct form
    INCORRECT_WORDS: ClassVar[dict[str, str]] = {
        # LaTeX variations
        "Latex": "LaTeX",
        "latex": "LaTeX",
        # Email
        "e-mail": "email",
        # CMS with Cyrillic letters (that look like Latin)
        "cms": "CMS",
        "СЬS": "CMS",  # noqa: RUF001 # ignore: HP001
        "СMS": "CMS",  # noqa: RUF001 # ignore: HP001
        "СМS": "CMS",  # noqa: RUF001 # ignore: HP001
        "сms": "CMS",  # noqa: RUF001 # ignore: HP001
        "смs": "CMS",  # noqa: RUF001 # ignore: HP001
        "СМС": "CMS",  # noqa: RUF001 # ignore: HP001
        "смс": "CMS",  # ignore: HP001
        # File extensions and tech terms
        "css": "CSS",
        "html": "HTML",
        "pdf": "PDF",
        "php": "PHP",
        "svg": "SVG",
        "xml": "XML",
        "odf": "ODF",
        "odt": "ODT",
        "dll": "DLL",
        "Dll": "DLL",
        "exe": "EXE",
        "qml": "QML",
        # Web document variations
        "web документ": "веб-документ",  # ignore: HP001
        "Web документ": "веб-документ",  # ignore: HP001
        "WEB документ": "веб-документ",  # ignore: HP001
        # Web application variations
        "web приложение": "веб-приложение",  # ignore: HP001
        "Web приложение": "веб-приложение",  # ignore: HP001
        "WEB приложение": "веб-приложение",  # ignore: HP001
        "web приложения": "веб-приложения",  # ignore: HP001
        "Web приложения": "веб-приложения",  # ignore: HP001
        "WEB приложения": "веб-приложения",  # ignore: HP001
        # Programming languages with Cyrillic letters
        "c++": "C++",
        "с++": "C++",  # noqa: RUF001 # ignore: HP001
        "С++": "C++",  # noqa: RUF001 # ignore: HP001
        "с#": "C#",  # noqa: RUF001 # ignore: HP001
        "С#": "C#",  # noqa: RUF001 # ignore: HP001
        "сpp": "cpp",  # noqa: RUF001 # ignore: HP001
        "срр": "cpp",  # noqa: RUF001 # ignore: HP001
        "pascal": "Pascal",
        # C++ standards
        "c++11": "C++11",
        "с++11": "C++11",  # noqa: RUF001 # ignore: HP001
        "С++11": "C++11",  # noqa: RUF001 # ignore: HP001
        "c++17": "C++17",
        "с++17": "C++17",  # noqa: RUF001 # ignore: HP001
        "С++17": "C++17",  # noqa: RUF001 # ignore: HP001
        "c++20": "C++20",
        "с++20": "C++20",  # noqa: RUF001  # ignore: HP001
        "С++20": "C++20",  # noqa: RUF001  # ignore: HP001
        # OK variations
        "ok": "OK",
        "Ok": "OK",
        "ОК": "OK",  # noqa: RUF001 # ignore: HP001
        "ок": "OK",  # ignore: HP001
        # ID variations
        "id": "ID",
        "Id": "ID",
        # JavaScript variations
        "javaScript": "JavaScript",
        "Javascript": "JavaScript",
        "javascript": "JavaScript",
        # PHP
        "Php": "PHP",
        # Cyrillic characters
        "Йе": "Qt",  # ignore: HP001
        "йе": "Qt",  # ignore: HP001
        # Qt
        "qt": "Qt",
        # Android and Java
        "android": "Android",
        "java": "Java",
        # APK
        "apk": "APK",
        # Markdown
        "markdon": "Markdown",
        "markdown": "Markdown",
        # Git and GitHub
        "Github": "GitHub",
        "github": "GitHub",
        "git": "Git",
    }

    def __init__(self, project_root: Path | str | None = None) -> None:
        """Initialize the MarkdownChecker with all available rules.

        Args:

        - `project_root` (`Path | str | None`): Root directory of the project for relative path calculation.
          If None, will try to find git root or use current working directory.

        """
        self.all_rules = set(self.RULES.keys())
        self.project_root = self._determine_project_root(project_root)

    def __call__(
        self, filename: Path | str, *, select: set[str] | None = None, exclude_rules: set[str] | None = None
    ) -> list[str]:
        """Check Markdown file for compliance with specified rules."""
        return self.check(filename, select=select, exclude_rules=exclude_rules)

    def check(
        self, filename: Path | str, *, select: set[str] | None = None, exclude_rules: set[str] | None = None
    ) -> list[str]:
        """Check Markdown file for compliance with specified rules.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file to check.
        - `select` (`set[str] | None`): Set of rule codes to check. If specified, only these rules will be checked.
          Defaults to `None` (check all rules).
        - `exclude_rules` (`set[str] | None`): Set of rule codes to exclude from checking. Defaults to `None`.
          If both `select` and `exclude_rules` are specified, `select` is applied first, then `exclude_rules`
          filters from the selected rules.

        Returns:

        - `list[str]`: List of error messages found during checking.

        Examples:

        ```python
        checker = MarkdownChecker()

        # Check all rules
        errors = checker.check("file.md")

        # Check only specific rules (like ruff --select)
        errors = checker.check("file.md", select={"H001", "H002"})

        # Check all rules except specified (like ruff --ignore)
        errors = checker.check("file.md", exclude_rules={"H006"})

        # Combine: select specific rules and exclude some from them
        errors = checker.check("file.md", select={"H001", "H002", "H003"}, exclude_rules={"H002"})
        ```

        """
        filename = Path(filename)
        active_rules = self._determine_active_rules(select, exclude_rules)
        return list(self._check_all_rules(filename, active_rules))

    def check_directory(
        self,
        directory: Path | str,
        *,
        select: set[str] | None = None,
        exclude_rules: set[str] | None = None,
        additional_ignore_patterns: list[str] | None = None,
    ) -> dict[str, list[str]]:
        """Check all Markdown files in directory for compliance with specified rules.

        Args:

        - `directory` (`Path | str`): Directory to search for Markdown files.
        - `select` (`set[str] | None`): Set of rule codes to check. If specified, only these rules will be checked.
          Defaults to `None` (check all rules).
        - `exclude_rules` (`set[str] | None`): Set of rule codes to exclude from checking. Defaults to `None`.
        - `additional_ignore_patterns` (`list[str] | None`): Additional patterns to ignore. Defaults to `None`.

        Returns:

        - `dict[str, list[str]]`: Dictionary mapping file paths to lists of error messages.

        """
        results = {}

        for md_file in self.find_markdown_files(directory, additional_ignore_patterns):
            errors = self.check(md_file, select=select, exclude_rules=exclude_rules)
            if errors:  # Only include files with errors
                results[str(md_file)] = errors

        return results

    def find_markdown_files(
        self, directory: Path | str, additional_ignore_patterns: list[str] | None = None
    ) -> Generator[Path, None, None]:
        """Find all Markdown files in directory, ignoring hidden folders and specified patterns.

        Args:

        - `directory` (`Path | str`): Directory to search for Markdown files.
        - `additional_ignore_patterns` (`list[str] | None`): Additional patterns to ignore. Defaults to `None`.

        Yields:

        - `Path`: Path to each found Markdown file.

        """
        directory = Path(directory)

        if not directory.is_dir():
            return

        # Check if current directory should be ignored
        if h.file.should_ignore_path(directory, additional_ignore_patterns):
            return

        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in {".md", ".markdown"}:
                yield item
            elif item.is_dir() and not h.file.should_ignore_path(item, additional_ignore_patterns):
                # Recursively search in subdirectories that are not ignored
                yield from self.find_markdown_files(item, additional_ignore_patterns)

    def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Generate all errors found during checking.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each found issue.

        """
        yield from self._check_filename_rules(filename, rules)

        # Read file only once for performance
        try:
            content = filename.read_text(encoding="utf-8")
            all_lines = content.splitlines()
            yaml_end_line = self._find_yaml_end_line(all_lines)

            yaml_part, _ = h.md.split_yaml_content(content)

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules)
            yield from self._check_content_rules(filename, all_lines, yaml_end_line, rules)
            yield from self._check_code_rules(filename, all_lines, yaml_end_line, rules)

        except Exception as e:
            yield self._format_error("H000", f"Exception error: {e}", filename)

    def _check_code_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set
    ) -> Generator[str, None, None]:
        """Check code block language identifier rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `all_lines` (`list[str]`): All lines from the original file.
        - `yaml_end_line` (`int`): Line number where YAML block ends (1-based).
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each code block language issue found.

        """
        if "H007" not in rules:
            return

        # Get content lines (after YAML)
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines

        # Use identify_code_blocks to determine which lines are code block delimiters
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        # Dictionary of incorrect language identifiers and their correct replacements
        incorrect_languages = {
            "console": "shell",
            "py": "python",
        }

        for i, (line, is_code_block) in enumerate(code_block_info):
            # Check if this is a code block delimiter line (starts with ```)
            if not is_code_block:
                continue

            # Check if line starts with ``` and has a language identifier
            match = re.match(r"^(`{3,})(\w+)?", line)
            if not match:
                continue

            language = match.group(2)
            if not language:
                continue

            # Check if the language identifier is incorrect
            if language in incorrect_languages:
                # Calculate actual line number in the original file
                actual_line_num = (yaml_end_line - 1) + i + 1  # Convert to 1-based

                # Find column position of the language identifier
                col = match.start(2) + 1  # +1 for 1-based column numbering

                correct_language = incorrect_languages[language]
                error_message = f'{self.RULES["H007"]}: "{language}" should be "{correct_language}"'
                yield self._format_error("H007", error_message, filename, line_num=actual_line_num, col=col)

    def _check_content_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set
    ) -> Generator[str, None, None]:
        """Check content-related rules working directly with original file lines.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `all_lines` (`list[str]`): All lines from the original file.
        - `yaml_end_line` (`int`): Line number where YAML block ends (1-based).
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each content-related issue found.

        """
        if "H006" not in rules:
            return

        # Get content lines (after YAML)
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines

        # Use identify_code_blocks to determine which lines are in code blocks
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        for i, (line, is_code_block) in enumerate(code_block_info):
            if is_code_block:
                continue

            # Calculate actual line number in the original file
            actual_line_num = (yaml_end_line - 1) + i + 1  # Convert to 1-based

            # Remove inline code from line before checking
            clean_line = ""
            for segment, in_code in h.md.identify_code_blocks_line(line):
                if not in_code:
                    clean_line += segment

            # Remove URLs from markdown links [text](url) and angle brackets <url>
            # Remove content in parentheses after square brackets (markdown links)
            clean_line = re.sub(r"\]\([^)]*\)", "]()", clean_line)
            # Remove content in angle brackets
            clean_line = re.sub(r"<[^>]*>", "<>", clean_line)

            # Check for incorrect words
            for incorrect_word, correct_word in self.INCORRECT_WORDS.items():
                # Escape special regex characters in the word
                escaped_word = re.escape(incorrect_word)

                # Check if word contains only alphanumeric and underscore characters
                # If yes, use word boundaries; otherwise use lookahead/lookbehind
                if re.match(r"^[\w]+$", incorrect_word):
                    # Standard word with word boundaries
                    pattern = rf"\b{escaped_word}\b"
                else:
                    # Word with special characters - use lookahead/lookbehind
                    # to ensure it's not part of a larger word
                    pattern = rf"(?<![a-zA-Zа-яА-ЯёЁ0-9_]){escaped_word}(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001

                # Search in clean_line for the incorrect word
                if re.search(pattern, clean_line):
                    # Find position in the original line
                    match = re.search(pattern, line)
                    col = match.start() + 1 if match else 1

                    error_message = f'{self.RULES["H006"]}: "{incorrect_word}" should be "{correct_word}"'
                    yield self._format_error("H006", error_message, filename, line_num=actual_line_num, col=col)

    def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Check filename-related rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each filename-related issue found.

        """
        if "H001" in rules and " " in filename.name:
            yield self._format_error("H001", self.RULES["H001"], filename)

        if "H002" in rules and " " in str(filename):
            yield self._format_error("H002", self.RULES["H002"], filename)

    def _check_yaml_rules(
        self, filename: Path, yaml_content: str, all_lines: list[str], rules: set
    ) -> Generator[str, None, None]:
        """Check YAML-related rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `yaml_content` (`str`): The YAML frontmatter content from the Markdown file.
        - `all_lines` (`list[str]`): All lines from the original file.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each YAML-related issue found.

        """
        try:
            data = yaml.safe_load(yaml_content.replace("---\n", "").replace("\n---", "")) if yaml_content else None

            if not data and "H003" in rules:
                yield self._format_error("H003", self.RULES["H003"], filename, line_num=1)
                return

            if data:
                lang = data.get("lang")
                if "H004" in rules and not lang:
                    # Find end of YAML block or use line 2 as default
                    line_num = self._find_yaml_block_end_line(all_lines)
                    yield self._format_error("H004", self.RULES["H004"], filename, line_num=line_num)
                elif "H005" in rules and lang and lang not in ["en", "ru"]:
                    # Find the line with lang field in original file
                    line_num = self._find_yaml_field_line_in_original(all_lines, "lang")
                    col = self._find_yaml_field_column(all_lines, line_num, "lang")
                    yield self._format_error("H005", self.RULES["H005"], filename, line_num=line_num, col=col)

        except yaml.YAMLError as e:
            yield self._format_error("H000", f"YAML parsing error: {e}", filename, line_num=1)

    def _determine_active_rules(self, select: set[str] | None, exclude_rules: set[str] | None) -> set[str]:
        """Determine which rules should be active based on select and exclude parameters.

        Args:

        - `select` (`set[str] | None`): Set of rule codes to check. If None, all rules are considered.
        - `exclude_rules` (`set[str] | None`): Set of rule codes to exclude from checking.

        Returns:

        - `set[str]`: Set of active rule codes to apply.

        """
        # Start with selected rules or all rules
        active = select & self.all_rules if select is not None else self.all_rules.copy()

        # Remove excluded rules
        if exclude_rules is not None:
            active -= exclude_rules

        return active

    def _determine_project_root(self, project_root: Path | str | None) -> Path:
        """Determine the project root directory."""
        if project_root:
            return Path(project_root).resolve()

        # Try to find git root
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        # Fallback to current working directory
        return Path.cwd()

    def _find_yaml_block_end_line(self, all_lines: list[str]) -> int:
        """Find the line number where YAML block ends (the closing --- line)."""
        if not all_lines or all_lines[0].strip() != "---":
            return 1

        for i, line in enumerate(all_lines[1:], 2):  # Start from line 2
            if line.strip() == "---":
                return i
        return len(all_lines)

    def _find_yaml_end_line(self, lines: list[str]) -> int:
        """Find the line number where YAML block ends (1-based).

        Returns:

        - `int`: Line number after YAML block, or 1 if no YAML.

        """
        if not lines or lines[0].strip() != "---":
            return 1

        for i, line in enumerate(lines[1:], 2):  # Start from line 2 (1-based)
            if line.strip() == "---":
                return i + 1  # Return line after YAML block

        return len(lines) + 1  # If no closing ---, YAML goes to end

    def _find_yaml_field_column(self, all_lines: list[str], line_num: int, field: str) -> int:
        """Find column position of field value in YAML."""
        if line_num <= len(all_lines):
            line = all_lines[line_num - 1]  # Convert to 0-based index
            match = re.search(f"{field}:\\s*(.+)", line)
            if match:
                return match.start(1) + 1  # +1 for 1-based column numbering
        return 1

    def _find_yaml_field_line_in_original(self, all_lines: list[str], field: str) -> int:
        """Find line number of a specific field in YAML content within original file."""
        if not all_lines or all_lines[0].strip() != "---":
            return 1

        # Look for field within YAML block (between first --- and second ---)
        for i, line in enumerate(all_lines[1:], 2):  # Start from line 2
            if line.strip() == "---":  # End of YAML block
                break
            if line.strip().startswith(f"{field}:"):
                return i

        return 2  # Default to line 2 if not found

    def _format_error(self, error_code: str, message: str, filename: Path, *, line_num: int = 0, col: int = 0) -> str:
        """Format error message in ruff style.

        Args:

        - `error_code` (`str`): The error code (e.g., "H001").
        - `message` (`str`): Description of the error.
        - `filename` (`Path`): Path to the file where the error was found.
        - `line_num` (`int`): Line number where the error occurred. Defaults to `0`.
        - `col` (`int`): Column number where the error occurred. Defaults to `0`.

        Returns:

        - `str`: Formatted error message in ruff style.

        """
        relative_path = self._get_relative_path(filename)

        location = relative_path
        if line_num > 0:
            location += f":{line_num}"
            if col > 0:
                location += f":{col}"

        return f"{location}: {error_code} {message}"

    def _get_relative_path(self, filename: Path) -> str:
        """Get relative path from project root, fallback to absolute if outside project."""
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            # File is outside project root
            return str(filename.resolve())
