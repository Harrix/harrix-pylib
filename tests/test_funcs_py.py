"""Tests for the functions in the py module of harrix_pylib."""

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import harrix_pylib as h
from harrix_pylib.funcs_py import _is_magic_dunder_name, _is_private_name

NOTEBOOK_NBFORMAT = 4


@pytest.mark.slow
def test_create_uv_new_project() -> None:
    with TemporaryDirectory() as temp_dir:
        project_name = "TestProject"
        path = Path(temp_dir)
        cli_commands = """
## CLI commands

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries.
- `ruff check --select I --fix` — sort imports.
- `ruff format` — format the project's Python files.
- `ruff check` — lint the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
        """

        h.py.create_uv_new_project(project_name, temp_dir, "code-insiders", cli_commands)

        # Check if the project directory was created
        project_path = path / project_name
        assert project_path.is_dir()

        project_name_under = project_name.replace("-", "_")
        src_path = project_path / "src" / project_name_under
        assert src_path.is_dir()

        # Check for the presence of expected files
        assert (src_path / "__init__.py").is_file()
        assert (src_path / "main.py").is_file()
        assert (project_path / "pyproject.toml").is_file()
        assert (project_path / "README.md").is_file()

        assert (src_path / "main.py").read_text(encoding="utf-8").strip() == 'print("Hello, World!")'

        settings_path = project_path / ".vscode" / "settings.json"
        tasks_path = project_path / ".vscode" / "tasks.json"
        assert settings_path.is_file()
        assert tasks_path.is_file()

        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        assert settings["python.defaultInterpreterPath"] == "${workspaceFolder}/.venv/Scripts/python.exe"
        assert settings["python.terminal.activateEnvironment"] is True
        assert settings["task.allowAutomaticTasks"] == "on"

        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        task = tasks["tasks"][0]
        assert task["runOptions"]["runOn"] == "folderOpen"
        assert ".venv\\Scripts\\Activate.ps1" in task["command"]

        # Verify content in README.md
        with (project_path / "README.md").open("r", encoding="utf-8") as file:
            content = file.read()
            assert f"# {project_name}\n\n" in content
            assert "uv self update" in content
            assert "uv sync --upgrade" in content
            assert "ruff check --select I --fix" in content
            assert "ruff format" in content
            assert "ruff check" in content
            assert "uv python install 3.13" in content

        # Clean up, if necessary
        if project_path.exists():
            shutil.rmtree(project_path)


@pytest.mark.slow
def test_create_uv_new_library() -> None:
    with TemporaryDirectory() as temp_dir:
        library_name = "TestLibrary"
        path = Path(temp_dir)
        cli_commands = """
## CLI commands

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries.
        """

        h.py.create_uv_new_library(library_name, temp_dir, "code-insiders", cli_commands)

        library_path = path / library_name
        assert library_path.is_dir()

        library_name_under = library_name.replace("-", "_")
        package_path = library_path / "src" / library_name_under
        assert package_path.is_dir()

        assert (package_path / "__init__.py").is_file()
        assert (package_path / "core.py").is_file()
        assert (package_path / "py.typed").is_file()
        assert (library_path / "pyproject.toml").is_file()
        assert (library_path / "README.md").is_file()
        assert (library_path / ".venv").is_dir()

        core_content = (package_path / "core.py").read_text(encoding="utf-8")
        assert "def hello(name: str = " in core_content

        init_content = (package_path / "__init__.py").read_text(encoding="utf-8")
        assert "from .core import hello" in init_content
        assert '__all__ = ["hello"]' in init_content

        settings_path = library_path / ".vscode" / "settings.json"
        tasks_path = library_path / ".vscode" / "tasks.json"
        assert settings_path.is_file()
        assert tasks_path.is_file()

        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        assert settings["python.defaultInterpreterPath"] == "${workspaceFolder}/.venv/Scripts/python.exe"
        assert settings["python.terminal.activateEnvironment"] is True

        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        task = tasks["tasks"][0]
        assert task["runOptions"]["runOn"] == "folderOpen"
        assert ".venv\\Scripts\\Activate.ps1" in task["command"]

        with (library_path / "README.md").open("r", encoding="utf-8") as file:
            content = file.read()
            assert f"# {library_name}\n\n" in content
            assert "uv self update" in content

        if library_path.exists():
            shutil.rmtree(library_path)


