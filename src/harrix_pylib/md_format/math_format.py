"""Format TeX/LaTeX content inside Markdown dollar-math spans."""

from __future__ import annotations

import re
from dataclasses import dataclass

_PROTECTED_PREFIX = "HSKMDFMTMATHPROT"
_PROTECTED_COMMANDS = frozenset(
    {
        "text",
        "mathrm",
        "operatorname",
        "textbf",
        "textrm",
        "textit",
        "textsf",
        "texttt",
        "mathit",
        "mathbf",
        "mathsf",
        "mathtt",
    }
)
_FRAC_COMMANDS = frozenset({"frac", "dfrac", "tfrac", "binom"})
_LEFT_RIGHT_COMMANDS = frozenset({"left", "right", "bigl", "bigr", "Bigl", "Bigr", "biggl", "biggr", "Biggl", "Biggr"})
_SPACE_COMMANDS = frozenset({",", ";", ":", "!", "quad", "qquad"})
_BINARY_COMMANDS = frozenset(
    {
        "pm",
        "mp",
        "cdot",
        "times",
        "div",
        "leq",
        "geq",
        "neq",
        "approx",
        "equiv",
        "sim",
        "to",
        "rightarrow",
        "leftarrow",
        "Rightarrow",
        "Leftarrow",
        "in",
        "notin",
        "subset",
        "subseteq",
        "cup",
        "cap",
        "land",
        "lor",
    }
)
_CHAR_OPERATORS = frozenset({"+", "-", "=", "<", ">"})
_UNARY_CHAR_OPS = frozenset({"+", "-"})
# Environments whose bodies are split into rows/columns (`\\` / `&`).
_ROW_ENVS = frozenset(
    {
        "align",
        "align*",
        "aligned",
        "eqnarray",
        "eqnarray*",
        "matrix",
        "pmatrix",
        "bmatrix",
        "Bmatrix",
        "vmatrix",
        "Vmatrix",
        "array",
        "cases",
    }
)
_INDENT_UNIT = "  "
_BEGIN_RE = re.compile(r"\\begin\{([A-Za-z*]+)\}")
_COMMAND_NAME_RE = re.compile(r"[A-Za-z]+|.")
_PROTECTED_PLACEHOLDER_RE = re.compile(rf"{_PROTECTED_PREFIX}(\d+)Z")
_HLINE_ROW_RE = re.compile(r"^(\\(?:hdashline|hline))\s*(.*)$", re.DOTALL)


@dataclass(frozen=True, slots=True)
class _EnvLine:
    """One structural line inside a row-oriented environment body."""

    kind: str  # "blank" | "hline" | "data"
    cells: tuple[str, ...] = ()
    style: str = "amp"  # "amp" | "eq" | "eqnar"
    hline: str = ""
    add_break: bool = False


@dataclass(frozen=True, slots=True)
class _Token:
    """One lexical unit of math content."""

    kind: str
    value: str


