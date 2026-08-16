---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `funcs_text.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `autocomplete_match_tier`](#-function-autocomplete_match_tier)
- [🔧 Function `clean_number_text`](#-function-clean_number_text)
- [🔧 Function `evaluate_arithmetic_expression`](#-function-evaluate_arithmetic_expression)
- [🔧 Function `swap_keyboard_layout`](#-function-swap_keyboard_layout)
- [🔧 Function `text_matches_autocomplete`](#-function-text_matches_autocomplete)
- [🔧 Function `try_evaluate_arithmetic_expression`](#-function-try_evaluate_arithmetic_expression)

</details>

## 🔧 Function `autocomplete_match_tier`

```python
def autocomplete_match_tier(text: str, query: str) -> int | None
```

Return best match tier for autocomplete, including EN/RU layout mistakes.

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

<details>
<summary>Code:</summary>

```python
def autocomplete_match_tier(text: str, query: str) -> int | None:
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
```

</details>

## 🔧 Function `clean_number_text`

```python
def clean_number_text(text: str) -> str
```

Remove spaces and replace subscript digits with ASCII digits.

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

<details>
<summary>Code:</summary>

```python
def clean_number_text(text: str) -> str:
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
```

</details>

## 🔧 Function `evaluate_arithmetic_expression`

```python
def evaluate_arithmetic_expression(expression: str) -> float
```

Safely evaluate a simple arithmetic expression (`+`, `-`, `*`, `/`, parentheses).

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

<details>
<summary>Code:</summary>

```python
def evaluate_arithmetic_expression(expression: str) -> float:
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
```

</details>

## 🔧 Function `swap_keyboard_layout`

```python
def swap_keyboard_layout(text: str) -> str
```

Swap characters as if typed on the other EN/RU keyboard layout.

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

<details>
<summary>Code:</summary>

```python
def swap_keyboard_layout(text: str) -> str:
    return "".join(_LAYOUT_SWAP.get(char, char) for char in text)
```

</details>

## 🔧 Function `text_matches_autocomplete`

```python
def text_matches_autocomplete(text: str, query: str) -> bool
```

Return `True` if query matches text for autocomplete, including layout mistakes.

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

<details>
<summary>Code:</summary>

```python
def text_matches_autocomplete(text: str, query: str) -> bool:
    return autocomplete_match_tier(text, query) is not None
```

</details>

## 🔧 Function `try_evaluate_arithmetic_expression`

```python
def try_evaluate_arithmetic_expression(expression: str) -> tuple[float | None, str | None]
```

Evaluate an expression and return `(value, None)` or `(None, error_message)`.

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

<details>
<summary>Code:</summary>

```python
def try_evaluate_arithmetic_expression(expression: str) -> tuple[float | None, str | None]:
    try:
        return evaluate_arithmetic_expression(expression), None
    except ValueError as e:
        return None, str(e)
```

</details>
