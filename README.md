# harrix-pylib

![harrix-pylib](img/featured-image.svg)

Common functions for working in Python (>= 3.12) for [my projects](https://github.com/Harrix?tab=repositories).

![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

## Install

- pip: `pip install harrix-pylib`
- uv: `uv add harrix-pylib`

## Quick start

Examples of using the library:

```py
import harrixpylib as h

h.file.clear_directory("C:/temp_dir")
```

```py
import harrixpylib as h

md_clean = h.file.remove_yaml_from_markdown("""
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode
""")
print(md_clean)  # Installing VSCode
```

## List of functions

### funcs_file

- `def all_to_parent_folder(path: Path | str) -> str`: Moves all files from subfolders within the given path to the parent folder and then
- `def apply_func(path: Path | str, ext: str, func: Callable) -> str`: Applies a given function to all files with a specified extension in a folder and its sub-folders.
- `def check_featured_image(path: str) -> tuple[bool, str]`: Checks for the presence of `featured_image.*` files in every child folder, not recursively.
- `def clear_directory(path: Path | str) -> None`: This function clears directory with sub-directories.
- `def find_max_folder_number(base_path: str, start_pattern: str) -> int`: Finds the highest folder number in a given folder based on a pattern.
- `def open_file_or_folder(path: Path | str) -> None`: Opens a file or folder using the operating system's default application.
- `def tree_view_folder(path: Path, is_ignore_hidden_folders: bool) -> str`: Generates a tree-like representation of folder contents.

## Functions

### Function `all_to_parent_folder`

Moves all files from subfolders within the given path to the parent folder and then
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
C:  est
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
C:  est
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

### Function `apply_func`

Applies a given function to all files with a specified extension in a folder and its sub-folders.

Args:

- `path` (`str`): The path to the root folder where the function should be applied. Defaults to `None`.
- `ext` (`str`): The file extension to filter files by. Should include the dot (e.g., '.py').
- `func` (`Callable`): The function to apply to each file. This function should take an argument, the file path.

Returns:

- `str`: A string listing the results of applying the function to each file, with each result on a new line.

### Function `check_featured_image`

Checks for the presence of `featured_image.*` files in every child folder, not recursively.

This function goes through each immediate subfolder of the given path and checks if there
is at least one file with the name starting with "featured-image". If such a file is missing
in any folder, it logs this occurrence.

Args:

- `path` (`str`): Path to the folder being checked. Can be either a string or a Path object.

Returns:

- `tuple[bool, str]`: A tuple where:
    - The first element (`bool`) indicates if all folders have a `featured_image.*` file.
    - The second element (`str`) contains a formatted string with status or error messages.

Note:

- This function does not search recursively; it only checks the immediate child folders.
- The output string uses ANSI color codes for visual distinction of errors.

### Function `clear_directory`

This function clears directory with sub-directories.

Args:

- `path` (Path | str): Path of directory.

Returns:

- `None`.

Examples:

```py
import harrix-pylib as h

h.file.clear_directory("C:/temp_dir")
```

```py
from pathlib import Path
import harrix-pylib as h

folder = Path(__file__).resolve().parent / "data/temp"
folder.mkdir(parents=True, exist_ok=True)
Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
...
h.file.clear_directory(folder)
```

### Function `find_max_folder_number`

Finds the highest folder number in a given folder based on a pattern.

Args:

- `base_path` (`str`): The base folder path to search for folders.
- `start_pattern` (`str`): A regex pattern for matching folder names.

Returns:

- `int`: The maximum folder number found, or 0 if no matches are found.

### Function `open_file_or_folder`

Opens a file or folder using the operating system's default application.

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

### Function `tree_view_folder`

Generates a tree-like representation of folder contents.

Example output:

```text
├─ note1
│  ├─ featured-image.png
│  └─ note1.md
└─ note2
    └─ note2.md
```

Args:

- `path` (`Path`): The root folder path to start the tree from.
- `is_ignore_hidden_folders` (`bool`): If `True`, hidden folders (starting with a dot) are excluded from the tree.
  Defaults to `False`.

Returns:

- `str`: A string representation of the folder structure with ASCII art tree elements.

Note:

- This function uses recursion to traverse folders. It handles `PermissionError`
  by excluding folders without permission.
- Uses ASCII characters to represent tree branches (`├──`, `└──`, `│`).
