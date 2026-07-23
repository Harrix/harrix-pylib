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


def test_format_math_content_keeps_compound_word_hyphens() -> None:
    assert _format_math_content("pdf-file") == "pdf-file"
    assert _format_math_content("bib-document") == "bib-document"
    assert _format_math_content("pdf-файле") == "pdf-файле"
    assert _format_math_content("bib-документ") == "bib-документ"
    assert _format_math_content(r"\KwData{pdf-файле}") == r"\KwData{pdf-файле}"
    # Single-letter math identifiers still get minus spacing.
    assert _format_math_content("a-b") == "a - b"


def test_format_math_content_preserves_tex_dashes_and_russian_ordinals() -> None:
    assert _format_math_content(r'\LaTeX{} "--- это для \TeX{}') == r'\LaTeX{} "--- это для \TeX{}'
    assert _format_math_content("в 1984-м году") == "в 1984-м году"
    assert _format_math_content("a--b") == "a--b"
    comment = r"\hspace*{.2em}% < ------------- This is where the rule starts from"
    assert _format_math_content(comment) == comment
    assert "------------ -" not in _format_math_content(comment)


def test_formatter_leaves_latex_document_tex_fence_unchanged() -> None:
    source = (
        "```tex\n"
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        '\\LaTeX{} "--- это своего рода препроцессор текста для \\TeX{} "---\n'
        "программы. В 1984-м году.\n"
        "\\end{document}\n"
        "```\n"
    )
    result = _format(source)
    assert '"--- это' in result
    assert "1984-м" in result
    assert '" - --' not in result
    assert "1984 - м" not in result
    assert "  \\LaTeX{}" not in result


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


def test_format_math_content_keeps_digits_after_protected_commands() -> None:
    assert _format_math_content(r"\mathrm{R}2") == r"\mathrm{R}2"
    assert _format_math_content(r"\mathbf{v}0") == r"\mathbf{v}0"
    assert _format_math_content(r"\text{a}123 + b") == r"\text{a}123 + b"


def test_format_math_content_preserves_spaces_in_command_args() -> None:
    assert _format_math_content(r"\KwData{this text}") == r"\KwData{this text}"
    assert _format_math_content(r"\KwResult{how to write algorithm with LaTeX2e}") == (
        r"\KwResult{how to write algorithm with LaTeX2e}"
    )


def test_format_math_content_preserves_algorithm_spaces_and_relative_indent() -> None:
    source = (
        "\\begin{algorithm}[H]\n"
        "  \\SetAlgoLined\n"
        "  \\KwData{this text}\n"
        "  \\KwResult{how to write algorithm with LaTeX2e}\n"
        "  initialization;\n"
        "  \\While{not at end of this document}{\n"
        "    read current;\n"
        "    \\eIf{understand}{\n"
        "      go to next section;\n"
        "    }{\n"
        "      go back to the beginning of current section;\n"
        "    }\n"
        "  }\n"
        "  \\caption{How to write algorithms}\n"
        "\\end{algorithm}"
    )
    result = _format_math_content(source, display=True)
    assert "\\KwData{this text}" in result
    assert "\\KwResult{how to write algorithm with LaTeX2e}" in result
    assert "not at end of this document" in result
    assert "go to next section" in result
    assert "\\caption{How to write algorithms}" in result
    lines = [line for line in result.splitlines() if line.strip()]
    kw_data = next(line for line in lines if "\\KwData" in line)
    read_current = next(line for line in lines if "read current" in line)
    go_next = next(line for line in lines if "go to next section" in line)
    assert len(kw_data) - len(kw_data.lstrip(" ")) < len(read_current) - len(read_current.lstrip(" "))
    assert len(read_current) - len(read_current.lstrip(" ")) < len(go_next) - len(go_next.lstrip(" "))


def test_formatter_preserves_spaces_in_tex_fence() -> None:
    source = "```tex\n\\KwData{this text}\n\\While{not at end}{\n  read current;\n}\n```\n"
    result = _format(source)
    assert "\\KwData{this text}" in result
    assert "not at end" in result
    assert "read current" in result


