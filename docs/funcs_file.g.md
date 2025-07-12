---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_file.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Function `all_to_parent_folder`](#function-all_to_parent_folder)
- [Function `apply_func`](#function-apply_func)
- [Function `check_featured_image`](#function-check_featured_image)
- [Function `check_func`](#function-check_func)
- [Function `clear_directory`](#function-clear_directory)
- [Function `extract_zip_archive`](#function-extract_zip_archive)
- [Function `find_max_folder_number`](#function-find_max_folder_number)
- [Function `list_files_simple`](#function-list_files_simple)
- [Function `open_file_or_folder`](#function-open_file_or_folder)
- [Function `remove_empty_folders`](#function-remove_empty_folders)
- [Function `rename_epub_file`](#function-rename_epub_file)
- [Function `rename_fb2_file`](#function-rename_fb2_file)
- [Function `rename_file_spaces_to_hyphens`](#function-rename_file_spaces_to_hyphens)
- [Function `rename_files_by_mapping`](#function-rename_files_by_mapping)
- [Function `rename_largest_images_to_featured`](#function-rename_largest_images_to_featured)
- [Function `rename_pdf_file`](#function-rename_pdf_file)
- [Function `should_ignore_path`](#function-should_ignore_path)
- [Function `tree_view_folder`](#function-tree_view_folder)

</details>

## Function `all_to_parent_folder`

```python
def all_to_parent_folder(path: Path | str) -> str
```

Move all files from subfolders within the given path to the parent folder and then
removes empty folders.

Args:

- `path` (`Path | str`): The path to the folder whose subfolders you want to flatten.
  Can be either a `Path` object or a string.

Returns:

- `str`: A string where each line represents an action taken on a subfolder (e.g., "Fix subfolder_name").

Notes:

- This function will print exceptions to stdout if there are issues with moving files or deleting folders.
- Folders will only be removed if they become empty after moving all files.

Before:

```text
C:/test
├─ folder1
│  ├─ image.jpg
│  ├─ sub1
│  │  ├─ file1.txt
│  │  └─ file2.txt
│  └─ sub2
│     ├─ file3.txt
│     └─ file4.txt
└─ folder2
   └─ sub3
      ├─ file6.txt
      └─ sub4
         └─ file5.txt
```

After:

```text
C:/test
├─ folder1
│  ├─ file1.txt
│  ├─ file2.txt
│  ├─ file3.txt
│  ├─ file4.txt
│  └─ image.jpg
└─ folder2
   ├─ file5.txt
   └─ file6.txt
```

Example:

```python
import harrix_pylib as h

h.file.all_to_parent_folder("C:/test")
```

<details>
<summary>Code:</summary>

```python
def all_to_parent_folder(path: Path | str) -> str:
    list_lines = []
    for child_folder in Path(path).iterdir():
        for file in Path(child_folder).glob("**/*"):
            if file.is_file():
                with contextlib.suppress(Exception):
                    file.replace(child_folder / file.name)
        for file in Path(child_folder).glob("**/*"):
            if file.is_dir():
                with contextlib.suppress(Exception):
                    shutil.rmtree(file)
        list_lines.append(f"Fix {child_folder}")
    return "\n".join(list_lines)
```

</details>

## Function `apply_func`

```python
def apply_func(path: Path | str, ext: str, func: Callable) -> str
```

Recursively apply a function to all files with a specified extension in a directory.

Args:

- `path` (`Path | str`): The directory path where the files will be searched.
  If provided as a string, it will be converted to a Path object.
- `ext` (`str`): The file extension to filter files. For example, ".txt".
- `func` (`Callable`): A function that takes a single argument (the file path as a string)
  and performs an operation on the file. It may return a value.

Returns:

- `str`: A newline-separated string of messages indicating the success or failure of applying `func` to each file.

Note:

- Files and folders that match common ignore patterns (like `.git`, `__pycache__`, `node_modules`, etc.)
  are ignored during processing.
- Hidden files and folders (those with names starting with a dot) are ignored during processing.
- The function handles different return types from the `func` parameter:
  - If `None`: Shows a simple success message
  - If `str`: Appends the string to the success message
  - If `list`: Formats each item in the list as a bullet point
  - For other types: Converts to string and appends to the success message

Example:

```python
from pathlib import Path

import harrix_pylib as h


def test_func(filename):
    content = Path(filename).read_text(encoding="utf8")
    content = content.upper()
    Path(filename).write_text(content, encoding="utf8")
    return ["Changed to uppercase", "No errors found"]


result = h.file.apply_func("C:/Notes/", ".txt", test_func)
print(result)
```

<details>
<summary>Code:</summary>

```python
def apply_func(path: Path | str, ext: str, func: Callable) -> str:
    list_lines = []
    folder_path = Path(path)

    for file_path in folder_path.rglob(f"*{ext}"):
        # Check if file should be processed
        if file_path.is_file():
            # Check if any part of the path should be ignored
            should_skip = False
            for part in file_path.parts:
                if should_ignore_path(part):
                    should_skip = True
                    break

            if should_skip:
                continue

            try:
                result = func(str(file_path))
                if result is None:
                    list_lines.append(f"✅ File {file_path.name} is applied.")
                elif isinstance(result, str):
                    list_lines.append(f"✅ File {file_path.name} is applied: {result}")
                elif isinstance(result, list):
                    if not result:  # Empty list
                        list_lines.append(f"✅ File {file_path.name} is applied.")
                    else:
                        list_lines.append(f"✅ File {file_path.name} is applied:")
                        list_lines.extend([f"  - {item}" for item in result])
                else:
                    list_lines.append(f"✅ File {file_path.name} is applied: {result}")
            except OSError as e:
                # Catching specific exceptions that are likely to occur
                list_lines.append(f"❌ File {file_path.name} is not applied: {e!s}")

    return "\n".join(list_lines)
```

</details>

## Function `check_featured_image`

```python
def check_featured_image(path: Path | str) -> tuple[bool, str]
```

Check for the presence of `featured_image.*` files in every child folder, not recursively.

This function goes through each immediate subfolder of the given path and checks if there
is at least one file with the name starting with "featured-image". If such a file is missing
in any folder, it logs this occurrence.

Args:

- `path` (`Path | str`): Path to the folder being checked. Can be either a string or a Path object.

Returns:

- `tuple[bool, str]`: A tuple where:
  - The first element (`bool`) indicates if all folders have a `featured_image.*` file.
  - The second element (`str`) contains a formatted string with status or error messages.

Note:

- This function does not search recursively; it only checks the immediate child folders.
- The output string uses ANSI color codes for visual distinction of errors.

Example:

```python
import harrix_pylib as h


is_correct = h.file.check_featured_image("C:/articles/")
```

<details>
<summary>Code:</summary>

```python
def check_featured_image(path: Path | str) -> tuple[bool, str]:
    line_list: list[str] = []
    is_correct: bool = True

    for child_folder in Path(path).iterdir():
        is_featured_image: bool = False
        for file in child_folder.iterdir():
            if file.is_file() and file.name.startswith("featured-image"):
                is_featured_image = True
        if not is_featured_image:
            is_correct = False
            line_list.append(f"❌ {child_folder} without featured-image")

    if is_correct:
        line_list.append(f"✅ All correct in {path}")
    return is_correct, "\n".join(line_list)
```

</details>

## Function `check_func`

```python
def check_func(path: Path | str, ext: str, func: Callable[[Path | str], list]) -> list
```

Recursively applies a checking function to all files with a specified extension in a directory.

Args:

- `path` (`Path | str`): The directory path where the files will be searched.
  If provided as a string, it will be converted to a Path object.
- `ext` (`str`): The file extension to filter files. For example, ".md".
- `func` (`Callable[[Path | str], list]`): A function that takes a file path and returns a list
  representing check results or errors.

Returns:

- `list`: A combined list of all check results from all processed files.

Note:

- Files and folders that match common ignore patterns (like `.git`, `__pycache__`, `node_modules`, etc.)
  are ignored during processing.
- Hidden files and folders (those with names starting with a dot) are ignored during processing.

Example:

```python
import harrix_pylib as h
from pathlib import Path

def check_markdown(filepath):
    errors = []
    # Some checking logic
    if some_condition:
        errors.append(f"Error in {filepath.name}: something is wrong")
    return errors

all_errors = h.file.check_func("docs/", ".md", check_markdown)
for error in all_errors:
    print(error)
```

<details>
<summary>Code:</summary>

```python
def check_func(path: Path | str, ext: str, func: Callable[[Path | str], list]) -> list:
    list_checkers = []
    folder_path = Path(path)

    for file_path in folder_path.rglob(f"*{ext}"):
        # Check if file should be processed
        if file_path.is_file():
            # Check if any part of the path should be ignored
            should_skip = False
            for part in file_path.parts:
                if should_ignore_path(part):
                    should_skip = True
                    break

            if should_skip:
                continue

            result = func(file_path)
            if result is not None and result:
                list_checkers.extend(result)

    return list_checkers
```

</details>

## Function `clear_directory`

```python
def clear_directory(path: Path | str) -> None
```

Clear directory with sub-directories.

Args:

- `path` (`Path | str`): Path of directory.

Returns:

- `None`.

Examples:

```python
import harrix-pylib as h

h.file.clear_directory("C:/temp_dir")
```

```python
from pathlib import Path
import harrix-pylib as h

folder = Path(__file__).resolve().parent / "data/temp"
folder.mkdir(parents=True, exist_ok=True)
Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
...
h.file.clear_directory(folder)
```

<details>
<summary>Code:</summary>

```python
def clear_directory(path: Path | str) -> None:
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
```

</details>

## Function `extract_zip_archive`

```python
def extract_zip_archive(filename: Path | str) -> str
```

Extract ZIP archive to the folder where the archive is located and remove the archive file.

This function extracts ZIP archives directly to the same directory where the
archive file is located. After successful extraction, the original archive
file is deleted.

Args:

- `filename` (`Path | str`): The path to the ZIP archive file to be extracted.

Returns:

- `str`: A status message indicating the result of the operation.

Note:

- Only supports ZIP format.
- Uses built-in zipfile module.
- Files are extracted directly to the archive's parent directory.
- The original archive file is deleted after successful extraction.

Example:

```python
import harrix_pylib as h

extract_zip_archive("C:/Downloads/archive.zip")
```

<details>
<summary>Code:</summary>

```python
def extract_zip_archive(filename: Path | str) -> str:

    def extract_zip_file(file_path: Path, extract_to: Path) -> bool:
        """Extract ZIP archive using built-in zipfile module."""
        try:
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        except Exception:
            return False
        else:
            return True

    filename = Path(filename)

    # Validate file existence and type
    if not filename.exists():
        return f"❌ File {filename} does not exist."

    if not filename.is_file():
        return f"❌ {filename} is not a file."

    if filename.suffix.lower() != ".zip":
        return f"❌ {filename.name} is not a ZIP file."

    # Extract to the same directory where the archive is located
    extract_to = filename.parent

    # Extract ZIP file directly to parent directory
    if not extract_zip_file(filename, extract_to):
        return f"❌ Failed to extract {filename.name}. Archive might be corrupted or password-protected."

    # Remove original archive file
    try:
        filename.unlink()
    except Exception as e:
        return f"⚠️ Archive extracted successfully, but failed to delete original file: {e!s}"
    else:
        return f"✅ Archive {filename.name} extracted and original file deleted."
```

</details>

## Function `find_max_folder_number`

```python
def find_max_folder_number(base_path: str, start_pattern: str) -> int
```

Find the highest folder number in a given folder based on a pattern.

Args:

- `base_path` (`str`): The base folder path to search for folders.
- `start_pattern` (`str`): A regex pattern for matching folder names.

Returns:

- `int`: The maximum folder number found, or 0 if no matches are found.

Example:

```python
import harrix_pylib as h


number = h.file.find_max_folder_number("C:/projects/", "python_project_")
```

<details>
<summary>Code:</summary>

```python
def find_max_folder_number(base_path: str, start_pattern: str) -> int:
    pattern = re.compile(start_pattern + r"(\d+)$")
    max_number = 0
    base_path_obj = Path(base_path)

    for item in base_path_obj.iterdir():
        if item.is_dir():
            match = pattern.match(item.name)
            if match:
                number = int(match.group(1))
                max_number = max(max_number, number)

    return max_number
```

</details>

## Function `list_files_simple`

```python
def list_files_simple(path: Path | str) -> str
```

Generate a simple list of all files in a directory structure.

Example output:

```text
file.txt
img/image.jpg
docs/readme.md
src/main.py
```

Args:

- `path` (`Path | str`): The root folder path to start the listing from.
- `is_ignore_hidden_folders` (`bool`): If `True`, hidden folders and files (starting with a dot or
  matching common ignore patterns like `.git`, `__pycache__`, `node_modules`, etc.) are ignored.
  Defaults to `False`.

Returns:

- `str`: A string representation of all files with their relative paths.

Note:

- This function uses recursion to traverse folders. It handles `PermissionError`
  by excluding folders without permission.
- Files are listed with their relative paths from the root directory.
- When `is_ignore_hidden_folders` is `True`, ignored folders are completely skipped.

Example:

```python
import harrix_pylib as h

files = h.file.list_files_simple("C:/Notes")
print(files)

# Ignore hidden folders and files
files_clean = h.file.list_files_simple("C:/Notes", is_ignore_hidden_folders=True)
print(files_clean)
```

<details>
<summary>Code:</summary>

```python
def list_files_simple(path: Path | str, *, is_ignore_hidden_folders: bool = False) -> str:

    def __list_files(path: Path | str, root_path: Path, *, is_ignore_hidden_folders: bool = False) -> Iterator[str]:
        path = Path(path)
        try:
            contents = list(path.iterdir())
        except PermissionError:
            contents = []

        for item in contents:
            # Skip ignored items if flag is set
            if is_ignore_hidden_folders and should_ignore_path(item.name):
                continue

            if item.is_file():
                # Get relative path from root and normalize to forward slashes
                relative_path = item.relative_to(root_path)
                yield str(relative_path).replace("\\", "/")
            elif item.is_dir():
                # Recursively process subdirectories
                yield from __list_files(item, root_path, is_ignore_hidden_folders=is_ignore_hidden_folders)

    root_path = Path(path)
    return "\n".join(sorted(__list_files(root_path, root_path, is_ignore_hidden_folders=is_ignore_hidden_folders)))
```

</details>

## Function `open_file_or_folder`

```python
def open_file_or_folder(path: Path | str) -> None
```

Open a file or folder using the operating system's default application.

This function checks the operating system and uses the appropriate method to open
the given path:

- On **Windows**, it uses `os.startfile`.
- On **macOS**, it invokes the `open` command.
- On **Linux**, it uses `xdg-open`.

Args:

- `path` (`Path | str`): The path to the file or folder to be opened. Can be either a `Path` object or a string.

Returns:

- `None`: This function does not return any value but opens the file or folder in the default application.

Note:

- Ensure the path provided is valid and accessible.
- If the path does not exist or cannot be opened, the function might raise an exception,
  depending on the underlying command's behavior.

Example:

```python
import harrix_pylib as h


h.file.open_file_or_folder("C:/Notes/note.md")
```

<details>
<summary>Code:</summary>

```python
def open_file_or_folder(path: Path | str) -> None:
    target = Path(path).expanduser().resolve(strict=True)

    system = platform.system()
    if system == "Windows":
        opener = shutil.which("explorer.exe")
    elif system == "Darwin":  # macOS
        opener = shutil.which("open")
    elif system == "Linux":
        opener = shutil.which("xdg-open")
    else:
        msg = f"Unsupported operating system: {system}"
        raise RuntimeError(msg)

    if opener is None:
        msg = "Could not locate the system open helper."
        raise RuntimeError(msg)

    subprocess.run([opener, str(target)], check=False, shell=False)
```

</details>

## Function `remove_empty_folders`

```python
def remove_empty_folders(folder_path: Path | str, additional_patterns: list[str] | None = None) -> str
```

Remove all empty folders recursively while respecting ignore patterns.

This function traverses the directory tree and removes empty folders, but does not
enter or process folders that should be ignored based on common ignore patterns.
The function works recursively from the deepest level up to avoid issues with
nested empty folders.

Args:

- `folder_path` (`Path | str`): The root path to start removing empty folders from.
- `additional_patterns` (`list[str] | None`): Additional patterns to ignore. Defaults to `None`.
- `is_ignore_hidden` (`bool`): Whether to ignore hidden files/folders (starting with dot). Defaults to `True`.

Returns:

- `str`: A status message indicating the result of the operation with count of removed folders.

Note:

- Uses `should_ignore_path()` function to determine which folders to skip.
- Processes folders recursively from deepest to shallowest level.
- Only removes truly empty folders (no files or subdirectories).
- Ignores system and development-related folders by default.

Example:

```python
import harrix_pylib as h

remove_empty_folders("C:/Projects/my_project")
remove_empty_folders("C:/Downloads", additional_patterns=["temp", "cache"])
```

<details>
<summary>Code:</summary>

```python
def remove_empty_folders(
    folder_path: Path | str, additional_patterns: list[str] | None = None, *, is_ignore_hidden: bool = True
) -> str:

    def is_folder_empty(path: Path) -> bool:
        """Check if folder is completely empty."""
        try:
            return not any(path.iterdir())
        except (OSError, PermissionError):
            return False

    def collect_all_folders(root_path: Path) -> list[Path]:
        """Collect all folders that should be processed, respecting ignore patterns."""
        folders = []

        try:
            for item in root_path.iterdir():
                if item.is_dir():
                    # Skip ignored folders
                    if should_ignore_path(item, additional_patterns, is_ignore_hidden=is_ignore_hidden):
                        continue

                    # Add current folder to list
                    folders.append(item)

                    # Recursively collect subfolders
                    folders.extend(collect_all_folders(item))
        except (OSError, PermissionError):
            pass

        return folders

    def remove_empty_folders_list(folders: list[Path]) -> int:
        """Remove empty folders from the list, starting from deepest level."""
        removed_count = 0

        # Sort folders by depth (deepest first) to handle nested empty folders
        folders_by_depth = sorted(folders, key=lambda p: len(p.parts), reverse=True)

        for folder in folders_by_depth:
            if folder.exists() and folder.is_dir() and is_folder_empty(folder):
                try:
                    folder.rmdir()
                    removed_count += 1
                except (OSError, PermissionError):
                    # Skip folders that can't be removed due to permissions
                    pass

        return removed_count

    folder_path = Path(folder_path)

    # Validate input path
    if not folder_path.exists():
        return f"❌ Folder {folder_path} does not exist."

    if not folder_path.is_dir():
        return f"❌ {folder_path} is not a directory."

    try:
        # Collect all folders that should be processed
        all_folders = collect_all_folders(folder_path)

        if not all_folders:
            return f"📁 No folders found to process in {folder_path.name}."

        # Remove empty folders
        removed_count = remove_empty_folders_list(all_folders)

        # Generate result message based on count
        if removed_count == 0:
            result_message = f"📁 No empty folders found in {folder_path.name}."
        elif removed_count == 1:
            result_message = f"✅ Removed 1 empty folder from {folder_path.name}."
        else:
            result_message = f"✅ Removed {removed_count} empty folders from {folder_path.name}"

    except Exception as e:
        return f"❌ Error removing empty folders: {e!s}"
    else:
        return result_message
```

</details>

## Function `rename_epub_file`

```python
def rename_epub_file(filename: Path | str) -> str
```

Rename EPUB file based on metadata from file content.

This function reads an EPUB file and extracts author, title, and year information
from its metadata (OPF file). The file is then renamed according to the pattern:
"LastName FirstName - Title - Year.epub" (year is optional).

If metadata extraction fails, the function attempts to transliterate the filename
from English to Russian, assuming it might be a transliterated Russian title.
If transliteration doesn't improve the filename, it remains unchanged.

Args:

- `filename` (`Path | str`): The path to the EPUB file to be processed.

Returns:

- `str`: A status message indicating the result of the operation.

Note:

- The function modifies the filename in place if changes are made.
- Requires 'transliterate' library for Russian transliteration.
- Handles various EPUB metadata formats and encodings.

Example:

```python
import harrix_pylib as h

rename_epub_file("C:/Books/unknown_book.epub")
```

<details>
<summary>Code:</summary>

```python
def rename_epub_file(filename: Path | str) -> str:

    def extract_epub_metadata(file_path: Path | str) -> tuple[str | None, str | None, str | None]:
        """Extract author, title, and year from EPUB file."""
        try:
            with zipfile.ZipFile(file_path, "r") as epub_zip:
                # Find the OPF file
                opf_file = None

                # First, try to find container.xml to get the OPF path
                try:
                    container_content = epub_zip.read("META-INF/container.xml").decode("utf-8")
                    opf_match = re.search(r'full-path="([^"]*\.opf)"', container_content)
                    if opf_match:
                        opf_file = opf_match.group(1)
                except Exception as e:
                    print(f"Error: {e!s}")

                # If container.xml method failed, look for OPF files directly
                if not opf_file:
                    for file_info in epub_zip.filelist:
                        if file_info.filename.endswith(".opf"):
                            opf_file = file_info.filename
                            break

                if not opf_file:
                    return None, None, None

                # Read and parse the OPF file
                opf_content = epub_zip.read(opf_file).decode("utf-8")

                # Extract metadata
                author = extract_epub_author(opf_content)
                title = extract_epub_title(opf_content)
                year = extract_epub_year(opf_content)

                return author, title, year

        except Exception:
            return None, None, None

    def extract_epub_author(opf_content: str) -> str | None:
        """Extract author from OPF content."""
        author_patterns = [
            r"<dc:creator[^>]*>(.*?)</dc:creator>",
            r"<creator[^>]*>(.*?)</creator>",
            r'<meta name="author" content="([^"]*)"',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, opf_content, re.DOTALL | re.IGNORECASE)
            if match:
                author_text = match.group(1).strip()
                # Remove HTML tags and entities
                author_text = re.sub(r"<[^>]+>", "", author_text)
                author_text = re.sub(r"&[^;]+;", "", author_text)
                author_text = author_text.strip()

                if author_text:
                    return format_author_name(author_text)

        return None

    def extract_epub_title(opf_content: str) -> str | None:
        """Extract title from OPF content."""
        title_patterns = [
            r"<dc:title[^>]*>(.*?)</dc:title>",
            r"<title[^>]*>(.*?)</title>",
            r'<meta name="title" content="([^"]*)"',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, opf_content, re.DOTALL | re.IGNORECASE)
            if match:
                title_text = match.group(1).strip()
                # Remove HTML tags and entities
                title_text = re.sub(r"<[^>]+>", "", title_text)
                title_text = re.sub(r"&[^;]+;", "", title_text)
                title_text = title_text.strip()

                if title_text:
                    return title_text

        return None

    def extract_epub_year(opf_content: str) -> str | None:
        """Extract year from OPF content."""
        year_patterns = [
            r"<dc:date[^>]*>.*?(\d{4}).*?</dc:date>",
            r"<date[^>]*>.*?(\d{4}).*?</date>",
            r'<meta name="date" content="[^"]*(\d{4})[^"]*"',
            r'<meta property="dcterms:created">.*?(\d{4}).*?</meta>',
            r'<meta property="dcterms:modified">.*?(\d{4}).*?</meta>',
        ]

        for pattern in year_patterns:
            match = re.search(pattern, opf_content, re.DOTALL | re.IGNORECASE)
            if match:
                year = match.group(1)
                # Validate year (should be reasonable)
                min_year = 1000
                max_year = 2100
                if min_year <= int(year) <= max_year:
                    return year

        return None

    def format_author_name(author_text: str) -> str:
        """Format author name as 'LastName FirstName' if possible."""
        if not author_text:
            return ""

        # Remove HTML tags and entities
        author_text = re.sub(r"<[^>]+>", "", author_text)
        author_text = re.sub(r"&[^;]+;", "", author_text)
        author_text = author_text.strip()

        # Split by spaces and try to identify first and last names
        parts = author_text.split()

        count_parts = 2
        if len(parts) >= count_parts:
            # Assume first part is first name, last part is last name
            # If there are middle names, include them with the first name
            first_name = " ".join(parts[:-1])
            last_name = parts[-1]
            return f"{last_name} {first_name}"
        # If only one part, return as is
        return author_text

    def clean_filename(text: str) -> str:
        """Clean text for use in filename."""
        if not text:
            return ""

        # Remove HTML entities and tags
        text = re.sub(r"&[^;]+;", "", text)
        text = re.sub(r"<[^>]+>", "", text)

        # Remove or replace invalid filename characters
        invalid_chars = r'[<>:"/\\|?*]'
        text = re.sub(invalid_chars, "", text)

        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def transliterate_filename(filename_stem: str) -> str:
        """Attempt to transliterate filename from English to Russian."""
        try:
            # Try reverse transliteration (English to Russian)
            transliterated = translit(filename_stem, "ru", reversed=True)

            # Check if transliteration made sense (contains Cyrillic characters)
            if re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", transliterated, re.IGNORECASE):
                return transliterated
        except Exception:
            return filename_stem
        else:
            return filename_stem

    filename = Path(filename)

    if not filename.exists():
        return f"❌ File {filename} does not exist."

    if filename.suffix.lower() != ".epub":
        return f"❌ File {filename} is not an EPUB file."

    # Extract metadata from EPUB file
    author, title, year = extract_epub_metadata(filename)

    new_name = None

    if author and title:
        # Clean the extracted data
        author = clean_filename(author)
        title = clean_filename(title)

        # Construct new filename
        new_name = f"{author} - {title} - {year}.epub" if year else f"{author} - {title}.epub"

    else:
        # Try transliteration
        original_stem = filename.stem
        transliterated = transliterate_filename(original_stem)

        if transliterated != original_stem:
            new_name = f"{transliterated}.epub"

    if new_name:
        new_name = clean_filename(new_name.replace(".epub", "")) + ".epub"
        new_path = filename.parent / new_name

        # Avoid overwriting existing files
        counter = 1
        while new_path.exists() and new_path != filename:
            name_without_ext = new_name.replace(".epub", "")
            new_name = f"{name_without_ext} ({counter}).epub"
            new_path = filename.parent / new_name
            counter += 1

        if new_path != filename:
            try:
                filename.rename(new_path)
            except Exception as e:
                return f"❌ Error renaming file: {e!s}"
            else:
                return f"✅ File renamed: {filename.name} → {new_name}"

    return f"📝 File {filename.name} left unchanged."
```

</details>

## Function `rename_fb2_file`

```python
def rename_fb2_file(filename: Path | str) -> str
```

Rename FB2 file based on metadata from file content.

This function reads an FB2 file and extracts author, title, and year information
from its XML metadata. The file is then renamed according to the pattern:
"LastName FirstName - Title - Year.fb2" (year is optional).

If metadata extraction fails, the function attempts to transliterate the filename
from English to Russian, assuming it might be a transliterated Russian title.
If transliteration doesn't improve the filename, it remains unchanged.

Args:

- `filename` (`Path | str`): The path to the FB2 file to be processed.

Returns:

- `str`: A status message indicating the result of the operation.

Note:

- The function modifies the filename in place if changes are made.
- Requires 'transliterate' library for Russian transliteration.
- Handles various FB2 metadata formats and encodings.

Example:

```python
import harrix_pylib as h

rename_fb2_file("C:/Books/unknown_book.fb2")
```

<details>
<summary>Code:</summary>

```python
def rename_fb2_file(filename: Path | str) -> str:

    def extract_fb2_metadata(file_path: Path | str) -> tuple[str | None, str | None, str | None]:
        """Extract author, title, and year from FB2 file."""
        try:
            with Path.open(Path(file_path), encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with Path.open(Path(file_path), encoding="windows-1251") as f:
                    content = f.read()
            except UnicodeDecodeError:
                return None, None, None

        # Clean up content for XML parsing
        content = re.sub(r"<\?xml[^>]*\?>", "", content)
        content = re.sub(r"<!DOCTYPE[^>]*>", "", content)

        try:
            # Find the description section
            desc_match = re.search(r"<description>(.*?)</description>", content, re.DOTALL)
            if not desc_match:
                return None, None, None

            desc_content = desc_match.group(1)

            # Extract author
            author = None
            first_name = None
            last_name = None

            # Try to extract first and last names separately
            author_patterns = [
                r"<first-name>(.*?)</first-name>.*?<last-name>(.*?)</last-name>",
                r"<last-name>(.*?)</last-name>.*?<first-name>(.*?)</first-name>",
            ]

            for pattern in author_patterns:
                match = re.search(pattern, desc_content, re.DOTALL)
                if match:
                    if "first-name" in pattern and pattern.index("first-name") < pattern.index("last-name"):
                        first_name = match.group(1).strip()
                        last_name = match.group(2).strip()
                    else:
                        last_name = match.group(1).strip()
                        first_name = match.group(2).strip()
                    break

            # If we have both first and last names, format as "LastName FirstName"
            if first_name and last_name:
                author = f"{last_name} {first_name}"
            else:
                # Fallback to other patterns
                fallback_patterns = [r"<author[^>]*>(.*?)</author>"]

                for pattern in fallback_patterns:
                    match = re.search(pattern, desc_content, re.DOTALL)
                    if match:
                        author_text = match.group(1).strip()
                        # Try to parse "FirstName LastName" format and reverse it
                        author = format_author_name(author_text)
                        break

            # Extract title
            title = None
            title_patterns = [r"<book-title>(.*?)</book-title>", r"<title[^>]*>(.*?)</title>"]

            for pattern in title_patterns:
                match = re.search(pattern, desc_content, re.DOTALL)
                if match:
                    title = match.group(1).strip()
                    # Remove HTML tags if present
                    title = re.sub(r"<[^>]+>", "", title)
                    break

            # Extract year
            year = None
            year_patterns = [r"<year>(\d{4})</year>", r"<date[^>]*>(\d{4})", r"(\d{4})"]

            for pattern in year_patterns:
                match = re.search(pattern, desc_content)
                if match:
                    year = match.group(1)
                    break

        except Exception:
            return None, None, None
        else:
            return author, title, year

    def format_author_name(author_text: str) -> str:
        """Format author name as 'LastName FirstName' if possible."""
        if not author_text:
            return ""

        # Remove HTML tags and entities
        author_text = re.sub(r"<[^>]+>", "", author_text)
        author_text = re.sub(r"&[^;]+;", "", author_text)
        author_text = author_text.strip()

        # Split by spaces and try to identify first and last names
        parts = author_text.split()

        count_parts = 2
        if len(parts) >= count_parts:
            # Assume first part is first name, last part is last name
            # If there are middle names, include them with the first name
            first_name = " ".join(parts[:-1])
            last_name = parts[-1]
            return f"{last_name} {first_name}"
        # If only one part, return as is
        return author_text

    def clean_filename(text: str) -> str:
        """Clean text for use in filename."""
        if not text:
            return ""

        # Remove HTML entities and tags
        text = re.sub(r"&[^;]+;", "", text)
        text = re.sub(r"<[^>]+>", "", text)

        # Remove or replace invalid filename characters
        invalid_chars = r'[<>:"/\\|?*]'
        text = re.sub(invalid_chars, "", text)

        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def transliterate_filename(filename_stem: str) -> str:
        """Attempt to transliterate filename from English to Russian."""
        try:
            # Try reverse transliteration (English to Russian)
            transliterated = translit(filename_stem, "ru", reversed=True)

            # Check if transliteration made sense (contains Cyrillic characters)
            if re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", transliterated, re.IGNORECASE):
                return transliterated
        except Exception:
            return filename_stem
        else:
            return filename_stem

    filename = Path(filename)

    if not filename.exists():
        return f"❌ File {filename} does not exist."

    if filename.suffix.lower() != ".fb2":
        return f"❌ File {filename} is not an FB2 file."

    # Extract metadata from FB2 file
    author, title, year = extract_fb2_metadata(filename)

    new_name = None

    if author and title:
        # Clean the extracted data
        author = clean_filename(author)
        title = clean_filename(title)

        # Construct new filename
        new_name = f"{author} - {title} - {year}.fb2" if year else f"{author} - {title}.fb2"

    else:
        # Try transliteration
        original_stem = filename.stem
        transliterated = transliterate_filename(original_stem)

        if transliterated != original_stem:
            new_name = f"{transliterated}.fb2"

    if new_name:
        new_name = clean_filename(new_name.replace(".fb2", "")) + ".fb2"
        new_path = filename.parent / new_name

        # Avoid overwriting existing files
        counter = 1
        while new_path.exists() and new_path != filename:
            name_without_ext = new_name.replace(".fb2", "")
            new_name = f"{name_without_ext} ({counter}).fb2"
            new_path = filename.parent / new_name
            counter += 1

        if new_path != filename:
            try:
                filename.rename(new_path)
            except Exception as e:
                return f"❌ Error renaming file: {e!s}"
            else:
                return f"✅ File renamed: {filename.name} → {new_name}"

    return f"📝 File {filename.name} left unchanged."
```

</details>

## Function `rename_file_spaces_to_hyphens`

```python
def rename_file_spaces_to_hyphens(filename: Path | str) -> str
```

Rename file by replacing spaces with hyphens in the filename.

This function takes any file and renames it by replacing all spaces in the filename
with hyphens. The file extension remains unchanged.

Args:

- `filename` (`Path | str`): The path to the file to be processed.

Returns:

- `str`: A status message indicating the result of the operation.

Note:

- The function modifies the filename in place if changes are made.
- Only renames files that contain spaces in their names.
- Preserves the file extension and path.
- Works with any file type.

Example:

```python
import harrix_pylib as h

rename_file_spaces_to_hyphens("C:/Books/my book title.fb2")
# Result: "my-book-title.fb2"

rename_file_spaces_to_hyphens("C:/Documents/my document.pdf")
# Result: "my-document.pdf"
```

<details>
<summary>Code:</summary>

```python
def rename_file_spaces_to_hyphens(filename: Path | str) -> str:
    filename = Path(filename)

    if not filename.exists():
        return f"❌ File {filename} does not exist."

    # Check if filename contains spaces
    if " " not in filename.stem:
        return f"📝 File {filename.name} left unchanged (no spaces found)."

    # Create new name by replacing spaces with hyphens
    new_stem = filename.stem.replace(" ", "-")
    new_name = f"{new_stem}{filename.suffix}"
    new_path = filename.parent / new_name

    # Avoid overwriting existing files
    counter = 1
    while new_path.exists() and new_path != filename:
        new_name = f"{new_stem} ({counter}){filename.suffix}"
        new_path = filename.parent / new_name
        counter += 1

    if new_path != filename:
        try:
            filename.rename(new_path)
        except Exception as e:
            return f"❌ Error renaming file: {e!s}"
        else:
            return f"✅ File renamed: {filename.name} → {new_name}"

    return f"📝 File {filename.name} left unchanged."
```

</details>

## Function `rename_files_by_mapping`

```python
def rename_files_by_mapping(folder_path: Path | str, rename_mapping: dict[str, str]) -> str
```

Rename files recursively based on a mapping dictionary while respecting ignore patterns.

This function traverses the directory tree and renames files according to the provided
mapping dictionary. It processes all files recursively, including nested files, but
does not enter or process folders that should be ignored based on common ignore patterns.

Args:

- `folder_path` (`Path | str`): The root path to start renaming files from.
- `rename_mapping` (`dict[str, str]`): Dictionary mapping old filename to new filename.

Returns:

- `str`: A status message indicating the result of the operation with count of renamed files.

Note:

- Uses `should_ignore_path()` function to determine which folders to skip.
- Only renames files, not directories.
- If target filename already exists, the operation is skipped for that file.
- Preserves file extensions and paths.

Example:

```python
import harrix_pylib as h

mapping = {
    "old_file.txt": "new_file.txt",
    "readme.md": "README_NEW.md",
    "config.json": "settings.json"
}

result = rename_files_by_mapping("C:/Projects/my_project", mapping)
print(result)
```

<details>
<summary>Code:</summary>

```python
def rename_files_by_mapping(folder_path: Path | str, rename_mapping: dict[str, str]) -> str:

    def collect_all_files(root_path: Path) -> list[Path]:
        """Collect all files that should be processed, respecting ignore patterns."""
        files = []

        try:
            for item in root_path.iterdir():
                if item.is_dir():
                    # Skip ignored folders
                    if should_ignore_path(item):
                        continue

                    # Recursively collect files from subfolders
                    files.extend(collect_all_files(item))
                elif item.is_file():
                    # Add file to list
                    files.append(item)
        except (OSError, PermissionError):
            pass

        return files

    def rename_files_from_list(files: list[Path], mapping: dict[str, str]) -> tuple[int, int]:
        """Rename files from the list based on mapping dictionary."""
        renamed_count = 0
        skipped_count = 0

        for file_path in files:
            old_name = file_path.name

            # Check if filename is in mapping
            if old_name in mapping:
                new_name = mapping[old_name]
                new_path = file_path.parent / new_name

                # Skip if target file already exists
                if new_path.exists():
                    skipped_count += 1
                    continue

                try:
                    file_path.rename(new_path)
                    renamed_count += 1
                except (OSError, PermissionError):
                    # Skip files that can't be renamed due to permissions
                    skipped_count += 1

        return renamed_count, skipped_count

    folder_path = Path(folder_path)

    # Validate input path
    if not folder_path.exists():
        return f"❌ Folder {folder_path} does not exist."

    if not folder_path.is_dir():
        return f"❌ {folder_path} is not a directory."

    # Validate rename mapping
    if not rename_mapping:
        return "❌ Rename mapping dictionary is empty."

    try:
        # Collect all files that should be processed
        all_files = collect_all_files(folder_path)

        if not all_files:
            return f"📁 No files found to process in {folder_path.name}."

        # Rename files based on mapping
        renamed_count, skipped_count = rename_files_from_list(all_files, rename_mapping)

        # Generate result message based on counts
        if renamed_count == 0 and skipped_count == 0:
            result_message = f"📁 No files matched the rename mapping in {folder_path.name}."
        elif renamed_count == 0:
            result_message = f"⚠️ No files were renamed in {folder_path.name}. {skipped_count} were skipped."
        elif skipped_count == 0:
            if renamed_count == 1:
                result_message = f"✅ Renamed 1 file in {folder_path.name}."
            else:
                result_message = f"✅ Renamed {renamed_count} files in {folder_path.name}."
        else:
            result_message = f"✅ Renamed {renamed_count} files in {folder_path.name}. {skipped_count} were skipped."

    except Exception as e:
        return f"❌ Error renaming files: {e!s}"
    else:
        return result_message
```

</details>

## Function `rename_largest_images_to_featured`

```python
def rename_largest_images_to_featured(path: Path | str) -> str
```

Find the largest image in each subdirectory of the given path and renames it to 'featured-image'.

Args:

- `path` (`Path | str`): The directory path to search for subdirectories containing images.

Returns:

- `str`: A string containing the log of operations performed, with each action on a new line.

Note:

- Only processes subdirectories, not the main directory itself.
- Looks for image files with extensions: .jpg, .jpeg, .png, .avif, .svg
- Will not overwrite existing 'featured-image' files.

Example:

```python
import harrix_pylib as h
from pathlib import Path

result = h.rename_largest_images_to_featured("C:/articles/")
print(result)
```

<details>
<summary>Code:</summary>

```python
def rename_largest_images_to_featured(path: Path | str) -> str:
    result_lines = []
    # Convert path to Path object if it's a string
    if not isinstance(path, Path):
        path = Path(path)

    # Make sure path exists and is a directory
    if not path.exists() or not path.is_dir():
        msg = f"❌ Error: {path} is not a valid directory"
        raise ValueError(msg)

    # Image extensions to look for
    image_extensions = [".jpg", ".jpeg", ".png", ".avif", ".svg"]

    # Get all subdirectories
    subdirs = [d for d in path.iterdir() if d.is_dir()]

    renamed_count = 0

    for subdir in subdirs:
        result_lines.append(f"Processing directory: {subdir}")

        # Find all image files in this subdirectory
        image_files = []
        for ext in image_extensions:
            image_files.extend(subdir.glob(f"*{ext}"))

        if not image_files:
            result_lines.append(f"❌ No image files found in {subdir}")
            continue

        # Find the largest file
        largest_file = max(image_files, key=lambda f: f.stat().st_size)

        # Create the new filename with the same extension
        new_filename = subdir / f"featured-image{largest_file.suffix}"

        # Rename the file
        try:
            # Check if the target file already exists
            if new_filename.exists():
                result_lines.append(f"⚠️ Warning: {new_filename} already exists. Skipping.")
                continue

            result_lines.append(f"✅ Renaming '{largest_file.name}' to '{new_filename.name}'")
            largest_file.rename(new_filename)
            renamed_count += 1

        except OSError as e:
            result_lines.append(f"❌ Error renaming file: {e}")

    result_lines.append(f"Total files renamed: {renamed_count}")
    return "\n".join(result_lines)
```

</details>

## Function `rename_pdf_file`

```python
def rename_pdf_file(filename: Path | str) -> str
```

Rename PDF file based on metadata from file content.

This function reads a PDF file and extracts author, title, and year information
from its metadata. The file is then renamed according to the pattern:
"LastName FirstName - Title - Year.pdf" (year is optional).

If metadata extraction fails, the function attempts to transliterate the filename
from English to Russian, assuming it might be a transliterated Russian title.
If transliteration doesn't improve the filename, it remains unchanged.

Args:

- `filename` (`Path | str`): The path to the PDF file to be processed.
- `verbose` (`bool`): If True, print detailed debug information. Default is False.

Returns:

- `str`: A status message indicating the result of the operation.

Note:

- The function modifies the filename in place if changes are made.
- Requires 'pypdf' library for PDF metadata extraction.
- Requires 'transliterate' library for Russian transliteration.
- Requires 'cryptography>=3.1' for encrypted PDF files.
- Handles various PDF metadata formats and encodings.
- Preserves Russian characters and avoids renaming if they would be lost.

Example:

```python
import harrix_pylib as h

rename_pdf_file("C:/Books/unknown_book.pdf")
rename_pdf_file("C:/Books/unknown_book.pdf", verbose=True)  # With debug output
```

<details>
<summary>Code:</summary>

```python
def rename_pdf_file(filename: Path | str, *, is_verbose: bool = False) -> str:

    def is_valid_pdf(file_path: Path) -> bool:
        """Quick check if file is likely a valid PDF."""
        try:
            min_file_size = 100
            if file_path.stat().st_size < min_file_size:  # Too small to be valid PDF
                return False

            with Path.open(file_path, "rb") as f:
                header = f.read(8)
                return header.startswith(b"%PDF-")
        except Exception:
            return False

    def extract_pdf_metadata(file_path: Path | str) -> tuple[str | None, str | None, str | None]:
        """Extract author, title, and year from PDF file with better error handling."""
        try:
            with Path.open(Path(file_path), "rb") as f:
                # Check file size
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                f.seek(0)  # Return to beginning

                min_file_size = 100
                if file_size < min_file_size:  # Too small
                    if is_verbose:
                        print(f"Debug: File {file_path} is too small to be a valid PDF")
                    return None, None, None

                # Check PDF header
                header = f.read(8)
                f.seek(0)
                if not header.startswith(b"%PDF-"):
                    if is_verbose:
                        print(f"Debug: File {file_path} doesn't have valid PDF header")
                    return None, None, None

                # Use strict=False for more tolerant parsing
                pdf_reader = pypdf.PdfReader(f, strict=False)

                # Check if file is encrypted
                if pdf_reader.is_encrypted:
                    if is_verbose:
                        print(f"Debug: File {file_path} is encrypted, skipping")
                    return None, None, None

                metadata = pdf_reader.metadata

                if not metadata:
                    return None, None, None

                # Extract metadata fields
                author = None
                if metadata.author:
                    author = format_author_name(str(metadata.author))

                title = None
                if metadata.title:
                    title = str(metadata.title).strip()

                # Extract year from creation date or modification date
                year = _extract_year_from_metadata(metadata)

                return author, title, year

        except Exception as e:
            if is_verbose:
                print(f"Debug: Error extracting PDF metadata from {file_path}: {e}")

        return None, None, None

    def _extract_year_from_metadata(metadata: object | None) -> str | None:
        """Extract year from PDF metadata."""
        date_fields = []
        if metadata is not None:
            # Try to get creation and modification date attributes safely
            creation_date = getattr(metadata, "creation_date", None)
            modification_date = getattr(metadata, "modification_date", None)
            date_fields = [creation_date, modification_date]

        for date_field in date_fields:
            if date_field:
                try:
                    # Handle different date formats
                    if hasattr(date_field, "year"):
                        return str(date_field.year)
                    # Try to extract year from string representation
                    date_str = str(date_field)
                    year_match = re.search(r"(\d{4})", date_str)
                    if year_match:
                        return year_match.group(1)
                except Exception as e:
                    if is_verbose:
                        print(f"Debug: Error extracting year from date field: {e}")
                    continue

        # Also try to extract year from subject
        text_fields = []
        if metadata is not None:
            subject = getattr(metadata, "subject", None)
            if subject:
                text_fields = [subject]
        for field in text_fields:
            if field:
                year_match = re.search(r"(\d{4})", str(field))
                if year_match:
                    return year_match.group(1)

        return None

    def extract_pdf_text_metadata(file_path: Path | str) -> tuple[str | None, str | None, str | None]:
        """Extract metadata from PDF text content as fallback."""
        try:
            with Path.open(Path(file_path), "rb") as f:
                pdf_reader = pypdf.PdfReader(f, strict=False)

                # Check if file is encrypted
                if pdf_reader.is_encrypted:
                    if is_verbose:
                        print(f"Debug: File {file_path} is encrypted, cannot extract text")
                    return None, None, None

                # Extract text from first few pages
                text = ""
                max_pages = min(3, len(pdf_reader.pages))

                for page_num in range(max_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n"
                    except Exception as e:
                        if is_verbose:
                            print(f"Debug: Error extracting text from page {page_num + 1}: {e}")
                        continue

                if not text.strip():
                    return None, None, None

                # Look for common patterns in academic papers and books
                author = None
                title = None
                year = None

                # Extract title (usually in first lines, often in caps or large font)
                lines = text.split("\n")[:10]  # First 10 lines
                for line in lines:
                    line_modify = line.strip()
                    min_length = 10
                    max_length = 200
                    if (
                        len(line_modify) > min_length
                        and len(line_modify) < max_length
                        and not re.match(r"^\d+$", line_modify)
                        and not re.match(r"^Page \d+", line_modify)
                        and (not title or len(line_modify) > len(title))
                    ):
                        title = line_modify

                # Extract author patterns
                author_patterns = [
                    r"(?:Author|By|Written by)[:\s]+([A-Za-zА-Яа-я\s\.]+)",  # ignore: HP001 # noqa: RUF001
                    r"([A-Za-zА-Яа-я]+\s+[A-Za-zА-Яа-я]+)(?:\s*,\s*Ph\.?D\.?)?",  # ignore: HP001 # noqa: RUF001
                ]

                for pattern in author_patterns:
                    match = re.search(pattern, text[:1000], re.IGNORECASE)
                    if match:
                        author = format_author_name(match.group(1))
                        break

                # Extract year
                year_match = re.search(r"(?:Copyright|©|\b)(\d{4})\b", text[:2000])
                if year_match:
                    year = year_match.group(1)

                return author, title, year

        except Exception as e:
            if is_verbose:
                print(f"Debug: Error extracting text metadata from {file_path}: {e}")
            return None, None, None

    def format_author_name(author_text: str) -> str:
        """Format author name as 'LastName FirstName' if possible."""
        if not author_text:
            return ""

        # Remove extra whitespace and clean up
        author_text = re.sub(r"\s+", " ", author_text.strip())

        # Remove common suffixes and prefixes
        author_text = re.sub(
            r"\b(?:Dr\.?|Prof\.?|Ph\.?D\.?|M\.?D\.?|Mr\.?|Mrs\.?|Ms\.?)\s*", "", author_text, flags=re.IGNORECASE
        )

        # Split by spaces and try to identify first and last names
        parts = author_text.split()

        count_parts = 2
        if len(parts) >= count_parts:
            # Assume first part is first name, last part is last name
            # If there are middle names, include them with the first name
            first_name = " ".join(parts[:-1])
            last_name = parts[-1]
            return f"{last_name} {first_name}"

        # If only one part, return as is
        return author_text

    def clean_filename(text: str) -> str:
        """Clean text for use in filename."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove or replace invalid filename characters
        invalid_chars = r'[<>:"/\\|?*]'
        text = re.sub(invalid_chars, "", text)

        # Remove problematic characters but preserve Cyrillic
        text = re.sub(r"[^\w\s\-.,()[\]{}\u0430-\u044F\u0451\u0410-\u042F\u0401]", "", text)

        # Limit length to avoid filesystem issues
        max_length_filename = 200
        if len(text) > max_length_filename:
            text = text[:max_length_filename].rsplit(" ", 1)[0]  # Cut at word boundary

        return text.strip()

    def has_cyrillic(text: str) -> bool:
        """Check if text contains Cyrillic characters."""
        return bool(re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", text))

    def transliterate_filename(filename_stem: str) -> str:
        """Attempt to transliterate filename from English to Russian."""
        try:
            # Try reverse transliteration (English to Russian)
            transliterated = translit(filename_stem, "ru", reversed=True)

            # Check if transliteration made sense (contains Cyrillic characters)
            if has_cyrillic(transliterated) and transliterated != filename_stem:
                return transliterated
        except Exception as e:
            if is_verbose:
                print(f"Debug: Error during transliteration: {e}")

        return filename_stem

    def would_lose_cyrillic(original: str, new: str) -> bool:
        """Check if the new name would lose Cyrillic characters from original."""
        return has_cyrillic(original) and not has_cyrillic(new)

    def validate_file(filename: Path) -> str | None:
        """Validate file exists and is PDF. Returns error message or None."""
        if not filename.exists():
            return f"❌ File {filename} does not exist."

        if filename.suffix.lower() != ".pdf":
            return f"❌ File {filename} is not a PDF file."

        # Quick PDF validation
        if not is_valid_pdf(filename):
            return f"⚠️ File {filename.name} is not a valid PDF, skipping."

        return None

    def generate_new_name(author: str | None, title: str | None, year: str | None, original_name: str) -> str | None:
        """Generate new filename based on metadata or transliteration."""
        if author and title:
            # Clean the extracted data
            author = clean_filename(author)
            title = clean_filename(title)

            # Construct new filename
            new_name = f"{author} - {title} - {year}.pdf" if year else f"{author} - {title}.pdf"

            # Check if we would lose Cyrillic characters
            new_stem = new_name.replace(".pdf", "")
            if would_lose_cyrillic(original_name, new_stem):
                return None

            return new_name

        # Try transliteration
        transliterated = transliterate_filename(original_name)
        if transliterated != original_name and has_cyrillic(transliterated):
            return f"{transliterated}.pdf"

        return None

    def attempt_rename(filename: Path, new_name: str, original_name: str) -> str:
        """Attempt to rename the file and return status message."""
        new_name = clean_filename(new_name.replace(".pdf", "")) + ".pdf"
        new_path = filename.parent / new_name

        # Final check for Cyrillic character loss
        final_stem = new_name.replace(".pdf", "")
        if would_lose_cyrillic(original_name, final_stem):
            return f"📝 File {filename.name} left unchanged (would lose Cyrillic characters)."

        # Avoid overwriting existing files
        counter = 1
        while new_path.exists() and new_path != filename:
            name_without_ext = new_name.replace(".pdf", "")
            new_name = f"{name_without_ext} ({counter}).pdf"
            new_path = filename.parent / new_name
            counter += 1

        if new_path != filename:
            try:
                filename.rename(new_path)
            except Exception as e:
                return f"❌ Error renaming file: {e!s}"
            else:
                return f"✅ File renamed: {filename.name} → {new_name}"

        return f"❗ File {filename.name} left unchanged."

    # Main function logic
    filename = Path(filename)

    # Early validation check
    validation_error = validate_file(filename)
    if validation_error:
        return validation_error

    original_name = filename.stem

    # Extract metadata from PDF file
    author, title, year = extract_pdf_metadata(filename)

    # If primary metadata extraction failed, try text-based extraction
    if not (author and title):
        author_text, title_text, year_text = extract_pdf_text_metadata(filename)
        author = author or author_text
        title = title or title_text
        year = year or year_text

    # Generate new name
    new_name = generate_new_name(author, title, year, original_name)

    if not new_name:
        return f"❗ File {filename.name} left unchanged."

    # Check if we would lose Cyrillic characters before renaming
    new_stem = new_name.replace(".pdf", "")
    if would_lose_cyrillic(original_name, new_stem):
        return f"📝 File {filename.name} left unchanged (would lose Cyrillic characters)."

    # Attempt to rename the file
    return attempt_rename(filename, new_name, original_name)
```

</details>

## Function `should_ignore_path`

```python
def should_ignore_path(path: Path | str, additional_patterns: list[str] | None = None) -> bool
```

Check if a path should be ignored based on common ignore patterns.

Args:

- `path` (`Path | str`): The path to check for ignoring.
- `additional_patterns` (`list[str] | None`): Additional patterns to ignore. Defaults to `None`.
- `is_ignore_hidden` (`bool`): Whether to ignore hidden files/folders (starting with dot). Defaults to `True`.

Returns:

- `bool`: `True` if the path should be ignored, `False` otherwise.

Example:

```python
import harrix_pylib as h
from pathlib import Path

path1 = Path(".git")
result1 = h.should_ignore_path(path1)
print(result1)

path2 = Path("my_folder")
result2 = h.should_ignore_path(path2)
print(result2)

path3 = Path("temp")
result3 = h.should_ignore_path(path3, additional_patterns=["temp", "logs"])
print(result3)
```

<details>
<summary>Code:</summary>

```python
def should_ignore_path(
    path: Path | str, additional_patterns: list[str] | None = None, *, is_ignore_hidden: bool = True
) -> bool:
    path = Path(path)

    # Base patterns to ignore
    base_patterns = {
        "__pycache__",
        ".cache",
        ".DS_Store",
        ".git",
        ".idea",
        ".npm",
        ".pytest_cache",
        ".venv",
        ".vs",
        ".vscode",
        "build",
        "config",
        "dist",
        "node_modules",
        "tests",
        "Thumbs.db",
        "venv",
    }

    # Add additional patterns if provided
    if additional_patterns:
        base_patterns.update(additional_patterns)

    # Check for hidden files/folders
    if is_ignore_hidden and path.name.startswith("."):
        return True

    # Check against patterns
    return path.name in base_patterns
```

</details>

## Function `tree_view_folder`

```python
def tree_view_folder(path: Path | str) -> str
```

Generate a tree-like representation of folder contents.

Example output:

```text
├─ note1
│  ├─ featured-image.png
│  └─ note1.md
└─ note2
    └─ note2.md
```

Args:

- `path` (`Path | str`): The root folder path to start the tree from.
- `is_ignore_hidden_folders` (`bool`): If `True`, hidden folders and files (starting with a dot or
  matching common ignore patterns like `.git`, `__pycache__`, `node_modules`, etc.) are shown in the tree
  but their contents are not explored. Defaults to `False`.

Returns:

- `str`: A string representation of the folder structure with ASCII art tree elements.

Note:

- This function uses recursion to traverse folders. It handles `PermissionError`
  by excluding folders without permission.
- Uses ASCII characters to represent tree branches (`├──`, `└──`, `│`).
- When `is_ignore_hidden_folders` is `True`, ignored folders are displayed but not traversed.

Example:

```python
import harrix_pylib as h


tree = h.file.tree_view_folder("C:/Notes")
print(tree)

# Show ignored folders but don't explore their contents
tree_clean = h.file.tree_view_folder("C:/Notes", is_ignore_hidden_folders=True)
print(tree_clean)
```

<details>
<summary>Code:</summary>

```python
def tree_view_folder(path: Path | str, *, is_ignore_hidden_folders: bool = False) -> str:

    def __tree(path: Path | str, *, is_ignore_hidden_folders: bool = False, prefix: str = "") -> Iterator[str]:
        path = Path(path)
        try:
            contents = list(path.iterdir())
        except PermissionError:
            contents = []

        pointers = ["├─ "] * (len(contents) - 1) + ["└─ "]
        for pointer, item in zip(pointers, contents, strict=False):
            yield prefix + pointer + item.name

            # Only traverse into directories if they shouldn't be ignored or if we're not ignoring
            if item.is_dir() and not (is_ignore_hidden_folders and should_ignore_path(item.name)):
                extension = "│  " if pointer == "├─ " else "   "
                yield from __tree(item, is_ignore_hidden_folders=is_ignore_hidden_folders, prefix=prefix + extension)

    return "\n".join(list(__tree(Path(path), is_ignore_hidden_folders=is_ignore_hidden_folders)))
```

</details>
