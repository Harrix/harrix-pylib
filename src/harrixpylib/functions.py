from pathlib import Path
from typing import Union
import shutil
import re


def clear_directory(path: Union[Path, str]) -> None:
    """This function clear directory with sub-directories.

    Args:
      path: Path of directory from pathlib.

    Returns:
      None.
    """
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def open_file(filename: Union[Path, str]) -> str:
    """This function open file as UTF8 text file.

    Args:
      filename: Name of the file to open.

    Returns:
      Text file content. If the file could not be opened, an empty string is returned.

    Examples:
    ```py
    import harrixpylib as h

    s = h.open_file("text.txt")
    ```
    ```py
    import harrixpylib as h

    text = "Hello, world!"
    h.save_file(text, "text.txt")

    s = h.open_file("text.txt")
    print(s)
    ```
    """
    try:
        with open(Path(filename), "r", encoding="utf8") as file:
            return file.read()
    except IOError:
        return ""


def save_file(text: str, full_filename: Union[Path, str]) -> None:
    """This function save file as UTF8 text file.

    Args:
      text: Text for saving.
      full_filename: Name of the file to save.

    Returns:
      None.
    """
    filename = Path(full_filename)
    with open(filename, "w", encoding="utf8") as file:
        file.write(text)


def remove_yaml_from_markdown(markdown_text: str) -> str:
    """Function remove YAML from text of markdown file.

    Args:
      markdown_text: Text of markdown file.

    Returns:
      Text of markdown file without YAML.
    """
    return re.sub(r"^---(.|\n)*?---\n", "", markdown_text.lstrip()).lstrip()