@pytest.mark.slow
def test_create_uv_new_notebook() -> None:
    with TemporaryDirectory() as temp_dir:
        notebook_name = "TestNotebook"
        path = Path(temp_dir)
        cli_commands = """
## CLI commands

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries.
        """

        h.py.create_uv_new_notebook(notebook_name, temp_dir, "code-insiders", cli_commands)

        notebook_path = path / notebook_name
        assert notebook_path.is_dir()
        assert (notebook_path / "notebook.ipynb").is_file()
        assert not (notebook_path / "main.py").is_file()
        assert (notebook_path / "pyproject.toml").is_file()
        assert (notebook_path / "README.md").is_file()
        assert (notebook_path / ".venv").is_dir()

        notebook = json.loads((notebook_path / "notebook.ipynb").read_text(encoding="utf-8"))
        assert notebook["nbformat"] == NOTEBOOK_NBFORMAT
        assert 'print("Hello, World!")' in notebook["cells"][0]["source"][0]

        pyproject = (notebook_path / "pyproject.toml").read_text(encoding="utf-8")
        assert "jupyter" in pyproject
        assert "ipykernel" in pyproject

        settings_path = notebook_path / ".vscode" / "settings.json"
        tasks_path = notebook_path / ".vscode" / "tasks.json"
        assert settings_path.is_file()
        assert tasks_path.is_file()

        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        assert settings["python.defaultInterpreterPath"] == "${workspaceFolder}/.venv/Scripts/python.exe"
        assert settings["python.terminal.activateEnvironment"] is True

        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        task = tasks["tasks"][0]
        assert task["runOptions"]["runOn"] == "folderOpen"
        assert ".venv\\Scripts\\Activate.ps1" in task["command"]

        with (notebook_path / "README.md").open("r", encoding="utf-8") as file:
            content = file.read()
            assert f"# {notebook_name}\n\n" in content
            assert "uv self update" in content

        if notebook_path.exists():
            shutil.rmtree(notebook_path)


def test_extract_functions_and_classes() -> None:
    current_folder = h.dev.get_project_root()
    filename = Path(current_folder / "tests/data/extract_functions_and_classes__before.txt")
    md_after = Path(current_folder / "tests/data/extract_functions_and_classes__after.txt").read_text(encoding="utf8")

    md = h.py.extract_functions_and_classes(filename, is_add_link_demo=False)
    assert md == md_after


def test_extract_functions_and_classes_nested_docs_links() -> None:
    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        src_folder = temp_path / "src" / "pkg"
        module_file = src_folder / "sub" / "module.py"
        module_file.parent.mkdir(parents=True)
        module_file.write_text(
            '''class NestedClass:
    """Nested class docstring."""
    pass

def nested_function() -> None:
    """Nested function docstring."""
    pass
''',
            encoding="utf-8",
        )

        md = h.py.extract_functions_and_classes(
            module_file,
            is_add_link_demo=True,
            domain="https://example.com/repo",
            src_folder=temp_path / "src",
        )

        assert "Doc: [sub/module.g.md](https://example.com/repo/blob/main/docs/sub/module.g.md)" in md
        assert "docs/sub/module.g.md" in md
        assert "docs/module.g.md" not in md


def test_generate_md_docs_nested_folder_readme_links() -> None:
    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        src_folder = temp_path / "src" / "pkg" / "sub"
        src_folder.mkdir(parents=True)

        (src_folder / "test_file.py").write_text(
            '''def example_function() -> None:
    """Example function in nested folder."""
    pass
''',
            encoding="utf-8",
        )
        (temp_path / "README.md").write_text("# Test\n\n## 📚 List of functions\n", encoding="utf-8")

        h.py.generate_md_docs(folder=temp_path, beginning_of_md="# Test Documentation\n", domain="test")

        readme_content = (temp_path / "README.md").read_text(encoding="utf-8")
        assert "test/blob/main/docs/sub/test_file.g.md" in readme_content
        assert "Doc: [sub/test_file.g.md](test/blob/main/docs/sub/test_file.g.md)" in readme_content
        assert (temp_path / "docs" / "sub" / "test_file.g.md").exists()


