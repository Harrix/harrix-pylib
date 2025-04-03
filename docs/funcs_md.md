---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_md.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Function `add_diary_new_diary`](#function-add_diary_new_diary)
- [Function `add_diary_new_dream`](#function-add_diary_new_dream)
- [Function `add_diary_new_note`](#function-add_diary_new_note)
- [Function `add_note`](#function-add_note)
- [Function `append_path_to_local_links_images_line`](#function-append_path_to_local_links_images_line)
- [Function `combine_markdown_files`](#function-combine_markdown_files)
- [Function `combine_markdown_files_recursively`](#function-combine_markdown_files_recursively)
- [Function `download_and_replace_images`](#function-download_and_replace_images)
- [Function `download_and_replace_images_content`](#function-download_and_replace_images_content)
- [Function `format_yaml`](#function-format_yaml)
- [Function `format_yaml_content`](#function-format_yaml_content)
- [Function `generate_author_book`](#function-generate_author_book)
- [Function `generate_image_captions`](#function-generate_image_captions)
- [Function `generate_image_captions_content`](#function-generate_image_captions_content)
- [Function `generate_toc_with_links`](#function-generate_toc_with_links)
- [Function `generate_toc_with_links_content`](#function-generate_toc_with_links_content)
- [Function `get_yaml_content`](#function-get_yaml_content)
- [Function `identify_code_blocks`](#function-identify_code_blocks)
- [Function `identify_code_blocks_line`](#function-identify_code_blocks_line)
- [Function `increase_heading_level_content`](#function-increase_heading_level_content)
- [Function `remove_toc_content`](#function-remove_toc_content)
- [Function `remove_yaml_and_code_content`](#function-remove_yaml_and_code_content)
- [Function `remove_yaml_content`](#function-remove_yaml_content)
- [Function `replace_section`](#function-replace_section)
- [Function `replace_section_content`](#function-replace_section_content)
- [Function `sort_sections`](#function-sort_sections)
- [Function `sort_sections_content`](#function-sort_sections_content)
- [Function `split_toc_content`](#function-split_toc_content)
- [Function `split_yaml_content`](#function-split_yaml_content)

</details>

## Function `add_diary_new_diary`

```python
def add_diary_new_diary(path_diary: str, beginning_of_md: str, is_with_images: bool = False) -> str | Path
```

Creates a new diary entry for the current day and time.

Args:

- `is_with_images` (`bool`): Whether to create folders for images. Defaults to `False`.
- `path_diary` (`str`): The path to the folder for diary notes.
- `beginning_of_md` (`str`): The section of YAML for a Markdown note.

Example of `beginning_of_md`:

```markdown
---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---
```

Returns:

- `str | Path`: The path to the created diary entry file or a string message indicating creation.

Example:

```python
import harrix_pylib as h

yaml_front_matter = '''---
author: Jane Doe
author-email: jane.doe@example.com
lang: en
---
'''

new_entry_path = h.md.add_diary_new_diary("C:/Diary/", yaml_front_matter, is_with_images=True)
print(new_entry_path)
```

<details>
<summary>Code:</summary>

```python
def add_diary_new_diary(path_diary: str, beginning_of_md: str, is_with_images: bool = False) -> str | Path:
    text = f"{beginning_of_md}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    return add_diary_new_note(path_diary, text, is_with_images)
```

</details>

## Function `add_diary_new_dream`

```python
def add_diary_new_dream(path_dream, beginning_of_md, is_with_images: bool = False) -> str | Path
```

Creates a new dream diary entry for the current day and time with placeholders for dream descriptions.

Args:

- `is_with_images` (`bool`): Whether to create folders for images. Defaults to `False`.
- `path_dream` (`str`): The path to the folder for dream notes.
- `beginning_of_md` (`str`): The section of YAML for a Markdown note.

Example of `beginning_of_md`:

```markdown
---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---
```

Returns:

- `str | Path`: The path to the created dream diary entry file or a string message indicating creation.

Example:

```python
import harrix_pylib as h

yaml_front_matter = '''---
author: Jane Doe
author-email: jane.doe@example.com
lang: en
---
'''

new_entry_path = h.md.add_diary_new_dream("C:/Dreams/", yaml_front_matter, is_with_images=True)
print(new_entry_path)
```

<details>
<summary>Code:</summary>

```python
def add_diary_new_dream(path_dream, beginning_of_md, is_with_images: bool = False) -> str | Path:
    text = f"{beginning_of_md}\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    text += "`` — не помню.\n\n" * 15 + "`` — не помню.\n"
    return add_diary_new_note(path_dream, text, is_with_images)
```

</details>

## Function `add_diary_new_note`

```python
def add_diary_new_note(base_path: str | Path, text: str, is_with_images: bool) -> str | Path
```

Adds a new note to the diary or dream diary for the given base path.

Args:

- `base_path` (`str | Path`): The base path where the note should be added.
- `text` (`str`): The content to write in the note.
- `is_with_images` (`bool`): Whether to create a folder for images alongside the note.

Returns:

- `str | Path`: A string message indicating the file was created along with the file path.

Example:

```python
import harrix_pylib as h

text = "# Diary Entry\nThis is a diary test entry without images.\n"
is_with_images = False

result_msg, result_path = h.md.add_diary_new_note("C:/Diary/", text, is_with_images)
# File C:\Diary\2025\01\2025-01-21.md is created
```

<details>
<summary>Code:</summary>

```python
def add_diary_new_note(base_path: str | Path, text: str, is_with_images: bool) -> str | Path:
    current_date = datetime.now()
    year = current_date.strftime("%Y")
    month = current_date.strftime("%m")
    day = current_date.strftime("%Y-%m-%d")

    base_path = Path(base_path)

    year_path = base_path / year
    year_path.mkdir(exist_ok=True)

    month_path = year_path / month
    month_path.mkdir(exist_ok=True)

    return add_note(month_path, day, text, is_with_images)
```

</details>

## Function `add_note`

```python
def add_note(base_path: str | Path, name: str, text: str, is_with_images: bool) -> str | Path
```

Adds a note to the specified base path.

Args:

- `base_path` (`str | Path`): The path where the note will be added.
- `name` (`str`): The name for the note file or folder.
- `text` (`str`): The text content for the note.
- `is_with_images` (`bool`): If true, creates folders for images.

Returns:

- `str | Path`: A tuple containing a message about file creation and the path to the file.

Example:

```python
import harrix_pylib as h


name = "test_note"
text = "# Test Note\nThis is a test note with images."
is_with_images = True
result_msg, result_path = h.md.add_note("C:/Notes/", name, text, is_with_images)
```

<details>
<summary>Code:</summary>

```python
def add_note(base_path: str | Path, name: str, text: str, is_with_images: bool) -> str | Path:
    base_path = Path(base_path)

    if is_with_images:
        (base_path / name).mkdir(exist_ok=True)
        (base_path / name / "img").mkdir(exist_ok=True)
        filename = base_path / name / f"{name}.md"
    else:
        filename = base_path / f"{name}.md"

    with filename.open(mode="w", encoding="utf-8") as file:
        file.write(text)

    return f"File {filename} created.", filename
```

</details>

## Function `append_path_to_local_links_images_line`

```python
def append_path_to_local_links_images_line(markdown_line: str, adding_path: str) -> str
```

Appends a path to local links and images within a Markdown line.

Args:

- `markdown_line` (`str`): The Markdown line containing links or images.
- `adding_path` (`str`): The path to prepend to local links.

Returns:

- `str`: A string with updated paths for local links and images.

Note:

This function processes only links that do not start with `http` or `https`, assuming they are local.

Example:

```python
import harrix_pylib as h
import re

markdown_line = "Here is an ![image](image.jpg) and a [link](folder/link.md)"
adding_path = "path/to/add"
result = h.md.append_path_to_local_links_images_line(markdown_line, adding_path)
print(result)
```

<details>
<summary>Code:</summary>

```python
def append_path_to_local_links_images_line(markdown_line: str, adding_path: str) -> str:

    def replace_path_in_links(match):
        link_text = match.group(1)
        file_path = match.group(2).replace("\\", "/")
        return f"[{link_text}]({adding_path}/{file_path})"

    adding_path = adding_path.replace("\\", "/")
    if adding_path.endswith("/"):
        adding_path = adding_path[:-1]
    return re.sub(r"\[(.*?)\]\(((?!http).*?)\)", replace_path_in_links, markdown_line)
```

</details>

## Function `combine_markdown_files`

```python
def combine_markdown_files(folder_path, recursive = False)
```

Combines multiple markdown files in a folder into a single file with intelligent YAML header merging.

Args:

- `folder_path` (`str` or `Path`): Path to the folder containing markdown files.
- `recursive` (`bool`): Whether to include files from subfolders. Defaults to `False`.

Returns:

- `str`: A message indicating the result of the operation.

Note:

- Files with `.g.md` extension in the target folder will be deleted before processing.
- Files with `published: false` in their YAML headers will be skipped.
- Heading levels in the content will be increased by one level.
- Local links and image paths will be adjusted to maintain proper references.
- The combined file will be named `_foldername.g.md`.

Example:

```python
import harrix_pylib as h

result = h.md.combine_markdown_files("C:/Notes", recursive=True)
print(result)
```

<details>
<summary>Code:</summary>

```python
def combine_markdown_files(folder_path, recursive=False):

    def merge_yaml_values(key, value, combined_dict):
        if key not in combined_dict:
            combined_dict[key] = value
            return

        # If current value and new value are the same, do nothing
        if combined_dict[key] == value:
            return

        # Handling lists
        if isinstance(combined_dict[key], list):
            if isinstance(value, list):
                # Merge two lists, removing duplicates
                for item in value:
                    if item not in combined_dict[key]:
                        combined_dict[key].append(item)
            else:
                # Add new value to the list if it's not already there
                if value not in combined_dict[key]:
                    combined_dict[key].append(value)
        else:
            # Current value is not a list - convert it to a list and add the new value
            current_value = combined_dict[key]
            if isinstance(value, list):
                combined_dict[key] = [current_value]
                for item in value:
                    if item != current_value and item not in combined_dict[key]:
                        combined_dict[key].append(item)
            else:
                if current_value != value:
                    combined_dict[key] = [current_value, value]

    folder_path = Path(folder_path)

    # Delete all files ending with .g.md
    for path in folder_path.glob("*.g.md"):
        if path.is_file():
            path.unlink()

    # Get all .md files based on the recursive flag
    if recursive:
        # For recursive mode, we will structure files by folders
        md_files = []

        # First add files from the current folder
        current_folder_files = [
            f for f in folder_path.glob("*.md") if f.is_file() and f.suffix == ".md" and not f.name.endswith(".g.md")
        ]
        md_files.extend(current_folder_files)

        # Then process subfolders in alphabetical order
        subfolders = sorted([d for d in folder_path.iterdir() if d.is_dir()])
        for subfolder in subfolders:
            subfolder_files = []
            # Recursively collect files from each subfolder
            for file_path in subfolder.rglob("*.md"):
                if file_path.is_file() and file_path.suffix == ".md" and not file_path.name.endswith(".g.md"):
                    subfolder_files.append(file_path)

            # Sort files in the subfolder
            subfolder_files.sort()
            md_files.extend(subfolder_files)
    else:
        # Non-recursive - only get files in the current folder
        md_files = sorted(
            [f for f in folder_path.glob("*.md") if f.is_file() and f.suffix == ".md" and not f.name.endswith(".g.md")]
        )

    # If there are no markdown files in the folder at all, exit
    if len(md_files) < 1:
        return f"Skipped {folder_path}: no markdown files found."

    data_yaml_headers = []
    contents = []

    for md_file in md_files:
        markdown_text = md_file.read_text(encoding="utf-8")
        yaml_md, content_md = split_yaml_content(markdown_text)

        # Check published flag
        if yaml_md:
            data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
            published = data_yaml.get("published") if data_yaml and "published" in data_yaml else True
            if not published:
                continue

        # Delete old TOC
        content_md = remove_yaml_content(remove_toc_content(markdown_text))

        # Parse YAML and collect headers
        if yaml_md:
            data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
            data_yaml_headers.append(data_yaml)
        else:
            data_yaml = {}

        # Increase heading levels
        content_md = increase_heading_level_content(content_md)

        # Fix links in no-code lines
        new_lines = []
        lines = content_md.split("\n")
        for line, is_code_block in identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line)
                continue

            # Check no-code line
            new_parts = []
            for part, is_code in identify_code_blocks_line(line):
                if is_code:
                    new_parts.append(part)
                    continue

                adding_path = "/".join(md_file.parent.parts[len(folder_path.parts) :])
                if adding_path:
                    part_new = append_path_to_local_links_images_line(part, adding_path)
                else:
                    part_new = part
                new_parts.append(part_new)

            line_new = "".join(new_parts)
            new_lines.append(line_new)
        content_md = "\n".join(new_lines)

        contents.append(content_md.strip())

    # Combine YAML headers intelligently
    combined_yaml = {}

    # Special processing for the attribution field
    all_attributions = []

    # Process all YAML headers
    for yaml_header in data_yaml_headers:
        for key, value in yaml_header.items():
            if key == "attribution":
                # Collect all attributions in a separate list
                if isinstance(value, list):
                    all_attributions.extend(value)
                else:
                    all_attributions.append(value)
            else:
                # For all other fields, use standard merging
                merge_yaml_values(key, value, combined_yaml)

    # Add collected attributions to the final YAML
    if all_attributions:
        combined_yaml["attribution"] = all_attributions

    # Fix final YAML
    combined_yaml.pop("related-id", None)
    combined_yaml.pop("date", None)
    combined_yaml.pop("update", None)
    combined_yaml.pop("permalink", None)
    combined_yaml.pop("permalink-source", None)
    if "lang" in combined_yaml and isinstance(combined_yaml["lang"], list):
        combined_yaml["lang"] = "en" if "en" in combined_yaml["lang"] else combined_yaml["lang"][0]
    adding_path = "/".join(md_file.parent.parts[len(folder_path.parts) :])

    # Prepare the final content
    folder_name = folder_path.name
    output_file = folder_path / f"_{folder_name}.g.md"

    # Dump combined YAML
    yaml_md = yaml.safe_dump(combined_yaml, allow_unicode=True, sort_keys=False)
    final_content = ""
    if combined_yaml:
        final_content += f"---\n{yaml_md}---\n\n"

    final_content += f"# {folder_name}\n\n"
    final_content += "\n\n".join(contents)

    final_content = generate_toc_with_links_content(final_content)
    final_content = generate_image_captions_content(final_content)

    # Write to the output file
    output_file.write_text(final_content, encoding="utf-8")

    return f"✅ File {output_file} is created."
```

</details>

## Function `combine_markdown_files_recursively`

```python
def combine_markdown_files_recursively(folder_path)
```

Recursively processes a folder structure and combines markdown files in each folder that meets specific criteria.

Args:

- `folder_path` (`str` or `Path`): Path to the root folder to process recursively.

Returns:

- `str`: A multi-line string with results of all combine operations.

Note:

- All `.g.md` files in the entire folder structure will be deleted before processing.
- Hidden folders (starting with `.`) will be skipped.
- Files will be combined in a folder if either:
  1. The folder directly contains at least 2 markdown files, or
  2. The folder and its subfolders together contain at least 2 markdown files.

Example:

```python
import harrix_pylib as h

result = h.md.combine_markdown_files_recursively("C:/Notes")
print(result)
```

<details>
<summary>Code:</summary>

```python
def combine_markdown_files_recursively(folder_path):
    result_lines = []
    folder_path = Path(folder_path)

    # Remove all existing .g.md files
    for file in filter(
        lambda path: not any((part for part in path.parts if part.startswith("."))),
        Path(folder_path).rglob("*.g.md"),
    ):
        if file.is_file():
            file.unlink()

    # Collect all folders, including the root folder
    all_folders = [folder_path]  # Start with the root folder

    # Add all subfolders
    for subfolder in filter(
        lambda path: not any((part for part in path.parts if part.startswith("."))),
        Path(folder_path).rglob("*"),
    ):
        if subfolder.is_dir():
            all_folders.append(subfolder)

    # Process each folder
    for folder in all_folders:
        # Get all .md files in this folder (non-recursively)
        md_files_in_folder = [f for f in folder.glob("*.md") if f.is_file() and not f.name.endswith(".g.md")]

        # Get all .md files in this folder and its subfolders (recursively)
        md_files_recursive = [f for f in folder.rglob("*.md") if f.is_file() and not f.name.endswith(".g.md")]

        # Check if there are markdown files directly in subfolders
        subfolders = [f for f in folder.iterdir() if f.is_dir()]
        md_files_in_subfolders = []
        for subfolder in subfolders:
            md_files_in_subfolders.extend(
                [f for f in subfolder.rglob("*.md") if f.is_file() and not f.name.endswith(".g.md")]
            )

        # Create a combined file if:
        # 1. The folder directly contains at least 2 .md files
        # 2. OR the folder and its subfolders contain at least 2 .md files
        # (including cases where all files are in subfolders)
        if len(md_files_in_folder) >= 2 or (
            len(md_files_recursive) >= 2 and len(md_files_recursive) > len(md_files_in_folder)
        ):
            try:
                result_lines.append(combine_markdown_files(folder, recursive=True))
            except Exception as e:
                result_lines.append(f"❌ Error processing {folder}: {e}")

    return "\n".join(result_lines)
```

</details>

## Function `download_and_replace_images`

```python
def download_and_replace_images(filename: Path | str) -> str
```

Downloads remote images in Markdown text and replaces their URLs with local paths.

Args:

- `filename` (`Path` | `str`): The path to the Markdown file. Can be either a `Path` object or a string.

Returns:

- `str`: A string containing the status of the operation or if the file was unchanged.

For example, here is the Markdown text before:

```markdown
![Alt text](https://example.com/image.png)
```

For example, here is the Markdown text after:

```markdown
![Alt text](img/image.png)
```

Example:

```python
import harrix_pylib as h

result = h.md.download_and_replace_images("C:/Notes/note.md")
print(result)
```

<details>
<summary>Code:</summary>

```python
def download_and_replace_images(filename: Path | str) -> str:
    filename = Path(filename)
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    document_new = download_and_replace_images_content(document, filename.parent)

    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>

## Function `download_and_replace_images_content`

```python
def download_and_replace_images_content(markdown_text: str, path_md: Path | str, image_folder: str = "img") -> str
```

Downloads remote images in Markdown text and replaces their URLs with local paths.

Args:

- `markdown_text` (`str`): The markdown text containing image links.
- `path_md` (`Path | str`): The path to the markdown file or its directory.
- `image_folder` (`str`, Defaults to "img"): The folder where images will be stored locally.

Returns:

- `str`: The updated markdown text with remote image URLs replaced by local relative paths.

For example, here is the Markdown text before:

```markdown
![Alt text](https://example.com/image.png)
```

For example, here is the Markdown text after:

```markdown
![Alt text](img/image.png)
```

Example:

```python
import harrix_pylib as h
from pathlib import Path

md_text = "![Example](http://example.com/image.png)"
md_path = Path("C:/Notes/Note")
updated_md_text = h.md.download_and_replace_images_content(md_text, md_path)
print(updated_md_text)
```

<details>
<summary>Code:</summary>

```python
def download_and_replace_images_content(markdown_text: str, path_md: Path | str, image_folder: str = "img") -> str:

    def download_and_replace_image_line(markdown_line, path_md, image_folder="img"):
        # Regular expression to match markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line doesn't contain a remote image, return the line unchanged.
        if not match:
            return markdown_line

        remote_url = match.group(2)

        # Create the img directory inside path_md if it doesn't exist.
        base_path = Path(path_md)
        image_folder_full = base_path / image_folder
        image_folder_full.mkdir(parents=True, exist_ok=True)

        # Parse the URL to retrieve the file name.
        parsed_url = urlparse(remote_url)
        original_file_name = Path(parsed_url.path).name
        if not original_file_name:
            original_file_name = "image"

        # Create a candidate file path and add a suffix if a file in the destination already exists.
        base_name = Path(original_file_name).stem
        extension = Path(original_file_name).suffix
        candidate_file = image_folder_full / original_file_name
        counter = 2
        while candidate_file.exists():
            candidate_file = image_folder_full / f"{base_name}__{counter:02d}{extension}"
            counter += 1

        if "." not in candidate_file.name:
            candidate_file = image_folder_full / f"{candidate_file.name}.png"

        # Attempt to download the image.
        try:
            response = requests.get(remote_url)
            if response.status_code != 200:
                return markdown_line  # If download failed, return the original line.
            # Save the image content to the candidate file.
            with candidate_file.open("wb") as file:
                file.write(response.content)
        except Exception:
            # In case of any exception during downloading, return the original line.
            return markdown_line

        # Replace the remote URL with the local relative path (img/candidate_file.name)
        new_line = markdown_line.replace(remote_url, f"{image_folder}/{candidate_file.name}")
        return new_line

    yaml_md, content_md = split_yaml_content(markdown_text)

    new_lines = []
    lines = content_md.split("\n")
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line)
            continue

        line = download_and_replace_image_line(line, path_md, image_folder)
        new_lines.append(line)
    content_md = "\n".join(new_lines)

    return yaml_md + "\n\n" + content_md
```

</details>

## Function `format_yaml`

```python
def format_yaml(filename: Path | str) -> str
```

Formats YAML content in a file, ensuring proper indentation and structure.

Args:

- `filename` (`Path | str`): The path to the file containing YAML content.

Returns:

- `str`: A message indicating whether the file was changed or not.

Note:

- The function will overwrite the file if changes are made to the YAML formatting.
- It uses a custom YAML dumper (`IndentDumper`) to adjust indentation.

Example:

```python
import harrix_pylib as h
from pathlib import Path

path = Path('example.md')
print(h.md.format_yaml(path))
```

<details>
<summary>Code:</summary>

```python
def format_yaml(filename: Path | str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    document_new = format_yaml_content(document)

    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>

## Function `format_yaml_content`

```python
def format_yaml_content(markdown_text: str) -> str
```

Formats the YAML front matter within the given markdown text.

Args:

- `markdown_text` (`str`): The markdown text containing YAML front matter.

Returns:

- `str`: The formatted YAML content followed by the markdown content.

Note:

- It uses a custom YAML dumper (`IndentDumper`) to adjust indentation.

Example:

```python
import harrix_pylib as h
from pathlib import Path

text = Path('example.md').read_text(encoding="utf8")
print(h.md.format_yaml(text))
```

<details>
<summary>Code:</summary>

```python
def format_yaml_content(markdown_text: str) -> str:
    yaml_md, content_md = split_yaml_content(markdown_text)

    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))

    class IndentDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(IndentDumper, self).increase_indent(flow, False)

    yaml_md = (
        yaml.dump(
            data_yaml,
            Dumper=IndentDumper,
            sort_keys=False,
            allow_unicode=True,
            explicit_start=True,
            default_flow_style=False,
        )
        + "---"
    )

    return yaml_md + "\n\n" + content_md
```

</details>

## Function `generate_author_book`

```python
def generate_author_book(filename: Path | str) -> str
```

Adds the author and the title of the book to the quotes and formats them as Markdown quotes.

Args:

- `filename` (`Path` | `str`): The filename of the Markdown file.

Returns:

- `str`: A string indicating whether changes were made to the file or not.

Example:

Given a file like `C:/test/Name_Surname/Title_of_book.md` with content:

```markdown
# Title of book

Line 1.

Line 2.

---

Line 3.

Line 4.

-- Modified title of book
```

After processing:

```markdown
# Title of book

> Line 1.
>
> Line 2.
>
> -- _Name Surname, Title of book_

---

> Line 3.
>
> Line 4.
>
> -- _Name Surname, Modified title of book_
```

Note:

- If the file does not exist or is not a Markdown file, the function will return `None`.
- If the file has been modified, it returns a message indicating the changes; otherwise,
  it indicates no changes were made.

Example:

```python
import harrix_pylib as h
from pathlib import Path

filename = Path("C:/test/Name_Surname/Title_of_book.md")

result = h.md.generate_author_book(filename)
print(result)
```

<details>
<summary>Code:</summary>

```python
def generate_author_book(filename: Path | str) -> str:
    lines_list = []
    file = Path(filename)
    if not file.is_file():
        return
    if file.suffix.lower() != ".md":
        return
    markdown_text = file.read_text(encoding="utf8")

    yaml_md, content_md = split_yaml_content(markdown_text)

    lines = content_md.splitlines()

    author = file.parts[-2].replace("-", " ")
    title = lines[0].replace("# ", "")

    lines = lines[1:] if lines and lines[0].startswith("# ") else lines
    lines = lines[:-1] if lines[-1].strip() == "---" else lines

    note = f"{yaml_md}\n\n# {title}\n\n"
    quotes = list(map(str.strip, filter(None, "\n".join(lines).split("\n---\n"))))

    quotes_fix = []
    for quote in quotes:
        lines_quote = quote.splitlines()
        if lines_quote[-1].startswith("> -- _"):
            quotes_fix.append(quote)  # The quote has already been processed
            continue
        if lines_quote[-1].startswith("-- "):
            title = lines_quote[-1][3:]
            del lines_quote[-2:]
        quote_fix = "\n".join([f"> {line}".rstrip() for line in lines_quote])
        quotes_fix.append(f"{quote_fix}\n>\n> -- _{author}, {title}_")
    note += "\n\n---\n\n".join(quotes_fix) + "\n"
    if markdown_text != note:
        file.write_text(note, encoding="utf8")
        lines_list.append(f"Fix {filename}")
    else:
        lines_list.append(f"No changes in {filename}")
    return "\n".join(lines_list)
```

</details>

## Function `generate_image_captions`

```python
def generate_image_captions(filename: Path | str) -> str
```

Processes a markdown file to add captions to images based on their alt text.

This function reads a markdown file, processes its content to:

- Recognize images by their markdown syntax.
- Add automatic captions with sequential numbering, localized for Russian or English.
- Skip image captions that already exist in italic format.
- Ensure proper handling within and outside of code blocks.

Args:

- `filename` (`Path | str`): The path to the markdown file to be processed.

Returns:

- `str`: A status message indicating whether the file was modified or not.

Note:

- The function modifies the file in place if changes are made.
- The first argument of the function can be either a `Path` object or a string representing the file path.

Example:

```python
import harrix_pylib as h

h.md.generate_image_captions("C:/Notes/note.md")
```

Before processing:

````markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
lang: en
---

# Installing VSCode

## Section

Example text.

![Alt text](img/image1.png)

Example text.

```markdown
Example text.

![Alt text](img/image1.png)

Example text.

## About
```

## About

Another text.

![Alt text 2](img/image2.png)

_Figure 22: Alt ds sdsd text_

Another text.

![Alt text](img/image3.png)
````

After processing:

````markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
lang: en
---

# Installing VSCode

## Section

Example text.

![Alt text](img/image1.png)

_Figure 1: Alt text_

Example text.

```markdown
Example text.

![Alt text](img/image1.png)

Example text.

## About
```

## About

Another text.

![Alt text 2](img/image2.png)

_Figure 2: Alt text 2_

Another text.

![Alt text](img/image3.png)

_Figure 3: Alt text_
````

<details>
<summary>Code:</summary>

```python
def generate_image_captions(filename: Path | str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    document_new = generate_image_captions_content(document)
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>

## Function `generate_image_captions_content`

```python
def generate_image_captions_content(markdown_text: str) -> str
```

Generates image captions in the provided markdown text.

This function reads a markdown file, processes its content to:

- Recognize images by their markdown syntax.
- Add automatic captions with sequential numbering, localized for Russian or English.
- Skip image captions that already exist in italic format.
- Ensure proper handling within and outside of code blocks.

Args:

- `markdown_text` (`str`): The markdown text to process.

Returns:

- `str`: The markdown text with image captions added.

Example:

```python
import harrix_pylib as h

text = Path('example.md').read_text(encoding="utf8")
print(h.md.generate_image_captions(text))
```

Before processing:

````markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
lang: en
---

# Installing VSCode

## Section

Example text.

![Alt text](img/image1.png)

Example text.

```markdown
Example text.

![Alt text](img/image1.png)

Example text.

## About
```

## About

Another text.

![Alt text 2](img/image2.png)

_Figure 22: Alt ds sdsd text_

Another text.

![Alt text](img/image3.png)
````

After processing:

````markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
lang: en
---

# Installing VSCode

## Section

Example text.

![Alt text](img/image1.png)

_Figure 1: Alt text_

Example text.

```markdown
Example text.

![Alt text](img/image1.png)

Example text.

## About
```

## About

Another text.

![Alt text 2](img/image2.png)

_Figure 2: Alt text 2_

Another text.

![Alt text](img/image3.png)

_Figure 3: Alt text_
````

<details>
<summary>Code:</summary>

```python
def generate_image_captions_content(markdown_text: str) -> str:
    yaml_md, content_md = split_yaml_content(markdown_text)

    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
    lang = data_yaml.get("lang") if data_yaml and "lang" in data_yaml else "en"

    # Remove captions
    is_caption = False
    new_lines = []
    lines = content_md.split("\n")
    for i, (line, is_code_block) in enumerate(identify_code_blocks(lines)):
        if is_code_block:
            new_lines.append(line)
            continue
        if is_caption:
            is_caption = False
            if line.strip() == "":
                continue
        if re.match(r"^_.*_$", line):
            if i > 0 and lines[i - 1].strip() == "":
                if i > 1 and re.match(r"^\!\[(.*?)\]\((.*?)\.(.*?)\)$", lines[i - 2].strip()):
                    is_caption = True
                    continue
        new_lines.append(line)
    content_md = "\n".join(new_lines)

    # Add captions
    image_count = 0
    new_lines = []
    lines = content_md.split("\n")
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line)
            continue
        match = re.match(r"^\!\[(.*?)\]\((.*?)\.(.*?)\)$", line)
        lst_forbidden = ["![Featured image](featured-image", "img.shields.io", "<!-- no-caption -->"]
        if match and not any(forbidden_word in line for forbidden_word in lst_forbidden):
            image_count += 1
            alt_text = match.group(1)
            if not alt_text:
                alt_text = match.group(2).split("/")[-1].replace("_", " ").replace("-", " ").title()
                line = line.replace("![](", f"![{alt_text}](", 1)
            new_lines.append(line)
            caption = f"_Рисунок {image_count} — {alt_text}_" if lang == "ru" else f"_Figure {image_count}: {alt_text}_"
            new_lines.append("\n" + caption)
        else:
            new_lines.append(line)
    content_md = "\n".join(new_lines)

    return yaml_md + "\n\n" + content_md
```

</details>

## Function `generate_toc_with_links`

```python
def generate_toc_with_links(filename: Path | str) -> str
```

Generates a Table of Contents (TOC) with clickable links for a given Markdown file and inserts or refreshes
the TOC in the document.

This function reads a Markdown file, processes its content to create or update a TOC, and writes
back the changes if any were made.

Args:

- `filename` (`Path` | `str`): The path to the Markdown file. Can be either a `Path` object or a string.

Returns:

- `str`: A string containing the status of the TOC operation, including whether the TOC was refreshed or
  if the file was unchanged.

Note:

- The function handles YAML frontmatter by preserving it and only modifying the content below the YAML if present.
- If the TOC already exists in the document, it will be replaced with the new TOC.
- Headers in the document are used to generate TOC entries, with appropriate indentation based on header level.

Example:

```python
import harrix_pylib as h

result = h.md.generate_toc_with_links_content("C:/Notes/note.md")
print(result)
```

<details>
<summary>Code:</summary>

```python
def generate_toc_with_links(filename: Path | str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    document_new = generate_toc_with_links_content(document)
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ TOC is added or refreshed in {filename}."
    return "File is not changed."
```

</details>

## Function `generate_toc_with_links_content`

```python
def generate_toc_with_links_content(markdown_text: str) -> str
```

Generates a Table of Contents (TOC) with links for the provided markdown content.

Args:

- `markdown_text` (`str`): The markdown text from which to generate the TOC.

Returns:

- `str`: The markdown content with the generated TOC inserted.

Note:

- The function handles YAML frontmatter by preserving it and only modifying the content below the YAML if present.
- If the TOC already exists in the document, it will be replaced with the new TOC.
- Headers in the document are used to generate TOC entries, with appropriate indentation based on header level.

Example:

```python
import harrix_pylib as h
from pathlib import Path

text = Path("C:/Notes/note.md").read_text(encoding="utf8")
print(h.md.generate_toc_with_links_content(text))
```

<details>
<summary>Code:</summary>

```python
def generate_toc_with_links_content(markdown_text: str) -> str:

    def generate_id(text: str, existing_ids: set) -> str:
        # Convert text to lowercase
        text = text.lower()

        # Remove all non-word characters (e.g., punctuation, HTML)
        text = text.replace("-", " ")
        text = re.sub(r"[^\w\s]", "", text)

        # Replace spaces with hyphens
        text = text.replace(" ", "-")

        # Ensure uniqueness by appending a number if necessary
        original_text = text
        counter = 1
        while text in existing_ids:
            text = f"{original_text}-{counter}"
            counter += 1

        # Add the new unique ID to the set
        existing_ids.add(text)

        return text

    yaml_md, _ = split_yaml_content(markdown_text)
    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
    lang = data_yaml.get("lang") if data_yaml and "lang" in data_yaml else "en"

    # Generate TOC
    existing_ids = set()
    lines = remove_yaml_and_code_content(markdown_text).splitlines()
    toc_lines = []
    for line in lines:
        if line.startswith("##"):
            if (lang == "ru" and line.strip() == "## Содержание") or (lang != "ru" and line.strip() == "## Contents"):
                continue
            # Determine the header level
            level = len(re.match(r"#+", line).group())
            # Extract the header text
            title = line[level:].strip()
            title = title.replace("<!-- top-section -->", "")
            text_link = generate_id(title, existing_ids)
            link = f"#{text_link}"
            title_text = title.strip()
            # Form the table of contents entry
            toc_lines.append(f"{'  ' * (level - 2)}- [{title_text}]({link})")
    toc = "\n".join(toc_lines)
    if lang == "ru":
        toc = f"<details>\n<summary>📖 Содержание</summary>\n\n## Содержание\n\n{toc}\n\n</details>"
    else:
        toc = f"<details>\n<summary>📖 Contents</summary>\n\n## Contents\n\n{toc}\n\n</details>"

    # Delete old TOC and its header
    content_without_yaml = remove_yaml_content(remove_toc_content(markdown_text))

    # Paste TOC
    is_stop_searching_place_toc = False
    is_first_paragraph = False
    new_lines = []
    lines = content_without_yaml.splitlines()

    for line, is_code_block in identify_code_blocks(lines):
        new_lines.append(line)
        if is_code_block:
            continue
        if line.startswith("##"):
            if not is_stop_searching_place_toc and len(toc_lines) > 1:
                new_lines.insert(len(new_lines) - 1, toc + "\n")
            is_stop_searching_place_toc = True
        if is_stop_searching_place_toc or line.startswith("# ") or line.startswith("![") or not line.strip():
            continue
        if line and not is_first_paragraph and len(toc_lines) > 1:
            new_lines.append("\n" + toc)
            is_first_paragraph = True
            is_stop_searching_place_toc = True
    content_without_yaml = "\n".join(new_lines)
    if content_without_yaml[-1] != "\n":
        content_without_yaml += "\n"

    return yaml_md + "\n\n" + content_without_yaml
```

</details>

## Function `get_yaml_content`

```python
def get_yaml_content(markdown_text: str) -> str
```

Function gets YAML from text of the Markdown file.

Markdown before processing:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode
```

Text after processing:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---
```

Args:

- `markdown_text` (str): Text of the Markdown file.

Returns:

- `str`: YAML from the Markdown file.

Examples:

```python
import harrix-pylib as h

yaml_content = h.md.get_yaml_content("---\ncategories: [it]\n---\n\nText")
print(yaml_content)  # Text
```

```python
from pathlib import Path
import harrix-pylib as h

md = Path("article.md").read_text(encoding="utf8")
yaml_content = h.md.get_yaml_content(md)
print(yaml_content)
```

<details>
<summary>Code:</summary>

```python
def get_yaml_content(markdown_text: str) -> str:
    find = re.search(r"^---(.|\n)*?---\n", markdown_text.lstrip(), re.DOTALL)
    if find:
        return find.group().rstrip()
    return ""
```

</details>

## Function `identify_code_blocks`

```python
def identify_code_blocks(lines: List[str]) -> Iterator[tuple[str, bool]]
```

Processes a list of text lines to identify code blocks and yield each line with a boolean flag.

Args:

- `lines` (`list[str]`): A list of strings where each string is a line of text to be processed.

Returns:

- `Iterator[tuple[str, bool]]`: An iterator yielding tuples. Each tuple contains:
  - The original line of text (`str`).
  - A boolean flag (`bool`) indicating if the line is within a code block (`True`) or not (`False`).

Note:

- This function identifies code blocks by looking for lines that start with three or more backticks (`` ` ``).
- Code blocks can be nested, and this function will toggle the `code_block_delimiter` on matching delimiters.

Example:

```python
from pathlib import Path

import harrix_pylib as h

md = Path("C:/Notes/note.md").read_text(encoding="utf8")
_, content = h.md.split_yaml_content(md)
count_lines_content = 0
count_lines_code = 0
for _, state in h.md.identify_code_blocks(content.splitlines()):
    if state:
        count_lines_code += 1
    else:
        count_lines_content += 1
```

<details>
<summary>Code:</summary>

```python
def identify_code_blocks(lines: List[str]) -> Iterator[tuple[str, bool]]:
    code_block_delimiter = None
    for line in lines:
        match = re.match(r"^(`{3,})(.*)", line)
        if match:
            delimiter = match.group(1)
            if code_block_delimiter is None:
                code_block_delimiter = delimiter
            elif code_block_delimiter == delimiter:
                code_block_delimiter = None
            yield line, True
            continue
        if code_block_delimiter:
            yield line, True
        else:
            yield line, False
```

</details>

## Function `identify_code_blocks_line`

```python
def identify_code_blocks_line(markdown_line: str) -> Iterator[tuple[str, bool]]
```

Parses a single line of Markdown to identify inline code blocks.

This function scans through a markdown line, identifying sequences of backticks (`) to determine where code
blocks start and end.

Args:

- `markdown_line` (`str`): The input Markdown line to analyze.

Returns:

- `Iterator[tuple[str, bool]]`: An iterator yielding tuples where the first element is a segment of the line,
  and the second is a boolean indicating whether this segment is part of an inline code block.

Example:

```python
import harrix_pylib as h

line = "Here is some `code` and more `code`."
for segment, in_code in h.md.identify_code_blocks_line(line):
    print(f"{'Code' if in_code else 'Text'}: {segment}")
```

<details>
<summary>Code:</summary>

```python
def identify_code_blocks_line(markdown_line: str) -> Iterator[tuple[str, bool]]:
    current_text = ""
    in_code = False
    backtick_count = 0

    i = 0
    while i < len(markdown_line):
        if markdown_line[i] == "`":
            # Counting the number of consecutive backquotes
            count = 1
            while i + 1 < len(markdown_line) and markdown_line[i + 1] == "`":
                count += 1
                i += 1

            if not in_code:
                # Start of code block
                if current_text:
                    yield current_text, False
                    current_text = ""
                backtick_count = count
                current_text = "`" * count
                in_code = True
            elif count == backtick_count:
                # End of code block
                current_text += "`" * count
                yield current_text, True
                current_text = ""
                in_code = False
            else:
                # Backquotes inside the code
                current_text += "`" * count
        else:
            current_text += markdown_line[i]

        i += 1

    if current_text:
        yield current_text, False
```

</details>

## Function `increase_heading_level_content`

```python
def increase_heading_level_content(markdown_text: str) -> str
```

Increases the heading level of Markdown content.

This function processes a Markdown text and increases the level of all headings
(lines starting with '#') outside of code blocks by prepending an additional '#'.

Args:

- `markdown_text` (`str`): The Markdown text to process.

Returns:

- `str`: The updated Markdown text with increased heading levels. The YAML header,
  if present, is preserved and included at the beginning of the output.

Note:

- Code blocks are detected using the helper function `identify_code_blocks` and are not modified.

Example:

```python
from pathlib import Path

import harrix_pylib as h

md = "# Title\n\nText## Subtitle\n\nText"
print(h.md.increase_heading_level_content(md))
```

<details>
<summary>Code:</summary>

```python
def increase_heading_level_content(markdown_text: str) -> str:
    new_lines = []
    lines = markdown_text.split("\n")
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line)
            continue
        new_lines.append("#" + line if line.startswith("#") else line)
    return "\n".join(new_lines)
```

</details>

## Function `remove_toc_content`

```python
def remove_toc_content(markdown_text: str) -> str
```

Removes the table of contents (TOC) section from a Markdown document.

The function identifies the TOC based on the document language (from YAML frontmatter)
and removes the entire TOC section, including the details/summary tags and all TOC links.
It preserves code blocks and other content in the document.

Args:

- `markdown_text` (`str`): The Markdown text containing a TOC to be removed.

Returns:

- `str`: The Markdown text with the TOC section removed.

Note:

- The function detects the document language from the YAML frontmatter's `lang` field.
- TOC is identified as content between <details> and </details> tags containing "📖 Contents" or "📖 Содержание".
- The function preserves the YAML frontmatter in the output.

Example:

```python
import harrix_pylib as h
from pathlib import Path

text = Path("C:/Notes/note.md").read_text(encoding="utf8")
print(h.md.remove_toc_content(text))
```

<details>
<summary>Code:</summary>

```python
def remove_toc_content(markdown_text: str) -> str:
    yaml_md, _ = split_yaml_content(markdown_text)

    # Delete TOC section enclosed in <details> tags
    new_lines = []
    lines = remove_yaml_content(markdown_text).splitlines()
    in_toc_section = False
    toc_section_found = False

    for i, (line, is_code_block) in enumerate(identify_code_blocks(lines)):
        if is_code_block:
            new_lines.append(line)
            continue

        # Check for TOC opening tag
        if not toc_section_found and line.strip() == "<details>":
            next_line_idx = i + 1
            if (
                next_line_idx < len(lines)
                and "<summary>" in lines[next_line_idx]
                and ("📖 Contents" in lines[next_line_idx] or "📖 Содержание" in lines[next_line_idx])
            ):
                in_toc_section = True
                toc_section_found = True
                continue

        # Check for TOC closing tag
        if in_toc_section and line.strip() == "</details>":
            in_toc_section = False
            continue

        if not in_toc_section:
            # Only add the line if it's not an empty line after the TOC section
            if not toc_section_found or len(new_lines) == 0 or new_lines[-1].strip() or line.strip():
                new_lines.append(line)

    content_without_yaml = "\n".join(new_lines)
    if content_without_yaml and content_without_yaml[-1] != "\n":
        content_without_yaml += "\n"

    return yaml_md + "\n\n" + content_without_yaml
```

</details>

## Function `remove_yaml_and_code_content`

```python
def remove_yaml_and_code_content(markdown_text: str) -> str
```

Removes YAML front matter and code blocks, and returns the remaining content.

Args:

- `markdown_text` (str): Text of the Markdown file.

Returns:

- `str`: A string containing the markdown content with YAML front matter and code blocks removed.

Examples:

```python
import harrix-pylib as h

md_clean = h.md.remove_yaml_and_code_content("---\ncategories: [it]\n---\n\nText")
print(md_clean)  # Text
```

```python
from pathlib import Path
import harrix-pylib as h

md = Path("article.md").read_text(encoding="utf8")
md_clean = h.md.remove_yaml_and_code_content(md)
print(md_clean)
```

<details>
<summary>Code:</summary>

```python
def remove_yaml_and_code_content(markdown_text: str) -> str:
    _, content_md = split_yaml_content(markdown_text)

    new_lines = []
    lines = content_md.split("\n")
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            continue
        new_lines.append(line)

    return "\n".join(new_lines)
```

</details>

## Function `remove_yaml_content`

```python
def remove_yaml_content(markdown_text: str) -> str
```

Function removes YAML from text of the Markdown file.

Markdown before processing:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode
```

Markdown after processing:

```markdown
# Installing VSCode
```

Args:

- `markdown_text` (str): Text of the Markdown file.

Returns:

- `str`: Text of the Markdown file without YAML.

Examples:

```python
import harrix-pylib as h

md_clean = h.md.remove_yaml_content("---\ncategories: [it]\n---\n\nText")
print(md_clean)  # Text
```

```python
from pathlib import Path
import harrix-pylib as h

md = Path("article.md").read_text(encoding="utf8")
md_clean = h.md.remove_yaml_content(md)
print(md_clean)
```

<details>
<summary>Code:</summary>

```python
def remove_yaml_content(markdown_text: str) -> str:
    return re.sub(r"^---(.|\n)*?---\n", "", markdown_text.lstrip()).lstrip()
```

</details>

## Function `replace_section`

```python
def replace_section(filename: Path | str, replace_content, title_section: str = "## List of commands") -> str
```

Replaces a section in a file defined by `title_section` with the provided `replace_content`.

This function searches for a section in a text file starting with `title_section` and
ending at the next line starting with a '#'. It then replaces the content of that section
with `replace_content`.

Args:

- `filename` (`Path | str`): The path to the file where the section needs to be replaced.
- `replace_content` (`str`): The content to replace the section with.
- `title_section` (`str`, Defaults to `"## List of commands"`): The title of the section to be replaced.

Returns:

- `str`: A message indicating that the section has been replaced.

Notes:

- If `start_index` or `end_index` is not found, the file remains unchanged.
- The function assumes that the file uses UTF-8 encoding for reading and writing.
- If no section matches the `title_section`, or if the section spans till the end of the file,
  only the content up to `end_index` (or the end of the file) will be replaced.

Example:

```python
import harrix_pylib as h

new_content = "New list of commands:\n\n- new command1\n- new command2"
result_message = h.md.replace_section("C:/Notes/note.md", new_content, "## List of commands")
```

<details>
<summary>Code:</summary>

```python
def replace_section(filename: Path | str, replace_content, title_section: str = "## List of commands") -> str:
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    document_new = replace_section_content(document, replace_content, title_section)
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} is changed."
    return "File is not changed."
```

</details>

## Function `replace_section_content`

```python
def replace_section_content(markdown_text: str, replace_content, title_section: str = "## List of commands") -> str
```

Replaces a section in the markdown text defined by `title_section` with the provided `replace_content`.

This function searches for a section in the markdown text starting with `title_section` and
ending at the next line starting with a '#'. It then replaces the content of that section
with `replace_content`.

Args:

- `markdown_text` (`str`): The markdown text.
- `replace_content` (`str`): The content to replace the section with.
- `title_section` (`str`, Defaults to `"## List of commands"`): The title of the section to be replaced.

Returns:

- `str`: The markdown content with the replaced section.

Notes:

- If `start_index` or `end_index` is not found, the text remains unchanged.
- If no section matches the `title_section`, or if the section spans till the end of the text,
  only the content up to `end_index` (or the end of the file) will be replaced.

Example:

```python
import harrix_pylib as h
from pathlib import Path

new_content = "New list of commands:\n\n- new command1\n- new command2"
text = Path('C:/Notes/note.md').read_text(encoding="utf8")
print(h.md.replace_section_content(text, new_content, "## List of commands"))
```

<details>
<summary>Code:</summary>

```python
def replace_section_content(markdown_text: str, replace_content, title_section: str = "## List of commands") -> str:
    ends_with_newline = markdown_text.endswith("\n")
    lines = markdown_text.splitlines()

    # Find the start index of the section to replace
    start_index = None
    for i, line in enumerate(lines):
        if line.strip() == title_section.strip():
            start_index = i
            break

    if start_index is None:
        raise ValueError(f"Section '{title_section}' not found in the file.")

    # Determine the heading level of the section to replace
    heading_match = re.match(r"^(#+)", title_section.strip())
    if not heading_match:
        raise ValueError(f"The section title '{title_section}' is not a valid Markdown heading.")
    title_level = len(heading_match.group(1))  # Number of '#' characters

    # Find the end index of the section to replace
    end_index = len(lines)  # Default to the end of the file
    for i in range(start_index + 1, len(lines)):
        line = lines[i].strip()
        # Check if the line is a heading of the same or higher level
        line_heading_match = re.match(r"^(#+)\s.*", line)
        if line_heading_match:
            heading_level = len(line_heading_match.group(1))
            if heading_level <= title_level:
                end_index = i
                break

    # Prepare the new content lines
    new_content_lines = replace_content.strip().split("\n")

    # Assemble the updated content
    updated_lines = (
        lines[: start_index + 1]  # Including the section heading
        + [""]  # Add a blank line after the heading
        + new_content_lines  # New section content
        + [""]  # Add a blank line after the new content
        + lines[end_index:]  # Rest of the original content
    )

    if ends_with_newline:
        updated_lines.append("")  # Ensure the markdown ends with a newline

    return "\n".join(updated_lines)
```

</details>

## Function `sort_sections`

```python
def sort_sections(filename: Path | str) -> str
```

Sorts the sections of a markdown file by their headings, maintaining YAML front matter
and code blocks in their original order.

This function reads a markdown file, splits it into a YAML front matter (if present) and content,
then processes the content to identify and sort sections based on their headings (starting with `##`).
Code blocks are kept intact and not reordered.

Args:

- `filename` (`Path` | `str`): The path to the markdown file to be processed. Can be either a `Path`
  object or a string representing the file path.

Returns:

- `str`: A message indicating whether the file was sorted and saved (`"✅ File {filename} applied."`)
  or if no changes were made (`"File is not changed."`).

Notes:

- The function assumes that sections are marked by `##` at the beginning of a line,
  and code blocks are delimited by triple backticks (```).
- If there's no YAML front matter, the entire document is considered content.
- The sorting of sections is done alphabetically, ignoring any code blocks or other formatting within the section.

Example:

```python
import harrix_pylib as h

h.md.sort_sections("C:/Notes/note.md")
```

Before sorting:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode

## Section

Example text.

Example text.

## About

Another text.

Another text.
```

After sorting:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode

## About

Another text.

Another text.

## Section

Example text.

Example text.
```

<details>
<summary>Code:</summary>

```python
def sort_sections(filename: Path | str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    document_new = sort_sections_content(document)

    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>

## Function `sort_sections_content`

```python
def sort_sections_content(markdown_text: str) -> str
```

Sorts the sections of a markdown text by their headings, maintaining YAML front matter
and code blocks in their original order. Date-like section headers are sorted in
descending order (newest first), while other sections are sorted alphabetically.

Args:

- `markdown_text` (`str`): The Markdown text to sort sections from.

Returns:

- `str`: The sorted Markdown text.

Notes:

- The function assumes that sections are marked by `##` at the beginning of a line,
  and code blocks are delimited by triple backticks (```).
- If there's no YAML front matter, the entire document is considered content.
- Date-like headers (e.g., "## 2024-01-30" or "## 2024-02-01 21:47") are sorted in
  descending order (newest first).
- Non-date headers are sorted alphabetically.
- The sorting ignores any code blocks or other formatting within the section.

Example:

```python
import harrix_pylib as h
from pathlib import Path

text = Path('C:/Notes/note.md').read_text(encoding="utf8")
print(h.md.sort_sections("C:/Notes/note.md"))
```

Before sorting:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode

## 2023-05-15

Example text.

## 2023-06-20 14:30

Another text.

## About

Documentation text.
```

After sorting:

```markdown
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode

## 2023-06-20 14:30

Another text.

## 2023-05-15

Example text.

## About

Documentation text.
```

<details>
<summary>Code:</summary>

```python
def sort_sections_content(markdown_text: str) -> str:
    import re
    from datetime import datetime

    yaml_md, content_md = split_yaml_content(markdown_text)

    is_main_section = True
    is_top_section = False
    top_sections = []
    date_sections = []
    regular_sections = []
    section = ""

    # Pattern for matching date headers: ## YYYY-MM-DD or ## YYYY-MM-DD HH:MM
    date_pattern = re.compile(r"^## (\d{4}-\d{2}-\d{2})(?: \d{2}:\d{2})?")

    lines = content_md.split("\n")
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            section += line + "\n"
            continue

        if line.startswith("## "):
            if is_main_section:
                main_section = section
                is_main_section = False
            else:
                if is_top_section:
                    top_sections.append(section)
                else:
                    # Check if the section header is a date
                    date_match = date_pattern.match(section.split("\n")[0])
                    if date_match:
                        date_sections.append(section)
                    else:
                        regular_sections.append(section)

            if "" in line:
                is_top_section = True
            else:
                is_top_section = False

            section = line + "\n"
        else:
            section += line + "\n"

    if not is_main_section:
        if is_top_section:
            top_sections.append(section)
        else:
            # Check if the last section header is a date
            date_match = date_pattern.match(section.split("\n")[0])
            if date_match:
                date_sections.append(section)
            else:
                regular_sections.append(section)

        # Sort date sections in descending order (newest first)
        if date_sections:

            def extract_date(section_text):
                header = section_text.split("\n")[0]
                # Try to extract full datetime if available
                datetime_match = re.match(r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", header)
                if datetime_match:
                    try:
                        return datetime.strptime(datetime_match.group(1), "%Y-%m-%d %H:%M")
                    except ValueError:
                        pass

                # Fall back to date only
                date_match = re.match(r"^## (\d{4}-\d{2}-\d{2})", header)
                if date_match:
                    try:
                        return datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    except ValueError:
                        return datetime.min
                return datetime.min

            date_sections.sort(key=extract_date, reverse=True)

        # Sort regular sections alphabetically
        if regular_sections:
            regular_sections.sort()

        # Sort top sections alphabetically
        if top_sections:
            top_sections.sort()

        # Remove trailing newline from last section if needed
        all_sections = date_sections + regular_sections
        if all_sections:
            all_sections[-1] = all_sections[-1].rstrip() + "\n"
        elif top_sections:
            top_sections[-1] = top_sections[-1].rstrip() + "\n"

        return yaml_md + "\n\n" + main_section + "".join(top_sections) + "".join(all_sections)

    # If there's only a main section, return the original text
    return markdown_text
```

</details>

## Function `split_toc_content`

```python
def split_toc_content(markdown_text: str) -> tuple[str, str]
```

Separates the Table of Contents (TOC) from the rest of the Markdown content.

Args:

- `markdown_text` (`str`): The string containing the markdown text which includes a TOC.

Returns:

- `tuple[str, str]`: A tuple containing:
  - The extracted TOC lines as a string.
  - The remaining markdown content without the TOC as a string.

Example:

```python\n
import harrix_pylib as h
import re

markdown = "# Title\n\n- [Introduction](#introduction)\n- [Content](#content)\n\n"
markdown += "## Introduction\n\nThis is the start.\n\n"

toc, content = h.md.split_toc_content(markdown)
print(toc)
print(content)
```

<details>
<summary>Code:</summary>

```python
def split_toc_content(markdown_text: str) -> tuple[str, str]:
    is_stop_searching_toc = False
    new_lines = []
    toc_lines = []
    lines = remove_yaml_content(markdown_text).splitlines()
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line)
            continue
        if line.startswith("##"):
            is_stop_searching_toc = True
        if is_stop_searching_toc:
            new_lines.append(line)
        elif not re.match(r"- \[(.*?)\]\(#(.*?)\)$", line.strip()):
            if len(new_lines) == 0 or new_lines[-1].strip() or line:
                new_lines.append(line)
        else:
            toc_lines.append(line)

    return "\n".join(toc_lines), "\n".join(new_lines)
```

</details>

## Function `split_yaml_content`

```python
def split_yaml_content(markdown_text: str) -> tuple[str, str]
```

Splits a markdown note into YAML front matter and the main content.

This function assumes that the note starts with YAML front matter separated by '---' from the rest of the content.

Args:

- `markdown_text` (`str`): The markdown note string to be split.

Returns:

- `tuple[str, str]`: A tuple containing:
  - The YAML front matter as a string, prefixed and suffixed with '---'.
  - The remaining markdown content after the YAML front matter, with leading whitespace removed.

Note:

- If there is no '---' or only one '---' in the note, the function returns an empty string for YAML content
  and the entire note for the content part.
- The function does not validate if the YAML content is properly formatted YAML.

Example:

```python
import harrix_pylib as h

md = Path('C:/Notes/note.md').read_text(encoding="utf8")
yaml, content = h.md.split_yaml_content(md)
```

<details>
<summary>Code:</summary>

```python
def split_yaml_content(markdown_text: str) -> tuple[str, str]:
    if not markdown_text.startswith("---"):
        return "", markdown_text
    parts = markdown_text.split("---", 2)
    if len(parts) < 3:
        return "", markdown_text
    return f"---{parts[1]}---", parts[2].lstrip()
```

</details>
