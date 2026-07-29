"""Tests for note-folder asset layout helpers and MdFormatter integration."""

from pathlib import Path

from harrix_pylib.md_assets import (
    MEDIA_EXTENSIONS,
    is_note_asset_folder,
    iter_misplaced_note_assets,
    organize_note_folder_assets,
    rewrite_note_asset_links,
)
from harrix_pylib.md_format import MdFormatter


def test_media_extensions_include_svg_gif_ico() -> None:
    """Media set includes svg, gif, and ico."""
    assert {".svg", ".gif", ".ico", ".png", ".mp4", ".webm"} <= MEDIA_EXTENSIONS


def test_project_root_is_not_organized(tmp_path: Path) -> None:
    """Do not move assets next to pyproject.toml / .git (library repo root)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "photo.png").write_bytes(b"png")
    (tmp_path / "README.md").write_text("# Repo\n", encoding="utf-8")
    assert not is_note_asset_folder(tmp_path)
    assert list(iter_misplaced_note_assets(tmp_path)) == []
    assert organize_note_folder_assets(tmp_path) == ""
    assert (tmp_path / "photo.png").is_file()

    git_root = tmp_path / "git_repo"
    git_root.mkdir()
    (git_root / ".git").mkdir()
    (git_root / "doc.pdf").write_bytes(b"%PDF")
    (git_root / "note.md").write_text("# Note\n", encoding="utf-8")
    assert not is_note_asset_folder(git_root)
    assert organize_note_folder_assets(git_root) == ""
    assert (git_root / "doc.pdf").is_file()


def test_readme_only_folder_is_not_organized(tmp_path: Path) -> None:
    """Folders with only README.md must not move sibling secrets into files/."""
    (tmp_path / "README.md").write_text("# Keys\n", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("token\n", encoding="utf-8")
    assert not is_note_asset_folder(tmp_path)
    assert organize_note_folder_assets(tmp_path) == ""
    assert (tmp_path / "secret.txt").is_file()
    assert not (tmp_path / "files").exists()


def test_iter_misplaced_note_assets_rules(tmp_path: Path) -> None:
    """Classify root/img/files placements; ignore featured-image and nested dirs."""
    (tmp_path / "note.md").write_text("# Note\n", encoding="utf-8")
    (tmp_path / "photo.png").write_bytes(b"png")
    (tmp_path / "featured-image.png").write_bytes(b"png")
    (tmp_path / "doc.pdf").write_bytes(b"%PDF")
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "ok.png").write_bytes(b"png")
    (tmp_path / "img" / "featured-image.mp4").write_bytes(b"mp4")
    (tmp_path / "img" / "archive.zip").write_bytes(b"zip")
    (tmp_path / "files").mkdir()
    (tmp_path / "files" / "readme.txt").write_bytes(b"txt")
    (tmp_path / "files" / "clip.webp").write_bytes(b"webp")
    (tmp_path / "files" / "featured-image.jpg").write_bytes(b"jpg")
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "nested.png").write_bytes(b"png")

    moves = {src.name: dst.as_posix() for src, dst in iter_misplaced_note_assets(tmp_path)}
    assert moves["photo.png"].endswith("/img/photo.png")
    assert moves["doc.pdf"].endswith("/files/doc.pdf")
    assert moves["archive.zip"].endswith("/files/archive.zip")
    assert moves["clip.webp"].endswith("/img/clip.webp")
    assert "featured-image.png" not in moves
    assert "featured-image.mp4" not in moves
    assert "featured-image.jpg" not in moves
    assert "ok.png" not in moves
    assert "readme.txt" not in moves
    assert "nested.png" not in moves


def test_organize_note_folder_assets_moves_and_rewrites_links(tmp_path: Path) -> None:
    """Organize moves files and updates Markdown plus YAML paths."""
    (tmp_path / "photo.png").write_bytes(b"png")
    (tmp_path / "files").mkdir()
    (tmp_path / "files" / "diagram.svg").write_bytes(b"<svg/>")
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "manual.pdf").write_bytes(b"%PDF")
    note = tmp_path / "note.md"
    note.write_text(
        "---\nlang: en\ndownload: files/diagram.svg\n---\n\n"
        "![Photo](photo.png)\n\n"
        "[Diagram](files/diagram.svg)\n\n"
        "[Manual](img/manual.pdf)\n",
        encoding="utf-8",
        newline="\n",
    )

    msg = organize_note_folder_assets(tmp_path)
    assert "Moved" in msg
    assert (tmp_path / "img" / "photo.png").is_file()
    assert (tmp_path / "img" / "diagram.svg").is_file()
    assert (tmp_path / "files" / "manual.pdf").is_file()
    assert not (tmp_path / "photo.png").exists()
    assert not (tmp_path / "files" / "diagram.svg").exists()
    assert not (tmp_path / "img" / "manual.pdf").exists()

    text = note.read_text(encoding="utf-8")
    assert "![Photo](img/photo.png)" in text
    assert "[Diagram](img/diagram.svg)" in text
    assert "[Manual](files/manual.pdf)" in text
    assert "download: img/diagram.svg" in text


def test_rewrite_note_asset_links_skips_code_and_urls() -> None:
    """Link rewrite ignores fenced code and absolute URLs."""
    path_map = {"photo.png": "img/photo.png"}
    source = "![A](photo.png)\n\n```md\n![A](photo.png)\n```\n\n![R](https://example.com/photo.png)\n"
    result = rewrite_note_asset_links(source, path_map)
    assert "![A](img/photo.png)" in result
    assert "```md\n![A](photo.png)\n```" in result
    assert "](https://example.com/photo.png)" in result


def test_organize_skips_destination_collision(tmp_path: Path) -> None:
    """Do not overwrite an existing destination file."""
    (tmp_path / "photo.png").write_bytes(b"loose")
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "photo.png").write_bytes(b"kept")
    (tmp_path / "note.md").write_text("# Note\n", encoding="utf-8")

    msg = organize_note_folder_assets(tmp_path)
    assert "Skip" in msg
    assert (tmp_path / "photo.png").read_bytes() == b"loose"
    assert (tmp_path / "img" / "photo.png").read_bytes() == b"kept"


def test_format_file_organizes_assets(tmp_path: Path) -> None:
    """MdFormatter.format_file moves assets and rewrites links before formatting."""
    (tmp_path / "photo.png").write_bytes(b"png")
    note = tmp_path / "note.md"
    note.write_text("![Photo](photo.png)\n\nUse markdown daily.\n", encoding="utf-8", newline="\n")

    MdFormatter(end_of_line="lf").format_file(note)

    assert (tmp_path / "img" / "photo.png").is_file()
    text = note.read_text(encoding="utf-8")
    assert "![Photo](img/photo.png)" in text
    assert "Markdown" in text


def test_format_folder_organizes_nested_note(tmp_path: Path) -> None:
    """MdFormatter.format_folder organizes each note folder once."""
    article = tmp_path / "article"
    article.mkdir()
    (article / "clip.webm").write_bytes(b"webm")
    (article / "pack.zip").write_bytes(b"zip")
    note = article / "note.md"
    note.write_text(
        "![Clip](clip.webm)\n\n[Pack](pack.zip)\n",
        encoding="utf-8",
        newline="\n",
    )

    MdFormatter(end_of_line="lf").format_folder(tmp_path)

    assert (article / "img" / "clip.webm").is_file()
    assert (article / "files" / "pack.zip").is_file()
    text = note.read_text(encoding="utf-8")
    assert "![Clip](img/clip.webm)" in text
    assert "[Pack](files/pack.zip)" in text
