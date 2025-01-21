import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h


@pytest.mark.slow
def test_create_uv_new_project():
    with TemporaryDirectory() as temp_dir:
        project_name = "TestProject"
        path = Path(temp_dir)
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

        h.py.create_uv_new_project(project_name, temp_dir, "code-insiders", cli_commands)

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


def test_extract_functions_and_classes():
    current_folder = h.dev.get_project_root()
    filename = Path(current_folder / "tests/data/extract_functions_and_classes__before.txt")
    md_after = Path(current_folder / "tests/data/extract_functions_and_classes__after.txt").read_text(encoding="utf8")

    md = h.py.extract_functions_and_classes(filename, False)
    assert md == md_after


def test_generate_docs_for_project():
    # Setup
    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)

        # Create a test environment
        src_folder = temp_path / "src"
        src_folder.mkdir()

        # Create a dummy Python file
        (src_folder / "test_file.py").write_text(
            '''def example_function(a: int, b: int) -> int:
    """Adds two integers and returns the sum."""
    return a + b

class ExampleClass:
    """A class for demonstration."""

    def __init__(self, value: str):
        """Initialize the class."""
        self.value = value

    def example_method(self):
        """A method that does nothing."""
        pass
''',
            encoding="utf8",
        )
        (temp_path / "README.md").write_text("""# Test\n\n## List of functions\n""", encoding="utf8")

        # Test the function
        result = h.py.generate_docs_for_project(
            folder=temp_path, beginning_of_md="# Test Documentation\n", domain="test"
        )

        # Assertions
        docs_folder = temp_path / "docs"
        index_file = docs_folder / "index.md"
        test_file_docs = docs_folder / "test_file.md"

        # Check if documentation was generated
        assert docs_folder.exists(), "Docs folder should be created."
        assert index_file.exists(), "Index file should be created."
        assert test_file_docs.exists(), "Test file documentation should be created."

        # Check content of index.md
        index_content = index_file.read_text(encoding="utf8")
        assert "# Test Documentation" in index_content, "Index file should contain the beginning markdown."
        assert "## List of functions" in index_content, "Index should include a list of functions section."

        # Check content of test_file.md
        test_file_content = test_file_docs.read_text(encoding="utf8")
        assert "# File `test_file.py`" in test_file_content, "Test file documentation should start with its name."
        assert "```python" in test_file_content, "Should contain code blocks."
        assert "<details>" in test_file_content, "Should contain details tags for code sections."
        assert "<summary>Code:</summary>" in test_file_content, "Should contain summary tags for code sections."
        assert "## Function `example_function`" in test_file_content, "Example function should be documented."
        assert "## Class `ExampleClass`" in test_file_content, "Example class should be documented."
        assert "### Method `__init__`" in test_file_content, "Class method should be documented."
        assert "### Method `example_method`" in test_file_content, "Another class method should be documented."

        # Check the result string
        assert "File test_file.py is processed." in result, "Result should indicate processing of the test file."
        assert "File index.md is created." in result, "Result should indicate creation of index.md."


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
