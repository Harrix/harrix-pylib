---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# harrix-pylib

![harrix-pylib](https://raw.githubusercontent.com/Harrix/harrix-pylib/refs/heads/main/img/featured-image.svg)

Common functions for working in Python (>= 3.12) for [my projects](https://github.com/Harrix?tab=repositories).

![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

Documentation: [docs](https://github.com/Harrix/harrix-pylib/blob/main/docs/index.md).

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

### File `funcs_dev.py`

Doc: [funcs_dev.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_dev.md)

| Function/Class | Description |
|----------------|-------------|
| `get_project_root` | Finds the root folder of the current project. |
| `load_config` | Loads configuration from a JSON file. |
| `run_powershell_script` | Runs a PowerShell script with the given commands. |
| `run_powershell_script_as_admin` | Executes a PowerShell script with administrator privileges and captures the output. |
| `write_in_output_txt` | Decorator to write function output to a temporary file and optionally display it. |

### File `funcs_file.py`

Doc: [funcs_file.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_file.md)

| Function/Class | Description |
|----------------|-------------|
| `all_to_parent_folder` | Moves all files from subfolders within the given path to the parent folder and then |
| `apply_func` | Applies a given function to all files with a specified extension in a folder and its sub-folders. |
| `check_featured_image` | Checks for the presence of `featured_image.*` files in every child folder, not recursively. |
| `clear_directory` | This function clears directory with sub-directories. |
| `find_max_folder_number` | Finds the highest folder number in a given folder based on a pattern. |
| `open_file_or_folder` | Opens a file or folder using the operating system's default application. |
| `tree_view_folder` | Generates a tree-like representation of folder contents. |

### File `funcs_md.py`

Doc: [funcs_md.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_md.md)

| Function/Class | Description |
|----------------|-------------|
| `add_author_book` | Adds the author and the title of the book to the quotes and formats them as Markdown quotes. |
| `add_diary_new_diary` | Creates a new diary entry for the current day and time. |
| `add_diary_new_dream` | Creates a new dream diary entry for the current day and time with placeholders for dream descriptions. |
| `add_diary_new_note` | Adds a new note to the diary or dream diary for the given base path. |
| `add_image_captions` | Processes a markdown file to add captions to images based on their alt text. |
| `add_note` | Adds a note to the specified base path. |
| `get_yaml` | Function gets YAML from text of the Markdown file. |
| `identify_code_blocks` | Processes a list of text lines to identify code blocks and yield each line with a boolean flag. |
| `remove_yaml` |     Function removes YAML from text of the Markdown file. |
| `replace_section` | Replaces a section in a file defined by `title_section` with the provided `replace_content`. |
| `sort_sections` | Sorts the sections of a markdown document by their headings, maintaining YAML front matter |
| `split_yaml_content` | Splits a markdown note into YAML front matter and the main content. |

### File `funcs_py.py`

Doc: [funcs_py.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_py.md)

| Function/Class | Description |
|----------------|-------------|
| `create_uv_new_project` | Creates a new project using uv, initializes it, and sets up necessary files. |
| `extract_functions_and_classes` | Extracts all classes and functions from a Python file and formats them into a markdown list. |
| `lint_and_fix_python_code` | Lints and fixes the provided Python code using the `ruff` formatter. |
| `sort_py_code` | Sorts the Python code in the given file by organizing classes, functions, and statements. |

### File `funcs_pyside.py`

Doc: [funcs_pyside.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_pyside.md)

| Function/Class | Description |
|----------------|-------------|
| `create_emoji_icon` | Creates an icon with the given emoji. |
| `generate_markdown_from_qmenu` | Generates a markdown representation of a QMenu structure. |

