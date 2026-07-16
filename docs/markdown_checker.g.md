---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `markdown_checker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MarkdownChecker`](#️-class-markdownchecker)
  - [⚙️ Method `__call__`](#️-method-__call__)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `check`](#️-method-check)
  - [⚙️ Method `check_directory`](#️-method-check_directory)
  - [⚙️ Method `find_markdown_files`](#️-method-find_markdown_files)

</details>

## 🏛️ Class `MarkdownChecker`

```python
class MarkdownChecker
```

Class for checking Markdown files for compliance with specified rules.

Rules:

- **H001** - Presence of a space in the Markdown file name.
- **H002** - Presence of a space in the path to the Markdown file.
- **H003** - YAML is missing (except `README.md` and `LICENSE.md`).
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
- **H021** - Lowercase letter after sentence-ending punctuation (abbreviations like `англ.`, # ignore: HP001
  `лат.`, `см.` are allowed). # ignore: HP001
- **H022** - Non-breaking space character found.
- **H023** - Capitalized Russian polite pronoun (use lowercase when addressing reader; ru only).
- **H024** - Latin "x" or Cyrillic "x" used instead of multiplication sign "x".
- **H025** - Image markdown "![" found not at start of line.
- **H026** - Horizontal bar "―" (dialogue dash) should not be used.
- **H027** - Space required after "№".
- **H028** - Question mark followed by period (?.).
- **H029** - Space required after colon in inline emphasis.
- **H030** - Colon outside inline emphasis (should be inside when line continues after colon).
- **H031** - Invalid or placeholder image alt text (empty, editor placeholder, or lowercase start).
- **H032** - Two consecutive dots (typo for period or incomplete ellipsis; `../` paths are allowed).
- **H033** - Unclosed fenced code block.
- **H034** - Code fence without language identifier.
- **H035** - Missing figure caption after image.
- **H036** - Missing space after `#` in ATX heading.
- **H037** - Skipped heading level (e.g. H1 to H3 without H2).
- **H038** - Multiple H1 headings in one file.
- **H039** - Backslash in local Markdown path.
- **H040** - `lang` field does not match document language.
- **H041** - Bare URL in text (not wrapped in `<>` or link).
- **H042** - Invisible Unicode character found.
- **H043** - Unmatched guillemet on line.
- **H044** - Missing space before `%` or `°` (Russian typography).
- **H045** - Broken relative Markdown link or image.
- **H046** - Wrong line endings (must match nearest `.gitattributes` `eol=`, else CRLF).
- **H047** - BOM at start of file.
- **H048** - Unicode replacement character U+FFFD found.
- **H049** - Mixed Latin and Cyrillic letters in one word.
- **H050** - Missing space after punctuation mark before a letter.
- **H051** - Malformed punctuation sequence.
- **H052** - Heading level deeper than H6.
- **H053** - Unbalanced `<details>` / `<summary>` tags.
- **H054** - Repeated adjacent word.
- **H055** - Broken internal fragment link.
- **H056** - Unbalanced inline code in table cell.
- **H057** - Trailing period at end of ATX heading.
- **H058** - Punctuation (`.`, `,`, `;`, `:`) before closing guillemet `»`
  (Russian typography; `!»` / `?»` / `…»` are allowed; single-letter abbreviations
  like `«и т. д.»` are exempt).

<details>
<summary>Code:</summary>

````python
class MarkdownChecker:

    # Minimum length for a line to be treated as italic-only caption (e.g. _text_)
    _MIN_ITALIC_CAPTION_LEN: ClassVar[int] = 2

    # Length of empty single-line display math ``$$$$``; real content must be longer
    _EMPTY_SINGLE_LINE_DISPLAY_MATH_LEN: ClassVar[int] = 4

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

    # Image URL/alt patterns that do not require a colon in the preceding paragraph (H014)
    _IMAGE_H014_SKIP_SUBSTRINGS: ClassVar[tuple[str, ...]] = (
        "![Featured image](",
        "img.shields.io",
        "badgen.net",
        "<!-- no-caption -->",
    )

    # Filenames exempt from H003 (YAML is missing)
    _H003_EXEMPT_FILENAMES: ClassVar[frozenset[str]] = frozenset({"README.MD", "LICENSE.MD"})

    # Image caption patterns generated by ``generate_image_captions`` (H035)
    _IMAGE_CAPTION_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^_\s*(?:Figure\s+\d+:|Рисунок\s+\d+\s+—).+_$"  # ignore: HP001
    )

    # ATX heading without space after hash marks (H036)
    _ATX_HEADING_NO_SPACE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\s{0,3}#{1,6}[^\s#]")

    # ATX heading with level (H037, H038, H057)
    _ATX_HEADING_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(#{1,6})\s+(.*)$")

    # Trailing closed-ATX hashes (H057): ``## Title ##``
    _ATX_CLOSING_HASHES_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\s+#+\s*$")

    # ATX heading deeper than H6 (H052); space after hashes optional
    _ATX_HEADING_TOO_DEEP_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\s{0,3}(#{7,})\s*")

    # Backslash in markdown link/image URL (H039)
    _BACKSLASH_PATH_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\]\(([^)]*\\[^)]*)\)")

    # Bare URL in prose (H041)
    _BARE_URL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"(?<![(<\[])(https?://[^\s<>)\]]+)")

    # Markdown link/image destination (H045, H055)
    _LINK_DESTINATION_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\]\(([^)]+)\)")

    # Letter token that may mix Latin and Cyrillic scripts (H049)
    _MIXED_SCRIPT_TOKEN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"[A-Za-z\u0400-\u04FF]+")
    _LATIN_LETTER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"[A-Za-z]")
    _CYRILLIC_LETTER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"[\u0400-\u04FF]")

    # Intentional mixed-script stylizations allowed by H049 (casefolded)
    _MIXED_SCRIPT_ALLOWLIST: ClassVar[frozenset[str]] = frozenset(
        {
            "zомбилэнд",  # noqa: RUF001  # ignore: HP001
            "духless",  # noqa: RUF001  # ignore: HP001
            "vизитеры",  # noqa: RUF001  # ignore: HP001
        }
    )

    # Missing space after punctuation before a letter (H050)
    _MISSING_SPACE_AFTER_PUNCT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"([,;!?])(?=[^\W\d_])", re.UNICODE)

    # Malformed punctuation sequences (H051).
    # Word+``.,`` requires 6+ letters so short abbrevs like ``напр.,`` / ``ул.,`` are ignored.  # ignore: HP001
    _MALFORMED_PUNCT_SEQUENCE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"(?::\.|(?:[»\"”'])\.,|(?:[^\W\d_]{6,})\.,)",
        re.UNICODE,
    )
    _MALFORMED_TIME_HEADING_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\s*#{1,6}\s+\d{1,2}(?:;:|::)\d{2}\s*$")

    # Punctuation before closing guillemet (H058). Period only after 2+ letters so
    # single-letter abbreviations like ``т. д.»`` / ``т. е.»`` are ignored.  # noqa: RUF003  # ignore: HP001
    _PUNCT_BEFORE_CLOSING_GUILLEMET_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"(?:[^\W\d_]{2,}\.|[,;:])»",
        re.UNICODE,
    )

    # Repeated adjacent word (H054); ignore short tokens like ``c c``.
    # Include hyphenated compounds (`well-known``) as one token so
    # ``well well-known`` is not treated as a repeat of ``well``.
    _WORD_TOKEN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)
    _H054_MIN_WORD_LEN: ClassVar[int] = 3

    # Allowed HTML container tags for balance check (H053)
    _DETAILS_OPEN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"<details\b[^>]*>", re.IGNORECASE)
    _DETAILS_CLOSE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"</details\s*>", re.IGNORECASE)
    _SUMMARY_OPEN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"<summary\b[^>]*>", re.IGNORECASE)
    _SUMMARY_CLOSE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"</summary\s*>", re.IGNORECASE)

    # Invisible characters beyond U+00A0 (H042)
    _INVISIBLE_CHARACTERS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("\u200b", "zero-width space"),
        ("\u00ad", "soft hyphen"),
        ("\u202f", "narrow no-break space"),
        ("\u2060", "word joiner"),
    )

    # Minimum share of Cyrillic lines to flag lang mismatch for ``lang: en`` (H040)
    _H040_CYRILLIC_LINE_RATIO: ClassVar[float] = 0.3

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
        "H023": "Capitalized Russian polite pronoun (use lowercase when addressing reader)",
        "H024": "Latin x or Cyrillic x used instead of multiplication sign ×",  # ignore: HP001  # noqa: RUF001
        "H025": "Image markdown ![ found not at start of line",
        "H026": "Horizontal bar ― (dialogue dash) should not be used",
        "H027": "Space required after №",
        "H028": "Question mark followed by period (?.)",
        "H029": "Space required after colon in inline emphasis",
        "H030": "Colon outside inline emphasis (should be inside)",
        "H031": "Invalid or placeholder image alt text",
        "H032": "Two consecutive dots",
        "H033": "Unclosed fenced code block",
        "H034": "Code fence without language identifier",
        "H035": "Missing figure caption after image",
        "H036": "Missing space after # in ATX heading",
        "H037": "Skipped heading level",
        "H038": "Multiple H1 headings in one file",
        "H039": "Backslash in local Markdown path",
        "H040": "lang field does not match document language",
        "H041": "Bare URL in text",
        "H042": "Invisible Unicode character found",
        "H043": "Unmatched guillemet on line",
        "H044": "Missing space before % or °",
        "H045": "Broken relative Markdown link",
        "H046": "Wrong line endings",
        "H047": "BOM at start of file",
        "H048": "Unicode replacement character found",
        "H049": "Mixed Latin and Cyrillic letters in one word",
        "H050": "Missing space after punctuation mark",
        "H051": "Malformed punctuation sequence",
        "H052": "Heading level deeper than H6",
        "H053": "Unbalanced details or summary HTML tags",
        "H054": "Repeated adjacent word",
        "H055": "Broken internal fragment link",
        "H056": "Unbalanced inline code in table cell",
        "H057": "Trailing period at end of ATX heading",
        "H058": "Punctuation before closing guillemet",
    }

    _IMAGE_ALT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
    _TWO_DOTS_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"(?<!\.)\.\.(?![\./])")
    _MATH_DELIMITER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\s*\$\$\s*$")
    _HORIZONTAL_RULE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(?:\*\s*){3,}$|^(?:-\s*){3,}$|^(?:_\s*){3,}$")

    # Abbreviations whose trailing period must not trigger H021
    _H021_ALLOWED_TAIL_LEN: ClassVar[int] = 10
    _H021_PERIOD_ABBREVS: ClassVar[frozenset[str]] = frozenset(
        {
            "англ.",  # ignore: HP001
            "анг.",  # ignore: HP001
            "лат.",  # ignore: HP001
            "нем.",  # ignore: HP001
            "франц.",  # ignore: HP001
            "греч.",  # ignore: HP001
            "рус.",  # noqa: RUF001  # ignore: HP001
            "итал.",  # ignore: HP001
            "исп.",  # ignore: HP001
            "порт.",  # ignore: HP001
            "укр.",  # ignore: HP001
            "кит.",  # ignore: HP001
            "яп.",  # ignore: HP001
            "см.",  # ignore: HP001
            "e.g.",
            "i.e.",
            "т. е.",  # noqa: RUF001  # ignore: HP001
            "т. д.",  # ignore: HP001
            "т. ч.",  # ignore: HP001
            "т. п.",  # ignore: HP001
        }
    )
    _H021_RU_DOTTED_ABBREV_SECONDS: ClassVar[frozenset[str]] = frozenset({"е", "д", "ч", "п"})  # noqa: RUF001  # ignore: HP001

    # Patterns for H029: colon inside or after inline emphasis without following space
    _EMPHASIS_COLON_NO_SPACE_PATTERNS: ClassVar[tuple[re.Pattern[str], ...]] = (
        re.compile(r"\*\*\*[^*\n]+:\*\*\*(?=\S)"),
        re.compile(r"\*\*\*[^*\n]+\*\*\*:(?=\S)"),
        re.compile(r"\*\*[^*\n]+:\*\*(?=\S)"),
        re.compile(r"\*\*[^*\n]+\*\*:(?=\S)"),
        re.compile(r"(?<!\*)\*(?!\*)[^*\n]+:\*(?!\*)(?=\S)"),
        re.compile(r"(?<!\*)\*(?!\*)[^*\n]+\*(?!\*):(?=\S)"),
        re.compile(r"__[^_\n]+:__(?=\S)"),
        re.compile(r"__[^_\n]+__:(?=\S)"),
        re.compile(r"(?<!_)_(?!_)[^_\n]+:_(?!_)(?=\S)"),
        re.compile(r"(?<!_)_(?!_)[^_\n]+_(?!_):(?=\S)"),
        re.compile(r"~~[^~\n]+:~~(?=\S)"),
        re.compile(r"~~[^~\n]+~~:(?=\S)"),
    )

    # Patterns for H030: colon outside inline emphasis (should be inside markers)
    _EMPHASIS_COLON_OUTSIDE_PATTERNS: ClassVar[tuple[re.Pattern[str], ...]] = (
        re.compile(r"\*\*\*[^*\n]+\*\*\*:"),
        re.compile(r"\*\*[^*\n]+\*\*:"),
        re.compile(r"(?<!\*)\*(?!\*)[^*\n]+\*(?!\*):"),
        re.compile(r"__[^_\n]+__:"),
        re.compile(r"(?<!_)_(?!_)[^_\n]+_:"),
        re.compile(r"~~[^~\n]+~~:"),
    )

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
        # TypeScript, Node.js, and common tech terms (H006 extension)
        "typescript": "TypeScript",
        "Typescript": "TypeScript",
        "nodejs": "Node.js",
        "Nodejs": "Node.js",
        "vscode": "VS Code",
        "Vscode": "VS Code",
        "wifi": "Wi-Fi",
        "Wifi": "Wi-Fi",
        "WIFI": "Wi-Fi",
        "json": "JSON",
        "yaml": "YAML",
        "sql": "SQL",
        "api": "API",
        "ui": "UI",
        "ux": "UX",
        "windows": "Windows",
        "linux": "Linux",
        "macos": "macOS",
        "Macos": "macOS",
        "MacOS": "macOS",
        "powershell": "PowerShell",
        "Powershell": "PowerShell",
        "docker": "Docker",
        "python": "Python",
        # Russian orthography (SFU web style / Gramota)
        "интернет": "Интернет",  # ignore: HP001
        "интернета": "Интернета",  # ignore: HP001
        "интернету": "Интернету",  # ignore: HP001
        "интернетом": "Интернетом",  # ignore: HP001
        "интернете": "Интернете",  # ignore: HP001
        "он-лайн": "онлайн",  # ignore: HP001
        "Он-лайн": "Онлайн",  # ignore: HP001
        "ОН-ЛАЙН": "онлайн",  # noqa: RUF001  # ignore: HP001
        "on-line": "онлайн",  # ignore: HP001
        "On-line": "Онлайн",  # ignore: HP001
        "ON-LINE": "онлайн",  # ignore: HP001
        "ВУЗ": "вуз",  # noqa: RUF001  # ignore: HP001
        "ВУЗа": "вуза",  # noqa: RUF001  # ignore: HP001
        "ВУЗу": "вузу",  # noqa: RUF001  # ignore: HP001
        "ВУЗом": "вузом",  # ignore: HP001
        "ВУЗе": "вузе",  # noqa: RUF001  # ignore: HP001
        "ВУЗы": "вузы",  # ignore: HP001
        "ВУЗов": "вузов",  # ignore: HP001
        "ВУЗам": "вузам",  # ignore: HP001
        "ВУЗами": "вузами",  # ignore: HP001
        "ВУЗах": "вузах",  # noqa: RUF001  # ignore: HP001
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
        "<br",
        "<div",
        "<span",
        "<img",
        "<ul",
        "<ol",
        "<li",
        "<font",
        "</",
    ]

    def __call__(
        self, filename: Path | str, *, select: set[str] | None = None, exclude_rules: set[str] | None = None
    ) -> list[str]:
        """Check Markdown file for compliance with specified rules."""
        return self.check(filename, select=select, exclude_rules=exclude_rules)

    def __init__(self, project_root: Path | str | None = None) -> None:
        """Initialize the MarkdownChecker with all available rules."""
        self.all_rules = set(self.RULES.keys())
        self.project_root = self._determine_project_root(project_root)

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

    def _build_display_math_line_indices(self, code_block_info: list) -> frozenset[int]:
        """Return content-line indices that belong to display-math ``$$...$$`` blocks."""
        display_math_lines: set[int] = set()
        in_math = False

        for index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue

            if self._MATH_DELIMITER_PATTERN.match(line):
                display_math_lines.add(index)
                in_math = not in_math
                continue

            stripped = line.strip()
            if (
                stripped.startswith("$$")
                and stripped.endswith("$$")
                and len(stripped) > self._EMPTY_SINGLE_LINE_DISPLAY_MATH_LEN
            ):
                display_math_lines.add(index)
                continue

            if in_math:
                display_math_lines.add(index)

        return frozenset(display_math_lines)

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

        # H042: Other invisible Unicode characters
        if "H042" in rules and not is_code_block:
            for char, description in self._INVISIBLE_CHARACTERS:
                if char in line:
                    col = line.index(char) + 1
                    error_msg = f"{self.RULES['H042']}: found {description}"
                    yield self._format_error("H042", error_msg, filename, line_num=line_num, col=col)
                    break

        # H048: Unicode replacement character (including inside code blocks)
        if "H048" in rules and "\ufffd" in line:
            start = 0
            while True:
                idx = line.find("\ufffd", start)
                if idx < 0:
                    break
                yield self._format_error("H048", self.RULES["H048"], filename, line_num=line_num, col=idx + 1)
                start = idx + 1

    def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Generate all errors found during checking."""
        yield from self._check_filename_rules(filename, rules)

        try:
            content = filename.read_text(encoding="utf-8")

            if "H047" in rules and content.startswith("\ufeff"):
                yield self._format_error("H047", self.RULES["H047"], filename, line_num=1, col=1)

            all_lines = content.splitlines()
            yaml_end_line = self._find_yaml_end_line(all_lines)
            yaml_part, _ = h.md.split_yaml_content(content)

            try:
                yaml_data = yaml.safe_load(yaml_part.replace("---\n", "").replace("\n---", "")) if yaml_part else None
                lang = (yaml_data or {}).get("lang") or ""
            except yaml.YAMLError:
                yaml_data = None
                lang = ""

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules, yaml_data=yaml_data)
            content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
            code_block_info = list(h.md.identify_code_blocks(content_lines))
            yield from self._check_content_rules(
                filename,
                all_lines,
                yaml_end_line,
                rules,
                content,
                lang=lang,
                code_block_info=code_block_info,
                yaml_data=yaml_data,
            )
            yield from self._check_code_rules(filename, yaml_end_line, rules, code_block_info=code_block_info)

        except (OSError, UnicodeDecodeError) as e:
            yield self._format_error("H000", f"Exception error: {e}", filename)

    def _check_atx_heading_space(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for missing space after # in ATX heading (H036)."""
        match = self._ATX_HEADING_NO_SPACE_PATTERN.match(line)
        if match:
            col = match.end()
            yield self._format_error("H036", self.RULES["H036"], filename, line_num=line_num, col=col)

    def _check_backslash_in_path(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for backslash in Markdown link/image paths (H039)."""
        for match in self._BACKSLASH_PATH_PATTERN.finditer(line):
            col = match.start(1) + 1
            yield self._format_error("H039", self.RULES["H039"], filename, line_num=line_num, col=col)

    def _check_bare_url(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for bare URL in prose (H041)."""
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                for match in self._BARE_URL_PATTERN.finditer(segment):
                    col = offset + match.start(1) + 1
                    yield self._format_error("H041", self.RULES["H041"], filename, line_num=line_num, col=col)
            offset += len(segment)

    def _check_broken_internal_fragments(
        self, filename: Path, code_block_info: list, yaml_end_line: int
    ) -> Generator[str, None, None]:
        """Check same-file ``#fragment`` links against generated heading IDs (H055)."""
        heading_ids = self._collect_heading_ids(code_block_info)
        resolved_self = filename.resolve()

        for index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue
            offset = 0
            actual_line_num = (yaml_end_line - 1) + index + 1
            for segment, in_inline_code in h.md.identify_code_blocks_line(line):
                if not in_inline_code:
                    for match in self._LINK_DESTINATION_PATTERN.finditer(segment):
                        destination = self._extract_link_destination(match.group(1))
                        if not destination or "#" not in destination:
                            continue
                        path_part, fragment = destination.split("#", maxsplit=1)
                        fragment = unquote(fragment)
                        if not fragment:
                            continue
                        path_part = unquote(path_part)
                        if path_part:
                            if path_part.startswith(("http://", "https://", "mailto:", "data:")):
                                continue
                            target = (filename.parent / path_part).resolve()
                            if target != resolved_self:
                                continue
                        if fragment not in heading_ids:
                            col = offset + match.start(1) + 1
                            error_msg = f'{self.RULES["H055"]}: "#{fragment}" not found'
                            yield self._format_error("H055", error_msg, filename, line_num=actual_line_num, col=col)
                offset += len(segment)

    def _check_broken_relative_links(
        self, filename: Path, content: str, yaml_end_line: int
    ) -> Generator[str, None, None]:
        """Check that relative Markdown links point to existing files (H045).

        Skips fenced code blocks and inline code. Decodes percent-encoded paths and
        strips optional link titles / angle-bracket destinations.
        """
        all_lines = content.splitlines()
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        for index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue
            offset = 0
            for segment, in_inline_code in h.md.identify_code_blocks_line(line):
                if not in_inline_code:
                    for match in self._LINK_DESTINATION_PATTERN.finditer(segment):
                        destination = self._extract_link_destination(match.group(1))
                        if not destination or destination.startswith(("http://", "https://", "#", "mailto:", "data:")):
                            continue
                        path_part = unquote(destination.split("#", maxsplit=1)[0])
                        if not path_part:
                            continue
                        target = (filename.parent / path_part).resolve()
                        if not target.exists():
                            actual_line_num = (yaml_end_line - 1) + index + 1
                            col = offset + match.start(1) + 1
                            error_msg = f'{self.RULES["H045"]}: "{path_part}" not found'
                            yield self._format_error("H045", error_msg, filename, line_num=actual_line_num, col=col)
                offset += len(segment)

    # =========================================================================
    # Code Block Rules (H007)
    # =========================================================================

    def _check_code_rules(
        self, filename: Path, yaml_end_line: int, rules: set, *, code_block_info: list
    ) -> Generator[str, None, None]:
        """Check code block related rules."""
        code_block_delimiter: str | None = None
        opening_fence_line_num = 0

        for i, (line, _is_code_block) in enumerate(code_block_info):
            actual_line_num = (yaml_end_line - 1) + i + 1
            stripped = line.strip()

            match = re.match(r"^\s*(`{3,})(.*)", line)
            if not match:
                continue

            delimiter = match.group(1)
            info = match.group(2).strip()
            language_match = re.match(r"^(\w+)", info)
            language = language_match.group(1) if language_match else None

            if code_block_delimiter is None:
                code_block_delimiter = delimiter
                opening_fence_line_num = actual_line_num
                if "H034" in rules and not language:
                    col = line.index("`") + 1
                    yield self._format_error("H034", self.RULES["H034"], filename, line_num=actual_line_num, col=col)
                if "H007" in rules and language and language in self.INCORRECT_LANGUAGES:
                    col = stripped.index(language) + 1
                    correct = self.INCORRECT_LANGUAGES[language]
                    error_msg = f'{self.RULES["H007"]}: "{language}" should be "{correct}"'
                    yield self._format_error("H007", error_msg, filename, line_num=actual_line_num, col=col)
            elif code_block_delimiter == delimiter:
                code_block_delimiter = None

        if "H033" in rules and code_block_delimiter is not None:
            yield self._format_error(
                "H033",
                self.RULES["H033"],
                filename,
                line_num=opening_fence_line_num,
                col=1,
            )

    def _check_colon_before_code(
        self,
        filename: Path,
        line: str,
        line_num: int,
        line_index: int,
        code_block_info: list,
        display_math_lines: frozenset[int],
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

        if line_index in display_math_lines:
            return

        # Check pattern: non-empty line, empty line, code block start
        if not (next_line.strip() == "" and next_next_line.strip().startswith("```")):
            return

        last_char, col = self._paragraph_last_char(line)

        if any(marker in line for marker in self._COLON_SKIP_MARKERS):
            return
        if line.strip().startswith("<"):
            return
        if last_char != ":":
            error_msg = f'{self.RULES["H013"]}: last char is "{last_char}"'
            yield self._format_error("H013", error_msg, filename, line_num=line_num, col=col)

    def _check_colon_before_image(
        self,
        filename: Path,
        line: str,
        line_num: int,
        content_lines: list[str],
        line_index: int,
        *,
        display_math_lines: frozenset[int],
    ) -> Generator[str, None, None]:
        """Check for missing colon before image (H014)."""
        if line_index + 2 >= len(content_lines):
            return
        if not self._should_check_paragraph_end(line):
            return

        if line_index in display_math_lines:
            return

        next_line = content_lines[line_index + 1]
        next_next_line = content_lines[line_index + 2]

        # Check pattern: non-empty line, empty line, image
        if not (next_line.strip() == "" and next_next_line.strip().startswith("![")):
            return

        if any(sub in next_next_line for sub in self._IMAGE_H014_SKIP_SUBSTRINGS):
            return
        if "<!-- no-caption -->" in line:
            return
        if next_next_line.count("![") > 1:
            return

        last_char, col = self._paragraph_last_char(line)

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
            yield self._format_error("H014", error_msg, filename, line_num=line_num, col=col)

    def _check_colon_outside_emphasis(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for colon outside inline emphasis (H030).

        Colon after *, **, _, __, ~~ labels should be inside emphasis markers when
        the same line continues after the colon. A trailing colon at end of line is allowed.
        Uses original line; matches inside inline code are skipped.
        """
        code_ranges: list[tuple[int, int]] = []
        pos = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if in_code:
                code_ranges.append((pos, pos + len(segment)))
            pos += len(segment)

        def _inside_inline_code(offset: int) -> bool:
            return any(start <= offset < end for start, end in code_ranges)

        reported_cols: set[int] = set()
        for pattern in self._EMPHASIS_COLON_OUTSIDE_PATTERNS:
            for match in pattern.finditer(line):
                if _inside_inline_code(match.start()):
                    continue
                if not line[match.end() :].strip():
                    continue
                col = match.end()
                if col in reported_cols:
                    continue
                reported_cols.add(col)
                yield self._format_error("H030", self.RULES["H030"], filename, line_num=line_num, col=col)

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
        self,
        filename: Path,
        all_lines: list[str],
        yaml_end_line: int,
        rules: set,
        content: str = "",
        *,
        lang: str = "",
        code_block_info: list,
        yaml_data: dict | None = None,
    ) -> Generator[str, None, None]:
        """Check content-related rules working directly with original file lines."""
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines
        display_math_lines = self._build_display_math_line_indices(code_block_info)

        yield from self._check_file_level_rules(
            filename,
            all_lines,
            rules,
            content,
            code_block_info=code_block_info,
            yaml_end_line=yaml_end_line,
            lang=lang,
            yaml_data=yaml_data,
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
                    display_math_lines=display_math_lines,
                )

    def _check_dash_usage(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for incorrect dash/hyphen usage (H016). Applies only to markdown text, not YAML/code.

        Exception: ``--`` at the start of blockquote attribution lines (e.g. ``> -- Author``).
        """
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
                        if not self._is_blockquote_attribution_line(line):
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

    def _check_file_level_rules(
        self,
        filename: Path,
        all_lines: list[str],
        rules: set,
        content: str = "",
        *,
        code_block_info: list | None = None,
        yaml_end_line: int = 1,
        lang: str = "",
        yaml_data: dict | None = None,  # noqa: ARG002
    ) -> Generator[str, None, None]:
        """Check rules that apply to the entire file."""
        # H011: No empty line at end of file
        if "H011" in rules and all_lines and not content.endswith("\n"):
            yield self._format_error("H011", self.RULES["H011"], filename, line_num=len(all_lines))

        # H012: Two consecutive empty lines (skip inside code blocks)
        if "H012" in rules:
            yield from self._check_consecutive_empty_lines(filename, all_lines, code_block_info, yaml_end_line)

        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines

        if "H035" in rules and code_block_info is not None:
            yield from self._check_missing_figure_captions(filename, code_block_info, yaml_end_line)

        if "H037" in rules and code_block_info is not None:
            yield from self._check_skipped_heading_levels(filename, code_block_info, yaml_end_line)

        if "H038" in rules and code_block_info is not None:
            yield from self._check_multiple_h1_headings(filename, code_block_info, yaml_end_line)

        if "H040" in rules and lang and code_block_info is not None:
            yield from self._check_lang_content_mismatch(filename, content_lines, code_block_info, lang, yaml_end_line)

        if "H045" in rules:
            yield from self._check_broken_relative_links(filename, content, yaml_end_line)

        if "H046" in rules:
            yield from self._check_line_endings(filename)

        if "H053" in rules and code_block_info is not None:
            yield from self._check_unbalanced_details_summary(filename, code_block_info, yaml_end_line)

        if "H055" in rules and code_block_info is not None:
            yield from self._check_broken_internal_fragments(filename, code_block_info, yaml_end_line)

    # =========================================================================
    # Filename Rules (H001, H002)
    # =========================================================================

    def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Check filename-related rules."""
        if "H001" in rules and " " in filename.name:
            yield self._format_error("H001", self.RULES["H001"], filename)

        if "H002" in rules and " " in str(filename):
            yield self._format_error("H002", self.RULES["H002"], filename)

    def _check_heading_too_deep(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for ATX headings deeper than H6 (H052)."""
        match = self._ATX_HEADING_TOO_DEEP_PATTERN.match(line)
        if not match:
            return
        level = len(match.group(1))
        error_msg = f"{self.RULES['H052']}: found H{level}"
        yield self._format_error("H052", error_msg, filename, line_num=line_num, col=1)

    def _check_heading_trailing_period(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for trailing period at end of ATX heading (H057).

        A final ``.`` is forbidden; ``?``, ``!``, and ``…`` are allowed. An internal
        period before the last sentence is fine (e.g. ``Глава 5. Буди, буди!``).  # ignore: HP001
        """
        match = self._ATX_HEADING_PATTERN.match(line)
        if not match:
            return
        title = match.group(2).strip()
        title = self._ATX_CLOSING_HASHES_PATTERN.sub("", title).strip()
        title = title.replace(" <!-- top-section -->", "").replace("<!-- top-section -->", "").strip()
        if not title or title.endswith(("...", "…")):
            return
        if title.endswith("."):
            col = line.rfind(".") + 1
            yield self._format_error("H057", self.RULES["H057"], filename, line_num=line_num, col=col)

    def _check_horizontal_bar(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for horizontal bar '―' (U+2015, dialogue dash) which should not be used (H026)."""
        if "\u2015" not in clean_line:
            return
        col = line.find("\u2015") + 1
        yield self._format_error("H026", self.RULES["H026"], filename, line_num=line_num, col=col)

    def _check_html_tags(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for HTML tags in content (H019). Exception: <details> and <summary> are allowed.

        Skips inline code segments (e.g. `` `<file>...</file>` `` in backticks).
        """
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                segment_lower = segment.lower()
                for tag in self.FORBIDDEN_HTML_TAGS:
                    tag_lower = tag.lower()
                    if tag_lower not in segment_lower:
                        continue
                    pos = segment_lower.find(tag_lower)
                    rest = segment_lower[pos:]
                    if rest.startswith(("<details", "<details>", "</details>", "<summary", "<summary>", "</summary>")):
                        continue
                    error_msg = f'{self.RULES["H019"]}: found "{tag}"'
                    yield self._format_error("H019", error_msg, filename, line_num=line_num, col=offset + pos + 1)
            offset += len(segment)

    def _check_image_alt_text(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check image alt text for empty, placeholder, or lowercase-start issues (H031)."""
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                for match in self._IMAGE_ALT_PATTERN.finditer(segment):
                    image_markdown = match.group(0)
                    if any(sub in image_markdown for sub in self._IMAGE_H014_SKIP_SUBSTRINGS):
                        continue
                    alt_text = match.group(1)
                    issue = self._image_alt_text_issue(alt_text)
                    if issue is None:
                        continue
                    col = offset + match.start(1) + 1
                    error_msg = f"{self.RULES['H031']}: {issue}"
                    yield self._format_error("H031", error_msg, filename, line_num=line_num, col=col)
            offset += len(segment)

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
        """Check that image markdown '![' is at start of (trimmed) line (H025)."""
        trimmed = line.strip()
        if "![" not in trimmed or trimmed.find("![") == 0:
            return
        col = line.find("![") + 1
        yield self._format_error("H025", self.RULES["H025"], filename, line_num=line_num, col=col)

    def _check_incorrect_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for incorrect word forms (H006). Uses pre-compiled patterns from _INCORRECT_WORD_PATTERNS."""
        for incorrect_word, (pattern, correct_word) in self._INCORRECT_WORD_PATTERNS.items():
            for match in pattern.finditer(clean_line):
                start, end = match.span()
                if self._is_hyphenated_identifier_fragment(clean_line, start, end):
                    continue
                line_match = next(
                    (
                        m
                        for m in pattern.finditer(line)
                        if not self._is_hyphenated_identifier_fragment(line, m.start(), m.end())
                    ),
                    None,
                )
                col = line_match.start() + 1 if line_match else start + 1
                error_message = f'{self.RULES["H006"]}: "{incorrect_word}" should be "{correct_word}"'
                yield self._format_error("H006", error_message, filename, line_num=line_num, col=col)
                break

    def _check_lang_content_mismatch(
        self,
        filename: Path,
        _content_lines: list[str],
        code_block_info: list,
        lang: str,
        _yaml_end_line: int,
    ) -> Generator[str, None, None]:
        """Check that YAML lang matches document language (H040)."""
        prose_lines = 0
        cyrillic_lines = 0
        cyrillic_pattern = re.compile(r"[а-яА-ЯёЁ]")  # noqa: RUF001  # ignore: HP001

        for _index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "![")):
                continue
            prose_lines += 1
            if cyrillic_pattern.search(line):
                cyrillic_lines += 1

        if prose_lines == 0:
            return

        cyrillic_ratio = cyrillic_lines / prose_lines
        if lang == "en" and cyrillic_ratio >= self._H040_CYRILLIC_LINE_RATIO:
            yield self._format_error("H040", f"{self.RULES['H040']}: lang is en but Cyrillic text found", filename)
        elif lang == "ru" and cyrillic_lines == 0:
            yield self._format_error("H040", f"{self.RULES['H040']}: lang is ru but no Cyrillic text found", filename)

    def _check_line_endings(self, filename: Path) -> Generator[str, None, None]:
        """Check line endings against preferred EOL from ``.gitattributes`` (H046)."""
        preferred = h.dev.get_preferred_end_of_line(filename)
        raw = filename.read_bytes()
        if b"\n" not in raw:
            return
        has_crlf = b"\r\n" in raw
        if preferred == "lf":
            if has_crlf:
                error_msg = f"{self.RULES['H046']}: CRLF line endings instead of LF"
                yield self._format_error("H046", error_msg, filename, line_num=1, col=1)
            return
        if not has_crlf:
            error_msg = f"{self.RULES['H046']}: LF line endings instead of CRLF"
            yield self._format_error("H046", error_msg, filename, line_num=1, col=1)

    def _check_lowercase_after_punctuation(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for lowercase letter after sentence-ending punctuation (H021).

        Checks each non-inline-code segment separately so removed code (e.g.
        ``Optional. `"value"` stores``) does not falsely join a period with the
        next word. Periods in ordered-list and section numbers (``1.``,
        ``3.1.``) and known abbreviations (``англ.``, ``лат.``, ``см.``) are ignored.  # ignore: HP001
        """
        pattern = r"[.!?]\s+([a-zа-яё])"  # noqa: RUF001  # ignore: HP001

        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                for match in re.finditer(pattern, segment):
                    letter = match.group(1)
                    pos = match.start()
                    if self._is_h021_allowed_period(segment, pos, match.end()):
                        continue

                    col = offset + match.start(1) + 1
                    error_msg = f'{self.RULES["H021"]}: found lowercase "{letter}" after punctuation'
                    yield self._format_error("H021", error_msg, filename, line_num=line_num, col=col)
            offset += len(segment)

    def _check_malformed_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for malformed punctuation sequences (H051)."""
        if self._MALFORMED_TIME_HEADING_PATTERN.match(line):
            yield self._format_error("H051", self.RULES["H051"], filename, line_num=line_num, col=1)

        for match in self._MALFORMED_PUNCT_SEQUENCE_PATTERN.finditer(clean_line):
            snippet = match.group(0)
            col = line.find(snippet)
            if col < 0:
                col = match.start()
            error_msg = f'{self.RULES["H051"]}: "{snippet}"'
            yield self._format_error("H051", error_msg, filename, line_num=line_num, col=col + 1)

    def _check_missing_figure_captions(
        self, filename: Path, code_block_info: list, yaml_end_line: int
    ) -> Generator[str, None, None]:
        """Check for figure caption after image (H035)."""
        index = 0
        while index < len(code_block_info):
            line, in_code = code_block_info[index]
            if in_code or "![" not in line.strip():
                index += 1
                continue

            stripped = line.strip()
            if not stripped.startswith("!["):
                index += 1
                continue
            if any(sub in line for sub in self._IMAGE_H014_SKIP_SUBSTRINGS):
                index += 1
                continue

            actual_line_num = (yaml_end_line - 1) + index + 1
            search_index = index + 1
            has_caption = False
            while search_index < len(code_block_info):
                next_line, next_in_code = code_block_info[search_index]
                if next_in_code:
                    break
                if not next_line.strip():
                    search_index += 1
                    continue
                if self._IMAGE_CAPTION_PATTERN.match(next_line.strip()):
                    has_caption = True
                break

            if not has_caption:
                yield self._format_error("H035", self.RULES["H035"], filename, line_num=actual_line_num, col=1)
            index += 1

    def _check_missing_space_after_punctuation(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for missing space after ``,;!?`` before a letter (H050)."""
        reported_cols: set[int] = set()
        for match in self._MISSING_SPACE_AFTER_PUNCT_PATTERN.finditer(clean_line):
            punct = match.group(1)
            next_char = clean_line[match.end()]
            # Admonitions / callouts: ``[!NOTE]``, ``[!gallery]``, …
            if punct == "!" and match.start() > 0 and clean_line[match.start() - 1] == "[":
                continue
            # Exempt ASCII identifier-like joins such as ``1979a,b`` or ``x,y``.
            if (
                punct in ",;"
                and match.start() > 0
                and clean_line[match.start() - 1].isascii()
                and clean_line[match.start() - 1].isalnum()
                and next_char.isascii()
                and next_char.isalpha()
            ):
                continue
            snippet = clean_line[match.start() : match.end() + 1]
            # Prefer original-line column when the snippet still exists there.
            col = line.find(snippet, match.start())
            if col < 0:
                col = match.start()
            if col in reported_cols:
                continue
            reported_cols.add(col)
            error_msg = f'{self.RULES["H050"]}: "{snippet}"'
            yield self._format_error("H050", error_msg, filename, line_num=line_num, col=col + 1)

    def _check_mixed_script_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for words that mix Latin and Cyrillic letters (H049)."""
        for match in self._MIXED_SCRIPT_TOKEN_PATTERN.finditer(clean_line):
            token = match.group(0)
            if not (self._LATIN_LETTER_PATTERN.search(token) and self._CYRILLIC_LETTER_PATTERN.search(token)):
                continue
            if token.casefold() in self._MIXED_SCRIPT_ALLOWLIST:
                continue
            col = line.find(token)
            if col < 0:
                col = match.start()
            error_msg = f'{self.RULES["H049"]}: "{token}"'
            yield self._format_error("H049", error_msg, filename, line_num=line_num, col=col + 1)

    def _check_multiple_h1_headings(
        self, filename: Path, code_block_info: list, yaml_end_line: int
    ) -> Generator[str, None, None]:
        """Check for multiple H1 headings (H038)."""
        h1_count = 0
        for index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue
            match = self._ATX_HEADING_PATTERN.match(line)
            if match and len(match.group(1)) == 1:
                h1_count += 1
                if h1_count > 1:
                    actual_line_num = (yaml_end_line - 1) + index + 1
                    yield self._format_error("H038", self.RULES["H038"], filename, line_num=actual_line_num, col=1)
                    return

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
        display_math_lines: frozenset[int],
    ) -> Generator[str, None, None]:
        """Check rules that apply only to non-code lines (markdown content, not YAML/code)."""
        # Remove inline code, URLs, and identifier-like link labels before text checks
        clean_line = self._remove_inline_code(line)
        clean_line = re.sub(r"\]\([^)]*\)", "]()", clean_line)
        clean_line = re.sub(
            r"\[([^\]]*)\]\(\)",
            lambda m: "[]()" if self._is_identifier_like_link_label(m.group(1)) else m.group(0),
            clean_line,
        )
        clean_line = re.sub(
            r"!\[([^\]]*)\]\(\)",
            lambda m: "![]()" if self._is_identifier_like_link_label(m.group(1)) else m.group(0),
            clean_line,
        )
        clean_line = re.sub(r"<[^>]*>", "<>", clean_line)

        if "H006" in rules:
            yield from self._check_incorrect_words(filename, line, clean_line, line_num)

        if "H009" in rules:
            yield from self._check_double_spaces(filename, line, clean_line, line_num, content_lines, line_index)

        if "H013" in rules:
            yield from self._check_colon_before_code(
                filename, line, line_num, line_index, code_block_info, display_math_lines
            )

        if "H014" in rules:
            yield from self._check_colon_before_image(
                filename, line, line_num, content_lines, line_index, display_math_lines=display_math_lines
            )

        if "H015" in rules:
            yield from self._check_space_before_punctuation(filename, line, clean_line, line_num)

        if "H016" in rules and line_num >= yaml_end_line:
            yield from self._check_dash_usage(filename, line, clean_line, line_num)

        if "H017" in rules and "..." in clean_line:
            col = line.index("...") + 1 if "..." in line else clean_line.index("...") + 1
            error_msg = f'{self.RULES["H017"]}: "..." should be "…"'
            yield self._format_error("H017", error_msg, filename, line_num=line_num, col=col)

        if "H032" in rules:
            yield from self._check_two_dots(filename, line, clean_line, line_num)

        if "H018" in rules:
            yield from self._check_quotes(filename, line, clean_line, line_num)

        if "H019" in rules:
            yield from self._check_html_tags(filename, line, clean_line, line_num)

        if "H020" in rules:
            yield from self._check_image_caption(filename, line, line_num)

        if "H021" in rules:
            yield from self._check_lowercase_after_punctuation(filename, line, clean_line, line_num)

        if "H023" in rules and lang == "ru":
            yield from self._check_russian_polite_pronouns(filename, line, clean_line, line_num)

        if "H024" in rules:
            yield from self._check_x_instead_of_times(filename, line, line_num)

        if "H025" in rules:
            yield from self._check_image_not_at_line_start(filename, line, line_num)

        if "H026" in rules:
            yield from self._check_horizontal_bar(filename, line, clean_line, line_num)

        if "H027" in rules:
            yield from self._check_numero_space(filename, line, line_num)

        if "H028" in rules:
            yield from self._check_question_mark_period(filename, line, line_num)

        if "H029" in rules:
            yield from self._check_space_after_emphasis_colon(filename, line, line_num)

        if "H030" in rules:
            yield from self._check_colon_outside_emphasis(filename, line, line_num)

        if "H031" in rules:
            yield from self._check_image_alt_text(filename, line, line_num)

        if "H036" in rules:
            yield from self._check_atx_heading_space(filename, line, line_num)

        if "H039" in rules:
            yield from self._check_backslash_in_path(filename, line, line_num)

        if "H041" in rules:
            yield from self._check_bare_url(filename, line, line_num)

        if "H043" in rules:
            yield from self._check_unmatched_guillemets(filename, line, clean_line, line_num)

        if "H044" in rules and lang == "ru":
            yield from self._check_space_before_percent_or_degree(filename, line, clean_line, line_num)

        if "H049" in rules:
            yield from self._check_mixed_script_words(filename, line, clean_line, line_num)

        if "H050" in rules:
            yield from self._check_missing_space_after_punctuation(filename, line, clean_line, line_num)

        if "H051" in rules:
            yield from self._check_malformed_punctuation(filename, line, clean_line, line_num)

        if "H052" in rules:
            yield from self._check_heading_too_deep(filename, line, line_num)

        if "H057" in rules:
            yield from self._check_heading_trailing_period(filename, line, line_num)

        if "H058" in rules:
            yield from self._check_punctuation_before_closing_guillemet(filename, line, clean_line, line_num)

        if "H054" in rules:
            yield from self._check_repeated_adjacent_words(filename, line, clean_line, line_num)

        if "H056" in rules:
            yield from self._check_unbalanced_table_inline_code(filename, line, line_num)

    def _check_numero_space(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check that '№' is followed by a space (H027).

        Uses a regex lookahead to match '№' only when the next character exists and is not a space,
        which naturally excludes '№' at the end of a line.
        """
        for match in re.finditer(r"\u2116(?=[^ ])", line):  # № followed by a non-space character
            yield self._format_error("H027", self.RULES["H027"], filename, line_num=line_num, col=match.start() + 1)

    def _check_punctuation_before_closing_guillemet(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for ``.``, ``,``, ``;``, ``:`` before closing guillemet (H058).

        Only applies when the line contains Russian letters. Period is flagged only
        after two or more letters so abbreviations like ``«и т. д.»`` are allowed.  # ignore: HP001
        """
        if not re.search(r"[а-яА-ЯёЁ]", line):  # noqa: RUF001  # ignore: HP001
            return
        for match in self._PUNCT_BEFORE_CLOSING_GUILLEMET_PATTERN.finditer(clean_line):
            snippet = match.group(0)
            col = line.find(snippet, match.start())
            if col < 0:
                col = match.start()
            error_msg = f'{self.RULES["H058"]}: "{snippet}"'
            yield self._format_error("H058", error_msg, filename, line_num=line_num, col=col + 1)

    def _check_question_mark_period(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for question mark followed by period '?.' (H028)."""
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code and "?." in segment:
                col = offset + segment.find("?.") + 1
                yield self._format_error("H028", self.RULES["H028"], filename, line_num=line_num, col=col)
                return
            offset += len(segment)

    def _check_quotes(self, filename: Path, line: str, clean_line: str, line_num: int) -> Generator[str, None, None]:
        """Check for incorrect quote characters (H018).

        Only applies when line contains Russian letters; otherwise straight quotes "" are allowed.
        Exception: straight double quote after a digit is allowed (inch notation, e.g. 14", 15.6").
        """
        if not re.search(r"[а-яА-ЯёЁ]", line):  # noqa: RUF001  # ignore: HP001
            return
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

    def _check_repeated_adjacent_words(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for repeated adjacent words outside code (H054).

        Only whitespace may separate the two words (so ``Notes-Notes`` is allowed).
        Hyphenated compounds count as one token.
        """
        previous: str | None = None
        previous_start = 0
        previous_end = 0
        for match in self._WORD_TOKEN_PATTERN.finditer(clean_line):
            token = match.group(0)
            current = token.casefold()
            if (
                previous is not None
                and current == previous
                and len(token) >= self._H054_MIN_WORD_LEN
                and clean_line[previous_end : match.start()].isspace()
            ):
                snippet = clean_line[previous_start : match.end()]
                col = line.find(snippet)
                if col < 0:
                    col = previous_start
                error_msg = f'{self.RULES["H054"]}: "{token}"'
                yield self._format_error("H054", error_msg, filename, line_num=line_num, col=col + 1)
            previous = current
            previous_start = match.start()
            previous_end = match.end()

    def _check_russian_polite_pronouns(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for capitalized Russian polite pronouns (H023). Use lowercase when addressing the reader.

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
                error_msg = f'{self.RULES["H023"]}: use lowercase "{word.lower()}" when addressing reader'
                yield self._format_error("H023", error_msg, filename, line_num=line_num, col=match.start() + 1)
                return

    def _check_skipped_heading_levels(
        self, filename: Path, code_block_info: list, yaml_end_line: int
    ) -> Generator[str, None, None]:
        """Check for skipped heading levels (H037)."""
        previous_level = 0
        for index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue
            match = self._ATX_HEADING_PATTERN.match(line)
            if not match:
                continue
            level = len(match.group(1))
            if previous_level and level > previous_level + 1:
                actual_line_num = (yaml_end_line - 1) + index + 1
                error_msg = f"{self.RULES['H037']}: H{previous_level} followed by H{level}"
                yield self._format_error("H037", error_msg, filename, line_num=actual_line_num, col=1)
            previous_level = level

    def _check_space_after_emphasis_colon(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for missing space after colon in or after inline emphasis (H029).

        Colon inside or after *, **, _, __, ~~ must be followed by a space before text.
        Uses original line; matches inside inline code are skipped.
        """
        code_ranges: list[tuple[int, int]] = []
        pos = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if in_code:
                code_ranges.append((pos, pos + len(segment)))
            pos += len(segment)

        def _inside_inline_code(offset: int) -> bool:
            return any(start <= offset < end for start, end in code_ranges)

        reported_cols: set[int] = set()
        for pattern in self._EMPHASIS_COLON_NO_SPACE_PATTERNS:
            for match in pattern.finditer(line):
                if _inside_inline_code(match.start()):
                    continue
                col = match.end() + 1
                if col in reported_cols:
                    continue
                reported_cols.add(col)
                yield self._format_error("H029", self.RULES["H029"], filename, line_num=line_num, col=col)

    def _check_space_before_percent_or_degree(
        self, filename: Path, line: str, clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for missing space before % or ° in Russian text (H044)."""
        for match in re.finditer(r"\d[%°]", clean_line):
            char = match.group(0)[-1]
            col = line.find(match.group(0)) + 2
            symbol = "%" if char == "%" else "°"
            error_msg = f'{self.RULES["H044"]}: missing space before "{symbol}"'
            yield self._format_error("H044", error_msg, filename, line_num=line_num, col=col)

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
            (r" \.(?![a-zA-Z0-9])", " ."),
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

    def _check_two_dots(self, filename: Path, _line: str, clean_line: str, line_num: int) -> Generator[str, None, None]:
        """Check for exactly two consecutive dots (H032).

        Does not match ``...`` (handled by H017) or ``../`` parent-directory paths.
        """
        for match in self._TWO_DOTS_PATTERN.finditer(clean_line):
            error_msg = f'{self.RULES["H032"]}: ".." should be "." or "…"'
            yield self._format_error("H032", error_msg, filename, line_num=line_num, col=match.start() + 1)

    def _check_unbalanced_details_summary(
        self, filename: Path, code_block_info: list, yaml_end_line: int
    ) -> Generator[str, None, None]:
        """Check nesting balance of ``<details>`` / ``<summary>`` (H053)."""
        details_depth = 0
        summary_depth = 0
        first_error_line: int | None = None
        tag_pattern = re.compile(
            r"</?(?:details|summary)\b[^>]*>",
            re.IGNORECASE,
        )

        for index, (line, in_code) in enumerate(code_block_info):
            if in_code:
                continue
            actual_line_num = (yaml_end_line - 1) + index + 1
            for segment, in_inline_code in h.md.identify_code_blocks_line(line):
                if in_inline_code:
                    continue
                for match in tag_pattern.finditer(segment):
                    tag = match.group(0).lower()
                    if tag.startswith("<details"):
                        details_depth += 1
                    elif tag.startswith("</details"):
                        details_depth -= 1
                        if details_depth < 0 and first_error_line is None:
                            first_error_line = actual_line_num
                            details_depth = 0
                    elif tag.startswith("<summary"):
                        summary_depth += 1
                    elif tag.startswith("</summary"):
                        summary_depth -= 1
                        if summary_depth < 0 and first_error_line is None:
                            first_error_line = actual_line_num
                            summary_depth = 0

        if first_error_line is not None or details_depth != 0 or summary_depth != 0:
            line_num = first_error_line or ((yaml_end_line - 1) + len(code_block_info))
            yield self._format_error("H053", self.RULES["H053"], filename, line_num=line_num, col=1)

    def _check_unbalanced_table_inline_code(
        self, filename: Path, line: str, line_num: int
    ) -> Generator[str, None, None]:
        r"""Check for unbalanced backticks inside Markdown table cells (H056).

        Splits on unescaped ``|`` only so escaped pipes (``\\|`` inside
        `` `a \\| b` ``) stay inside one cell and do not trigger this rule.
        """
        stripped = line.strip()
        if not stripped.startswith("|"):
            return
        cells = self._split_markdown_table_row(line)
        for cell_index, (cell, cell_start) in enumerate(cells):
            if cell_index == 0:
                continue
            if cell_index == len(cells) - 1 and not cell.strip():
                break
            # Skip alignment rows like ``| --- | :---: |``
            if re.fullmatch(r"\s*:?-{3,}:?\s*", cell):
                continue
            if cell.count("`") % 2 == 1:
                odd_pos = cell.find("`")
                while odd_pos >= 0 and cell[: odd_pos + 1].count("`") % 2 == 0:
                    odd_pos = cell.find("`", odd_pos + 1)
                col = cell_start + max(odd_pos, 0) + 1
                yield self._format_error("H056", self.RULES["H056"], filename, line_num=line_num, col=col)
                return

    def _check_unmatched_guillemets(
        self, filename: Path, line: str, _clean_line: str, line_num: int
    ) -> Generator[str, None, None]:
        """Check for unmatched guillemets on a line (H043)."""
        open_count = line.count("\u00ab")
        close_count = line.count("\u00bb")
        if open_count == close_count:
            return
        col = line.index("\u00ab") + 1 if "\u00ab" in line else line.index("\u00bb") + 1
        yield self._format_error("H043", self.RULES["H043"], filename, line_num=line_num, col=col)

    def _check_x_instead_of_times(self, filename: Path, line: str, line_num: int) -> Generator[str, None, None]:
        """Check for Latin 'x' or Cyrillic 'x' used instead of multiplication sign '&ast;' (H024).

        Only checks text outside inline code and outside link URLs.
        Exceptions: 'x86' and 'x64'; digit + 'x' + space (e.g. 2x Type-C);
        'x' + digit(s) when not after digit (e.g. PCIe x4, x16).
        """
        link_url_ranges = self._get_link_url_ranges(line)
        offset = 0
        for segment, in_code in h.md.identify_code_blocks_line(line):
            if not in_code:
                for pos, char in enumerate(segment):
                    if offset + pos in link_url_ranges:
                        continue
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
                        if after.isdigit() and not before.isdigit():
                            continue  # e.g. "PCIe 4.0 x4", "x16" — lane designation, not multiplication
                        error_msg = f'{self.RULES["H024"]}: "x" should be "×"'  # noqa: RUF001
                    else:  # Cyrillic x  # ignore: HP001
                        error_msg = f'{self.RULES["H024"]}: "х" should be "×"'  # noqa: RUF001  # ignore: HP001
                    yield self._format_error("H024", error_msg, filename, line_num=line_num, col=offset + pos + 1)
            offset += len(segment)

    # =========================================================================
    # YAML Rules (H003-H005)
    # =========================================================================

    def _check_yaml_rules(
        self,
        filename: Path,
        yaml_content: str,
        all_lines: list[str],
        rules: set,
        *,
        yaml_data: dict | None = None,
    ) -> Generator[str, None, None]:
        """Check YAML-related rules."""
        try:
            data = yaml_data
            if data is None:
                data = yaml.safe_load(yaml_content.replace("---\n", "").replace("\n---", "")) if yaml_content else None

            if not data and "H003" in rules and filename.name.upper() not in self._H003_EXEMPT_FILENAMES:
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

    def _collect_heading_ids(self, code_block_info: list) -> set[str]:
        """Collect GitHub-style heading IDs from ATX headings outside fenced code.

        IDs are stored percent-decoded so fragments like ``#️-technologies`` (raw
        U+FE0F) match slugs that ``generate_id`` emits as ``%EF%B8%8F-technologies``.
        """
        existing_ids: set[str] = set()
        heading_ids: set[str] = set()
        for line, in_code in code_block_info:
            if in_code:
                continue
            match = self._ATX_HEADING_PATTERN.match(line)
            if not match:
                continue
            level = len(match.group(1))
            title = line[level:].strip()
            title = title.replace(" <!-- top-section -->", "").replace("<!-- top-section -->", "")
            slug = h.md.generate_id(title, existing_ids)
            heading_ids.add(unquote(slug))
        return heading_ids

    def _determine_active_rules(self, select: set[str] | None, exclude_rules: set[str] | None) -> set[str]:
        """Determine which rules should be active."""
        active = select & set(self.RULES.keys()) if select is not None else self.all_rules.copy()
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

    @staticmethod
    def _extract_link_destination(raw: str) -> str:
        """Return the path/URL part of a Markdown link destination, without title.

        A title is stripped only when it uses CommonMark quoting
        (``path "title"``, ``path 'title'``, or ``path (title)``).
        """
        url = raw.strip()
        if not url:
            return ""
        if url.startswith("<"):
            end = url.find(">")
            return url[1:end].strip() if end != -1 else url[1:].strip()
        titled = re.match(r"^(.*?)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))\s*$", url)
        if titled:
            return titled.group(1).strip()
        return url

    def _find_yaml_block_end_line(self, all_lines: list[str]) -> int:
        """Find the line number where YAML block ends."""
        yaml_part, _ = h.md.split_yaml_content("\n".join(all_lines))
        if not yaml_part:
            return 1
        return len(yaml_part.splitlines())

    def _find_yaml_end_line(self, lines: list[str]) -> int:
        """Find the first content line number after the YAML block (1-based)."""
        yaml_part, _ = h.md.split_yaml_content("\n".join(lines))
        if not yaml_part:
            return 1
        return len(yaml_part.splitlines()) + 1

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

    def _get_link_url_ranges(self, line: str) -> set[int]:
        """Return set of 0-based character positions that are inside Markdown link URLs (](url))."""
        positions: set[int] = set()
        for m in re.finditer(r"\]\([^)]*\)", line):
            for i in range(m.start() + 2, m.end() - 1):
                positions.add(i)
        return positions

    def _get_relative_path(self, filename: Path) -> str:
        """Get relative path from project root."""
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            return str(filename.resolve())

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _image_alt_text_issue(self, alt: str) -> str | None:
        """Return H031 issue description for invalid alt text, or None if alt text is acceptable."""
        stripped = alt.strip()
        if not stripped:
            return "empty alt text"
        if stripped.casefold() == "alt text":
            return f'placeholder alt text "{stripped}"'
        if stripped[0].isalpha() and stripped[0].islower():
            return f'alt text starts with "{stripped[0]}"'
        return None

    @staticmethod
    def _is_blockquote_attribution_line(line: str) -> bool:
        """Return True if line is a blockquote attribution (e.g. '> -- Author')."""
        stripped = line.lstrip()
        if not stripped.startswith(">"):
            return False
        content = stripped
        while content.lstrip().startswith(">"):
            content = content.lstrip()[1:].lstrip()
        return content.startswith("--")

    @staticmethod
    def _is_escaped_table_pipe(line: str, index: int) -> bool:
        """Return True if ``line[index]`` is a pipe escaped by an odd run of backslashes."""
        n = 0
        j = index - 1
        while j >= 0 and line[j] == "\\":
            n += 1
            j -= 1
        return n % 2 == 1

    def _is_h021_allowed_period(self, segment: str, period_pos: int, match_end: int) -> bool:
        """Return True if punctuation at ``period_pos`` is not a sentence-ending period for H021."""
        if period_pos > 0 and segment[period_pos - 1].isdigit():
            return True
        if self._is_h021_ru_dotted_abbrev_period(segment, period_pos):
            return True
        tail = segment[max(0, period_pos - self._H021_ALLOWED_TAIL_LEN) : period_pos + 1].lower()
        if any(tail.endswith(abbrev) for abbrev in self._H021_PERIOD_ABBREVS):
            return True
        context = segment[max(0, period_pos - 6) : match_end].lower()
        return any(abbrev in context for abbrev in self._H021_PERIOD_ABBREVS)

    @staticmethod
    def _is_h021_ru_dotted_abbrev_period(segment: str, period_pos: int) -> bool:
        """Return True if period opens a Russian dotted abbrev like ``т. д.`` or ``т. е.``."""  # noqa: RUF002  # ignore: HP001
        return (
            period_pos > 0
            and segment[period_pos - 1].lower() == "т"  # ignore: HP001
            and period_pos + 2 < len(segment)
            and segment[period_pos + 1] == " "
            and segment[period_pos + 2].lower() in MarkdownChecker._H021_RU_DOTTED_ABBREV_SECONDS
        )

    def _is_horizontal_rule(self, line: str) -> bool:
        """Return True if the line is a Markdown horizontal rule (``---``, ``***``, ``___``)."""
        return bool(self._HORIZONTAL_RULE_PATTERN.match(line.strip()))

    @staticmethod
    def _is_hyphenated_identifier_fragment(text: str, start: int, end: int) -> bool:
        """Return True if span is part of a hyphenated identifier (e.g. ``markdown-it``, ``git-diff-friendly``)."""
        if start > 0 and text[start - 1] == "-":
            return True
        return end < len(text) and text[end] == "-"

    @staticmethod
    def _is_identifier_like_link_label(label: str) -> bool:
        """Return True if link label looks like a package/URL identifier, not prose."""
        stripped = label.strip()
        if not stripped or " " in stripped:
            return False
        return any(c in stripped for c in "-._")

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

    def _paragraph_last_char(self, line: str) -> tuple[str, int]:
        """Return last meaningful character and its 1-based column for colon checks.

        Trailing Markdown emphasis markers (``*``, ``_``) are ignored so lines like
        ``**Title:**`` are treated as ending with ``:``.
        """
        stripped = line.rstrip()
        end = len(stripped)
        while end > 0 and stripped[end - 1] in "*_":
            end -= 1
        if end == 0:
            return "", 0
        return stripped[end - 1], end

    def _remove_inline_code(self, line: str) -> str:
        """Remove inline code segments from line, keeping only non-code text."""
        return "".join(segment for segment, in_code in h.md.identify_code_blocks_line(line) if not in_code)

    def _should_check_paragraph_end(self, line: str) -> bool:
        """Return True if line is a regular paragraph that should end with colon before code/image."""
        stripped = line.strip()
        return (
            bool(stripped)
            and stripped != "```"
            and not stripped.startswith(("![", "#"))
            and not self._is_horizontal_rule(stripped)
        )

    @classmethod
    def _split_markdown_table_row(cls, line: str) -> list[tuple[str, int]]:
        """Split a table row on unescaped ``|``; return ``(cell, start_index)`` pairs."""
        cells: list[tuple[str, int]] = []
        start = 0
        for i, ch in enumerate(line):
            if ch == "|" and not cls._is_escaped_table_pipe(line, i):
                cells.append((line[start:i], start))
                start = i + 1
        cells.append((line[start:], start))
        return cells
````

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
