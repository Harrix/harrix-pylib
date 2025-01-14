import re
from datetime import datetime
from pathlib import Path

import yaml


def add_author_book(filename: Path | str) -> str:
    """
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
    > _Name Surname - Title of book_

    ---

    > Line 3.
    >
    > Line 4.
    >
    > _Name Surname - Modified title of book_
    ```

    Note:

    - If the file does not exist or is not a Markdown file, the function will return `None`.
    - If the file has been modified, it returns a message indicating the changes; otherwise,
      it indicates no changes were made.
    """
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


def add_diary_new_diary(path_diary: str, beginning_of_md: str, is_with_images: bool = False) -> str | Path:
    """
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
    """
    text = f"{beginning_of_md}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    return add_diary_new_note(path_diary, text, is_with_images)


def add_diary_new_dream(path_dream, beginning_of_md, is_with_images: bool = False) -> str | Path:
    """
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
    """
    text = f"{beginning_of_md}\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    text += "`` — не помню.\n\n" * 15 + "`` — не помню.\n"
    return add_diary_new_note(path_dream, text, is_with_images)


def add_diary_new_note(base_path: str | Path, text: str, is_with_images: bool) -> str | Path:
    """
    Adds a new note to the diary or dream diary for the given base path.

    Args:

    - `base_path` (`str | Path`): The base path where the note should be added.
    - `text` (`str`): The content to write in the note.
    - `is_with_images` (`bool`): Whether to create a folder for images alongside the note.

    Returns:

    - `str | Path`: A string message indicating the file was created along with the file path.
    """
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


def add_image_captions(filename: Path | str) -> str:
    """
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
    """
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()
    yaml_md, content_md = split_yaml_content(document)
    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
    lang = data_yaml.get("lang")

    def process_lines(lines):
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

    # Remove captions
    is_caption = False
    new_lines = []
    lines = content_md.split("\n")
    for i, (line, is_code_block) in enumerate(process_lines(lines)):
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
    for line, is_code_block in process_lines(lines):
        if is_code_block:
            new_lines.append(line)
            continue
        match = re.match(r"^\!\[(.*?)\]\((.*?)\.(.*?)\)$", line)
        lst_forbidden = ["![Featured image](featured-image", "img.shields.io", "<!-- no caption -->"]
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


def add_note(base_path: str | Path, name: str, text: str, is_with_images: bool) -> str | Path:
    """
    Adds a note to the specified base path.

    Args:

    - `base_path` (`str | Path`): The path where the note will be added.
    - `name` (`str`): The name for the note file or folder.
    - `text` (`str`): The text content for the note.
    - `is_with_images` (`bool`): If true, creates folders for images.

    Returns:

    - `str | Path`: A tuple containing a message about file creation and the path to the file.
    """
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


def get_yaml(markdown_text: str) -> str:
    """
    Function gets YAML from text of the Markdown file.

    Markdown before processing:

    ```md
    ---
    categories: [it, program]
    tags: [VSCode, FAQ]
    ---

    # Installing VSCode

    ```

    Text after processing:
    ```md
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

    md_clean = h.md.get_yaml("---\ncategories: [it]\n---\n\nText")
    print(md_clean)  # Text
    ```

    ```py
    from pathlib import Path
    import harrix-pylib as h

    md = Path("article.md").read_text(encoding="utf8")
    md_clean = h.md.get_yaml(md)
    print(md_clean)
    ```
    """
    find = re.search(r"^---(.|\n)*?---\n", markdown_text.lstrip(), re.DOTALL)
    if find:
        return find.group().rstrip()
    return ""


def remove_yaml(markdown_text: str) -> str:
    """
    Function removes YAML from text of the Markdown file.

    Markdown before processing:

    ```md
    ---
    categories: [it, program]
    tags: [VSCode, FAQ]
    ---

    # Installing VSCode

    ```

    Markdown after processing:
    ```md
    # Installing VSCode
    ```

    Args:

    - `markdown_text` (str): Text of the Markdown file.

    Returns:

    - `str`: Text of the Markdown file without YAML.

    Examples:
    ```py
    import harrix-pylib as h

    md_clean = h.md.remove_yaml("---\ncategories: [it]\n---\n\nText")
    print(md_clean)  # Text
    ```

    ```py
    from pathlib import Path
    import harrix-pylib as h

    md = Path("article.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml(md)
    print(md_clean)
    ```
    """
    return re.sub(r"^---(.|\n)*?---\n", "", markdown_text.lstrip()).lstrip()


def sort_sections(filename: Path | str) -> str:
    """
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
    """
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()

    # yaml_md, content_md = markdown_split_yaml_content(document)
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

    def process_lines(lines):
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

    lines = content_md.split("\n")
    for i, (line, is_code_block) in enumerate(process_lines(lines)):
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

            if "<!-- top section -->" in line:
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


def split_yaml_content(note: str) -> tuple[str, str]:
    """
    Splits a markdown note into YAML front matter and the main content.

    This function assumes that the note starts with YAML front matter separated by '---' from the rest of the content.

    Args:

    - `note` (`str`): The markdown note string to be split.

    Returns:

    - `tuple[str, str]`: A tuple containing:
        - The YAML front matter as a string, prefixed and suffixed with '---'.
        - The remaining markdown content after the YAML front matter, with leading whitespace removed.

    Note:

    - If there is no '---' or only one '---' in the note, the function returns an empty string for YAML content and the entire note for the content part.
    - The function does not validate if the YAML content is properly formatted YAML.
    """
    parts = note.split("---", 2)
    if len(parts) < 3:
        return "", note
    return f"---{parts[1]}---", parts[2].lstrip()
