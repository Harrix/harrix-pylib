import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h


def test_get_project_root():
    path = h.dev.get_project_root()
    assert "harrix-pylib" in str(path)
    assert (path / "tests").is_dir()


def test_lint_and_fix_python_code():
    python_code = "def greet(name):\n    print('Hello, ' +    name)"
    expected_formatted_code = 'def greet(name):\n    print("Hello, " + name)\n'

    formatted_code = h.dev.lint_and_fix_python_code(python_code)
    assert formatted_code.strip() == expected_formatted_code.strip()

    empty_code = ""
    assert h.dev.lint_and_fix_python_code(empty_code) == empty_code

    well_formatted_code = 'def greet(name):\n    print(f"Hello, {name}")\n'
    assert h.dev.lint_and_fix_python_code(well_formatted_code) == well_formatted_code


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


def test_sort_py_code():
    current_folder = h.dev.get_project_root()
    py = Path(current_folder / "tests/data/sort_py_code__before.txt").read_text(encoding="utf8")
    py_after = Path(current_folder / "tests/data/sort_py_code__after.txt").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.py"
        temp_filename.write_text(py, encoding="utf-8")
        h.dev.sort_py_code(temp_filename, True)
        py_applied = temp_filename.read_text(encoding="utf8")

    assert py_after == py_applied


def test_write_in_output_txt():
    @h.dev.write_in_output_txt(is_show_output=False)
    def test_func():
        test_func.add_line("Test")

    test_func()

    output_file = (h.dev.get_project_root() / "temp/output.txt").read_text(encoding="utf8")

    assert "Test" in output_file
    shutil.rmtree(h.dev.get_project_root() / "temp")