def _apply_operator_spacing(content: str) -> str:
    """Insert canonical spaces around binary operators and alignment markers."""
    tokens = _tokenize(content)
    script_ranges = _script_group_ranges(tokens)

    def _in_script(index: int) -> bool:
        return any(start <= index <= end for start, end in script_ranges)

    parts: list[str] = []

    def _ends_with_space() -> bool:
        return bool(parts) and parts[-1].endswith(" ")

    def _ensure_space() -> None:
        if parts and not _ends_with_space() and not parts[-1].endswith("\n"):
            parts.append(" ")

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.kind == "ws":
            if "\n" not in token.value:
                # Keep inter-word spaces (e.g. \KwData{this text}).
                parts.append(" ")
            else:
                # Keep newlines and trailing indent after the last newline.
                parts.append("\n" * token.value.count("\n"))
                trailing = re.search(r"[ \t]+$", token.value)
                if trailing is not None:
                    parts.append(trailing.group(0))
            index += 1
            continue
        if token.kind == "op" and token.value in _UNARY_CHAR_OPS and _is_unary_plus_minus(tokens, index):
            parts.append(token.value)
            index += 1
            continue
        if token.kind == "op" and token.value in _UNARY_CHAR_OPS and _in_script(index):
            # Keep compact forms like x_{i-1} and x^{a+b}.
            parts.append(token.value)
            index += 1
            continue
        if token.kind == "amp":
            eq_index = index + 1
            while eq_index < len(tokens) and tokens[eq_index].kind == "ws":
                eq_index += 1
            amp2_index = eq_index + 1
            while amp2_index < len(tokens) and tokens[amp2_index].kind == "ws":
                amp2_index += 1
            # eqnarray alignment marker &=&
            if (
                eq_index < len(tokens)
                and tokens[eq_index].kind == "op"
                and tokens[eq_index].value == "="
                and amp2_index < len(tokens)
                and tokens[amp2_index].kind == "amp"
            ):
                _ensure_space()
                parts.append("&=&")
                index = amp2_index + 1
                if _next_significant(tokens, amp2_index) is not None:
                    parts.append(" ")
                continue
            nxt = _next_significant(tokens, index)
            _ensure_space()
            parts.append("&")
            if nxt is not None and not (nxt.kind == "op" and nxt.value == "="):
                parts.append(" ")
            index += 1
            continue
        if token.kind in {"op", "binop"}:
            prev = _prev_significant(tokens, index)
            if not (token.value == "=" and prev is not None and prev.kind == "amp"):
                _ensure_space()
            parts.append(token.value)
            if _next_significant(tokens, index) is not None:
                parts.append(" ")
            index += 1
            continue
        if token.kind == "command" and token.value == "\\\\":
            _ensure_space()
            parts.append("\\\\")
            if _next_significant(tokens, index) is not None:
                parts.append(" ")
            index += 1
            continue
        if token.kind == "comma":
            parts.append(",")
            if _next_significant(tokens, index) is not None:
                parts.append(" ")
            index += 1
            continue
        parts.append(token.value)
        # Control words must be separated from a following letter token: \lvert x
        if token.kind in {"command", "binop"} and _is_control_word(token.value):
            nxt = _next_significant(tokens, index)
            if nxt is not None and nxt.kind == "word":
                parts.append(" ")
        index += 1
    return _collapse_horizontal_spaces("".join(parts))


def _collapse_horizontal_spaces(text: str) -> str:
    """Collapse internal horizontal space runs; keep leading line indent."""
    lines = text.split("\n")
    collapsed_lines: list[str] = []
    for line in lines:
        stripped = line.lstrip(" \t")
        lead = line[: len(line) - len(stripped)]
        body = re.sub(r"[^\S\n]+", " ", stripped).rstrip(" \t")
        collapsed_lines.append(f"{lead}{body}")
    return "\n".join(collapsed_lines)


def _column_widths(lines: list[_EnvLine]) -> list[int]:
    """Return max display width for each column across data rows."""
    widths: list[int] = []
    for line in lines:
        if line.kind != "data":
            continue
        for index, cell in enumerate(line.cells):
            if index >= len(widths):
                widths.append(len(cell))
            else:
                widths[index] = max(widths[index], len(cell))
    return widths


def _consume_begin_args(content: str, start: int) -> int:
    r"""Consume optional `[...]` / `{...}` arguments after `\begin{env}`."""
    cursor = start
    length = len(content)
    while cursor < length:
        while cursor < length and content[cursor] in {" ", "\t"}:
            cursor += 1
        if cursor >= length:
            break
        if content[cursor] == "[":
            close = content.find("]", cursor + 1)
            if close < 0:
                break
            cursor = close + 1
            continue
        if content[cursor] == "{":
            close = _find_balanced_brace(content, cursor)
            if close is None:
                break
            cursor = close + 1
            continue
        break
    return cursor


def _dedent_common(text: str) -> str:
    """Remove common leading horizontal whitespace from non-empty lines."""
    if not text:
        return text
    lines = text.split("\n")
    non_empty = [line for line in lines if line.strip()]
    if not non_empty:
        return text
    common = min(len(line) - len(line.lstrip(" \t")) for line in non_empty)
    if not common:
        return text
    return "\n".join(line[common:] if line.strip() else "" for line in lines)


