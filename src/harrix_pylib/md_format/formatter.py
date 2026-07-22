"""Markdown formatting orchestration."""

from __future__ import annotations

import re
from pathlib import Path

from harrix_pylib.md_format.autolink_format import _extract_angle_autolinks, _restore_angle_autolinks
from harrix_pylib.md_format.bullet_list_format import _extract_bullet_list_marker_groups
from harrix_pylib.md_format.code_guard import _extract_code_blocks, _restore_code_blocks
from harrix_pylib.md_format.front_matter import (
    _collapse_extra_blank_lines,
    _compact_front_matter,
    _extract_toml_blocks,
    _extract_yaml_blocks,
    _join_front_matter,
    _restore_toml_blocks,
    _restore_yaml_blocks,
    _split_front_matter,
    _trim_trailing_blank_lines,
)
from harrix_pylib.md_format.hard_break_format import _extract_backslash_hard_breaks
from harrix_pylib.md_format.ignore_format import _extract_ignore_blocks, _restore_ignore_blocks
from harrix_pylib.md_format.inline_link_format import _prepare_inline_links
from harrix_pylib.md_format.list_format import _ensure_blank_line_after_lists
from harrix_pylib.md_format.list_loose_format import _extract_list_layouts
from harrix_pylib.md_format.math_guard import _extract_empty_math_blocks, _restore_empty_math_blocks
from harrix_pylib.md_format.options import _FormatOptions
from harrix_pylib.md_format.ordered_list_format import _extract_ordered_list_marker_groups
from harrix_pylib.md_format.parser import _get_markdown_parser
from harrix_pylib.md_format.printer import _render_tokens
from harrix_pylib.md_format.prose_fixes import _apply_checker_prose_fixes
from harrix_pylib.md_format.reference_format import _extract_reference_blocks, _restore_reference_blocks
from harrix_pylib.md_format.table_format import _ensure_blank_line_after_tables, _unwrap_spurious_table_rows
from harrix_pylib.md_format.task_list_format import _extract_task_list_markers

_EMPTY_FENCE_RE = re.compile(r"(?m)^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})[ \t]*\n(?P=indent)(?P=fence)[ \t]*$")


class MdFormatter:
    """Format Markdown text inspired by Prettier Markdown parser."""

    def __call__(self, text: str) -> str:
        """Format Markdown text."""
        return self.format(text)

    def __init__(
        self,
        *,
        end_of_line: str = "crlf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
    ) -> None:
        """Initialize the MdFormatter.

        Args:

        - `end_of_line` (`str`): Line ending style (`crlf` or `lf`). Defaults to `crlf`.
        - `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`). Defaults to `preserve`.
        - `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.
        - `apply_prose_fixes` (`bool`): Apply mechanical MdChecker autofixes (typography, H006-H058
          subset). Defaults to `True`.

        """
        self.options = _FormatOptions(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
        )

    def format(self, text: str) -> str:
        """Format Markdown text.

        `prose_wrap` matches Prettier: `preserve` (default), `always`, or `never`.
        Line wrapping uses `print_width` only when `prose_wrap` is `always`.

        Args:

        - `text` (`str`): Markdown source text.

        Returns:

        - `str`: Formatted Markdown text.

        """
        from harrix_pylib.funcs_md import is_raw_markdown_enabled  # noqa: PLC0415

        if is_raw_markdown_enabled(text):
            return text
        return _format_with_options(text, self.options)

    def format_file(self, filename: Path | str) -> str:
        """Format a Markdown file in place when content or line endings change.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file.

        Returns:

        - `str`: Status message.

        """
        from harrix_pylib.funcs_md import is_raw_markdown_enabled  # noqa: PLC0415

        path = Path(filename)
        raw = path.read_bytes()
        document = self.read_markdown_text(path)
        if is_raw_markdown_enabled(document):
            return f"Skipped {path}: raw-markdown."
        document_new = self.format(document)
        if document != document_new or self._needs_end_of_line_rewrite(raw):
            path.write_text(document_new, encoding="utf-8", newline="")
            return f"✅ File {path} applied."
        return "File is not changed."

    def format_folder(self, folder: Path | str) -> str:
        """Recursively format Markdown files in a folder.

        Args:

        - `folder` (`Path | str`): Directory containing Markdown files.

        Returns:

        - `str`: Newline-separated status messages.

        """
        from harrix_pylib import funcs_file  # noqa: PLC0415

        return funcs_file.apply_func(folder, ".md", self.format_file)

    @staticmethod
    def normalize_line_endings(text: str) -> str:
        r"""Normalize mixed or corrupted line endings to LF.

        Handles CRLF applied twice (`\r\r\n`), which otherwise becomes a blank
        line between every source line after a two-step `\r` cleanup or
        after `pathlib.Path.read_text` universal-newline translation.

        Args:

        - `text` (`str`): Text with mixed line endings.

        Returns:

        - `str`: Text normalized to LF line endings.

        """
        return re.sub(r"\r+\n", "\n", text).replace("\r", "\n")

    @staticmethod
    def read_markdown_text(filename: Path | str) -> str:
        r"""Read Markdown from disk without universal-newline mangling of `\r\r\n`.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file.

        Returns:

        - `str`: File contents with normalized line endings.

        """
        path = Path(filename)
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            data = data[3:]
        return MdFormatter.normalize_line_endings(data.decode("utf-8"))

    def _needs_end_of_line_rewrite(self, raw: bytes) -> bool:
        """Return `True` when on-disk endings disagree with `end_of_line`."""
        if b"\n" not in raw:
            return False
        has_crlf = b"\r\n" in raw
        if self.options.end_of_line == "lf":
            return has_crlf
        if self.options.end_of_line == "crlf":
            return not has_crlf
        return False


