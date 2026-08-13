"""Tests for @hsk-sync:note-meta title/date resolution."""

from datetime import UTC, date, datetime

from harrix_pylib.note_meta import (
    parse_date_from_file_name,
    resolve_note_date,
    resolve_note_title,
    title_from_id,
)


def test_resolve_note_title_prefers_yaml() -> None:
    md = "---\ntitle: From YAML\n---\n\n# From H1\n"
    assert resolve_note_title(md, file_stem="file-stem") == "From YAML"


def test_resolve_note_title_falls_back_to_h1() -> None:
    md = "---\ndate: 2022-09-18\n---\n\n# From H1\n"
    assert resolve_note_title(md, file_stem="file-stem") == "From H1"


def test_resolve_note_title_falls_back_to_title_from_id() -> None:
    md = "---\ndate: 2022-09-18\n---\n\nNo heading here.\n"
    assert resolve_note_title(md, file_stem="file-stem") == "File Stem"
    assert resolve_note_title(md, file_stem="clothes__suit") == "Suit"


def test_title_from_id() -> None:
    assert title_from_id("clothes__suit") == "Suit"
    assert title_from_id("building__two-story_house") == "Two Story House"
    assert title_from_id("file-stem") == "File Stem"
    assert title_from_id("garage") == "Garage"
    assert title_from_id("") == ""


def test_parse_date_from_file_name_formats() -> None:
    assert parse_date_from_file_name("2022-09-18-note.md") == date(2022, 9, 18)
    assert parse_date_from_file_name("2022.09.18_note.md") == date(2022, 9, 18)
    assert parse_date_from_file_name("18.09.2022-note.md") == date(2022, 9, 18)
    assert parse_date_from_file_name("20220918-note.md") == date(2022, 9, 18)


def test_resolve_note_date_priority_filename_over_yaml() -> None:
    md = "---\ndate: 2020-01-01\n---\n"
    resolved = resolve_note_date(md, file_name="2022-09-18-note.md")
    assert resolved is not None
    assert resolved.value == date(2022, 9, 18)
    assert resolved.source == "filename"


def test_resolve_note_date_yaml_then_mtime() -> None:
    md = "---\ndate: 2021-05-06\n---\n"
    resolved = resolve_note_date(
        md,
        file_name="note.md",
        mtime=datetime(2024, 1, 2, 15, 30, tzinfo=UTC),
    )
    assert resolved is not None
    assert resolved.value == date(2021, 5, 6)
    assert resolved.source == "yaml"

    resolved_mtime = resolve_note_date(
        "# No yaml\n",
        file_name="note.md",
        mtime=datetime(2024, 1, 2, 15, 30, tzinfo=UTC),
    )
    assert resolved_mtime is not None
    assert resolved_mtime.value == date(2024, 1, 2)
    assert resolved_mtime.source == "file_mtime"
