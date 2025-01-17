import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h


@pytest.fixture
def setup_all_to_parent_folder(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = tmp_path / "folder2"
    folder1.mkdir()
    folder2.mkdir()

    (folder1 / "image.jpg").touch()
    (folder1 / "sub1").mkdir()
    (folder1 / "sub1" / "file1.txt").touch()
    (folder1 / "sub2").mkdir()
    (folder1 / "sub2" / "file3.txt").touch()

    sub3 = folder2 / "sub3"
    sub3.mkdir()
    (sub3 / "file6.txt").touch()
    sub4 = sub3 / "sub4"
    sub4.mkdir()
    (sub4 / "file5.txt").touch()

    return str(tmp_path)


def test_all_to_parent_folder(setup_all_to_parent_folder, capsys):
    base_path = setup_all_to_parent_folder
    result = h.file.all_to_parent_folder(base_path)
    assert (Path(base_path) / "folder1" / "file1.txt").exists()
    assert (Path(base_path) / "folder1" / "file3.txt").exists()
    assert (Path(base_path) / "folder2" / "file5.txt").exists()
    assert (Path(base_path) / "folder2" / "file6.txt").exists()
    assert not (Path(base_path) / "folder1" / "sub1").exists()
    assert not (Path(base_path) / "folder1" / "sub2").exists()
    assert not (Path(base_path) / "folder2" / "sub3" / "sub4").exists()
    assert "folder1" in result
    assert "folder2" in result
    # Check if exceptions were printed (none should be printed in this ideal case)
    captured = capsys.readouterr()
    assert captured.out == ""
    shutil.rmtree(base_path)


def test_apply_func():
    def test_func(filename):
        content = Path(filename).read_text(encoding="utf8")
        content = content.upper()
        Path(filename).write_text(content, encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        file1 = Path(temp_folder) / "file1.txt"
        file2 = Path(temp_folder) / "file2.txt"
        Path(file1).write_text("text", encoding="utf8")
        Path(file2).write_text("other", encoding="utf8")
        h.file.apply_func(temp_folder, ".txt", test_func)
        result = file1.read_text(encoding="utf8") + " " + file2.read_text(encoding="utf8")

    assert result == "TEXT OTHER"


def test_check_featured_image():
    folder = h.dev.get_project_root() / "tests/data/check_featured_image/folder_correct"
    assert h.file.check_featured_image(folder)[0]
    folder = h.dev.get_project_root() / "tests/data/check_featured_image/folder_wrong"
    assert not h.file.check_featured_image(folder)[0]


def test_clear_directory():
    folder = h.dev.get_project_root() / "tests/data/temp"
    folder.mkdir(parents=True, exist_ok=True)
    Path(folder / "temp.txt").write_text("Hello, world!", encoding="utf8")
    h.file.clear_directory(folder)
    assert len(next(os.walk(folder))[2]) == 0
    shutil.rmtree(folder)


def test_find_max_folder_number():
    folder = h.dev.get_project_root() / "tests/data/check_featured_image/folder_correct"
    assert h.file.find_max_folder_number(folder, "folder") == 2


def test_open_file_or_folder():
    with pytest.raises(FileNotFoundError):
        h.file.open_file_or_folder("this_path_does_not_exist")


def test_tree_view_folder():
    current_folder = h.dev.get_project_root()
    tree_check = (current_folder / "tests/data/tree_view_folder__01.txt").read_text(encoding="utf8")
    folder_path = current_folder / "tests/data/tree_view_folder"
    assert h.file.tree_view_folder(folder_path) == tree_check
    tree_check = (current_folder / "tests/data/tree_view_folder__02.txt").read_text(encoding="utf8")
    assert h.file.tree_view_folder(folder_path, True) == tree_check