def _ensure_blank_line_in_empty_fences(body: str) -> str:
    """Ensure empty fenced blocks are parsed as fences, not inline code."""
    return _EMPTY_FENCE_RE.sub(r"\g<indent>\g<fence>\n\n\g<indent>\g<fence>", body)


def _format_with_options(text: str, options: _FormatOptions) -> str:
    """Run the full extract-parse-render-restore formatting pipeline."""
    normalized = MdFormatter.normalize_line_endings(text)
    front_matter, body = _split_front_matter(normalized)
    if front_matter:
        front_matter = _compact_front_matter(front_matter)
        front_matter = front_matter.replace("\u00a0", " ")
    if options.apply_prose_fixes:
        # Run before parse/render so source-preserving paths keep fixed prose and
        # emphasis/link markup is not yet escaped or rewritten.
        body = _apply_checker_prose_fixes(body, lang=_lang_from_front_matter(front_matter))
    body = _ensure_blank_line_in_empty_fences(body)
    body, empty_math_blocks = _extract_empty_math_blocks(body)
    body, ignore_blocks = _extract_ignore_blocks(body)
    body, hard_break_styles = _extract_backslash_hard_breaks(body)
    body, angle_autolinks = _extract_angle_autolinks(body)
    body, reference_blocks = _extract_reference_blocks(body)
    body, code_blocks = _extract_code_blocks(body)
    body, yaml_blocks = _extract_yaml_blocks(body)
    body, toml_blocks = _extract_toml_blocks(body)
    body, ordered_list_marker_groups = _extract_ordered_list_marker_groups(body)
    body, bullet_list_marker_groups = _extract_bullet_list_marker_groups(body)
    tight_code_indices = {block.index for block in code_blocks if block.tight}
    body, list_layouts = _extract_list_layouts(body, tight_code_indices)
    body, task_list_markers = _extract_task_list_markers(body)
    body = _collapse_extra_blank_lines(body)
    body = _unwrap_spurious_table_rows(_ensure_blank_line_after_tables(body))
    body = _ensure_blank_line_after_lists(body)
    body, link_destinations = _prepare_inline_links(body)
    if not body.strip() and front_matter and not reference_blocks:
        result = front_matter.rstrip() + "\n"
    elif not body.strip() and not front_matter and reference_blocks:
        rendered_body = _restore_reference_blocks("", reference_blocks, options=options)
        result = rendered_body
    else:
        source_lines = body.split("\n")
        parser = _get_markdown_parser()
        tokens = parser.parse(body)
        rendered_body = _render_tokens(
            tokens,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=hard_break_styles,
            list_layouts=list_layouts,
            source_lines=source_lines,
            link_destinations=link_destinations,
            angle_autolinks=angle_autolinks,
        )
        rendered_body = _restore_code_blocks(rendered_body, code_blocks, options=options)
        rendered_body = _restore_empty_math_blocks(rendered_body, empty_math_blocks)
        rendered_body = _restore_angle_autolinks(rendered_body, angle_autolinks)
        rendered_body = _restore_reference_blocks(rendered_body, reference_blocks, options=options)
        rendered_body = _restore_toml_blocks(rendered_body, toml_blocks)
        rendered_body = _restore_yaml_blocks(rendered_body, yaml_blocks)
        rendered_body = _restore_ignore_blocks(rendered_body, ignore_blocks)
        result = _join_front_matter(front_matter, rendered_body) if front_matter else rendered_body
    result = _trim_trailing_blank_lines(result)
    return _normalize_end_of_line(result, options.end_of_line)


def _lang_from_front_matter(front_matter: str) -> str:
    """Return YAML `lang` from compacted front matter text."""
    if not front_matter:
        return ""
    for line in front_matter.splitlines():
        match = re.match(r"^lang:\s*[\"']?([^\s\"'#]+)", line.strip())
        if match:
            return match.group(1)
    return ""


def _normalize_end_of_line(text: str, end_of_line: str) -> str:
    """Convert normalized LF text to the requested line-ending style."""
    normalized = MdFormatter.normalize_line_endings(text)
    if end_of_line == "lf":
        return normalized
    if end_of_line == "crlf":
        return normalized.replace("\n", "\r\n")
    msg = f"Unsupported end_of_line value: {end_of_line}"
    raise ValueError(msg)
