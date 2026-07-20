"""Tests for abbreviation_data loader (H006 / H021 databases)."""

from harrix_pylib.abbreviation_data import (
    is_spaced_multipart,
    load_abbreviation_data,
    mask_abbreviations,
    unspaced_variant,
)


def test_load_abbreviation_data_classifies_forms() -> None:
    data = load_abbreviation_data()
    assert "т. е." in data.all_forms
    assert "e.g." in data.all_forms
    assert "incl." in data.all_forms
    assert "excl." in data.all_forms
    assert "т. е." in data.dotted_forms
    assert "т. е." in data.spaced_forms
    assert "англ." in data.dotted_forms
    assert "англ." not in data.spaced_forms
    assert data.h006_pairs["т.е."] == "т. е."
    assert data.h006_pairs["в т.ч."] == "в т. ч."
    assert data.h021_mask_pattern is not None


def test_spaced_multipart_and_unspaced() -> None:
    assert is_spaced_multipart("т. е.")
    assert is_spaced_multipart("в т. ч.")
    assert is_spaced_multipart("мм рт. ст.")
    assert not is_spaced_multipart("англ.")
    assert not is_spaced_multipart("кг")
    assert unspaced_variant("т. е.") == "т.е."
    assert unspaced_variant("в т. ч.") == "в т.ч."


def test_mask_abbreviations_removes_periods() -> None:
    data = load_abbreviation_data()
    masked = mask_abbreviations("Используют т. е. так и e.g. this.", data.h021_mask_pattern)
    assert "т. е." not in masked
    assert "e.g." not in masked
    assert "так" in masked
    assert "this" in masked
