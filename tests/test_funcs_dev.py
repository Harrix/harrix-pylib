import harrix_pylib as h


def test_get_project_root():
    path = h.dev.get_project_root()
    assert "harrix-pylib" in str(path)
    assert (path / "tests").is_dir()


def test_get_project_root():
    config = h.dev.load_config(h.dev.get_project_root() / "tests/data/config.json")
    assert config["path_github"] == "C:/GitHub"