def test_generate_md_docs() -> None:
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
        result = h.py.generate_md_docs(folder=temp_path, beginning_of_md="# Test Documentation\n", domain="test")

        # Assertions
        docs_folder = temp_path / "docs"
        index_file = docs_folder / "index.g.md"
        test_file_docs = docs_folder / "test_file.g.md"

        # Check if documentation was generated
        assert docs_folder.exists(), "Docs folder should be created."
        assert index_file.exists(), "Index file should be created."
        assert test_file_docs.exists(), "Test file documentation should be created."

        # Check content of index.g.md
        index_content = index_file.read_text(encoding="utf8")
        assert "# Test Documentation" in index_content, "Index file should contain the beginning Markdown."
        assert "## List of functions" in index_content, "Index should include a list of functions section."

        # Check content of test_file.g.md
        test_file_content = test_file_docs.read_text(encoding="utf8")
        assert "# 📄 File `test_file.py`" in test_file_content, (
            "Test file documentation should start with its name and emoji."
        )
        assert "```python" in test_file_content, "Should contain code blocks."
        assert "<details>" in test_file_content, "Should contain details tags for code sections."
        assert "<summary>Code:</summary>" in test_file_content, "Should contain summary tags for code sections."
        assert "## 🔧 Function `example_function`" in test_file_content, (
            "Example function should be documented with emoji."
        )
        assert "## 🏛️ Class `ExampleClass`" in test_file_content, "Example class should be documented with emoji."
        assert "### ⚙️ Method `__init__`" in test_file_content, "Class method should be documented with emoji."
        assert "### ⚙️ Method `example_method`" in test_file_content, (
            "Another class method should be documented with emoji."
        )

        # Check the result string
        assert "File test_file.py is processed." in result, "Result should indicate processing of the test file."
        assert "File README.md copied as index.g.md" in result, (
            "Result should indicate creation of index.g.md from README.md."
        )


def test_generate_md_docs_strips_existing_front_matter_from_root_md() -> None:
    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        (temp_path / "src").mkdir()
        (temp_path / "README.md").write_text("# Test\n\n## List of functions\n", encoding="utf-8")
        (temp_path / "DEVELOPMENT.md").write_text(
            "---\nlang: en\n---\n\n# Development\n",
            encoding="utf-8",
        )
        beginning = "---\nlang: en\nauthor: Test\n---"
        h.py.generate_md_docs(temp_path, beginning, "test")
        development_content = (temp_path / "docs" / "development.g.md").read_text(encoding="utf-8")
        assert development_content.count("---") == 2  # noqa: PLR2004
        assert "author: Test" in development_content
        assert "# Development" in development_content
        assert "lang: en\n---\n\n---" not in development_content


def test_generate_md_docs_content() -> None:
    # Setup
    content = '''
def example_function(a: int, b: int) -> int:
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
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)

        # Create the test file
        test_file = temp_path / "test_file.py"
        test_file.write_text(content, encoding="utf8")

        # Test
        md_content = h.py.generate_md_docs_content(str(test_file))

        # Assertions
        assert "# 📄 File `test_file.py`" in md_content, "Doc should start with file name and emoji."
        assert "```python" in md_content, "Doc should contain code blocks."
        assert "<details>" in md_content, "Doc should have details tags for code sections."
        assert "<summary>Code:</summary>" in md_content, "Doc should have summary tags for code sections."

        assert "## 🔧 Function `example_function`" in md_content, "Example function should be documented with emoji."
        assert "def example_function(a: int, b: int) -> int" in md_content, "Function signature should be present."
        assert "Adds two integers and returns the sum" in md_content, "Function docstring should be included."

        assert "## 🏛️ Class `ExampleClass`" in md_content, "Example class should be documented with emoji."
        assert "class ExampleClass" in md_content, "Class signature should be present."
        assert "A class for demonstration" in md_content, "Class docstring should be included."

        assert "### ⚙️ Method `__init__`" in md_content, "Class __init__ method should be documented with emoji."
        assert "def __init__(self, value: str)" in md_content, "Method signature should be present."
        assert "Initialize the class" in md_content, "Method docstring should be included."

        assert "### ⚙️ Method `example_method`" in md_content, "Class method should be documented with emoji."
        assert "def example_method(self)" in md_content, "Method signature should be present."
        assert "A method that does nothing" in md_content, "Method docstring should be included."


def test_is_private_name() -> None:
    assert _is_private_name("_helper")
    assert _is_private_name("__internal")
    assert not _is_private_name("public")
    assert not _is_private_name("__init__")
    assert not _is_private_name("__str__")
    assert _is_magic_dunder_name("__init__")
    assert not _is_magic_dunder_name("__internal")


def test_generate_md_docs_content_excludes_private_symbols() -> None:
    content = '''
