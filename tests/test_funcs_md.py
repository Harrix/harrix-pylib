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
