---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# Harrix PyLib

![Featured image](https://raw.githubusercontent.com/Harrix/harrix-pylib/refs/heads/main/img/featured-image.svg)

🐍 Common **Python functions (3.11+)** library for my projects for [my projects](https://github.com/Harrix?tab=repositories).

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🏃 Quick start](#-quick-start)
- [📚 List of functions](#-list-of-functions)
  - [📄 File `funcs_dev.py`](#-file-funcs_devpy)
  - [📄 File `funcs_file.py`](#-file-funcs_filepy)
  - [📄 File `funcs_img.py`](#-file-funcs_imgpy)
  - [📄 File `funcs_md.py`](#-file-funcs_mdpy)
  - [📄 File `funcs_py.py`](#-file-funcs_pypy)
  - [📄 File `img_tools.py`](#-file-img_toolspy)
  - [📄 File `markdown_checker.py`](#-file-markdown_checkerpy)
  - [📄 File `python_checker.py`](#-file-python_checkerpy)
  - [📄 File `code_guard.py`](#-file-code_guardpy)
  - [📄 File `escape_format.py`](#-file-escape_formatpy)
  - [📄 File `formatter.py`](#-file-formatterpy)
  - [📄 File `front_matter.py`](#-file-front_matterpy)
  - [📄 File `list_format.py`](#-file-list_formatpy)
  - [📄 File `options.py`](#-file-optionspy)
  - [📄 File `parser.py`](#-file-parserpy)
  - [📄 File `printer.py`](#-file-printerpy)
  - [📄 File `table_format.py`](#-file-table_formatpy)
  - [📄 File `wiki_plugin.py`](#-file-wiki_pluginpy)
  - [📄 File `cleanup.py`](#-file-cleanuppy)
  - [📄 File `hidden.py`](#-file-hiddenpy)
  - [📄 File `optimizer.py`](#-file-optimizerpy)
  - [📄 File `paths.py`](#-file-pathspy)
  - [📄 File `serialize.py`](#-file-serializepy)
  - [📄 File `shapes.py`](#-file-shapespy)
  - [📄 File `structure.py`](#-file-structurepy)
  - [📄 File `styles.py`](#-file-stylespy)
  - [📄 File `xml_tags.py`](#-file-xml_tagspy)
- [📄 License](#-license)
- [👤 Author](#-author)

</details>

![GitHub](https://img.shields.io/badge/GitHub-harrix--pylib-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

GitHub: <https://github.com/Harrix/harrix-pylib>

Documentation: [docs](https://github.com/Harrix/harrix-pylib/blob/main/docs/index.g.md)

## ✨ Features

- 📁 **File Operations** - Directory management, file processing, archive handling
- 📝 **Markdown Tools** - YAML processing, TOC generation, content manipulation
- 🔧 **Development Utils** - Project setup, code formatting, documentation generation
- 🛡️ **Code Checkers** - Custom validation rules for Python and Markdown (complements standard linters)

## 📦 Installation

Using `pip`:

```shell
pip install harrix-pylib
```

Using `uv` (recommended):

```shell
uv add harrix-pylib
```

## 🏃 Quick start

Examples of using the library:

```python
import harrixpylib as h

h.file.clear_directory("C:/temp_dir")
```

```python
import harrixpylib as h

md_clean = h.file.remove_yaml_content("""
---
categories: [it, program]
tags: [VSCode, FAQ]
---
# Installing VSCode
""")
print(md_clean)
```

## 📚 List of functions

### 📄 File `funcs_dev.py`

Doc: [funcs_dev.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md)

| Function/Class                                                                                                                                       | Description                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 🔧 [`config_load`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-config_load)                                       | Load configuration from a JSON file.                                               |
| 🔧 [`config_save`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-config_save)                                       | Save configuration to a JSON file.                                                 |
| 🔧 [`config_update_value`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-config_update_value)                       | Update a single configuration value and save it to a JSON file.                    |
| 🔧 [`get_project_root`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-get_project_root)                             | Find the root folder of the current project.                                       |
| 🔧 [`run_command`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-run_command)                                       | Run a console command and return its output.                                       |
| 🔧 [`run_powershell_script`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-run_powershell_script)                   | Run a PowerShell script with the given commands.                                   |
| 🔧 [`run_powershell_script_as_admin`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-run_powershell_script_as_admin) | Execute a PowerShell script with administrator privileges and captures the output. |
| 🔧 [`write_in_output_txt`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_dev.g.md#-function-write_in_output_txt)                       | Decorate to write function output to a temporary file and optionally display it.   |

### 📄 File `funcs_file.py`

Doc: [funcs_file.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md)

| Function/Class                                                                                                                                              | Description                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 🔧 [`all_to_parent_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-all_to_parent_folder)                           | Move all files from subfolders within the given path to the parent folder and then                |
| 🔧 [`apply_func`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-apply_func)                                               | Recursively apply a function to all files with a specified extension in a directory.              |
| 🔧 [`check_featured_image`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-check_featured_image)                           | Check for the presence of `featured_image.*` files in every child folder, not recursively.        |
| 🔧 [`check_func`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-check_func)                                               | Recursively applies a checking function to all files with a specified extension in a directory.   |
| 🔧 [`clear_directory`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-clear_directory)                                     | Clear directory with sub-directories.                                                             |
| 🔧 [`collect_text_files_to_markdown`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-collect_text_files_to_markdown)       | Create a Markdown document containing the contents of text files.                                 |
| 🔧 [`extract_zip_archive`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-extract_zip_archive)                             | Extract ZIP archive to the folder where the archive is located and remove the archive file.       |
| 🔧 [`find_max_folder_number`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-find_max_folder_number)                       | Find the highest folder number in a given folder based on a pattern.                              |
| 🔧 [`list_files_simple`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-list_files_simple)                                 | Generate a simple list of all files in a directory structure.                                     |
| 🔧 [`open_file_or_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-open_file_or_folder)                             | Open a file or folder using the operating system's default application.                           |
| 🔧 [`remove_empty_folders`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-remove_empty_folders)                           | Remove all empty folders recursively while respecting ignore patterns.                            |
| 🔧 [`rename_epub_file`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-rename_epub_file)                                   | Rename EPUB file based on metadata from file content.                                             |
| 🔧 [`rename_fb2_file`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-rename_fb2_file)                                     | Rename FB2 file based on metadata from file content.                                              |
| 🔧 [`rename_file_spaces_to_hyphens`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-rename_file_spaces_to_hyphens)         | Rename file by replacing spaces with hyphens in the filename.                                     |
| 🔧 [`rename_files_by_mapping`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-rename_files_by_mapping)                     | Rename files recursively based on a mapping dictionary while respecting ignore patterns.          |
| 🔧 [`rename_largest_images_to_featured`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-rename_largest_images_to_featured) | Find the largest image in each subdirectory of the given path and renames it to 'featured-image'. |
| 🔧 [`rename_pdf_file`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-rename_pdf_file)                                     | Rename PDF file based on metadata from file content.                                              |
| 🔧 [`should_ignore_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-should_ignore_path)                               | Check if a path should be ignored based on common ignore patterns.                                |
| 🔧 [`tree_view_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-tree_view_folder)                                   | Generate a tree-like representation of folder contents.                                           |
| 🔧 [`_clean_filename`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-_clean_filename)                                     | Clean text for use in filename.                                                                   |
| 🔧 [`_format_author_name`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-_format_author_name)                             | Format author name as 'LastName FirstName' if possible.                                           |
| 🔧 [`_resolve_unique_rename_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-_resolve_unique_rename_path)             | Return a non-colliding destination path and final filename.                                       |
| 🔧 [`_transliterate_filename`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_file.g.md#-function-_transliterate_filename)                     | Attempt to transliterate filename from English to Russian.                                        |

### 📄 File `funcs_img.py`

Doc: [funcs_img.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_img.g.md)

| Function/Class                                                                                                                             | Description                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| 🔧 [`optimize_image_with_tools`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_img.g.md#-function-optimize_image_with_tools) | Optimize GIF, MP4, or AVIF using ffmpeg, avifenc, and avifdec.        |
| 🔧 [`optimize_svg`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_img.g.md#-function-optimize_svg)                           | Optimize an SVG file and write the result.                            |
| 🔧 [`optimize_svg_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_img.g.md#-function-optimize_svg_content)           | Optimize SVG markup to a compact form similar to SVGO preset-default. |
| 🔧 [`optimize_svg_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_img.g.md#-function-optimize_svg_folder)             | Optimize all SVG files in a folder.                                   |

### 📄 File `funcs_md.py`

Doc: [funcs_md.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md)

| Function/Class                                                                                                                                                              | Description                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 🔧 [`add_diary_entry_in_year`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_entry_in_year)                                       | Add a new diary entry to the yearly Markdown file.                                                              |
| 🔧 [`add_diary_new_cases_in_year`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_new_cases_in_year)                               | Add new case entries to the yearly cases file.                                                                  |
| 🔧 [`add_diary_new_dairy_in_year`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_new_dairy_in_year)                               | Add a new diary entry to the yearly diary file.                                                                 |
| 🔧 [`add_diary_new_diary`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_new_diary)                                               | Create a new diary entry for the current day and time.                                                          |
| 🔧 [`add_diary_new_dream`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_new_dream)                                               | Create a new dream diary entry for the current day and time with placeholders for dream descriptions.           |
| 🔧 [`add_diary_new_dream_in_year`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_new_dream_in_year)                               | Add a new dream diary entry to the yearly dream file.                                                           |
| 🔧 [`add_diary_new_note`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_diary_new_note)                                                 | Add a new note to the diary or dream diary for the given base path.                                             |
| 🔧 [`add_note`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-add_note)                                                                     | Add a note to the specified base path.                                                                          |
| 🔧 [`append_path_to_local_links_images_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-append_path_to_local_links_images_line)         | Append a path to local links and images within a Markdown line.                                                 |
| 🔧 [`append_yaml_tag`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-append_yaml_tag)                                                       | Append a YAML tag to a Markdown file and save it.                                                               |
| 🔧 [`collect_subfolder_md`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-collect_subfolder_md)                                             | Collect Markdown files from a subfolder for combine operations.                                                 |
| 🔧 [`combine_markdown_files`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-combine_markdown_files)                                         | Combine multiple Markdown files in a folder into a single file with intelligent YAML header merging.            |
| 🔧 [`combine_markdown_files_recursively`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-combine_markdown_files_recursively)                 | Recursively process a folder structure and combines Markdown files in each folder that meets specific criteria. |
| 🔧 [`decrease_heading_level_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-decrease_heading_level_content)                         | Decrease the heading level of Markdown content.                                                                 |
| 🔧 [`delete_g_md_files_recursively`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-delete_g_md_files_recursively)                           | Delete all `*.g.md` files recursively in the specified folder.                                                  |
| 🔧 [`download_and_replace_images`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-download_and_replace_images)                               | Download remote images in Markdown text and replaces their URLs with local paths.                               |
| 🔧 [`download_and_replace_images_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-download_and_replace_images_content)               | Download remote images in Markdown text and replaces their URLs with local paths.                               |
| 🔧 [`format_markdown`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-format_markdown)                                                       | Format a Markdown file in place when content changes.                                                           |
| 🔧 [`format_markdown_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-format_markdown_content)                                       | Format Markdown content using the harrix-pylib Markdown formatter.                                              |
| 🔧 [`format_markdown_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-format_markdown_folder)                                         | Recursively format Markdown files in a folder.                                                                  |
| 🔧 [`format_quotes_as_markdown_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-format_quotes_as_markdown_content)                   | Convert raw text with quotes into Markdown format.                                                              |
| 🔧 [`format_yaml`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-format_yaml)                                                               | Format YAML content in a file, ensuring proper indentation and structure.                                       |
| 🔧 [`format_yaml_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-format_yaml_content)                                               | Format the YAML front matter within the given Markdown text.                                                    |
| 🔧 [`generate_author_book`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_author_book)                                             | Add the author and the title of the book to the quotes and formats them as Markdown quotes.                     |
| 🔧 [`generate_id`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_id)                                                               | Return exactly the same anchor slug GitHub creates for a Markdown heading.                                      |
| 🔧 [`generate_image_captions`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_image_captions)                                       | Process a Markdown file to add captions to images based on their alt text.                                      |
| 🔧 [`generate_image_captions_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_image_captions_content)                       | Generate image captions in the provided Markdown text.                                                          |
| 🔧 [`generate_short_note_toc_with_links`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_short_note_toc_with_links)                 | Generate a separate Markdown file with only the Table of Contents (TOC) from a given Markdown file.             |
| 🔧 [`generate_short_note_toc_with_links_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_short_note_toc_with_links_content) | Generate a Markdown content with only the Table of Contents (TOC) from a given Markdown text.                   |
| 🔧 [`generate_summaries`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_summaries)                                                 | Generate two summary files for a directory of year-based Markdown files.                                        |
| 🔧 [`generate_toc_with_links`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_toc_with_links)                                       | Generate a Table of Contents (TOC) with clickable links for a given Markdown file and inserts or refreshes      |
| 🔧 [`generate_toc_with_links_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-generate_toc_with_links_content)                       | Generate a Table of Contents (TOC) with links for the provided Markdown content.                                |
| 🔧 [`get_set_variables_from_yaml`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-get_set_variables_from_yaml)                               | Generate a sorted list of all variables from YAML from all Markdown files in folder recursively.                |
| 🔧 [`get_yaml_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-get_yaml_content)                                                     | Get YAML from text of the Markdown file.                                                                        |
| 🔧 [`identify_code_blocks`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-identify_code_blocks)                                             | Process a sequence of text lines to identify code blocks and yield each line with a boolean flag.               |
| 🔧 [`identify_code_blocks_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-identify_code_blocks_line)                                   | Parse a single line of Markdown to identify inline code blocks.                                                 |
| 🔧 [`increase_heading_level_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-increase_heading_level_content)                         | Increase the heading level of Markdown content.                                                                 |
| 🔧 [`is_note_in_named_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-is_note_in_named_folder)                                       | Check whether a Markdown path uses the named-folder layout.                                                     |
| 🔧 [`iter_note_md_in_folder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-iter_note_md_in_folder)                                         | Iterate scannable note Markdown files in a folder.                                                              |
| 🔧 [`named_note_md_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-named_note_md_path)                                                 | Build the canonical named-folder path for a note.                                                               |
| 🔧 [`note_md_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-note_md_path)                                                             | Resolve the path to an existing note, preferring the named-folder layout.                                       |
| 🔧 [`remove_markdown_formatting_for_headings`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-remove_markdown_formatting_for_headings)       | Remove Markdown formatting from text.                                                                           |
| 🔧 [`remove_toc_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-remove_toc_content)                                                 | Remove the table of contents (TOC) section from a Markdown document.                                            |
| 🔧 [`remove_yaml_and_code_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-remove_yaml_and_code_content)                             | Remove YAML front matter and code blocks, and returns the remaining content.                                    |
| 🔧 [`remove_yaml_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-remove_yaml_content)                                               | Remove YAML from text of the Markdown file.                                                                     |
| 🔧 [`replace_section`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-replace_section)                                                       | Replace a section in a file defined by `title_section` with the provided `replace_content`.                     |
| 🔧 [`replace_section_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-replace_section_content)                                       | Replace a section in the Markdown text defined by `title_section` with the provided `replace_content`.          |
| 🔧 [`resolve_md_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-resolve_md_path)                                                       | Resolve a Markdown path to an existing file, including named-folder layout.                                     |
| 🔧 [`sort_sections`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-sort_sections)                                                           | Sort the sections of a Markdown file by their headings, maintaining YAML front matter                           |
| 🔧 [`sort_sections_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-sort_sections_content)                                           | Sort sections by their `##` headings: top sections first, then dates in descending order,                       |
| 🔧 [`split_toc_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-split_toc_content)                                                   | Separate the Table of Contents (TOC) from the rest of the Markdown content.                                     |
| 🔧 [`split_yaml_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-split_yaml_content)                                                 | Split a Markdown note into YAML front matter and the main content.                                              |
| 🔧 [`_is_toc_details_open`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_md.g.md#-function-_is_toc_details_open)                                             |                                                                                                                 |

### 📄 File `funcs_py.py`

Doc: [funcs_py.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md)

| Function/Class                                                                                                                                    | Description                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 🔧 [`create_uv_new_project`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-create_uv_new_project)                 | Create a new project using uv, initializes it, and sets up necessary files.                 |
| 🔧 [`extract_functions_and_classes`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-extract_functions_and_classes) | Extract all classes and functions from a Python file and formats them into a Markdown list. |
| 🔧 [`generate_md_docs`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-generate_md_docs)                           | Generate documentation for all Python files within a given project folder.                  |
| 🔧 [`generate_md_docs_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-generate_md_docs_content)           | Generate Markdown documentation for a single Python file.                                   |
| 🔧 [`lint_and_fix_python_code`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-lint_and_fix_python_code)           | Lints and fixes the provided Python code using the `ruff` formatter.                        |
| 🔧 [`sort_py_code`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-sort_py_code)                                   | Sorts the Python code in the given file by organizing classes, functions, and statements.   |
| 🔧 [`_fence_for_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-_fence_for_content)                       | Return opening and closing Markdown fences long enough to contain `content`.                |
| 🔧 [`_max_backtick_run`](https://github.com/Harrix/harrix-pylib/blob/main/docs/funcs_py.g.md#-function-_max_backtick_run)                         |                                                                                             |

### 📄 File `img_tools.py`

Doc: [img_tools.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md)

| Function/Class                                                                                                                                       | Description                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 🔧 [`convert_gif_mp4_to_avif`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-convert_gif_mp4_to_avif)               | Convert GIF or MP4 to AVIF using ffmpeg.                              |
| 🔧 [`get_frame_rate`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-get_frame_rate)                                 | Detect frame rate from media file using ffmpeg output.                |
| 🔧 [`is_avif_animated`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-is_avif_animated)                             | Return True if AVIF contains more than one frame.                     |
| 🔧 [`optimize_avif`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-optimize_avif)                                   | Optimize AVIF using ffmpeg or avifdec/avifenc depending on animation. |
| 🔧 [`optimize_image_with_tools`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-optimize_image_with_tools)           | Optimize a raster image using ffmpeg, avifenc, or avifdec.            |
| 🔧 [`process_animated_avif`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-process_animated_avif)                   | Optimize animated AVIF with avifdec and avifenc or ffmpeg.            |
| 🔧 [`process_static_avif`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-process_static_avif)                       | Optimize static AVIF with ffmpeg.                                     |
| 🔧 [`_exe`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_exe)                                                     |                                                                       |
| 🔧 [`_ffmpeg_output`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_ffmpeg_output)                                 |                                                                       |
| 🔧 [`_is_avif_animated_with_avifdec`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_is_avif_animated_with_avifdec) |                                                                       |
| 🔧 [`_reduce_frames`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_reduce_frames)                                 |                                                                       |
| 🔧 [`_resize_frames`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_resize_frames)                                 |                                                                       |
| 🔧 [`_run_checked`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_run_checked)                                     |                                                                       |
| 🔧 [`_scale_vf`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_scale_vf)                                           |                                                                       |
| 🔧 [`_sequence_pattern`](https://github.com/Harrix/harrix-pylib/blob/main/docs/img_tools.g.md#-function-_sequence_pattern)                           |                                                                       |

### 📄 File `markdown_checker.py`

Doc: [markdown_checker.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/markdown_checker.g.md)

| Function/Class                                                                                                                   | Description                                                            |
| -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 🏛️ Class [`MarkdownChecker`](https://github.com/Harrix/harrix-pylib/blob/main/docs/markdown_checker.g.md#️-class-markdownchecker) | Class for checking Markdown files for compliance with specified rules. |

### 📄 File `python_checker.py`

Doc: [python_checker.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/python_checker.g.md)

| Function/Class                                                                                                             | Description                                                          |
| -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 🏛️ Class [`PythonChecker`](https://github.com/Harrix/harrix-pylib/blob/main/docs/python_checker.g.md#️-class-pythonchecker) | Class for checking Python files for compliance with specified rules. |

### 📄 File `code_guard.py`

Doc: [code_guard.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md)

| Function/Class                                                                                                                  | Description                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 🏛️ Class [`CodeBlock`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#️-class-codeblock)                  | Stored fenced code block extracted from Markdown body.                          |
| 🔧 [`extract_code_blocks`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-extract_code_blocks) | Replace fenced code blocks with placeholders and store originals verbatim.      |
| 🔧 [`restore_code_blocks`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-restore_code_blocks) | Restore fenced code blocks from placeholders.                                   |
| 🔧 [`_join_lines`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-_join_lines)                 |                                                                                 |
| 🔧 [`_leading_whitespace`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-_leading_whitespace) |                                                                                 |
| 🔧 [`_placeholder`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-_placeholder)               |                                                                                 |
| 🔧 [`_reindent_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-_reindent_line)           |                                                                                 |
| 🔧 [`_split_lines`](https://github.com/Harrix/harrix-pylib/blob/main/docs/code_guard.g.md#-function-_split_lines)               | Split text into lines without the trailing split artifact from a final newline. |

### 📄 File `escape_format.py`

Doc: [escape_format.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md)

| Function/Class                                                                                                                                         | Description                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| 🔧 [`escape_markdown_text`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-escape_markdown_text)                   | Escape emphasis-like `*` and `_` characters in plain text. |
| 🔧 [`_is_all_caps_macro_underscore`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_is_all_caps_macro_underscore) | Match C-style macros like `_WIN32` and `_DEBUG`.           |
| 🔧 [`_is_alphanumeric`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_is_alphanumeric)                           |                                                            |
| 🔧 [`_is_left_flanking`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_is_left_flanking)                         |                                                            |
| 🔧 [`_is_punctuation`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_is_punctuation)                             |                                                            |
| 🔧 [`_is_right_flanking`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_is_right_flanking)                       |                                                            |
| 🔧 [`_is_whitespace`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_is_whitespace)                               |                                                            |
| 🔧 [`_should_escape_asterisk`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_should_escape_asterisk)             |                                                            |
| 🔧 [`_should_escape_underscore`](https://github.com/Harrix/harrix-pylib/blob/main/docs/escape_format.g.md#-function-_should_escape_underscore)         |                                                            |

### 📄 File `formatter.py`

Doc: [formatter.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/formatter.g.md)

| Function/Class                                                                                                                         | Description                                                             |
| -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 🔧 [`format_markdown_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/formatter.g.md#-function-format_markdown_content) | Format Markdown text with Prettier-like defaults.                       |
| 🔧 [`normalize_line_endings`](https://github.com/Harrix/harrix-pylib/blob/main/docs/formatter.g.md#-function-normalize_line_endings)   | Normalize mixed or corrupted line endings to LF.                        |
| 🔧 [`read_markdown_text`](https://github.com/Harrix/harrix-pylib/blob/main/docs/formatter.g.md#-function-read_markdown_text)           | Read Markdown from disk without universal-newline mangling of `\r\r\n`. |
| 🔧 [`_format_with_options`](https://github.com/Harrix/harrix-pylib/blob/main/docs/formatter.g.md#-function-_format_with_options)       |                                                                         |
| 🔧 [`_normalize_end_of_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/formatter.g.md#-function-_normalize_end_of_line)   |                                                                         |

### 📄 File `front_matter.py`

Doc: [front_matter.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/front_matter.g.md)

| Function/Class                                                                                                                                  | Description                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 🔧 [`collapse_extra_blank_lines`](https://github.com/Harrix/harrix-pylib/blob/main/docs/front_matter.g.md#-function-collapse_extra_blank_lines) | Collapse consecutive blank lines to a single blank line.                   |
| 🔧 [`compact_front_matter`](https://github.com/Harrix/harrix-pylib/blob/main/docs/front_matter.g.md#-function-compact_front_matter)             | Remove blank lines inside YAML front matter while keeping delimiters.      |
| 🔧 [`join_front_matter`](https://github.com/Harrix/harrix-pylib/blob/main/docs/front_matter.g.md#-function-join_front_matter)                   | Join front matter and formatted body.                                      |
| 🔧 [`prepend_markdown_header`](https://github.com/Harrix/harrix-pylib/blob/main/docs/front_matter.g.md#-function-prepend_markdown_header)       | Prepend YAML or Markdown prefix without duplicating existing front matter. |
| 🔧 [`split_front_matter`](https://github.com/Harrix/harrix-pylib/blob/main/docs/front_matter.g.md#-function-split_front_matter)                 | Split YAML front matter from Markdown body.                                |

### 📄 File `list_format.py`

Doc: [list_format.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/list_format.g.md)

| Function/Class                                                                                                                                         | Description                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| 🔧 [`ensure_blank_line_after_lists`](https://github.com/Harrix/harrix-pylib/blob/main/docs/list_format.g.md#-function-ensure_blank_line_after_lists)   | Insert a blank line after a list when the next line starts a new block.  |
| 🔧 [`is_list_continuation`](https://github.com/Harrix/harrix-pylib/blob/main/docs/list_format.g.md#-function-is_list_continuation)                     | Return whether the line continues the previous list item paragraph.      |
| 🔧 [`is_list_item_continuation_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/list_format.g.md#-function-is_list_item_continuation_line) | Return whether an unindented line continues the previous list item text. |
| 🔧 [`is_list_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/list_format.g.md#-function-is_list_line)                                     | Return whether the line is a bullet or ordered list item.                |

### 📄 File `options.py`

Doc: [options.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/options.g.md)

| Function/Class                                                                                                      | Description                  |
| ------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| 🏛️ Class [`FormatOptions`](https://github.com/Harrix/harrix-pylib/blob/main/docs/options.g.md#️-class-formatoptions) | Markdown formatting options. |

### 📄 File `parser.py`

Doc: [parser.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/parser.g.md)

| Function/Class                                                                                                              | Description                                                              |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 🔧 [`get_markdown_parser`](https://github.com/Harrix/harrix-pylib/blob/main/docs/parser.g.md#-function-get_markdown_parser) | Return a configured `markdown-it` parser with GFM, math, and wiki-links. |

### 📄 File `printer.py`

Doc: [printer.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md)

| Function/Class                                                                                                                                   | Description                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| 🔧 [`render_tokens`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-render_tokens)                                 | Render top-level block tokens to Markdown.                               |
| 🔧 [`_find_close`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_find_close)                                     |                                                                          |
| 🔧 [`_format_code_inline`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_format_code_inline)                     |                                                                          |
| 🔧 [`_format_self_referential_link`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_format_self_referential_link) | Return angle-bracket autolink syntax for bare and self-referential URLs. |
| 🔧 [`_format_table_row`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_format_table_row)                         |                                                                          |
| 🔧 [`_format_table_separator`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_format_table_separator)             |                                                                          |
| 🔧 [`_is_spurious_table_row`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_is_spurious_table_row)               |                                                                          |
| 🔧 [`_join_blocks`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_join_blocks)                                   |                                                                          |
| 🔧 [`_link_raw_text`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_link_raw_text)                               | Return raw link label text when it contains only text and soft breaks.   |
| 🔧 [`_list_is_loose`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_list_is_loose)                               |                                                                          |
| 🔧 [`_list_item_is_loose`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_list_item_is_loose)                     |                                                                          |
| 🔧 [`_max_backtick_run`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_max_backtick_run)                         |                                                                          |
| 🔧 [`_readable_link_href`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_readable_link_href)                     | Decode percent-encoded Unicode in URLs for readable Markdown output.     |
| 🔧 [`_render_block`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_block)                                 |                                                                          |
| 🔧 [`_render_blockquote`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_blockquote)                       |                                                                          |
| 🔧 [`_render_fence`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_fence)                                 |                                                                          |
| 🔧 [`_render_heading`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_heading)                             |                                                                          |
| 🔧 [`_render_inline`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_inline)                               |                                                                          |
| 🔧 [`_render_inline_token`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_inline_token)                   |                                                                          |
| 🔧 [`_render_inline_until`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_inline_until)                   |                                                                          |
| 🔧 [`_render_list`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_list)                                   |                                                                          |
| 🔧 [`_render_list_item_lines`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_list_item_lines)             |                                                                          |
| 🔧 [`_render_math_block`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_math_block)                       |                                                                          |
| 🔧 [`_render_paragraph`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_paragraph)                         |                                                                          |
| 🔧 [`_render_table`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_table)                                 |                                                                          |
| 🔧 [`_render_until_close`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_render_until_close)                     |                                                                          |
| 🔧 [`_table_column_widths`](https://github.com/Harrix/harrix-pylib/blob/main/docs/printer.g.md#-function-_table_column_widths)                   |                                                                          |

### 📄 File `table_format.py`

Doc: [table_format.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md)

| Function/Class                                                                                                                                          | Description                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 🔧 [`ensure_blank_line_after_tables`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-ensure_blank_line_after_tables) | Insert a blank line after a GFM table when the next line is not a table row.  |
| 🔧 [`is_table_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-is_table_line)                                   | Return whether the line is a GFM table row.                                   |
| 🔧 [`looks_like_prose_table_row`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-looks_like_prose_table_row)         | Return whether a single table cell looks like a misparsed paragraph.          |
| 🔧 [`parse_table_cells`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-parse_table_cells)                           | Split a table row into cell values.                                           |
| 🔧 [`text_display_width`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-text_display_width)                         | Return the terminal display width of text (emoji and CJK count as 2 columns). |
| 🔧 [`unwrap_spurious_table_rows`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-unwrap_spurious_table_rows)         | Turn ``                                                                       |
| 🔧 [`_is_emoji_base`](https://github.com/Harrix/harrix-pylib/blob/main/docs/table_format.g.md#-function-_is_emoji_base)                                 |                                                                               |

### 📄 File `wiki_plugin.py`

Doc: [wiki_plugin.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/wiki_plugin.g.md)

| Function/Class                                                                                                             | Description                                       |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| 🔧 [`wiki_link_plugin`](https://github.com/Harrix/harrix-pylib/blob/main/docs/wiki_plugin.g.md#-function-wiki_link_plugin) | Register wiki-link parsing before standard links. |

### 📄 File `cleanup.py`

Doc: [cleanup.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/cleanup.g.md)

| Function/Class                                                                                       | Description                                                           |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 🔧 [`cleanup`](https://github.com/Harrix/harrix-pylib/blob/main/docs/cleanup.g.md#-function-cleanup) | Remove metadata elements and deprecated attributes from the SVG tree. |

### 📄 File `hidden.py`

Doc: [hidden.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/hidden.g.md)

| Function/Class                                                                                                    | Description                                                                     |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 🔧 [`remove_hidden`](https://github.com/Harrix/harrix-pylib/blob/main/docs/hidden.g.md#-function-remove_hidden)   | Remove elements that are not rendered. Returns True if any element was removed. |
| 🔧 [`_float`](https://github.com/Harrix/harrix-pylib/blob/main/docs/hidden.g.md#-function-_float)                 |                                                                                 |
| 🔧 [`_is_hidden`](https://github.com/Harrix/harrix-pylib/blob/main/docs/hidden.g.md#-function-_is_hidden)         |                                                                                 |
| 🔧 [`_is_zero_sized`](https://github.com/Harrix/harrix-pylib/blob/main/docs/hidden.g.md#-function-_is_zero_sized) |                                                                                 |

### 📄 File `optimizer.py`

Doc: [optimizer.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/optimizer.g.md)

| Function/Class                                                                                                                   | Description                                                           |
| -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 🔧 [`optimize_svg_content`](https://github.com/Harrix/harrix-pylib/blob/main/docs/optimizer.g.md#-function-optimize_svg_content) | Optimize SVG markup to a compact form similar to SVGO preset-default. |

### 📄 File `paths.py`

Doc: [paths.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md)

| Function/Class                                                                                                                   | Description                                                   |
| -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 🔧 [`format_path_data`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-format_path_data)             | Format path commands into a compact d attribute.              |
| 🔧 [`optimize_path_data`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-optimize_path_data)         | Optimize a path d attribute string.                           |
| 🔧 [`optimize_paths`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-optimize_paths)                 | Optimize path d attributes. Returns True if any path changed. |
| 🔧 [`parse_path_data`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-parse_path_data)               | Parse SVG path data into command tuples.                      |
| 🔧 [`_format_args_spaced`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_format_args_spaced)       |                                                               |
| 🔧 [`_format_number`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_format_number)                 |                                                               |
| 🔧 [`_is_valid_command_list`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_is_valid_command_list) |                                                               |
| 🔧 [`_minimal_path_cleanup`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_minimal_path_cleanup)   |                                                               |
| 🔧 [`_optimize_commands`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_optimize_commands)         |                                                               |
| 🔧 [`_relative_line`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_relative_line)                 |                                                               |
| 🔧 [`_resolve_point`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_resolve_point)                 |                                                               |
| 🔧 [`_trim_number`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_trim_number)                     |                                                               |
| 🔧 [`_update_pos_for_curve`](https://github.com/Harrix/harrix-pylib/blob/main/docs/paths.g.md#-function-_update_pos_for_curve)   |                                                               |

### 📄 File `serialize.py`

Doc: [serialize.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/serialize.g.md)

| Function/Class                                                                                             | Description                                                  |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 🔧 [`serialize`](https://github.com/Harrix/harrix-pylib/blob/main/docs/serialize.g.md#-function-serialize) | Serialize SVG element tree to a minified single-line string. |

### 📄 File `shapes.py`

Doc: [shapes.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md)

| Function/Class                                                                                                          | Description                                                             |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 🔧 [`convert_shapes`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-convert_shapes)       | Convert basic shapes to paths. Returns True if any conversion happened. |
| 🔧 [`_circle_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_circle_to_path)     |                                                                         |
| 🔧 [`_ellipse_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_ellipse_to_path)   |                                                                         |
| 🔧 [`_line_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_line_to_path)         |                                                                         |
| 🔧 [`_num`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_num)                           |                                                                         |
| 🔧 [`_parse_points`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_parse_points)         |                                                                         |
| 🔧 [`_polygon_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_polygon_to_path)   |                                                                         |
| 🔧 [`_polyline_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_polyline_to_path) |                                                                         |
| 🔧 [`_rect_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_rect_to_path)         |                                                                         |
| 🔧 [`_shape_to_path`](https://github.com/Harrix/harrix-pylib/blob/main/docs/shapes.g.md#-function-_shape_to_path)       |                                                                         |

### 📄 File `structure.py`

Doc: [structure.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md)

| Function/Class                                                                                                                                     | Description                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 🔧 [`optimize_structure`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-optimize_structure)                       | Collapse groups and strip empty attributes. Returns True if anything changed. |
| 🔧 [`_clean_number`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_clean_number)                                 |                                                                               |
| 🔧 [`_cleanup_numeric_values`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_cleanup_numeric_values)             |                                                                               |
| 🔧 [`_cleanup_root_attrs`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_cleanup_root_attrs)                     |                                                                               |
| 🔧 [`_collapse_single_child_groups`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_collapse_single_child_groups) |                                                                               |
| 🔧 [`_index_to_short_id`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_index_to_short_id)                       |                                                                               |
| 🔧 [`_is_id_referenced`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_is_id_referenced)                         |                                                                               |
| 🔧 [`_merge_element_attrs`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_merge_element_attrs)                   |                                                                               |
| 🔧 [`_remove_empty_containers`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_remove_empty_containers)           |                                                                               |
| 🔧 [`_shorten_ids`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_shorten_ids)                                   |                                                                               |
| 🔧 [`_strip_default_attrs`](https://github.com/Harrix/harrix-pylib/blob/main/docs/structure.g.md#-function-_strip_default_attrs)                   |                                                                               |

### 📄 File `styles.py`

Doc: [styles.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/styles.g.md)

| Function/Class                                                                                                  | Description                                          |
| --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 🏛️ Class [`StyleSheet`](https://github.com/Harrix/harrix-pylib/blob/main/docs/styles.g.md#️-class-stylesheet)    | Collected CSS class rules from SVG <style> elements. |
| 🔧 [`_format_style`](https://github.com/Harrix/harrix-pylib/blob/main/docs/styles.g.md#-function-_format_style) |                                                      |

### 📄 File `xml_tags.py`

Doc: [xml_tags.g.md](https://github.com/Harrix/harrix-pylib/blob/main/docs/xml_tags.g.md)

| Function/Class                                                                                                      | Description                                           |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 🔧 [`tag_endswith`](https://github.com/Harrix/harrix-pylib/blob/main/docs/xml_tags.g.md#-function-tag_endswith)     | Return whether the tag's local name ends with suffix. |
| 🔧 [`tag_local_name`](https://github.com/Harrix/harrix-pylib/blob/main/docs/xml_tags.g.md#-function-tag_local_name) | Return the local part of an element tag.              |

## 📄 License

This project is licensed under the [MIT License](https://github.com/Harrix/harrix-pylib/blob/main/LICENSE.md).

## 👤 Author

Author: [Anton Sergienko](https://github.com/Harrix).
