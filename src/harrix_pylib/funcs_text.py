"""General text helpers: keyboard layout, numbers, and safe arithmetic."""

from __future__ import annotations

import ast
import re
from typing import NoReturn

# Physical QWERTY <-> Russian JCUKEN key pairs (lowercase and uppercase).
_LAYOUT_PAIRS: tuple[tuple[str, str], ...] = (
    ("q", "\u0439"),
    ("w", "\u0446"),
    ("e", "\u0443"),
    ("r", "\u043a"),
    ("t", "\u0435"),
    ("y", "\u043d"),
    ("u", "\u0433"),
    ("i", "\u0448"),
    ("o", "\u0449"),
    ("p", "\u0437"),
    ("[", "\u0445"),
    ("]", "\u044a"),
    ("a", "\u0444"),
    ("s", "\u044b"),
    ("d", "\u0432"),
    ("f", "\u0430"),
    ("g", "\u043f"),
    ("h", "\u0440"),
    ("j", "\u043e"),
    ("k", "\u043b"),
    ("l", "\u0434"),
    (";", "\u0436"),
    ("'", "\u044d"),
    ("z", "\u044f"),
    ("x", "\u0447"),
    ("c", "\u0441"),
    ("v", "\u043c"),
    ("b", "\u0438"),
    ("n", "\u0442"),
    ("m", "\u044c"),
    (",", "\u0431"),
    (".", "\u044e"),
    ("`", "\u0451"),
    ("Q", "\u0419"),
    ("W", "\u0426"),
    ("E", "\u0423"),
    ("R", "\u041a"),
    ("T", "\u0415"),
    ("Y", "\u041d"),
    ("U", "\u0413"),
    ("I", "\u0428"),
    ("O", "\u0429"),
    ("P", "\u0417"),
    ("{", "\u0425"),
    ("}", "\u042a"),
    ("A", "\u0424"),
    ("S", "\u042b"),
    ("D", "\u0412"),
    ("F", "\u0410"),
    ("G", "\u041f"),
    ("H", "\u0420"),
    ("J", "\u041e"),
    ("K", "\u041b"),
    ("L", "\u0414"),
    (":", "\u0416"),
    ('"', "\u042d"),
    ("Z", "\u042f"),
    ("X", "\u0427"),
    ("C", "\u0421"),
    ("V", "\u041c"),
    ("B", "\u0418"),
    ("N", "\u0422"),
    ("M", "\u042c"),
    ("<", "\u0411"),
    (">", "\u042e"),
    ("~", "\u0401"),
)

_LAYOUT_SWAP: dict[str, str] = {}
for _en, _ru in _LAYOUT_PAIRS:
    _LAYOUT_SWAP[_en] = _ru
    _LAYOUT_SWAP[_ru] = _en


def autocomplete_match_tier(text: str, query: str) -> int | None:
    """Return best match tier for autocomplete, including EN/RU layout mistakes.

    Tiers: `0` exact, `1` starts-with, `2` contains. Returns `None` if neither the
    plain query nor its layout-swapped form matches `text`.

    Args:

    - `text` (`str`): Candidate string to match against.
    - `query` (`str`): User query, possibly typed on the wrong keyboard layout.

    Returns:

    - `int | None`: Best match tier, or `None` when there is no match.

    Example:

    ```python
    import harrix_pylib as h

    assert h.text.autocomplete_match_tier("Привет", "ghbdtn") == 0  # ignore: HP001
    assert h.text.autocomplete_match_tier("Finance", "fin") == 1
    ```

    """
    text_fold = text.casefold()
    query_fold = query.casefold()
    swapped_fold = swap_keyboard_layout(query).casefold()

    best: int | None = None
    for needle in (query_fold, swapped_fold):
        if not needle:
            continue
        tier = _plain_autocomplete_tier(text_fold, needle)
        if tier is not None and (best is None or tier < best):
            best = tier
    return best


def clean_number_text(text: str) -> str:
    """Remove spaces and replace subscript digits with ASCII digits.

    Args:

    - `text` (`str`): Raw string that may contain spaces and Unicode subscript digits.

    Returns:

    - `str`: String with spaces removed and ₀-₉ replaced by 0-9.

    Example:

    ```python
    import harrix_pylib as h

    assert h.text.clean_number_text("1 234.56") == "1234.56"
    assert h.text.clean_number_text("₁₂₃") == "123"
    ```

    """
    return (
        str(text)
        .replace(" ", "")
        .replace("₀", "0")
        .replace("₁", "1")
        .replace("₂", "2")
        .replace("₃", "3")
        .replace("₄", "4")
        .replace("₅", "5")
        .replace("₆", "6")
        .replace("₇", "7")
        .replace("₈", "8")
        .replace("₉", "9")
    )


