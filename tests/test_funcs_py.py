import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import harrix_pylib as h


def test_create_uv_new_project():
    with TemporaryDirectory() as temp_dir:
        project_name = "TestProject"
        path = Path(temp_dir)
        editor = "code"
        cli_commands = """
## CLI commands

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries.
- `isort .` — sort imports.
- `ruff format` — format the project's Python files.
- `ruff check` — lint the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
        """

        result = h.py.create_uv_new_project(project_name, temp_dir, "code-insiders", cli_commands)

        # Check if the project directory was created
        project_path = path / project_name
        assert project_path.is_dir()

        # Check if the `src` directory was created
        src_path = project_path / "src" / project_name
        assert src_path.is_dir()

        # Check for the presence of expected files
        assert (src_path / "__init__.py").is_file()
        assert (src_path / "main.py").is_file()
        assert (project_path / "pyproject.toml").is_file()
        assert (project_path / "README.md").is_file()

        # Verify content in README.md
        with (project_path / "README.md").open("r", encoding="utf-8") as file:
            content = file.read()
            assert f"# {project_name}\n\n" in content
            assert "uv self update" in content
            assert "uv sync --upgrade" in content
            assert "isort ." in content
            assert "ruff format" in content
            assert "ruff check" in content
            assert "uv python install 3.13" in content

        # Clean up, if necessary
        if project_path.exists():
            shutil.rmtree(project_path)


def test_lint_and_fix_python_code():
    python_code = "def greet(name):\n    print('Hello, ' +    name)"
    expected_formatted_code = 'def greet(name):\n    print("Hello, " + name)\n'

    formatted_code = h.py.lint_and_fix_python_code(python_code)
    assert formatted_code.strip() == expected_formatted_code.strip()

    empty_code = ""
    assert h.py.lint_and_fix_python_code(empty_code) == empty_code

    well_formatted_code = 'def greet(name):\n    print(f"Hello, {name}")\n'
    assert h.py.lint_and_fix_python_code(well_formatted_code) == well_formatted_code


def test_sort_py_code():
    current_folder = h.dev.get_project_root()
    py = Path(current_folder / "tests/data/sort_py_code__before.txt").read_text(encoding="utf8")
    py_after = Path(current_folder / "tests/data/sort_py_code__after.txt").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.py"
        temp_filename.write_text(py, encoding="utf-8")
        h.py.sort_py_code(temp_filename, True)
        py_applied = temp_filename.read_text(encoding="utf8")

    assert py_after == py_applied
