---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `markdown_checker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MarkdownChecker`](#%EF%B8%8F-class-markdownchecker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `__call__`](#%EF%B8%8F-method-__call__)
  - [⚙️ Method `check`](#%EF%B8%8F-method-check)
  - [⚙️ Method `check_directory`](#%EF%B8%8F-method-check_directory)
  - [⚙️ Method `find_markdown_files`](#%EF%B8%8F-method-find_markdown_files)
  - [⚙️ Method `_check_all_lines_rules`](#%EF%B8%8F-method-_check_all_lines_rules)
  - [⚙️ Method `_check_all_rules`](#%EF%B8%8F-method-_check_all_rules)
  - [⚙️ Method `_check_code_rules`](#%EF%B8%8F-method-_check_code_rules)
  - [⚙️ Method `_check_colon_before_code`](#%EF%B8%8F-method-_check_colon_before_code)
  - [⚙️ Method `_check_colon_before_image`](#%EF%B8%8F-method-_check_colon_before_image)
  - [⚙️ Method `_check_content_rules`](#%EF%B8%8F-method-_check_content_rules)
  - [⚙️ Method `_check_dash_usage`](#%EF%B8%8F-method-_check_dash_usage)
  - [⚙️ Method `_check_double_spaces`](#%EF%B8%8F-method-_check_double_spaces)
  - [⚙️ Method `_check_file_level_rules`](#%EF%B8%8F-method-_check_file_level_rules)
  - [⚙️ Method `_check_filename_rules`](#%EF%B8%8F-method-_check_filename_rules)
  - [⚙️ Method `_check_html_tags`](#%EF%B8%8F-method-_check_html_tags)
  - [⚙️ Method `_check_image_caption`](#%EF%B8%8F-method-_check_image_caption)
  - [⚙️ Method `_check_incorrect_words`](#%EF%B8%8F-method-_check_incorrect_words)
  - [⚙️ Method `_check_lowercase_after_punctuation`](#%EF%B8%8F-method-_check_lowercase_after_punctuation)
  - [⚙️ Method `_check_non_code_line_rules`](#%EF%B8%8F-method-_check_non_code_line_rules)
  - [⚙️ Method `_check_quotes`](#%EF%B8%8F-method-_check_quotes)
  - [⚙️ Method `_check_space_before_punctuation`](#%EF%B8%8F-method-_check_space_before_punctuation)
  - [⚙️ Method `_check_yaml_rules`](#%EF%B8%8F-method-_check_yaml_rules)
  - [⚙️ Method `_determine_active_rules`](#%EF%B8%8F-method-_determine_active_rules)
  - [⚙️ Method `_determine_project_root`](#%EF%B8%8F-method-_determine_project_root)
  - [⚙️ Method `_find_yaml_block_end_line`](#%EF%B8%8F-method-_find_yaml_block_end_line)
  - [⚙️ Method `_find_yaml_end_line`](#%EF%B8%8F-method-_find_yaml_end_line)
  - [⚙️ Method `_find_yaml_field_column`](#%EF%B8%8F-method-_find_yaml_field_column)
  - [⚙️ Method `_find_yaml_field_line_in_original`](#%EF%B8%8F-method-_find_yaml_field_line_in_original)
  - [⚙️ Method `_format_error`](#%EF%B8%8F-method-_format_error)
  - [⚙️ Method `_get_relative_path`](#%EF%B8%8F-method-_get_relative_path)
  - [⚙️ Method `_remove_inline_code`](#%EF%B8%8F-method-_remove_inline_code)
  - [⚙️ Method `_should_check_paragraph_end`](#%EF%B8%8F-method-_should_check_paragraph_end)

</details>

## 🏛️ Class `MarkdownChecker`

```python
class MarkdownChecker
```

Class for checking Markdown files for compliance with specified rules.

Rules:

- **H001** - Presence of a space in the Markdown file name.
- **H002** - Presence of a space in the path to the Markdown file.
- **H003** - YAML is missing.
- **H004** - The lang field is missing in YAML.
- **H005** - In YAML, lang is not set to `en` or `ru`.
- **H006** - Incorrect word form used (e.g., "markdown" instead of "Markdown").
- **H007** - Incorrect code block language identifier.
- **H008** - Trailing whitespace at end of line.
- **H009** - Double spaces in line (not in code blocks).
- **H010** - Tab character found.
- **H011** - No empty line at end of file.
- **H012** - Two consecutive empty lines.
- **H013** - Missing colon before code block.
- **H014** - Missing colon before image.
- **H015** - Space before punctuation mark.
- **H016** - Incorrect dash/hyphen usage.
- **H017** - Three dots instead of ellipsis character.
- **H018** - Curly/straight quotes instead of angle quotes.
- **H019** - HTML tags in markdown content.
- **H020** - Image caption starts with lowercase letter.
- **H021** - Lowercase letter after sentence-ending punctuation.
- **H022** - Non-breaking space character found.
- **H023** - Incorrect dash characters in code blocks.

<details>
<summary>Code:</summary>

````python
class MarkdownChecker:

    # Rule constants for easier maintenance
    RULES: ClassVar[dict[str, str]] = {
        "H001": "Presence of a space in the Markdown file name",
        "H002": "Presence of a space in the path to the Markdown file",
        "H003": "YAML is missing",
        "H004": "The lang field is missing in YAML",
        "H005": "In YAML, lang is not set to en or ru",
        "H006": "Incorrect word form used",
        "H007": "Incorrect code block language identifier",
        "H008": "Trailing whitespace at end of line",
        "H009": "Double spaces in line",
        "H010": "Tab character found",
        "H011": "No empty line at end of file",
        "H012": "Two consecutive empty lines",
        "H013": "Missing colon before code block",
        "H014": "Missing colon before image",
        "H015": "Space before punctuation mark",
        "H016": "Incorrect dash/hyphen usage",
        "H017": "Three dots instead of ellipsis character",
        "H018": "Curly/straight quotes instead of angle quotes",
        "H019": "HTML tags in markdown content",
        "H020": "Image caption starts with lowercase letter",
        "H021": "Lowercase letter after sentence-ending punctuation",
        "H022": "Non-breaking space character found",
        "H023": "Incorrect dash characters in code blocks",
    }

    # Dictionary of incorrect word forms that should be flagged
    INCORRECT_WORDS: ClassVar[dict[str, str]] = {
        # LaTeX variations
        "Latex": "LaTeX",
        "latex": "LaTeX",
        # Email
        "e-mail": "email",
        # CMS with Cyrillic letters
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

    # Incorrect code block language identifiers
    INCORRECT_LANGUAGES: ClassVar[dict[str, str]] = {
        "console": "shell",
        "py": "python",
    }

    # HTML tags that should not appear in markdown content
    FORBIDDEN_HTML_TAGS: ClassVar[list[str]] = [
        "<pre class",
        "<table",
        "<strong",
        "<b>",
        "<b ",
        "<a>",
        "<a ",
        "<i>",
        "<i ",
        "<p>",
        "<p ",
        "<h1",
        "<h2",
        "<h3",
        "<h4",
        "<h5",
        "<h6",
        "</",
    ]

    # Incorrect dash characters in code blocks
    INCORRECT_CODE_DASHES: ClassVar[dict[str, str]] = {
        "―": "horizontal bar",
        "—": "em dash",
        "‒": "figure dash",  # noqa: RUF001
        "−": "minus sign",  # noqa: RUF001
        "‐": "hyphen",  # noqa: RUF001
    }

    def __init__(self, project_root: Path | str | None = None) -> None:
        """Initialize the MarkdownChecker with all available rules."""
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
        """Check Markdown file for compliance with specified rules."""
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
        """Check all Markdown files in directory for compliance with specified rules."""
        results = {}
        for md_file in self.find_markdown_files(directory, additional_ignore_patterns):
            errors = self.check(md_file, select=select, exclude_rules=exclude_rules)
            if errors:
                results[str(md_file)] = errors
        return results

    def find_markdown_files(
        self, directory: Path | str, additional_ignore_patterns: list[str] | None = None
    ) -> Generator[Path, None, None]:
        """Find all Markdown files in directory, ignoring hidden folders."""
        directory = Path(directory)
        if not directory.is_dir():
            return
        if h.file.should_ignore_path(directory, additional_ignore_patterns):
            return
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in {".md", ".markdown"}:
                yield item
            elif item.is_dir() and not h.file.should_ignore_path(item, additional_ignore_patterns):
                yield from self.find_markdown_files(item, additional_ignore_patterns)

    def _check_all_lines_rules(
        self, filename: Path, line: str, line_num: int, rules: set
    ) -> Generator[str, None, None]:
        """Check rules that apply to all lines including code blocks."""
        # H008: Trailing whitespace
        if "H008" in rules and line != line.rstrip():
            col = len(line.rstrip()) + 1
            yield self._format_error("H008", self.RULES["H008"], filename, line_num=line_num, col=col)

        # H010: Tab character
        if "H010" in rules and "\t" in line:
            col = line.index("\t") + 1
            yield self._format_error("H010", self.RULES["H010"], filename, line_num=line_num, col=col)

        # H022: Non-breaking space
        if "H022" in rules and "\u00a0" in line:
            col = line.index("\u00a0") + 1
            yield self._format_error("H022", self.RULES["H022"], filename, line_num=line_num, col=col)

    def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Generate all errors found during checking."""
        yield from self._check_filename_rules(filename, rules)

        try:
            content = filename.read_text(encoding="utf-8")
            all_lines = content.splitlines()
            yaml_end_line = self._find_yaml_end_line(all_lines)
            yaml_part, _ = h.md.split_yaml_content(content)

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules)
            yield from self._check_content_rules(filename, all_lines, yaml_end_line, rules, content)
            yield from self._check_code_rules(filename, all_lines, yaml_end_line, rules)

        except Exception as e:
            yield self._format_error("H000", f"Exception error: {e}", filename)

    # =========================================================================
    # Code Block Rules (H007, H023)
    # =========================================================================

    def _check_code_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set
    ) -> Generator[str, None, None]:
        """Check code block related rules."""
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        in_code_block = False
        for i, (line, _is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1

            # H007: Incorrect code block language identifier
            if "H007" in rules and line.strip().startswith("```"):
                match = re.match(r"^(`{3,})(\w+)?", line)
                if match:
                    language = match.group(2)
                    if language and language in self.INCORRECT_LANGUAGES:
                        col = match.start(2) + 1
                        correct = self.INCORRECT_LANGUAGES[language]
                        error_msg = f'{self.RULES["H007"]}: "{language}" should be "{correct}"'
                        yield self._format_error("H007", error_msg, filename, line_num=actual_line_num, col=col)

            # Track code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # H023: Incorrect dash characters in code blocks
            if "H023" in rules and in_code_block:
                for char, name in self.INCORRECT_CODE_DASHES.items():
                    if char in line:
                        col = line.index(char) + 1
                        error_msg = f'{self.RULES["H023"]}: found "{char}" ({name}) in code block'
                        yield self._format_error("H023", error_msg, filename, line_num=actual_line_num, col=col)

    def _check_colon_before_code(
        self,
        filename: Path,
        line: str,
        line_num: int,
        _content_lines: list[str],
        line_index: int,
        code_block_info: list,
    ) -> Generator[str, None, None]:
        """Check for missing colon before code block (H013)."""
        if line_index + 2 >= len(code_block_info):
            return

        # Check if next non-empty line is a code block start
        next_line_info = code_block_info[line_index + 1] if line_index + 1 < len(code_block_info) else None
        next_next_info = code_block_info[line_index + 2] if line_index + 2 < len(code_block_info) else None

        if not next_line_info or not next_next_info:
            return

        next_line, _ = next_line_info
        next_next_line, _ = next_next_info

        # Check pattern: non-empty line, empty line, code block start
        if not self._should_check_paragraph_end(line):
            return

        if next_line.strip() == "" and next_next_line.strip().startswith("```"):
            last_char = line.rstrip()[-1] if line.rstrip() else ""

            # Skip exceptions
            if any(
                marker in line
                for marker in [
                    "[!DETAILS]",
                    "[!WARNING]",
                    "[!IMPORTANT]",
                    "[!NOTE]",
                    "<!-- !details -->",
                    "<!-- !note -->",
                    "<!-- !important -->",
                    "<!-- !warning -->",
                ]
            ):
                return

            if line.strip().startswith("<"):
                return

            if last_char != ":":
                error_msg = f'{self.RULES["H013"]}: last char is "{last_char}"'
                yield self._format_error("H013", error_msg, filename, line_num=line_num, col=len(line.rstrip()))

    def _check_colon_before_image(
        self, filename: Path, line: str, line_num: int, content_lines: list[str], line_index: int
    ) -> Generator[str, None, None]:
        """Check for missing colon before image (H014)."""
        if line_index + 2 >= len(content_lines):
            return

        if not self._should_check_paragraph_end(line):
            return

        next_line = content_lines[line_index + 1]
        next_next_line = content_lines[line_index + 2]

        # Check pattern: non-empty line, empty line, image
        if next_line.strip() == "" and next_next_line.strip().startswith("!["):
            last_char = line.rstrip()[-1] if line.rstrip() else ""

            # Skip exceptions
            if any(
                marker in line
                for marker in ["<!-- !details -->", "<!-- !note -->", "<!-- !important -->", "<!-- !warning -->"]
            ):
                return

            if line.strip().startswith("<"):
                return

            if last_char != ":":
                error_msg = f'{self.RULES["H014"]}: last char is "{last_char}"'
                yield self._format_error("H014", error_msg, filename, line_num=line_num, col=len(line.rstrip()))

    # =========================================================================
    # Content Rules (H006, H008-H022) - for non-code content
    # =========================================================================

    def _check_content_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set, content: str = ""
    ) -> Generator[str, None, None]:
        """Check content-related rules working directly with original file lines."""
        # Get content lines (after YAML)
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines

        # Use identify_code_blocks to determine which lines are in code blocks
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        # Check file-level rules
        yield from self._check_file_level_rules(filename, all_lines, rules, content)

        # Check line-by-line rules
        for i, (line, is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1

            # Rules that apply to ALL lines (including code blocks)
            yield from self._check_all_lines_rules(filename, line, actual_line_num, rules)

            # Rules that apply only to NON-code lines
            if not is_code_block:
                yield from self._check_non_code_line_rules(
                    filename, line, actual_line_num, content_lines, i, code_block_info, rules
                )

    def _check_dash_usage(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for incorrect dash/hyphen usage (H016)."""
        # Check for " - " (hyphen with spaces should be em dash)
        if " - " in clean_line and not clean_line.strip().startswith("-"):
            pos = line.find(" - ") if " - " in line else clean_line.find(" - ")
            error_msg = f'{self.RULES["H016"]}: " - " should be " — " (em dash)'
            yield self._format_error("H016", error_msg, filename, line_num=line_num, col=pos + 1)

        # Check for en dash not between digits
        if "–" in clean_line:  # noqa: RUF001
            line_matches = list(re.finditer(r"–", line))  # noqa: RUF001
            for i, match in enumerate(re.finditer(r"–", clean_line)):  # noqa: RUF001
                pos = match.start()
                before = clean_line[pos - 1] if pos > 0 else ""
                after = clean_line[pos + 1] if pos + 1 < len(clean_line) else ""
                if not (before.isdigit() and after.isdigit()):
                    col_pos = line_matches[i].start() if i < len(line_matches) else pos
                    error_msg = f'{self.RULES["H016"]}: en dash "–" should only be between digits'  # noqa: RUF001
                    yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)

        # Check for em dash not between spaces
        if "—" in clean_line:
            line_matches = list(re.finditer(r"—", line))
            for i, match in enumerate(re.finditer(r"—", clean_line)):
                pos = match.start()
                before = clean_line[pos - 1] if pos > 0 else " "
                after = clean_line[pos + 1] if pos + 1 < len(clean_line) else " "
                col_pos = line_matches[i].start() if i < len(line_matches) else pos
                # Em dash should have spaces around it (or be at line start for dialogue)
                if pos == 0:
                    if after != " ":
                        error_msg = f'{self.RULES["H016"]}: em dash "—" at start should be followed by space'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)
                elif not (before == " " and after == " "):
                    error_msg = f'{self.RULES["H016"]}: em dash "—" should have spaces around it'
                    yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)

    def _check_double_spaces(
        self, filename: Path, line: str, clean_line: str, line_num: int, content_lines: list[str], line_index: int
    ) -> Generator[str, None, None]:
        """Check for double spaces (H009)."""
        if "  " not in clean_line:
            return

        # Skip if line starts with list indentation
        if line.startswith(("  ", "  *", "  -")):
            return

        # Skip if previous line is a list item
        if line_index > 0:
            prev_line = content_lines[line_index - 1]
            if prev_line.strip().startswith("*") or prev_line.strip().startswith("-"):
                return

        # Skip table lines
        if line.strip().startswith("|"):
            return

        col = clean_line.index("  ") + 1
        yield self._format_error("H009", self.RULES["H009"], filename, line_num=line_num, col=col)

    def _check_file_level_rules(
        self, filename: Path, all_lines: list[str], rules: set, content: str = ""
    ) -> Generator[str, None, None]:
        """Check rules that apply to the entire file."""
        # H011: No empty line at end of file
        if "H011" in rules and all_lines and not content.endswith("\n"):
            yield self._format_error("H011", self.RULES["H011"], filename, line_num=len(all_lines))

        # H012: Two consecutive empty lines
        if "H012" in rules:
            for i in range(len(all_lines) - 1):
                if not all_lines[i].strip() and not all_lines[i + 1].strip() and i > 0 and i + 1 < len(all_lines) - 1:
                    yield self._format_error("H012", self.RULES["H012"], filename, line_num=i + 1)

    # =========================================================================
    # Filename Rules (H001, H002)
    # =========================================================================

    def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Check filename-related rules."""
        if "H001" in rules and " " in filename.name:
            yield self._format_error("H001", self.RULES["H001"], filename)

        if "H002" in rules and " " in str(filename):
            yield self._format_error("H002", self.RULES["H002"], filename)

    def _check_html_tags(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for HTML tags in content (H019)."""
        for tag in self.FORBIDDEN_HTML_TAGS:
            if tag.lower() in line.lower():
                pos = line.lower().find(tag.lower())
                error_msg = f'{self.RULES["H019"]}: found "{tag}"'
                yield self._format_error("H019", error_msg, filename, line_num=line_num, col=pos + 1)

    def _check_image_caption(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check that image captions start with uppercase (H020)."""
        if not line.strip().startswith("!["):
            return

        match = re.match(r"!\[([^\]]*)\]", line.strip())
        if match:
            caption = match.group(1)
            if caption and caption[0].isalpha() and caption[0].islower():
                error_msg = f'{self.RULES["H020"]}: caption starts with "{caption[0]}"'
                yield self._format_error("H020", error_msg, filename, line_num=line_num, col=3)

    def _check_incorrect_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for incorrect word forms (H006)."""
        for incorrect_word, correct_word in self.INCORRECT_WORDS.items():
            escaped_word = re.escape(incorrect_word)
            if re.match(r"^[\w]+$", incorrect_word):
                pattern = rf"\b{escaped_word}\b"
            else:
                pattern = rf"(?<![a-zA-Zа-яА-ЯёЁ0-9_]){escaped_word}(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001

            if re.search(pattern, clean_line):
                match = re.search(pattern, line)
                col = match.start() + 1 if match else 1
                error_message = f'{self.RULES["H006"]}: "{incorrect_word}" should be "{correct_word}"'
                yield self._format_error("H006", error_message, filename, line_num=line_num, col=col)

    def _check_lowercase_after_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for lowercase letter after sentence-ending punctuation (H021)."""
        # Pattern: sentence end punctuation, space, lowercase letter
        pattern = r"[.!?]\s+([a-zа-яё])"  # noqa: RUF001  # ignore: HP001

        for match in re.finditer(pattern, clean_line):
            letter = match.group(1)
            pos = match.start()

            # Check for exceptions like "e.g. ", "т. е.", "т. д."  # noqa: RUF003  # ignore: HP001
            context_before = clean_line[max(0, pos - 4) : pos + 1]
            exceptions = ["e.g.", "i.e.", "т. е", "т. д", "т. ч", "т. п"]  # noqa: RUF001  # ignore: HP001
            if any(exc in context_before for exc in exceptions):
                continue

            line_match = re.search(re.escape(match.group(0)), line)
            offset = match.start(1) - match.start(0)
            col = line_match.start(0) + offset + 1 if line_match else match.start(1) + 1

            error_msg = f'{self.RULES["H021"]}: found lowercase "{letter}" after punctuation'
            yield self._format_error("H021", error_msg, filename, line_num=line_num, col=col)

    def _check_non_code_line_rules(
        self,
        filename: Path,
        line: str,
        line_num: int,
        content_lines: list[str],
        line_index: int,
        code_block_info: list,
        rules: set,
    ) -> Generator[str, None, None]:
        """Check rules that apply only to non-code lines."""
        # Remove inline code from line before checking text rules
        clean_line = self._remove_inline_code(line)
        # Remove URLs from markdown links
        clean_line = re.sub(r"\]\([^)]*\)", "]()", clean_line)
        clean_line = re.sub(r"<[^>]*>", "<>", clean_line)

        # H006: Incorrect word forms
        if "H006" in rules:
            yield from self._check_incorrect_words(filename, line, clean_line, line_num)

        # H009: Double spaces
        if "H009" in rules:
            yield from self._check_double_spaces(filename, line, clean_line, line_num, content_lines, line_index)

        # H013: Missing colon before code block
        if "H013" in rules:
            yield from self._check_colon_before_code(
                filename, line, line_num, content_lines, line_index, code_block_info
            )

        # H014: Missing colon before image
        if "H014" in rules:
            yield from self._check_colon_before_image(filename, line, line_num, content_lines, line_index)

        # H015: Space before punctuation
        if "H015" in rules:
            yield from self._check_space_before_punctuation(filename, line, clean_line, line_num)

        # H016: Incorrect dash/hyphen usage
        if "H016" in rules:
            yield from self._check_dash_usage(filename, line, clean_line, line_num)

        # H017: Three dots instead of ellipsis
        if "H017" in rules and "..." in clean_line:
            col = line.index("...") + 1 if "..." in line else clean_line.index("...") + 1
            error_msg = f'{self.RULES["H017"]}: "..." should be "…"'
            yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)

        # H018: Curly/straight quotes
        if "H018" in rules:
            yield from self._check_quotes(filename, line, clean_line, line_num)

        # H019: HTML tags
        if "H019" in rules:
            yield from self._check_html_tags(filename, line, clean_line, line_num)

        # H020: Image caption lowercase
        if "H020" in rules:
            yield from self._check_image_caption(filename, line, line_num)

        # H021: Lowercase after sentence end
        if "H021" in rules:
            yield from self._check_lowercase_after_punctuation(filename, line, clean_line, line_num)

    def _check_quotes(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]:
        """Check for incorrect quote characters (H018)."""
        incorrect_quotes = [
            ('"', 'straight double quote "'),
            ("\u201c", "curly quote \u201c"),
            ("\u201d", "curly quote \u201d"),
            ("« ", "space after «"),
            (" »", "space before »"),
        ]

        for char, description in incorrect_quotes:
            if char in clean_line:
                pos = line.find(char) if char in line else clean_line.find(char)
                error_msg = f"{self.RULES['H018']}: found {description}"
                yield self._format_error("H018", error_msg, filename, line_num=line_num, col=pos + 1)

    def _check_space_before_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for space before punctuation marks (H015)."""
        patterns = [
            (r" \.", " ."),
            (r" ,", " ,"),
            (r" ;", " ;"),
            (r" :", " :"),
            (r" \?", " ?"),
        ]

        for pattern, display in patterns:
            match = re.search(pattern, clean_line)
            if match:
                line_match = re.search(pattern, line)
                col = line_match.start() + 1 if line_match else match.start() + 1
                error_msg = f'{self.RULES["H015"]}: found "{display}"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=col)

        # Special handling for " !" - skip special markers
        if " !" in clean_line:
            exceptions = [" !details", " !note", " !important", " !warning"]
            pos = clean_line.find(" !")
            if not any(clean_line[pos:].startswith(exc) for exc in exceptions) and not clean_line.strip().startswith(
                "!"
            ):
                line_pos = line.find(" !") if " !" in line else pos
                error_msg = f'{self.RULES["H015"]}: found " !"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=line_pos + 1)

    # =========================================================================
    # YAML Rules (H003-H005)
    # =========================================================================

    def _check_yaml_rules(
        self, filename: Path, yaml_content: str, all_lines: list[str], rules: set
    ) -> Generator[str, None, None]:
        """Check YAML-related rules."""
        try:
            data = yaml.safe_load(yaml_content.replace("---\n", "").replace("\n---", "")) if yaml_content else None

            if not data and "H003" in rules:
                yield self._format_error("H003", self.RULES["H003"], filename, line_num=1)
                return

            if data:
                lang = data.get("lang")
                if "H004" in rules and not lang:
                    line_num = self._find_yaml_block_end_line(all_lines)
                    yield self._format_error("H004", self.RULES["H004"], filename, line_num=line_num)
                elif "H005" in rules and lang and lang not in ["en", "ru"]:
                    line_num = self._find_yaml_field_line_in_original(all_lines, "lang")
                    col = self._find_yaml_field_column(all_lines, line_num, "lang")
                    yield self._format_error("H005", self.RULES["H005"], filename, line_num=line_num, col=col)

        except yaml.YAMLError as e:
            yield self._format_error("H000", f"YAML parsing error: {e}", filename, line_num=1)

    def _determine_active_rules(self, select: set[str] | None, exclude_rules: set[str] | None) -> set[str]:
        """Determine which rules should be active."""
        active = select & self.all_rules if select is not None else self.all_rules.copy()
        if exclude_rules is not None:
            active -= exclude_rules
        return active

    def _determine_project_root(self, project_root: Path | str | None) -> Path:
        """Determine the project root directory."""
        if project_root:
            return Path(project_root).resolve()
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()

    def _find_yaml_block_end_line(self, all_lines: list[str]) -> int:
        """Find the line number where YAML block ends."""
        if not all_lines or all_lines[0].strip() != "---":
            return 1
        for i, line in enumerate(all_lines[1:], 2):
            if line.strip() == "---":
                return i
        return len(all_lines)

    def _find_yaml_end_line(self, lines: list[str]) -> int:
        """Find the line number where YAML block ends (1-based)."""
        if not lines or lines[0].strip() != "---":
            return 1
        for i, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                return i + 1
        return len(lines) + 1

    def _find_yaml_field_column(self, all_lines: list[str], line_num: int, field: str) -> int:
        """Find column position of field value in YAML."""
        if line_num <= len(all_lines):
            line = all_lines[line_num - 1]
            match = re.search(f"{field}:\\s*(.+)", line)
            if match:
                return match.start(1) + 1
        return 1

    def _find_yaml_field_line_in_original(self, all_lines: list[str], field: str) -> int:
        """Find line number of a specific field in YAML content."""
        if not all_lines or all_lines[0].strip() != "---":
            return 1
        for i, line in enumerate(all_lines[1:], 2):
            if line.strip() == "---":
                break
            if line.strip().startswith(f"{field}:"):
                return i
        return 2

    def _format_error(self, error_code: str, message: str, filename: Path, *, line_num: int = 0, col: int = 0) -> str:
        """Format error message in ruff style."""
        relative_path = self._get_relative_path(filename)
        location = relative_path
        if line_num > 0:
            location += f":{line_num}"
            if col > 0:
                location += f":{col}"
        return f"{location}: {error_code} {message}"

    def _get_relative_path(self, filename: Path) -> str:
        """Get relative path from project root."""
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            return str(filename.resolve())

    def _remove_inline_code(self, line: str) -> str:
        """Remove inline code segments from line."""
        clean_line = ""
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                clean_line += segment
        return clean_line

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _should_check_paragraph_end(self, line: str) -> bool:
        """Check if line is a regular paragraph that should end with colon before code/image."""
        if not line.strip():
            return False
        if line.strip() == "```":
            return False
        if line.strip().startswith("!["):
            return False
        return not line.strip().startswith("#")
````

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, project_root: Path | str | None = None) -> None
```

Initialize the MarkdownChecker with all available rules.

<details>
<summary>Code:</summary>

```python
def __init__(self, project_root: Path | str | None = None) -> None:
        self.all_rules = set(self.RULES.keys())
        self.project_root = self._determine_project_root(project_root)
```

</details>

### ⚙️ Method `__call__`

```python
def __call__(self, filename: Path | str) -> list[str]
```

Check Markdown file for compliance with specified rules.

<details>
<summary>Code:</summary>

```python
def __call__(
        self, filename: Path | str, *, select: set[str] | None = None, exclude_rules: set[str] | None = None
    ) -> list[str]:
        return self.check(filename, select=select, exclude_rules=exclude_rules)
```

</details>

### ⚙️ Method `check`

```python
def check(self, filename: Path | str) -> list[str]
```

Check Markdown file for compliance with specified rules.

<details>
<summary>Code:</summary>

```python
def check(
        self, filename: Path | str, *, select: set[str] | None = None, exclude_rules: set[str] | None = None
    ) -> list[str]:
        filename = Path(filename)
        active_rules = self._determine_active_rules(select, exclude_rules)
        return list(self._check_all_rules(filename, active_rules))
```

</details>

### ⚙️ Method `check_directory`

```python
def check_directory(self, directory: Path | str) -> dict[str, list[str]]
```

Check all Markdown files in directory for compliance with specified rules.

<details>
<summary>Code:</summary>

```python
def check_directory(
        self,
        directory: Path | str,
        *,
        select: set[str] | None = None,
        exclude_rules: set[str] | None = None,
        additional_ignore_patterns: list[str] | None = None,
    ) -> dict[str, list[str]]:
        results = {}
        for md_file in self.find_markdown_files(directory, additional_ignore_patterns):
            errors = self.check(md_file, select=select, exclude_rules=exclude_rules)
            if errors:
                results[str(md_file)] = errors
        return results
```

</details>

### ⚙️ Method `find_markdown_files`

```python
def find_markdown_files(self, directory: Path | str, additional_ignore_patterns: list[str] | None = None) -> Generator[Path, None, None]
```

Find all Markdown files in directory, ignoring hidden folders.

<details>
<summary>Code:</summary>

```python
def find_markdown_files(
        self, directory: Path | str, additional_ignore_patterns: list[str] | None = None
    ) -> Generator[Path, None, None]:
        directory = Path(directory)
        if not directory.is_dir():
            return
        if h.file.should_ignore_path(directory, additional_ignore_patterns):
            return
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in {".md", ".markdown"}:
                yield item
            elif item.is_dir() and not h.file.should_ignore_path(item, additional_ignore_patterns):
                yield from self.find_markdown_files(item, additional_ignore_patterns)
```

</details>

### ⚙️ Method `_check_all_lines_rules`

```python
def _check_all_lines_rules(self, filename: Path, line: str, line_num: int, rules: set) -> Generator[str, None, None]
```

Check rules that apply to all lines including code blocks.

<details>
<summary>Code:</summary>

```python
def _check_all_lines_rules(
        self, filename: Path, line: str, line_num: int, rules: set
    ) -> Generator[str, None, None]:
        # H008: Trailing whitespace
        if "H008" in rules and line != line.rstrip():
            col = len(line.rstrip()) + 1
            yield self._format_error("H008", self.RULES["H008"], filename, line_num=line_num, col=col)

        # H010: Tab character
        if "H010" in rules and "\t" in line:
            col = line.index("\t") + 1
            yield self._format_error("H010", self.RULES["H010"], filename, line_num=line_num, col=col)

        # H022: Non-breaking space
        if "H022" in rules and "\u00a0" in line:
            col = line.index("\u00a0") + 1
            yield self._format_error("H022", self.RULES["H022"], filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_all_rules`

```python
def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]
```

Generate all errors found during checking.

<details>
<summary>Code:</summary>

```python
def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        yield from self._check_filename_rules(filename, rules)

        try:
            content = filename.read_text(encoding="utf-8")
            all_lines = content.splitlines()
            yaml_end_line = self._find_yaml_end_line(all_lines)
            yaml_part, _ = h.md.split_yaml_content(content)

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules)
            yield from self._check_content_rules(filename, all_lines, yaml_end_line, rules, content)
            yield from self._check_code_rules(filename, all_lines, yaml_end_line, rules)

        except Exception as e:
            yield self._format_error("H000", f"Exception error: {e}", filename)
```

</details>

### ⚙️ Method `_check_code_rules`

```python
def _check_code_rules(self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set) -> Generator[str, None, None]
```

Check code block related rules.

<details>
<summary>Code:</summary>

````python
def _check_code_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set
    ) -> Generator[str, None, None]:
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        in_code_block = False
        for i, (line, _is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1

            # H007: Incorrect code block language identifier
            if "H007" in rules and line.strip().startswith("```"):
                match = re.match(r"^(`{3,})(\w+)?", line)
                if match:
                    language = match.group(2)
                    if language and language in self.INCORRECT_LANGUAGES:
                        col = match.start(2) + 1
                        correct = self.INCORRECT_LANGUAGES[language]
                        error_msg = f'{self.RULES["H007"]}: "{language}" should be "{correct}"'
                        yield self._format_error("H007", error_msg, filename, line_num=actual_line_num, col=col)

            # Track code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # H023: Incorrect dash characters in code blocks
            if "H023" in rules and in_code_block:
                for char, name in self.INCORRECT_CODE_DASHES.items():
                    if char in line:
                        col = line.index(char) + 1
                        error_msg = f'{self.RULES["H023"]}: found "{char}" ({name}) in code block'
                        yield self._format_error("H023", error_msg, filename, line_num=actual_line_num, col=col)
````

</details>

### ⚙️ Method `_check_colon_before_code`

```python
def _check_colon_before_code(self, filename: Path, line: str, line_num: int, _content_lines: list[str], line_index: int, code_block_info: list) -> Generator[str, None, None]
```

Check for missing colon before code block (H013).

<details>
<summary>Code:</summary>

````python
def _check_colon_before_code(
        self,
        filename: Path,
        line: str,
        line_num: int,
        _content_lines: list[str],
        line_index: int,
        code_block_info: list,
    ) -> Generator[str, None, None]:
        if line_index + 2 >= len(code_block_info):
            return

        # Check if next non-empty line is a code block start
        next_line_info = code_block_info[line_index + 1] if line_index + 1 < len(code_block_info) else None
        next_next_info = code_block_info[line_index + 2] if line_index + 2 < len(code_block_info) else None

        if not next_line_info or not next_next_info:
            return

        next_line, _ = next_line_info
        next_next_line, _ = next_next_info

        # Check pattern: non-empty line, empty line, code block start
        if not self._should_check_paragraph_end(line):
            return

        if next_line.strip() == "" and next_next_line.strip().startswith("```"):
            last_char = line.rstrip()[-1] if line.rstrip() else ""

            # Skip exceptions
            if any(
                marker in line
                for marker in [
                    "[!DETAILS]",
                    "[!WARNING]",
                    "[!IMPORTANT]",
                    "[!NOTE]",
                    "<!-- !details -->",
                    "<!-- !note -->",
                    "<!-- !important -->",
                    "<!-- !warning -->",
                ]
            ):
                return

            if line.strip().startswith("<"):
                return

            if last_char != ":":
                error_msg = f'{self.RULES["H013"]}: last char is "{last_char}"'
                yield self._format_error("H013", error_msg, filename, line_num=line_num, col=len(line.rstrip()))
````

</details>

### ⚙️ Method `_check_colon_before_image`

```python
def _check_colon_before_image(self, filename: Path, line: str, line_num: int, content_lines: list[str], line_index: int) -> Generator[str, None, None]
```

Check for missing colon before image (H014).

<details>
<summary>Code:</summary>

```python
def _check_colon_before_image(
        self, filename: Path, line: str, line_num: int, content_lines: list[str], line_index: int
    ) -> Generator[str, None, None]:
        if line_index + 2 >= len(content_lines):
            return

        if not self._should_check_paragraph_end(line):
            return

        next_line = content_lines[line_index + 1]
        next_next_line = content_lines[line_index + 2]

        # Check pattern: non-empty line, empty line, image
        if next_line.strip() == "" and next_next_line.strip().startswith("!["):
            last_char = line.rstrip()[-1] if line.rstrip() else ""

            # Skip exceptions
            if any(
                marker in line
                for marker in ["<!-- !details -->", "<!-- !note -->", "<!-- !important -->", "<!-- !warning -->"]
            ):
                return

            if line.strip().startswith("<"):
                return

            if last_char != ":":
                error_msg = f'{self.RULES["H014"]}: last char is "{last_char}"'
                yield self._format_error("H014", error_msg, filename, line_num=line_num, col=len(line.rstrip()))
```

</details>

### ⚙️ Method `_check_content_rules`

```python
def _check_content_rules(self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set, content: str = "") -> Generator[str, None, None]
```

Check content-related rules working directly with original file lines.

<details>
<summary>Code:</summary>

```python
def _check_content_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set, content: str = ""
    ) -> Generator[str, None, None]:
        # Get content lines (after YAML)
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines

        # Use identify_code_blocks to determine which lines are in code blocks
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        # Check file-level rules
        yield from self._check_file_level_rules(filename, all_lines, rules, content)

        # Check line-by-line rules
        for i, (line, is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1

            # Rules that apply to ALL lines (including code blocks)
            yield from self._check_all_lines_rules(filename, line, actual_line_num, rules)

            # Rules that apply only to NON-code lines
            if not is_code_block:
                yield from self._check_non_code_line_rules(
                    filename, line, actual_line_num, content_lines, i, code_block_info, rules
                )
```

</details>

### ⚙️ Method `_check_dash_usage`

```python
def _check_dash_usage(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for incorrect dash/hyphen usage (H016).

<details>
<summary>Code:</summary>

```python
def _check_dash_usage(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        # Check for " - " (hyphen with spaces should be em dash)
        if " - " in clean_line and not clean_line.strip().startswith("-"):
            pos = line.find(" - ") if " - " in line else clean_line.find(" - ")
            error_msg = f'{self.RULES["H016"]}: " - " should be " — " (em dash)'
            yield self._format_error("H016", error_msg, filename, line_num=line_num, col=pos + 1)

        # Check for en dash not between digits
        if "–" in clean_line:  # noqa: RUF001
            line_matches = list(re.finditer(r"–", line))  # noqa: RUF001
            for i, match in enumerate(re.finditer(r"–", clean_line)):  # noqa: RUF001
                pos = match.start()
                before = clean_line[pos - 1] if pos > 0 else ""
                after = clean_line[pos + 1] if pos + 1 < len(clean_line) else ""
                if not (before.isdigit() and after.isdigit()):
                    col_pos = line_matches[i].start() if i < len(line_matches) else pos
                    error_msg = f'{self.RULES["H016"]}: en dash "–" should only be between digits'  # noqa: RUF001
                    yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)

        # Check for em dash not between spaces
        if "—" in clean_line:
            line_matches = list(re.finditer(r"—", line))
            for i, match in enumerate(re.finditer(r"—", clean_line)):
                pos = match.start()
                before = clean_line[pos - 1] if pos > 0 else " "
                after = clean_line[pos + 1] if pos + 1 < len(clean_line) else " "
                col_pos = line_matches[i].start() if i < len(line_matches) else pos
                # Em dash should have spaces around it (or be at line start for dialogue)
                if pos == 0:
                    if after != " ":
                        error_msg = f'{self.RULES["H016"]}: em dash "—" at start should be followed by space'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)
                elif not (before == " " and after == " "):
                    error_msg = f'{self.RULES["H016"]}: em dash "—" should have spaces around it'
                    yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)
```

</details>

### ⚙️ Method `_check_double_spaces`

```python
def _check_double_spaces(self, filename: Path, line: str, clean_line: str, line_num: int, content_lines: list[str], line_index: int) -> Generator[str, None, None]
```

Check for double spaces (H009).

<details>
<summary>Code:</summary>

```python
def _check_double_spaces(
        self, filename: Path, line: str, clean_line: str, line_num: int, content_lines: list[str], line_index: int
    ) -> Generator[str, None, None]:
        if "  " not in clean_line:
            return

        # Skip if line starts with list indentation
        if line.startswith(("  ", "  *", "  -")):
            return

        # Skip if previous line is a list item
        if line_index > 0:
            prev_line = content_lines[line_index - 1]
            if prev_line.strip().startswith("*") or prev_line.strip().startswith("-"):
                return

        # Skip table lines
        if line.strip().startswith("|"):
            return

        col = clean_line.index("  ") + 1
        yield self._format_error("H009", self.RULES["H009"], filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_file_level_rules`

```python
def _check_file_level_rules(self, filename: Path, all_lines: list[str], rules: set, content: str = "") -> Generator[str, None, None]
```

Check rules that apply to the entire file.

<details>
<summary>Code:</summary>

```python
def _check_file_level_rules(
        self, filename: Path, all_lines: list[str], rules: set, content: str = ""
    ) -> Generator[str, None, None]:
        # H011: No empty line at end of file
        if "H011" in rules and all_lines and not content.endswith("\n"):
            yield self._format_error("H011", self.RULES["H011"], filename, line_num=len(all_lines))

        # H012: Two consecutive empty lines
        if "H012" in rules:
            for i in range(len(all_lines) - 1):
                if not all_lines[i].strip() and not all_lines[i + 1].strip() and i > 0 and i + 1 < len(all_lines) - 1:
                    yield self._format_error("H012", self.RULES["H012"], filename, line_num=i + 1)
```

</details>

### ⚙️ Method `_check_filename_rules`

```python
def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]
```

Check filename-related rules.

<details>
<summary>Code:</summary>

```python
def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        if "H001" in rules and " " in filename.name:
            yield self._format_error("H001", self.RULES["H001"], filename)

        if "H002" in rules and " " in str(filename):
            yield self._format_error("H002", self.RULES["H002"], filename)
```

</details>

### ⚙️ Method `_check_html_tags`

```python
def _check_html_tags(self, filename: Path, line: str, _clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for HTML tags in content (H019).

<details>
<summary>Code:</summary>

```python
def _check_html_tags(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        for tag in self.FORBIDDEN_HTML_TAGS:
            if tag.lower() in line.lower():
                pos = line.lower().find(tag.lower())
                error_msg = f'{self.RULES["H019"]}: found "{tag}"'
                yield self._format_error("H019", error_msg, filename, line_num=line_num, col=pos + 1)
```

</details>

### ⚙️ Method `_check_image_caption`

```python
def _check_image_caption(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]
```

Check that image captions start with uppercase (H020).

<details>
<summary>Code:</summary>

```python
def _check_image_caption(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        if not line.strip().startswith("!["):
            return

        match = re.match(r"!\[([^\]]*)\]", line.strip())
        if match:
            caption = match.group(1)
            if caption and caption[0].isalpha() and caption[0].islower():
                error_msg = f'{self.RULES["H020"]}: caption starts with "{caption[0]}"'
                yield self._format_error("H020", error_msg, filename, line_num=line_num, col=3)
```

</details>

### ⚙️ Method `_check_incorrect_words`

```python
def _check_incorrect_words(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for incorrect word forms (H006).

<details>
<summary>Code:</summary>

```python
def _check_incorrect_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        for incorrect_word, correct_word in self.INCORRECT_WORDS.items():
            escaped_word = re.escape(incorrect_word)
            if re.match(r"^[\w]+$", incorrect_word):
                pattern = rf"\b{escaped_word}\b"
            else:
                pattern = rf"(?<![a-zA-Zа-яА-ЯёЁ0-9_]){escaped_word}(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001

            if re.search(pattern, clean_line):
                match = re.search(pattern, line)
                col = match.start() + 1 if match else 1
                error_message = f'{self.RULES["H006"]}: "{incorrect_word}" should be "{correct_word}"'
                yield self._format_error("H006", error_message, filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_lowercase_after_punctuation`

```python
def _check_lowercase_after_punctuation(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for lowercase letter after sentence-ending punctuation (H021).

<details>
<summary>Code:</summary>

```python
def _check_lowercase_after_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        # Pattern: sentence end punctuation, space, lowercase letter
        pattern = r"[.!?]\s+([a-zа-яё])"  # noqa: RUF001  # ignore: HP001

        for match in re.finditer(pattern, clean_line):
            letter = match.group(1)
            pos = match.start()

            # Check for exceptions like "e.g. ", "т. е.", "т. д."  # noqa: RUF003  # ignore: HP001
            context_before = clean_line[max(0, pos - 4) : pos + 1]
            exceptions = ["e.g.", "i.e.", "т. е", "т. д", "т. ч", "т. п"]  # noqa: RUF001  # ignore: HP001
            if any(exc in context_before for exc in exceptions):
                continue

            line_match = re.search(re.escape(match.group(0)), line)
            offset = match.start(1) - match.start(0)
            col = line_match.start(0) + offset + 1 if line_match else match.start(1) + 1

            error_msg = f'{self.RULES["H021"]}: found lowercase "{letter}" after punctuation'
            yield self._format_error("H021", error_msg, filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_non_code_line_rules`

```python
def _check_non_code_line_rules(self, filename: Path, line: str, line_num: int, content_lines: list[str], line_index: int, code_block_info: list, rules: set) -> Generator[str, None, None]
```

Check rules that apply only to non-code lines.

<details>
<summary>Code:</summary>

```python
def _check_non_code_line_rules(
        self,
        filename: Path,
        line: str,
        line_num: int,
        content_lines: list[str],
        line_index: int,
        code_block_info: list,
        rules: set,
    ) -> Generator[str, None, None]:
        # Remove inline code from line before checking text rules
        clean_line = self._remove_inline_code(line)
        # Remove URLs from markdown links
        clean_line = re.sub(r"\]\([^)]*\)", "]()", clean_line)
        clean_line = re.sub(r"<[^>]*>", "<>", clean_line)

        # H006: Incorrect word forms
        if "H006" in rules:
            yield from self._check_incorrect_words(filename, line, clean_line, line_num)

        # H009: Double spaces
        if "H009" in rules:
            yield from self._check_double_spaces(filename, line, clean_line, line_num, content_lines, line_index)

        # H013: Missing colon before code block
        if "H013" in rules:
            yield from self._check_colon_before_code(
                filename, line, line_num, content_lines, line_index, code_block_info
            )

        # H014: Missing colon before image
        if "H014" in rules:
            yield from self._check_colon_before_image(filename, line, line_num, content_lines, line_index)

        # H015: Space before punctuation
        if "H015" in rules:
            yield from self._check_space_before_punctuation(filename, line, clean_line, line_num)

        # H016: Incorrect dash/hyphen usage
        if "H016" in rules:
            yield from self._check_dash_usage(filename, line, clean_line, line_num)

        # H017: Three dots instead of ellipsis
        if "H017" in rules and "..." in clean_line:
            col = line.index("...") + 1 if "..." in line else clean_line.index("...") + 1
            error_msg = f'{self.RULES["H017"]}: "..." should be "…"'
            yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)

        # H018: Curly/straight quotes
        if "H018" in rules:
            yield from self._check_quotes(filename, line, clean_line, line_num)

        # H019: HTML tags
        if "H019" in rules:
            yield from self._check_html_tags(filename, line, clean_line, line_num)

        # H020: Image caption lowercase
        if "H020" in rules:
            yield from self._check_image_caption(filename, line, line_num)

        # H021: Lowercase after sentence end
        if "H021" in rules:
            yield from self._check_lowercase_after_punctuation(filename, line, clean_line, line_num)
```

</details>

### ⚙️ Method `_check_quotes`

```python
def _check_quotes(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for incorrect quote characters (H018).

<details>
<summary>Code:</summary>

```python
def _check_quotes(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]:
        incorrect_quotes = [
            ('"', 'straight double quote "'),
            ("\u201c", "curly quote \u201c"),
            ("\u201d", "curly quote \u201d"),
            ("« ", "space after «"),
            (" »", "space before »"),
        ]

        for char, description in incorrect_quotes:
            if char in clean_line:
                pos = line.find(char) if char in line else clean_line.find(char)
                error_msg = f"{self.RULES['H018']}: found {description}"
                yield self._format_error("H018", error_msg, filename, line_num=line_num, col=pos + 1)
```

</details>

### ⚙️ Method `_check_space_before_punctuation`

```python
def _check_space_before_punctuation(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for space before punctuation marks (H015).

<details>
<summary>Code:</summary>

```python
def _check_space_before_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        patterns = [
            (r" \.", " ."),
            (r" ,", " ,"),
            (r" ;", " ;"),
            (r" :", " :"),
            (r" \?", " ?"),
        ]

        for pattern, display in patterns:
            match = re.search(pattern, clean_line)
            if match:
                line_match = re.search(pattern, line)
                col = line_match.start() + 1 if line_match else match.start() + 1
                error_msg = f'{self.RULES["H015"]}: found "{display}"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=col)

        # Special handling for " !" - skip special markers
        if " !" in clean_line:
            exceptions = [" !details", " !note", " !important", " !warning"]
            pos = clean_line.find(" !")
            if not any(clean_line[pos:].startswith(exc) for exc in exceptions) and not clean_line.strip().startswith(
                "!"
            ):
                line_pos = line.find(" !") if " !" in line else pos
                error_msg = f'{self.RULES["H015"]}: found " !"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=line_pos + 1)
```

</details>

### ⚙️ Method `_check_yaml_rules`

```python
def _check_yaml_rules(self, filename: Path, yaml_content: str, all_lines: list[str], rules: set) -> Generator[str, None, None]
```

Check YAML-related rules.

<details>
<summary>Code:</summary>

```python
def _check_yaml_rules(
        self, filename: Path, yaml_content: str, all_lines: list[str], rules: set
    ) -> Generator[str, None, None]:
        try:
            data = yaml.safe_load(yaml_content.replace("---\n", "").replace("\n---", "")) if yaml_content else None

            if not data and "H003" in rules:
                yield self._format_error("H003", self.RULES["H003"], filename, line_num=1)
                return

            if data:
                lang = data.get("lang")
                if "H004" in rules and not lang:
                    line_num = self._find_yaml_block_end_line(all_lines)
                    yield self._format_error("H004", self.RULES["H004"], filename, line_num=line_num)
                elif "H005" in rules and lang and lang not in ["en", "ru"]:
                    line_num = self._find_yaml_field_line_in_original(all_lines, "lang")
                    col = self._find_yaml_field_column(all_lines, line_num, "lang")
                    yield self._format_error("H005", self.RULES["H005"], filename, line_num=line_num, col=col)

        except yaml.YAMLError as e:
            yield self._format_error("H000", f"YAML parsing error: {e}", filename, line_num=1)
```

</details>

### ⚙️ Method `_determine_active_rules`

```python
def _determine_active_rules(self, select: set[str] | None, exclude_rules: set[str] | None) -> set[str]
```

Determine which rules should be active.

<details>
<summary>Code:</summary>

```python
def _determine_active_rules(self, select: set[str] | None, exclude_rules: set[str] | None) -> set[str]:
        active = select & self.all_rules if select is not None else self.all_rules.copy()
        if exclude_rules is not None:
            active -= exclude_rules
        return active
```

</details>

### ⚙️ Method `_determine_project_root`

```python
def _determine_project_root(self, project_root: Path | str | None) -> Path
```

Determine the project root directory.

<details>
<summary>Code:</summary>

```python
def _determine_project_root(self, project_root: Path | str | None) -> Path:
        if project_root:
            return Path(project_root).resolve()
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
```

</details>

### ⚙️ Method `_find_yaml_block_end_line`

```python
def _find_yaml_block_end_line(self, all_lines: list[str]) -> int
```

Find the line number where YAML block ends.

<details>
<summary>Code:</summary>

```python
def _find_yaml_block_end_line(self, all_lines: list[str]) -> int:
        if not all_lines or all_lines[0].strip() != "---":
            return 1
        for i, line in enumerate(all_lines[1:], 2):
            if line.strip() == "---":
                return i
        return len(all_lines)
```

</details>

### ⚙️ Method `_find_yaml_end_line`

```python
def _find_yaml_end_line(self, lines: list[str]) -> int
```

Find the line number where YAML block ends (1-based).

<details>
<summary>Code:</summary>

```python
def _find_yaml_end_line(self, lines: list[str]) -> int:
        if not lines or lines[0].strip() != "---":
            return 1
        for i, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                return i + 1
        return len(lines) + 1
```

</details>

### ⚙️ Method `_find_yaml_field_column`

```python
def _find_yaml_field_column(self, all_lines: list[str], line_num: int, field: str) -> int
```

Find column position of field value in YAML.

<details>
<summary>Code:</summary>

```python
def _find_yaml_field_column(self, all_lines: list[str], line_num: int, field: str) -> int:
        if line_num <= len(all_lines):
            line = all_lines[line_num - 1]
            match = re.search(f"{field}:\\s*(.+)", line)
            if match:
                return match.start(1) + 1
        return 1
```

</details>

### ⚙️ Method `_find_yaml_field_line_in_original`

```python
def _find_yaml_field_line_in_original(self, all_lines: list[str], field: str) -> int
```

Find line number of a specific field in YAML content.

<details>
<summary>Code:</summary>

```python
def _find_yaml_field_line_in_original(self, all_lines: list[str], field: str) -> int:
        if not all_lines or all_lines[0].strip() != "---":
            return 1
        for i, line in enumerate(all_lines[1:], 2):
            if line.strip() == "---":
                break
            if line.strip().startswith(f"{field}:"):
                return i
        return 2
```

</details>

### ⚙️ Method `_format_error`

```python
def _format_error(self, error_code: str, message: str, filename: Path) -> str
```

Format error message in ruff style.

<details>
<summary>Code:</summary>

```python
def _format_error(self, error_code: str, message: str, filename: Path, *, line_num: int = 0, col: int = 0) -> str:
        relative_path = self._get_relative_path(filename)
        location = relative_path
        if line_num > 0:
            location += f":{line_num}"
            if col > 0:
                location += f":{col}"
        return f"{location}: {error_code} {message}"
```

</details>

### ⚙️ Method `_get_relative_path`

```python
def _get_relative_path(self, filename: Path) -> str
```

Get relative path from project root.

<details>
<summary>Code:</summary>

```python
def _get_relative_path(self, filename: Path) -> str:
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            return str(filename.resolve())
```

</details>

### ⚙️ Method `_remove_inline_code`

```python
def _remove_inline_code(self, line: str) -> str
```

Remove inline code segments from line.

<details>
<summary>Code:</summary>

```python
def _remove_inline_code(self, line: str) -> str:
        clean_line = ""
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                clean_line += segment
        return clean_line
```

</details>

### ⚙️ Method `_should_check_paragraph_end`

```python
def _should_check_paragraph_end(self, line: str) -> bool
```

Check if line is a regular paragraph that should end with colon before code/image.

<details>
<summary>Code:</summary>

````python
def _should_check_paragraph_end(self, line: str) -> bool:
        if not line.strip():
            return False
        if line.strip() == "```":
            return False
        if line.strip().startswith("!["):
            return False
        return not line.strip().startswith("#")
````

</details>
