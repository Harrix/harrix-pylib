import re
import shutil
from pathlib import Path


def file_clear_directory(path: Path | str) -> None:
    """
    This function clears directory with sub-directories.

    Args:

    - `path` (Path | str): Path of directory.

    Returns:

    - `None`.

    Examples:

    ```py
    import harrix-py-funcs as h

    h.file_clear_directory("C:/temp_dir")
    ```

    ```py
    from pathlib import Path
    import harrix-py-funcs as h

    folder = Path(__file__).resolve().parent / "data/temp"
    folder.mkdir(parents=True, exist_ok=True)
    Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
    ...
    h.file_clear_directory(folder)
    ```
    """
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def markdown_get_yaml(markdown_text: str) -> str:
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
    import harrix-py-funcs as h

    md_clean = h.markdown_get_yaml("---\ncategories: [it]\n---\n\nText")
    print(md_clean)  # Text
    ```

    ```py
    from pathlib import Path
    import harrix-py-funcs as h

    md = Path("article.md").read_text(encoding="utf8")
    md_clean = h.markdown_get_yaml(md)
    print(md_clean)
    ```
    """
    find = re.search(r"^---(.|\n)*?---\n", markdown_text.lstrip(), re.DOTALL)
    if find:
        return find.group().rstrip()
    return ""


def markdown_remove_yaml(markdown_text: str) -> str:
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
    import harrix-py-funcs as h

    md_clean = h.markdown_remove_yaml("---\ncategories: [it]\n---\n\nText")
    print(md_clean)  # Text
    ```

    ```py
    from pathlib import Path
    import harrix-py-funcs as h

    md = Path("article.md").read_text(encoding="utf8")
    md_clean = h.markdown_remove_yaml(md)
    print(md_clean)
    ```
    """
    return re.sub(r"^---(.|\n)*?---\n", "", markdown_text.lstrip()).lstrip()
