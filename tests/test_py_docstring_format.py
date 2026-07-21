"""Tests for Markdown formatting inside Python docstrings."""

from __future__ import annotations

import ast
import re
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h
from harrix_pylib.py_docstring_format import PyDocstringFormatter

_NON_RAW_SOURCE = '''\
def example(text: str) -> str:
    """Format something.

    Mentions _private and *star* and line
    0. alone on its own line.

    Args:

    - `text` (`str`): Input.

    Returns:

    - `str`: Output.
    """
    return text
'''

_RAW_SOURCE = '''\
def example() -> None:
    r"""Mentions _private name.

    More text about \\* escapes.
    """
    return None
'''

_PLAIN_SOURCE = '''\
def example() -> None:
    """Plain summary without special chars.

    Second paragraph.
    """
    return None
'''


def _syntax_warnings(source: str) -> list[str]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", SyntaxWarning)
        compile(source, "<test>", "exec")
    return [str(item.message) for item in caught if issubclass(item.category, SyntaxWarning)]


def _closing_quote_has_blank_before(source: str) -> bool:
    """Return whether a multiline docstring ends with a blank line before closing quotes."""
    return bool(re.search(r"\n\n[ \t]*(?:r)?(\"\"\"|''')", source))


def test_normalize_code_spans_wraps_literals_and_quoted_idents() -> None:
    text = (
        "Return True if ready. Defaults to False.\n"
        "\n"
        "Requires 'transliterate'. Code `True` stays. Defaults to \"img\".\n"
        "\n"
        "```python\n"
        "flag = True\n"
        "```\n"
    )
    out = PyDocstringFormatter.normalize_code_spans(text)
    assert "Return `True` if ready. Defaults to `False`." in out
    assert "Requires `transliterate`." in out
    assert "Defaults to `img`." in out
    assert "Code `True` stays." in out
    assert "flag = True" in out


def test_py_docstring_formatter_format_source() -> None:
    source = '''\
def ready() -> bool:
    """Return True if ready."""
    return True
'''
    after = PyDocstringFormatter().format(source)
    assert '"""Return `True` if ready."""' in after


def test_py_docstring_formatter_normalizes_one_line_code_spans() -> None:
    source = '''\
def ready() -> bool:
    """Return True if ready."""
    return True
'''
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(source, encoding="utf-8")
        PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")
        assert '"""Return `True` if ready."""' in after


def test_py_docstring_formatter_applies_prose_fixes_on_one_line() -> None:
    source = '''\
def edit() -> None:
    """Edit an existing markdown entry - use the form."""
    return None
'''
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(source, encoding="utf-8")
        PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")
        assert '"""Edit an existing Markdown entry — use the form."""' in after
        # Still a single-line docstring (opening and closing quotes on one line).
        assert re.search(
            r'^\s+"""Edit an existing Markdown entry — use the form\."""\s*$',
            after,
            re.MULTILINE,
        )


def test_py_docstring_formatter_restores_trailing_blank_and_args_shape() -> None:
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(_NON_RAW_SOURCE, encoding="utf-8")
        h.py.PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")

        assert _syntax_warnings(after) == []
        assert "Args:\n\n" in after or "Args:\r\n\r\n" in after
        assert "Returns:\n\n" in after or "Returns:\r\n\r\n" in after
        assert re.search(r'Returns:\n\n\s+- `str`: Output\.\n\n\s+"""', after) or re.search(
            r"Returns:\n\n\s+- `str`: Output\.\n\n\s+r?\"\"\"", after
        )


def test_py_docstring_formatter_adds_r_prefix_for_md_escapes() -> None:
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(_NON_RAW_SOURCE, encoding="utf-8")
        h.py.PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")

        assert _syntax_warnings(after) == []
        assert 'r"""' in after or "r'''" in after
        # Single-backslash MD escapes in raw source (not doubled).
        assert r"\_" in after or r"\*" in after or r"\." in after
        assert r"\\_" not in after
        assert r"\\*" not in after

        module = ast.parse(after)
        first = module.body[0]
        assert isinstance(first, ast.FunctionDef)
        docstring = ast.get_docstring(first)
        assert docstring is not None
        assert "_private" in docstring or r"\_private" in docstring or "private" in docstring


def test_py_docstring_formatter_keeps_raw_prefix() -> None:
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(_RAW_SOURCE, encoding="utf-8")
        h.py.PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")

        assert _syntax_warnings(after) == []
        assert 'r"""' in after
        assert r"\_" in after or "_private" in after


def test_py_docstring_formatter_keeps_quotes_in_code_fences() -> None:
    source = '''\
def example() -> None:
    """Show path example.

    ```python
    md_folder = "C:/GitHub/harrix.dev/content"
    ```

    """
    return None
'''
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(source, encoding="utf-8")
        h.py.PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")

        assert 'md_folder = "C:/GitHub/harrix.dev/content"' in after
        assert '\\"' not in after
        assert _syntax_warnings(after) == []


def test_py_docstring_formatter_skips_eol_only_rewrite() -> None:
    """Do not rewrite a file solely to convert CRLF to LF when docstrings are unchanged."""
    source = '''\
def example() -> None:
    """Plain summary without special chars.

    Second paragraph.

    """
    return None
'''
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_bytes(source.replace("\n", "\r\n").encode("utf-8"))
        assert b"\r\n" in path.read_bytes()
        # Format once with LF so docstring body matches formatter output.
        path.write_text(source, encoding="utf-8", newline="\n")
        h.py.PyDocstringFormatter().format_file(path)
        stable = path.read_text(encoding="utf-8")
        path.write_bytes(stable.replace("\n", "\r\n").encode("utf-8"))
        msg = h.py.PyDocstringFormatter().format_file(path)
        assert msg == "File is not changed."
        assert b"\r\n" in path.read_bytes()


def test_py_docstring_formatter_writes_lf_when_content_changes() -> None:
    """When docstrings change, persist the file with LF even if input used CRLF."""
    source = '''\
def example() -> None:
    """Plain summary without special chars.
    Second paragraph.
    """
    return None
'''
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_bytes(source.replace("\n", "\r\n").encode("utf-8"))
        msg = h.py.PyDocstringFormatter().format_file(path)
        after = path.read_bytes()
        assert "formatted" in msg
        assert b"\r\n" not in after
        assert after.count(b"\r") == 0


def test_py_docstring_formatter_keeps_non_raw_without_backslashes() -> None:
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "example.py"
        path.write_text(_PLAIN_SOURCE, encoding="utf-8")
        h.py.PyDocstringFormatter().format_file(path)
        after = path.read_text(encoding="utf-8")

        assert _syntax_warnings(after) == []
        # No MD escapes → stay non-raw (no leading r on the docstring).
        assert 'r"""' not in after
        assert '"""Plain summary' in after
        assert _closing_quote_has_blank_before(after)
