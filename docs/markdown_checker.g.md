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
  - [⚙️ Method `_check_consecutive_empty_lines`](#%EF%B8%8F-method-_check_consecutive_empty_lines)
  - [⚙️ Method `_check_content_rules`](#%EF%B8%8F-method-_check_content_rules)
  - [⚙️ Method `_check_dash_usage`](#%EF%B8%8F-method-_check_dash_usage)
  - [⚙️ Method `_check_double_spaces`](#%EF%B8%8F-method-_check_double_spaces)
  - [⚙️ Method `_check_empty_line_between_paragraphs`](#%EF%B8%8F-method-_check_empty_line_between_paragraphs)
  - [⚙️ Method `_check_file_level_rules`](#%EF%B8%8F-method-_check_file_level_rules)
  - [⚙️ Method `_check_filename_rules`](#%EF%B8%8F-method-_check_filename_rules)
  - [⚙️ Method `_check_horizontal_bar`](#%EF%B8%8F-method-_check_horizontal_bar)
  - [⚙️ Method `_check_html_tags`](#%EF%B8%8F-method-_check_html_tags)
  - [⚙️ Method `_check_image_caption`](#%EF%B8%8F-method-_check_image_caption)
  - [⚙️ Method `_check_image_not_at_line_start`](#%EF%B8%8F-method-_check_image_not_at_line_start)
  - [⚙️ Method `_check_incorrect_words`](#%EF%B8%8F-method-_check_incorrect_words)
  - [⚙️ Method `_check_lowercase_after_punctuation`](#%EF%B8%8F-method-_check_lowercase_after_punctuation)
  - [⚙️ Method `_check_non_code_line_rules`](#%EF%B8%8F-method-_check_non_code_line_rules)
  - [⚙️ Method `_check_numero_space`](#%EF%B8%8F-method-_check_numero_space)
  - [⚙️ Method `_check_question_mark_period`](#%EF%B8%8F-method-_check_question_mark_period)
  - [⚙️ Method `_check_quotes`](#%EF%B8%8F-method-_check_quotes)
  - [⚙️ Method `_check_russian_polite_pronouns`](#%EF%B8%8F-method-_check_russian_polite_pronouns)
  - [⚙️ Method `_check_space_before_punctuation`](#%EF%B8%8F-method-_check_space_before_punctuation)
  - [⚙️ Method `_check_x_instead_of_times`](#%EF%B8%8F-method-_check_x_instead_of_times)
  - [⚙️ Method `_check_yaml_rules`](#%EF%B8%8F-method-_check_yaml_rules)
  - [⚙️ Method `_determine_active_rules`](#%EF%B8%8F-method-_determine_active_rules)
  - [⚙️ Method `_determine_project_root`](#%EF%B8%8F-method-_determine_project_root)
  - [⚙️ Method `_find_yaml_block_end_line`](#%EF%B8%8F-method-_find_yaml_block_end_line)
  - [⚙️ Method `_find_yaml_end_line`](#%EF%B8%8F-method-_find_yaml_end_line)
  - [⚙️ Method `_find_yaml_field_column`](#%EF%B8%8F-method-_find_yaml_field_column)
  - [⚙️ Method `_find_yaml_field_line_in_original`](#%EF%B8%8F-method-_find_yaml_field_line_in_original)
  - [⚙️ Method `_format_error`](#%EF%B8%8F-method-_format_error)
  - [⚙️ Method `_get_relative_path`](#%EF%B8%8F-method-_get_relative_path)
  - [⚙️ Method `_inside_details_block`](#%EF%B8%8F-method-_inside_details_block)
  - [⚙️ Method `_is_paragraph_pair_requiring_empty_line`](#%EF%B8%8F-method-_is_paragraph_pair_requiring_empty_line)
  - [⚙️ Method `_is_table_cell_only_dash`](#%EF%B8%8F-method-_is_table_cell_only_dash)
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
- **H023** - No empty line between paragraphs.
- **H024** - Capitalized Russian polite pronoun (use lowercase when addressing reader; ru only).
- **H025** - Latin "x" or Cyrillic "x" used instead of multiplication sign "x".
- **H026** - Image markdown "![" found not at start of line.
- **H028** - Horizontal bar "―" (dialogue dash) should not be used.
- **H029** - Space required after "№".
- **H030** - Question mark followed by period (?.).

<details>
<summary>Code:</summary>

````python
class MarkdownChecker:

    # Minimum length for a line to be treated as italic-only caption (e.g. _text_)
    _MIN_ITALIC_CAPTION_LEN: ClassVar[int] = 2

    # Markers that suppress colon-before-code/image warnings (shared between H013 and H014 checks)
    _COLON_SKIP_MARKERS: ClassVar[tuple[str, ...]] = (
        "[!DETAILS]",
        "[!WARNING]",
        "[!IMPORTANT]",
        "[!NOTE]",
        "<!-- !details -->",
        "<!-- !note -->",
        "<!-- !important -->",
        "<!-- !warning -->",
    )

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
        "H023": "No empty line between paragraphs",
        "H024": "Capitalized Russian polite pronoun (use lowercase when addressing reader)",
        "H025": "Latin x or Cyrillic x used instead of multiplication sign ×",  # ignore: HP001  # noqa: RUF001
        "H026": "Image markdown ![ found not at start of line",
        "H028": "Horizontal bar ― (dialogue dash) should not be used",
        "H029": "Space required after №",
        "H030": "Question mark followed by period (?.)",
    }

    # Russian polite "you" pronouns that must be lowercase when addressing the reader (lang: ru)
    RUSSIAN_POLITE_PRONOUNS_CAPITALIZED: ClassVar[tuple[str, ...]] = (
        "Вы",  # ignore: HP001
        "Вас",  # ignore: HP001  # noqa: RUF001
        "Вам",  # ignore: HP001
        "Вами",  # ignore: HP001
        "Ваш",  # ignore: HP001
        "Вашего",  # ignore: HP001
        "Ваше",  # ignore: HP001
        "Вашу",  # ignore: HP001
        "Вашей",  # ignore: HP001
        "Ваша",  # ignore: HP001
        "Вашему",  # ignore: HP001
        "Вашим",  # ignore: HP001
        "Вашем",  # ignore: HP001
        "Вашею",  # ignore: HP001
        "Ваши",  # ignore: HP001
        "Ваших",  # ignore: HP001
        "Вашими",  # ignore: HP001
    )

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
        # Russian abbreviations (with spaces: т. е., т. д., т. ч., т. п.)  # ignore: HP001  # noqa: RUF003
        "т.е.": "т. е.",  # noqa: RUF001  # ignore: HP001
        "Т.е.": "Т. е.",  # noqa: RUF001  # ignore: HP001
        "т.д.": "т. д.",  # ignore: HP001
        "т.ч.": "т. ч.",  # ignore: HP001
        "т.п.": "т. п.",  # ignore: HP001
    }

    # Pre-compiled regex patterns for INCORRECT_WORDS — built once at class definition time
    # to avoid recompiling on every checked line.
    _INCORRECT_WORD_PATTERNS: ClassVar[dict[str, tuple[re.Pattern, str]]] = {
        word: (
            re.compile(
                rf"\b{re.escape(word)}\b"
                if re.match(r"^[\w]+$", word)
                else rf"(?<![a-zA-Zа-яА-ЯёЁ0-9_]){re.escape(word)}(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001
            ),
            correct,
        )
        for word, correct in INCORRECT_WORDS.items()
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
        self, filename: Path, line: str, line_num: int, rules: set, *, is_code_block: bool = False
    ) -> Generator[str, None, None]:
        """Check rules that apply to all lines including code blocks."""
        # H008: Trailing whitespace
        if "H008" in rules and line != line.rstrip():
            col = len(line.rstrip()) + 1
            yield self._format_error("H008", self.RULES["H008"], filename, line_num=line_num, col=col)

        # H010: Tab character (skip inside code blocks — tabs are valid there, e.g. CSV/TSV examples)
        if "H010" in rules and "\t" in line and not is_code_block:
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

            try:
                yaml_data = yaml.safe_load(yaml_part.replace("---\n", "").replace("\n---", "")) if yaml_part else None
                lang = (yaml_data or {}).get("lang") or ""
            except yaml.YAMLError:
                lang = ""

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules)
            yield from self._check_content_rules(filename, all_lines, yaml_end_line, rules, content, lang=lang)
            yield from self._check_code_rules(filename, all_lines, yaml_end_line, rules)

        except Exception as e:
            yield self._format_error("H000", f"Exception error: {e}", filename)

    # =========================================================================
    # Code Block Rules (H007)
    # =========================================================================

    def _check_code_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set
    ) -> Generator[str, None, None]:
        """Check code block related rules."""
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        code_block_info = list(h.md.identify_code_blocks(content_lines))

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

        next_line_info = code_block_info[line_index + 1] if line_index + 1 < len(code_block_info) else None
        next_next_info = code_block_info[line_index + 2] if line_index + 2 < len(code_block_info) else None

        if not next_line_info or not next_next_info:
            return

        next_line, _ = next_line_info
        next_next_line, _ = next_next_info

        if not self._should_check_paragraph_end(line):
            return

        # Check pattern: non-empty line, empty line, code block start
        if not (next_line.strip() == "" and next_next_line.strip().startswith("```")):
            return

        last_char = line.rstrip()[-1] if line.rstrip() else ""

        if any(marker in line for marker in self._COLON_SKIP_MARKERS):
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
        if not (next_line.strip() == "" and next_next_line.strip().startswith("![")):
            return

        last_char = line.rstrip()[-1] if line.rstrip() else ""

        if any(marker in line for marker in self._COLON_SKIP_MARKERS):
            return
        if line.strip().startswith("<"):
            return

        stripped = line.strip()
        # Skip image caption line (italic only, e.g. _Figure 1: ..._): belongs to previous image
        if len(stripped) >= self._MIN_ITALIC_CAPTION_LEN and stripped.startswith("_") and stripped.endswith("_"):
            return
        # Skip list item: no colon required before image when last line is a list item
        if stripped.startswith("- "):
            return

        if last_char != ":":
            error_msg = f'{self.RULES["H014"]}: last char is "{last_char}"'
            yield self._format_error("H014", error_msg, filename, line_num=line_num, col=len(line.rstrip()))

    def _check_consecutive_empty_lines(
        self,
        filename: Path,
        all_lines: list[str],
        code_block_info: list | None,
        yaml_end_line: int,
    ) -> Generator[str, None, None]:
        """Check for two consecutive empty lines (H012 helper)."""
        content_start = yaml_end_line - 1
        for i in range(len(all_lines) - 1):
            if all_lines[i].strip() or all_lines[i + 1].strip():
                continue
            if i == 0 or i + 1 == len(all_lines) - 1:
                continue
            if code_block_info is not None and yaml_end_line >= 1:
                ci, ci1 = i - content_start, i + 1 - content_start
                if (
                    i >= content_start
                    and i + 1 >= content_start
                    and ci < len(code_block_info)
                    and ci1 < len(code_block_info)
                    and (code_block_info[ci][1] or code_block_info[ci1][1])
                ):
                    continue
            yield self._format_error("H012", self.RULES["H012"], filename, line_num=i + 1)

    # =========================================================================
    # Content Rules (H006, H008-H022) - for non-code content
    # =========================================================================

    def _check_content_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set, content: str = "", *, lang: str = ""
    ) -> Generator[str, None, None]:
        """Check content-related rules working directly with original file lines."""
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        yield from self._check_file_level_rules(
            filename, all_lines, rules, content, code_block_info=code_block_info, yaml_end_line=yaml_end_line
        )

        # H023: No empty line between paragraphs (content-level, respects code blocks)
        if "H023" in rules:
            yield from self._check_empty_line_between_paragraphs(
                filename, content_lines, code_block_info, yaml_end_line
            )

        for i, (line, is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1

            yield from self._check_all_lines_rules(filename, line, actual_line_num, rules, is_code_block=is_code_block)

            if not is_code_block:
                yield from self._check_non_code_line_rules(
                    filename,
                    line,
                    actual_line_num,
                    content_lines,
                    i,
                    code_block_info,
                    rules,
                    yaml_end_line,
                    lang=lang,
                )

    def _check_dash_usage(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for incorrect dash/hyphen usage (H016). Applies only to markdown text, not YAML/code."""
        # Single pass over segments: check for " - ", " − " (Unicode minus), and " -- "  # noqa: RUF003
        hyphen_found = False
        minus_or_double_found = False
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                if not hyphen_found and " - " in segment and not segment.strip().startswith("-"):
                    pos = offset + segment.find(" - ")
                    if not ("|" in line and self._is_table_cell_only_dash(line, pos)):
                        error_msg = f'{self.RULES["H016"]}: " - " should be " — " (em dash)'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=pos + 1)
                        hyphen_found = True

                if not minus_or_double_found:
                    if " \u2212 " in segment:  # Unicode minus
                        col = offset + segment.find(" \u2212 ") + 1
                        error_msg = f'{self.RULES["H016"]}: " − " (minus) should be " — " (em dash)'  # noqa: RUF001
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col)
                        minus_or_double_found = True
                    elif " -- " in segment:
                        col = offset + segment.find(" -- ") + 1
                        error_msg = f'{self.RULES["H016"]}: " -- " should be " — " (em dash)'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col)
                        minus_or_double_found = True

            offset += len(segment)
            if hyphen_found and minus_or_double_found:
                break

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

        # Check for em dash not surrounded by spaces
        if "—" in clean_line:
            line_matches = list(re.finditer(r"—", line))
            for i, match in enumerate(re.finditer(r"—", clean_line)):
                pos = match.start()
                before = clean_line[pos - 1] if pos > 0 else " "
                after = clean_line[pos + 1] if pos + 1 < len(clean_line) else " "
                col_pos = line_matches[i].start() if i < len(line_matches) else pos
                if pos == 0:
                    if after != " ":
                        error_msg = f'{self.RULES["H016"]}: em dash "—" at start should be followed by space'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)
                elif not (before == " " and after == " "):
                    error_msg = f'{self.RULES["H016"]}: em dash "—" should have spaces around it'
                    yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col_pos + 1)

    def _check_double_spaces(
        self, filename: Path, line: str, _clean_line: str, line_num: int, content_lines: list[str], line_index: int
    ) -> Generator[str, None, None]:
        """Check for double spaces (H009).

        Uses original line so that removal of inline code does not create
        false double space when segments are concatenated.
        """
        if "  " not in line:
            return
        if line.startswith(("  ", "  *", "  -")):
            return
        if line_index > 0:
            prev_line = content_lines[line_index - 1]
            if prev_line.strip().startswith(("*", "-")):
                return
        if line.strip().startswith("|"):
            return

        col = line.index("  ") + 1
        yield self._format_error("H009", self.RULES["H009"], filename, line_num=line_num, col=col)

    def _check_empty_line_between_paragraphs(
        self,
        filename: Path,
        content_lines: list[str],
        code_block_info: list,
        yaml_end_line: int,
    ) -> Generator[str, None, None]:
        """Check that two consecutive paragraph lines have an empty line between them (H023)."""
        for i in range(len(content_lines) - 1):
            line_i = content_lines[i]
            line_i_next = content_lines[i + 1]
            if not line_i.strip() or not line_i_next.strip():
                continue
            _, is_code_i = code_block_info[i] if i < len(code_block_info) else (line_i, False)
            _, is_code_next = code_block_info[i + 1] if i + 1 < len(code_block_info) else (line_i_next, False)
            if is_code_i or is_code_next:
                continue
            if self._inside_details_block(content_lines, i):
                continue
            if not self._is_paragraph_pair_requiring_empty_line(line_i, line_i_next):
                continue
            actual_line_num = (yaml_end_line - 1) + i + 1
            error_msg = f"{self.RULES['H023']}: add empty line between paragraphs"
            yield self._format_error("H023", error_msg, filename, line_num=actual_line_num)

    def _check_file_level_rules(
        self,
        filename: Path,
        all_lines: list[str],
        rules: set,
        content: str = "",
        *,
        code_block_info: list | None = None,
        yaml_end_line: int = 1,
    ) -> Generator[str, None, None]:
        """Check rules that apply to the entire file."""
        # H011: No empty line at end of file
        if "H011" in rules and all_lines and not content.endswith("\n"):
            yield self._format_error("H011", self.RULES["H011"], filename, line_num=len(all_lines))

        # H012: Two consecutive empty lines (skip inside code blocks)
        if "H012" in rules:
            yield from self._check_consecutive_empty_lines(filename, all_lines, code_block_info, yaml_end_line)

    # =========================================================================
    # Filename Rules (H001, H002)
    # =========================================================================

    def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Check filename-related rules."""
        if "H001" in rules and " " in filename.name:
            yield self._format_error("H001", self.RULES["H001"], filename)

        if "H002" in rules and " " in str(filename):
            yield self._format_error("H002", self.RULES["H002"], filename)

    def _check_horizontal_bar(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for horizontal bar '―' (U+2015, dialogue dash) which should not be used (H028)."""
        if "\u2015" not in clean_line:
            return
        col = line.find("\u2015") + 1
        yield self._format_error("H028", self.RULES["H028"], filename, line_num=line_num, col=col)

    def _check_html_tags(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for HTML tags in content (H019). Exception: <details> and <summary> are allowed."""
        line_lower = line.lower()
        for tag in self.FORBIDDEN_HTML_TAGS:
            if tag.lower() not in line_lower:
                continue
            pos = line_lower.find(tag.lower())
            rest = line_lower[pos:]
            if rest.startswith(("<details", "<details>", "</details>", "<summary", "<summary>", "</summary>")):
                continue
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

    def _check_image_not_at_line_start(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check that image markdown '![' is at start of (trimmed) line (H026)."""
        trimmed = line.strip()
        if "![" not in trimmed or trimmed.find("![") == 0:
            return
        col = line.find("![") + 1
        yield self._format_error("H026", self.RULES["H026"], filename, line_num=line_num, col=col)

    def _check_incorrect_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for incorrect word forms (H006). Uses pre-compiled patterns from _INCORRECT_WORD_PATTERNS."""
        for incorrect_word, (pattern, correct_word) in self._INCORRECT_WORD_PATTERNS.items():
            if pattern.search(clean_line):
                match = pattern.search(line)
                col = match.start() + 1 if match else 1
                error_message = f'{self.RULES["H006"]}: "{incorrect_word}" should be "{correct_word}"'
                yield self._format_error("H006", error_message, filename, line_num=line_num, col=col)

    def _check_lowercase_after_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for lowercase letter after sentence-ending punctuation (H021)."""
        pattern = r"[.!?]\s+([a-zа-яё])"  # noqa: RUF001  # ignore: HP001
        exceptions = ["e.g.", "i.e.", "т. е", "т. д", "т. ч", "т. п"]  # noqa: RUF001  # ignore: HP001

        for match in re.finditer(pattern, clean_line):
            letter = match.group(1)
            pos = match.start()
            context = clean_line[max(0, pos - 4) : match.end()]
            if any(exc in context.lower() for exc in exceptions):
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
        yaml_end_line: int,
        *,
        lang: str = "",
    ) -> Generator[str, None, None]:
        """Check rules that apply only to non-code lines (markdown content, not YAML/code)."""
        # Remove inline code and URLs before text checks
        clean_line = self._remove_inline_code(line)
        clean_line = re.sub(r"\]\([^)]*\)", "]()", clean_line)
        clean_line = re.sub(r"<[^>]*>", "<>", clean_line)

        if "H006" in rules:
            yield from self._check_incorrect_words(filename, line, clean_line, line_num)

        if "H009" in rules:
            yield from self._check_double_spaces(filename, line, clean_line, line_num, content_lines, line_index)

        if "H013" in rules:
            yield from self._check_colon_before_code(
                filename, line, line_num, content_lines, line_index, code_block_info
            )

        if "H014" in rules:
            yield from self._check_colon_before_image(filename, line, line_num, content_lines, line_index)

        if "H015" in rules:
            yield from self._check_space_before_punctuation(filename, line, clean_line, line_num)

        if "H016" in rules and line_num >= yaml_end_line:
            yield from self._check_dash_usage(filename, line, clean_line, line_num)

        if "H017" in rules:
            if "..." in clean_line:
                col = line.index("...") + 1 if "..." in line else clean_line.index("...") + 1
                error_msg = f'{self.RULES["H017"]}: "..." should be "…"'
                yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)
            elif clean_line.rstrip().endswith("\u2026"):
                trimmed = line.rstrip()
                col = trimmed.rfind("\u2026") + 1
                error_msg = f'{self.RULES["H017"]}: ellipsis "…" at end of line'
                yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)

        if "H018" in rules:
            yield from self._check_quotes(filename, line, clean_line, line_num)

        if "H019" in rules:
            yield from self._check_html_tags(filename, line, clean_line, line_num)

        if "H020" in rules:
            yield from self._check_image_caption(filename, line, line_num)

        if "H021" in rules:
            yield from self._check_lowercase_after_punctuation(filename, line, clean_line, line_num)

        if "H024" in rules and lang == "ru":
            yield from self._check_russian_polite_pronouns(filename, line, clean_line, line_num)

        if "H025" in rules:
            yield from self._check_x_instead_of_times(filename, line, line_num)

        if "H026" in rules:
            yield from self._check_image_not_at_line_start(filename, line, line_num)

        if "H028" in rules:
            yield from self._check_horizontal_bar(filename, line, clean_line, line_num)

        if "H029" in rules:
            yield from self._check_numero_space(filename, line, line_num)

        if "H030" in rules:
            yield from self._check_question_mark_period(filename, line, line_num)

    def _check_numero_space(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check that '№' is followed by a space (H029).

        Uses a regex lookahead to match '№' only when the next character exists and is not a space,
        which naturally excludes '№' at the end of a line.
        """
        for match in re.finditer(r"\u2116(?=[^ ])", line):  # № followed by a non-space character
            yield self._format_error("H029", self.RULES["H029"], filename, line_num=line_num, col=match.start() + 1)

    def _check_question_mark_period(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for question mark followed by period '?.' (H030)."""
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code and "?." in segment:
                col = offset + segment.find("?.") + 1
                yield self._format_error("H030", self.RULES["H030"], filename, line_num=line_num, col=col)
                return
            offset += len(segment)

    def _check_quotes(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]:
        """Check for incorrect quote characters (H018).

        Exception: straight double quote after a digit is allowed (inch notation, e.g. 14", 15.6").
        """
        incorrect_quotes = [
            ('"', 'straight double quote "'),
            ("\u201c", "curly quote \u201c"),
            ("\u201d", "curly quote \u201d"),
            ("« ", "space after «"),
            (" »", "space before »"),
        ]

        for char, description in incorrect_quotes:
            if char not in clean_line:
                continue
            if char == '"':
                pos = 0
                while True:
                    pos = clean_line.find('"', pos)
                    if pos < 0:
                        break
                    if pos > 0 and clean_line[pos - 1].isdigit():
                        pos += 1
                        continue
                    # Find column in original line: first non-inch " occurrence
                    idx = 0
                    col = pos + 1
                    while True:
                        q = line.find('"', idx)
                        if q < 0:
                            break
                        if q == 0 or not line[q - 1].isdigit():
                            col = q + 1
                            break
                        idx = q + 1
                    error_msg = f"{self.RULES['H018']}: found {description}"
                    yield self._format_error("H018", error_msg, filename, line_num=line_num, col=col)
                    return
                continue
            pos = line.find(char) if char in line else clean_line.find(char)
            error_msg = f"{self.RULES['H018']}: found {description}"
            yield self._format_error("H018", error_msg, filename, line_num=line_num, col=pos + 1)

    def _check_russian_polite_pronouns(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for capitalized Russian polite pronouns (H024). Use lowercase when addressing the reader.

        Exception: pronoun at sentence start is allowed:
        - after line start or after .!?;
        - after opening guillemet « (direct speech, e.g. «Ваша задача);  # ignore: HP001
        - after dash at line start (dialogue, e.g. — Ваша работа хороша).  # ignore: HP001
        Yields at most one error per line.
        """
        boundary_before = r"(?<![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001
        boundary_after = r"(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001

        code_ranges: list[tuple[int, int]] = []
        pos = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if in_code:
                code_ranges.append((pos, pos + len(segment)))
            pos += len(segment)

        def inside_inline_code(offset: int) -> bool:
            return any(s <= offset < e for s, e in code_ranges)

        def at_sentence_start(match_start: int) -> bool:
            text_before = line[:match_start]
            stripped = text_before.strip()
            if not stripped:
                return True
            if re.search(r"[.!?]\s*$", text_before):
                return True
            if stripped.endswith("\u00ab"):  # After «
                return True
            return bool(re.match(r"^\s*[—\-]\s*$", text_before))  # Dialogue dash at line start

        for word in self.RUSSIAN_POLITE_PRONOUNS_CAPITALIZED:
            pattern = boundary_before + re.escape(word) + boundary_after
            for match in re.finditer(pattern, line):
                if inside_inline_code(match.start()):
                    continue
                if at_sentence_start(match.start()):
                    continue
                error_msg = f'{self.RULES["H024"]}: use lowercase "{word.lower()}" when addressing reader'
                yield self._format_error("H024", error_msg, filename, line_num=line_num, col=match.start() + 1)
                return

    def _check_space_before_punctuation(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for space before punctuation marks (H015).

        Uses original line so that removal of inline code (e.g. `word`:)
        does not create false " :" when segments are concatenated.
        Matches inside inline code (e.g. `cd ..`) are skipped.
        """
        code_ranges: list[tuple[int, int]] = []
        pos = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if in_code:
                code_ranges.append((pos, pos + len(segment)))
            pos += len(segment)

        def _inside_inline_code(offset: int) -> bool:
            return any(start <= offset < end for start, end in code_ranges)

        patterns = [
            (r" \.", " ."),
            (r" ,", " ,"),
            (r" ;", " ;"),
            (r" :", " :"),
            (r" \?", " ?"),
        ]

        for pattern, display in patterns:
            match = re.search(pattern, line)
            if match and not _inside_inline_code(match.start()):
                error_msg = f'{self.RULES["H015"]}: found "{display}"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=match.start() + 1)

        # Special handling for " !" — skip special Markdown/directive markers
        if " !" in line:
            exceptions = [" !details", " !note", " !important", " !warning"]
            pos_found = line.find(" !")
            if (
                not _inside_inline_code(pos_found)
                and not any(line[pos_found:].startswith(exc) for exc in exceptions)
                and not line.strip().startswith("!")
            ):
                error_msg = f'{self.RULES["H015"]}: found " !"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=pos_found + 1)

    def _check_x_instead_of_times(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for Latin 'x' or Cyrillic 'x' used instead of multiplication sign '&ast;' (H025).

        Only checks text outside inline code. Exceptions: 'x86' and 'x64'; digit + 'x' + space (e.g. 2x Type-C).
        """
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                for pos, char in enumerate(segment):
                    if char not in ("x", "\u0445"):  # Latin x, Cyrillic x  # ignore: HP001
                        continue
                    if pos <= 0 or pos >= len(segment) - 1:
                        continue
                    before = segment[pos - 1]
                    after = segment[pos + 1]
                    if before not in " \t" and not before.isdigit():
                        continue
                    if after not in " \t" and not after.isdigit():
                        continue
                    if char == "x":  # Latin x
                        if before == " " and segment[pos : pos + 3] in ("x86", "x64"):
                            continue
                        if before.isdigit() and after in " \t":
                            continue  # e.g. "2x Type-C", "1x USB" — Latin x is correct
                        error_msg = f'{self.RULES["H025"]}: "x" should be "×"'  # noqa: RUF001
                    else:  # Cyrillic x  # ignore: HP001
                        error_msg = f'{self.RULES["H025"]}: "х" should be "×"'  # noqa: RUF001  # ignore: HP001
                    yield self._format_error("H025", error_msg, filename, line_num=line_num, col=offset + pos + 1)
            offset += len(segment)

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
        for i, line in enumerate(all_lines[1:], start=2):
            if line.strip() == "---":
                return i
        return len(all_lines)

    def _find_yaml_end_line(self, lines: list[str]) -> int:
        """Find the first content line number after the YAML block (1-based)."""
        if not lines or lines[0].strip() != "---":
            return 1
        for i, line in enumerate(lines[1:], start=2):
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
        for i, line in enumerate(all_lines[1:], start=2):
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

    def _inside_details_block(self, content_lines: list[str], line_index: int) -> bool:
        """Return True if line at line_index is inside a <details>...</details> block."""
        nest = 0
        for j in range(line_index + 1):
            line_lower = content_lines[j].strip().lower()
            if "<details" in line_lower:
                nest += 1
            if "</details>" in line_lower:
                nest -= 1
        return nest > 0

    def _is_paragraph_pair_requiring_empty_line(self, line_i: str, line_i_next: str) -> bool:
        """Return True if these two consecutive non-empty lines should have an empty line between them."""
        stripped_i = line_i.strip()
        if not stripped_i:
            return False

        # Do not require empty line around <details>/<summary> tags
        details_tags = ("<details", "</details>", "<summary", "</summary>")
        if stripped_i.lower().startswith(details_tags) or line_i_next.strip().lower().startswith(details_tags):
            return False

        # Skip lines starting with block-level markers that don't need separation
        if line_i.strip().startswith(("$$", "* ", "- ", "  * ", "  - ")):
            return False

        # Next line starts with image or math block
        if line_i_next.strip().startswith(("![", "$$")):
            return False

        # Table, blockquote, numbered list, or unordered list
        first_char = stripped_i[0]
        return not (first_char in ("|", "*", ">") or first_char.isdigit())

    def _is_table_cell_only_dash(self, line: str, pos: int) -> bool:
        """Return True if position pos in line is inside a table cell that contains only a hyphen."""
        parts = line.split("|")
        min_count_parts = 2
        if len(parts) < min_count_parts:
            return False
        start = 0
        for part in parts:
            end = start + len(part)
            if start <= pos < end:
                return part.strip() == "-"
            start = end + 1  # +1 for the | separator
        return False

    def _remove_inline_code(self, line: str) -> str:
        """Remove inline code segments from line, keeping only non-code text."""
        return "".join(segment for segment, in_code in h.md.identify_code_blocks_line(line) if not in_code)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _should_check_paragraph_end(self, line: str) -> bool:
        """Return True if line is a regular paragraph that should end with colon before code/image."""
        stripped = line.strip()
        return bool(stripped) and stripped != "```" and not stripped.startswith(("![", "#"))
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
        self, filename: Path, line: str, line_num: int, rules: set, *, is_code_block: bool = False
    ) -> Generator[str, None, None]:
        # H008: Trailing whitespace
        if "H008" in rules and line != line.rstrip():
            col = len(line.rstrip()) + 1
            yield self._format_error("H008", self.RULES["H008"], filename, line_num=line_num, col=col)

        # H010: Tab character (skip inside code blocks — tabs are valid there, e.g. CSV/TSV examples)
        if "H010" in rules and "\t" in line and not is_code_block:
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

            try:
                yaml_data = yaml.safe_load(yaml_part.replace("---\n", "").replace("\n---", "")) if yaml_part else None
                lang = (yaml_data or {}).get("lang") or ""
            except yaml.YAMLError:
                lang = ""

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules)
            yield from self._check_content_rules(filename, all_lines, yaml_end_line, rules, content, lang=lang)
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

        next_line_info = code_block_info[line_index + 1] if line_index + 1 < len(code_block_info) else None
        next_next_info = code_block_info[line_index + 2] if line_index + 2 < len(code_block_info) else None

        if not next_line_info or not next_next_info:
            return

        next_line, _ = next_line_info
        next_next_line, _ = next_next_info

        if not self._should_check_paragraph_end(line):
            return

        # Check pattern: non-empty line, empty line, code block start
        if not (next_line.strip() == "" and next_next_line.strip().startswith("```")):
            return

        last_char = line.rstrip()[-1] if line.rstrip() else ""

        if any(marker in line for marker in self._COLON_SKIP_MARKERS):
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
        if not (next_line.strip() == "" and next_next_line.strip().startswith("![")):
            return

        last_char = line.rstrip()[-1] if line.rstrip() else ""

        if any(marker in line for marker in self._COLON_SKIP_MARKERS):
            return
        if line.strip().startswith("<"):
            return

        stripped = line.strip()
        # Skip image caption line (italic only, e.g. _Figure 1: ..._): belongs to previous image
        if len(stripped) >= self._MIN_ITALIC_CAPTION_LEN and stripped.startswith("_") and stripped.endswith("_"):
            return
        # Skip list item: no colon required before image when last line is a list item
        if stripped.startswith("- "):
            return

        if last_char != ":":
            error_msg = f'{self.RULES["H014"]}: last char is "{last_char}"'
            yield self._format_error("H014", error_msg, filename, line_num=line_num, col=len(line.rstrip()))
```

</details>

### ⚙️ Method `_check_consecutive_empty_lines`

```python
def _check_consecutive_empty_lines(self, filename: Path, all_lines: list[str], code_block_info: list | None, yaml_end_line: int) -> Generator[str, None, None]
```

Check for two consecutive empty lines (H012 helper).

<details>
<summary>Code:</summary>

```python
def _check_consecutive_empty_lines(
        self,
        filename: Path,
        all_lines: list[str],
        code_block_info: list | None,
        yaml_end_line: int,
    ) -> Generator[str, None, None]:
        content_start = yaml_end_line - 1
        for i in range(len(all_lines) - 1):
            if all_lines[i].strip() or all_lines[i + 1].strip():
                continue
            if i == 0 or i + 1 == len(all_lines) - 1:
                continue
            if code_block_info is not None and yaml_end_line >= 1:
                ci, ci1 = i - content_start, i + 1 - content_start
                if (
                    i >= content_start
                    and i + 1 >= content_start
                    and ci < len(code_block_info)
                    and ci1 < len(code_block_info)
                    and (code_block_info[ci][1] or code_block_info[ci1][1])
                ):
                    continue
            yield self._format_error("H012", self.RULES["H012"], filename, line_num=i + 1)
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
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set, content: str = "", *, lang: str = ""
    ) -> Generator[str, None, None]:
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        yield from self._check_file_level_rules(
            filename, all_lines, rules, content, code_block_info=code_block_info, yaml_end_line=yaml_end_line
        )

        # H023: No empty line between paragraphs (content-level, respects code blocks)
        if "H023" in rules:
            yield from self._check_empty_line_between_paragraphs(
                filename, content_lines, code_block_info, yaml_end_line
            )

        for i, (line, is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1

            yield from self._check_all_lines_rules(filename, line, actual_line_num, rules, is_code_block=is_code_block)

            if not is_code_block:
                yield from self._check_non_code_line_rules(
                    filename,
                    line,
                    actual_line_num,
                    content_lines,
                    i,
                    code_block_info,
                    rules,
                    yaml_end_line,
                    lang=lang,
                )
```

</details>

### ⚙️ Method `_check_dash_usage`

```python
def _check_dash_usage(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for incorrect dash/hyphen usage (H016). Applies only to markdown text, not YAML/code.

<details>
<summary>Code:</summary>

```python
def _check_dash_usage(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        # Single pass over segments: check for " - ", " − " (Unicode minus), and " -- "  # noqa: RUF003
        hyphen_found = False
        minus_or_double_found = False
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                if not hyphen_found and " - " in segment and not segment.strip().startswith("-"):
                    pos = offset + segment.find(" - ")
                    if not ("|" in line and self._is_table_cell_only_dash(line, pos)):
                        error_msg = f'{self.RULES["H016"]}: " - " should be " — " (em dash)'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=pos + 1)
                        hyphen_found = True

                if not minus_or_double_found:
                    if " \u2212 " in segment:  # Unicode minus
                        col = offset + segment.find(" \u2212 ") + 1
                        error_msg = f'{self.RULES["H016"]}: " − " (minus) should be " — " (em dash)'  # noqa: RUF001
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col)
                        minus_or_double_found = True
                    elif " -- " in segment:
                        col = offset + segment.find(" -- ") + 1
                        error_msg = f'{self.RULES["H016"]}: " -- " should be " — " (em dash)'
                        yield self._format_error("H016", error_msg, filename, line_num=line_num, col=col)
                        minus_or_double_found = True

            offset += len(segment)
            if hyphen_found and minus_or_double_found:
                break

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

        # Check for em dash not surrounded by spaces
        if "—" in clean_line:
            line_matches = list(re.finditer(r"—", line))
            for i, match in enumerate(re.finditer(r"—", clean_line)):
                pos = match.start()
                before = clean_line[pos - 1] if pos > 0 else " "
                after = clean_line[pos + 1] if pos + 1 < len(clean_line) else " "
                col_pos = line_matches[i].start() if i < len(line_matches) else pos
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
def _check_double_spaces(self, filename: Path, line: str, _clean_line: str, line_num: int, content_lines: list[str], line_index: int) -> Generator[str, None, None]
```

Check for double spaces (H009).

Uses original line so that removal of inline code does not create
false double space when segments are concatenated.

<details>
<summary>Code:</summary>

```python
def _check_double_spaces(
        self, filename: Path, line: str, _clean_line: str, line_num: int, content_lines: list[str], line_index: int
    ) -> Generator[str, None, None]:
        if "  " not in line:
            return
        if line.startswith(("  ", "  *", "  -")):
            return
        if line_index > 0:
            prev_line = content_lines[line_index - 1]
            if prev_line.strip().startswith(("*", "-")):
                return
        if line.strip().startswith("|"):
            return

        col = line.index("  ") + 1
        yield self._format_error("H009", self.RULES["H009"], filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_empty_line_between_paragraphs`

```python
def _check_empty_line_between_paragraphs(self, filename: Path, content_lines: list[str], code_block_info: list, yaml_end_line: int) -> Generator[str, None, None]
```

Check that two consecutive paragraph lines have an empty line between them (H023).

<details>
<summary>Code:</summary>

```python
def _check_empty_line_between_paragraphs(
        self,
        filename: Path,
        content_lines: list[str],
        code_block_info: list,
        yaml_end_line: int,
    ) -> Generator[str, None, None]:
        for i in range(len(content_lines) - 1):
            line_i = content_lines[i]
            line_i_next = content_lines[i + 1]
            if not line_i.strip() or not line_i_next.strip():
                continue
            _, is_code_i = code_block_info[i] if i < len(code_block_info) else (line_i, False)
            _, is_code_next = code_block_info[i + 1] if i + 1 < len(code_block_info) else (line_i_next, False)
            if is_code_i or is_code_next:
                continue
            if self._inside_details_block(content_lines, i):
                continue
            if not self._is_paragraph_pair_requiring_empty_line(line_i, line_i_next):
                continue
            actual_line_num = (yaml_end_line - 1) + i + 1
            error_msg = f"{self.RULES['H023']}: add empty line between paragraphs"
            yield self._format_error("H023", error_msg, filename, line_num=actual_line_num)
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
        self,
        filename: Path,
        all_lines: list[str],
        rules: set,
        content: str = "",
        *,
        code_block_info: list | None = None,
        yaml_end_line: int = 1,
    ) -> Generator[str, None, None]:
        # H011: No empty line at end of file
        if "H011" in rules and all_lines and not content.endswith("\n"):
            yield self._format_error("H011", self.RULES["H011"], filename, line_num=len(all_lines))

        # H012: Two consecutive empty lines (skip inside code blocks)
        if "H012" in rules:
            yield from self._check_consecutive_empty_lines(filename, all_lines, code_block_info, yaml_end_line)
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

### ⚙️ Method `_check_horizontal_bar`

```python
def _check_horizontal_bar(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for horizontal bar '―' (U+2015, dialogue dash) which should not be used (H028).

<details>
<summary>Code:</summary>

```python
def _check_horizontal_bar(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        if "\u2015" not in clean_line:
            return
        col = line.find("\u2015") + 1
        yield self._format_error("H028", self.RULES["H028"], filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_html_tags`

```python
def _check_html_tags(self, filename: Path, line: str, _clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for HTML tags in content (H019). Exception: <details> and <summary> are allowed.

<details>
<summary>Code:</summary>

```python
def _check_html_tags(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        line_lower = line.lower()
        for tag in self.FORBIDDEN_HTML_TAGS:
            if tag.lower() not in line_lower:
                continue
            pos = line_lower.find(tag.lower())
            rest = line_lower[pos:]
            if rest.startswith(("<details", "<details>", "</details>", "<summary", "<summary>", "</summary>")):
                continue
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

### ⚙️ Method `_check_image_not_at_line_start`

```python
def _check_image_not_at_line_start(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]
```

Check that image markdown '![' is at start of (trimmed) line (H026).

<details>
<summary>Code:</summary>

```python
def _check_image_not_at_line_start(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        trimmed = line.strip()
        if "![" not in trimmed or trimmed.find("![") == 0:
            return
        col = line.find("![") + 1
        yield self._format_error("H026", self.RULES["H026"], filename, line_num=line_num, col=col)
```

</details>

### ⚙️ Method `_check_incorrect_words`

```python
def _check_incorrect_words(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for incorrect word forms (H006). Uses pre-compiled patterns from \_INCORRECT_WORD_PATTERNS.

<details>
<summary>Code:</summary>

```python
def _check_incorrect_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        for incorrect_word, (pattern, correct_word) in self._INCORRECT_WORD_PATTERNS.items():
            if pattern.search(clean_line):
                match = pattern.search(line)
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
        pattern = r"[.!?]\s+([a-zа-яё])"  # noqa: RUF001  # ignore: HP001
        exceptions = ["e.g.", "i.e.", "т. е", "т. д", "т. ч", "т. п"]  # noqa: RUF001  # ignore: HP001

        for match in re.finditer(pattern, clean_line):
            letter = match.group(1)
            pos = match.start()
            context = clean_line[max(0, pos - 4) : match.end()]
            if any(exc in context.lower() for exc in exceptions):
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
def _check_non_code_line_rules(self, filename: Path, line: str, line_num: int, content_lines: list[str], line_index: int, code_block_info: list, rules: set, yaml_end_line: int) -> Generator[str, None, None]
```

Check rules that apply only to non-code lines (markdown content, not YAML/code).

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
        yaml_end_line: int,
        *,
        lang: str = "",
    ) -> Generator[str, None, None]:
        # Remove inline code and URLs before text checks
        clean_line = self._remove_inline_code(line)
        clean_line = re.sub(r"\]\([^)]*\)", "]()", clean_line)
        clean_line = re.sub(r"<[^>]*>", "<>", clean_line)

        if "H006" in rules:
            yield from self._check_incorrect_words(filename, line, clean_line, line_num)

        if "H009" in rules:
            yield from self._check_double_spaces(filename, line, clean_line, line_num, content_lines, line_index)

        if "H013" in rules:
            yield from self._check_colon_before_code(
                filename, line, line_num, content_lines, line_index, code_block_info
            )

        if "H014" in rules:
            yield from self._check_colon_before_image(filename, line, line_num, content_lines, line_index)

        if "H015" in rules:
            yield from self._check_space_before_punctuation(filename, line, clean_line, line_num)

        if "H016" in rules and line_num >= yaml_end_line:
            yield from self._check_dash_usage(filename, line, clean_line, line_num)

        if "H017" in rules:
            if "..." in clean_line:
                col = line.index("...") + 1 if "..." in line else clean_line.index("...") + 1
                error_msg = f'{self.RULES["H017"]}: "..." should be "…"'
                yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)
            elif clean_line.rstrip().endswith("\u2026"):
                trimmed = line.rstrip()
                col = trimmed.rfind("\u2026") + 1
                error_msg = f'{self.RULES["H017"]}: ellipsis "…" at end of line'
                yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)

        if "H018" in rules:
            yield from self._check_quotes(filename, line, clean_line, line_num)

        if "H019" in rules:
            yield from self._check_html_tags(filename, line, clean_line, line_num)

        if "H020" in rules:
            yield from self._check_image_caption(filename, line, line_num)

        if "H021" in rules:
            yield from self._check_lowercase_after_punctuation(filename, line, clean_line, line_num)

        if "H024" in rules and lang == "ru":
            yield from self._check_russian_polite_pronouns(filename, line, clean_line, line_num)

        if "H025" in rules:
            yield from self._check_x_instead_of_times(filename, line, line_num)

        if "H026" in rules:
            yield from self._check_image_not_at_line_start(filename, line, line_num)

        if "H028" in rules:
            yield from self._check_horizontal_bar(filename, line, clean_line, line_num)

        if "H029" in rules:
            yield from self._check_numero_space(filename, line, line_num)

        if "H030" in rules:
            yield from self._check_question_mark_period(filename, line, line_num)
```

</details>

### ⚙️ Method `_check_numero_space`

```python
def _check_numero_space(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]
```

Check that '№' is followed by a space (H029).

Uses a regex lookahead to match '№' only when the next character exists and is not a space,
which naturally excludes '№' at the end of a line.

<details>
<summary>Code:</summary>

```python
def _check_numero_space(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        for match in re.finditer(r"\u2116(?=[^ ])", line):  # № followed by a non-space character
            yield self._format_error("H029", self.RULES["H029"], filename, line_num=line_num, col=match.start() + 1)
```

</details>

### ⚙️ Method `_check_question_mark_period`

```python
def _check_question_mark_period(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]
```

Check for question mark followed by period '?.' (H030).

<details>
<summary>Code:</summary>

```python
def _check_question_mark_period(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code and "?." in segment:
                col = offset + segment.find("?.") + 1
                yield self._format_error("H030", self.RULES["H030"], filename, line_num=line_num, col=col)
                return
            offset += len(segment)
```

</details>

### ⚙️ Method `_check_quotes`

```python
def _check_quotes(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for incorrect quote characters (H018).

Exception: straight double quote after a digit is allowed (inch notation, e.g. 14", 15.6").

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
            if char not in clean_line:
                continue
            if char == '"':
                pos = 0
                while True:
                    pos = clean_line.find('"', pos)
                    if pos < 0:
                        break
                    if pos > 0 and clean_line[pos - 1].isdigit():
                        pos += 1
                        continue
                    # Find column in original line: first non-inch " occurrence
                    idx = 0
                    col = pos + 1
                    while True:
                        q = line.find('"', idx)
                        if q < 0:
                            break
                        if q == 0 or not line[q - 1].isdigit():
                            col = q + 1
                            break
                        idx = q + 1
                    error_msg = f"{self.RULES['H018']}: found {description}"
                    yield self._format_error("H018", error_msg, filename, line_num=line_num, col=col)
                    return
                continue
            pos = line.find(char) if char in line else clean_line.find(char)
            error_msg = f"{self.RULES['H018']}: found {description}"
            yield self._format_error("H018", error_msg, filename, line_num=line_num, col=pos + 1)
```

</details>

### ⚙️ Method `_check_russian_polite_pronouns`

```python
def _check_russian_polite_pronouns(self, filename: Path, line: str, _clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for capitalized Russian polite pronouns (H024). Use lowercase when addressing the reader.

Exception: pronoun at sentence start is allowed:

- after line start or after .!?;
- after opening guillemet « (direct speech, e.g. «Ваша задача); # ignore: HP001
- after dash at line start (dialogue, e.g. — Ваша работа хороша). # ignore: HP001
  Yields at most one error per line.

<details>
<summary>Code:</summary>

```python
def _check_russian_polite_pronouns(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        boundary_before = r"(?<![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001
        boundary_after = r"(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001 # ignore: HP001

        code_ranges: list[tuple[int, int]] = []
        pos = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if in_code:
                code_ranges.append((pos, pos + len(segment)))
            pos += len(segment)

        def inside_inline_code(offset: int) -> bool:
            return any(s <= offset < e for s, e in code_ranges)

        def at_sentence_start(match_start: int) -> bool:
            text_before = line[:match_start]
            stripped = text_before.strip()
            if not stripped:
                return True
            if re.search(r"[.!?]\s*$", text_before):
                return True
            if stripped.endswith("\u00ab"):  # After «
                return True
            return bool(re.match(r"^\s*[—\-]\s*$", text_before))  # Dialogue dash at line start

        for word in self.RUSSIAN_POLITE_PRONOUNS_CAPITALIZED:
            pattern = boundary_before + re.escape(word) + boundary_after
            for match in re.finditer(pattern, line):
                if inside_inline_code(match.start()):
                    continue
                if at_sentence_start(match.start()):
                    continue
                error_msg = f'{self.RULES["H024"]}: use lowercase "{word.lower()}" when addressing reader'
                yield self._format_error("H024", error_msg, filename, line_num=line_num, col=match.start() + 1)
                return
```

</details>

### ⚙️ Method `_check_space_before_punctuation`

```python
def _check_space_before_punctuation(self, filename: Path, line: str, _clean_line: str, line_num: int) -> Generator[str, None, None]
```

Check for space before punctuation marks (H015).

Uses original line so that removal of inline code (e.g. `word`:)
does not create false " :" when segments are concatenated.
Matches inside inline code (e.g. `cd ..`) are skipped.

<details>
<summary>Code:</summary>

```python
def _check_space_before_punctuation(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        code_ranges: list[tuple[int, int]] = []
        pos = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if in_code:
                code_ranges.append((pos, pos + len(segment)))
            pos += len(segment)

        def _inside_inline_code(offset: int) -> bool:
            return any(start <= offset < end for start, end in code_ranges)

        patterns = [
            (r" \.", " ."),
            (r" ,", " ,"),
            (r" ;", " ;"),
            (r" :", " :"),
            (r" \?", " ?"),
        ]

        for pattern, display in patterns:
            match = re.search(pattern, line)
            if match and not _inside_inline_code(match.start()):
                error_msg = f'{self.RULES["H015"]}: found "{display}"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=match.start() + 1)

        # Special handling for " !" — skip special Markdown/directive markers
        if " !" in line:
            exceptions = [" !details", " !note", " !important", " !warning"]
            pos_found = line.find(" !")
            if (
                not _inside_inline_code(pos_found)
                and not any(line[pos_found:].startswith(exc) for exc in exceptions)
                and not line.strip().startswith("!")
            ):
                error_msg = f'{self.RULES["H015"]}: found " !"'
                yield self._format_error("H015", error_msg, filename, line_num=line_num, col=pos_found + 1)
```

</details>

### ⚙️ Method `_check_x_instead_of_times`

```python
def _check_x_instead_of_times(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]
```

Check for Latin 'x' or Cyrillic 'x' used instead of multiplication sign '\*' (H025).

Only checks text outside inline code. Exceptions: 'x86' and 'x64'; digit + 'x' + space (e.g. 2x Type-C).

<details>
<summary>Code:</summary>

```python
def _check_x_instead_of_times(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                for pos, char in enumerate(segment):
                    if char not in ("x", "\u0445"):  # Latin x, Cyrillic x  # ignore: HP001
                        continue
                    if pos <= 0 or pos >= len(segment) - 1:
                        continue
                    before = segment[pos - 1]
                    after = segment[pos + 1]
                    if before not in " \t" and not before.isdigit():
                        continue
                    if after not in " \t" and not after.isdigit():
                        continue
                    if char == "x":  # Latin x
                        if before == " " and segment[pos : pos + 3] in ("x86", "x64"):
                            continue
                        if before.isdigit() and after in " \t":
                            continue  # e.g. "2x Type-C", "1x USB" — Latin x is correct
                        error_msg = f'{self.RULES["H025"]}: "x" should be "×"'  # noqa: RUF001
                    else:  # Cyrillic x  # ignore: HP001
                        error_msg = f'{self.RULES["H025"]}: "х" should be "×"'  # noqa: RUF001  # ignore: HP001
                    yield self._format_error("H025", error_msg, filename, line_num=line_num, col=offset + pos + 1)
            offset += len(segment)
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
        for i, line in enumerate(all_lines[1:], start=2):
            if line.strip() == "---":
                return i
        return len(all_lines)
```

</details>

### ⚙️ Method `_find_yaml_end_line`

```python
def _find_yaml_end_line(self, lines: list[str]) -> int
```

Find the first content line number after the YAML block (1-based).

<details>
<summary>Code:</summary>

```python
def _find_yaml_end_line(self, lines: list[str]) -> int:
        if not lines or lines[0].strip() != "---":
            return 1
        for i, line in enumerate(lines[1:], start=2):
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
        for i, line in enumerate(all_lines[1:], start=2):
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

### ⚙️ Method `_inside_details_block`

```python
def _inside_details_block(self, content_lines: list[str], line_index: int) -> bool
```

Return True if line at line_index is inside a <details>...</details> block.

<details>
<summary>Code:</summary>

```python
def _inside_details_block(self, content_lines: list[str], line_index: int) -> bool:
        nest = 0
        for j in range(line_index + 1):
            line_lower = content_lines[j].strip().lower()
            if "<details" in line_lower:
                nest += 1
            if "</details>" in line_lower:
                nest -= 1
        return nest > 0
```

</details>

### ⚙️ Method `_is_paragraph_pair_requiring_empty_line`

```python
def _is_paragraph_pair_requiring_empty_line(self, line_i: str, line_i_next: str) -> bool
```

Return True if these two consecutive non-empty lines should have an empty line between them.

<details>
<summary>Code:</summary>

```python
def _is_paragraph_pair_requiring_empty_line(self, line_i: str, line_i_next: str) -> bool:
        stripped_i = line_i.strip()
        if not stripped_i:
            return False

        # Do not require empty line around <details>/<summary> tags
        details_tags = ("<details", "</details>", "<summary", "</summary>")
        if stripped_i.lower().startswith(details_tags) or line_i_next.strip().lower().startswith(details_tags):
            return False

        # Skip lines starting with block-level markers that don't need separation
        if line_i.strip().startswith(("$$", "* ", "- ", "  * ", "  - ")):
            return False

        # Next line starts with image or math block
        if line_i_next.strip().startswith(("![", "$$")):
            return False

        # Table, blockquote, numbered list, or unordered list
        first_char = stripped_i[0]
        return not (first_char in ("|", "*", ">") or first_char.isdigit())
```

</details>

### ⚙️ Method `_is_table_cell_only_dash`

```python
def _is_table_cell_only_dash(self, line: str, pos: int) -> bool
```

Return True if position pos in line is inside a table cell that contains only a hyphen.

<details>
<summary>Code:</summary>

```python
def _is_table_cell_only_dash(self, line: str, pos: int) -> bool:
        parts = line.split("|")
        min_count_parts = 2
        if len(parts) < min_count_parts:
            return False
        start = 0
        for part in parts:
            end = start + len(part)
            if start <= pos < end:
                return part.strip() == "-"
            start = end + 1  # +1 for the | separator
        return False
```

</details>

### ⚙️ Method `_remove_inline_code`

```python
def _remove_inline_code(self, line: str) -> str
```

Remove inline code segments from line, keeping only non-code text.

<details>
<summary>Code:</summary>

```python
def _remove_inline_code(self, line: str) -> str:
        return "".join(segment for segment, in_code in h.md.identify_code_blocks_line(line) if not in_code)
```

</details>

### ⚙️ Method `_should_check_paragraph_end`

```python
def _should_check_paragraph_end(self, line: str) -> bool
```

Return True if line is a regular paragraph that should end with colon before code/image.

<details>
<summary>Code:</summary>

````python
def _should_check_paragraph_end(self, line: str) -> bool:
        stripped = line.strip()
        return bool(stripped) and stripped != "```" and not stripped.startswith(("![", "#"))
````

</details>