def _private_function() -> None:
    """Private module function."""
    pass

def public_function() -> None:
    """Public module function."""
    pass

class _PrivateClass:
    """Private class."""

    def method(self) -> None:
        """Private class method."""
        pass

class PublicClass:
    """Public class."""

    def __init__(self) -> None:
        """Initialize the class."""
        pass

    def _internal_method(self) -> None:
        """Private method."""
        pass

    def public_method(self) -> None:
        """Public method."""
        pass
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        test_file = temp_path / "private_symbols.py"
        test_file.write_text(content, encoding="utf8")

        md_content = h.py.generate_md_docs_content(str(test_file))

        assert "# 📄 File `private_symbols.py`" in md_content
        assert "## 🔧 Function `public_function`" in md_content
        assert "## 🏛️ Class `PublicClass`" in md_content
        assert "### ⚙️ Method `__init__`" in md_content
        assert "### ⚙️ Method `public_method`" in md_content
        assert "_private_function" not in md_content
        assert "_PrivateClass" not in md_content
        assert "### ⚙️ Method `_internal_method`" not in md_content


def test_extract_functions_and_classes_excludes_private_symbols() -> None:
    content = '''
def _private_function() -> None:
    """Private module function."""
    pass

def public_function() -> None:
    """Public module function."""
    pass

class _PrivateClass:
    """Private class."""
    pass
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        test_file = temp_path / "private_symbols.py"
        test_file.write_text(content, encoding="utf8")

        md = h.py.extract_functions_and_classes(test_file, is_add_link_demo=False)

        assert "public_function" in md
        assert "_private_function" not in md
        assert "_PrivateClass" not in md


def test_extract_functions_and_classes_returns_empty_for_private_only_file() -> None:
    content = '''
def _private_function() -> None:
    """Private module function."""
    pass

class _PrivateClass:
    """Private class."""
    pass
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        test_file = temp_path / "private_only.py"
        test_file.write_text(content, encoding="utf8")

        md = h.py.extract_functions_and_classes(test_file, is_add_link_demo=False)

        assert md == ""


def test_generate_md_docs_skips_private_only_file() -> None:
    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        src_folder = temp_path / "src"
        src_folder.mkdir()

        (src_folder / "public_file.py").write_text(
            '''def public_function() -> None:
    """Public module function."""
    pass
''',
            encoding="utf8",
        )
        (src_folder / "private_only.py").write_text(
            '''def _private_function() -> None:
    """Private module function."""
    pass

class _PrivateClass:
    """Private class."""
    pass
''',
            encoding="utf8",
        )
        (temp_path / "README.md").write_text("# Test\n\n## 📚 List of functions\n", encoding="utf8")

        result = h.py.generate_md_docs(folder=temp_path, beginning_of_md="# Test Documentation\n", domain="test")

        docs_folder = temp_path / "docs"
        assert (docs_folder / "public_file.g.md").exists()
        assert not (docs_folder / "private_only.g.md").exists()
        assert "File public_file.py is processed." in result
        assert "File private_only.py is skipped (no public API)." in result

        readme_content = (temp_path / "README.md").read_text(encoding="utf8")
        assert "public_file" in readme_content
        assert "private_only" not in readme_content


