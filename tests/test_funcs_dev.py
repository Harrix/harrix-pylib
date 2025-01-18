import shutil
import subprocess

import pytest

import harrix_pylib as h


def test_get_project_root():
    path = h.dev.get_project_root()
    assert "harrix-pylib" in str(path)
    assert (path / "tests").is_dir()


def test_load_config():
    config = h.dev.load_config(h.dev.get_project_root() / "tests/data/config.json")
    assert config["path_github"] == "C:/GitHub"


@pytest.mark.skipif(
    not subprocess.run(["powershell", "-Command", "echo test"], capture_output=True, text=True).returncode == 0,
    reason="PowerShell is not available",
)
def test_run_powershell_script():
    test_commands = "Write-Output 'Hello, World!'"
    expected_output = "Hello, World!\n"

    output = h.dev.run_powershell_script(test_commands)

    assert output.strip() == expected_output.strip()


# @pytest.mark.skipif(
#     not subprocess.run(["powershell", "-Command", "echo test"], capture_output=True, text=True).returncode == 0,
#     reason="PowerShell is not available",
# )
# def test_run_powershell_script_as_admin():
#     test_commands = "Write-Output 'Hello, World!'"
#     expected_output = "Hello, World!\n"
#     output = h.dev.run_powershell_script_as_admin(test_commands)
#     assert output.strip() == "\ufeff" + expected_output.strip()


def test_write_in_output_txt():
    @h.dev.write_in_output_txt(is_show_output=False)
    def test_func():
        test_func.add_line("Test")

    test_func()

    output_file = (h.dev.get_project_root() / "temp/output.txt").read_text(encoding="utf8")

    assert "Test" in output_file
    shutil.rmtree(h.dev.get_project_root() / "temp")
