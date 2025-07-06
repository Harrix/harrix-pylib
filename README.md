# harrix-pylib

![Featured image](https://raw.githubusercontent.com/Harrix/harrix-pylib/refs/heads/main/img/featured-image.svg)

This is a **Python library** containing common functions for working in Python (>= 3.10) for [my projects](https://github.com/Harrix?tab=repositories).

![GitHub](https://img.shields.io/badge/GitHub-harrix--pylib-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

GitHub: <https://github.com/Harrix/harrix-pylib>

Documentation: [docs](https://github.com/Harrix/harrix-pylib/blob/main/docs/index.md)

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

| Function/Class                   | Description                                                                        |
| -------------------------------- | ---------------------------------------------------------------------------------- |
| `get_project_root`               | Find the root folder of the current project.                                       |
| `load_config`                    | Load configuration from a JSON file.                                               |
| `run_command`                    | Run a console command and return its output.                                       |
| `run_powershell_script`          | Run a PowerShell script with the given commands.                                   |
| `run_powershell_script_as_admin` | Execute a PowerShell script with administrator privileges and captures the output. |
| `write_in_output_txt`            | Decorate to write function output to a temporary file and optionally display it.   |

### File `funcs_file.py`

Doc: [funcs_file.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_file.md)

| Function/Class                      | Description                                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------------------- |
| `all_to_parent_folder`              | Move all files from subfolders within the given path to the parent folder and then                |
| `apply_func`                        | Recursively apply a function to all files with a specified extension in a directory.              |
| `check_featured_image`              | Check for the presence of `featured_image.*` files in every child folder, not recursively.        |
| `check_func`                        | Recursively applies a checking function to all files with a specified extension in a directory.   |
| `clear_directory`                   | Clear directory with sub-directories.                                                             |
| `find_max_folder_number`            | Find the highest folder number in a given folder based on a pattern.                              |
| `open_file_or_folder`               | Open a file or folder using the operating system's default application.                           |
| `rename_largest_images_to_featured` | Find the largest image in each subdirectory of the given path and renames it to 'featured-image'. |
| `should_ignore_path`                | Check if a path should be ignored based on common ignore patterns.                                |
| `tree_view_folder`                  | Generate a tree-like representation of folder contents.                                           |

### File `funcs_md.py`

Doc: [funcs_md.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_md.md)

| Function/Class                               | Description                                                                                                     |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `add_diary_entry_in_year`                    | Add a new diary entry to the yearly Markdown file.                                                              |
| `add_diary_new_dairy_in_year`                | Add a new diary entry to the yearly diary file.                                                                 |
| `add_diary_new_diary`                        | Create a new diary entry for the current day and time.                                                          |
| `add_diary_new_dream`                        | Create a new dream diary entry for the current day and time with placeholders for dream descriptions.           |
| `add_diary_new_dream_in_year`                | Add a new dream diary entry to the yearly dream file.                                                           |
| `add_diary_new_note`                         | Add a new note to the diary or dream diary for the given base path.                                             |
| `add_note`                                   | Add a note to the specified base path.                                                                          |
| `append_path_to_local_links_images_line`     | Append a path to local links and images within a Markdown line.                                                 |
| `combine_markdown_files`                     | Combine multiple Markdown files in a folder into a single file with intelligent YAML header merging.            |
| `combine_markdown_files_recursively`         | Recursively process a folder structure and combines Markdown files in each folder that meets specific criteria. |
| `delete_g_md_files_recursively`              | Delete all `*.g.md` files recursively in the specified folder.                                                  |
| `download_and_replace_images`                | Download remote images in Markdown text and replaces their URLs with local paths.                               |
| `download_and_replace_images_content`        | Download remote images in Markdown text and replaces their URLs with local paths.                               |
| `format_quotes_as_markdown_content`          | Convert raw text with quotes into Markdown format.                                                              |
| `format_yaml`                                | Format YAML content in a file, ensuring proper indentation and structure.                                       |
| `format_yaml_content`                        | Format the YAML front matter within the given Markdown text.                                                    |
| `generate_author_book`                       | Add the author and the title of the book to the quotes and formats them as Markdown quotes.                     |
| `generate_image_captions`                    | Process a Markdown file to add captions to images based on their alt text.                                      |
| `generate_image_captions_content`            | Generate image captions in the provided Markdown text.                                                          |
| `generate_short_note_toc_with_links`         | Generate a separate Markdown file with only the Table of Contents (TOC) from a given Markdown file.             |
| `generate_short_note_toc_with_links_content` | Generate a Markdown content with only the Table of Contents (TOC) from a given Markdown text.                   |
| `generate_summaries`                         | Generate two summary files for a directory of year-based Markdown files.                                        |
| `generate_toc_with_links`                    | Generate a Table of Contents (TOC) with clickable links for a given Markdown file and inserts or refreshes      |
| `generate_toc_with_links_content`            | Generate a Table of Contents (TOC) with links for the provided Markdown content.                                |
| `get_yaml_content`                           | Get YAML from text of the Markdown file.                                                                        |
| `identify_code_blocks`                       | Process a sequence of text lines to identify code blocks and yield each line with a boolean flag.               |
| `identify_code_blocks_line`                  | Parse a single line of Markdown to identify inline code blocks.                                                 |
| `increase_heading_level_content`             | Increase the heading level of Markdown content.                                                                 |
| `remove_toc_content`                         | Remove the table of contents (TOC) section from a Markdown document.                                            |
| `remove_yaml_and_code_content`               | Remove YAML front matter and code blocks, and returns the remaining content.                                    |
| `remove_yaml_content`                        | Remove YAML from text of the Markdown file.                                                                     |
| `replace_section`                            | Replace a section in a file defined by `title_section` with the provided `replace_content`.                     |
| `replace_section_content`                    | Replace a section in the Markdown text defined by `title_section` with the provided `replace_content`.          |
| `sort_sections`                              | Sort the sections of a Markdown file by their headings, maintaining YAML front matter                           |
| `sort_sections_content`                      | Sort sections by their `##` headings: top sections first, then dates in descending order,                       |
| `split_toc_content`                          | Separate the Table of Contents (TOC) from the rest of the Markdown content.                                     |
| `split_yaml_content`                         | Split a Markdown note into YAML front matter and the main content.                                              |

### File `funcs_py.py`

Doc: [funcs_py.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/funcs_py.md)

| Function/Class                  | Description                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| `create_uv_new_project`         | Create a new project using uv, initializes it, and sets up necessary files.                 |
| `extract_functions_and_classes` | Extract all classes and functions from a Python file and formats them into a Markdown list. |
| `generate_md_docs`              | Generate documentation for all Python files within a given project folder.                  |
| `generate_md_docs_content`      | Generate Markdown documentation for a single Python file.                                   |
| `lint_and_fix_python_code`      | Lints and fixes the provided Python code using the `ruff` formatter.                        |
| `sort_py_code`                  | Sorts the Python code in the given file by organizing classes, functions, and statements.   |

### File `markdown_checker.py`

Doc: [markdown_checker.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/markdown_checker.md)

| Function/Class          | Description                                                            |
| ----------------------- | ---------------------------------------------------------------------- |
| Class `MarkdownChecker` | Class for checking Markdown files for compliance with specified rules. |

### File `python_checker.py`

Doc: [python_checker.md](https://github.com/Harrix/harrix-pylib/tree/main/docs/python_checker.md)

| Function/Class        | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| Class `PythonChecker` | Class for checking Python files for compliance with specified rules. |

## License

License: [MIT](https://github.com/Harrix/harrix-pylib/blob/main/LICENSE.md).