def test_generate_md_docs_content_includes_private_symbols() -> None:
    content = '''
def _private_function() -> None:
    """Private module function."""
    pass

def public_function() -> None:
    """Public module function."""
    pass

class _PrivateClass:
    """Private class."""

    def method(self) -> None:
        """Private class method."""
        pass

class PublicClass:
    """Public class."""

    def __init__(self) -> None:
        """Initialize the class."""
        pass

    def _internal_method(self) -> None:
        """Private method."""
        pass

    def public_method(self) -> None:
        """Public method."""
        pass
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        test_file = temp_path / "private_symbols.py"
        test_file.write_text(content, encoding="utf8")

        md_content = h.py.generate_md_docs_content(str(test_file), include_private=True)

        assert "# 📄 File `private_symbols.py`" in md_content
        assert "## 🔧 Function `public_function`" in md_content
        assert "## 🔧 Function `_private_function`" in md_content
        assert "## 🏛️ Class `PublicClass`" in md_content
        assert "## 🏛️ Class `_PrivateClass`" in md_content
        assert "### ⚙️ Method `__init__`" in md_content
        assert "### ⚙️ Method `public_method`" in md_content
        assert "### ⚙️ Method `_internal_method`" in md_content
        assert "### ⚙️ Method `method`" in md_content


def test_extract_functions_and_classes_includes_private_symbols() -> None:
    content = '''
def _private_function() -> None:
    """Private module function."""
    pass

def public_function() -> None:
    """Public module function."""
    pass

class _PrivateClass:
    """Private class."""
    pass
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        test_file = temp_path / "private_symbols.py"
        test_file.write_text(content, encoding="utf8")

        md = h.py.extract_functions_and_classes(test_file, is_add_link_demo=False, include_private=True)

        assert "public_function" in md
        assert "_private_function" in md
        assert "_PrivateClass" in md


def test_generate_md_docs_includes_private_only_file() -> None:
    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        src_folder = temp_path / "src"
        src_folder.mkdir()

        (src_folder / "public_file.py").write_text(
            '''def public_function() -> None:
    """Public module function."""
    pass
''',
            encoding="utf8",
        )
        (src_folder / "private_only.py").write_text(
            '''def _private_function() -> None:
    """Private module function."""
    pass

class _PrivateClass:
    """Private class."""
    pass
''',
            encoding="utf8",
        )
        (temp_path / "README.md").write_text("# Test\n\n## 📚 List of functions\n", encoding="utf8")

        result = h.py.generate_md_docs(
            folder=temp_path,
            beginning_of_md="# Test Documentation\n",
            domain="test",
            include_private=True,
        )

        docs_folder = temp_path / "docs"
        assert (docs_folder / "public_file.g.md").exists()
        assert (docs_folder / "private_only.g.md").exists()
        assert "File public_file.py is processed." in result
        assert "File private_only.py is processed." in result

        private_docs = (docs_folder / "private_only.g.md").read_text(encoding="utf8")
        assert "## 🔧 Function `_private_function`" in private_docs
        assert "## 🏛️ Class `_PrivateClass`" in private_docs

        readme_content = (temp_path / "README.md").read_text(encoding="utf8")
        assert "public_file" in readme_content
        assert "private_only" in readme_content
        assert "_private_function" in readme_content


def test_generate_md_docs_content_uses_longer_fence_for_nested_backticks() -> None:
    content = '''
class ExampleAction:
    """Process quote files separated by `---`."""

    def execute(self) -> None:
        """Run the action."""
        self.show_instructions("""Given a file like `C:/test/Name-Surname/Title-of-book.md` with content:

````markdown
# Title of book

Line 1.

---

Line 2.
````

After processing:

````markdown
# Title of book

> Line 1.
>
> -- _Name Surname, Title of book_
````
""")
'''

    with TemporaryDirectory() as temp_folder:
        temp_path = Path(temp_folder)
        test_file = temp_path / "example_action.py"
        test_file.write_text(content, encoding="utf8")

        md_content = h.py.generate_md_docs_content(str(test_file))

        assert "Process quote files separated by `---`." in md_content
        assert "`````python" in md_content
        assert "````markdown" in md_content
        details_start = md_content.index("<details>")
        details_end = md_content.index("</details>", details_start)
        details_block = md_content[details_start:details_end]
        assert details_block.count("`````") == 2  # noqa: PLR2004
        assert "```python\ndef execute" not in details_block


def test_lint_and_fix_python_code() -> None:
    python_code = "def greet(name):\n    print('Hello, ' +    name)"
    expected_formatted_code = 'def greet(name):\n    print("Hello, " + name)\n'

    formatted_code = h.py.lint_and_fix_python_code(python_code)
    assert formatted_code.strip() == expected_formatted_code.strip()

    empty_code = ""
    assert h.py.lint_and_fix_python_code(empty_code) == empty_code

    well_formatted_code = 'def greet(name):\n    print(f"Hello, {name}")\n'
    assert h.py.lint_and_fix_python_code(well_formatted_code) == well_formatted_code


