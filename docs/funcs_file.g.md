---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_file.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Function `all_to_parent_folder`](#function-all_to_parent_folder)
- [Function `apply_func`](#function-apply_func)
- [Function `check_featured_image`](#function-check_featured_image)
- [Function `check_func`](#function-check_func)
- [Function `clear_directory`](#function-clear_directory)
- [Function `find_max_folder_number`](#function-find_max_folder_number)
- [Function `open_file_or_folder`](#function-open_file_or_folder)
- [Function `rename_largest_images_to_featured`](#function-rename_largest_images_to_featured)
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
        # Exclude all folders and files starting with a dot
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
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
                        list_lines.append([f"  - {item}\n" for item in result])
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
- `func` (`Callable[[Path | str], lis]`): A function that takes a file path and returns a list
  representing check results or errors.

Returns:

- `list`: A combined list of all check results from all processed files.

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
        # Exclude all folders and files starting with a dot
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
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

## Function `should_ignore_path`

```python
def should_ignore_path(path: Path | str, additional_patterns: list[str] | None = None, ignore_hidden: bool = True) -> bool
```

Check if a path should be ignored based on common ignore patterns.

Args:

- `path` (`Path | str`): The path to check for ignoring.
- `additional_patterns` (`list[str] | None`): Additional patterns to ignore. Defaults to `None`.
- `ignore_hidden` (`bool`): Whether to ignore hidden files/folders (starting with dot). Defaults to `True`.

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
    path: Path | str, additional_patterns: list[str] | None = None, ignore_hidden: bool = True
) -> bool:
    path = Path(path)

    # Base patterns to ignore
    base_patterns = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".idea",
        ".vscode",
        "build",
        "dist",
        ".DS_Store",
        "Thumbs.db",
        ".cache",
        ".npm",
        ".vs",
    }

    # Add additional patterns if provided
    if additional_patterns:
        base_patterns.update(additional_patterns)

    # Check for hidden files/folders
    if ignore_hidden and path.name.startswith("."):
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
- `is_ignore_hidden_folders` (`bool`): If `True`, hidden folders (starting with a dot or
  in the list of ignored folders) are excluded from the tree. Defaults to `False`.

Returns:

- `str`: A string representation of the folder structure with ASCII art tree elements.

Note:

- This function uses recursion to traverse folders. It handles `PermissionError`
  by excluding folders without permission.
- Uses ASCII characters to represent tree branches (`├──`, `└──`, `│`).

Example:

```python
import harrix_pylib as h


tree = h.file.tree_view_folder("C:/Notes")
print(tree)
```

<details>
<summary>Code:</summary>

```python
def tree_view_folder(path: Path | str, *, is_ignore_hidden_folders: bool = False) -> str:

    def __tree(path: Path | str, *, is_ignore_hidden_folders: bool = False, prefix: str = "") -> Iterator[str]:
        path = Path(path)
        if is_ignore_hidden_folders and (path.name.startswith(".") or should_ignore_path(path.name)):
            contents = []
        else:
            try:
                contents = list(path.iterdir())
            except PermissionError:
                contents = []
        pointers = ["├─ "] * (len(contents) - 1) + ["└─ "]
        for pointer, item in zip(pointers, contents, strict=False):
            yield prefix + pointer + item.name
            if item.is_dir():
                extension = "│  " if pointer == "├─ " else "   "
                yield from __tree(item, is_ignore_hidden_folders=is_ignore_hidden_folders, prefix=prefix + extension)

    return "\n".join(list(__tree(Path(path), is_ignore_hidden_folders=is_ignore_hidden_folders)))
```

</details>