def _extract_protected_groups(content: str) -> tuple[str, list[str]]:
    """Replace protected command groups with placeholders."""
    protected: list[str] = []
    parts: list[str] = []
    index = 0
    length = len(content)
    while index < length:
        if content[index] == "\\" and index + 1 < length:
            name_match = re.match(r"[A-Za-z]+", content[index + 1 :])
            if name_match and name_match.group(0) in _PROTECTED_COMMANDS:
                name = name_match.group(0)
                start = index
                index = index + 1 + len(name)
                while index < length and content[index].isspace():
                    index += 1
                if index < length and content[index] == "{":
                    end = _find_balanced_brace(content, index)
                    if end is not None:
                        protected.append(content[start : end + 1])
                        parts.append(f"{_PROTECTED_PREFIX}{len(protected) - 1}Z")
                        index = end + 1
                        continue
                index = start
        parts.append(content[index])
        index += 1
    return "".join(parts), protected


def _find_balanced_brace(content: str, open_index: int) -> int | None:
    """Return index of matching `}` for `{` at `open_index`, or `None`."""
    if open_index >= len(content) or content[open_index] != "{":
        return None
    depth = 0
    index = open_index
    while index < len(content):
        char = content[index]
        if char == "\\" and index + 1 < len(content):
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _find_matching_end(content: str, start: int, env: str) -> int | None:
    r"""Find start index of matching \end{env}, respecting nesting."""
    depth = 1
    index = start
    begin_pat = re.compile(rf"\\begin\{{{re.escape(env)}\}}")
    end_pat = re.compile(rf"\\end\{{{re.escape(env)}\}}")
    while index < len(content):
        begin_match = begin_pat.search(content, index)
        end_match = end_pat.search(content, index)
        if end_match is None:
            return None
        if begin_match is not None and begin_match.start() < end_match.start():
            depth += 1
            index = begin_match.end()
            continue
        depth -= 1
        if depth == 0:
            return end_match.start()
        index = end_match.end()
    return None


def _find_matching_right(content: str, body_start: int) -> tuple[int, int, str] | None:
    r"""Find matching `\right...` for a `\left...` whose body starts at `body_start`."""
    depth = 1
    index = body_start
    length = len(content)
    while index < length:
        if content.startswith("\\left", index) and not content.startswith("\\leftarrow", index):
            left = _read_lr_command(content, index, "left")
            if left is not None:
                depth += 1
                index = left[0]
                continue
        if content.startswith("\\right", index) and not content.startswith("\\rightarrow", index):
            right = _read_lr_command(content, index, "right")
            if right is not None:
                depth -= 1
                if depth == 0:
                    end, text = right
                    return index, end, text
                index = right[0]
                continue
        index += 1
    return None


def _format_environment_body(body: str, *, depth: int = 1) -> str:
    """Format rows/columns inside a row-oriented environment at `depth` indent."""
    lines = _parse_environment_lines(body)
    widths = _column_widths(lines)
    indent = _INDENT_UNIT * depth
    formatted: list[str] = []
    for line in lines:
        if line.kind == "blank":
            formatted.append("")
            continue
        if line.kind == "hline":
            formatted.append(f"{indent}{line.hline}")
            continue
        rendered = _render_padded_cells(line.cells, widths, style=line.style)
        if line.add_break:
            formatted.append(f"{indent}{rendered} \\\\")
        else:
            formatted.append(f"{indent}{rendered}")
    return "\n".join(formatted)


def _format_math_content(content: str, *, display: bool = False) -> str:
    """Format TeX/LaTeX math content with a small conservative rule set.

    Args:

    - `content` (`str`): Raw math body without surrounding `$` / `$$` delimiters.
    - `display` (`bool`): Whether the span is display math. Defaults to `False`.

    Returns:

    - `str`: Formatted math body.

    """
    if not content or not content.strip():
        return content
    working, protected = _extract_protected_groups(content)
    working = _normalize_frac_args(working)
    working = _normalize_left_right(working)
    working = _apply_operator_spacing(working)
    working = _restore_protected(working, protected)
    if display:
        working = _layout_structures(working)
        working = "\n".join(line.rstrip() for line in working.splitlines())
    return working


def _is_control_word(command: str) -> bool:
    r"""Return whether `command` is a TeX control word like \lvert (not \{)."""
    return len(command) > 1 and command.startswith("\\") and command[1:].isalpha()


