import os
from pathlib import Path

import harrix_pylib as h


def test_get_yaml_from_markdown():
    current_folder = h.dev.get_project_root()
    filename = current_folder / "tests/data/article.md"
    md = Path(filename).read_text(encoding="utf8")
    md_clean = h.md.get_yaml(md)
    assert len(md_clean.splitlines()) == 4


def test_remove_yaml_from_markdown():
    current_folder = h.dev.get_project_root()
    filename = current_folder / "tests/data/article.md"
    md = Path(filename).read_text(encoding="utf8")
    md_clean = h.md.remove_yaml(md)
    assert len(md_clean.splitlines()) == 1
