"""YAML front matter handling."""

from __future__ import annotations

import re
from dataclasses import dataclass

_MIN_FRONT_MATTER_PARTS = 3
_YAML_BLOCK_PREFIX = "HSKMDFMTYAML"
_YAML_BLOCK_RE = re.compile(rf"{_YAML_BLOCK_PREFIX}\d+")


@dataclass(frozen=True)
class YamlBlock:
    """Stored YAML block from the markdown body."""

    index: int
    lines: list[str]


def collapse_extra_blank_lines(text: str) -> str:
    """Collapse consecutive blank lines to a single blank line."""
    lines = text.split("\n")
    collapsed: list[str] = []
    for line in lines:
        if line == "":
            if collapsed and collapsed[-1] != "":
                collapsed.append("")
            continue
        collapsed.append(line)
    return "\n".join(collapsed)


def compact_front_matter(front_matter: str) -> str:
    """Remove blank lines inside YAML front matter while keeping delimiters."""
    parts = front_matter.split("---", 2)
    if len(parts) < _MIN_FRONT_MATTER_PARTS:
        return front_matter
    yaml_lines = [line for line in parts[1].splitlines() if line.strip()]
    if not yaml_lines:
        return front_matter
    yaml_body = "\n".join(yaml_lines)
    return f"---\n{yaml_body}\n---"


def extract_yaml_blocks(body: str) -> tuple[str, list[YamlBlock]]:
    """Replace standalone YAML blocks in the markdown body with placeholders."""
    lines, trailing = _split_lines(body)
    result: list[str] = []
    blocks: list[YamlBlock] = []
    index = 0
    line_index = 0

    while line_index < len(lines):
        if lines[line_index].strip() != "---":
            result.append(lines[line_index])
            line_index += 1
            continue

        close_index = _find_yaml_block_close(lines, line_index + 1)
        if close_index is None:
            result.append(lines[line_index])
            line_index += 1
            continue

        block_lines = lines[line_index : close_index + 1]
        blocks.append(YamlBlock(index=index, lines=block_lines))
        result.append(f"{_YAML_BLOCK_PREFIX}{index}")
        index += 1
        line_index = close_index + 1

    return _join_lines(result, trailing_newline=trailing), blocks


def restore_yaml_blocks(text: str, blocks: list[YamlBlock]) -> str:
    """Restore YAML body blocks."""
    if not blocks:
        return text
    blocks_by_index = {block.index: block for block in blocks}

    def replace(match: re.Match[str]) -> str:
        block_index = int(match.group().removeprefix(_YAML_BLOCK_PREFIX))
        block = blocks_by_index.get(block_index)
        if block is None:
            return match.group()
        return _format_yaml_block(block)

    return _YAML_BLOCK_RE.sub(replace, text)


def join_front_matter(front_matter: str, body: str) -> str:
    """Join front matter and formatted body."""
    if not front_matter:
        return body
    body = body.lstrip("\n")
    if body:
        return f"{front_matter.rstrip()}\n\n{body}"
    return f"{front_matter.rstrip()}\n"


def prepend_markdown_header(header: str, markdown_text: str) -> str:
    """Prepend YAML or Markdown prefix without duplicating existing front matter."""
    _, body = split_front_matter(markdown_text)
    header = header.rstrip("\n")
    if not header:
        return body or markdown_text
    if not body:
        return f"{header}\n"
    return f"{header}\n\n{body}"


def split_front_matter(markdown_text: str) -> tuple[str, str]:
    """Split YAML front matter from Markdown body.

    Returns front matter including `---` delimiters and the remaining body.
    """
    markdown_text = markdown_text.lstrip("\ufeff")
    if not markdown_text.startswith("---"):
        return "", markdown_text
    parts = markdown_text.split("---", 2)
    if len(parts) < _MIN_FRONT_MATTER_PARTS:
        return "", markdown_text
    return f"---{parts[1]}---", parts[2].lstrip()


def _find_yaml_block_close(lines: list[str], start_index: int) -> int | None:
    for line_index in range(start_index, len(lines)):
        if lines[line_index].strip() == "---":
            return line_index
        if lines[line_index].strip() == "":
            return None
    return None


def _format_yaml_block(block: YamlBlock) -> str:
    inner = [_format_yaml_line(line) for line in block.lines[1:-1] if line.strip()]
    if not inner:
        return "---\n---"
    return "---\n" + "\n".join(inner) + "\n---"


def _format_yaml_line(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("-"):
        stripped = re.sub(r"^-\s+", "- ", stripped)
    return re.sub(r":\s+", ": ", stripped)


def _join_lines(lines: list[str], *, trailing_newline: bool) -> str:
    text = "\n".join(lines)
    if trailing_newline:
        text += "\n"
    return text


def _split_lines(text: str) -> tuple[list[str], bool]:
    has_trailing_newline = text.endswith("\n")
    lines = text.split("\n")
    if has_trailing_newline and lines:
        lines.pop()
    return lines, has_trailing_newline


def trim_trailing_blank_lines(text: str) -> str:
    """Remove trailing blank lines while keeping a single final newline."""
    lines = text.split("\n")
    has_trailing_newline = text.endswith("\n")
    if has_trailing_newline and lines:
        lines.pop()
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return "\n"
    return "\n".join(lines) + "\n"
