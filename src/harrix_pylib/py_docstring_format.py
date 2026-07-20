"""Format Markdown inside Python docstrings safely for source literals."""

from __future__ import annotations

import ast
import inspect
import re
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import libcst as cst

from harrix_pylib.md_format import MdFormatter
from harrix_pylib.md_format.code_fence import _identify_code_blocks, _identify_code_blocks_line
from harrix_pylib.md_format.prose_fixes import _apply_checker_prose_fixes

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

_OwnerT = TypeVar("_OwnerT", cst.ClassDef, cst.FunctionDef)

_STRING_PREFIX_RE = re.compile(r"^[rRuUbBfF]*")
_TRIPLE_QUOTES = ('"""', "'''")
_UNSUPPORTED_PREFIX_CHARS = frozenset("fbFB")
_MIN_MULTILINE_LITERAL_LINES = 2
_BARE_LITERAL_RE = re.compile(r"\b(True|False|None)\b")
_QUOTED_CODE_RE = re.compile(r"""(['"])([A-Za-z_][\w.-]*)\1""")


class PyDocstringFormatter:
    """Format Markdown inside Python docstrings, similar to `MdFormatter` for `.md` files."""

    def __call__(self, filename: Path | str) -> str:
        """Format docstrings in a Python file in place."""
        return self.format_file(filename)

    def __init__(
        self,
        *,
        end_of_line: str = "lf",
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
    ) -> None:
        """Initialize the docstring formatter.

        Args:

        - `end_of_line` (`str`): Line ending style passed to `MdFormatter` for docstring
          bodies (`crlf` or `lf`). Defaults to `lf` (matches typical Python sources).
        - `prose_wrap` (`str`): Prettier-style prose wrap (`preserve`, `always`, `never`).
          Defaults to `preserve`.
        - `print_width` (`int`): Wrap width when `prose_wrap` is `always`. Defaults to `80`.
        - `apply_prose_fixes` (`bool`): Apply mechanical MdChecker autofixes inside docstring
          Markdown. Defaults to `True`.

        """
        self.md_formatter = MdFormatter(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
        )

    def format(self, source: str) -> str:
        """Format Markdown inside docstrings in Python source text.

        Args:

        - `source` (`str`): Python source code.

        Returns:

        - `str`: Source with formatted docstrings (unchanged when nothing applies).

        """
        module = cst.parse_module(source)
        transformer = _DocstringMdFormatTransformer(self)
        return module.visit(transformer).code

    def format_file(self, filename: Path | str) -> str:
        r"""Format Markdown inside Python docstrings in a file.

        Uses `MdFormatter` on multiline docstring bodies, then writes them back so that:

        - Multiline docstrings keep a blank line before the closing quotes
        - When the formatted body contains backslashes, the literal gets an `r`
          prefix (D301) and Markdown escapes are written as single `\` in source
        - Code tokens in prose (`True` / `False` / `None`, and quoted identifiers) use
          backticks; fenced and inline code are left unchanged
        - One-line docstrings get the same prose fixes and code-span normalization, but
          stay on a single physical line between the opening and closing quotes

        Args:

        - `filename` (`Path | str`): Path to the Python file to update.

        Returns:

        - `str`: Status message.

        """
        path = Path(filename)
        raw = path.read_bytes()
        had_crlf = b"\r\n" in raw or b"\r" in raw
        original = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        try:
            module = cst.parse_module(original)
        except Exception as e:
            return f"⚠️ Skip {path}: parse error: {e}"

        transformer = _DocstringMdFormatTransformer(self)
        updated = module.visit(transformer)
        new_code = updated.code
        content_changed = new_code != original
        if not content_changed and not had_crlf:
            if transformer.skipped:
                return f"⚠️ File {path}: skipped {transformer.skipped} docstring(s); unchanged."
            return "File is not changed."
        path.write_text(new_code, encoding="utf-8", newline="\n")
        if not content_changed and had_crlf:
            return f"✅ File {path} line endings normalized to LF."
        skip_note = f" (skipped {transformer.skipped})" if transformer.skipped else ""
        return f"✅ File {path} docstring Markdown formatted.{skip_note}"

    def format_folder(self, folder: Path | str) -> str:
        """Recursively format docstrings in Python files in a folder.

        Args:

        - `folder` (`Path | str`): Directory containing Python files.

        Returns:

        - `str`: Newline-separated status messages.

        """
        from harrix_pylib import funcs_file  # noqa: PLC0415

        return funcs_file.apply_func(folder, ".py", self.format_file)

    @staticmethod
    def iter_code_span_issues(text: str) -> Iterator[tuple[int, int, str]]:
        """Yield `(line_index, col_1based, token)` for prose tokens that should use backticks."""
        lines = text.split("\n")
        for line_index, (line, in_fence) in enumerate(_identify_code_blocks(lines)):
            if in_fence:
                continue
            offset = 0
            for segment, in_code in _identify_code_blocks_line(line):
                if not in_code:
                    for match in _QUOTED_CODE_RE.finditer(segment):
                        yield line_index, offset + match.start() + 1, match.group(0)
                    for match in _BARE_LITERAL_RE.finditer(segment):
                        yield line_index, offset + match.start() + 1, match.group(1)
                offset += len(segment)

    @staticmethod
    def normalize_code_spans(text: str) -> str:
        """Wrap code tokens in backticks in docstring Markdown prose.

        Outside fenced and inline code:

        - Bare `True`, `False`, and `None` become `` `True` `` / `` `False` `` / `` `None` ``
        - Quoted identifiers like `'name'` or `"HP001"` become `` `name` `` / `` `HP001` ``

        """
        lines = text.split("\n")
        out_lines: list[str] = []
        for line, in_fence in _identify_code_blocks(lines):
            if in_fence:
                out_lines.append(line)
                continue
            parts: list[str] = []
            for segment, in_code in _identify_code_blocks_line(line):
                if in_code:
                    parts.append(segment)
                else:
                    parts.append(_normalize_prose_segment(segment))
            out_lines.append("".join(parts))
        result = "\n".join(out_lines)
        if text.endswith("\n") and not result.endswith("\n"):
            result += "\n"
        return result


