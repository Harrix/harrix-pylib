"""Format Markdown inside Python docstrings safely for source literals."""

from __future__ import annotations

import ast
import inspect
import re
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import libcst as cst

from harrix_pylib.md_format import MdFormatter

if TYPE_CHECKING:
    from collections.abc import Sequence

_STRING_PREFIX_RE = re.compile(r"^[rRuUbBfF]*")
_TRIPLE_QUOTES = ('"""', "'''")
_UNSUPPORTED_PREFIX_CHARS = frozenset("fbFB")
_MIN_MULTILINE_LITERAL_LINES = 2


def format_python_docstrings(filename: Path | str) -> str:
    r"""Format Markdown inside multiline Python docstrings in a file.

    Uses `MdFormatter` on docstring bodies, then writes them back so that:

    - Multiline docstrings keep a blank line before the closing quotes
    - When the formatted body contains backslashes, the literal gets an `r`
      prefix (D301) and Markdown escapes are written as single `\` in source
    - One-line docstrings are left unchanged

    Args:

    - `filename` (`Path | str`): Path to the Python file to update.

    Returns:

    - `str`: Status message.

    """
    path = Path(filename)
    original = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(original)
    except Exception as e:
        return f"⚠️ Skip {path}: parse error: {e}"

    transformer = _DocstringMdFormatTransformer()
    updated = module.visit(transformer)
    new_code = updated.code
    if new_code == original:
        if transformer.skipped:
            return f"⚠️ File {path}: skipped {transformer.skipped} docstring(s); unchanged."
        return "File is not changed."
    path.write_text(new_code, encoding="utf-8", newline="\n")
    skip_note = f" (skipped {transformer.skipped})" if transformer.skipped else ""
    return f"✅ File {path} docstring Markdown formatted.{skip_note}"


class _DocstringMdFormatTransformer(cst.CSTTransformer):
    """Rewrite multiline docstring SimpleString nodes with formatted Markdown."""

    def __init__(self) -> None:
        """Initialize skip counter."""
        super().__init__()
        self.skipped = 0

    def leave_Module(  # noqa: N802
        self, original_node: cst.Module, updated_node: cst.Module  # noqa: ARG002
    ) -> cst.Module:
        """Format module docstring if present."""
        new_body = self._format_first_docstring_in_body(updated_node.body, content_indent="")
        if new_body is None:
            return updated_node
        return updated_node.with_changes(body=new_body)

    def leave_ClassDef(  # noqa: N802
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef  # noqa: ARG002
    ) -> cst.ClassDef:
        """Format class docstring if present."""
        return self._format_indented_owner(updated_node)

    def leave_FunctionDef(  # noqa: N802
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef  # noqa: ARG002
    ) -> cst.FunctionDef:
        """Format function/method docstring if present."""
        return self._format_indented_owner(updated_node)

    def _format_indented_owner(
        self, updated_node: cst.ClassDef | cst.FunctionDef
    ) -> cst.ClassDef | cst.FunctionDef:
        body = updated_node.body
        if not isinstance(body, cst.IndentedBlock):
            return updated_node
        indent = body.indent if isinstance(body.indent, str) else "    "
        new_statements = self._format_first_docstring_in_body(body.body, content_indent=indent)
        if new_statements is None:
            return updated_node
        return updated_node.with_changes(body=body.with_changes(body=new_statements))

    def _format_first_docstring_in_body(
        self,
        statements: Sequence[cst.BaseStatement],
        *,
        content_indent: str,
    ) -> list[cst.BaseStatement] | None:
        if not statements:
            return None
        first = statements[0]
        string_node = _docstring_simple_string(first)
        if string_node is None:
            return None
        if "\n" not in string_node.value:
            return None

        inferred_indent = _content_indent_from_literal(string_node.value) or content_indent
        new_string = _format_docstring_simple_string(string_node, content_indent=inferred_indent)
        if new_string is None:
            self.skipped += 1
            return None
        if new_string.value == string_node.value:
            return None

        if not isinstance(first, cst.SimpleStatementLine):
            return None
        expr = first.body[0]
        if not isinstance(expr, cst.Expr):
            return None
        new_first = first.with_changes(body=[expr.with_changes(value=new_string)])
        return [new_first, *list(statements[1:])]