def test_format_math_content_layouts_bmatrix_display() -> None:
    result = _format_math_content(r"\begin{bmatrix}1&2\\3&4\end{bmatrix}", display=True)
    assert result == "\\begin{bmatrix}\n  1 & 2 \\\\\n  3 & 4\n\\end{bmatrix}"


def test_format_math_content_layouts_align_display() -> None:
    result = _format_math_content(r"\begin{align*}a&=b\\c&=d\end{align*}", display=True)
    assert result == "\\begin{align*}\n  a &= b \\\\\n  c &= d\n\\end{align*}"


def test_format_math_content_aligns_columns_by_ampersand() -> None:
    source = r"\begin{array}{cc}a & bbb \\ cc & d\end{array}"
    expected = "\\begin{array}{cc}\n  a  & bbb \\\\\n  cc & d\n\\end{array}"
    result = _format_math_content(source, display=True)
    assert result == expected
    assert _format_math_content(result, display=True) == result

    align = r"\begin{align*}x&=1\\long&=2\end{align*}"
    align_expected = "\\begin{align*}\n  x    &= 1 \\\\\n  long &= 2\n\\end{align*}"
    assert _format_math_content(align, display=True) == align_expected


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
        "    z_0     &= d = 0 \\\\\n"
        "    z_{n+1} &= z_n^2 + c\n"
        "  \\end{align*}\n"
        "  eqnarray:\n"
        "  \\begin{eqnarray*}\n"
        "    z_0     &=& d = 0 \\\\\n"
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


def test_formatter_formats_latex_fenced_code_blocks() -> None:
    source = "```latex\n\\begin{bmatrix}1&2\\\\3&4\\end{bmatrix}\n```\n"
    result = _format(source)
    assert "```latex" in result
    assert "  1 & 2 \\\\" in result
    assert "  3 & 4" in result
    assert _format(result) == result


def test_formatter_keeps_digits_after_protected_commands_in_tex_fence() -> None:
    source = "```tex\n\\mathrm{R}2\n```\n"
    result = _format(source)
    assert "\\mathrm{R}2" in result
    assert _format(result) == result


def test_formatter_can_disable_code_block_formatting() -> None:
    source = "```latex\na+b=c\n```\n"
    result = MdFormatter(
        end_of_line="lf",
        apply_prose_fixes=False,
        format_code_blocks=False,
    ).format(source)
    assert "```latex\na+b=c\n```" in result.replace("\r\n", "\n")


def test_formatter_math_formatting_is_idempotent() -> None:
    source = "$$\n\\begin{align*}a&=b\\\\c&=d\\end{align*}\n$$\n"
    once = _format(source)
    twice = _format(once)
    assert once == twice


def test_formatter_flalign_placeholder_backslash_before_newline_is_idempotent() -> None:
    """Lone `\\` before EOL (docs placeholder): normalize indent, stay idempotent."""
    source = "```tex\n\\State < text > \\begin{flalign*}\n     < formula > \\\n  < formula >\n\\end{flalign*}\n```\n"
    once = _format(source)
    twice = _format(once)
    assert once == twice
    normalized = once.replace("\r\n", "\n")
    assert "\\begin{flalign*}\n  < formula > \\\n  < formula >\n\\end{flalign*}" in normalized

    source_amp = (
        "```tex\n\\State < text > \\begin{flalign*}\n     & < formula > \\\n  & < formula >\n\\end{flalign*}\n```\n"
    )
    once_amp = _format(source_amp)
    assert _format(once_amp) == once_amp
    normalized_amp = once_amp.replace("\r\n", "\n")
    assert "\\begin{flalign*}\n  & < formula > \\\n  & < formula >\n\\end{flalign*}" in normalized_amp


def test_formatter_flalign_with_real_row_breaks_aligns_cells() -> None:
    source = "```tex\n\\begin{flalign*}a&=b\\\\c&=d\\end{flalign*}\n```\n"
    result = _format(source)
    assert "\\begin{flalign*}\n  a &= b \\\\\n  c &= d\n\\end{flalign*}" in result.replace("\r\n", "\n")
    assert _format(result) == result


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
