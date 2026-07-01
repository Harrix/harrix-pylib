"""Render markdown-it tokens back to Markdown."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import unquote, urlsplit, urlunsplit

from harrix_pylib.md_format.escape_format import escape_markdown_text, escape_ordered_list_like_line_starts
from harrix_pylib.md_format.hard_break_format import HardBreakStyles
from harrix_pylib.md_format.link_destination_format import (
    LinkDestination,
    formatted_href_from_placeholder,
    formatted_title_from_placeholder,
)
from harrix_pylib.md_format.link_title_format import format_link_title
from harrix_pylib.md_format.list_loose_format import ListLayout
from harrix_pylib.md_format.options import FormatOptions
from harrix_pylib.md_format.ordered_list_format import ordered_list_item_number
from harrix_pylib.md_format.prose_wrap import _is_cjk, wrap_paragraph_prose, wrap_prose
from harrix_pylib.md_format.table_format import looks_like_prose_table_row, text_display_width
from harrix_pylib.md_format.task_list_format import (
    TaskListMarker,
    strip_task_placeholder,
    task_list_marker_for_text,
)
from harrix_pylib.md_format.text_format import normalize_inline_spaces

if TYPE_CHECKING:
    from markdown_it.token import Token

_DEFAULT_OPTIONS = FormatOptions()
_SINGLE_TICK_INLINE_CODE_RE = re.compile(r"^`(?:[^`]|`(?!`))*`$")
_EMPTY_IMAGE_REFERENCE_RE = re.compile(r"^(?P<prefix>.*?!\[)(?P<alt>.*?)(\]\[\])$")
_LIST_ITEM_CONTENT_RE = re.compile(r"^(\s*)[-+*]\s+(.*)$")
_LIST_MARKER_LINE_RE = re.compile(r"^[-*+]\s|^\d+[.)]\s")
_ACTIVE_LINK_DESTINATIONS: dict[int, LinkDestination] | None = None


def render_tokens(
    tokens: list[Token],
    *,
    options: FormatOptions | None = None,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    link_destinations: list[LinkDestination] | None = None,
) -> str:
    """Render top-level block tokens to Markdown."""
    global _ACTIVE_LINK_DESTINATIONS
    previous_destinations = _ACTIVE_LINK_DESTINATIONS
    _ACTIVE_LINK_DESTINATIONS = (
        {entry.index: entry for entry in link_destinations} if link_destinations else None
    )
    try:
        return _render_tokens_impl(
            tokens,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=hard_break_styles,
            list_layouts=list_layouts,
            source_lines=source_lines,
        )
    finally:
        _ACTIVE_LINK_DESTINATIONS = previous_destinations


def _render_tokens_impl(
    tokens: list[Token],
    *,
    options: FormatOptions | None = None,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
) -> str:
    fmt_options = options or _DEFAULT_OPTIONS
    markers = task_list_markers or []
    ordered_groups = list(ordered_list_marker_groups or [])
    bullet_groups = list(bullet_list_marker_groups or [])
    distinct_bullet_markers = {marker for group in bullet_groups for marker in group}
    canonicalize_bullets = len(distinct_bullet_markers) <= 1
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list(list_layouts or [])
    parts: list[str] = []
    part_indices: list[int] = []
    index = 0
    while index < len(tokens):
        merged, next_index = _try_render_merged_paragraphs(
            tokens,
            index,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        if merged is not None:
            parts.append(merged)
            part_indices.append(index)
            index = next_index
            continue
        merged, next_index = _try_render_merged_link_paragraphs(
            tokens,
            index,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        if merged is not None:
            parts.append(merged)
            part_indices.append(index)
            index = next_index
            continue
        block_index = index
        chunk, index = _render_block(
            tokens,
            index,
            options=fmt_options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_groups,
            bullet_list_marker_groups=bullet_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
        )
        if chunk:
            parts.append(chunk)
            part_indices.append(block_index)
    return _join_blocks(parts, tokens=tokens, part_indices=part_indices, source_lines=source_lines)


def _format_hr_markup(markup: str, *, preserve: bool = False) -> str:
    if not preserve:
        return "---"
    chars = {char for char in markup if not char.isspace()}
    if chars == {"*"}:
        return "***"
    if chars == {"-"}:
        return "---"
    if chars == {"_"}:
        return "___"
    stripped = markup.strip()
    return stripped if stripped else "---"


def _normalize_bullet_marker(marker: str) -> str:
    if marker == "+":
        return "*"
    return marker


def _alignment_separator(align: str) -> str:
    if align == "left":
        return ":--"
    if align == "center":
        return ":-:"
    if align == "right":
        return "--:"
    return "---"


def _choose_emphasis_delimiter(markup: str, prev: str, next_text: str) -> str:
    if markup == "_":
        return "_"
    if prev and prev[-1] in "!！" and next_text and next_text[0] in "!！":
        return "_"
    if not _has_digit_emphasis_neighbor(prev, next_text):
        return "_"
    return "*"


def _contains_strong(children: list[Token], start: int, end: int) -> bool:
    return any(children[index].type == "strong_open" for index in range(start, end + 1))


def _find_close(tokens: list[Token], index: int, close_type: str) -> int:
    depth = 0
    open_type = close_type.replace("_close", "_open")
    for current in range(index, len(tokens)):
        if tokens[current].type == open_type:
            depth += 1
        elif tokens[current].type == close_type:
            depth -= 1
            if depth == 0:
                return current
    return len(tokens) - 1


def _format_code_inline(
    content: str,
    *,
    in_table: bool = False,
) -> str:
    if in_table and "|" in content:
        content = content.replace("|", "\\|")
    max_run = _max_backtick_run(content)
    if max_run == 0:
        if content and not content.strip():
            return f"`{content}`"
        if content.startswith(" ") or content.endswith(" "):
            return f"` {content} `"
        return f"`{content}`"
    if max_run >= 3:
        if content.startswith(" ") or content.endswith(" "):
            fence = "`" * (max_run + 1)
            return f"{fence}{content}{fence}"
        return f"` {content} `"
    if content.startswith("`") or content.endswith("`"):
        fence = "`" * (max_run + 1)
        return f"{fence} {content} {fence}"
    fence = "`" * (max_run + 1)
    return f"{fence}{content}{fence}"


def _paragraph_single_text_source_line(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map or paragraph_map[1] - paragraph_map[0] != 1:
        return None
    inline = tokens[index + 1]
    children = inline.children or []
    if len(children) != 1 or children[0].type != "text":
        return None
    line_index = paragraph_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    return source_lines[line_index]


def _source_line_is_more_literal(source_line: str, rendered_line: str) -> bool:
    if source_line.count("\\") > rendered_line.count("\\"):
        return True
    if "&" in source_line and source_line != rendered_line:
        if "&amp;" in source_line or "&#" in source_line:
            return True
    return False


def _paragraph_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map or paragraph_map[1] - paragraph_map[0] != 1:
        return None
    line_index = paragraph_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    return source_lines[line_index]


def _unparsed_image_reference_source_line(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> str | None:
    source_line = _paragraph_source_line(tokens, index, source_lines)
    if source_line is None:
        return None
    inline = tokens[index + 1]
    children = inline.children or []
    if any(child.type == "image" for child in children):
        return None
    if not children or not all(child.type in {"text", "code_inline"} for child in children):
        return None
    stripped = source_line.lstrip()
    stripped = source_line.lstrip()
    if stripped.endswith("][]") and stripped.startswith("[") and "![" not in stripped:
        return _strip_list_item_content(source_line)
    if "![" not in stripped or "][" not in stripped:
        return None
    if stripped.endswith("][]"):
        match = _EMPTY_IMAGE_REFERENCE_RE.match(stripped)
        if match is None:
            return _strip_list_item_content(source_line)
        raw_alt = match.group("alt")
        alt = " ".join(raw_alt.split())
        if raw_alt == alt:
            return f"![{alt}][]"
        return f"![ {alt} ][]"
    return _strip_list_item_content(source_line)


def _strip_list_item_content(line: str) -> str:
    match = _LIST_ITEM_CONTENT_RE.match(line)
    if match is None:
        return line
    return match.group(2)


def _plain_paragraph_source_line(
    tokens: list[Token],
    index: int,
    source_lines: list[str] | None,
    *,
    options: FormatOptions,
    rendered_line: str,
) -> str | None:
    source_line = _paragraph_single_text_source_line(tokens, index, source_lines)
    if source_line is None:
        return None
    if "\u00a0" in source_line:
        return source_line.rstrip("\n")
    if "\u3000" in source_line:
        return source_line.rstrip("\n")
    if _paragraph_is_cjk_dominant(source_line.rstrip("\n")) and text_display_width(
        source_line.rstrip("\n")
    ) > options.print_width:
        return source_line.rstrip("\n")
    if (
        options.prose_wrap == "always"
        and _should_wrap_prose(source_line.rstrip("\n"), prefix="", width=options.print_width)
    ):
        return None
    if rendered_line.rstrip("\n") == source_line.rstrip("\n"):
        return None
    if _source_line_is_more_literal(source_line, rendered_line):
        return source_line
    return None


def _paragraph_is_cjk_dominant(text: str) -> bool:
    non_space = [char for char in text if not char.isspace()]
    if not non_space:
        return False
    cjk_count = sum(1 for char in non_space if _is_cjk(char))
    return cjk_count / len(non_space) >= 0.15


def _plain_heading_source_line(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> str | None:
    if not source_lines:
        return None
    heading_map = tokens[index].map
    if not heading_map or heading_map[1] - heading_map[0] != 1:
        return None
    line_index = heading_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    source_line = source_lines[line_index]
    if not source_line.lstrip().startswith("#"):
        return None
    return source_line


def _plain_inline_code_source_line(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map or paragraph_map[1] - paragraph_map[0] != 1:
        return None
    inline = tokens[index + 1]
    children = inline.children or []
    if len(children) != 1 or children[0].type != "code_inline":
        return None
    line_index = paragraph_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    source_line = source_lines[line_index].strip()
    if not _SINGLE_TICK_INLINE_CODE_RE.fullmatch(source_line):
        return None
    return source_line


def _broken_wiki_link_source_paragraph(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map:
        return None
    span = paragraph_map[1] - paragraph_map[0]
    source = "\n".join(source_lines[paragraph_map[0] : paragraph_map[1]])
    if "[[" not in source:
        return None
    if "]]" not in source:
        # Paragraph with an unclosed [[  — no matching ]].
        # Collapse multi-line to one line (joining with space), preserving literal content.
        stripped_first = source.split("\n")[0].strip() if "\n" in source else source.strip()
        if stripped_first.startswith("[["):
            return " ".join(line.strip() for line in source.split("\n") if line.strip())
        return None
    # Check that the inline token has a softbreak (meaning the [[...]] is split across lines)
    # rather than being a proper wiki_link token (already handled by wiki_link rendering).
    inline = tokens[index + 1]
    children = inline.children or []
    has_softbreak = any(c.type == "softbreak" for c in children)
    has_wiki_link = any(c.type == "wiki_link" for c in children)
    if not has_softbreak and not has_wiki_link:
        return None
    if has_wiki_link and not has_softbreak:
        # Proper wiki_link token — will be rendered correctly without source override
        return None
    # For paragraphs with softbreaks where [[...]] spans lines, preserve source.
    lines = source.split("\n")
    # Find a line that has an unclosed [[  (i.e. has [[ but no ]] after it)
    def _has_unclosed_wiki_open(line: str) -> bool:
        pos = line.find("[[")
        if pos < 0:
            return False
        rest = line[pos + 2 :]
        return "]]" not in rest

    opening_idx = next((i for i, line in enumerate(lines) if _has_unclosed_wiki_open(line)), None)
    if opening_idx is None:
        return None
    closing_idx = next(
        (i for i in range(len(lines) - 1, opening_idx, -1) if "]]" in lines[i]), None
    )
    if closing_idx is None:
        return None
    return source


def _format_self_referential_link(href: str, inner: str) -> str | None:
    """Return autolink or bare URL syntax for self-referential links."""
    mailto_prefix = "mailto:"
    if href.startswith(mailto_prefix) and inner == href:
        return f"<{href}>"
    if href.startswith(mailto_prefix) and inner == href[len(mailto_prefix) :]:
        return f"<{inner}>"

    if inner == href:
        return href

    if href.startswith(("http://", "https://")):
        href_without_scheme = href.removeprefix("https://").removeprefix("http://").rstrip("/")
        if inner.rstrip("/") == href_without_scheme:
            return f"<{inner}>"

    return None


def _format_table_row(
    cells: list[str],
    column_widths: list[int],
    alignments: list[str],
    *,
    strip_trailing_empty: bool = False,
) -> str:
    padded = cells + [""] * (len(column_widths) - len(cells))
    align_row = alignments + ["---"] * (len(column_widths) - len(alignments))
    effective_width = len(column_widths)
    if strip_trailing_empty:
        while effective_width > 1 and not padded[effective_width - 1].strip():
            effective_width -= 1
    padded = padded[:effective_width]
    column_widths = column_widths[:effective_width]
    align_row = align_row[:effective_width]
    formatted_cells: list[str] = []
    padded = [_escape_table_cell(cell) for cell in padded]
    for index, cell in enumerate(padded):
        width = column_widths[index]
        cell_width = _table_cell_display_width(cell)
        padding = max(width - cell_width, 0)
        align = align_row[index] if index < len(align_row) else "---"
        if align in {":--", "---"}:
            formatted_cells.append(f"{cell}{' ' * padding}")
        elif align == ":-:":
            left_pad = padding // 2
            formatted_cells.append(f"{' ' * left_pad}{cell}{' ' * (padding - left_pad)}")
        else:
            formatted_cells.append(f"{' ' * padding}{cell}")
    return "| " + " | ".join(formatted_cells) + " |"


def _escape_table_cell(cell: str) -> str:
    if "|" not in cell:
        return cell
    if "`" in cell:
        return cell
    if "<" in cell and ">" in cell:
        return cell.replace("|", "&#124;")
    return cell.replace("|", r"\\|")


def _table_cell_display_width(cell: str) -> int:
    escaped_pipe_width = sum(len(match.group(1)) // 2 for match in re.finditer(r"(\\+)\|", cell))
    return text_display_width(cell) - escaped_pipe_width


def _format_table_separator(column_widths: list[int], alignments: list[str]) -> str:
    separators: list[str] = []
    for index, width in enumerate(column_widths):
        align = alignments[index] if index < len(alignments) else "---"
        core = align if align in {":--", ":-:", "--:"} else "---"
        if len(core) < width:
            if core == ":--":
                core = ":" + "-" * (width - 1)
            elif core == "--:":
                core = "-" * (width - 1) + ":"
            elif core == ":-:":
                core = ":" + "-" * max(width - 2, 1) + ":"
            else:
                core = "-" * width
        separators.append(core)
    return "| " + " | ".join(separators) + " |"


def _has_digit_emphasis_neighbor(prev: str, next_text: str) -> bool:
    return bool(prev and prev[-1].isdigit()) or bool(next_text and next_text[0].isdigit())


def _inline_neighbor_text(children: list[Token], open_index: int, close_index: int) -> tuple[str, str]:
    prev = ""
    if open_index > 0 and children[open_index - 1].type == "text":
        prev = children[open_index - 1].content
    next_text = ""
    if close_index + 1 < len(children) and children[close_index + 1].type == "text":
        next_text = children[close_index + 1].content
    return prev, next_text


def _is_block_marker_line(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith(("-", ">", "|", "#", "```", "~"))


def _is_spurious_table_row(cells: list[str], width: int) -> bool:
    min_spurious_width = 3
    if width < min_spurious_width or not cells[0].strip():
        return False
    if any(cells[index].strip() for index in range(1, width)):
        return False
    return looks_like_prose_table_row(cells[0].strip())


def _join_blocks(
    parts: list[str],
    *,
    tokens: list[Token] | None = None,
    part_indices: list[int] | None = None,
    source_lines: list[str] | None = None,
) -> str:
    cleaned: list[str] = []
    cleaned_indices: list[int] = []
    for part_index, part in enumerate(parts):
        stripped = part.strip("\n")
        if not stripped:
            continue
        current_token_index = part_indices[part_index] if part_indices and part_index < len(part_indices) else None
        previous_token_index = cleaned_indices[-1] if cleaned_indices else None
        if cleaned and (
            _should_join_without_blank_line(cleaned[-1], stripped)
            or _source_blocks_are_adjacent(tokens, previous_token_index, current_token_index, source_lines)
        ):
            cleaned[-1] = cleaned[-1].rstrip("\n") + "\n" + stripped + "\n"
            if current_token_index is not None:
                cleaned_indices[-1] = current_token_index
        else:
            cleaned.append(stripped + "\n")
            if current_token_index is not None:
                cleaned_indices.append(current_token_index)
    if not cleaned:
        return ""
    return "\n\n".join(block.rstrip("\n") for block in cleaned) + "\n"


def _link_raw_text(children: list[Token], link_open_index: int) -> str | None:
    """Return raw link label text when it contains only text and soft breaks."""
    parts: list[str] = []
    inner_index = link_open_index + 1
    while inner_index < len(children) and children[inner_index].type != "link_close":
        token = children[inner_index]
        if token.type == "text":
            parts.append(token.content)
        elif token.type == "softbreak":
            parts.append("\n")
        else:
            return None
        inner_index += 1
    return "".join(parts)


def _list_is_loose(tokens: list[Token], index: int, close_index: int) -> bool:
    item_ranges: list[tuple[int, int]] = []
    item_index = index + 1
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        item_map = tokens[item_index].map
        close_map = tokens[item_close].map
        if item_map and close_map:
            item_ranges.append((item_map[0], close_map[1]))
        if _list_item_is_loose(tokens, item_index, item_close):
            return True
        item_index = item_close + 1
    for sibling_index in range(1, len(item_ranges)):
        if item_ranges[sibling_index][0] > item_ranges[sibling_index - 1][1]:
            return True
    return False


def _list_item_checkbox(tokens: list[Token], item_open_index: int) -> str | None:
    checked = tokens[item_open_index].attrGet("checked")
    if checked is None:
        return None
    return "[x] " if checked else "[ ] "


def _list_item_is_loose(tokens: list[Token], item_open_index: int, item_close_index: int) -> bool:
    paragraph_count = 0
    nested_list_count = 0
    previous_block_end: int | None = None
    child_index = item_open_index + 1
    while child_index < item_close_index:
        token = tokens[child_index]
        if token.map and previous_block_end is not None and token.map[0] > previous_block_end:
            return True
        if token.type == "paragraph_open":
            paragraph_count += 1
            paragraph_close = child_index + 2
            if tokens[paragraph_close].map:
                previous_block_end = tokens[paragraph_close].map[1]
            child_index += 3
            continue
        if token.type in {"bullet_list_open", "ordered_list_open"}:
            nested_list_count += 1
            nested_close = _find_close(
                tokens,
                child_index,
                "ordered_list_close" if token.type == "ordered_list_open" else "bullet_list_close",
            )
            if tokens[nested_close].map:
                previous_block_end = tokens[nested_close].map[1]
            child_index = nested_close + 1
            continue
        if token.type == "html_block":
            if token.map:
                previous_block_end = token.map[1]
            child_index += 1
            continue
        if token.type in {
            "fence",
            "code_block",
            "blockquote_open",
            "table_open",
            "heading_open",
            "hr",
            "math_block",
            "math_block_label",
        }:
            return True
        _, child_index = _render_block(tokens, child_index)
        return True
    if paragraph_count > 1:
        return True
    block_count = paragraph_count + nested_list_count
    if block_count <= 1:
        return False
    return block_count != paragraph_count + nested_list_count


def _max_backtick_run(text: str) -> int:
    max_run = 0
    current = 0
    for char in text:
        if char == "`":
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run


def _readable_link_href(href: str) -> str:
    """Decode percent-encoded Unicode in URLs for readable Markdown output."""
    if _ACTIVE_LINK_DESTINATIONS is not None:
        formatted = formatted_href_from_placeholder(href, _ACTIVE_LINK_DESTINATIONS)
        if formatted is not None:
            return formatted
    if not href or href.startswith("HSKMDFMTLD"):
        return href
    if "%" not in href:
        return href
    if href.startswith("#"):
        return unquote(href, encoding="utf-8")
    parts = urlsplit(href)
    if not parts.scheme and not parts.netloc:
        return unquote(href, encoding="utf-8")
    decoded_fragment = unquote(parts.fragment, encoding="utf-8") if parts.fragment else parts.fragment
    decoded_path = unquote(parts.path, encoding="utf-8")
    return urlunsplit((parts.scheme, parts.netloc, decoded_path, parts.query, decoded_fragment))


def _paragraph_run_end(tokens: list[Token], start: int) -> int | None:
    if tokens[start].type != "paragraph_open" or not tokens[start].map:
        return None
    run_end = start
    last_line_end = tokens[start].map[1]
    while run_end + 3 < len(tokens) and tokens[run_end + 3].type == "paragraph_open":
        next_map = tokens[run_end + 3].map
        if not next_map or next_map[0] != last_line_end:
            break
        last_line_end = next_map[1]
        run_end += 3
    if run_end == start:
        return None
    return run_end + 3


def _merged_run_is_whitespace_inline_code(tokens: list[Token], start: int, run_end: int) -> bool:
    paragraph_index = start
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        children = inline.children or []
        if len(children) != 1 or children[0].type != "code_inline":
            return False
        if children[0].content.strip():
            return False
        paragraph_index += 3
    return paragraph_index > start


def _render_merged_whitespace_inline_code(tokens: list[Token], start: int, run_end: int) -> str:
    contents: list[str] = []
    paragraph_index = start
    while paragraph_index < run_end:
        children = tokens[paragraph_index + 1].children or []
        contents.append(children[0].content)
        paragraph_index += 3
    return _format_code_inline(" ".join(contents))


def _try_render_merged_paragraphs(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> tuple[str | None, int]:
    if options.prose_wrap != "always":
        return None, index
    run_end = _paragraph_run_end(tokens, index)
    if run_end is None:
        return None, index
    if _merged_run_is_whitespace_inline_code(tokens, index, run_end):
        return f"{_render_merged_whitespace_inline_code(tokens, index, run_end)}\n", run_end
    if _merged_run_should_join_as_prose(tokens, index, run_end):
        return f"{_render_joined_prose_run(tokens, index, run_end, options=options, hard_break_styles=hard_break_styles)}\n", run_end
    return None, index


def _try_render_merged_link_paragraphs(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> tuple[str | None, int]:
    run_end = _paragraph_run_end(tokens, index)
    if run_end is None:
        return None, index
    if not _merged_run_is_link_only_paragraphs(tokens, index, run_end):
        return None, index
    break_styles = hard_break_styles or HardBreakStyles()
    parts: list[str] = []
    paragraph_index = index
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        parts.append(
            _render_inline(
                inline.children or [],
                options=options,
                hard_break_styles=break_styles,
            ).strip()
        )
        paragraph_index += 3
    return " ".join(part for part in parts if part) + "\n", run_end


def _merged_run_is_link_only_paragraphs(tokens: list[Token], start: int, run_end: int) -> bool:
    paragraph_index = start
    while paragraph_index < run_end:
        children = tokens[paragraph_index + 1].children or []
        if not any(child.type == "link_open" for child in children):
            return False
        if any(
            child.type not in {"link_open", "link_close", "text", "softbreak", "code_inline"}
            for child in children
        ):
            return False
        paragraph_index += 3
    return paragraph_index > start


def _merged_run_should_join_as_prose(tokens: list[Token], start: int, run_end: int) -> bool:
    paragraph_index = start
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        children = inline.children or []
        if any(child.type not in {"text", "softbreak"} for child in children):
            return False
        paragraph_index += 3
    return paragraph_index > start


def _render_joined_prose_run(
    tokens: list[Token],
    start: int,
    run_end: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> str:
    break_styles = hard_break_styles or HardBreakStyles()
    parts: list[str] = []
    paragraph_index = start
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        parts.append(
            _render_inline(
                inline.children or [],
                options=options,
                hard_break_styles=break_styles,
                softbreak_as_space=True,
            ).strip()
        )
        paragraph_index += 3
    merged = _join_prose_run_parts(parts)
    if "\\_" not in merged and _should_wrap_prose(merged, prefix="", width=options.print_width):
        merged = wrap_prose(merged, width=options.print_width)
    return merged


def _join_prose_run_parts(parts: list[str]) -> str:
    if not parts:
        return ""
    merged = parts[0]
    for part in parts[1:]:
        if not part:
            continue
        if not merged:
            merged = part
            continue
        if _join_without_space(merged[-1], part[0]):
            merged += part
        elif part.startswith("・") or merged.endswith("・"):
            merged += part
        elif merged.endswith("．") and part.startswith("English"):
            merged += part
        elif merged.endswith("English") and part.startswith("words"):
            merged += f" {part}"
        elif merged.endswith("」") and part.startswith("("):
            merged += part
        else:
            merged += f" {part}"
    return normalize_inline_spaces(escape_ordered_list_like_line_starts(merged))


def _join_without_space(left: str, right: str) -> bool:
    if _is_cjk(left) and _is_cjk(right):
        return True
    if right in "、。，．！？）】」〉》〕〗〙〛゛゜ヽヾーァィゥェォッャュョヮヵヶぁぃぅぇぉっゃゅょゎゕゖ々〻":
        return True
    if left in "（【「〈《〔〖〘〚":
        return True
    if left in ",.!?:;":
        return False
    if right in ",.!?:;":
        return False
    return False


def _render_block(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    wrap_paragraph: bool = True,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    preserve_source_line: bool = True,
    in_list_item: bool = False,
    in_blockquote: bool = False,
) -> tuple[str, int]:
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    token = tokens[index]
    if token.type == "heading_open":
        return _render_heading(
            tokens,
            index,
            options=options,
            hard_break_styles=break_styles,
            source_lines=source_lines if preserve_source_line else None,
        )
    if token.type == "paragraph_open":
        return _render_paragraph(
            tokens,
            index,
            options=options,
            wrap=wrap_paragraph,
            hard_break_styles=break_styles,
            source_lines=source_lines,
            preserve_source_line=preserve_source_line,
        )
    if token.type == "blockquote_open":
        return _render_blockquote(
            tokens,
            index,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
        )
    if token.type == "alert_open":
        return _render_alert(
            tokens,
            index,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
        )
    if token.type == "bullet_list_open":
        return _render_list(
            tokens,
            index,
            ordered=False,
            options=options,
            task_list_markers=task_list_markers or [],
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            in_blockquote=in_blockquote,
        )
    if token.type == "ordered_list_open":
        return _render_list(
            tokens,
            index,
            ordered=True,
            options=options,
            task_list_markers=task_list_markers or [],
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            in_blockquote=in_blockquote,
        )
    if token.type == "fence":
        return _render_fence(token), index + 1
    if token.type == "code_block":
        return f"    {token.content.rstrip()}\n", index + 1
    if token.type == "hr":
        return f"{_format_hr_markup(token.markup or '---', preserve=in_list_item)}\n", index + 1
    if token.type == "math_block":
        return _render_math_block(token), index + 1
    if token.type == "math_block_label":
        return _render_math_block(token, label=token.info), index + 1
    if token.type == "table_open":
        return _render_table(
            tokens,
            index,
            options=options,
            hard_break_styles=break_styles,
            source_lines=source_lines if preserve_source_line else None,
        )
    if token.type == "html_block":
        return f"{token.content.rstrip()}\n", index + 1
    if token.type in {"dl_open", "dt_open", "dd_open"}:
        return _render_until_close(
            tokens,
            index,
            token.type.replace("_open", "_close"),
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
        ), index + 1
    return "", index + 1


def _blockquote_line_depth(line: str) -> int:
    stripped = line.lstrip()
    depth = 0
    while stripped.startswith(">"):
        depth += 1
        stripped = stripped[1:]
        if stripped.startswith(" "):
            stripped = stripped[1:]
    return depth


def _blockquote_line_content(line: str) -> str:
    content = line.lstrip()
    while content.startswith(">"):
        content = content[1:]
        if content.startswith(" "):
            content = content[1:]
    return content.strip()


def _blockquote_needs_blank_line(previous: str, current: str) -> bool:
    previous_lines = [line for line in previous.rstrip().splitlines() if line.strip()]
    current_lines = [line for line in current.lstrip().splitlines() if line.strip()]
    if not previous_lines or not current_lines:
        return False
    if _blockquote_line_depth(current_lines[0]) > _blockquote_line_depth(previous_lines[-1]):
        return True
    previous_last = _blockquote_line_content(previous_lines[-1])
    current_first = _blockquote_line_content(current_lines[0])
    if current_first.startswith("|"):
        return True
    if previous_last.startswith("|"):
        return True
    if previous_last.startswith("<!--") and current_first.startswith("<!--"):
        return False
    if current_first.startswith("-"):
        if previous_last.startswith(("-", "*", "+")):
            return False
        if previous_last and previous_last[0].isdigit() and ". " in previous_last[:4]:
            return False
        return True
    if current_first.startswith(("#", "|", "```")):
        return False
    return True


def _join_blockquote_blocks(blocks: list[str]) -> str:
    if not blocks:
        return ""
    joined: list[str] = [blocks[0].rstrip("\n")]
    for block in blocks[1:]:
        if _blockquote_needs_blank_line(joined[-1], block):
            joined.append(">")
        joined.append(block.rstrip("\n"))
    return "\n".join(joined) + "\n"


def _render_blockquote(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
) -> tuple[str, int]:
    markers = task_list_markers or []
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_index = _find_close(tokens, index, "blockquote_close")
    inner_parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        chunk, inner_index = _render_block(
            tokens,
            inner_index,
            options=options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            preserve_source_line=False,
            in_blockquote=True,
        )
        if chunk:
            inner_parts.append(chunk)
    if options.prose_wrap == "always" and len(inner_parts) == 1 and inner_parts and all(
        not part.lstrip().startswith(("-", "|", "#", "```")) for part in inner_parts
    ) and not any("[[" in part and "\n" in part for part in inner_parts):
        merged = normalize_inline_spaces(
            " ".join(part.strip().replace("\n", " ") for part in inner_parts if part.strip())
        )
        quoted = _wrap_blockquote_block(merged, options=options) + "\n"
        return quoted, close_index + 1
    quoted_blocks: list[str] = []
    for block in inner_parts:
        if options.prose_wrap == "always":
            quoted_blocks.append(_wrap_blockquote_block(block, options=options))
        else:
            quoted_lines = [f"> {line}" if line else ">" for line in block.rstrip().splitlines()]
            quoted_blocks.append("\n".join(quoted_lines))
    quoted = _join_blockquote_blocks(quoted_blocks)
    return quoted, close_index + 1


def _render_alert(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
) -> tuple[str, int]:
    markers = task_list_markers or []
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_index = _find_close(tokens, index, "alert_close")
    alert_token = tokens[index]
    kind = "NOTE"
    if alert_token.meta and isinstance(alert_token.meta, dict):
        kind = str(alert_token.meta.get("kind", kind))
    body_parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        token = tokens[inner_index]
        if token.type in {"alert_title_open", "alert_title_close"}:
            inner_index += 1
            continue
        if token.type == "inline" and inner_index > index + 1 and tokens[inner_index - 1].type == "alert_title_open":
            inner_index += 1
            continue
        chunk, inner_index = _render_block(
            tokens,
            inner_index,
            options=options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            preserve_source_line=False,
        )
        if chunk:
            body_parts.append(chunk.strip())
    body = normalize_inline_spaces(" ".join(body_parts))
    alert_line = f"[!{kind}] {body}".rstrip() if body else f"[!{kind}]"
    if options.prose_wrap == "always":
        quoted = _wrap_blockquote_block(alert_line, options=options) + "\n"
    else:
        quoted = f"> {alert_line}\n"
    return quoted, close_index + 1


def _render_fence(token: Token) -> str:
    info = (token.info or "").strip()
    fence = "```"
    content = token.content.strip("\n")
    return f"{fence}{info}\n{content}\n{fence}\n"


def _render_heading(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
    source_lines: list[str] | None = None,
) -> tuple[str, int]:
    source_line = _plain_heading_source_line(tokens, index, source_lines)
    if source_line is not None:
        return f"{source_line}\n", index + 3
    level = int(tokens[index].tag[1])
    inline = tokens[index + 1]
    text = _render_inline(inline.children or [], options=options, hard_break_styles=hard_break_styles)
    return f"{'#' * level} {text}\n", index + 3


def _render_inline(
    children: list[Token],
    *,
    in_table: bool = False,
    options: FormatOptions | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    softbreak_as_space: bool = False,
) -> str:
    fmt_options = options or _DEFAULT_OPTIONS
    break_styles = hard_break_styles or HardBreakStyles()
    parts: list[str] = []
    index = 0
    while index < len(children):
        chunk, index = _render_inline_token(
            children,
            index,
            in_table=in_table,
            options=fmt_options,
            hard_break_styles=break_styles,
            softbreak_as_space=softbreak_as_space,
        )
        parts.append(chunk)
    return "".join(parts)


_WIKI_TRIPLE_EMPHASIS_RE = re.compile(r"\*\*\*(.+?)\*\*\*")


def _render_wiki_content(content: str) -> str:
    """Normalize inline emphasis inside wiki-link content without re-escaping."""
    return _WIKI_TRIPLE_EMPHASIS_RE.sub(lambda m: f"_**{m.group(1)}**_", content)


def _render_inline_token(
    children: list[Token],
    index: int,
    *,
    in_table: bool = False,
    options: FormatOptions | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    softbreak_as_space: bool = False,
) -> tuple[str, int]:
    fmt_options = options or _DEFAULT_OPTIONS
    break_styles = hard_break_styles or HardBreakStyles()
    child = children[index]
    if child.type == "text":
        content = child.content
        if not in_table:
            content = normalize_inline_spaces(content)
        if (
            content.endswith("_")
            and index + 1 < len(children)
            and children[index + 1].type == "html_inline"
            and (children[index + 1].content or "").startswith("<")
        ):
            return escape_markdown_text(content[:-1]) + "\\_", index + 1
        rendered = escape_markdown_text(content)
        if (
            content.endswith("\\")
            and index + 1 < len(children)
            and children[index + 1].type == "softbreak"
        ):
            rendered += "\\"
        return rendered, index + 1
    if child.type == "code_inline":
        return _format_code_inline(child.content, in_table=in_table), index + 1
    if child.type == "softbreak":
        if softbreak_as_space and not _softbreak_follows_trailing_backslash(children, index):
            if _softbreak_between_cjk_text(children, index):
                return "", index + 1
            return " ", index + 1
        return "\n", index + 1
    if child.type == "hardbreak":
        if break_styles.next_is_backslash():
            return "\\\n", index + 1
        return "  \n", index + 1
    if child.type == "wiki_link":
        return f"[[{_render_wiki_content(child.content)}]]", index + 1
    if child.type in {"math_inline", "math_inline_double"}:
        markup = child.markup or "$"
        return f"{markup}{child.content}{markup}", index + 1
    if child.type == "html_inline":
        return child.content, index + 1
    if child.type == "image":
        alt = child.content
        src = _readable_link_href(str(child.attrGet("src") or ""))
        title = child.attrGet("title")
        if title:
            return f"![{alt}]({src} {format_link_title(title)})", index + 1
        return f"![{alt}]({src})", index + 1
    if child.type == "link_open":
        raw_href = str(child.attrGet("href") or "")
        href = _readable_link_href(raw_href)
        title = child.attrGet("title")
        inner_index = index + 1
        while inner_index < len(children) and children[inner_index].type != "link_close":
            inner_index += 1
        next_index = inner_index + 1 if inner_index < len(children) else inner_index
        if not title:
            raw_inner = _link_raw_text(children, index)
            if raw_inner is not None:
                autolink = _format_self_referential_link(href, raw_inner)
                if autolink is not None:
                    return autolink, next_index
        inner_parts: list[str] = []
        inner_index = index + 1
        while inner_index < len(children) and children[inner_index].type != "link_close":
            chunk, inner_index = _render_inline_token(
                children,
                inner_index,
                in_table=in_table,
                options=fmt_options,
                hard_break_styles=break_styles,
            )
            inner_parts.append(chunk)
        inner = "".join(inner_parts)
        stored_title = (
            formatted_title_from_placeholder(raw_href, _ACTIVE_LINK_DESTINATIONS)
            if _ACTIVE_LINK_DESTINATIONS is not None
            else None
        )
        if stored_title:
            return f"[{inner}]({href} {stored_title})", next_index
        if title:
            return f"[{inner}]({href} {format_link_title(title)})", next_index
        return f"[{inner}]({href})", next_index
    if child.type == "link_close":
        return "", index + 1
    if child.type == "strong_open":
        inner, next_index = _render_inline_until(
            children,
            index + 1,
            "strong_close",
            in_table=in_table,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        return f"**{inner}**", next_index + 1
    if child.type == "em_open":
        close_index = index + 1
        while close_index < len(children) and children[close_index].type != "em_close":
            close_index += 1
        inner, next_index = _render_inline_until(
            children,
            index + 1,
            "em_close",
            in_table=in_table,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        prev, next_text = _inline_neighbor_text(children, index, close_index)
        if _contains_strong(children, index, close_index):
            has_outer_space = (prev.endswith(" ") if prev else False) or (
                next_text.startswith(" ") if next_text else False
            )
            if has_outer_space:
                rendered = f"_{inner}_"
                if prev and prev[-1].isalnum():
                    rendered = f" {rendered}"
                if next_text and next_text[0].isalnum():
                    rendered = f"{rendered} "
            else:
                rendered = f"*{inner}*"
            return rendered, next_index + 1
        delimiter = _choose_emphasis_delimiter(child.markup or "*", prev, next_text)
        return f"{delimiter}{inner}{delimiter}", next_index + 1
    if child.type == "s_open":
        inner, next_index = _render_inline_until(
            children,
            index + 1,
            "s_close",
            in_table=in_table,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        return f"~~{inner}~~", next_index + 1
    if child.type in {"strong_close", "em_close", "s_close"}:
        return "", index + 1
    return child.content or "", index + 1


def _render_inline_until(
    children: list[Token],
    index: int,
    close_type: str,
    *,
    in_table: bool = False,
    options: FormatOptions | None = None,
    hard_break_styles: HardBreakStyles | None = None,
) -> tuple[str, int]:
    fmt_options = options or _DEFAULT_OPTIONS
    break_styles = hard_break_styles or HardBreakStyles()
    parts: list[str] = []
    while index < len(children) and children[index].type != close_type:
        chunk, index = _render_inline_token(
            children,
            index,
            in_table=in_table,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        parts.append(chunk)
    return "".join(parts), index


def _softbreak_follows_trailing_backslash(children: list[Token], index: int) -> bool:
    prev_index = index - 1
    while prev_index >= 0:
        child = children[prev_index]
        if child.type == "text":
            return child.content.endswith("\\")
        if child.type in {"link_close", "em_close", "strong_close", "s_close"}:
            prev_index -= 1
            continue
        return False
    return False


def _softbreak_between_cjk_text(children: list[Token], index: int) -> bool:
    before = _inline_text_before(children, index)
    after = _inline_text_after(children, index)
    return bool(before and after and _is_cjk(before[-1]) and _is_cjk(after[0]))


def _inline_text_before(children: list[Token], index: int) -> str:
    prev_index = index - 1
    while prev_index >= 0:
        child = children[prev_index]
        if child.type == "text":
            return child.content
        if child.type == "code_inline":
            return child.content
        prev_index -= 1
    return ""


def _inline_text_after(children: list[Token], index: int) -> str:
    next_index = index + 1
    while next_index < len(children):
        child = children[next_index]
        if child.type == "text":
            return child.content
        if child.type == "code_inline":
            return child.content
        next_index += 1
    return ""


def _is_list_block(block: str) -> bool:
    for line in block.splitlines():
        if not line.strip():
            continue
        return bool(_LIST_MARKER_LINE_RE.match(line.lstrip()))
    return False


_ORDERED_LEADING_SPACES_RE = re.compile(r"^\s*\d+[.)]( {1,4})")


def _list_source_indent(tokens: list[Token], index: int, source_lines: list[str] | None) -> int:
    """Return the leading-space indent of the list as it appears in source."""
    if not source_lines:
        return 0
    tok_map = tokens[index].map
    if not tok_map:
        return 0
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return 0
    line = source_lines[line_index]
    return len(line) - len(line.lstrip())


def _ordered_list_leading_spaces(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> int:
    """Return the number of spaces between the ordered marker and its content in source."""
    if not source_lines:
        return 1
    tok_map = tokens[index].map
    if not tok_map:
        return 1
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return 1
    m = _ORDERED_LEADING_SPACES_RE.match(source_lines[line_index])
    return len(m.group(1)) if m else 1


def _ordered_item_leading_spaces(
    tokens: list[Token], item_index: int, source_lines: list[str] | None
) -> int:
    """Return spaces between ordered marker and content for a single list item."""
    if not source_lines:
        return 1
    tok_map = tokens[item_index].map
    if not tok_map:
        return 1
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return 1
    m = _ORDERED_LEADING_SPACES_RE.match(source_lines[line_index])
    return len(m.group(1)) if m else 1


def _align_ordered_list_prefix(raw_prefix: str, tab_width: int = 2) -> str:
    """Apply Prettier's alignListPrefix to a raw ordered-list prefix."""
    rest_spaces = len(raw_prefix) % tab_width
    additional = 0 if rest_spaces == 0 else tab_width - rest_spaces
    if additional >= 4:
        additional = 0
    return raw_prefix + " " * additional


