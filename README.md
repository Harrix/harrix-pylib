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

### funcs_file.py

| Function | Description |
|----------|-------------|
| `all_to_parent_folder` | Moves all files from subfolders within the given path to the parent folder and then |
| `apply_func` | Applies a given function to all files with a specified extension in a folder and its sub-folders. |
| `check_featured_image` | Checks for the presence of `featured_image.*` files in every child folder, not recursively. |
| `clear_directory` | This function clears directory with sub-directories. |
| `find_max_folder_number` | Finds the highest folder number in a given folder based on a pattern. |
| `open_file_or_folder` | Opens a file or folder using the operating system's default application. |
| `tree_view_folder` | Generates a tree-like representation of folder contents. |
