"""Tests for the functions in the dev module of harrix_pylib."""

import json
import platform
import shutil
import subprocess
from pathlib import Path

import pytest

import harrix_pylib as h

powershell_path = shutil.which("powershell")


def test_get_project_root() -> None:
    path = h.dev.get_project_root()
    assert "harrix-pylib" in str(path)
    assert (path / "tests").is_dir()


def test_config_load() -> None:
    config = h.dev.config_load(str(h.dev.get_project_root() / "tests/data/config.json"))
    assert config["path_github"] == "C:/GitHub"

    config_path = Path(h.dev.get_project_root() / "tests/data/config.json")
    config_temp_path = Path(h.dev.get_project_root() / "tests/data/config-temp.json")

    # Create temporary config file
    config_temp_path.write_text('{"path_github": "C:/GitHub/Temp"}', encoding="utf8")

    try:
        # Test loading main config (default behavior)
        config = h.dev.config_load(str(config_path))
        assert config["path_github"] == "C:/GitHub"

        # Test loading temp config with is_temp=True
        config_temp = h.dev.config_load(str(config_path), is_temp=True)
        assert config_temp["path_github"] == "C:/GitHub/Temp"

        # Test loading temp config with relative path
        config_temp2 = h.dev.config_load("tests/data/config.json", is_temp=True)
        assert config_temp2["path_github"] == "C:/GitHub/Temp"
    finally:
        # Clean up temporary config file
        config_temp_path.unlink(missing_ok=True)


def test_config_save() -> None:
    """Test saving configuration to JSON file."""
    config_path = Path(h.dev.get_project_root() / "tests/data/config-save.json")
    config_temp_path = Path(h.dev.get_project_root() / "tests/data/config-save-temp.json")

    test_config = {"path_github": "C:/GitHub/Test", "version": "1.0"}
    test_config_temp = {"path_github": "C:/GitHub/Temp/Test", "version": "2.0"}

    try:
        # Test saving main config
        h.dev.config_save(test_config, str(config_path))
        assert config_path.exists()
        loaded_config = json.loads(config_path.read_text(encoding="utf8"))
        assert loaded_config == test_config

        # Test saving temp config with is_temp=True
        h.dev.config_save(test_config_temp, str(config_path), is_temp=True)
        assert config_temp_path.exists()
        loaded_config_temp = json.loads(config_temp_path.read_text(encoding="utf8"))
        assert loaded_config_temp == test_config_temp

        # Test saving temp config with relative path
        h.dev.config_save(test_config_temp, "tests/data/config-save.json", is_temp=True)
        loaded_config_temp2 = json.loads(config_temp_path.read_text(encoding="utf8"))
        assert loaded_config_temp2 == test_config_temp
    finally:
        # Clean up test config files
        config_path.unlink(missing_ok=True)
        config_temp_path.unlink(missing_ok=True)


def test_config_update_value() -> None:
    """Test updating a single configuration value in JSON file."""
    config_path = Path(h.dev.get_project_root() / "tests/data/config-update.json")
    config_temp_path = Path(h.dev.get_project_root() / "tests/data/config-update-temp.json")

    initial_config = {"path_github": "C:/GitHub", "version": "1.0", "database": {"host": "localhost", "port": 5432}}

    try:
        # Create initial config file
        h.dev.config_save(initial_config, str(config_path))

        # Test updating simple key
        h.dev.config_update_value("path_github", "C:/GitHub/Updated", str(config_path))
        config = h.dev.config_load(str(config_path))
        assert config["path_github"] == "C:/GitHub/Updated"
        assert config["version"] == "1.0"  # Other values should remain unchanged

        # Test updating nested key using dot notation
        h.dev.config_update_value("database.host", "remote-host", str(config_path))
        config = h.dev.config_load(str(config_path))
        assert config["database"]["host"] == "remote-host"
        port = 5432
        assert config["database"]["port"] == port  # Other nested values should remain unchanged

        # Test updating with is_temp=True
        h.dev.config_save(initial_config, str(config_path), is_temp=True)
        h.dev.config_update_value("version", "2.0", str(config_path), is_temp=True)
        config_temp = h.dev.config_load(str(config_path), is_temp=True)
        assert config_temp["version"] == "2.0"

        # Test updating with relative path
        h.dev.config_update_value("path_github", "C:/GitHub/Relative", "tests/data/config-update.json")
        config2 = h.dev.config_load(str(config_path))
        assert config2["path_github"] == "C:/GitHub/Relative"
    finally:
        # Clean up test config files
        config_path.unlink(missing_ok=True)
        config_temp_path.unlink(missing_ok=True)


@pytest.mark.skipif(
    (
        subprocess.run(
            ["cmd", "/c", "echo", "test"] if platform.system() == "Windows" else ["echo", "test"],
            capture_output=True,
            text=True,
            check=False,
        ).returncode
        != 0
    ),
    reason="Shell commands are not available",
)
def test_run_command() -> None:
    if platform.system() == "Windows":
        test_command = "echo Hello, World!"
        expected_output = "Hello, World!"
    else:
        test_command = "echo 'Hello, World!'"
        expected_output = "Hello, World!"

    output = h.dev.run_command(test_command)

    assert output.strip() == expected_output.strip()


@pytest.mark.skipif(
    powershell_path is None
    or subprocess.run(
        [powershell_path, "-Command", "echo test"],
        capture_output=True,
        text=True,
        check=False,
    ).returncode
    != 0,
    reason="PowerShell is not available",
)
def test_run_powershell_script() -> None:
    test_commands = "Write-Output 'Hello, World!'"
    expected_output = "Hello, World!\n"

    output = h.dev.run_powershell_script(test_commands)

    assert output.strip() == expected_output.strip()


@pytest.mark.slow
@pytest.mark.skipif(
    powershell_path is None
    or subprocess.run(
        [powershell_path, "-Command", "echo test"],
        capture_output=True,
        text=True,
        check=False,
    ).returncode
    != 0,
    reason="PowerShell is not available",
)
def test_run_powershell_script_as_admin() -> None:
    test_commands = "Write-Output 'Hello, World!'"
    expected_output = "Hello, World!\n"
    output = h.dev.run_powershell_script_as_admin(test_commands)
    assert output.strip() == "\ufeff" + expected_output.strip()


def test_write_in_output_txt() -> None:
    @h.dev.write_in_output_txt(is_show_output=False)
    def test_func() -> None:
        test_func.add_line("Test")

    test_func()

    output_file = (h.dev.get_project_root() / "temp/output.txt").read_text(encoding="utf8")

    assert "Test" in output_file
    shutil.rmtree(h.dev.get_project_root() / "temp")
