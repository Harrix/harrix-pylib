"""Note-folder asset layout helpers for MdChecker (H061) and MdFormatter."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote

if TYPE_CHECKING:
    from collections.abc import Iterator

MEDIA_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".gif",
        ".svg",
        ".ico",
        ".webp",
        ".avif",
        ".mp4",
        ".webm",
    }
)

_MARKDOWN_SUFFIXES: frozenset[str] = frozenset({".md", ".markdown"})
_ASSET_DIR_NAMES: frozenset[str] = frozenset({"img", "files"})
_ASSET_REL_PARTS_LEN: int = 2
_INLINE_LINK_PATTERN = re.compile(r"(!?\[[^\]]*\]\()([^)\n]+)(\))")

# Folders with these markers are software project roots, not note folders.
_PROJECT_ROOT_FILE_MARKERS: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "package.json",
        "cargo.toml",
        "go.mod",
        "pipfile",
        "poetry.lock",
        "uv.lock",
    }
)

# Markdown stems that alone do not make a folder a note (README-only dirs, etc.).
_EXEMPT_NOTE_MD_STEMS: frozenset[str] = frozenset(
    {
        "readme",
        "license",
        "changelog",
        "contributing",
        "authors",
        "history",
        "security",
        "code_of_conduct",
        "third_party_notices",
    }
)


def desired_note_asset_path(folder: Path | str, path: Path | str) -> Path | None:
    """Return the correct path for a note asset, or `None` if already correct / ignored.

    Only direct children of the note folder and of sibling `img/` / `files/` are
    considered. Markdown files, hidden files, nested folders, and `featured-image.*`
    special cases follow the note-folder layout rules.

    Args:

    - `folder` (`Path | str`): Note folder that owns the asset.
    - `path` (`Path | str`): Asset path to check.

    Returns:

    - `Path | None`: Correct asset path, or `None` when the asset is already correct or ignored.

    """
    folder = Path(folder)
    path = Path(path)
    try:
        rel = path.relative_to(folder)
    except ValueError:
        return None
    if len(rel.parts) == 0:
        return None
    if path.suffix.lower() in _MARKDOWN_SUFFIXES:
        return None
    if path.name.startswith("."):
        return None

    name = path.name
    featured = is_featured_image_name(name)
    media = is_media_file(path)

    if len(rel.parts) == 1:
        if featured:
            return None
        if media:
            return folder / "img" / name
        return folder / "files" / name

    if len(rel.parts) != _ASSET_REL_PARTS_LEN or rel.parts[0] not in _ASSET_DIR_NAMES:
        return None

    kind = rel.parts[0]
    if kind == "img":
        if featured or media:
            return None
        return folder / "files" / name

    # files/
    if featured or not media:
        return None
    return folder / "img" / name


def is_featured_image_name(name: str) -> bool:
    """Return whether `name` is a featured-image asset (`featured-image.*`).

    Args:

    - `name` (`str`): File name to check.

    Returns:

    - `bool`: `True` when the name starts with `featured-image`.

    """
    return name.startswith("featured-image")


def is_media_file(path: Path | str) -> bool:
    """Return whether `path` has a media extension used for the `img/` folder.

    Args:

    - `path` (`Path | str`): Asset path to check.

    Returns:

    - `bool`: `True` when the suffix is in `MEDIA_EXTENSIONS`.

    """
    return Path(path).suffix.lower() in MEDIA_EXTENSIONS


def is_note_asset_folder(folder: Path | str) -> bool:
    """Return whether `folder` should use note asset layout (H061 / organize).

    Excludes:

    - software project roots (`.git`, `pyproject.toml`, `package.json`, …);
    - folders whose only Markdown files are docs like `README.md` / `LICENSE.md`
      (so `api-keys/README.md` does not trigger moving secrets into `files/`).

    Args:

    - `folder` (`Path | str`): Folder to check.

    Returns:

    - `bool`: `True` when the folder is a note folder that uses the asset layout.

    """
    root = Path(folder)
    if not root.is_dir():
        return False
    if (root / ".git").exists():
        return False
    try:
        children = list(root.iterdir())
    except OSError:
        return False
    names = {child.name.casefold() for child in children}
    if names & _PROJECT_ROOT_FILE_MARKERS:
        return False
    return _folder_has_note_markdown(children)


def iter_misplaced_note_assets(folder: Path | str) -> Iterator[tuple[Path, Path]]:
    """Yield `(source, destination)` for misplaced direct assets in a note folder.

    Destination may already exist; callers that move files should skip collisions.
    Project roots are skipped (see `is_note_asset_folder`).

    Args:

    - `folder` (`Path | str`): Note folder to scan.

    Yields:

    - `tuple[Path, Path]`: Current asset path and the path it should be moved to.

    """
    root = Path(folder)
    if not is_note_asset_folder(root):
        return

    candidates: list[Path] = []
    try:
        children = list(root.iterdir())
    except OSError:
        return

    for child in children:
        if child.is_file():
            candidates.append(child)
        elif child.is_dir() and child.name in _ASSET_DIR_NAMES:
            try:
                nested = list(child.iterdir())
            except OSError:
                continue
            candidates.extend(path for path in nested if path.is_file())

    for source in sorted(candidates, key=lambda item: item.as_posix().casefold()):
        destination = desired_note_asset_path(root, source)
        if destination is None:
            continue
        if source.resolve() == destination.resolve():
            continue
        yield source, destination


def organize_note_folder_assets(folder: Path | str) -> str:
    """Move misplaced note assets into `img/` / `files/` and rewrite Markdown links.

    No-op for software project roots (see `is_note_asset_folder`).

    Args:

    - `folder` (`Path | str`): Note folder (parent of a Markdown file).

    Returns:

    - `str`: Status message (may be empty when nothing changed).

    """
    root = Path(folder)
    if not root.is_dir():
        return f"❌ Error: {root} is not a valid directory"
    if not is_note_asset_folder(root):
        return ""

    moves: list[tuple[Path, Path]] = []
    lines: list[str] = []
    for source, destination in iter_misplaced_note_assets(root):
        if destination.exists():
            lines.append(f"⚠️ Skip {source}: destination exists ({destination})")
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)
        except OSError as exc:
            lines.append(f"❌ Error moving {source} → {destination}: {exc}")
            continue
        moves.append((source, destination))
        lines.append(f"✅ Moved {source.relative_to(root)} → {destination.relative_to(root)}")

    if moves:
        path_map = {
            _to_posix_rel(source.relative_to(root)): _to_posix_rel(destination.relative_to(root))
            for source, destination in moves
        }
        for md_path in _iter_markdown_files(root):
            try:
                original = md_path.read_text(encoding="utf-8")
            except OSError as exc:
                lines.append(f"❌ Error reading {md_path}: {exc}")
                continue
            updated = rewrite_note_asset_links(original, path_map)
            if updated != original:
                try:
                    md_path.write_text(updated, encoding="utf-8", newline="")
                except OSError as exc:
                    lines.append(f"❌ Error writing {md_path}: {exc}")
                    continue
                lines.append(f"✅ Updated links in {md_path.relative_to(root)}")

    if not lines:
        return ""
    return "\n".join(lines)


def rewrite_note_asset_links(markdown_text: str, path_map: dict[str, str]) -> str:
    """Rewrite local Markdown/YAML asset paths after files were moved.

    Args:

    - `markdown_text` (`str`): Full Markdown document (optional YAML front matter).
    - `path_map` (`dict[str, str]`): Old relative POSIX path → new relative POSIX path.

    Returns:

    - `str`: Document with updated destinations.

    """
    if not path_map:
        return markdown_text

    from harrix_pylib.funcs_md import (  # noqa: PLC0415
        identify_code_blocks,
        identify_code_blocks_line,
        split_yaml_content,
    )

    normalized_map = {_normalize_rel(old): _normalize_rel(new) for old, new in path_map.items()}
    basename_map: dict[str, str] = {}
    for old, new in normalized_map.items():
        base = Path(old).name.casefold()
        if base in basename_map and basename_map[base] != new:
            basename_map[base] = ""  # ambiguous
        else:
            basename_map[base] = new
    basename_map = {key: value for key, value in basename_map.items() if value}

    yaml_part, content_part = split_yaml_content(markdown_text)
    new_yaml = _rewrite_yaml_asset_paths(yaml_part, normalized_map, basename_map) if yaml_part else yaml_part

    content_lines = content_part.split("\n")
    new_content_lines: list[str] = []
    for line, in_code in identify_code_blocks(content_lines):
        if in_code:
            new_content_lines.append(line)
            continue
        rebuilt: list[str] = []
        for segment, in_inline_code in identify_code_blocks_line(line):
            if in_inline_code:
                rebuilt.append(segment)
            else:
                rebuilt.append(_rewrite_links_in_segment(segment, normalized_map, basename_map))
        new_content_lines.append("".join(rebuilt))

    new_content = "\n".join(new_content_lines)
    if new_yaml:
        return f"{new_yaml}\n\n{new_content}" if new_content else new_yaml
    return new_content


def _extract_link_destination_parts(raw: str) -> tuple[str, str, str, bool]:
    """Return `(path, fragment, title_suffix, was_angle)` for a destination."""
    url = raw.strip()
    if not url:
        return "", "", "", False

    if url.startswith("<"):
        end = url.find(">")
        inner = url[1:end] if end != -1 else url[1:]
        after = url[end + 1 :] if end != -1 else ""
        path_part = inner
        fragment = ""
        if "#" in path_part:
            path_part, frag = path_part.split("#", maxsplit=1)
            fragment = f"#{frag}"
        return path_part, fragment, after, True

    title_suffix = ""
    path_part = url
    titled = re.match(r"^(.*?)(\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))\s*$", url)
    if titled:
        path_part = titled.group(1).strip()
        title_suffix = titled.group(2)
    fragment = ""
    if "#" in path_part and not path_part.startswith("#"):
        path_part, frag = path_part.split("#", maxsplit=1)
        fragment = f"#{frag}"
    return path_part, fragment, title_suffix, False


def _folder_has_note_markdown(children: list[Path]) -> bool:
    """Return whether direct children include a non-exempt Markdown note file."""
    for path in children:
        if not path.is_file() or path.suffix.lower() not in _MARKDOWN_SUFFIXES:
            continue
        stem = path.stem.casefold().removesuffix(".g")
        if stem in _EXEMPT_NOTE_MD_STEMS:
            continue
        if stem.startswith("_"):
            continue
        return True
    return False


def _iter_markdown_files(folder: Path) -> list[Path]:
    """Return direct Markdown files in `folder` (sorted)."""
    try:
        children = list(folder.iterdir())
    except OSError:
        return []
    found = [path for path in children if path.is_file() and path.suffix.lower() in _MARKDOWN_SUFFIXES]
    return sorted(found, key=lambda item: item.name.casefold())


def _lookup_new_path(path_part: str, path_map: dict[str, str], basename_map: dict[str, str]) -> str | None:
    """Resolve a local path part to a new relative path, if mapped."""
    if not path_part or "://" in path_part or path_part.startswith(("#", "mailto:", "data:")):
        return None
    if path_part.startswith(("http://", "https://", "//")):
        return None
    normalized = _normalize_rel(path_part)
    if not normalized:
        return None
    if normalized in path_map:
        return path_map[normalized]
    base = Path(normalized).name.casefold()
    return basename_map.get(base)


def _normalize_rel(path_str: str) -> str:
    """Normalize a relative path for map keys (POSIX, no leading `./`)."""
    text = unquote(path_str.replace("\\", "/")).strip()
    while text.startswith("./"):
        text = text[2:]
    return text


def _rewrite_links_in_segment(segment: str, path_map: dict[str, str], basename_map: dict[str, str]) -> str:
    """Rewrite Markdown link/image destinations inside a non-code segment."""

    def repl(match: re.Match[str]) -> str:
        prefix, raw_dest, suffix = match.group(1), match.group(2), match.group(3)
        path_part, fragment, title_suffix, was_angle = _extract_link_destination_parts(raw_dest)
        new_path = _lookup_new_path(path_part, path_map, basename_map)
        if new_path is None:
            return match.group(0)
        if was_angle:
            return f"{prefix}<{new_path}{fragment}>{title_suffix}{suffix}"
        return f"{prefix}{new_path}{fragment}{title_suffix}{suffix}"

    return _INLINE_LINK_PATTERN.sub(repl, segment)


def _rewrite_yaml_asset_paths(yaml_part: str, path_map: dict[str, str], basename_map: dict[str, str]) -> str:
    """Replace old relative asset paths inside YAML front matter text."""
    result = yaml_part
    # Longer paths first so `files/a.png` is rewritten before bare `a.png`.
    for old in sorted(path_map, key=len, reverse=True):
        new = path_map[old]
        if old in result:
            result = result.replace(old, new)
    for old_base, new in basename_map.items():
        # Only replace basename forms that were not already rewritten as paths.
        pattern = re.compile(rf"(?<![\w./-]){re.escape(old_base)}(?![\w./-])", re.IGNORECASE)
        result = pattern.sub(new, result)
    return result


def _to_posix_rel(path: Path) -> str:
    """Return a POSIX relative path string."""
    return path.as_posix()
