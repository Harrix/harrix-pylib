"""Preserve and format link-reference and footnote definition lines."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from harrix_pylib.md_format.link_title_format import (
    _canonicalize_link_title_content,
    _split_trailing_link_title,
    _unescape_title,
    format_link_title,
)
from harrix_pylib.md_format.options import DEFAULT_PRINT_WIDTH, FormatOptions
from harrix_pylib.md_format.prose_wrap import wrap_prose
from harrix_pylib.md_format.table_format import text_display_width

PLACEHOLDER_PREFIX = "HSKMDFMTREF"
_PLACEHOLDER_RE = re.compile(r"HSKMDFMTREF\d+")
_URL_RE = re.compile(r"https?://\S+")
_LINK_DEF_RE = re.compile(r"^(\s*)\[([^\]]+)\]:\s*(.*)$")
_FOOTNOTE_DEF_RE = re.compile(r"^(\s*)\[\^([^\]]+)\]:\s*(.*)$")


@dataclass(frozen=True)
class ReferenceBlock:
    """Stored reference-definition block."""

    index: int
    lines: list[str]
    kind: str  # "link" or "footnote"


def extract_reference_blocks(body: str) -> tuple[str, list[ReferenceBlock]]:
    """Replace link/footnote definitions with placeholders."""
    lines, trailing = _split_lines(body)
    result: list[str] = []
    blocks: list[ReferenceBlock] = []
    index = 0
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        link_match = _LINK_DEF_RE.match(line)
        footnote_match = _FOOTNOTE_DEF_RE.match(line)
        if not link_match and not footnote_match:
            result.append(line)
            line_index += 1
            continue

        kind = "footnote" if footnote_match else "link"
        block_lines = [line]
        line_index += 1
        while line_index < len(lines):
            next_line = lines[line_index]
            if not next_line.strip():
                break
            if _LINK_DEF_RE.match(next_line) or _FOOTNOTE_DEF_RE.match(next_line):
                break
            if kind == "footnote" and next_line.startswith("    "):
                block_lines.append(next_line)
                line_index += 1
                continue
            break

        blocks.append(ReferenceBlock(index=index, lines=block_lines, kind=kind))
        placeholder = _placeholder(index)
        previous_line = result[-1] if result else ""
        if (
            result
            and PLACEHOLDER_PREFIX not in previous_line
            and not _LINK_DEF_RE.match(previous_line)
            and not _FOOTNOTE_DEF_RE.match(previous_line)
        ):
            result[-1] = f"{result[-1]} {placeholder}"
        else:
            result.append(placeholder)
        index += 1
        if line_index < len(lines) and not lines[line_index].strip():
            next_index = line_index + 1
            if next_index < len(lines):
                next_line = lines[next_index]
                if _LINK_DEF_RE.match(next_line) or _FOOTNOTE_DEF_RE.match(next_line):
                    line_index += 1

    return _join_lines(result, trailing_newline=trailing), blocks


def restore_reference_blocks(
    text: str,
    blocks: list[ReferenceBlock],
    *,
    options: FormatOptions | None = None,
    print_width: int | None = None,
) -> str:
    """Restore reference-definition blocks, optionally applying prose wrap."""
    fmt_options = options or FormatOptions()
    width = print_width if print_width is not None else fmt_options.print_width
    if not blocks:
        return text
    blocks_by_index = {block.index: block for block in blocks}
    lines, trailing = _split_lines(text)
    restored: list[str] = []
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        if not _PLACEHOLDER_RE.search(line):
            restored.append(line)
            line_index += 1
            continue

        merged_line = line
        while line_index + 1 < len(lines):
            next_line = lines[line_index + 1]
            if not _PLACEHOLDER_RE.search(next_line):
                break
            next_match = _PLACEHOLDER_RE.search(next_line)
            if next_match is None or next_match.start() > 0:
                break
            if _PLACEHOLDER_RE.sub("", next_line).strip():
                break
            merged_line = f"{merged_line} {next_line.strip()}"
            line_index += 1

        first_match = _PLACEHOLDER_RE.search(merged_line)
        if first_match and first_match.start() > 0:
            restored.extend(_restore_inline_reference_line(merged_line, blocks_by_index, print_width=width))
            line_index += 1
            continue

        emitted_block = False
        for match in _PLACEHOLDER_RE.finditer(merged_line):
            block_index = int(match.group().removeprefix(PLACEHOLDER_PREFIX))
            block = blocks_by_index.get(block_index)
            if block is None:
                restored.append(match.group())
            else:
                if emitted_block and block.kind == "footnote":
                    restored.append("")
                restored.extend(_format_reference_block(block, options=fmt_options, print_width=width))
                emitted_block = True
        line_index += 1
    return _join_lines(restored, trailing_newline=trailing)


def _format_footnote_block(lines: list[str], *, print_width: int) -> list[str]:
    first = lines[0]
    match = _FOOTNOTE_DEF_RE.match(first)
    if not match:
        return lines
    indent, label, first_text = match.group(1), match.group(2), match.group(3)
    prefix = f"{indent}[^{label}]: "
    continuation = indent + "    "
    body_parts = [first_text, *[line[4:] if line.startswith("    ") else line for line in lines[1:]]]
    body = " ".join(part.strip() for part in body_parts if part.strip())
    wrapped_inline = wrap_prose(body, width=print_width, prefix=prefix, continuation=continuation).split("\n")
    if len(wrapped_inline) == 1:
        return wrapped_inline
    wrapped_body = wrap_prose(body, width=print_width, prefix=continuation, continuation=continuation)
    return [prefix.rstrip(), *wrapped_body.split("\n")]


def _format_reference_title(title: str) -> str:
    unescaped = _unescape_title(title)
    if title.startswith("(") and title.endswith(")"):
        if " " in unescaped:
            return f"({unescaped})"
        return format_link_title(unescaped)
    return format_link_title(unescaped)


def _canonicalize_reference_title(title: str) -> str:
    return _canonicalize_link_title_content(_unescape_title(title))


def format_reference_link_url(url: str) -> str:
    """Return canonical URL text for link-reference definitions."""
    return url.replace("&amp;", "&")


def _reference_label_markup(label: str) -> str:
    normalized = _normalize_reference_label(label)
    if " " in normalized:
        return f"[ {normalized} ]"
    return f"[{normalized}]"


def _format_link_definition(line: str, *, print_width: int) -> list[str]:
    match = _LINK_DEF_RE.match(line)
    if not match:
        return [line]
    indent, label, rest = match.group(1), match.group(2), match.group(3).rstrip()
    url, title = _split_link_definition_rest(rest)
    url = format_reference_link_url(url)
    label_prefix = f"{indent}{_reference_label_markup(label)}: "
    continuation = indent + "  "
    if title is None:
        body = url
    else:
        body = f"{url} {_format_reference_title(title)}"
    if text_display_width(label_prefix + body) <= print_width:
        if title is None:
            return [f"{label_prefix}{url}"]
        return [f"{label_prefix}{url} {_format_reference_title(title)}"]
    lines = [f"{indent}{_reference_label_markup(label)}:"]
    lines.extend(wrap_prose(url, width=print_width, prefix=continuation, continuation=continuation).split("\n"))
    if title is not None:
        lines.extend(
            wrap_prose(
                _format_reference_title(title),
                width=print_width,
                prefix=continuation,
                continuation=continuation,
            ).split("\n")
        )
    return lines


def _format_reference_block(
    block: ReferenceBlock, *, options: FormatOptions, print_width: int = DEFAULT_PRINT_WIDTH
) -> list[str]:
    if options.prose_wrap != "always":
        return list(block.lines)
    if block.kind == "footnote":
        return _format_footnote_block(block.lines, print_width=print_width)
    formatted: list[str] = []
    for line in block.lines:
        formatted.extend(_format_link_definition(line, print_width=print_width))
    return formatted


def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


def _placeholder(index: int) -> str:
    return f"{PLACEHOLDER_PREFIX}{index}"


def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline


def _split_link_definition_rest(rest: str) -> tuple[str, str | None]:
    rest = rest.strip()
    if rest.endswith(' ""') or rest.endswith(" ''"):
        return rest[:-3].rstrip(), None
    if len(rest) >= 2 and rest.startswith("<") and rest.endswith(">"):
        return rest, None
    url, title = _split_trailing_link_title(rest)
    if title is not None:
        if title in {'""', "''"}:
            return url, None
        return url, title
    return rest, None


def _normalize_reference_label(label: str) -> str:
    return " ".join(label.split())


def _format_inline_reference_part(line: str) -> str:
    match = _LINK_DEF_RE.match(line)
    if not match:
        return line
    label = _normalize_reference_label(match.group(2))
    url, title = _split_link_definition_rest(match.group(3).rstrip())
    url = format_reference_link_url(url)
    if title is None:
        return f"[{label}]: {url}"
    return f"[{label}]: {url} {_format_reference_title(title)}"


def _restore_inline_reference_line(
    line: str, blocks_by_index: dict[int, ReferenceBlock], *, print_width: int
) -> list[str]:
    ref_parts: list[str] = []
    first_match = _PLACEHOLDER_RE.search(line)
    prefix = line[: first_match.start()].rstrip() if first_match else ""
    for match in _PLACEHOLDER_RE.finditer(line):
        block_index = int(match.group().removeprefix(PLACEHOLDER_PREFIX))
        block = blocks_by_index.get(block_index)
        if block is None:
            continue
        ref_parts.append(_format_inline_reference_part(block.lines[0]))
    body = " ".join(ref_parts)
    if not prefix:
        return _wrap_inline_reference_body(body, width=print_width)
    wrapped = _wrap_inline_reference_body(f"{prefix} {body}", width=print_width)
    return wrapped


def _wrap_inline_reference_body(text: str, *, width: int) -> list[str]:
    match = re.match(r"^(?P<prefix>.*?)(?P<refs>(?:\[[^\]]+\]: https?://\S+\s*)+)$", text)
    if match is None:
        return _wrap_protected_urls(text, width=width)
    prefix = match.group("prefix").rstrip()
    ref_parts = re.findall(r"(\[[^\]]+\]:) (https?://\S+)", match.group("refs"))
    if not ref_parts:
        return [text.rstrip()]

    labels = [label for label, _ in ref_parts]
    urls = [url for _, url in ref_parts]
    lines: list[str] = []
    url_index = 0
    if prefix:
        lines.append(f"{prefix} {labels[0]}".rstrip())
        url_index = 0

    while url_index < len(urls):
        current = urls[url_index]
        next_label_index = url_index + 1
        while next_label_index < len(urls):
            trial = f"{current} {labels[next_label_index]} {urls[next_label_index]}"
            if text_display_width(trial) <= width:
                current = trial
                next_label_index += 1
            else:
                break
        if next_label_index < len(urls):
            trial = f"{current} {labels[next_label_index]}"
            if text_display_width(trial) <= width:
                lines.append(trial)
                url_index = next_label_index
                continue
        lines.append(current)
        url_index = next_label_index
    return lines


def _wrap_protected_urls(text: str, *, width: int) -> list[str]:
    protected_urls: list[str] = []

    def protect_url(match: re.Match[str]) -> str:
        protected_urls.append(match.group(0))
        return f"\x00URL{len(protected_urls) - 1}\x00"

    protected = _URL_RE.sub(protect_url, text)
    wrapped = wrap_prose(protected, width=width)
    for index, url in enumerate(protected_urls):
        wrapped = wrapped.replace(f"\x00URL{index}\x00", url)
    return wrapped.split("\n")

