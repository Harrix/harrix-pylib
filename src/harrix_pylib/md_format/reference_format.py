"""Preserve and format link-reference and footnote definition lines."""

from __future__ import annotations

import re
from dataclasses import dataclass

from harrix_pylib.md_format.link_title_format import _canonicalize_link_title_content, format_link_title
from harrix_pylib.md_format.options import DEFAULT_PRINT_WIDTH, FormatOptions
from harrix_pylib.md_format.prose_wrap import wrap_prose
from harrix_pylib.md_format.table_format import text_display_width

PLACEHOLDER_PREFIX = "HSKMDFMTREF"
_PLACEHOLDER_RE = re.compile(r"HSKMDFMTREF\d+")
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
        if result and result[-1].startswith(PLACEHOLDER_PREFIX) and not result[-1].endswith("\n"):
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
    for line in lines:
        if not _PLACEHOLDER_RE.search(line):
            restored.append(line)
            continue
        last = 0
        for match in _PLACEHOLDER_RE.finditer(line):
            if match.start() > last:
                gap = line[last : match.start()]
                if gap.strip():
                    restored.append(gap)
            block_index = int(match.group().removeprefix(PLACEHOLDER_PREFIX))
            block = blocks_by_index.get(block_index)
            if block is None:
                restored.append(match.group())
            else:
                restored.extend(_format_reference_block(block, options=fmt_options, print_width=width))
            last = match.end()
        if last < len(line):
            restored.append(line[last:])
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
    wrapped = wrap_prose(body, width=print_width, prefix=prefix, continuation=continuation)
    return wrapped.split("\n")


def _format_reference_title(title: str) -> str:
    if title.startswith("(") and title.endswith(")"):
        inner = _unescape_reference_title(title)
        if " " in inner:
            return f"({inner})"
    return format_link_title(_canonicalize_reference_title(title))


def _canonicalize_reference_title(title: str) -> str:
    return _canonicalize_link_title_content(_unescape_reference_title(title))


def _format_link_definition(line: str, *, print_width: int) -> list[str]:
    match = _LINK_DEF_RE.match(line)
    if not match:
        return [line]
    indent, label, rest = match.group(1), match.group(2), match.group(3).rstrip()
    url, title = _split_link_definition_rest(rest)
    label_prefix = f"{indent}[{label}]: "
    continuation = indent + "  "
    if title is None:
        body = url
    else:
        body = f"{url} {_format_reference_title(title)}"
    if text_display_width(label_prefix + body) <= print_width:
        if title is None:
            return [f"{label_prefix}{url}"]
        return [f"{label_prefix}{url} {_format_reference_title(title)}"]
    lines = [f"{indent}[{label}]:"]
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


def _unescape_reference_title(quoted: str) -> str:
    if not quoted:
        return quoted
    if quoted[0] == "(" and quoted.endswith(")"):
        inner = quoted[1:-1]
    elif len(quoted) >= 2 and quoted[0] == quoted[-1] and quoted[0] in {'"', "'"}:
        inner = quoted[1:-1]
    else:
        return quoted
    result: list[str] = []
    index = 0
    while index < len(inner):
        char = inner[index]
        if char == "\\" and index + 1 < len(inner):
            result.append(inner[index + 1])
            index += 2
            continue
        result.append(char)
        index += 1
    return "".join(result)


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
    title_match = re.search(
        r'\s+("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\((?:\\.|[^)\\])*\))\s*$',
        rest,
    )
    if title_match:
        title = title_match.group(1)
        if title in {'""', "''"}:
            return rest[: title_match.start()].rstrip(), None
        return rest[: title_match.start()].rstrip(), title
    return rest, None
