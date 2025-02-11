---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# harrix-pylib

![harrix-pylib](https://raw.githubusercontent.com/Harrix/harrix-pylib/refs/heads/main/img/featured-image.svg)

Common functions for working in Python (>= 3.10) for [my projects](https://github.com/Harrix?tab=repositories).

![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

GitHub: <https://github.com/Harrix/harrix-pylib>.

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

| Function/Class                   | Description                                                                         |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| `get_project_root`               | Finds the root folder of the current project.                                       |
| `load_config`                    | Loads configuration from a JSON file.                                               |
| `run_powershell_script`          | Runs a PowerShell script with the given commands.                                   |
| `run_powershell_script_as_admin` | Executes a PowerShell script with administrator privileges and captures the output. |
| `write_in_output_txt`            | Decorator to write function output to a temporary file and optionally display it.   |

### File `funcs_file.py`

Doc: [funcs_file.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_file.md)

| Function/Class           | Description                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------- |
| `all_to_parent_folder`   | Moves all files from subfolders within the given path to the parent folder and then               |
| `apply_func`             | Applies a given function to all files with a specified extension in a folder and its sub-folders. |
| `check_featured_image`   | Checks for the presence of `featured_image.*` files in every child folder, not recursively.       |
| `clear_directory`        | This function clears directory with sub-directories.                                              |
| `find_max_folder_number` | Finds the highest folder number in a given folder based on a pattern.                             |
| `open_file_or_folder`    | Opens a file or folder using the operating system's default application.                          |
| `tree_view_folder`       | Generates a tree-like representation of folder contents.                                          |

### File `funcs_md.py`

Doc: [funcs_md.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_md.md)

| Function/Class                           | Description                                                                                                 |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `add_diary_new_diary`                    | Creates a new diary entry for the current day and time.                                                     |
| `add_diary_new_dream`                    | Creates a new dream diary entry for the current day and time with placeholders for dream descriptions.      |
| `add_diary_new_note`                     | Adds a new note to the diary or dream diary for the given base path.                                        |
| `add_note`                               | Adds a note to the specified base path.                                                                     |
| `append_path_to_local_links_images_line` | Appends a path to local links and images within a Markdown line.                                            |
| `download_and_replace_images`            | Downloads remote images in Markdown text and replaces their URLs with local paths.                          |
| `download_and_replace_images_content`    | Downloads remote images in Markdown text and replaces their URLs with local paths.                          |
| `format_yaml`                            | Formats YAML content in a file, ensuring proper indentation and structure.                                  |
| `format_yaml_content`                    | Formats the YAML front matter within the given markdown text.                                               |
| `generate_author_book`                   | Adds the author and the title of the book to the quotes and formats them as Markdown quotes.                |
| `generate_image_captions`                | Processes a markdown file to add captions to images based on their alt text.                                |
| `generate_image_captions_content`        | Generates image captions in the provided markdown text.                                                     |
| `generate_toc_with_links`                | Generates a Table of Contents (TOC) with clickable links for a given Markdown file and inserts or refreshes |
| `generate_toc_with_links_content`        | Generates a Table of Contents (TOC) with links for the provided markdown content.                           |
| `get_yaml_content`                       | Function gets YAML from text of the Markdown file.                                                          |
| `identify_code_blocks`                   | Processes a list of text lines to identify code blocks and yield each line with a boolean flag.             |
| `identify_code_blocks_line`              | Parses a single line of Markdown to identify inline code blocks.                                            |
| `increase_heading_level_content`         | Increases the heading level of Markdown content.                                                            |
| `remove_yaml_and_code_content`           | Removes YAML front matter and code blocks, and returns the remaining content.                               |
| `remove_yaml_content`                    | Function removes YAML from text of the Markdown file.                                                       |
| `replace_section`                        | Replaces a section in a file defined by `title_section` with the provided `replace_content`.                |
| `replace_section_content`                | Replaces a section in the markdown text defined by `title_section` with the provided `replace_content`.     |
| `sort_sections`                          | Sorts the sections of a markdown file by their headings, maintaining YAML front matter                      |
| `sort_sections_content`                  | Sorts the sections of a markdown text by their headings, maintaining YAML front matter                      |
| `split_yaml_content`                     | Splits a markdown note into YAML front matter and the main content.                                         |

### File `funcs_py.py`

Doc: [funcs_py.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_py.md)

| Function/Class                  | Description                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------------- |
| `create_uv_new_project`         | Creates a new project using uv, initializes it, and sets up necessary files.                 |
| `extract_functions_and_classes` | Extracts all classes and functions from a Python file and formats them into a markdown list. |
| `generate_docs_for_project`     | Generates documentation for all Python files within a given project folder.                  |
| `generate_md_docs_content`      | Generates Markdown documentation for a single Python file.                                   |
| `lint_and_fix_python_code`      | Lints and fixes the provided Python code using the `ruff` formatter.                         |
| `sort_py_code`                  | Sorts the Python code in the given file by organizing classes, functions, and statements.    |

## Development

<details>
<summary>Deploy on an empty machine ⬇️</summary>

For me:

- Install [uv](https://docs.astral.sh/uv/) ([Installing and Working with uv (Python) in VSCode](https://github.com/Harrix/harrix.dev-articles-2025-en/blob/main/uv-vscode-python/uv-vscode-python.md)), VSCode (with python extensions), Git.

- Clone project:

  ```shell
  mkdir C:/GitHub
  cd C:/GitHub
  git clone https://github.com/Harrix/harrix-pylib.git
  ```

- Open the folder `C:/GitHub/harrix-pylib` in VSCode.

- Open a terminal `Ctrl` + `` ` ``.

- Run `uv sync`.

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `isort .` — sort imports.
- `ruff format` — format the project's Python files.
- `ruff check` — lint the project's Python files.
- `ruff check --fix` — lint and fix the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `vermin src` — determines the minimum version of Python.

</details>

<details>
<summary>Adding a new function ⬇️</summary>

For me:

- Add the function in `src/harrix_pylib/funcs_<module>.py`.
- Write a docstring in Markdown style.
- Add an example in Markdown style.
- Add a test in `tests/funcs_<module>.py`.
- Run `pytest`.
- From `harrix-swiss-knife`, call the command `Python` → `Sort classes, methods, functions in PY files`.
  and select folder `harrix-pylib`.
- From `harrix-swiss-knife`, call the command `Python` → `Generate MD documentation in …`
  and select folder `harrix-pylib`.
- Create a commit `➕ Add function <function>()`.
- Update the version in `pyproject.toml`.
- Delete the folder `dist`.
- Run `uv sync --upgrade`.
- Run `uv build`.
- Run `uv publish --token <token>`.
- Create a commit `🚀 Build version <number>`.

### Minimum Python Version

We determine the minimum Python version using [vermin](https://github.com/netromdk/vermin):

```shell
vermin src
```

However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

</details>

## License

License: [MIT](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).
