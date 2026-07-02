"""Printer submodule: inline."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import unquote, urlsplit, urlunsplit

from harrix_pylib.md_format.escape_format import escape_markdown_text
from harrix_pylib.md_format.hard_break_format import HardBreakStyles
from harrix_pylib.md_format.link_destination_format import (
    formatted_href_from_placeholder,
    formatted_title_from_placeholder,
)
from harrix_pylib.md_format.link_title_format import format_link_title
from harrix_pylib.md_format.options import FormatOptions
from harrix_pylib.md_format.printer import context as printer_context
from harrix_pylib.md_format.printer.context import (
    DEFAULT_OPTIONS,
)
from harrix_pylib.md_format.prose_wrap import (
    _softbreak_prefers_newline,
    should_omit_space_between,
)
from harrix_pylib.md_format.table_format import text_display_width
from harrix_pylib.md_format.text_format import normalize_inline_spaces

if TYPE_CHECKING:
    from markdown_it.token import Token

from harrix_pylib.md_format.printer.tokens import _choose_emphasis_delimiter, _contains_strong, _link_raw_text


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


def _inline_children_are_link_run(children: list[Token]) -> bool:
    if not any(child.type == "link_open" for child in children):
        return False
    for child in children:
        if child.type == "text" and child.content.strip():
            return False
        if child.type not in {"link_open", "link_close", "text", "softbreak"}:
            return False
    return True


def _inline_neighbor_text(children: list[Token], open_index: int, close_index: int) -> tuple[str, str]:
    prev = ""
    if open_index > 0 and children[open_index - 1].type == "text":
        prev = children[open_index - 1].content
    next_text = ""
    if close_index + 1 < len(children) and children[close_index + 1].type == "text":
        next_text = children[close_index + 1].content
    return prev, next_text


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


def _readable_link_href(href: str) -> str:
    """Decode percent-encoded Unicode in URLs for readable Markdown output."""
    if printer_context.ACTIVE_LINK_DESTINATIONS is not None:
        formatted = formatted_href_from_placeholder(href, printer_context.ACTIVE_LINK_DESTINATIONS)
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


def _render_inline(
    children: list[Token],
    *,
    in_table: bool = False,
    options: FormatOptions | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    softbreak_as_space: bool = False,
) -> str:
    fmt_options = options or DEFAULT_OPTIONS
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


def _render_inline_token(
    children: list[Token],
    index: int,
    *,
    in_table: bool = False,
    options: FormatOptions | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    softbreak_as_space: bool = False,
) -> tuple[str, int]:
    fmt_options = options or DEFAULT_OPTIONS
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
        if content.endswith("\\") and index + 1 < len(children) and children[index + 1].type == "softbreak":
            rendered += "\\"
        return rendered, index + 1
    if child.type == "code_inline":
        return _format_code_inline(child.content, in_table=in_table), index + 1
    if child.type == "softbreak":
        if softbreak_as_space and not _softbreak_follows_trailing_backslash(children, index):
            if _softbreak_should_omit_space(children, index):
                return "", index + 1
            prev_child = children[index - 1] if index > 0 else None
            next_child = children[index + 1] if index + 1 < len(children) else None
            if (
                prev_child is not None
                and next_child is not None
                and prev_child.type == "text"
                and next_child.type == "text"
                and _softbreak_prefers_newline(prev_child.content, next_child.content)
            ):
                return "\n", index + 1
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
            formatted_title_from_placeholder(raw_href, printer_context.ACTIVE_LINK_DESTINATIONS)
            if printer_context.ACTIVE_LINK_DESTINATIONS is not None
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
    fmt_options = options or DEFAULT_OPTIONS
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


def _render_wiki_content(content: str) -> str:
    """Normalize inline emphasis inside wiki-link content without re-escaping."""
    return _WIKI_TRIPLE_EMPHASIS_RE.sub(lambda m: f"_**{m.group(1)}**_", content)


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


def _softbreak_should_omit_space(children: list[Token], index: int) -> bool:
    before = _inline_text_before(children, index)
    after = _inline_text_after(children, index)
    if not before or not after:
        return False
    return should_omit_space_between(before, after)


_WIKI_TRIPLE_EMPHASIS_RE = re.compile(r"\*\*\*(.+?)\*\*\*")