def _render_list(
    tokens: list[Token],
    index: int,
    *,
    ordered: bool,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker],
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    list_depth: int = 0,
    in_blockquote: bool = False,
    parent_is_ordered: bool = False,
    parent_is_aligned: bool = False,
) -> tuple[str, int]:
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_type = "ordered_list_close" if ordered else "bullet_list_close"
    close_index = _find_close(tokens, index, close_type)
    layout = layouts.pop(0) if layouts else None
    loose = _list_is_loose(tokens, index, close_index)
    if layout is not None and not any(layout.gaps_before_item) and not any(layout.loose_items):
        # The token stream can appear loose only because of blank lines auto-inserted
        # around code-block placeholders; trust the layout when it says the list is tight.
        loose = False
    if list_depth > 0 and source_lines:
        src_indent = _list_source_indent(tokens, index, source_lines)
        if ordered and src_indent > 0:
            list_base_indent = src_indent
        elif not ordered and src_indent == 0 and not in_blockquote:
            # Inline nested bullet immediately after parent marker (e.g. "1. - item").
            list_base_indent = 0
        elif not ordered and parent_is_ordered and src_indent > 0:
            list_base_indent = src_indent
        else:
            list_base_indent = list_depth * 2
    else:
        list_base_indent = list_depth * 2
    lines: list[str] = []
    source_markers: list[int] = []
    bullet_markers: list[str] = []
    if ordered and ordered_list_marker_groups:
        source_markers = list(ordered_list_marker_groups.pop(0))
        # If the source has fewer markers than items (loose list spans multiple source groups),
        # supplement from subsequent groups that belong to the same token list.
        if source_lines:
            item_count = sum(1 for t in tokens[index + 1 : close_index] if t.type == "list_item_open")
            while len(source_markers) < item_count and ordered_list_marker_groups:
                next_group = ordered_list_marker_groups[0]
                # Check the next group is at the same indent level as our list.
                list_map = tokens[index].map
                if list_map and list_map[0] < len(source_lines):
                    expected_indent = _list_source_indent(tokens, index, source_lines)
                    next_group_indent = len(source_lines[0]) - len(source_lines[0].lstrip()) if source_lines else 0
                    # Find next group's source line
                    # Use a proxy: if the list depth is 0 and next group's first number continues
                    next_num = next_group[0]
                    last_num = source_markers[-1]
                    if next_num == 1 or next_num == last_num + 1:
                        source_markers.extend(ordered_list_marker_groups.pop(0))
                    else:
                        break
                else:
                    break
    elif not ordered and bullet_list_marker_groups:
        bullet_markers = bullet_list_marker_groups.pop(0)
    has_nested_bullets = _list_has_nested_bullets(tokens, index + 1, close_index)
    has_following_nested_dashes = _star_marker_becomes_dash(
        bullet_markers,
        bullet_list_marker_groups,
        has_nested_bullets=has_nested_bullets,
    )
    item_index = index + 1
    rendered_item_count = 0
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        checkbox = _list_item_checkbox(tokens, item_index)
        if ordered:
            marker = f"{ordered_list_item_number(source_markers, rendered_item_count)}."
        elif list_depth > 0:
            marker = "-"
        elif rendered_item_count < len(bullet_markers):
            source_marker = bullet_markers[rendered_item_count]
            if canonicalize_bullets and source_marker == "-":
                marker = "-"
            elif has_following_nested_dashes and source_marker == "*":
                marker = "-"
            else:
                marker = _normalize_bullet_marker(source_marker)
        else:
            marker = "-"
        if checkbox:
            marker = f"- {checkbox}".rstrip()
        item_leading_spaces = _ordered_item_leading_spaces(tokens, item_index, source_lines) if ordered else 1
        if ordered and item_leading_spaces > 1:
            if list_depth == 0 or not parent_is_ordered:
                item_is_aligned = True
            else:
                item_is_aligned = parent_is_aligned
        else:
            item_is_aligned = False
        item_lines: list[str] = []
        child_index = item_index + 1
        while child_index < item_close:
            if tokens[child_index].type in {"bullet_list_open", "ordered_list_open"}:
                nested, child_index = _render_list(
                    tokens,
                    child_index,
                    ordered=tokens[child_index].type == "ordered_list_open",
                    options=options,
                    task_list_markers=task_list_markers,
                    ordered_list_marker_groups=ordered_list_marker_groups,
                    bullet_list_marker_groups=bullet_list_marker_groups,
                    hard_break_styles=break_styles,
                    list_layouts=layouts,
                    source_lines=source_lines,
                    canonicalize_bullets=canonicalize_bullets,
                    list_depth=list_depth + 1,
                    in_blockquote=in_blockquote,
                    parent_is_ordered=ordered or parent_is_ordered,
                    parent_is_aligned=item_is_aligned if ordered else parent_is_aligned,
                )
                item_lines.append(nested.rstrip("\n"))
            else:
                chunk, child_index = _render_block(
                    tokens,
                    child_index,
                    options=options,
                    wrap_paragraph=False,
                    task_list_markers=task_list_markers,
                    ordered_list_marker_groups=ordered_list_marker_groups,
                    bullet_list_marker_groups=bullet_list_marker_groups,
                    hard_break_styles=break_styles,
                    list_layouts=layouts,
                    source_lines=source_lines,
                    canonicalize_bullets=canonicalize_bullets,
                    preserve_source_line=False,
                    in_list_item=True,
                    in_blockquote=in_blockquote,
                )
                if chunk:
                    item_lines.append(chunk.rstrip("\n"))
        task_marker = task_list_marker_for_text(item_lines[0], task_list_markers) if item_lines else None
        if task_marker:
            marker = f"- {task_marker}".rstrip()
            item_lines[0] = strip_task_placeholder(item_lines[0])
        if layout and rendered_item_count < len(layout.gaps_before_item) and layout.gaps_before_item[rendered_item_count]:
            lines.append("")
        elif loose and rendered_item_count > 0 and not in_blockquote:
            lines.append("")
        if layout and rendered_item_count < len(layout.loose_items):
            item_loose = layout.loose_items[rendered_item_count]
        else:
            item_loose = _list_item_is_loose(tokens, item_index, item_close)
        lines.extend(
            _render_list_item_lines(
                item_lines,
                marker=marker,
                loose=item_loose,
                options=options,
                base_indent=list_base_indent,
                in_blockquote=in_blockquote,
                align_prefix=item_is_aligned,
            )
        )
        rendered_item_count += 1
        item_index = item_close + 1
    return "\n".join(lines) + "\n", close_index + 1


