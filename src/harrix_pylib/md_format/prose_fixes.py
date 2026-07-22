"""Apply unambiguous MdChecker autofixes to Markdown prose.

Runs before the Prettier-style parse/render pipeline so source-preserving paths
keep fixed prose. Skips fenced and inline code the same way as MdChecker
(H006, H007, H015-H017, H020-H024, H026-H030, H036, H039, H042, H044, H050,
H057, H058).

Bare filenames and paths (for example `config.json`, `src/app/recover.sql`) are
wrapped in inline code before H006 so file extensions are not uppercased.
Product names that look like files (for example Node.js) are left as prose.
A leading-dot mention like `.g.md` becomes `` `g.md` `` (not `` .`g.md` ``).

"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING

from harrix_pylib.abbreviation_data import mask_abbreviations
from harrix_pylib.md_format.code_fence import _identify_code_blocks, _identify_code_blocks_line

if TYPE_CHECKING:
    from collections.abc import Callable

_INCORRECT_LANGUAGES = {
    "console": "shell",
    "py": "python",
}

_INVISIBLE_CHARACTERS = (
    "\u200b",  # zero-width space
    "\u00ad",  # soft hyphen
    "\u202f",  # narrow no-break space
    "\u2060",  # word joiner
)

_RUSSIAN_POLITE_PRONOUNS_CAPITALIZED = (
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

_ATX_HEADING_NO_SPACE_PATTERN = re.compile(r"^(\s{0,3}#{1,6})([^\s#].*)$")
_ATX_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
_ATX_CLOSING_HASHES_PATTERN = re.compile(r"\s+#+\s*$")
_BACKSLASH_PATH_PATTERN = re.compile(r"\]\(([^)]*\\[^)]*)\)")
_MISSING_SPACE_AFTER_PUNCT_PATTERN = re.compile(r"([,;!?])(?=[^\W\d_])", re.UNICODE)
_PUNCT_BEFORE_CLOSING_GUILLEMET_PATTERN = re.compile(
    r"((?:[^\W\d_]{2,}\.|[,;:]))»",
    re.UNICODE,
)
_H021_PATTERN = re.compile(r"([.!?])(\s+)([a-zа-яё])")  # noqa: RUF001  # ignore: HP001
_CYRILLIC_PATTERN = re.compile(r"[а-яА-ЯёЁ]")  # noqa: RUF001  # ignore: HP001
_FENCE_OPEN_PATTERN = re.compile(r"^(\s*)(`{3,})(\s*)(\w+)(.*)$")
_IMAGE_ALT_PATTERN = re.compile(r"!\[([^\]]*)\]")
_NUMERO_PATTERN = re.compile(r"\u2116(?=[^ ])")
_PERCENT_DEGREE_PATTERN = re.compile(r"(\d)([%°])")
_EMPHASIS_COLON_NO_SPACE_PATTERNS = (
    re.compile(r"(\*\*\*[^*\n]+:\*\*\*)(?=\S)"),
    re.compile(r"(\*\*\*[^*\n]+\*\*\*:)(?=\S)"),
    re.compile(r"(\*\*[^*\n]+:\*\*)(?=\S)"),
    re.compile(r"(\*\*[^*\n]+\*\*:)(?=\S)"),
    re.compile(r"((?<!\*)\*(?!\*)[^*\n]+:\*(?!\*))(?=\S)"),
    re.compile(r"((?<!\*)\*(?!\*)[^*\n]+\*(?!\*):)(?=\S)"),
    re.compile(r"(__[^_\n]+:__)(?=\S)"),
    re.compile(r"(__[^_\n]+__:)(?=\S)"),
    re.compile(r"((?<!_)_(?!_)[^_\n]+:_(?!_))(?=\S)"),
    re.compile(r"((?<!_)_(?!_)[^_\n]+_(?!_):)(?=\S)"),
    re.compile(r"(~~[^~\n]+:~~)(?=\S)"),
    re.compile(r"(~~[^~\n]+~~:)(?=\S)"),
)
_EMPHASIS_COLON_OUTSIDE_PATTERNS = (
    re.compile(r"(\*\*\*)([^*\n]+)(\*\*\*):"),
    re.compile(r"(\*\*)([^*\n]+)(\*\*):"),
    re.compile(r"(?<!\*)(\*)(?!\*)([^*\n]+)(\*)(?!\*):"),
    re.compile(r"(__)([^_\n]+)(__):"),
    re.compile(r"(?<!_)(_)(?!_)([^_\n]+)(_):"),
    re.compile(r"(~~)([^~\n]+)(~~):"),
)
_H015_BANG_EXCEPTIONS = (" !details", " !note", " !important", " !warning")
_SPACE_BEFORE_PUNCT_PATTERNS = (
    (re.compile(r" \.(?![a-zA-Z0-9])"), "."),
    (re.compile(r" ,"), ","),
    (re.compile(r" ;"), ";"),
    (re.compile(r" :"), ":"),
    (re.compile(r" \?"), "?"),
)
_PRONOUN_BOUNDARY_BEFORE = r"(?<![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001  # ignore: HP001
_PRONOUN_BOUNDARY_AFTER = r"(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001  # ignore: HP001

# File extensions wrapped as inline code before H006 so `recover.sql` stays lowercase.
_FILE_PATH_EXTENSIONS = frozenset(
    {
        "apk",
        "bat",
        "cfg",
        "cpp",
        "css",
        "csv",
        "dll",
        "exe",
        "go",
        "h",
        "hpp",
        "html",
        "ini",
        "java",
        "js",
        "json",
        "jsx",
        "kt",
        "lock",
        "log",
        "md",
        "odf",
        "odt",
        "pdf",
        "php",
        "ps1",
        "py",
        "qml",
        "rs",
        "sh",
        "sql",
        "svg",
        "swift",
        "toml",
        "ts",
        "tsv",
        "tsx",
        "txt",
        "xml",
        "yaml",
        "yml",
    }
)
_FILE_PATH_EXT_ALT = "|".join(sorted(_FILE_PATH_EXTENSIONS, key=lambda item: (-len(item), item)))
# Product names that look like `name.ext` but are not files (skip backtick wrap).
_BARE_FILENAME_PRODUCT_BASENAMES = frozenset({"node.js"})
# Group 1: leading-dot mention `.g.md` (capture without the leading `.`).
# Group 2: normal basename/path `config.json`, `../recover.sql`, `src/a.py`.
_BARE_FILENAME_PATTERN = re.compile(
    rf"(?:(?<!\S)\.((?:[\w.-]+[/\\])*[\w][\w.-]*\.(?:{_FILE_PATH_EXT_ALT}))"
    rf"|(?<![A-Za-z0-9_`.])(?:[A-Za-z]:[/\\])?(?:(?:[\w.-]+|\.\.)[/\\])*[\w][\w.-]*\.(?:{_FILE_PATH_EXT_ALT}))"
    rf"(?!\.[A-Za-z0-9_])(?![A-Za-z0-9_])",
    re.IGNORECASE,
)


def _apply_checker_prose_fixes(text: str, *, lang: str = "") -> str:
    """Apply mechanical MdChecker autofixes to Markdown body text.

    Args:

    - `text` (`str`): Markdown body (typically without YAML front matter).
    - `lang` (`str`): Document language from YAML (`en` / `ru`); gates H023/H044.

    """
    if not text:
        return text

    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines and lines[-1] == "":
        lines.pop()

    fence_info = list(_identify_code_blocks(lines))
    result: list[str] = []

    for line, in_fence in fence_info:
        if in_fence:
            result.append(_fix_fence_or_code_line(line))
        else:
            result.append(_fix_prose_line(line, lang=lang))

    output = "\n".join(result)
    if has_trailing_newline:
        output += "\n"
    return output


def _extract_url_regions(line: str) -> tuple[str, list[str]]:
    """Replace link destinations and angle autolinks with placeholders."""
    stored: list[str] = []

    def keep(text: str) -> str:
        stored.append(text)
        return f"{_URL_PLACEHOLDER_PREFIX}{len(stored) - 1}"

    def repl_dest(match: re.Match[str]) -> str:
        return f"]({keep(match.group(1))})"

    def repl_angle(match: re.Match[str]) -> str:
        return keep(match.group(0))

    masked = _LINK_DESTINATION_RE.sub(repl_dest, line)
    masked = _ANGLE_AUTOLINK_RE.sub(repl_angle, masked)
    return masked, stored


def _fix_atx_heading_space(line: str) -> str:
    """Insert space after ATX hashes when missing (H036)."""
    match = _ATX_HEADING_NO_SPACE_PATTERN.match(line)
    if not match:
        return line
    return f"{match.group(1)} {match.group(2)}"


def _fix_backslash_paths(segment: str) -> str:
    """Normalize backslashes in local Markdown destinations (H039)."""
    return _BACKSLASH_PATH_PATTERN.sub(lambda match: f"]({match.group(1).replace(chr(92), '/')})", segment)


def _fix_bare_filenames_and_cheap_typography(segment: str) -> str:
    """Wrap bare filenames, then apply cheap H017/H026/H028/H027 typography fixes."""
    if "." in segment or "/" in segment or "\\" in segment:
        segment = _fix_bare_filenames_to_inline_code(segment)
    if "..." in segment:
        segment = _fix_ellipsis(segment)  # H017
    if "\u2015" in segment:
        segment = _fix_horizontal_bar(segment)  # H026
    if "?." in segment:
        segment = _fix_question_mark_period(segment)  # H028
    if "\u2116" in segment:
        segment = _fix_numero_space(segment)  # H027
    return segment


def _fix_bare_filenames_to_inline_code(segment: str) -> str:
    """Wrap bare filenames and paths in backticks before H006 uppercase fixes.

    Leading-dot mentions like `.g.md` become `` `g.md` `` so H015 cannot glue the
    leftover period onto the previous word (`combined .` → `combined.`).

    Product names such as `Node.js` are left unwrapped (not a file). Paths like
    `src/node.js` are still wrapped.

    """

    def replacer(match: re.Match[str]) -> str:
        leading_dot_name = match.group(1)
        if leading_dot_name is not None:
            return f"`{leading_dot_name}`"
        matched = match.group(0)
        if "/" not in matched and "\\" not in matched and matched.casefold() in _BARE_FILENAME_PRODUCT_BASENAMES:
            return matched
        return f"`{matched}`"

    return _BARE_FILENAME_PATTERN.sub(replacer, segment)


def _fix_dash_usage(line: str) -> str:
    """Normalize hyphen / en dash / em dash usage (H016)."""
    if not any(marker in line for marker in (" - ", " -- ", "–", "—", " \u2212 ")):  # noqa: RUF001
        return line

    list_hyphen_positions = {match.end() - 1 for match in _LIST_MARKER_HYPHEN_PATTERN.finditer(line)}
    keep_double_dash = _is_blockquote_attribution_line(line)

    parts = []
    offset = 0
    for segment, in_code in _line_code_segments(line):
        if in_code:
            parts.append(segment)
        else:
            fixed = segment
            search_from = 0
            while True:
                pos = fixed.find(" - ", search_from)
                if pos < 0:
                    break
                absolute = offset + pos
                hyphen_at = absolute + 1
                if (
                    hyphen_at in list_hyphen_positions
                    or fixed.strip().startswith("-")
                    or ("|" in line and _is_table_cell_only_dash(line, absolute))
                ):
                    search_from = pos + 3
                    continue
                fixed = f"{fixed[:pos]} — {fixed[pos + 3 :]}"
                search_from = pos + 3
            fixed = fixed.replace(" \u2212 ", " — ")
            if not keep_double_dash:
                fixed = fixed.replace(" -- ", " — ")
            fixed = _normalize_en_and_em_dashes(fixed)
            parts.append(fixed)
        offset += len(segment)
    return "".join(parts)


def _fix_ellipsis(segment: str) -> str:
    """Replace `...` with ellipsis (H017)."""
    return segment.replace("...", "…")


def _fix_emphasis_colon_outside(line: str) -> str:
    """Move colon inside emphasis markers when line continues (H030)."""
    if ":" not in line or not any(marker in line for marker in ("*", "_", "~")):
        return line

    code_ranges = _inline_code_ranges(line)

    def replacer(match: re.Match[str]) -> str:
        if _inside_ranges(match.start(), code_ranges):
            return match.group(0)
        if not line[match.end() :].strip():
            return match.group(0)
        open_m, inner, close_m = match.group(1), match.group(2), match.group(3)
        return f"{open_m}{inner}:{close_m}"

    for pattern in _EMPHASIS_COLON_OUTSIDE_PATTERNS:
        new_line = pattern.sub(replacer, line)
        if new_line != line:
            line = new_line
            code_ranges = _inline_code_ranges(line)
    return line


def _fix_emphasis_colon_space(line: str) -> str:
    """Insert space after emphasis colon when missing (H029)."""
    if ":" not in line or not any(marker in line for marker in ("*", "_", "~")):
        return line

    code_ranges = _inline_code_ranges(line)

    def replacer(match: re.Match[str]) -> str:
        if _inside_ranges(match.start(), code_ranges):
            return match.group(0)
        return f"{match.group(1)} "

    for pattern in _EMPHASIS_COLON_NO_SPACE_PATTERNS:
        new_line = pattern.sub(replacer, line)
        if new_line != line:
            line = new_line
            code_ranges = _inline_code_ranges(line)
    return line


def _fix_fence_or_code_line(line: str) -> str:
    """Fix fence language ids (H007) and NBSP (H022) inside fenced regions."""
    line = line.replace("\u00a0", " ")
    match = _FENCE_OPEN_PATTERN.match(line)
    if not match:
        return line
    language = match.group(4)
    correct = _INCORRECT_LANGUAGES.get(language)
    if correct is None:
        return line
    return f"{match.group(1)}{match.group(2)}{match.group(3)}{correct}{match.group(5)}"


def _fix_heading_trailing_period(line: str) -> str:
    """Remove trailing period from ATX headings (H057)."""
    match = _ATX_HEADING_PATTERN.match(line)
    if not match:
        return line
    hashes, title = match.group(1), match.group(2)
    working = title
    closing = ""
    closing_match = _ATX_CLOSING_HASHES_PATTERN.search(working)
    if closing_match:
        closing = closing_match.group(0)
        working = working[: closing_match.start()]
    top_section = ""
    for marker in (" <!-- top-section -->", "<!-- top-section -->"):
        if marker in working:
            working = working.replace(marker, "", 1)
            top_section = marker if marker.startswith(" ") else f" {marker}"
            break
    stripped = working.rstrip()
    if not stripped or stripped.endswith(("...", "…")) or not stripped.endswith("."):
        return line
    fixed_title = stripped[:-1].rstrip()
    trailing_ws = working[len(stripped) :]
    return f"{hashes} {fixed_title}{trailing_ws}{top_section}{closing}"


def _fix_horizontal_bar(segment: str) -> str:
    """Replace horizontal bar with em dash (H026)."""
    return segment.replace("\u2015", "—")


def _fix_image_alt_capitalization(line: str) -> str:
    """Capitalize lowercase-starting image alt text (H020)."""
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]
    if not stripped.startswith("!["):
        return line
    match = _IMAGE_ALT_PATTERN.match(stripped)
    if not match:
        return line
    caption = match.group(1)
    if not caption or not caption[0].isalpha() or not caption[0].islower():
        return line
    fixed = f"{caption[0].upper()}{caption[1:]}"
    return f"{indent}![{fixed}]{stripped[match.end() :]}"


def _fix_incorrect_words(segment: str) -> str:
    r"""Replace incorrect word forms (H006), skipping URLs and HTML.

    Pure word tokens use a dict lookup after one `\w+` scan. Phrases and
    punctuated forms (abbreviations with dots, `e-mail`, `c++`, …) use a
    smaller longest-first combined regex, and only when the segment contains
    characters that those patterns need.

    """
    word_map, phrase_pattern, phrase_replacements = _h006_lookup_tables()
    if not word_map and not phrase_replacements:
        return segment

    masked = _mask_urls_and_html(segment) if "](" in segment or "<" in segment else segment
    working = segment

    # Phrase / punctuated forms first (longest-first), when relevant.
    if phrase_replacements and _needs_h006_phrase_scan(masked):
        matches = [
            match
            for match in phrase_pattern.finditer(masked)
            if not _is_hyphenated_identifier_fragment(masked, *match.span())
            and not _is_file_extension_fragment(masked, *match.span())
        ]
        for match in reversed(matches):
            start, end = match.span()
            incorrect = match.group(0)
            if working[start:end] != incorrect:
                continue
            correct = phrase_replacements.get(incorrect)
            if correct is None:
                continue
            working = f"{working[:start]}{correct}{working[end:]}"
        if working != segment:
            masked = _mask_urls_and_html(working) if "](" in working or "<" in working else working

    if not word_map:
        return working

    word_matches = [
        match
        for match in _H006_WORD_TOKEN_PATTERN.finditer(masked)
        if match.group(0) in word_map
        and not _is_hyphenated_identifier_fragment(masked, *match.span())
        and not _is_file_extension_fragment(masked, *match.span())
    ]
    for match in reversed(word_matches):
        start, end = match.span()
        incorrect = match.group(0)
        if working[start:end] != incorrect:
            continue
        working = f"{working[:start]}{word_map[incorrect]}{working[end:]}"
    return working


def _fix_lowercase_after_punctuation(line: str) -> str:
    """Capitalize lowercase letters after sentence-ending punctuation (H021)."""
    if not any(char in line for char in ".!?"):
        return line

    mask_pattern = _h021_abbrev_mask_pattern()
    parts: list[str] = []
    for segment, in_code in _line_code_segments(line):
        if in_code:
            parts.append(segment)
            continue
        # Abbreviation masking is only needed when the segment has periods.
        masked = mask_abbreviations(segment, mask_pattern) if "." in segment else segment
        chars = list(segment)
        for match in _H021_PATTERN.finditer(masked):
            if _is_h021_allowed_period(masked, match.start()):
                continue
            letter_index = match.start(3)
            chars[letter_index] = chars[letter_index].upper()
        parts.append("".join(chars))
    return "".join(parts)


def _fix_missing_space_after_punctuation(segment: str) -> str:
    """Insert missing space after `,;!?` before a letter (H050)."""

    def replacer(match: re.Match[str]) -> str:
        punct = match.group(1)
        next_char = segment[match.end()]
        if punct == "!" and match.start() > 0 and segment[match.start() - 1] == "[":
            return match.group(0)
        if (
            punct in ",;"
            and match.start() > 0
            and segment[match.start() - 1].isascii()
            and segment[match.start() - 1].isalnum()
            and next_char.isascii()
            and next_char.isalpha()
        ):
            return match.group(0)
        return f"{punct} "

    return _MISSING_SPACE_AFTER_PUNCT_PATTERN.sub(replacer, segment)


def _fix_multiplication_sign(line: str) -> str:
    """Replace Latin/Cyrillic `x` used as multiply with the multiplication sign (H024)."""
    if "x" not in line and "\u0445" not in line:  # ignore: HP001
        return line

    link_url_ranges = _get_link_url_ranges(line)
    parts: list[str] = []
    offset = 0
    for segment, in_code in _line_code_segments(line):
        if in_code:
            parts.append(segment)
            offset += len(segment)
            continue
        chars = list(segment)
        pos = 0
        while pos < len(chars):
            char = chars[pos]
            absolute = offset + pos
            if absolute in link_url_ranges or char not in ("x", "\u0445"):  # ignore: HP001
                pos += 1
                continue
            if pos <= 0 or pos >= len(chars) - 1:
                pos += 1
                continue
            before = chars[pos - 1]
            after = chars[pos + 1]
            if before not in " \t" and not before.isdigit():
                pos += 1
                continue
            if after not in " \t" and not after.isdigit():
                pos += 1
                continue
            if char == "x":
                if before == " " and "".join(chars[pos : pos + 3]) in ("x86", "x64"):
                    pos += 1
                    continue
                if before.isdigit() and after in " \t":
                    pos += 1
                    continue
                if after.isdigit() and not before.isdigit():
                    pos += 1
                    continue
            chars[pos] = "×"  # noqa: RUF001
            pos += 1
        parts.append("".join(chars))
        offset += len(segment)
    return "".join(parts)


def _fix_numero_space(segment: str) -> str:
    """Insert space after № when missing (H027)."""
    return _NUMERO_PATTERN.sub("№ ", segment)


def _fix_prose_line(line: str, *, lang: str) -> str:
    """Apply all prose autofixes to one non-fenced Markdown line."""
    line = line.replace("\u00a0", " ")  # H022
    for char in _INVISIBLE_CHARACTERS:
        line = line.replace(char, "")  # H042

    line = _fix_atx_heading_space(line)  # H036
    line = _fix_heading_trailing_period(line)  # H057
    line = _fix_image_alt_capitalization(line)  # H020

    # Protect link/image destinations and angle autolinks from typography fixes
    # (H050 would turn `?logo=` into `? logo=` and break shields.io badges).
    line, url_parts = _extract_url_regions(line)

    # Wrap bare filenames/paths before H006 so extensions are not uppercased.
    # Cheap typography fixes share one non-code pass to avoid repeated segmentation.
    line = _map_non_code(line, _fix_bare_filenames_and_cheap_typography)
    line = _map_non_code(line, _fix_incorrect_words)  # H006
    line = _fix_space_before_punctuation(line)  # H015
    line = _fix_dash_usage(line)  # H016
    line = _fix_multiplication_sign(line)  # H024
    line = _fix_emphasis_colon_outside(line)  # H030 (before H029)
    line = _fix_emphasis_colon_space(line)  # H029
    line = _fix_lowercase_after_punctuation(line)  # H021
    line = _map_non_code(line, _fix_missing_space_after_punctuation)  # H050
    if lang == "ru":
        line = _map_non_code(line, _fix_space_before_percent_or_degree)  # H044
        line = _fix_russian_polite_pronouns(line)  # H023
    if _CYRILLIC_PATTERN.search(line):
        line = _map_non_code(line, _fix_punctuation_before_closing_guillemet)  # H058

    line = _restore_url_regions(line, url_parts)
    return _map_non_code(line, _fix_backslash_paths)  # H039 (paths only)


def _fix_punctuation_before_closing_guillemet(segment: str) -> str:
    """Move `. , ; :` after closing guillemet (H058)."""

    def replacer(match: re.Match[str]) -> str:
        punct_run = match.group(1)
        # `слово.»` → `слово».` ; `,»` → `»,` # ignore: HP001
        if punct_run.endswith(".") and len(punct_run) > 1:
            return f"{punct_run[:-1]}»."
        return f"»{punct_run}"

    return _PUNCT_BEFORE_CLOSING_GUILLEMET_PATTERN.sub(replacer, segment)


def _fix_question_mark_period(segment: str) -> str:
    """Replace `?.` with `?` (H028)."""
    return segment.replace("?.", "?")


def _fix_russian_polite_pronouns(line: str) -> str:
    """Lowercase Russian polite pronouns when not at sentence start (H023)."""

    def at_sentence_start(match_start: int) -> bool:
        text_before = line[:match_start]
        stripped = text_before.strip()
        if not stripped:
            return True
        if re.search(r"[.!?]\s*$", text_before):
            return True
        if stripped.endswith("\u00ab"):
            return True
        return bool(re.match(r"^\s*[—\-]\s*$", text_before))

    for word in _RUSSIAN_POLITE_PRONOUNS_CAPITALIZED:
        pattern = re.compile(_PRONOUN_BOUNDARY_BEFORE + re.escape(word) + _PRONOUN_BOUNDARY_AFTER)
        code_ranges = _inline_code_ranges(line)

        def replacer(
            match: re.Match[str],
            *,
            lower: str = word.lower(),
            ranges: list[tuple[int, int]] = code_ranges,
        ) -> str:
            if _inside_ranges(match.start(), ranges) or at_sentence_start(match.start()):
                return match.group(0)
            return lower

        line = pattern.sub(replacer, line)
    return line


def _fix_space_before_percent_or_degree(segment: str) -> str:
    """Insert space before `%` / `°` after a digit (H044)."""
    return _PERCENT_DEGREE_PATTERN.sub(r"\1 \2", segment)


def _fix_space_before_punctuation(line: str) -> str:
    """Remove spaces before punctuation marks (H015)."""
    if not any(marker in line for marker in (" .", " ,", " ;", " :", " ?", " !")):
        return line

    code_ranges = _inline_code_ranges(line)

    def replace_outside_code(pattern: re.Pattern[str], replacement: str, text: str) -> str:
        pieces: list[str] = []
        last = 0
        for match in pattern.finditer(text):
            if _inside_ranges(match.start(), code_ranges):
                continue
            pieces.append(text[last : match.start()])
            pieces.append(replacement)
            last = match.end()
        pieces.append(text[last:])
        return "".join(pieces)

    for pattern, replacement in _SPACE_BEFORE_PUNCT_PATTERNS:
        line = replace_outside_code(pattern, replacement, line)

    if " !" in line:
        pos_found = 0
        while True:
            pos_found = line.find(" !", pos_found)
            if pos_found < 0:
                break
            if (
                not _inside_ranges(pos_found, code_ranges)
                and not any(line[pos_found:].startswith(exc) for exc in _H015_BANG_EXCEPTIONS)
                and not line.strip().startswith("!")
            ):
                line = f"{line[:pos_found]}!{line[pos_found + 2 :]}"
                code_ranges = _inline_code_ranges(line)
                continue
            pos_found += 2
    return line


def _get_link_url_ranges(line: str) -> set[int]:
    """Return 0-based positions inside Markdown link/image destinations."""
    positions: set[int] = set()
    for match in re.finditer(r"\]\([^)]*\)", line):
        positions.update(range(match.start() + 2, match.end() - 1))
    return positions


@lru_cache(maxsize=1)
def _h006_lookup_tables() -> tuple[dict[str, str], re.Pattern[str], dict[str, str]]:
    r"""Build H006 word map and phrase regex (shared with MdChecker dictionary).

    Pure `\w+` tokens use a dict lookup. Phrases / punctuated forms keep a
    longest-first combined regex with Unicode lookaround boundaries.

    """
    patterns = _incorrect_word_patterns()
    if not patterns:
        return {}, re.compile(r"(?!)"), {}

    word_map: dict[str, str] = {}
    phrase_items: list[tuple[str, str]] = []
    for incorrect, (_pattern, correct) in patterns.items():
        if re.fullmatch(r"[\w]+", incorrect):
            word_map[incorrect] = correct
        else:
            phrase_items.append((incorrect, correct))

    phrase_items.sort(key=lambda item: len(item[0]), reverse=True)
    phrase_replacements = dict(phrase_items)
    if phrase_items:
        alternatives = [
            rf"(?<![a-zA-Zа-яА-ЯёЁ0-9_]){re.escape(incorrect)}(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001  # ignore: HP001
            for incorrect, _correct in phrase_items
        ]
        phrase_pattern = re.compile("|".join(f"(?:{alt})" for alt in alternatives))
    else:
        phrase_pattern = re.compile(r"(?!)")
    return word_map, phrase_pattern, phrase_replacements


@lru_cache(maxsize=1)
def _h021_abbrev_mask_pattern() -> re.Pattern[str] | None:
    """Load H021 abbreviation mask from MdChecker."""
    from harrix_pylib.md_checker import MdChecker  # noqa: PLC0415

    return MdChecker._H021_ABBREV_MASK_PATTERN  # noqa: SLF001


@lru_cache(maxsize=1)
def _incorrect_word_patterns() -> dict[str, tuple[re.Pattern[str], str]]:
    """Load H006 patterns from MdChecker (shared source of truth)."""
    from harrix_pylib.md_checker import MdChecker  # noqa: PLC0415

    return MdChecker._INCORRECT_WORD_PATTERNS  # noqa: SLF001


def _inline_code_ranges(line: str) -> list[tuple[int, int]]:
    """Return 0-based ranges of inline code spans on a line."""
    ranges: list[tuple[int, int]] = []
    pos = 0
    for segment, in_code in _line_code_segments(line):
        if in_code:
            ranges.append((pos, pos + len(segment)))
        pos += len(segment)
    return ranges


def _inside_ranges(offset: int, ranges: list[tuple[int, int]]) -> bool:
    """Return whether `offset` lies inside any half-open range."""
    return any(start <= offset < end for start, end in ranges)


def _is_blockquote_attribution_line(line: str) -> bool:
    """Return `True` if line is a blockquote attribution (e.g. `> -- Author`)."""
    stripped = line.lstrip()
    if not stripped.startswith(">"):
        return False
    content = stripped
    while content.lstrip().startswith(">"):
        content = content.lstrip()[1:].lstrip()
    return content.startswith("--")


def _is_file_extension_fragment(text: str, start: int, _end: int) -> bool:
    """Return `True` if span is a file extension after a dotted filename stem."""
    dot_index = start - 1
    stem_index = start - 2
    if stem_index < 0 or text[dot_index] != ".":
        return False
    prev = text[stem_index]
    return prev.isalnum() or prev == "_"


def _is_h021_allowed_period(segment: str, period_pos: int) -> bool:
    """Return `True` if punctuation is an ordered-list / section number period."""
    return period_pos > 0 and segment[period_pos - 1].isdigit()


def _is_hyphenated_identifier_fragment(text: str, start: int, end: int) -> bool:
    """Return `True` if span is part of a hyphenated identifier."""
    if start > 0 and text[start - 1] == "-":
        return True
    return end < len(text) and text[end] == "-"


def _is_table_cell_only_dash(line: str, pos: int) -> bool:
    """Return `True` if `pos` is inside a table cell that contains only `-`."""
    parts = line.split("|")
    if len(parts) < 2:
        return False
    start = 0
    for part in parts:
        end = start + len(part)
        if start <= pos < end:
            return part.strip() == "-"
        start = end + 1
    return False


@lru_cache(maxsize=16)
def _line_code_segments(line: str) -> tuple[tuple[str, bool], ...]:
    """Cache inline-code segmentation for a line (reused across prose fixes)."""
    return tuple(_identify_code_blocks_line(line))


def _map_non_code(line: str, transform: Callable[[str], str]) -> str:
    """Apply `transform` to non-inline-code segments only."""
    return "".join(segment if in_code else transform(segment) for segment, in_code in _line_code_segments(line))


def _mask_urls_and_html(text: str) -> str:
    """Mask link destinations and HTML tags with same-length spaces (H006 scope)."""

    def mask_dest(match: re.Match[str]) -> str:
        return "](" + (" " * (len(match.group(0)) - 3)) + ")"

    def mask_html(match: re.Match[str]) -> str:
        return "<" + (" " * (len(match.group(0)) - 2)) + ">"

    masked = _LINK_DEST_MASK_RE.sub(mask_dest, text)
    return _HTML_TAG_MASK_RE.sub(mask_html, masked)


def _needs_h006_phrase_scan(text: str) -> bool:
    """Return whether a segment may contain punctuated / multi-word H006 keys."""
    # Space-separated keys without dots/hyphens: "web документ", "web приложение".
    if "web " in text.casefold():
        return True
    if not any(char in text for char in _H006_PHRASE_TRIGGER_CHARS):
        return False
    # Most phrase keys are Russian dotted abbreviations; skip that large regex for
    # ASCII-only segments that only contain dots from paths / versions / code.
    if _CYRILLIC_PATTERN.search(text):
        return True
    lowered = text.casefold()
    return (
        any(char in text for char in "-+#")
        or "node." in lowered
        or "e-mail" in lowered
        or "p.s." in lowered
        or "op.cit" in lowered
        or "loc.cit" in lowered
    )


def _normalize_en_and_em_dashes(segment: str) -> str:
    """Fix en dashes outside digit ranges and em-dash spacing."""
    chars = list(segment)
    i = 0
    while i < len(chars):
        char = chars[i]
        if char == "–":  # noqa: RUF001
            before = chars[i - 1] if i > 0 else ""
            after = chars[i + 1] if i + 1 < len(chars) else ""
            if not (before.isdigit() and after.isdigit()):
                # Non-digit en dash becomes spaced em dash.
                left = "" if before == " " else " "
                right = "" if after == " " else " "
                replacement = f"{left}—{right}"
                chars[i : i + 1] = list(replacement)
                i += len(replacement)
                continue
        elif char == "—":
            before = chars[i - 1] if i > 0 else " "
            after = chars[i + 1] if i + 1 < len(chars) else " "
            if i == 0:
                if after != " ":
                    chars[i : i + 1] = list("— ")
                    i += 2
                    continue
            elif not (before == " " and after == " "):
                left = "" if before == " " else " "
                right = "" if after == " " else " "
                replacement = f"{left}—{right}"
                chars[i : i + 1] = list(replacement)
                i += len(replacement)
                continue
        i += 1
    return "".join(chars)


def _restore_url_regions(line: str, stored: list[str]) -> str:
    """Restore placeholders created by `_extract_url_regions`."""
    if not stored:
        return line

    def replacer(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if 0 <= index < len(stored):
            return stored[index]
        return match.group(0)

    return _URL_PLACEHOLDER_TOKEN_RE.sub(replacer, line)


_URL_PLACEHOLDER_PREFIX = "HSKPROSEURL"
_LINK_DESTINATION_RE = re.compile(r"\]\(([^)]*)\)")
_ANGLE_AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")
_URL_PLACEHOLDER_TOKEN_RE = re.compile(rf"{_URL_PLACEHOLDER_PREFIX}(\d+)")
_LINK_DEST_MASK_RE = re.compile(r"\]\([^)]*\)")
_HTML_TAG_MASK_RE = re.compile(r"<[^>]*>")
_H006_WORD_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
# Characters that appear in punctuated H006 keys (abbreviations, e-mail, c++, …).
# Space alone is not a trigger: almost every prose line has spaces.
_H006_PHRASE_TRIGGER_CHARS = frozenset(".-+#")

_LIST_MARKER_HYPHEN_PATTERN = re.compile(r"^(?:\s*>\s*)*\s*-")