def evaluate_arithmetic_expression(expression: str) -> float:
    """Safely evaluate a simple arithmetic expression (`+`, `-`, `*`, `/`, parentheses).

    Args:

    - `expression` (`str`): String containing a mathematical expression.

    Returns:

    - `float`: Calculated result.

    Raises:

    - `ValueError`: If the expression is empty, invalid, or unsafe.

    Example:

    ```python
    import harrix_pylib as h

    assert h.text.evaluate_arithmetic_expression("2 + 3 * 4") == 14.0
    assert h.text.evaluate_arithmetic_expression("1,5 + 0,5") == 2.0
    ```

    """
    expression = expression.replace(" ", "").replace(",", ".")
    if not expression:
        msg = "Expression is empty"
        raise ValueError(msg)

    if not re.match(r"^[0-9+\-*/().]+$", expression):
        msg = "Expression contains invalid characters"
        raise ValueError(msg)

    if expression.count("(") != expression.count(")"):
        msg = "Unbalanced parentheses"
        raise ValueError(msg)

    def _raise_value_error(msg: str) -> NoReturn:
        raise ValueError(msg)

    try:
        tree = ast.parse(expression, mode="eval")
        if not _is_safe_arithmetic_node(tree):
            _raise_value_error("Expression contains unsafe operations")
        code = compile(tree, "<string>", "eval")
        result = eval(code, {"__builtins__": {}}, {})  # noqa: S307
        if not isinstance(result, (int, float)):
            _raise_value_error("Expression does not evaluate to a number")
        return float(result)
    except SyntaxError as e:
        _raise_value_error(f"Invalid expression syntax: {e!s}")
    except ZeroDivisionError:
        _raise_value_error("Division by zero")
    except ValueError:
        raise
    except Exception as e:
        _raise_value_error(f"Invalid expression: {e!s}")


def swap_keyboard_layout(text: str) -> str:
    """Swap characters as if typed on the other EN/RU keyboard layout.

    Args:

    - `text` (`str`): Text typed on QWERTY or Russian JCUKEN.

    Returns:

    - `str`: Text with each mapped character swapped to the other layout.

    Example:

    ```python
    import harrix_pylib as h

    assert h.text.swap_keyboard_layout("qwerty") == "йцукен"  # ignore: HP001
    assert h.text.swap_keyboard_layout("йцукен") == "qwerty"  # ignore: HP001
    ```

    """
    return "".join(_LAYOUT_SWAP.get(char, char) for char in text)


def text_matches_autocomplete(text: str, query: str) -> bool:
    """Return `True` if query matches text for autocomplete, including layout mistakes.

    Args:

    - `text` (`str`): Candidate string to match against.
    - `query` (`str`): User query, possibly typed on the wrong keyboard layout.

    Returns:

    - `bool`: `True` when the query matches `text`.

    Example:

    ```python
    import harrix_pylib as h

    assert h.text.text_matches_autocomplete("Привет", "ghbdtn")  # ignore: HP001
    assert not h.text.text_matches_autocomplete("Привет", "xyz")  # ignore: HP001
    ```

    """
    return autocomplete_match_tier(text, query) is not None


def try_evaluate_arithmetic_expression(expression: str) -> tuple[float | None, str | None]:
    """Evaluate an expression and return `(value, None)` or `(None, error_message)`.

    Args:

    - `expression` (`str`): String containing a mathematical expression.

    Returns:

    - `tuple[float | None, str | None]`: Result and error message.

    Example:

    ```python
    import harrix_pylib as h

    value, error = h.text.try_evaluate_arithmetic_expression("10 / 2")
    assert value == 5.0 and error is None
    ```

    """
    try:
        return evaluate_arithmetic_expression(expression), None
    except ValueError as e:
        return None, str(e)


def _is_safe_arithmetic_node(node: ast.AST) -> bool:
    """Return `True` if the AST node is limited to safe arithmetic."""
    if isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float))
    if isinstance(node, ast.BinOp):
        return (
            isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div))
            and _is_safe_arithmetic_node(node.left)
            and _is_safe_arithmetic_node(node.right)
        )
    if isinstance(node, ast.UnaryOp):
        return isinstance(node.op, (ast.UAdd, ast.USub)) and _is_safe_arithmetic_node(node.operand)
    if isinstance(node, ast.Expression):
        return _is_safe_arithmetic_node(node.body)
    return False


def _plain_autocomplete_tier(text_fold: str, query_fold: str) -> int | None:
    """Return match tier for a single folded query, or `None` if no match."""
    if text_fold == query_fold:
        return 0
    if text_fold.startswith(query_fold):
        return 1
    if query_fold in text_fold:
        return 2
    return None
