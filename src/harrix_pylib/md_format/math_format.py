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
_LAYOUT_ENVS = frozenset(
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
_BEGIN_RE = re.compile(r"\\begin\{([A-Za-z*]+)\}")
_COMMAND_NAME_RE = re.compile(r"[A-Za-z]+|.")
_PROTECTED_PLACEHOLDER_RE = re.compile(rf"{_PROTECTED_PREFIX}(\d+)")


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

    for index, token in enumerate(tokens):
        if token.kind == "ws":
            if "\n" in token.value:
                # Preserve line structure; collapse horizontal runs later via spacing rules.
                newline_count = token.value.count("\n")
                parts.append("\n" * newline_count)
            continue
        if token.kind == "op" and token.value in _UNARY_CHAR_OPS and _is_unary_plus_minus(tokens, index):
            parts.append(token.value)
            continue
        if token.kind == "op" and token.value in _UNARY_CHAR_OPS and _in_script(index):
            # Keep compact forms like x_{i-1} and x^{a+b}.
            parts.append(token.value)
            continue
        if token.kind in {"op", "binop"}:
            prev = _prev_significant(tokens, index)
            if not (token.value == "=" and prev is not None and prev.kind == "amp"):
                _ensure_space()
            parts.append(token.value)
            if _next_significant(tokens, index) is not None:
                parts.append(" ")
            continue
        if token.kind == "amp":
            _ensure_space()
            parts.append("&")
            nxt = _next_significant(tokens, index)
            if nxt is not None and not (nxt.kind == "op" and nxt.value == "="):
                parts.append(" ")
            continue
        if token.kind == "command" and token.value == "\\\\":
            _ensure_space()
            parts.append("\\\\")
            if _next_significant(tokens, index) is not None:
                parts.append(" ")
            continue
        if token.kind == "comma":
            parts.append(",")
            if _next_significant(tokens, index) is not None:
                parts.append(" ")
            continue
        parts.append(token.value)
        # Control words must be separated from a following letter token: \lvert x
        if token.kind in {"command", "binop"} and _is_control_word(token.value):
            nxt = _next_significant(tokens, index)
            if nxt is not None and nxt.kind == "word":
                parts.append(" ")
    # Collapse runs of spaces but keep newlines.
    collapsed = re.sub(r"[^\S\n]+", " ", "".join(parts))
    collapsed = re.sub(r" +\n", "\n", collapsed)
    return re.sub(r"\n +", "\n", collapsed)


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
                        parts.append(f"{_PROTECTED_PREFIX}{len(protected) - 1}")
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


def _format_environment_body(body: str) -> str:
    """Format rows/columns inside a layout environment with 2-space indent."""
    nested = _layout_environments(body.strip("\n"))
    rows = _split_top_level(nested, "\\\\")
    # Trailing \\ produces an empty final segment — drop it.
    if rows and not rows[-1].strip():
        rows = rows[:-1]
    formatted_rows: list[str] = []
    for row_index, row in enumerate(rows):
        if not row.strip():
            formatted_rows.append("")
            continue
        add_break = row_index < len(rows) - 1
        formatted_rows.extend(_format_environment_row(row, add_break=add_break))
    while formatted_rows and formatted_rows[-1] == "":
        formatted_rows.pop()
    return "\n".join(formatted_rows)


def _format_environment_row(row: str, *, add_break: bool) -> list[str]:
    r"""Format one environment row, peeling leading \hline/\hdashline markers."""
    stripped = row.strip()
    if not stripped:
        return [""]
    hline_match = _HLINE_ROW_RE.match(stripped)
    if hline_match:
        lines = [f"  {hline_match.group(1)}"]
        rest = hline_match.group(2).strip()
        if rest:
            lines.extend(_format_environment_row(rest, add_break=add_break))
        return lines
    cells = _split_top_level(stripped, "&")
    rebuilt: list[str] = []
    for cell_index, cell in enumerate(cells):
        text = " ".join(cell.split())
        if cell_index == 0:
            rebuilt.append(text)
            continue
        if text.startswith("="):
            rhs = text[1:].lstrip()
            rebuilt.append(f"&= {rhs}" if rhs else "&=")
        else:
            rebuilt.append(f"& {text}")
    line = " ".join(rebuilt)
    if add_break:
        return [f"  {line} \\\\"]
    return [f"  {line}"]


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
        working = _layout_environments(working)
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


def _layout_environments(content: str) -> str:
    """Pretty-print supported multi-line math environments in display math."""
    parts: list[str] = []
    index = 0
    length = len(content)
    while index < length:
        match = _BEGIN_RE.search(content, index)
        if match is None:
            parts.append(content[index:])
            break
        env = match.group(1)
        if env not in _LAYOUT_ENVS:
            parts.append(content[index : match.end()])
            index = match.end()
            continue
        begin_start = match.start()
        parts.append(content[index:begin_start])
        # Optional argument after \begin{array}{...}
        header_end = match.end()
        cursor = header_end
        while cursor < length and content[cursor] in {" ", "\t"}:
            cursor += 1
        if cursor < length and content[cursor] == "{":
            arg_close = _find_balanced_brace(content, cursor)
            if arg_close is not None:
                header_end = arg_close + 1
                cursor = header_end
        end_marker = f"\\end{{{env}}}"
        end_index = _find_matching_end(content, cursor, env)
        if end_index is None:
            parts.append(content[begin_start:header_end])
            index = header_end
            continue
        body = content[header_end:end_index]
        formatted_body = _format_environment_body(body)
        header = content[begin_start:header_end].strip()
        parts.append(f"{header}\n{formatted_body}\n{end_marker}")
        index = end_index + len(end_marker)
    return "".join(parts)


def _next_significant(tokens: list[_Token], index: int) -> _Token | None:
    """Return next non-whitespace token after `index`."""
    cursor = index + 1
    while cursor < len(tokens):
        if tokens[cursor].kind != "ws":
            return tokens[cursor]
        cursor += 1
    return None


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


def _prev_significant(tokens: list[_Token], index: int) -> _Token | None:
    """Return previous non-whitespace token before `index`."""
    cursor = index - 1
    while cursor >= 0:
        if tokens[cursor].kind != "ws":
            return tokens[cursor]
        cursor -= 1
    return None


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


_HLINE_ROW_RE = re.compile(r"^(\\(?:hdashline|hline))\s*(.*)$", re.DOTALL)