class _DocstringMdFormatTransformer(cst.CSTTransformer):
    """Rewrite docstring SimpleString nodes with formatted Markdown."""

    def __init__(self, formatter: PyDocstringFormatter) -> None:
        """Initialize with parent formatter and skip counter."""
        super().__init__()
        self.formatter = formatter
        self.skipped = 0

    def leave_ClassDef(  # noqa: N802
        self,
        original_node: cst.ClassDef,  # noqa: ARG002
        updated_node: cst.ClassDef,
    ) -> cst.ClassDef:
        """Format class docstring if present."""
        return self._format_indented_owner(updated_node)

    def leave_FunctionDef(  # noqa: N802
        self,
        original_node: cst.FunctionDef,  # noqa: ARG002
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        """Format function/method docstring if present."""
        return self._format_indented_owner(updated_node)

    def leave_Module(  # noqa: N802
        self,
        original_node: cst.Module,  # noqa: ARG002
        updated_node: cst.Module,
    ) -> cst.Module:
        """Format module docstring if present."""
        new_body = self._format_first_docstring_in_body(updated_node.body, content_indent="")
        if new_body is None:
            return updated_node
        return updated_node.with_changes(body=new_body)

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
            new_string = _format_one_line_docstring(
                string_node,
                md_formatter=self.formatter.md_formatter,
            )
        else:
            inferred_indent = _content_indent_from_literal(string_node.value) or content_indent
            new_string = _format_docstring_simple_string(
                string_node,
                md_formatter=self.formatter.md_formatter,
                content_indent=inferred_indent,
            )
            if new_string is None:
                self.skipped += 1
                return None

        if new_string is None or new_string.value == string_node.value:
            return None

        if not isinstance(first, cst.SimpleStatementLine):
            return None
        expr = first.body[0]
        if not isinstance(expr, cst.Expr):
            return None
        new_first = first.with_changes(body=[expr.with_changes(value=new_string)])
        return [new_first, *list(statements[1:])]

    def _format_indented_owner(self, updated_node: _OwnerT) -> _OwnerT:
        body = updated_node.body
        if not isinstance(body, cst.IndentedBlock):
            return updated_node
        indent = body.indent if isinstance(body.indent, str) else "    "
        new_statements = self._format_first_docstring_in_body(body.body, content_indent=indent)
        if new_statements is None:
            return updated_node
        return updated_node.with_changes(body=body.with_changes(body=new_statements))


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


def _docstring_simple_string(stmt: cst.BaseStatement) -> cst.SimpleString | None:
    if not isinstance(stmt, cst.SimpleStatementLine):
        return None
    if len(stmt.body) != 1:
        return None
    expr = stmt.body[0]
    if not isinstance(expr, cst.Expr) or not isinstance(expr.value, cst.SimpleString):
        return None
    return expr.value


def _encode_non_raw_line(line: str, *, quote: str) -> str:
    """Encode a logical line for a non-raw string literal.

    Triple-quoted docstrings may contain unescaped `"` or `'` matching the
    outer quote character; only the full delimiter is banned (checked by the
    caller). Escaping every matching quote would corrupt code examples inside
    Markdown fences.

    """
    if quote in _TRIPLE_QUOTES:
        return line
    single = quote[0]
    if single in line:
        return line.replace(single, f"\\{single}")
    return line


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


def _format_docstring_simple_string(
    string_node: cst.SimpleString,
    *,
    md_formatter: MdFormatter,
    content_indent: str,
) -> cst.SimpleString | None:
    """Format a multiline docstring SimpleString with Markdown + code-span rules."""
    prefix, quote = _literal_prefix_and_quote(string_node.value)
    if quote not in _TRIPLE_QUOTES:
        return None
    if any(char in prefix for char in _UNSUPPORTED_PREFIX_CHARS):
        return None

    content = _evaluate_string_literal(string_node.value)
    if content is None or "\n" not in content:
        return None

    cleaned = inspect.cleandoc(content)
    formatted = md_formatter.format(cleaned + "\n")
    formatted = PyDocstringFormatter.normalize_code_spans(formatted)
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


def _format_one_line_docstring(
    string_node: cst.SimpleString,
    *,
    md_formatter: MdFormatter,
) -> cst.SimpleString | None:
    """Apply prose fixes and code-span rules to a one-line docstring; keep one line."""
    prefix, quote = _literal_prefix_and_quote(string_node.value)
    if any(char in prefix for char in _UNSUPPORTED_PREFIX_CHARS):
        return None

    content = _evaluate_string_literal(string_node.value)
    if content is None or "\n" in content:
        return None

    new_content = content
    if md_formatter.options.apply_prose_fixes:
        new_content = _apply_checker_prose_fixes(new_content)
    new_content = PyDocstringFormatter.normalize_code_spans(new_content)
    # Keep a single physical line inside """...""" (prose fixes are line-based).
    if "\n" in new_content:
        new_content = " ".join(part.strip() for part in new_content.splitlines() if part.strip())
    new_content = new_content.strip()
    if new_content == content:
        return None

    is_raw = "r" in prefix.lower()
    if not is_raw and "\\" in new_content:
        prefix = _ensure_raw_prefix(prefix)
        is_raw = True

    body = new_content if is_raw else _encode_non_raw_line(new_content, quote=quote)
    if quote in body:
        return None
    return cst.SimpleString(value=f"{prefix}{quote}{body}{quote}")


def _normalize_prose_segment(segment: str) -> str:
    """Normalize quoted identifiers and bare `True`/`False`/`None` in a prose segment."""
    result = _QUOTED_CODE_RE.sub(lambda match: f"`{match.group(2)}`", segment)
    return _BARE_LITERAL_RE.sub(lambda match: f"`{match.group(1)}`", result)
