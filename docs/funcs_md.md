---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_md.py`

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

```py
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

```py
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

```py
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

```py
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

    parts = document.split("---", 2)
    if len(parts) < 3:
        return "File is not changed."
    else:
        yaml_md, content_md = f"---{parts[1]}---", parts[2].lstrip()

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

    document_new = yaml_md + "\n\n" + content_md
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
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

```py
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
    note_initial = file.read_text(encoding="utf8")

    parts = note_initial.split("---", 2)
    yaml_content, main_content = f"---{parts[1]}---", parts[2].lstrip()

    lines = main_content.splitlines()

    author = file.parts[-2].replace("-", " ")
    title = lines[0].replace("# ", "")

    lines = lines[1:] if lines and lines[0].startswith("# ") else lines
    lines = lines[:-1] if lines[-1].strip() == "---" else lines

    note = f"{yaml_content}\n\n# {title}\n\n"
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
    if note_initial != note:
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

```py
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

    parts = document.split("---", 2)
    if len(parts) < 3:
        yaml_md, content_md = "", document
    else:
        yaml_md, content_md = f"---{parts[1]}---", parts[2].lstrip()

    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
    lang = data_yaml.get("lang")

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
            new_lines.append(line)
            caption = f"_Рисунок {image_count} — {alt_text}_" if lang == "ru" else f"_Figure {image_count}: {alt_text}_"
            new_lines.append("\n" + caption)
        else:
            new_lines.append(line)
    content_md = "\n".join(new_lines)

    document_new = yaml_md + "\n\n" + content_md
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
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

result = h.md.sort_sections("C:/Notes/note.md")
print(result)
```

<details>
<summary>Code:</summary>

```python
def generate_toc_with_links(filename: Path | str) -> str:

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

    result_lines = []
    filename = Path(filename)

    document = filename.read_text(encoding="utf8")

    parts = document.split("---", 2)
    if len(parts) < 3:
        yaml_md = ""
    else:
        yaml_md = f"---{parts[1]}---"

    # Generate TOC
    existing_ids = set()
    lines = remove_yaml_and_code_content(document).splitlines()
    toc_lines = []
    for line in lines:
        if line.startswith("##"):
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
    result_lines.append("TOC:\n\n" + toc)

    # Delete old TOC
    is_stop_searching_toc = False
    new_lines = []
    lines = remove_yaml_content(document).splitlines()
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
    content_without_yaml = "\n".join(new_lines)

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

    document_new = yaml_md + "\n\n" + content_without_yaml
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        result_lines.append(f"✅ TOC is added or refreshed in {filename}.")
    else:
        result_lines.append("File is not changed.")

    return "\n".join(result_lines)
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

```py
import harrix-pylib as h

md_clean = h.md.get_yaml_content("---\ncategories: [it]\n---\n\nText")
print(md_clean)  # Text
```

```py
from pathlib import Path
import harrix-pylib as h

md = Path("article.md").read_text(encoding="utf8")
md_clean = h.md.get_yaml_content(md)
print(md_clean)
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

```py
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

## Function `remove_yaml`

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

```py
import harrix-pylib as h

md_clean = h.md.remove_yaml_content("---\ncategories: [it]\n---\n\nText")
print(md_clean)  # Text
```

```py
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

```py
import harrix-pylib as h

md_clean = h.md.remove_yaml_and_code_content("---\ncategories: [it]\n---\n\nText")
print(md_clean)  # Text
```

```py
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
    parts = markdown_text.split("---", 2)
    if len(parts) < 3:
        content_md = markdown_text
    else:
        content_md = parts[2].lstrip()

    new_lines = []
    lines = content_md.split("\n")
    for line, is_code_block in identify_code_blocks(lines):
        if is_code_block:
            continue
        new_lines.append(line)

    return "\n".join(new_lines)
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

```py
import harrix_pylib as h

new_content = "New list of commands:\n\n- new command1\n- new command2"
result_message = h.md.replace_section("C:/Notes/note.md", new_content, "## List of commands")
```

<details>
<summary>Code:</summary>

```python
def replace_section(filename: Path | str, replace_content, title_section: str = "## List of commands") -> str:
    filename = Path(filename)  # Ensure filename is a Path object

    if not filename.exists():
        raise FileNotFoundError(f"The file {filename} does not exist.")

    # Read the file content
    with filename.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the start index of the section to replace
    start_index = None
    for i, line in enumerate(lines):
        if line.strip() == title_section:
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
    end_index = len(lines)  # Default to end of file
    for i in range(start_index + 1, len(lines)):
        line = lines[i].strip()
        # Check if the line is a heading of the same or higher level
        line_heading_match = re.match(r"^(#+)\s.*", line)
        if line_heading_match:
            heading_level = len(line_heading_match.group(1))
            if heading_level <= title_level:
                end_index = i
                break

    # Prepare the new content lines (ensure each line ends with a newline character)
    new_content_lines = [line + "\n" for line in replace_content.strip().split("\n")]

    # Assemble the updated content
    updated_lines = (
        lines[: start_index + 1]  # Include lines up to and including the section title
        + ["\n"]  # Add a blank line after the section title
        + new_content_lines  # Add the new section content
        + ["\n"]  # Add a blank line after the new content
        + lines[end_index:]  # Include the rest of the original content
    )

    # Write the updated content back to the file
    with filename.open("w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    return f"Section {title_section} is replaced."
```

</details>

## Function `sort_sections`

```python
def sort_sections(filename: Path | str) -> str
```

Sorts the sections of a markdown document by their headings, maintaining YAML front matter
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

```py
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

    parts = document.split("---", 2)
    if len(parts) < 3:
        yaml_md, content_md = "", document
    else:
        yaml_md, content_md = f"---{parts[1]}---", parts[2].lstrip()

    is_main_section = True
    is_top_section = False
    top_sections = []
    sections = []
    section = ""

    lines = content_md.split("\n")
    for i, (line, is_code_block) in enumerate(identify_code_blocks(lines)):
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
                    sections.append(section)

            if "<!-- top-section -->" in line:
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
            sections.append(section)
        if sections:
            sections.sort()
            sections[-1] = sections[-1][:-1]
        if top_sections:
            if not sections:
                top_sections[-1] = top_sections[-1][:-1]
            top_sections.sort()
        document_new = yaml_md + "\n\n" + main_section + "".join(top_sections) + "".join(sections)
    else:
        document_new = document
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>

## Function `split_yaml_content`

```python
def split_yaml_content(note: str) -> tuple[str, str]
```

Splits a markdown note into YAML front matter and the main content.

This function assumes that the note starts with YAML front matter separated by '---' from the rest of the content.

Args:

- `note` (`str`): The markdown note string to be split.

Returns:

- `tuple[str, str]`: A tuple containing:
  - The YAML front matter as a string, prefixed and suffixed with '---'.
  - The remaining markdown content after the YAML front matter, with leading whitespace removed.

Note:

- If there is no '---' or only one '---' in the note, the function returns an empty string for YAML content
  and the entire note for the content part.
- The function does not validate if the YAML content is properly formatted YAML.

Example:

```py
import harrix_pylib as h

md = h.md.sort_sections("C:/Notes/note.md")
yaml, content = h.md.split_yaml_content(md)
```

<details>
<summary>Code:</summary>

```python
def split_yaml_content(note: str) -> tuple[str, str]:
    parts = note.split("---", 2)
    if len(parts) < 3:
        return "", note
    return f"---{parts[1]}---", parts[2].lstrip()
```

</details>
