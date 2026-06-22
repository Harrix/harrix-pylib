"""YAML front matter handling."""

from __future__ import annotations

_MIN_FRONT_MATTER_PARTS = 3


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