def _is_unary_plus_minus(tokens: list[_Token], index: int) -> bool:
    """Return whether `+`/`-` at `index` is unary."""
    prev = _prev_significant(tokens, index)
    if prev is None:
        return True
    if prev.kind in {
        "caret",
        "underscore",
        "lbrace",
        "lparen",
        "lbracket",
        "comma",
        "amp",
        "op",
        "binop",
    }:
        return True
    return prev.kind == "command" and prev.value == "\\\\"


def _layout_structures(content: str, *, depth: int = 0) -> str:
    r"""Pretty-print `\begin{...}` and multiline `\left...\right` by nesting depth."""
    return _prefix_indent(_layout_structures_root(_dedent_common(content)), depth)


def _layout_structures_root(content: str) -> str:
    r"""Layout structures with top-level items at indent depth 0."""
    parts: list[str] = []
    index = 0
    length = len(content)
    while index < length:
        begin_match = _BEGIN_RE.search(content, index)
        left_start: int | None = None
        search_from = index
        while search_from < length:
            found = content.find("\\left", search_from)
            if found < 0:
                break
            if _read_lr_command(content, found, "left") is not None:
                left_start = found
                break
            search_from = found + 5

        next_begin = begin_match.start() if begin_match is not None else None
        use_left = left_start is not None and (next_begin is None or left_start < next_begin)

        if not use_left and begin_match is None:
            parts.append(content[index:])
            break

        if use_left and left_start is not None:
            left = _read_lr_command(content, left_start, "left")
            if left is None:
                parts.append(content[index : left_start + 5])
                index = left_start + 5
                continue
            left_end, left_cmd = left
            matched = _find_matching_right(content, left_end)
            parts.append(content[index:left_start])
            if matched is None:
                parts.append(left_cmd)
                index = left_end
                continue
            right_start, right_end, right_cmd = matched
            body = content[left_end:right_start]
            should_break = "\\begin" in body or "\n" in body.strip()
            if should_break:
                # lstrip drops the space often left after \left(; keep line indents for dedent.
                formatted_body = _layout_structures(body.strip("\n").lstrip(" \t"), depth=1)
                block = f"{left_cmd}\n"
                if formatted_body.strip():
                    block += formatted_body.rstrip("\n") + "\n"
                block += right_cmd
            else:
                inner = _layout_structures_root(body.strip("\n").lstrip(" \t")).strip() or body.strip()
                block = f"{left_cmd}{inner}{right_cmd}"
            parts.append(block)
            index = right_end
            sibling = _skip_interstitial_ws_before_begin(content, index)
            if sibling is not None:
                if parts and not parts[-1].endswith("\n"):
                    parts.append("\n")
                if parts and not parts[-1].endswith("\n\n"):
                    parts.append("\n")
                index = sibling
            continue

        if begin_match is None:
            parts.append(content[index:])
            break
        env = begin_match.group(1)
        begin_start = begin_match.start()
        parts.append(content[index:begin_start])
        header_end = _consume_begin_args(content, begin_match.end())
        end_marker = f"\\end{{{env}}}"
        end_index = _find_matching_end(content, header_end, env)
        if end_index is None:
            parts.append(content[begin_start:header_end])
            index = header_end
            continue
        body = content[header_end:end_index]
        header = content[begin_start:header_end].strip()
        if env in _ROW_ENVS:
            formatted_body = _format_environment_body(body, depth=1)
        else:
            # Keep line indents so _dedent_common can normalize before re-indenting.
            formatted_body = _layout_structures(body.strip("\n"), depth=1)
        block = f"{header}\n"
        if formatted_body.strip():
            block += formatted_body.rstrip("\n") + "\n"
        block += end_marker
        parts.append(block)
        index = end_index + len(end_marker)
        sibling = _skip_interstitial_ws_before_begin(content, index)
        if sibling is not None:
            if parts and not parts[-1].endswith("\n"):
                parts.append("\n")
            if parts and not parts[-1].endswith("\n\n"):
                parts.append("\n")
            index = sibling
    return "".join(parts)


def _next_significant(tokens: list[_Token], index: int) -> _Token | None:
    """Return next non-whitespace token after `index`."""
    cursor = index + 1
    while cursor < len(tokens):
        if tokens[cursor].kind != "ws":
            return tokens[cursor]
        cursor += 1
    return None


