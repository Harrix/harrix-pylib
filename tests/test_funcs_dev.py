"""Tests for the functions in the dev module of harrix_pylib."""

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


def test_load_config() -> None:
    config = h.dev.load_config(str(h.dev.get_project_root() / "tests/data/config.json"))
    assert config["path_github"] == "C:/GitHub"

    config_path = Path(h.dev.get_project_root() / "tests/data/config.json")
    config_temp_path = Path(h.dev.get_project_root() / "tests/data/config-temp.json")

    # Create temporary config file
    config_temp_path.write_text('{"path_github": "C:/GitHub/Temp"}', encoding="utf8")

    try:
        # Test loading main config (default behavior)
        config = h.dev.load_config(str(config_path))
        assert config["path_github"] == "C:/GitHub"

        # Test loading temp config with is_temp=True
        config_temp = h.dev.load_config(str(config_path), is_temp=True)
        assert config_temp["path_github"] == "C:/GitHub/Temp"

        # Test loading temp config with relative path
        config_temp2 = h.dev.load_config("tests/data/config.json", is_temp=True)
        assert config_temp2["path_github"] == "C:/GitHub/Temp"
    finally:
        # Clean up temporary config file
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
