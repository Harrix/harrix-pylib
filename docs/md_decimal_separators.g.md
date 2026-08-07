---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `md_decimal_separators.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `classify_decimal_separator_issue`](#-function-classify_decimal_separator_issue)
- [🔧 Function `fix_decimal_separators`](#-function-fix_decimal_separators)
- [🔧 Function `iter_decimal_separator_issues`](#-function-iter_decimal_separator_issues)

</details>

## 🔧 Function `classify_decimal_separator_issue`

```python
def classify_decimal_separator_issue(token: str, lang: str) -> DecimalIssueKind | None
```

Return autofix kind for a compact numeric token, or `None` if allowed.

<details>
<summary>Code:</summary>

```python
def classify_decimal_separator_issue(token: str, lang: str) -> DecimalIssueKind | None:
    if lang not in {"en", "ru"}:
        return None
    if _EN_THOUSANDS_PATTERN.fullmatch(token):
        return None
    if "," in token:
        return "fix_comma_to_dot"
    return None
```

</details>

## 🔧 Function `fix_decimal_separators`

```python
def fix_decimal_separators(segment: str, lang: str) -> str
```

Rewrite comma decimals to points in `segment` for `lang` (`en` / `ru`).

<details>
<summary>Code:</summary>

```python
def fix_decimal_separators(segment: str, lang: str) -> str:
    if lang not in {"en", "ru"} or not segment:
        return segment

    def replacer(match: re.Match[str]) -> str:
        token = match.group(0)
        kind = classify_decimal_separator_issue(token, lang)
        if kind == "fix_comma_to_dot":
            simple = _SIMPLE_COMMA_DECIMAL_PATTERN.fullmatch(token)
            if simple:
                return f"{simple.group(1)}{simple.group(2)}.{simple.group(3)}"
        return token

    return _COMPACT_NUMBER_PATTERN.sub(replacer, segment)
```

</details>

## 🔧 Function `iter_decimal_separator_issues`

```python
def iter_decimal_separator_issues(segment: str, lang: str) -> Iterator[tuple[int, int, str, DecimalIssueKind]]
```

Yield `(start, end, token, kind)` for wrong decimal separators in `segment`.

<details>
<summary>Code:</summary>

```python
def iter_decimal_separator_issues(segment: str, lang: str) -> Iterator[tuple[int, int, str, DecimalIssueKind]]:
    if lang not in {"en", "ru"}:
        return
    for match in _COMPACT_NUMBER_PATTERN.finditer(segment):
        token = match.group(0)
        kind = classify_decimal_separator_issue(token, lang)
        if kind is not None:
            yield match.start(), match.end(), token, kind
```

</details>