def _normalize_cell_text(cell: str) -> str:
    """Collapse internal whitespace in one table/align cell."""
    return " ".join(cell.split())


def _normalize_frac_args(content: str) -> str:
    """Trim spaces inside braced arguments of frac-like commands."""
    parts: list[str] = []
    index = 0
    length = len(content)
    while index < length:
        if content[index] == "\\" and index + 1 < length:
            name_match = re.match(r"[A-Za-z]+", content[index + 1 :])
            if name_match and name_match.group(0) in _FRAC_COMMANDS:
                name = name_match.group(0)
                start = index
                index = index + 1 + len(name)
                args: list[str] = []
                ok = True
                for _ in range(2):
                    while index < length and content[index].isspace() and content[index] != "\n":
                        index += 1
                    if index >= length or content[index] != "{":
                        ok = False
                        break
                    close = _find_balanced_brace(content, index)
                    if close is None:
                        ok = False
                        break
                    inner = content[index + 1 : close]
                    args.append("{" + inner.strip() + "}")
                    index = close + 1
                if ok and len(args) == 2:
                    parts.append(f"\\{name}{args[0]}{args[1]}")
                    continue
                index = start
        parts.append(content[index])
        index += 1
    return "".join(parts)


def _normalize_left_right(content: str) -> str:
    r"""Remove spaces between \left/\right-style commands and their delimiters."""
    parts: list[str] = []
    index = 0
    length = len(content)
    while index < length:
        if content[index] == "\\" and index + 1 < length:
            name_match = re.match(r"[A-Za-z]+", content[index + 1 :])
            if name_match and name_match.group(0) in _LEFT_RIGHT_COMMANDS:
                name = name_match.group(0)
                cursor = index + 1 + len(name)
                while cursor < length and content[cursor] in {" ", "\t"}:
                    cursor += 1
                if cursor >= length:
                    parts.append(content[index:cursor])
                    index = cursor
                    continue
                if content[cursor] == "\\" and cursor + 1 < length:
                    esc_match = _COMMAND_NAME_RE.match(content, cursor + 1)
                    if esc_match:
                        delimiter = "\\" + esc_match.group(0)
                        parts.append(f"\\{name}{delimiter}")
                        index = cursor + len(delimiter)
                        continue
                parts.append(f"\\{name}{content[cursor]}")
                index = cursor + 1
                continue
        parts.append(content[index])
        index += 1
    return "".join(parts)


def _parse_environment_lines(body: str) -> list[_EnvLine]:
    """Parse environment body into blank/hline/data lines with cell lists."""
    rows = _split_top_level(body.strip("\n"), "\\\\")
    if rows and not rows[-1].strip():
        rows = rows[:-1]
    lines: list[_EnvLine] = []
    for row_index, row in enumerate(rows):
        add_break = row_index < len(rows) - 1
        lines.extend(_parse_environment_row(row, add_break=add_break))
    while lines and lines[-1].kind == "blank":
        lines.pop()
    return lines


def _parse_environment_row(row: str, *, add_break: bool) -> list[_EnvLine]:
    r"""Parse one raw row, peeling leading \hline/\hdashline markers."""
    stripped = row.strip()
    if not stripped:
        return [_EnvLine(kind="blank")]
    hline_match = _HLINE_ROW_RE.match(stripped)
    if hline_match:
        parsed = [_EnvLine(kind="hline", hline=hline_match.group(1))]
        rest = hline_match.group(2).strip()
        if rest:
            parsed.extend(_parse_environment_row(rest, add_break=add_break))
        return parsed
    if "&=&" in stripped:
        left, _, right = stripped.partition("&=&")
        return [
            _EnvLine(
                kind="data",
                cells=(_normalize_cell_text(left), _normalize_cell_text(right)),
                style="eqnar",
                add_break=add_break,
            )
        ]
    cells_raw = _split_top_level(stripped, "&")
    cells: list[str] = []
    style = "amp"
    for cell_index, cell in enumerate(cells_raw):
        text = _normalize_cell_text(cell)
        if cell_index == 0:
            cells.append(text)
            continue
        if text.startswith("="):
            style = "eq"
            cells.append(_normalize_cell_text(text[1:]))
        else:
            cells.append(text)
    return [_EnvLine(kind="data", cells=tuple(cells), style=style, add_break=add_break)]