def _docstring_simple_string(stmt: cst.BaseStatement) -> cst.SimpleString | None:
    if not isinstance(stmt, cst.SimpleStatementLine):
        return None
    if len(stmt.body) != 1:
        return None
    expr = stmt.body[0]
    if not isinstance(expr, cst.Expr) or not isinstance(expr.value, cst.SimpleString):
        return None
    return expr.value


def _format_docstring_simple_string(
    string_node: cst.SimpleString,
    *,
    content_indent: str,
) -> cst.SimpleString | None:
    prefix, quote = _literal_prefix_and_quote(string_node.value)
    if quote not in _TRIPLE_QUOTES:
        return None
    if any(char in prefix for char in _UNSUPPORTED_PREFIX_CHARS):
        return None

    content = _evaluate_string_literal(string_node.value)
    if content is None or "\n" not in content:
        return None

    cleaned = inspect.cleandoc(content)
    formatter = MdFormatter(end_of_line="lf", prose_wrap="preserve")
    formatted = formatter.format(cleaned + "\n")
    # Docstrings need a blank content line before the closing quotes (unlike .md files).
    formatted = formatted.rstrip("\n") + "\n\n"

    if "\\" in formatted:
        prefix = _ensure_raw_prefix(prefix)

    try:
        new_literal = _build_docstring_literal(
            formatted,
            prefix=prefix,
            quote=quote,
            content_indent=content_indent,
        )
    except ValueError:
        return None
    return cst.SimpleString(value=new_literal)


def _ensure_raw_prefix(prefix: str) -> str:
    """Return a string prefix that includes raw (`r` / `R`)."""
    if "r" in prefix.lower():
        return prefix
    return f"r{prefix}"


def _evaluate_string_literal(literal: str) -> str | None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            value = ast.literal_eval(literal)
        except (SyntaxError, ValueError):
            return None
    return value if isinstance(value, str) else None


def _literal_prefix_and_quote(literal: str) -> tuple[str, str]:
    match = _STRING_PREFIX_RE.match(literal)
    prefix = match.group(0) if match else ""
    rest = literal[len(prefix) :]
    for quote in _TRIPLE_QUOTES:
        if rest.startswith(quote):
            return prefix, quote
    if rest.startswith('"'):
        return prefix, '"'
    if rest.startswith("'"):
        return prefix, "'"
    msg = f"Unsupported string literal: {literal[:20]!r}"
    raise ValueError(msg)


def _content_indent_from_literal(literal: str) -> str:
    """Infer indentation used on continuation lines inside a multiline literal."""
    lines = literal.split("\n")
    if len(lines) < _MIN_MULTILINE_LITERAL_LINES:
        return ""
    last = lines[-1]
    for quote in _TRIPLE_QUOTES:
        if last.endswith(quote):
            return last[: -len(quote)]
    match = re.match(r"^([ \t]*)\S", lines[1])
    return match.group(1) if match else ""


def _build_docstring_literal(
    content: str,
    *,
    prefix: str,
    quote: str,
    content_indent: str,
) -> str:
    r"""Build a SimpleString.value for a multiline docstring.

    `content` is the logical docstring value and should end with a blank line
    (`...\n\n`) so the closing quotes sit after an empty line.

    """
    is_raw = "r" in prefix.lower()
    body = content.rstrip("\n") + "\n\n"
    # Drop the final newline so split keeps the trailing blank content line.
    lines = body[:-1].split("\n")

    encoded: list[str] = []
    for line in lines:
        if quote in line:
            msg = f"Docstring cannot contain delimiter {quote}"
            raise ValueError(msg)
        if is_raw:
            encoded.append(line)
        else:
            # No backslashes by policy; still escape quote characters if needed.
            encoded.append(_encode_non_raw_line(line, quote=quote))

    parts = [f"{prefix}{quote}{encoded[0]}"]
    for line in encoded[1:]:
        if line == "":
            parts.append("")
        else:
            parts.append(f"{content_indent}{line}")
    parts.append(f"{content_indent}{quote}")
    return "\n".join(parts)


def _encode_non_raw_line(line: str, *, quote: str) -> str:
    """Encode a logical line for a non-raw triple-quoted string literal."""
    single = quote[0]
    if single in line:
        return line.replace(single, f"\\{single}")
    return line
