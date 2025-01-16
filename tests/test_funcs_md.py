from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h


def test_get_yaml_from_markdown():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml.md").read_text(encoding="utf8")
    md_clean = h.md.get_yaml(md)
    assert len(md_clean.splitlines()) == 4


def test_remove_yaml_from_markdown():
    md = Path(h.dev.get_project_root() / "tests/data/get_yaml.md").read_text(encoding="utf8")
    md_clean = h.md.remove_yaml(md)
    assert len(md_clean.splitlines()) == 1


def test_sort_sections():
    current_folder = h.dev.get_project_root()
    md = Path(current_folder / "tests/data/sort_sections__01.md").read_text(encoding="utf8")
    md_sorted = Path(current_folder / "tests/data/sort_sections__02.md").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_dir:
        temp_filename = Path(temp_dir) / "temp.md"
        temp_filename.write_text(md, encoding="utf-8")
        h.md.sort_sections(temp_filename)
        md_temp_sorted = temp_filename.read_text(encoding="utf8")
        print(md_temp_sorted)

    assert md_sorted == md_temp_sorted