def _prefix_indent(text: str, depth: int) -> str:
    """Prefix every non-empty line with `depth` indent units.

    Dedents by the common leading whitespace of non-empty lines first so that
    re-running layout stays idempotent when prior indents were preserved.

    """
    if not text or depth <= 0:
        return text
    lines = _dedent_common(text).split("\n")
    indent = _INDENT_UNIT * depth
    out = [f"{indent}{line}" if line.strip() else "" for line in lines]
    result = "\n".join(out)
    if text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def _prev_significant(tokens: list[_Token], index: int) -> _Token | None:
    """Return previous non-whitespace token before `index`."""
    cursor = index - 1
    while cursor >= 0:
        if tokens[cursor].kind != "ws":
            return tokens[cursor]
        cursor -= 1
    return None


def _read_lr_command(content: str, start: int, which: str) -> tuple[int, str] | None:
    r"""Read `\left`/`\right` plus delimiter; return end index and full command text."""
    prefix = f"\\{which}"
    if not content.startswith(prefix, start):
        return None
    cursor = start + len(prefix)
    if cursor >= len(content):
        return None
    # Reject longer control words that share a prefix (\leftarrow, \rightarrow, ...).
    if content[cursor].isalpha():
        return None
    if content[cursor] == "\\" and cursor + 1 < len(content):
        esc_match = _COMMAND_NAME_RE.match(content, cursor + 1)
        if esc_match is None:
            return None
        end = cursor + 1 + len(esc_match.group(0))
        return end, content[start:end]
    return cursor + 1, content[start : cursor + 1]


def _render_padded_cells(cells: tuple[str, ...], widths: list[int], *, style: str) -> str:
    """Join cells with aligned padding; do not pad the last column."""
    if not cells:
        return ""
    padded: list[str] = []
    for index, cell in enumerate(cells):
        width = widths[index] if index < len(widths) else len(cell)
        if index < len(cells) - 1:
            padded.append(cell.ljust(width))
        else:
            padded.append(cell)
    if style == "eqnar":
        return f"{padded[0]} &=& {padded[1]}" if len(padded) > 1 else padded[0]
    if style == "eq":
        if len(padded) == 1:
            return padded[0]
        return padded[0] + "".join(f" &= {part}" for part in padded[1:])
    if len(padded) == 1:
        return padded[0]
    return padded[0] + "".join(f" & {part}" for part in padded[1:])


def _restore_protected(content: str, protected: list[str]) -> str:
    """Restore protected command groups from placeholders."""

    def _replace(match: re.Match[str]) -> str:
        return protected[int(match.group(1))]

    return _PROTECTED_PLACEHOLDER_RE.sub(_replace, content)


def _script_group_ranges(tokens: list[_Token]) -> list[tuple[int, int]]:
    """Return inclusive token index ranges for `^`/`_` braced or single-token groups."""
    ranges: list[tuple[int, int]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.kind in {"caret", "underscore"}:
            cursor = index + 1
            while cursor < len(tokens) and tokens[cursor].kind == "ws":
                cursor += 1
            if cursor >= len(tokens):
                index += 1
                continue
            if tokens[cursor].kind == "lbrace":
                depth = 0
                end = cursor
                while end < len(tokens):
                    if tokens[end].kind == "lbrace":
                        depth += 1
                    elif tokens[end].kind == "rbrace":
                        depth -= 1
                        if depth == 0:
                            ranges.append((cursor, end))
                            break
                    end += 1
                index = end + 1 if end < len(tokens) else cursor + 1
                continue
            ranges.append((cursor, cursor))
            index = cursor + 1
            continue
        index += 1
    return ranges


def _skip_interstitial_ws_before_begin(content: str, index: int) -> int | None:
    r"""If only whitespace remains before a sibling `\begin`, return index of that `\begin`."""
    cursor = index
    length = len(content)
    while cursor < length and content[cursor] in {" ", "\t", "\n"}:
        cursor += 1
    if content.startswith("\\begin{", cursor):
        return cursor
    return None


def _split_top_level(content: str, separator: str) -> list[str]:
    """Split `content` by `separator` outside braces and nested begin/end."""
    parts: list[str] = []
    start = 0
    index = 0
    brace_depth = 0
    env_depth = 0
    length = len(content)
    sep_len = len(separator)
    while index < length:
        char = content[index]
        if char == "\\" and index + 1 < length:
            begin_match = _BEGIN_RE.match(content, index)
            if begin_match:
                env_depth += 1
                index = begin_match.end()
                continue
            end_match = re.match(r"\\end\{[A-Za-z*]+\}", content[index:])
            if end_match:
                env_depth = max(0, env_depth - 1)
                index += end_match.end()
                continue
            if content.startswith(separator, index) and brace_depth == 0 and env_depth == 0:
                parts.append(content[start:index])
                index += sep_len
                start = index
                continue
            # Skip command name / escaped char
            name_match = re.match(r"[A-Za-z]+|.", content[index + 1 :])
            index += 1 + (len(name_match.group(0)) if name_match else 1)
            continue
        if char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)
        elif char == separator and brace_depth == 0 and env_depth == 0 and sep_len == 1:
            parts.append(content[start:index])
            index += 1
            start = index
            continue
        index += 1
    parts.append(content[start:])
    return parts


