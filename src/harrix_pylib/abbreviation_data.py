"""Load packaged abbreviation databases for MdChecker (H006 / H021)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

SOFT_HYPHEN = "\u00ad"
_BOUNDARY_LOOKBEHIND = r"(?<![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001  # ignore: HP001
_BOUNDARY_LOOKAHEAD = r"(?![a-zA-Zа-яА-ЯёЁ0-9_])"  # noqa: RUF001  # ignore: HP001


@dataclass(frozen=True, slots=True)
class AbbreviationData:
    """Compiled abbreviation data for H006 spacing and H021 masking."""

    all_forms: tuple[str, ...]
    dotted_forms: tuple[str, ...]
    spaced_forms: tuple[str, ...]
    h006_pairs: dict[str, str]
    h021_mask_pattern: re.Pattern[str] | None
    h006_patterns: dict[str, tuple[re.Pattern[str], str]]


def is_spaced_multipart(form: str) -> bool:
    """Return `True` if form is a multi-part dotted abbrev with spaces (H006 candidate).

    Args:

    - `form` (`str`): Abbreviation form to inspect, for example `e. g.`.

    Returns:

    - `bool`: `True` when the form contains both a period and a space.

    """
    if "." not in form or " " not in form:
        return False
    # Space after a period, or space before a dotted token
    return bool(re.search(r"\.\s+\S", form) or re.search(r"\s+\S+\.", form))


@lru_cache(maxsize=1)
def load_abbreviation_data() -> AbbreviationData:
    """Load RU+EN abbreviation JSON (always both; not gated by document lang).

    Returns:

    - `AbbreviationData`: Compiled forms and patterns, cached after the first call.

    """
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


def mask_abbreviations(text: str, pattern: re.Pattern[str] | None, placeholder: str = "\u00b7") -> str:
    """Replace known dotted abbreviations with same-length placeholders for H021.

    Args:

    - `text` (`str`): Text to mask.
    - `pattern` (`re.Pattern[str] | None`): Compiled abbreviation pattern. `None` returns `text` as is.
    - `placeholder` (`str`): Single character used for masking. Defaults to `·`.

    Returns:

    - `str`: Text with abbreviations replaced by placeholders of the same length.

    """
    if pattern is None:
        return text

    def _repl(match: re.Match[str]) -> str:
        return placeholder * len(match.group(0))

    return pattern.sub(_repl, text)


def normalize_abbrev(text: str) -> str:
    """Normalize soft hyphens and trim whitespace.

    Args:

    - `text` (`str`): Raw abbreviation form.

    Returns:

    - `str`: Form with soft hyphens replaced by `-` and outer whitespace removed.

    """
    return text.replace(SOFT_HYPHEN, "-").strip()


def unspaced_variant(form: str) -> str:
    """Collapse spaces that follow periods inside multi-part dotted abbreviations.

    Args:

    - `form` (`str`): Canonical abbreviation form, for example `e. g.`.

    Returns:

    - `str`: Form without spaces after periods, for example `e.g.`.

    """
    return re.sub(r"\.\s+", ".", form)


def _dedupe_casefold(forms: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for form in forms:
        key = form.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(form)
    return out


def _load_json_forms(package: str, filename: str) -> list[str]:
    root = resources.files(package)
    text = (root / filename).read_text(encoding="utf-8")
    payload = json.loads(text)
    forms = payload.get("abbreviations", [])
    if not isinstance(forms, list):
        msg = f"{filename}: 'abbreviations' must be a list"
        raise TypeError(msg)
    return [normalize_abbrev(str(item)) for item in forms if str(item).strip()]


def _word_boundary_pattern(literal: str) -> re.Pattern[str]:
    escaped = re.escape(literal)
    if re.fullmatch(r"[\w]+", literal):
        return re.compile(rf"\b{escaped}\b")
    return re.compile(rf"{_BOUNDARY_LOOKBEHIND}{escaped}{_BOUNDARY_LOOKAHEAD}")
