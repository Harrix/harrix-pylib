---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `md_assets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `desired_note_asset_path`](#-function-desired_note_asset_path)
- [🔧 Function `is_featured_image_name`](#-function-is_featured_image_name)
- [🔧 Function `is_media_file`](#-function-is_media_file)
- [🔧 Function `is_note_asset_folder`](#-function-is_note_asset_folder)
- [🔧 Function `iter_misplaced_note_assets`](#-function-iter_misplaced_note_assets)
- [🔧 Function `organize_note_folder_assets`](#-function-organize_note_folder_assets)
- [🔧 Function `rewrite_note_asset_links`](#-function-rewrite_note_asset_links)

</details>

## 🔧 Function `desired_note_asset_path`

```python
def desired_note_asset_path(folder: Path | str, path: Path | str) -> Path | None
```

Return the correct path for a note asset, or `None` if already correct / ignored.

Only direct children of the note folder and of sibling `img/` / `files/` are
considered. Markdown files, hidden files, nested folders, and `featured-image.*`
special cases follow the note-folder layout rules.

Args:

- `folder` (`Path | str`): Note folder that owns the asset.
- `path` (`Path | str`): Asset path to check.

Returns:

- `Path | None`: Correct asset path, or `None` when the asset is already correct or ignored.

<details>
<summary>Code:</summary>

```python
def desired_note_asset_path(folder: Path | str, path: Path | str) -> Path | None:
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
```

</details>

## 🔧 Function `is_featured_image_name`

```python
def is_featured_image_name(name: str) -> bool
```

Return whether `name` is a featured-image asset (`featured-image.*`).

Args:

- `name` (`str`): File name to check.

Returns:

- `bool`: `True` when the name starts with `featured-image`.

<details>
<summary>Code:</summary>

```python
def is_featured_image_name(name: str) -> bool:
    return name.startswith("featured-image")
```

</details>

## 🔧 Function `is_media_file`

```python
def is_media_file(path: Path | str) -> bool
```

Return whether `path` has a media extension used for the `img/` folder.

Args:

- `path` (`Path | str`): Asset path to check.

Returns:

- `bool`: `True` when the suffix is in `MEDIA_EXTENSIONS`.

<details>
<summary>Code:</summary>

```python
def is_media_file(path: Path | str) -> bool:
    return Path(path).suffix.lower() in MEDIA_EXTENSIONS
```

</details>

## 🔧 Function `is_note_asset_folder`

```python
def is_note_asset_folder(folder: Path | str) -> bool
```

Return whether `folder` should use note asset layout (H061 / organize).

Excludes:

- software project roots (`.git`, `pyproject.toml`, `package.json`, …);
- folders whose only Markdown files are docs like `README.md` / `LICENSE.md`
  (so `api-keys/README.md` does not trigger moving secrets into `files/`).

Args:

- `folder` (`Path | str`): Folder to check.

Returns:

- `bool`: `True` when the folder is a note folder that uses the asset layout.

<details>
<summary>Code:</summary>

```python
def is_note_asset_folder(folder: Path | str) -> bool:
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
```

</details>

## 🔧 Function `iter_misplaced_note_assets`

```python
def iter_misplaced_note_assets(folder: Path | str) -> Iterator[tuple[Path, Path]]
```

Yield `(source, destination)` for misplaced direct assets in a note folder.

Destination may already exist; callers that move files should skip collisions.
Project roots are skipped (see [`is_note_asset_folder`](#-function-is_note_asset_folder)).

Args:

- `folder` (`Path | str`): Note folder to scan.

Yields:

- `tuple[Path, Path]`: Current asset path and the path it should be moved to.

<details>
<summary>Code:</summary>

```python
def iter_misplaced_note_assets(folder: Path | str) -> Iterator[tuple[Path, Path]]:
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
```

</details>

## 🔧 Function `organize_note_folder_assets`

```python
def organize_note_folder_assets(folder: Path | str) -> str
```

Move misplaced note assets into `img/` / `files/` and rewrite Markdown links.

No-op for software project roots (see [`is_note_asset_folder`](#-function-is_note_asset_folder)).

Args:

- `folder` (`Path | str`): Note folder (parent of a Markdown file).

Returns:

- `str`: Status message (may be empty when nothing changed).

<details>
<summary>Code:</summary>

```python
def organize_note_folder_assets(folder: Path | str) -> str:
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
```

</details>

## 🔧 Function `rewrite_note_asset_links`

```python
def rewrite_note_asset_links(markdown_text: str, path_map: dict[str, str]) -> str
```

Rewrite local Markdown/YAML asset paths after files were moved.

Args:

- `markdown_text` (`str`): Full Markdown document (optional YAML front matter).
- `path_map` (`dict[str, str]`): Old relative POSIX path → new relative POSIX path.

Returns:

- `str`: Document with updated destinations.

<details>
<summary>Code:</summary>

```python
def rewrite_note_asset_links(markdown_text: str, path_map: dict[str, str]) -> str:
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
```

</details>