def _tokenize(content: str) -> list[_Token]:
    """Tokenize math content into a flat token list."""
    tokens: list[_Token] = []
    index = 0
    length = len(content)
    while index < length:
        char = content[index]
        if char.isspace():
            end = index + 1
            while end < length and content[end].isspace():
                end += 1
            tokens.append(_Token("ws", content[index:end]))
            index = end
            continue
        if char == "\\":
            if index + 1 >= length:
                tokens.append(_Token("other", "\\"))
                index += 1
                continue
            next_char = content[index + 1]
            if next_char == "\\":
                tokens.append(_Token("command", "\\\\"))
                index += 2
                continue
            if next_char == " ":
                tokens.append(_Token("space_cmd", "\\ "))
                index += 2
                continue
            if next_char in {",", ";", ":", "!"}:
                tokens.append(_Token("space_cmd", "\\" + next_char))
                index += 2
                continue
            name_match = re.match(r"[A-Za-z]+", content[index + 1 :])
            if name_match:
                name = name_match.group(0)
                command = "\\" + name
                if name in _SPACE_COMMANDS:
                    tokens.append(_Token("space_cmd", command))
                elif name in _BINARY_COMMANDS:
                    tokens.append(_Token("binop", command))
                else:
                    tokens.append(_Token("command", command))
                index += 1 + len(name)
                continue
            tokens.append(_Token("command", "\\" + next_char))
            index += 2
            continue
        if char in _CHAR_OPERATORS:
            tokens.append(_Token("op", char))
            index += 1
            continue
        if char == "&":
            tokens.append(_Token("amp", "&"))
            index += 1
            continue
        if char == "^":
            tokens.append(_Token("caret", "^"))
            index += 1
            continue
        if char == "_":
            tokens.append(_Token("underscore", "_"))
            index += 1
            continue
        if char == "{":
            tokens.append(_Token("lbrace", "{"))
            index += 1
            continue
        if char == "}":
            tokens.append(_Token("rbrace", "}"))
            index += 1
            continue
        if char == "(":
            tokens.append(_Token("lparen", "("))
            index += 1
            continue
        if char == ")":
            tokens.append(_Token("rparen", ")"))
            index += 1
            continue
        if char == "[":
            tokens.append(_Token("lbracket", "["))
            index += 1
            continue
        if char == "]":
            tokens.append(_Token("rbracket", "]"))
            index += 1
            continue
        if char == ",":
            tokens.append(_Token("comma", ","))
            index += 1
            continue
        if char.isdigit():
            end = index + 1
            while end < length and content[end].isdigit():
                end += 1
            tokens.append(_Token("number", content[index:end]))
            index = end
            continue
        if char.isalpha():
            end = index + 1
            # Underscore is the TeX subscript operator, not part of an identifier.
            while end < length and content[end].isalnum():
                end += 1
            tokens.append(_Token("word", content[index:end]))
            index = end
            continue
        tokens.append(_Token("other", char))
        index += 1
    return tokens
