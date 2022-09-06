"""
Common functions for working in Python.
"""

import re
import shutil
from pathlib import Path


def clear_directory(path: Path | str) -> None:
    """
    This function clear directory with sub-directories.

    Args:

    - `path` (Path | str): Path of directory.

    Returns:

    - `None`.

    Examples:

    ```py
    import harrixpylib as h

    h.clear_directory("C:/temp_dir")
    ```

    ```py
    from pathlib import Path
    import harrixpylib as h

    folder = Path(__file__).resolve().parent / "data/temp"
    folder.mkdir(parents=True, exist_ok=True)
    Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
    ...
    h.clear_directory(folder)
    ```
    """
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def remove_yaml_from_markdown(markdown_text: str) -> str:
    """
    Function remove YAML from text of the Markdown file.

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
    import harrixpylib as h

    md_clean = h.remove_yaml_from_markdown("---\ncategories: [it]\n---\n\nText")
    print(md_clean)  # Text
    ```

    ```py
    from pathlib import Path
    import harrixpylib as h

    md = Path("article.md").read_text(encoding="utf8")
    md_clean = h.remove_yaml_from_markdown(md)
    print(md_clean)
    ```
    """
    return re.sub(r"^---(.|\n)*?---\n", "", markdown_text.lstrip()).lstrip()


def get_yaml_from_markdown(markdown_text: str) -> str:
    """
    Function get YAML from text of the Markdown file.

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
    import harrixpylib as h

    md_clean = h.get_yaml_from_markdown("---\ncategories: [it]\n---\n\nText")
    print(md_clean)  # Text
    ```

    ```py
    from pathlib import Path
    import harrixpylib as h

    md = Path("article.md").read_text(encoding="utf8")
    md_clean = h.get_yaml_from_markdown(md)
    print(md_clean)
    ```
    """
    find = re.search(r"^---(.|\n)*?---\n", markdown_text.lstrip(), re.DOTALL)
    if find:
        return find.group().rstrip()
    return ""
