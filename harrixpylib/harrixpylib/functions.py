from pathlib import Path
import shutil


def path_to_pathlib(path):
    if isinstance(path, str):
        return Path(path)
    return path


def clear_directory(path):
    """
    This function clear directory with sub-directories
    :param path: path of directory from pathlib
    """
    path = path_to_pathlib(path)
    if path.is_dir():
        shutil.rmtree(path)  # Remove folder
    path.mkdir(parents=True, exist_ok=True)  # Add folder


def open_file(filename):
    filename = path_to_pathlib(filename)
    s = ""
    with open(filename, 'r', encoding='utf8') as file:
        s = file.read()
    return s


def save_file(text, full_filename):
    filename = path_to_pathlib(full_filename)
    with open(full_filename, 'w', encoding='utf8') as file:
        file.write(text)