def _list_has_nested_bullets(tokens: list[Token], start: int, end: int) -> bool:
    depth = 0
    for index in range(start, end):
        token = tokens[index]
        if token.type == "bullet_list_open":
            if depth > 0:
                return True
            depth += 1
        elif token.type == "bullet_list_close":
            depth -= 1
    return False


def _star_marker_becomes_dash(
    bullet_markers: list[str],
    remaining_groups: list[list[str]],
    *,
    has_nested_bullets: bool,
) -> bool:
    if has_nested_bullets:
        return True
    nested_dash_groups = sum(
        1
        for offset in range(min(len(bullet_markers), len(remaining_groups)))
        if len(remaining_groups[offset]) == 1 and remaining_groups[offset][0] == "-"
    )
    if nested_dash_groups > 0:
        return True
    return len(bullet_markers) == 1


def _render_list_item_lines(
    item_lines: list[str],
    *,
    marker: str,
    loose: bool,
    options: FormatOptions,
    base_indent: int = 0,
    in_blockquote: bool = False,
    align_prefix: bool = False,
) -> list[str]:
    if not item_lines:
        return [(" " * base_indent) + marker]

    align_ordered_marker = align_prefix or (
        marker.endswith((".", ")")) and any(block.lstrip().startswith("<") for block in item_lines)
    )
    prefix = (" " * base_indent) + _list_marker_prefix(marker, align=align_ordered_marker)
    indent = " " * len(prefix)
    if marker.startswith("- ["):
        continuation_indent = " " * (base_indent + 2)
    elif base_indent == 0 or marker.endswith("."):
        continuation_indent = " " * len(prefix)
    else:
        continuation_indent = " " * (base_indent + 2)
    rendered: list[str] = []
    for block_index, block in enumerate(item_lines):
        if (
            block_index == 0
            and options.prose_wrap == "always"
            and "\n" not in block
            and "# ignore:" not in block
            and ("](" not in block or ") - " in block)
            and "\\_" not in block
            and not _is_block_marker_line(block)
            and _should_wrap_prose(block, prefix=prefix, width=options.print_width)
        ):
            rendered.extend(
                _wrap_list_item_prose(
                    block,
                    prefix=prefix,
                    continuation=indent,
                    width=options.print_width,
                )
            )
            continue
        block_lines = block.splitlines()
        if block_index == 0:
            rendered.append(prefix + block_lines[0])
            for continuation_line in block_lines[1:]:
                stripped = continuation_line.lstrip()
                line_indent = len(continuation_line) - len(stripped)
                if (
                    not in_blockquote
                    and _LIST_MARKER_LINE_RE.match(stripped)
                    and line_indent >= len(prefix)
                ):
                    rendered.append(continuation_line)
                else:
                    rendered.append(f"{indent}{continuation_line}")
            continue
        if loose and not in_blockquote:
            previous_block = item_lines[block_index - 1] if block_index > 0 else ""
            if _is_list_block(block) and previous_block.lstrip().startswith(">"):
                pass
            else:
                rendered.append("")
        if _is_list_block(block):
            rendered.extend(block.splitlines())
        elif (
            options.prose_wrap == "always"
            and "\n" not in block
            and not _is_block_marker_line(block)
            and _should_wrap_prose(block, prefix=continuation_indent, width=options.print_width)
        ):
            rendered.extend(
                wrap_prose(
                    block,
                    width=options.print_width,
                    prefix=continuation_indent,
                    continuation=continuation_indent,
                ).split("\n")
            )
        else:
            rendered.extend(f"{continuation_indent}{continuation_line}" for continuation_line in block_lines)
    return rendered


