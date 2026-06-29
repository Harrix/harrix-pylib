"""Render markdown-it tokens back to Markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import unquote, urlsplit, urlunsplit

from harrix_pylib.md_format.escape_format import escape_markdown_text, escape_ordered_list_like_line_starts
from harrix_pylib.md_format.table_format import looks_like_prose_table_row, text_display_width
from harrix_pylib.md_format.text_format import normalize_inline_spaces

if TYPE_CHECKING:
    from markdown_it.token import Token


def render_tokens(tokens: list[Token]) -> str:
    """Render top-level block tokens to Markdown."""
    parts: list[str] = []
    index = 0
    while index < len(tokens):
        chunk, index = _render_block(tokens, index)
        if chunk:
            parts.append(chunk)
    return _join_blocks(parts)


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


def _format_code_inline(content: str, *, in_table: bool = False) -> str:
    if in_table and "|" in content:
        content = content.replace("|", "\\|")
    if "`" not in content:
        return f"`{content}`"
    fence = "`" * (_max_backtick_run(content) + 1)
    if content.startswith("`") or content.endswith("`"):
        return f"{fence} {content} {fence}"
    return f"{fence}{content}{fence}"


def _format_self_referential_link(href: str, inner: str) -> str | None:
    """Return angle-bracket autolink syntax for bare and self-referential URLs."""
    mailto_prefix = "mailto:"
    if href.startswith(mailto_prefix) and inner == href[len(mailto_prefix) :]:
        return f"<{inner}>"

    if inner == href and href.startswith(("http://", "https://")):
        return f"<{href}>"

    if href.startswith(("http://", "https://")):
        href_without_scheme = href.removeprefix("https://").removeprefix("http://").rstrip("/")
        if inner.rstrip("/") == href_without_scheme:
            return f"<{inner}>"

    return None


def _format_table_row(cells: list[str], column_widths: list[int]) -> str:
    padded = cells + [""] * (len(column_widths) - len(cells))
    return (
        "| "
        + " | ".join(
            f"{padded[index]}{' ' * (column_widths[index] - text_display_width(padded[index]))}"
            for index in range(len(column_widths))
        )
        + " |"
    )


def _format_table_separator(column_widths: list[int]) -> str:
    return "| " + " | ".join("-" * width for width in column_widths) + " |"


def _is_spurious_table_row(cells: list[str], width: int) -> bool:
    min_spurious_width = 3
    if width < min_spurious_width or not cells[0].strip():
        return False
    if any(cells[index].strip() for index in range(1, width)):
        return False
    return looks_like_prose_table_row(cells[0].strip())


def _join_blocks(parts: list[str]) -> str:
    cleaned = [part.strip("\n") for part in parts if part.strip()]
    if not cleaned:
        return ""
    return "\n\n".join(cleaned) + "\n"


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
    item_index = index + 1
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        if _list_item_is_loose(tokens, item_index, item_close):
            return True
        item_index = item_close + 1
    return False


def _list_item_is_loose(tokens: list[Token], item_open_index: int, item_close_index: int) -> bool:
    paragraph_count = 0
    nested_list_count = 0
    child_index = item_open_index + 1
    while child_index < item_close_index:
        token = tokens[child_index]
        if token.type == "paragraph_open":
            paragraph_count += 1
            child_index += 3
            continue
        if token.type in {"bullet_list_open", "ordered_list_open"}:
            nested_list_count += 1
            child_index = (
                _find_close(
                    tokens,
                    child_index,
                    "ordered_list_close" if token.type == "ordered_list_open" else "bullet_list_close",
                )
                + 1
            )
            continue
        if token.type in {
            "fence",
            "code_block",
            "blockquote_open",
            "table_open",
            "heading_open",
            "html_block",
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
    if not href or "%" not in href:
        return href
    if href.startswith("#"):
        return unquote(href, encoding="utf-8")
    parts = urlsplit(href)
    if not parts.scheme and not parts.netloc:
        return unquote(href, encoding="utf-8")
    decoded_fragment = unquote(parts.fragment, encoding="utf-8") if parts.fragment else parts.fragment
    decoded_path = unquote(parts.path, encoding="utf-8")
    return urlunsplit((parts.scheme, parts.netloc, decoded_path, parts.query, decoded_fragment))


def _render_block(tokens: list[Token], index: int) -> tuple[str, int]:
    token = tokens[index]
    if token.type == "heading_open":
        return _render_heading(tokens, index)
    if token.type == "paragraph_open":
        return _render_paragraph(tokens, index)
    if token.type == "blockquote_open":
        return _render_blockquote(tokens, index)
    if token.type == "bullet_list_open":
        return _render_list(tokens, index, ordered=False)
    if token.type == "ordered_list_open":
        return _render_list(tokens, index, ordered=True)
    if token.type == "fence":
        return _render_fence(token), index + 1
    if token.type == "code_block":
        return f"    {token.content.rstrip()}\n", index + 1
    if token.type == "hr":
        return "---\n", index + 1
    if token.type == "math_block":
        return _render_math_block(token), index + 1
    if token.type == "math_block_label":
        return _render_math_block(token, label=token.info), index + 1
    if token.type == "table_open":
        return _render_table(tokens, index)
    if token.type == "html_block":
        return f"{token.content.rstrip()}\n", index + 1
    if token.type in {"dl_open", "dt_open", "dd_open"}:
        return _render_until_close(tokens, index, token.type.replace("_open", "_close")), index + 1
    return "", index + 1


def _render_blockquote(tokens: list[Token], index: int) -> tuple[str, int]:
    close_index = _find_close(tokens, index, "blockquote_close")
    inner_parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        chunk, inner_index = _render_block(tokens, inner_index)
        if chunk:
            inner_parts.append(chunk)
    quoted_blocks: list[str] = []
    for block in inner_parts:
        quoted_lines: list[str] = []
        for raw_line in block.rstrip().splitlines():
            line = escape_ordered_list_like_line_starts(raw_line) if raw_line else raw_line
            quoted_lines.append(f"> {line}" if line else ">")
        quoted_blocks.append("\n".join(quoted_lines))
    quoted = "\n>\n".join(quoted_blocks)
    return quoted + "\n", close_index + 1


def _render_fence(token: Token) -> str:
    info = (token.info or "").strip()
    fence = "```"
    content = token.content.strip("\n")
    return f"{fence}{info}\n{content}\n{fence}\n"


def _render_heading(tokens: list[Token], index: int) -> tuple[str, int]:
    level = int(tokens[index].tag[1])
    inline = tokens[index + 1]
    text = _render_inline(inline.children or [])
    return f"{'#' * level} {text}\n", index + 3


def _render_inline(children: list[Token], *, in_table: bool = False) -> str:
    parts: list[str] = []
    index = 0
    while index < len(children):
        chunk, index = _render_inline_token(children, index, in_table=in_table)
        parts.append(chunk)
    return "".join(parts)


def _render_inline_token(children: list[Token], index: int, *, in_table: bool = False) -> tuple[str, int]:
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
        return escape_markdown_text(content), index + 1
    if child.type == "code_inline":
        return _format_code_inline(child.content, in_table=in_table), index + 1
    if child.type == "softbreak":
        return "\n", index + 1
    if child.type == "hardbreak":
        return "\\\n", index + 1
    if child.type == "wiki_link":
        return f"[[{child.content}]]", index + 1
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
            return f'![{alt}]({src} "{title}")', index + 1
        return f"![{alt}]({src})", index + 1
    if child.type == "link_open":
        href = _readable_link_href(str(child.attrGet("href") or ""))
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
            chunk, inner_index = _render_inline_token(children, inner_index, in_table=in_table)
            inner_parts.append(chunk)
        inner = "".join(inner_parts)
        if title:
            return f'[{inner}]({href} "{title}")', next_index
        return f"[{inner}]({href})", next_index
    if child.type == "link_close":
        return "", index + 1
    if child.type == "strong_open":
        inner, next_index = _render_inline_until(children, index + 1, "strong_close", in_table=in_table)
        return f"**{inner}**", next_index + 1
    if child.type == "em_open":
        inner, next_index = _render_inline_until(children, index + 1, "em_close", in_table=in_table)
        return f"_{inner}_", next_index + 1
    if child.type == "s_open":
        inner, next_index = _render_inline_until(children, index + 1, "s_close", in_table=in_table)
        return f"~~{inner}~~", next_index + 1
    if child.type in {"strong_close", "em_close", "s_close"}:
        return "", index + 1
    return child.content or "", index + 1


def _render_inline_until(
    children: list[Token], index: int, close_type: str, *, in_table: bool = False
) -> tuple[str, int]:
    parts: list[str] = []
    while index < len(children) and children[index].type != close_type:
        chunk, index = _render_inline_token(children, index, in_table=in_table)
        parts.append(chunk)
    return "".join(parts), index


def _render_list(tokens: list[Token], index: int, *, ordered: bool) -> tuple[str, int]:
    close_type = "ordered_list_close" if ordered else "bullet_list_close"
    close_index = _find_close(tokens, index, close_type)
    loose = _list_is_loose(tokens, index, close_index)
    lines: list[str] = []
    item_number = int(tokens[index].attrGet("start") or 1)
    item_index = index + 1
    rendered_item_count = 0
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        marker = f"{item_number}." if ordered else "-"
        item_lines: list[str] = []
        child_index = item_index + 1
        while child_index < item_close:
            if tokens[child_index].type in {"bullet_list_open", "ordered_list_open"}:
                nested, child_index = _render_list(
                    tokens,
                    child_index,
                    ordered=tokens[child_index].type == "ordered_list_open",
                )
                item_lines.append(nested.rstrip("\n"))
            else:
                chunk, child_index = _render_block(tokens, child_index)
                if chunk:
                    item_lines.append(chunk.rstrip("\n"))
        if loose and rendered_item_count > 0:
            lines.append("")
        item_loose = _list_item_is_loose(tokens, item_index, item_close)
        lines.extend(_render_list_item_lines(item_lines, marker=marker, loose=item_loose))
        item_number += 1
        rendered_item_count += 1
        item_index = item_close + 1
    return "\n".join(lines) + "\n", close_index + 1


def _render_list_item_lines(
    item_lines: list[str],
    *,
    marker: str,
    loose: bool,
) -> list[str]:
    if not item_lines:
        return [f"{marker} "]

    prefix = f"{marker} "
    indent = " " * len(prefix)
    rendered: list[str] = []
    for block_index, block in enumerate(item_lines):
        block_lines = block.splitlines()
        if block_index == 0:
            rendered.append(prefix + block_lines[0])
            rendered.extend(f"{indent}{continuation_line}" for continuation_line in block_lines[1:])
            continue
        if loose:
            rendered.append("")
        rendered.extend(f"{indent}{continuation_line}" for continuation_line in block_lines)
    return rendered


def _render_math_block(token: Token, *, label: str | None = None) -> str:
    content = token.content.strip()
    if label:
        return f"$$\n{content}\n$$ ({label})\n"
    return f"$$\n{content}\n$$\n"


def _render_paragraph(tokens: list[Token], index: int) -> tuple[str, int]:
    inline = tokens[index + 1]
    text = escape_ordered_list_like_line_starts(_render_inline(inline.children or []))
    return f"{text}\n", index + 3


def _render_table(tokens: list[Token], index: int) -> tuple[str, int]:
    close_index = _find_close(tokens, index, "table_close")
    rows: list[list[str]] = []
    is_header = False
    alignments: list[str] = []
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
                    inline = tokens[cell_index + 1]
                    cells.append(_render_inline(inline.children or [], in_table=True))
                    cell_index += 3
                else:
                    cell_index += 1
            if is_header and not alignments:
                alignments = ["---"] * len(cells)
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
    column_widths = _table_column_widths([header, *filtered_body_rows], width)
    lines = [
        _format_table_row(header, column_widths),
        _format_table_separator(column_widths),
        *(_format_table_row(row, column_widths) for row in filtered_body_rows),
    ]
    result = "\n".join(lines) + "\n"
    if trailing_paragraphs:
        result += "\n".join(f"{paragraph}\n" for paragraph in trailing_paragraphs)
    return result, close_index + 1


def _render_until_close(tokens: list[Token], index: int, close_type: str) -> str:
    close_index = _find_close(tokens, index, close_type)
    parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        chunk, inner_index = _render_block(tokens, inner_index)
        if chunk:
            parts.append(chunk)
    return _join_blocks(parts)


def _table_column_widths(rows: list[list[str]], width: int) -> list[int]:
    column_widths = [3] * width
    for row in rows:
        for index, cell in enumerate(row[:width]):
            column_widths[index] = max(column_widths[index], text_display_width(cell), 3)
    return column_widths
