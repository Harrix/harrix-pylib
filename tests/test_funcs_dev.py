"""Tests for the functions in the dev module of harrix_pylib."""

import platform
import shutil
import subprocess

import pytest

import harrix_pylib as h


def test_get_project_root() -> None:
    path = h.dev.get_project_root()
    assert "harrix-pylib" in str(path)
    assert (path / "tests").is_dir()


def test_load_config() -> None:
    config = h.dev.load_config(h.dev.get_project_root() / "tests/data/config.json")
    assert config["path_github"] == "C:/GitHub"

@pytest.mark.skipif(
    subprocess.run(
        "echo test",
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    ).returncode
    != 0,
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
    subprocess.run(
        [shutil.which("powershell"), "-Command", "echo test"],
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
    shutil.which("powershell") is None
    or subprocess.run(
        [shutil.which("powershell"), "-Command", "echo test"],
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
