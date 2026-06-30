"""Prose wrapping for Markdown output."""

from __future__ import annotations

import re
import unicodedata

from harrix_pylib.md_format.table_format import text_display_width

_INLINE_SEGMENT_RE = re.compile(
    r"(`+[^`]*`+)"
    r"|(\[[^\]]*\]\([^)]*\))"
    r"|(!\[[^\]]*\]\([^)]*\))"
    r"|(<[^>\n]+>)"
    r"|(\*\*[^*]+\*\*)"
    r"|(_[^_]+_)"
    r"|(~~[^~]+~~)"
    r"|(\\\n)"
    r"|([ \t]+)"
    r"|([^\s`\[!<>_*\\~]+)"
)


def wrap_prose(text: str, *, width: int, prefix: str = "", continuation: str | None = None) -> str:
    """Wrap phrasing Markdown text to the given display width."""
    if not text or width <= 0:
        return text
    continuation = continuation if continuation is not None else prefix
    lines = _wrap_text_lines(text, width=width, first_prefix=prefix, next_prefix=continuation)
    return "\n".join(lines)


def wrap_paragraph_prose(text: str, *, width: int) -> str:
    """Wrap paragraph text, preserving hard breaks and backslash-only lead lines."""
    if not text or width <= 0:
        return text
    if text.startswith("\\") and "\n" in text:
        lead, _, rest = text.partition("\n")
        if lead and set(lead) <= {"\\"}:
            wrapped_rest = wrap_prose(rest.lstrip(), width=width) if rest.strip() else rest
            return f"{lead}\n{wrapped_rest}" if wrapped_rest else lead
    hard_break = "  \n"
    if hard_break not in text:
        return wrap_prose(text, width=width)
    head, tail = text.split(hard_break, 1)
    wrapped_tail = _wrap_prose_after_hard_break(tail.lstrip(), width=width)
    return f"{head}{hard_break}{wrapped_tail}"


def _wrap_prose_after_hard_break(text: str, *, width: int) -> str:
    words = re.findall(r"\S+", text)
    if not words:
        return text
    lines: list[str] = []
    current: list[str] = []
    current_width = 0
    first_line = True

    for word in words:
        word_width = text_display_width(word)
        gap = 1 if current else 0
        if (
            current
            and current_width + gap + word_width > width
            and first_line
            and word_width <= width
        ):
            current.append(word)
            lines.append(" ".join(current))
            current = []
            current_width = 0
            first_line = False
            continue
        if current and current_width + gap + word_width > width and not first_line:
            lines.append(" ".join(current))
            current = [word]
            current_width = word_width
            continue
        if current:
            current.append(word)
            current_width += gap + word_width
        else:
            current = [word]
            current_width = word_width

    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def _is_cjk(char: str) -> bool:
    if not char:
        return False
    if unicodedata.east_asian_width(char) in {"F", "W"}:
        return True
    code = ord(char)
    return (
        0x1100 <= code <= 0x11FF
        or 0x2E80 <= code <= 0x9FFF
        or 0xAC00 <= code <= 0xD7AF
        or 0xF900 <= code <= 0xFAFF
        or 0xFE10 <= code <= 0xFE1F
        or 0xFF00 <= code <= 0xFFEF
    )


def _segments(text: str) -> list[str]:
    segments: list[str] = []
    position = 0
    while position < len(text):
        match = _INLINE_SEGMENT_RE.match(text, position)
        if not match:
            segments.append(text[position])
            position += 1
            continue
        segments.append(match.group(0))
        position = match.end()
    return segments


def _wrap_plain_words(text: str, *, width: int, first_prefix: str, next_prefix: str) -> list[str]:
    words = re.split(r"(\s+)", text)
    lines: list[str] = []
    current = first_prefix
    current_width = text_display_width(first_prefix)

    for part in words:
        if not part:
            continue
        part_width = text_display_width(part)
        if part.isspace():
            if current_width + part_width <= width:
                current += part
                current_width += part_width
            continue
        if current not in {first_prefix, next_prefix} and current_width + part_width > width:
            lines.append(current.rstrip())
            current = next_prefix + part
            current_width = text_display_width(current)
            continue
        if current in {first_prefix, next_prefix}:
            current += part
        else:
            current += part if current.endswith((" ", "\t")) or current == first_prefix else f" {part}"
        current_width = text_display_width(current)

    if current.strip() or current in {first_prefix, next_prefix}:
        lines.append(current.rstrip())
    return lines or [first_prefix.rstrip()]


def _wrap_text_lines(text: str, *, width: int, first_prefix: str, next_prefix: str) -> list[str]:
    if text_display_width(first_prefix + text) <= width:
        return [first_prefix + text]

    if not re.search(r"[*_`\[\]!<>~\\]", text):
        return _wrap_plain_words(text, width=width, first_prefix=first_prefix, next_prefix=next_prefix)

    lines: list[str] = []
    current = first_prefix
    current_width = text_display_width(first_prefix)

    for segment in _segments(text):
        if segment == "\\\n":
            lines.append(current.rstrip())
            current = next_prefix
            current_width = text_display_width(next_prefix)
            continue

        segment_width = text_display_width(segment)
        if segment_width == 0:
            continue

        if current_width + segment_width <= width or current in {first_prefix, next_prefix} and not current.strip():
            if (
                segment.isspace()
                and current_width + segment_width > width
                and current not in {first_prefix, next_prefix}
            ):
                lines.append(current.rstrip())
                current = next_prefix
                current_width = text_display_width(next_prefix)
                if segment.isspace():
                    continue
            current += segment
            current_width += segment_width
            continue

        if segment.isspace():
            continue

        if current not in {first_prefix, next_prefix} and current.strip():
            lines.append(current.rstrip())
            current = next_prefix
            current_width = text_display_width(next_prefix)

        if segment_width > width - text_display_width(next_prefix):
            for char in segment:
                char_width = text_display_width(char)
                if (
                    current_width + char_width > width
                    and current.strip()
                    and current not in {first_prefix, next_prefix}
                ):
                    lines.append(current.rstrip())
                    current = next_prefix
                    current_width = text_display_width(next_prefix)
                if (
                    current_width + char_width > width
                    and current.endswith(segment[: segment.index(char)])
                    and _is_cjk(char)
                    and current
                    and _is_cjk(current[-1])
                ):
                    lines.append(current.rstrip())
                    current = next_prefix + char
                    current_width = text_display_width(next_prefix) + char_width
                    continue
                current += char
                current_width += char_width
            continue

        current += segment
        current_width += segment_width

    if current.strip() or current in {first_prefix, next_prefix}:
        lines.append(current.rstrip())
    return lines or [first_prefix.rstrip()]
