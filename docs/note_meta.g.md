---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `note_meta.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ResolvedNoteDate`](#%EF%B8%8F-class-resolvednotedate)
- [🔧 Function `extract_title_from_markdown`](#-function-extract_title_from_markdown)
- [🔧 Function `note_stem_from_name`](#-function-note_stem_from_name)
- [🔧 Function `parse_date_from_file_name`](#-function-parse_date_from_file_name)
- [🔧 Function `parse_date_from_yaml`](#-function-parse_date_from_yaml)
- [🔧 Function `parse_date_value`](#-function-parse_date_value)
- [🔧 Function `resolve_note_date`](#-function-resolve_note_date)
- [🔧 Function `resolve_note_date_for_path`](#-function-resolve_note_date_for_path)
- [🔧 Function `resolve_note_title`](#-function-resolve_note_title)
- [🔧 Function `title_from_id`](#-function-title_from_id)

</details>

## 🏛️ Class `ResolvedNoteDate`

```python
class ResolvedNoteDate
```

Resolved calendar date for a note and where it came from.

<details>
<summary>Code:</summary>

```python
class ResolvedNoteDate:

    value: date
    source: DateSource
```

</details>

## 🔧 Function `extract_title_from_markdown`

```python
def extract_title_from_markdown(md_text: str) -> str
```

Return YAML `title` or first H1 from Markdown (empty when neither exists).

<details>
<summary>Code:</summary>

```python
def extract_title_from_markdown(md_text: str) -> str:
    src = _strip_bom(str(md_text or ""))
    fm_match = _FRONTMATTER_RE.match(src)
    if fm_match is not None:
        title = _title_from_frontmatter_block(fm_match.group(1))
        if not title:
            title = _first_h1_after_frontmatter(src[fm_match.end() :])
    else:
        title = _first_h1_after_frontmatter(src)
    return _strip_html_comments(title)
```

</details>

## 🔧 Function `note_stem_from_name`

```python
def note_stem_from_name(file_name: str) -> str
```

Return file stem for `.md` / `.g.md` names.

<details>
<summary>Code:</summary>

```python
def note_stem_from_name(file_name: str) -> str:
    name = str(file_name or "")
    lower = name.lower()
    if lower.endswith(".g.md"):
        return name[:-5]
    if lower.endswith(".md"):
        return name[:-3]
    return Path(name).stem
```

</details>

## 🔧 Function `parse_date_from_file_name`

```python
def parse_date_from_file_name(file_name: str) -> date | None
```

Extract the first calendar date fragment from a file name / stem.

<details>
<summary>Code:</summary>

```python
def parse_date_from_file_name(file_name: str) -> date | None:
    stem = note_stem_from_name(Path(str(file_name or "")).name)
    match = _DATE_IN_NAME_RE.search(stem)
    if match is None:
        return None
    return _date_from_match(match)
```

</details>

## 🔧 Function `parse_date_from_yaml`

```python
def parse_date_from_yaml(md_text: str) -> date | None
```

Parse YAML frontmatter `date:` when present.

<details>
<summary>Code:</summary>

```python
def parse_date_from_yaml(md_text: str) -> date | None:
    src = _strip_bom(str(md_text or ""))
    fm_match = _FRONTMATTER_RE.match(src)
    if fm_match is None:
        return None
    for line in fm_match.group(1).splitlines():
        match = _DATE_LINE_RE.match(line.strip())
        if match is None:
            continue
        parsed = parse_date_value(_unquote_yaml_scalar(match.group(1)))
        if parsed is not None:
            return parsed
    return None
```

</details>

## 🔧 Function `parse_date_value`

```python
def parse_date_value(value: object) -> date | None
```

Parse a YAML/scalar date value into a `date`.

<details>
<summary>Code:</summary>

```python
def parse_date_value(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    # Take leading date token from datetime-like strings.
    token = text.split()[0]
    match = _DATE_IN_NAME_RE.search(token)
    if match is not None:
        return _date_from_match(match)
    try:
        return date.fromisoformat(token)
    except ValueError:
        return None
```

</details>

## 🔧 Function `resolve_note_date`

```python
def resolve_note_date(md_text: str, *, file_name: str, ctime: datetime | date | None = None, mtime: datetime | date | None = None) -> ResolvedNoteDate | None
```

Resolve note date: file name → YAML `date` → ctime → mtime.

<details>
<summary>Code:</summary>

```python
def resolve_note_date(
    md_text: str,
    *,
    file_name: str,
    ctime: datetime | date | None = None,
    mtime: datetime | date | None = None,
) -> ResolvedNoteDate | None:
    from_name = parse_date_from_file_name(file_name)
    if from_name is not None:
        return ResolvedNoteDate(value=from_name, source="filename")

    from_yaml = parse_date_from_yaml(md_text)
    if from_yaml is not None:
        return ResolvedNoteDate(value=from_yaml, source="yaml")

    ctime_date = _as_date(ctime)
    if ctime_date is not None:
        return ResolvedNoteDate(value=ctime_date, source="file_ctime")

    mtime_date = _as_date(mtime)
    if mtime_date is not None:
        return ResolvedNoteDate(value=mtime_date, source="file_mtime")

    return None
```

</details>

## 🔧 Function `resolve_note_date_for_path`

```python
def resolve_note_date_for_path(path: Path, md_text: str | None = None) -> ResolvedNoteDate | None
```

Resolve note date for a filesystem path (reads the file when `md_text` is omitted).

<details>
<summary>Code:</summary>

```python
def resolve_note_date_for_path(path: Path, md_text: str | None = None) -> ResolvedNoteDate | None:
    file_path = Path(path)
    text = md_text if md_text is not None else _read_text_prefix(file_path)
    if file_path.is_file():
        stat = file_path.stat()
        ctime = _local_date_from_timestamp(stat.st_ctime)
        mtime = _local_date_from_timestamp(stat.st_mtime)
    else:
        ctime = None
        mtime = None
    return resolve_note_date(text, file_name=file_path.name, ctime=ctime, mtime=mtime)
```

</details>

## 🔧 Function `resolve_note_title`

```python
def resolve_note_title(md_text: str, *, file_stem: str) -> str
```

Resolve display title: YAML `title` → H1 → `title_from_id(file_stem)`.

<details>
<summary>Code:</summary>

```python
def resolve_note_title(md_text: str, *, file_stem: str) -> str:
    meta_title = extract_title_from_markdown(md_text)
    if meta_title:
        return meta_title
    human = title_from_id(file_stem)
    return human or "Untitled"
```

</details>

## 🔧 Function `title_from_id`

```python
def title_from_id(file_stem: str) -> str
```

Humanize a note or icon-family stem into a display title.

Takes the part after the first `__` (`clothes__suit` → `Suit`), replaces
`-` / `_` with spaces, and applies `str.title()`. Stems without `__`
are title-cased as a whole (`file-stem` → `File Stem`).

Args:

- `file_stem` (`str`): File stem or family ID.

Returns:

- `str`: Display title, or empty string when `file_stem` is blank.

<details>
<summary>Code:</summary>

```python
def title_from_id(file_stem: str) -> str:
    stem = str(file_stem or "").strip()
    if not stem:
        return ""
    slug = stem.split("__", 1)[-1]
    return slug.replace("-", " ").replace("_", " ").title()
```

</details>
