"""Resolve note title and date from Markdown metadata.

@hsk-sync:note-meta — keep behavior aligned with:

- `harrix-swiss-knife/vscode/harrix-notes-explorer-hsk/note-meta.js`
- `harrix-notes-android` `NoteMetaResolver` / `NoteTitleExtractor`
- `harrix-pyssg.note_meta` (re-export)

Title priority: YAML `title` → first `#` heading → `title_from_id(file_stem)`.

Date priority: date in file name → YAML `date` → file ctime → file mtime.

"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal

_FRONTMATTER_RE = re.compile(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n?")
_TITLE_LINE_RE = re.compile(r"^title\s*:\s*(.*)$", re.IGNORECASE)
_DATE_LINE_RE = re.compile(r"^date\s*:\s*(.*)$", re.IGNORECASE)
_H1_RE = re.compile(r"^#\s+(.+)$")
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")
_MIN_QUOTED_SCALAR_LEN = 2

# YYYY-MM-DD / YYYY.MM.DD / YYYYMMDD / DD.MM.YYYY
_DATE_IN_NAME_RE = re.compile(
    r"(?:"
    r"(?P<y4>\d{4})[.\-](?P<m4>\d{2})[.\-](?P<d4>\d{2})"
    r"|"
    r"(?P<y8>\d{4})(?P<m8>\d{2})(?P<d8>\d{2})"
    r"|"
    r"(?P<d_eu>\d{2})\.(?P<m_eu>\d{2})\.(?P<y_eu>\d{4})"
    r")"
)

DateSource = Literal["filename", "yaml", "file_ctime", "file_mtime"]


@dataclass(frozen=True, slots=True)
class ResolvedNoteDate:
    """Resolved calendar date for a note and where it came from."""

    value: date
    source: DateSource


def extract_title_from_markdown(md_text: str) -> str:
    """Return YAML `title` or first H1 from Markdown (empty when neither exists)."""
    src = _strip_bom(str(md_text or ""))
    fm_match = _FRONTMATTER_RE.match(src)
    if fm_match is not None:
        title = _title_from_frontmatter_block(fm_match.group(1))
        if not title:
            title = _first_h1_after_frontmatter(src[fm_match.end() :])
    else:
        title = _first_h1_after_frontmatter(src)
    return _strip_html_comments(title)


def note_stem_from_name(file_name: str) -> str:
    """Return file stem for `.md` / `.g.md` names."""
    name = str(file_name or "")
    lower = name.lower()
    if lower.endswith(".g.md"):
        return name[:-5]
    if lower.endswith(".md"):
        return name[:-3]
    return Path(name).stem


def parse_date_from_file_name(file_name: str) -> date | None:
    """Extract the first calendar date fragment from a file name / stem."""
    stem = note_stem_from_name(Path(str(file_name or "")).name)
    match = _DATE_IN_NAME_RE.search(stem)
    if match is None:
        return None
    return _date_from_match(match)


def parse_date_from_yaml(md_text: str) -> date | None:
    """Parse YAML frontmatter `date:` when present."""
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


def parse_date_value(value: object) -> date | None:
    """Parse a YAML/scalar date value into a `date`."""
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


def resolve_note_date(
    md_text: str,
    *,
    file_name: str,
    ctime: datetime | date | None = None,
    mtime: datetime | date | None = None,
) -> ResolvedNoteDate | None:
    """Resolve note date: file name → YAML `date` → ctime → mtime."""
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


def resolve_note_date_for_path(path: Path, md_text: str | None = None) -> ResolvedNoteDate | None:
    """Resolve note date for a filesystem path (reads the file when `md_text` is omitted)."""
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


def resolve_note_title(md_text: str, *, file_stem: str) -> str:
    """Resolve display title: YAML `title` → H1 → `title_from_id(file_stem)`."""
    meta_title = extract_title_from_markdown(md_text)
    if meta_title:
        return meta_title
    human = title_from_id(file_stem)
    return human or "Untitled"


def title_from_id(file_stem: str) -> str:
    """Humanize a note or icon-family stem into a display title.

    Takes the part after the first `__` (`clothes__suit` → `Suit`), replaces
    `-` / `_` with spaces, and applies `str.title()`. Stems without `__`
    are title-cased as a whole (`file-stem` → `File Stem`).

    Args:

    - `file_stem` (`str`): File stem or family ID.

    Returns:

    - `str`: Display title, or empty string when `file_stem` is blank.

    """
    stem = str(file_stem or "").strip()
    if not stem:
        return ""
    slug = stem.split("__", 1)[-1]
    return slug.replace("-", " ").replace("_", " ").title()


def _as_date(value: datetime | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone().date()
        return value.date()
    return value


def _date_from_match(match: re.Match[str]) -> date | None:
    try:
        if match.group("y4"):
            return date(int(match.group("y4")), int(match.group("m4")), int(match.group("d4")))
        if match.group("y8"):
            return date(int(match.group("y8")), int(match.group("m8")), int(match.group("d8")))
        if match.group("y_eu"):
            return date(int(match.group("y_eu")), int(match.group("m_eu")), int(match.group("d_eu")))
    except ValueError:
        return None
    return None


def _first_h1_after_frontmatter(body: str) -> str:
    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("<!--") and "-->" in line:
            continue
        if line.startswith("##"):
            continue
        h1 = _H1_RE.match(line)
        if h1 is not None:
            return h1.group(1).strip()
    return ""


def _local_date_from_timestamp(timestamp: float) -> date:
    return datetime.fromtimestamp(timestamp, tz=UTC).astimezone().date()


def _read_text_prefix(path: Path, max_bytes: int = 16 * 1024) -> str:
    try:
        with path.open("rb") as handle:
            raw = handle.read(max_bytes)
        return raw.decode("utf-8", errors="replace")
    except OSError:
        return ""


def _strip_bom(text: str) -> str:
    return text.removeprefix("\ufeff")


def _strip_html_comments(text: str) -> str:
    return _HTML_COMMENT_RE.sub("", str(text or "")).strip()


def _title_from_frontmatter_block(fm_text: str) -> str:
    for line in fm_text.splitlines():
        match = _TITLE_LINE_RE.match(line.strip())
        if match is None:
            continue
        title = _unquote_yaml_scalar(match.group(1))
        if title:
            return title
    return ""


def _unquote_yaml_scalar(value: str) -> str:
    text = str(value or "").strip()
    if len(text) >= _MIN_QUOTED_SCALAR_LEN and ((text[0] == text[-1] == '"') or (text[0] == text[-1] == "'")):
        text = text[1:-1]
    return text.strip()
