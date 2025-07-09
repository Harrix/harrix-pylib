"""Functions for working with files."""

import contextlib
import platform
import re
import shutil
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path

from transliterate import translit


def all_to_parent_folder(path: Path | str) -> str:
    """Move all files from subfolders within the given path to the parent folder and then
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

    """
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


def apply_func(path: Path | str, ext: str, func: Callable) -> str:
    """Recursively apply a function to all files with a specified extension in a directory.

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

    """
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


def check_featured_image(path: Path | str) -> tuple[bool, str]:
    """Check for the presence of `featured_image.*` files in every child folder, not recursively.

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

    """
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


def check_func(path: Path | str, ext: str, func: Callable[[Path | str], list]) -> list:
    """Recursively applies a checking function to all files with a specified extension in a directory.

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

    """
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


def clear_directory(path: Path | str) -> None:
    """Clear directory with sub-directories.

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

    """
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def find_max_folder_number(base_path: str, start_pattern: str) -> int:
    """Find the highest folder number in a given folder based on a pattern.

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

    """
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


def open_file_or_folder(path: Path | str) -> None:
    """Open a file or folder using the operating system's default application.

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

    """
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


def rename_fb2_file(filename: Path | str) -> str:
    """Rename FB2 file based on metadata from file content.

    This function reads an FB2 file and extracts author, title, and year information
    from its XML metadata. The file is then renamed according to the pattern:
    "Author - Title - Year.fb2" (year is optional).

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

    """

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
            author_patterns = [
                r"<first-name>(.*?)</first-name>.*?<last-name>(.*?)</last-name>",
                r"<last-name>(.*?)</last-name>.*?<first-name>(.*?)</first-name>",
                r"<author[^>]*>(.*?)</author>",
            ]

            for pattern in author_patterns:
                match = re.search(pattern, desc_content, re.DOTALL)
                if match:
                    count_elements = 2
                    if len(match.groups()) == count_elements:
                        first_name = match.group(1).strip()
                        last_name = match.group(2).strip()
                        author = f"{first_name} {last_name}"
                    else:
                        author = match.group(1).strip()
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


def rename_largest_images_to_featured(path: Path | str) -> str:
    """Find the largest image in each subdirectory of the given path and renames it to 'featured-image'.

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

    """
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


def should_ignore_path(
    path: Path | str, additional_patterns: list[str] | None = None, *, is_ignore_hidden: bool = True
) -> bool:
    """Check if a path should be ignored based on common ignore patterns.

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

    """
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


def tree_view_folder(path: Path | str, *, is_ignore_hidden_folders: bool = False) -> str:
    """Generate a tree-like representation of folder contents.

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

    """

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
