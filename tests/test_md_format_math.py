"""Tests for LaTeX math content formatting inside MdFormatter."""

from __future__ import annotations

from harrix_pylib.md_format import MdFormatter
from harrix_pylib.md_format.math_format import _format_math_content


def _format(
    text: str,
    *,
    format_math: bool = True,
    apply_prose_fixes: bool = False,
) -> str:
    return MdFormatter(
        end_of_line="lf",
        apply_prose_fixes=apply_prose_fixes,
        format_math=format_math,
    ).format(text)


def test_format_math_content_spaces_around_operators() -> None:
    assert _format_math_content("a+b=c") == "a + b = c"


def test_format_math_content_keeps_unary_minus() -> None:
    assert _format_math_content("-x+y") == "-x + y"
    assert _format_math_content("x^{-2}") == "x^{-2}"
    assert _format_math_content("x_{i-1}") == "x_{i-1}"


def test_format_math_content_normalizes_frac_args() -> None:
    assert _format_math_content(r"\frac{ a }{ b }") == r"\frac{a}{b}"
    assert _format_math_content(r"\dfrac{ x + 1 }{ y }") == r"\dfrac{x + 1}{y}"


def test_format_math_content_normalizes_left_right() -> None:
    assert _format_math_content(r"\left (x\right )") == r"\left(x\right)"


def test_format_math_content_preserves_text_command_body() -> None:
    assert _format_math_content(r"\text{a+b} + c") == r"\text{a+b} + c"


def test_format_math_content_layouts_bmatrix_display() -> None:
    result = _format_math_content(r"\begin{bmatrix}1&2\\3&4\end{bmatrix}", display=True)
    assert result == "\\begin{bmatrix}\n  1 & 2 \\\\\n  3 & 4\n\\end{bmatrix}"


def test_format_math_content_layouts_align_display() -> None:
    result = _format_math_content(r"\begin{align*}a&=b\\c&=d\end{align*}", display=True)
    assert result == "\\begin{align*}\n  a &= b \\\\\n  c &= d\n\\end{align*}"


def test_format_math_content_indents_nested_environments_by_depth() -> None:
    source = (
        r"\begin{minipage}{0.5\textwidth}"
        "\n"
        "equation:\n"
        r"\begin{equation*}"
        "\n"
        "z_0 = d = 0\n"
        r"\end{equation*}"
        "\n"
        "align:\n"
        r"\begin{align*}"
        "\n"
        r"z_0 &= d = 0 \\"
        "\n"
        r"z_{n+1} &= z_n^2+c"
        "\n"
        r"\end{align*}"
        "\n"
        "eqnarray:\n"
        r"\begin{eqnarray*}"
        "\n"
        r"z_0 &=& d = 0 \\"
        "\n"
        r"z_{n+1} &=& z_n^2+c"
        "\n"
        r"\end{eqnarray*}"
        "\n"
        r"\end{minipage}"
    )
    expected = (
        "\\begin{minipage}{0.5\\textwidth}\n"
        "  equation:\n"
        "  \\begin{equation*}\n"
        "    z_0 = d = 0\n"
        "  \\end{equation*}\n"
        "  align:\n"
        "  \\begin{align*}\n"
        "    z_0 &= d = 0 \\\\\n"
        "    z_{n+1} &= z_n^2 + c\n"
        "  \\end{align*}\n"
        "  eqnarray:\n"
        "  \\begin{eqnarray*}\n"
        "    z_0 &=& d = 0 \\\\\n"
        "    z_{n+1} &=& z_n^2 + c\n"
        "  \\end{eqnarray*}\n"
        "\\end{minipage}"
    )
    result = _format_math_content(source, display=True)
    assert result == expected
    assert _format_math_content(result, display=True) == result


def test_format_math_content_wraps_left_right_around_environments() -> None:
    source = (
        r"\left( \begin{array}{ccc}"
        "\n"
        r"a & b & c \\"
        "\n"
        r"d & e & f \\"
        "\n"
        r"g & h & i"
        "\n"
        r"\end{array} \right)"
    )
    expected = (
        "\\left(\n"
        "  \\begin{array}{ccc}\n"
        "    a & b & c \\\\\n"
        "    d & e & f \\\\\n"
        "    g & h & i\n"
        "  \\end{array}\n"
        "\\right)"
    )
    result = _format_math_content(source, display=True)
    assert result == expected
    assert _format_math_content(result, display=True) == result


def test_format_math_content_wraps_left_lbrace_aligned() -> None:
    source = r"=\left\lbrace \begin{aligned}11 \\ 22\end{aligned}\right."
    expected = "= \\left\\lbrace\n  \\begin{aligned}\n    11 \\\\\n    22\n  \\end{aligned}\n\\right."
    result = _format_math_content(source, display=True)
    assert result == expected


def test_format_math_content_keeps_compact_left_right_without_env() -> None:
    assert _format_math_content(r"\left(x + y\right)", display=True) == r"\left(x + y\right)"


def test_format_math_content_blank_line_between_sibling_environments() -> None:
    source = (
        r"\begin{equation*}"
        "\n"
        "a = 1\n"
        r"\end{equation*}"
        "\n"
        r"\begin{equation*}"
        "\n"
        "b = 2\n"
        r"\end{equation*}"
    )
    expected = "\\begin{equation*}\n  a = 1\n\\end{equation*}\n\n\\begin{equation*}\n  b = 2\n\\end{equation*}"
    result = _format_math_content(source, display=True)
    assert result == expected
    assert _format_math_content(result, display=True) == result


def test_format_math_content_inline_skips_environment_layout() -> None:
    source = r"\begin{bmatrix}1&2\\3&4\end{bmatrix}"
    result = _format_math_content(source, display=False)
    assert "\n" not in result
    assert result == r"\begin{bmatrix}1 & 2 \\ 3 & 4\end{bmatrix}"


def test_formatter_formats_inline_math() -> None:
    result = _format("$a+b=c$\n")
    assert "$a + b = c$" in result


def test_formatter_formats_display_bmatrix() -> None:
    source = "$$\n\\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}\n$$\n"
    result = _format(source)
    assert "\\begin{bmatrix}" in result
    assert "  1 & 2 \\\\" in result
    assert "  3 & 4" in result


def test_formatter_can_disable_math_formatting() -> None:
    source = "$a+b$\n"
    result = _format(source, format_math=False)
    assert "$a+b$" in result


def test_formatter_math_formatting_is_idempotent() -> None:
    source = "$$\n\\begin{align*}a&=b\\\\c&=d\\end{align*}\n$$\n"
    once = _format(source)
    twice = _format(once)
    assert once == twice


def test_formatter_preserves_hyphens_inside_formatted_math() -> None:
    source = (
        "Prose uses 1 - 2.\n\n"
        "$$\n"
        "5\\left(-\\sqrt{1 - x^{2} - \\left(y - \\lvert x\\rvert\\right)^{2}}\\right),"
        "\n"
        "$$\n\n"
        "Inline $a - b$ stays.\n"
    )
    result = _format(source, apply_prose_fixes=True)
    assert "1 — 2" in result
    assert "1 - x^{2} - \\left(y - \\lvert x\\rvert\\right)^{2}" in result
    assert "$a - b$" in result
