"""
Common functions for working in Python.
"""

import re
import shutil
from pathlib import Path
from typing import Union


def clear_directory(path: Union[Path, str]) -> None:
    """This function clear directory with sub-directories.

    Args:
      path: Path of directory.

    Returns:
      None.

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
    """Function remove YAML from text of markdown file.

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
      markdown_text: Text of markdown file.

    Returns:
      Text of markdown file without YAML.

    Examples:
    ```py
    import harrixpylib as h

    md_clean = h.remove_yaml_from_markdown("---\\ncategories: [it]\\n---\\n\\nText")
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