def test_should_ignore_path() -> None:
    """Test the h.file.should_ignore_path function with various scenarios."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test directories and files
        hidden_dir = temp_path / ".hidden"
        hidden_dir.mkdir()

        git_dir = temp_path / ".git"
        git_dir.mkdir()

        venv_dir = temp_path / ".venv"
        venv_dir.mkdir()

        venv_no_dot_dir = temp_path / "venv"
        venv_no_dot_dir.mkdir()

        pycache_dir = temp_path / "__pycache__"
        pycache_dir.mkdir()

        node_modules_dir = temp_path / "node_modules"
        node_modules_dir.mkdir()

        idea_dir = temp_path / ".idea"
        idea_dir.mkdir()

        normal_dir = temp_path / "normal_folder"
        normal_dir.mkdir()

        custom_dir = temp_path / "temp_logs"
        custom_dir.mkdir()

        # Test hidden files/folders (starting with dot)
        assert h.file.should_ignore_path(hidden_dir)
        assert h.file.should_ignore_path(git_dir)
        assert h.file.should_ignore_path(venv_dir)
        assert h.file.should_ignore_path(idea_dir)

        # Test standard ignore patterns
        assert h.file.should_ignore_path(venv_no_dot_dir)
        assert h.file.should_ignore_path(pycache_dir)
        assert h.file.should_ignore_path(node_modules_dir)

        # Test normal folders that should not be ignored
        assert not h.file.should_ignore_path(normal_dir)
        assert not h.file.should_ignore_path(custom_dir)

        # Test with string paths instead of Path objects
        assert h.file.should_ignore_path(str(git_dir))
        assert not h.file.should_ignore_path(str(normal_dir))

        # Test with additional patterns
        assert h.file.should_ignore_path(custom_dir, additional_patterns=["temp_logs"])
        assert not h.file.should_ignore_path(normal_dir, additional_patterns=["temp_logs"])

        # Test with ignore_hidden=False
        assert not h.file.should_ignore_path(hidden_dir, is_ignore_hidden=False)
        assert h.file.should_ignore_path(git_dir, is_ignore_hidden=False)  # Still ignored due to pattern
        assert h.file.should_ignore_path(venv_dir, is_ignore_hidden=False)  # Still ignored due to pattern

        # Test with both additional patterns and ignore_hidden=False
        dot_custom = temp_path / ".custom"
        dot_custom.mkdir()
        assert not h.file.should_ignore_path(dot_custom, additional_patterns=["custom"], is_ignore_hidden=False)
        assert h.file.should_ignore_path(dot_custom, additional_patterns=["custom"], is_ignore_hidden=True)

        # Test system-specific files
        ds_store = temp_path / ".DS_Store"
        ds_store.touch()
        thumbs_db = temp_path / "Thumbs.db"
        thumbs_db.touch()

        assert h.file.should_ignore_path(ds_store)
        assert h.file.should_ignore_path(thumbs_db)

        install_deps = temp_path / "install" / "dependencies"
        install_deps.mkdir(parents=True)
        install_only = temp_path / "install"
        deps_only = temp_path / "other" / "dependencies"
        deps_only.mkdir(parents=True)

        assert h.file.should_ignore_path(install_deps)
        assert h.file.should_ignore_path(install_deps / "cache")
        assert not h.file.should_ignore_path(install_only)
        assert not h.file.should_ignore_path(deps_only)
        assert not h.file.should_ignore_path(Path("dependencies"))
        assert h.file.should_ignore_path(Path(".hidden") / "file.md")


def test_sort_py_code() -> None:
    current_folder = h.dev.get_project_root()
    py = Path(current_folder / "tests/data/sort_py_code__before.txt").read_text(encoding="utf8")
    py_after = Path(current_folder / "tests/data/sort_py_code__after.txt").read_text(encoding="utf8")

    with TemporaryDirectory() as temp_folder:
        temp_filename = Path(temp_folder) / "temp.py"
        temp_filename.write_text(py, encoding="utf-8")
        h.py.sort_py_code(str(temp_filename), is_use_ruff_format=True)
        py_applied = temp_filename.read_text(encoding="utf8")

    assert py_after == py_applied