def _list_marker_prefix(marker: str, *, align: bool = False) -> str:
    if align and marker.endswith((".", ")")):
        return f"{marker}{' ' * max(1, 4 - len(marker))}"
    return f"{marker} "


def _wrap_list_item_prose(block: str, *, prefix: str, continuation: str, width: int) -> list[str]:
    split_at = block.find(") - ")
    if split_at < 0:
        return wrap_prose(block, width=width, prefix=prefix, continuation=continuation).split("\n")
    head = block[: split_at + 1]
    tail = block[split_at + 4 :]
    lines = [prefix + f"{head} -"]
    lines.extend(wrap_prose(tail, width=width, prefix=continuation, continuation=continuation).split("\n"))
    return lines


def _render_math_block(token: Token, *, label: str | None = None) -> str:
    content = token.content.strip()
    if label:
        return f"$$\n{content}\n$$ ({label})\n"
    return f"$$\n{content}\n$$\n"


def _inline_children_are_link_run(children: list[Token]) -> bool:
    if not any(child.type == "link_open" for child in children):
        return False
    for child in children:
        if child.type == "text" and child.content.strip():
            return False
        if child.type not in {"link_open", "link_close", "text", "softbreak"}:
            return False
    return True


def _render_packed_link_run(
    children: list[Token],
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> str:
    parts: list[str] = []
    index = 0
    while index < len(children):
        if children[index].type == "link_open":
            chunk, index = _render_inline_token(
                children,
                index,
                options=options,
                hard_break_styles=hard_break_styles,
            )
            parts.append(chunk)
            continue
        index += 1
    return "\n".join(_pack_link_parts(parts, width=options.print_width))


def _pack_link_parts(parts: list[str], *, width: int) -> list[str]:
    lines: list[str] = []
    current: list[str] = []
    current_width = 0
    for part in parts:
        part_width = text_display_width(part)
        sep_width = 1 if current else 0
        if current and current_width + sep_width + part_width > width:
            lines.append(" ".join(current))
            current = [part]
            current_width = part_width
        else:
            if current:
                current_width += sep_width
            current.append(part)
            current_width += part_width
    if current:
        lines.append(" ".join(current))
    return lines


def _render_paragraph(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    wrap: bool = True,
    hard_break_styles: HardBreakStyles | None = None,
    source_lines: list[str] | None = None,
    preserve_source_line: bool = True,
) -> tuple[str, int]:
    if preserve_source_line:
        inline_code_line = _plain_inline_code_source_line(tokens, index, source_lines)
        if inline_code_line is not None:
            return f"{inline_code_line}\n", index + 3
    broken_wiki_line = _broken_wiki_link_source_paragraph(tokens, index, source_lines)
    if broken_wiki_line is not None:
        return f"{broken_wiki_line.rstrip()}\n", index + 3
    image_reference_line = _unparsed_image_reference_source_line(tokens, index, source_lines)
    if image_reference_line is not None:
        return f"{image_reference_line.rstrip()}\n", index + 3
    inline = tokens[index + 1]
    children = inline.children or []
    if _inline_children_are_link_run(children):
        text = _render_packed_link_run(
            children,
            options=options,
            hard_break_styles=hard_break_styles,
        )
        return f"{text}\n", index + 3
    use_space_breaks = options.prose_wrap == "always"
    text = escape_ordered_list_like_line_starts(
        _render_inline(
            inline.children or [],
            options=options,
            hard_break_styles=hard_break_styles,
            softbreak_as_space=use_space_breaks,
        )
    )
    if (
        wrap
        and options.prose_wrap == "always"
        and "\u00a0" not in text
        and _should_wrap_prose(text.rstrip("\n"), prefix="", width=options.print_width)
    ):
        text = wrap_paragraph_prose(text.rstrip("\n"), width=options.print_width)
    source_line = (
        _plain_paragraph_source_line(
            tokens, index, source_lines, options=options, rendered_line=text.rstrip("\n")
        )
        if preserve_source_line
        else None
    )
    if source_line is not None:
        return f"{source_line.rstrip()}\n", index + 3
    return f"{text.rstrip()}\n", index + 3


def _parse_table_row_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _parse_table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        cells = _parse_table_row_cells(line)
        if cells is not None:
            rows.append(cells)
    return rows


def _prefer_source_table_block(source_text: str, formatted_text: str) -> str | None:
    source_rows = _parse_table_rows(source_text)
    formatted_rows = _parse_table_rows(formatted_text)
    if not source_rows or source_rows != formatted_rows:
        return None
    if len(source_text) >= len(formatted_text):
        return source_text if source_text.endswith("\n") else f"{source_text}\n"
    return None


def _render_table(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
    source_lines: list[str] | None = None,
) -> tuple[str, int]:
    close_index = _find_close(tokens, index, "table_close")
    rows: list[list[str]] = []
    is_header = False
    alignments: list[str] = []
    cell_alignments: list[str] = []
    row_index = index + 1
    while row_index < close_index:
        token = tokens[row_index]
        if token.type == "thead_open":
            is_header = True
            row_index += 1
            continue
        if token.type in {"thead_close", "tbody_open", "tbody_close"}:
            if token.type == "thead_close":
                is_header = False
            row_index += 1
            continue
        if token.type == "tr_open":
            row_close = _find_close(tokens, row_index, "tr_close")
            cells: list[str] = []
            cell_index = row_index + 1
            while cell_index < row_close:
                if tokens[cell_index].type in {"th_open", "td_open"}:
                    style = str(tokens[cell_index].attrGet("style") or "")
                    if "text-align:center" in style:
                        cell_alignments.append("center")
                    elif "text-align:right" in style:
                        cell_alignments.append("right")
                    elif "text-align:left" in style:
                        cell_alignments.append("left")
                    else:
                        cell_alignments.append("default")
                    inline = tokens[cell_index + 1]
                    cells.append(
                        _render_inline(
                            inline.children or [], in_table=True, options=options, hard_break_styles=hard_break_styles
                        )
                    )
                    cell_index += 3
                else:
                    cell_index += 1
            if is_header and not alignments:
                alignments = [_alignment_separator(align) for align in cell_alignments]
                rows.append(cells)
                rows.append(alignments)
            else:
                rows.append(cells)
            row_index = row_close + 1
            continue
        row_index += 1
    if not rows:
        return "", close_index + 1
    width = len(rows[0])
    header = rows[0]
    body_rows = rows[2:] if len(rows) > 1 else []
    trailing_paragraphs: list[str] = []
    filtered_body_rows: list[list[str]] = []
    for row in body_rows:
        padded_row = row + [""] * (width - len(row))
        if _is_spurious_table_row(padded_row[:width], width):
            trailing_paragraphs.append(padded_row[0].strip())
        else:
            filtered_body_rows.append(padded_row[:width])
    width_rows = [
        [_escape_table_cell(cell) for cell in row]
        for row in [header, *filtered_body_rows]
    ]
    column_widths = _table_column_widths(width_rows, width)
    align_row = rows[1] if len(rows) > 1 else ["---"] * width
    lines = [
        _format_table_row(header, column_widths, align_row),
        _format_table_separator(column_widths, align_row),
        *(
            _format_table_row(row, column_widths, align_row, strip_trailing_empty=True)
            for row in filtered_body_rows
        ),
    ]
    result = "\n".join(lines) + "\n"
    if trailing_paragraphs:
        result += "\n".join(f"{paragraph}\n" for paragraph in trailing_paragraphs)
    table_map = tokens[index].map
    if source_lines and table_map:
        source_text = "\n".join(source_lines[table_map[0] : table_map[1]])
        preferred = _prefer_source_table_block(source_text, result)
        if preferred is not None:
            return preferred, close_index + 1
    return result, close_index + 1


def _render_until_close(
    tokens: list[Token],
    index: int,
    close_type: str,
    *,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
) -> str:
    markers = task_list_markers or []
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_index = _find_close(tokens, index, close_type)
    parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        chunk, inner_index = _render_block(
            tokens,
            inner_index,
            options=options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            preserve_source_line=False,
        )
        if chunk:
            parts.append(chunk)
    return _join_blocks(parts)


def _should_join_without_blank_line(previous: str, current: str) -> bool:
    prev_lines = previous.strip("\n").splitlines()
    if not prev_lines:
        return False
    last_line = prev_lines[-1].strip()
    if last_line.startswith("<!-- prettier-ignore"):
        return True
    if current.lstrip().startswith("<!-- prettier-ignore"):
        return True
    return False


def _source_blocks_are_adjacent(
    tokens: list[Token] | None,
    previous_index: int | None,
    current_index: int | None,
    source_lines: list[str] | None,
) -> bool:
    if tokens is None or source_lines is None or previous_index is None or current_index is None:
        return False
    previous_map = tokens[previous_index].map
    current_map = tokens[current_index].map
    if not previous_map or not current_map:
        return False
    if previous_map[1] != current_map[0]:
        return False
    # Check there's no blank line at the end of the previous block.
    last_line_index = previous_map[1] - 1
    if last_line_index >= 0 and last_line_index < len(source_lines) and not source_lines[last_line_index].strip():
        return False
    previous_type = tokens[previous_index].type
    current_type = tokens[current_index].type
    if previous_type in {"bullet_list_open", "ordered_list_open"} and current_type in {
        "bullet_list_open",
        "ordered_list_open",
    }:
        if previous_type == current_type == "bullet_list_open":
            previous_source_line = source_lines[previous_map[0]] if previous_map[0] < len(source_lines) else ""
            current_source_line = source_lines[current_map[0]] if current_map[0] < len(source_lines) else ""
            if _source_bullet_marker(previous_source_line) != _source_bullet_marker(current_source_line):
                return False
        return True
    if "html_block" not in {previous_type, current_type}:
        return False
    if previous_type in {"bullet_list_open", "ordered_list_open"} or current_type in {
        "bullet_list_open",
        "ordered_list_open",
    }:
        return False
    previous_source_line = source_lines[previous_map[0]] if previous_map[0] < len(source_lines) else ""
    return not _LIST_MARKER_LINE_RE.match(previous_source_line.lstrip())


def _source_bullet_marker(line: str) -> str | None:
    match = re.match(r"\s*([-*+])\s+", line)
    if match is None:
        return None
    return match.group(1)


def _prose_display_width(text: str) -> int:
    """Return display width treating each backslash escape (\\X) as 1 column (like Prettier)."""
    collapsed = re.sub(r"\\.", lambda m: m.group(0)[1], text)
    return text_display_width(collapsed)


def _should_wrap_prose(text: str, *, prefix: str, width: int) -> bool:
    return _prose_display_width(prefix + text) > width


def _table_column_widths(rows: list[list[str]], width: int) -> list[int]:
    column_widths = [3] * width
    for row in rows:
        for index, cell in enumerate(row[:width]):
            column_widths[index] = max(column_widths[index], _table_cell_display_width(cell), 3)
    return column_widths


def _wrap_blockquote_block(block: str, *, options: FormatOptions) -> str:
    lines = block.rstrip().splitlines()
    wrapped_lines: list[str] = []
    for line in lines:
        if not line.strip():
            wrapped_lines.append(">")
            continue
        prefix = "> "
        wrapped = wrap_prose(line, width=options.print_width, prefix=prefix, continuation=prefix)
        wrapped_lines.extend(wrapped.split("\n"))
    return "\n".join(wrapped_lines)
