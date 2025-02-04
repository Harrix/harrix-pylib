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

| Function/Class                 | Description                                                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `add_author_book`              | Adds the author and the title of the book to the quotes and formats them as Markdown quotes.                |
| `add_diary_new_diary`          | Creates a new diary entry for the current day and time.                                                     |
| `add_diary_new_dream`          | Creates a new dream diary entry for the current day and time with placeholders for dream descriptions.      |
| `add_diary_new_note`           | Adds a new note to the diary or dream diary for the given base path.                                        |
| `add_note`                     | Adds a note to the specified base path.                                                                     |
| `format_yaml`                  | Formats YAML content in a file, ensuring proper indentation and structure.                                  |
| `generate_image_captions_file` | Processes a markdown file to add captions to images based on their alt text.                                |
| `generate_toc_with_links`      | Generates a Table of Contents (TOC) with clickable links for a given Markdown file and inserts or refreshes |
| `get_yaml`                     | Function gets YAML from text of the Markdown file.                                                          |
| `identify_code_blocks`         | Processes a list of text lines to identify code blocks and yield each line with a boolean flag.             |
| `remove_yaml`                  | Function removes YAML from text of the Markdown file.                                                       |
| `remove_yaml_and_code`         | Removes YAML front matter and code blocks, and returns the remaining content.                               |
| `replace_section`              | Replaces a section in a file defined by `title_section` with the provided `replace_content`.                |
| `sort_sections`                | Sorts the sections of a markdown document by their headings, maintaining YAML front matter                  |
| `split_yaml_content`           | Splits a markdown note into YAML front matter and the main content.                                         |

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
- From `harrix-swiss-knife`, call the command `Python` → `Generate MD documentation in …`.
  and select folder `harrix-pylib`.
- Create a commit `➕ Add function def <function>()`.
- Update the version in `pyproject.toml`.
- Delete the folder `dist`.
- Run `uv sync --upgrade`.
- Run `uv build`.
- Run `uv publish --token <token>`.
- Create a commit `🚀 Build version <number>`.

Example of a function:

````python
def format_yaml(filename: Path | str) -> str:
    """
    Formats YAML content in a file, ensuring proper indentation and structure.

    Args:

    - `filename` (`Path | str`): The path to the file containing YAML content.

    Returns:

    - `str`: A message indicating whether the file was changed or not.

    Note:

    - If the file does not contain YAML front matter separated by "---", it will treat the entire
      content as markdown without YAML.
    - The function will overwrite the file if changes are made to the YAML formatting.
    - It uses a custom YAML dumper (`IndentDumper`) to adjust indentation.

    Example:

    ```python
    import harrix_pylib as h
    from pathlib import Path

    path = Path('example.md')
    print(h.md.format_yaml(path))
    ```
    """
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    parts = document.split("---", 2)
    if len(parts) < 3:
        yaml_md, content_md = "", document
    else:
        yaml_md, content_md = f"---{parts[1]}---", parts[2].lstrip()

    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))

    class IndentDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(IndentDumper, self).increase_indent(flow, False)

    yaml_md = yaml.dump(
        data_yaml,
        Dumper=IndentDumper,
        sort_keys=False,
        allow_unicode=True,
        explicit_start=True,
        default_flow_style=False,
    ) + '---'

    document_new = yaml_md +  "\n\n" + content_md
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
````

Example of a test:

```python
def test_format_yaml():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/format_yaml__before.md").read_text(encoding="utf8")
    md_after = Path(current_folder / "tests/data/format_yaml__after.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.format_yaml(temp_filename)
        md_applied = temp_filename.read_text(encoding="utf8")

    assert md_after == md_applied
```

### Minimum Python Version

We determine the minimum Python version using [vermin](https://github.com/netromdk/vermin):

```shell
vermin src
```

However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

</details>

## License

License: [MIT](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).
