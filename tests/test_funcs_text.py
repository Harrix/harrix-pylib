"""Tests for the text module of harrix_pylib."""

import pytest

import harrix_pylib as h

_TIER_CONTAINS = 2
_TIER_EXACT = 0
_TIER_STARTS = 1


def test_autocomplete_match_tier() -> None:
    assert h.text.autocomplete_match_tier("Привет", "ghbdtn") == _TIER_EXACT
    assert h.text.autocomplete_match_tier("Finance", "аштфтсу") == _TIER_EXACT
    assert h.text.autocomplete_match_tier("Привет мир", "ghbd") == _TIER_STARTS
    assert h.text.autocomplete_match_tier("Hello Привет", "ghbdtn") == _TIER_CONTAINS
    assert h.text.autocomplete_match_tier("Привет", "привет") == _TIER_EXACT
    assert h.text.autocomplete_match_tier("Привет мир", "прив") == _TIER_STARTS
    assert h.text.autocomplete_match_tier("Привет", "xyz") is None


def test_clean_number_text() -> None:
    assert h.text.clean_number_text("1 234.56") == "1234.56"
    assert h.text.clean_number_text("₁₂₃₄₅₆₇₈₉") == "123456789"
    assert h.text.clean_number_text("  ₁ 2 ₃  ") == "123"


def test_evaluate_arithmetic_expression() -> None:
    assert h.text.evaluate_arithmetic_expression("2 + 3 * 4") == float(2 + 3 * 4)
    assert h.text.evaluate_arithmetic_expression("1,5 + 0,5") == float(1.5 + 0.5)
    assert h.text.evaluate_arithmetic_expression("(10 - 4) / 2") == float((10 - 4) / 2)
    with pytest.raises(ValueError, match="empty"):
        h.text.evaluate_arithmetic_expression("   ")
    with pytest.raises(ValueError, match="invalid characters"):
        h.text.evaluate_arithmetic_expression("2 + abc")
    with pytest.raises(ValueError, match="Division by zero"):
        h.text.evaluate_arithmetic_expression("1 / 0")


def test_swap_keyboard_layout() -> None:
    assert h.text.swap_keyboard_layout("qwerty") == "йцукен"
    assert h.text.swap_keyboard_layout("йцукен") == "qwerty"
    assert h.text.swap_keyboard_layout("abc 123") == "фис 123"


def test_text_matches_autocomplete() -> None:
    assert h.text.text_matches_autocomplete("Привет", "ghbdtn")
    assert not h.text.text_matches_autocomplete("Привет", "xyz")


def test_try_evaluate_arithmetic_expression() -> None:
    value, error = h.text.try_evaluate_arithmetic_expression("10 / 2")
    assert value == float(10 / 2)
    assert error is None
    value, error = h.text.try_evaluate_arithmetic_expression("oops")
    assert value is None
    assert error is not None
