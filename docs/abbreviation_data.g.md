---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `abbreviation_data.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AbbreviationData`](#️-class-abbreviationdata)
- [🔧 Function `is_spaced_multipart`](#-function-is_spaced_multipart)
- [🔧 Function `load_abbreviation_data`](#-function-load_abbreviation_data)
- [🔧 Function `mask_abbreviations`](#-function-mask_abbreviations)
- [🔧 Function `normalize_abbrev`](#-function-normalize_abbrev)
- [🔧 Function `unspaced_variant`](#-function-unspaced_variant)

</details>

## 🏛️ Class `AbbreviationData`

```python
class AbbreviationData
```

Compiled abbreviation data for H006 spacing and H021 masking.

<details>
<summary>Code:</summary>

```python
class AbbreviationData:

    all_forms: tuple[str, ...]
    dotted_forms: tuple[str, ...]
    spaced_forms: tuple[str, ...]
    h006_pairs: dict[str, str]
    h021_mask_pattern: re.Pattern[str] | None
    h006_patterns: dict[str, tuple[re.Pattern[str], str]]
```

</details>

## 🔧 Function `is_spaced_multipart`

```python
def is_spaced_multipart(form: str) -> bool
```

Return `True` if form is a multi-part dotted abbrev with spaces (H006 candidate).

<details>
<summary>Code:</summary>

```python
def is_spaced_multipart(form: str) -> bool:
    if "." not in form or " " not in form:
        return False
    # Space after a period, or space before a dotted token
    return bool(re.search(r"\.\s+\S", form) or re.search(r"\s+\S+\.", form))
```

</details>

## 🔧 Function `load_abbreviation_data`

```python
def load_abbreviation_data() -> AbbreviationData
```

Load RU+EN abbreviation JSON (always both; not gated by document lang).

<details>
<summary>Code:</summary>

```python
def load_abbreviation_data() -> AbbreviationData:
    package = "harrix_pylib.data"
    forms = _dedupe_casefold(
        [
            *_load_json_forms(package, "abbreviations_ru.json"),
            *_load_json_forms(package, "abbreviations_en.json"),
        ]
    )

    dotted = [f for f in forms if "." in f]
    spaced = [f for f in dotted if is_spaced_multipart(f)]

    h006_pairs: dict[str, str] = {}
    for form in spaced:
        incorrect = unspaced_variant(form)
        if incorrect != form:
            # Prefer first canonical if collisions
            h006_pairs.setdefault(incorrect, form)
            # Capitalized first-letter variant for sentence starts
            if form[:1].islower():
                cap_incorrect = incorrect[:1].upper() + incorrect[1:]
                cap_correct = form[:1].upper() + form[1:]
                if cap_incorrect != cap_correct:
                    h006_pairs.setdefault(cap_incorrect, cap_correct)

    # Longest-first so longer multi-part abbrevs win over shorter ones
    dotted_sorted = sorted(dotted, key=len, reverse=True)
    if dotted_sorted:
        alternation = "|".join(re.escape(f) for f in dotted_sorted)
        # Case-insensitive matching for dotted forms
        h021_mask_pattern: re.Pattern[str] | None = re.compile(
            rf"{_BOUNDARY_LOOKBEHIND}(?:{alternation}){_BOUNDARY_LOOKAHEAD}",
            re.IGNORECASE,
        )
    else:
        h021_mask_pattern = None

    h006_patterns = {
        incorrect: (_word_boundary_pattern(incorrect), correct) for incorrect, correct in h006_pairs.items()
    }

    return AbbreviationData(
        all_forms=tuple(forms),
        dotted_forms=tuple(dotted_sorted),
        spaced_forms=tuple(spaced),
        h006_pairs=h006_pairs,
        h021_mask_pattern=h021_mask_pattern,
        h006_patterns=h006_patterns,
    )
```

</details>

## 🔧 Function `mask_abbreviations`

```python
def mask_abbreviations(text: str, pattern: re.Pattern[str] | None, placeholder: str = "·") -> str
```

Replace known dotted abbreviations with same-length placeholders for H021.

<details>
<summary>Code:</summary>

```python
def mask_abbreviations(text: str, pattern: re.Pattern[str] | None, placeholder: str = "\u00b7") -> str:
    if pattern is None:
        return text

    def _repl(match: re.Match[str]) -> str:
        return placeholder * len(match.group(0))

    return pattern.sub(_repl, text)
```

</details>

## 🔧 Function `normalize_abbrev`

```python
def normalize_abbrev(text: str) -> str
```

Normalize soft hyphens and trim whitespace.

<details>
<summary>Code:</summary>

```python
def normalize_abbrev(text: str) -> str:
    return text.replace(SOFT_HYPHEN, "-").strip()
```

</details>

## 🔧 Function `unspaced_variant`

```python
def unspaced_variant(form: str) -> str
```

Collapse spaces that follow periods inside multi-part dotted abbreviations.

<details>
<summary>Code:</summary>

```python
def unspaced_variant(form: str) -> str:
    return re.sub(r"\.\s+", ".", form)
```

</details>
