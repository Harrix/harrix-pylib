"""Functions for working with Python code."""

import ast
import shutil
import subprocess
import tempfile
from pathlib import Path

import libcst as cst

import harrix_pylib as h


def create_uv_new_project(project_name: str, folder: Path | str, editor: str = "code", cli_commands: str = "") -> str:
    """Create a new project using uv, initializes it, and sets up necessary files.

    Args:

    - `name_project` (`str`): The name of the new project.
    - `path` (`Path | str`): The folder path where the project will be created.
    - `editor` (`str`): The name of the text editor for opening the project. Example: `code`
    - `cli_commands` (`Path | str`): The section of CLI commands for `README.md`.

    Example of `cli_commands`:

    ```markdown
    ## CLI commands

    CLI commands after installation.

    - `uv self update` — update uv itself.
    - `uv sync --upgrade` — update all project libraries.
    - `isort .` — sort imports.
    - `ruff format` — format the project's Python files.
    - `ruff check` — lint the project's Python files.
    - `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.

    ```

    Returns:

    - `str`: A string containing the result of the operations performed.

    Example:

    ```python
    import harrix_pylib as h
    from pathlib import Path

    project_name = "TestProject"
    path = Path("C:/projects")
    h.py.create_uv_new_project(project_name, path, "code")
    ```

    Structure "C:/projects/TestProject":

    ```text
    ├─ .git
    ├─ .gitignore
    ├─ .python-version
    ├─ .venv
    ├─ pyproject.toml
    ├─ README.md
    ├─ src
    │  └─ testproject
    │     ├─ main.py
    │     └─ __init__.py
    └─ uv.lock
    ```

    """
    project_name = project_name.replace("_", "-").replace(" ", "-")
    project_name_under = project_name.replace("-", "_")
    commands = f"""
        cd {folder}
        uv init --package {project_name}
        cd {project_name}
        uv sync
        uv add --dev isort
        uv add --dev ruff
        uv add --dev pytest
        New-Item -ItemType File -Path src/{project_name_under}/main.py -Force
        New-Item -ItemType File -Path src/{project_name_under}/__init__.py -Force
        Add-Content -Path pyproject.toml -Value "`n[tool.ruff]"
        Add-Content -Path pyproject.toml -Value "line-length = 120"
        {editor} {folder}/{project_name}"""

    res = h.dev.run_powershell_script(commands)

    readme_path = Path(folder) / project_name / "README.md"
    try:
        with readme_path.open("a", encoding="utf-8") as file:
            file.write(f"# {project_name}\n\n{cli_commands}")
        res += f"Content successfully added to {readme_path}"
    except FileNotFoundError:
        res += f"File not found: {readme_path}"
    except OSError as e:
        res += f"I/O error: {e}"

    return res


def extract_functions_and_classes(filename: Path | str, *, is_add_link_demo: bool = True, domain: str = "") -> str:
    """Extract all classes and functions from a Python file and formats them into a Markdown list.

    Args:

    - `filename` (Path | str): The path to the Python file to be parsed.
    - `is_add_link_demo` (`bool`): Whether to add a link to the documentation demo. Defaults to `True`.
    - `domain` (`str`): The domain for the documentation link. Defaults to an empty string.

    Returns:

    - `str`: Returns the markdown-formatted list of classes and functions.

    Example output:

    ```text
    ### File `extract_functions_and_classes__before.py`

    | Function/Class | Description |
    |----------------|-------------|
    | Class `Cat (Animal)` | Represents a domestic cat, inheriting from the `Animal` base class. |
    | `add` | Adds two integers. |
    | `multiply` | Multiples two integers. |
    ```

    Examples:

    ```python
    import harrix_pylib as h

    md = h.py.extract_functions_and_classes("C:/project/main.py", is_add_link_demo=False)
    ```

    ```python
    import harrix_pylib as h

    filename = "C:/project/main.py"
    domain = "https://github.com/Harrix/harrix-pylib"
    md = h.py.extract_functions_and_classes(filename, is_add_link_demo=True, domain=domain)
    ```

    """
    filename = Path(filename)
    with Path(filename).open(encoding="utf-8") as f:
        code = f.read()

    # Parse the code into an Abstract Syntax Tree (AST)
    tree = ast.parse(code, filename)

    functions = []
    classes = []

    # Traverse the AST to collect function and class definitions
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
        # Skip other node types (imports, variables, etc.)

    # List of entries for the table
    entries = []

    # Process classes
    for class_node in classes:
        # Get the class name
        class_name = class_node.name
        # Get base classes (inheritance)
        base_classes = [ast.unparse(base) if base is not None else "" for base in class_node.bases]
        base_classes_str = ", ".join(base_classes) if base_classes else ""
        # Retrieve docstring and extract the first line (summary)
        docstring = ast.get_docstring(class_node)
        summary = docstring.splitlines()[0] if docstring else ""

        # Format the class entry with link
        if is_add_link_demo and domain:
            class_link = f"{domain}/tree/main/docs/{filename.stem}.g.md#class-{class_name.lower()}"
            if base_classes_str:
                name = f"Class [`{class_name} ({base_classes_str})`]({class_link})"
            else:
                name = f"Class [`{class_name}`]({class_link})"
        else:
            name = f"Class `{class_name} ({base_classes_str})`" if base_classes_str else f"Class `{class_name}`"

        description = summary
        entries.append((name, description))

    # Process functions
    for func_node in functions:
        func_name = func_node.name
        # Retrieve docstring and extract the first line (summary)
        docstring = ast.get_docstring(func_node)
        summary = docstring.splitlines()[0] if docstring else ""

        # Format the function entry with link
        if is_add_link_demo and domain:
            func_link = f"{domain}/tree/main/docs/{filename.stem}.g.md#function-{func_name.lower()}"
            name = f"[`{func_name}`]({func_link})"
        else:
            name = f"`{func_name}`"

        entries.append((name, summary))

    # Create Markdown table
    output_lines = []
    output_lines.append(f"### File `{filename.name}`\n")
    if is_add_link_demo:
        link = f"{domain}/tree/main/docs/{filename.stem}.g.md"
        output_lines.append(f"Doc: [{filename.stem}.g.md]({link})\n")
    output_lines.append("| Function/Class | Description |")
    output_lines.append("|----------------|-------------|")

    for name, description in entries:
        output_lines.append(f"| {name} | {description} |")

    # Combine all lines and return the result
    return "\n".join(output_lines)


def generate_md_docs(folder: Path | str, beginning_of_md: str, domain: str) -> str:
    r"""Generate documentation for all Python files within a given project folder.

    Args:

    - `folder` (`Path | str`): The path to the project folder, can be either a `Path` object or a string. Defaults to
      the current directory if not specified.
    - `beginning_of_md` (`str`): The content to prepend to each documentation file. This could include headers
      or other Markdown formatting.
    - `domain` (`str`): The domain or context in which the project is used, which might influence how
      documentation is generated or formatted.

    Returns:

    - `str`: A string containing a summary of the operations performed, with each line indicating which file
      was processed or created.

    Example:

    ```python
    import harrix_pylib as h

    path = "C:/projects/project"
    domain = "https://github.com/Harrix/harrix-pylib"
    result = h.py.generate_md_docs(path, "---\nlang: en\n---\n", domain)
    ```

    """
    result_lines = []
    folder = Path(folder)

    docs_folder = folder / "docs"

    # Remove entire docs folder and recreate it
    if docs_folder.exists():
        shutil.rmtree(docs_folder)
        result_lines.append("Removed entire docs folder")

    docs_folder.mkdir(parents=True, exist_ok=True)
    result_lines.append("Created clean docs folder")

    list_funcs_all = ""
    src_folder = folder / "src"

    for filename in src_folder.rglob("*.py"):
        if not (filename.is_file() and not filename.stem.startswith("__")):
            continue

        list_funcs = h.py.extract_functions_and_classes(filename, is_add_link_demo=True, domain=domain)
        docs = generate_md_docs_content(filename)

        # Calculate relative path from src folder to preserve folder structure
        relative_path = filename.relative_to(src_folder)

        # Skip the first part (project name folder) if it exists
        if len(relative_path.parts) > 1:
            # Remove the first directory (project name) from the path
            relative_path_parts = relative_path.parts[1:]
            docs_relative_path = Path(*relative_path_parts).with_suffix(".g.md")
        else:
            # If file is directly in src folder, keep original path
            docs_relative_path = relative_path.with_suffix(".g.md")

        filename_docs = docs_folder / docs_relative_path

        # Create parent directories if they don't exist
        filename_docs.parent.mkdir(parents=True, exist_ok=True)

        final_content = beginning_of_md + "\n" + docs
        final_content = h.md.generate_toc_with_links_content(final_content)
        final_content = h.md.generate_image_captions_content(final_content)
        filename_docs.write_text(final_content, encoding="utf8")

        list_funcs_all += list_funcs + "\n\n"

        result_lines.append(f"File {filename.name} is processed.")

    min_count_lines = 2
    if len(list_funcs_all.splitlines()) > min_count_lines:
        list_funcs_all = list_funcs_all[:-1]

    try:
        h.md.replace_section(folder / "README.md", list_funcs_all, "## 📚 List of functions")
    except FileNotFoundError:
        result_lines.append("❗ Don't find `## List of functions`.")
    except ValueError:
        result_lines.append("❗ Don't find `## List of functions`.")

    # Copy all MD files from root to docs folder
    for md_file in folder.glob("*.md"):
        if md_file.is_file() and not md_file.name.startswith("."):
            # Special handling for README.md - create index.g.md
            if md_file.name.upper() == "README.MD":
                original_content = md_file.read_text(encoding="utf8")
                final_content = beginning_of_md + "\n" + original_content
                final_content = h.md.generate_toc_with_links_content(final_content)
                final_content = h.md.generate_image_captions_content(final_content)

                (docs_folder / "index.g.md").write_text(final_content, encoding="utf8")
                result_lines.append(f"File {md_file.name} copied as index.g.md")
            else:
                # Convert filename to lowercase for other MD files and add .g.md
                target_filename = md_file.stem.lower() + ".g.md"
                target_path = docs_folder / target_filename

                # Read original content and add beginning_of_md
                original_content = md_file.read_text(encoding="utf8")
                final_content = beginning_of_md + "\n" + original_content

                # Apply additional processing
                final_content = h.md.generate_toc_with_links_content(final_content)
                final_content = h.md.generate_image_captions_content(final_content)

                # Write to docs folder
                target_path.write_text(final_content, encoding="utf8")
                result_lines.append(f"File {md_file.name} copied as {target_filename}")

    return "\n".join(result_lines)


def generate_md_docs_content(file_path: Path | str) -> str:
    """Generate Markdown documentation for a single Python file.

    Args:

    - `file_path` (`Path | str`): The path to the Python file to be documented, can be either
      a `Path` object or a string.

    Returns:

    - `str`: A Markdown string containing documentation for the file, including its classes, methods,
      and functions with their signatures, docstrings, and implementation details.

    Example:

    ```python
    import harrix_pylib as h

    filename = "C:/projects/project/main.py"
    result = h.py.generate_md_docs_content(filename)
    ```

    """

    def get_function_signature(node: ast.FunctionDef) -> str:
        args = []
        defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + node.args.defaults

        for arg, default in zip(node.args.args, defaults, strict=False):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            if default:
                arg_str += f" = {ast.unparse(default)}"
            args.append(arg_str)

        if node.args.vararg:
            arg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                arg_str += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(arg_str)

        if node.args.kwarg:
            arg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                arg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(arg_str)

        args_str = ", ".join(args)
        args_str = args_str.replace("'", '"')
        signature = f"def {node.name}({args_str})"  # Create the function signature
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
        return signature

    def get_class_signature(node: ast.ClassDef) -> str:
        bases = [ast.unparse(base) for base in node.bases]
        bases_str = ", ".join(bases)
        signature = f"class {node.name}"
        if bases_str:
            signature += f"({bases_str})"
        return signature

    def get_node_code(node: ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef, source_lines: list[str]) -> str:
        start_line = node.lineno - 1  # AST line numbers start from 1
        end_line = node.end_lineno

        # Check that end_lineno is not None
        if end_line is None:
            return ""

        node_lines = source_lines[start_line:end_line]

        # Remove the docstring if it exists
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_node = node.body[0]
            docstring_start = docstring_node.lineno - 1
            docstring_end = docstring_node.end_lineno

            # Check that docstring_end is not None
            if docstring_end is not None:
                # Calculate the line indexes related to the docstring
                docstring_lines = set(range(docstring_start, docstring_end))
                node_lines = [line for i, line in enumerate(node_lines, start=start_line) if i not in docstring_lines]

        return "".join(node_lines)

    file_path = Path(file_path)
    with Path(file_path).open(encoding="utf-8") as f:
        source = f.read()
    source_lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    markdown_lines = []
    markdown_lines.append(f"# File `{file_path.name}`\n")

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_docstring = ast.get_docstring(node)
            class_signature = get_class_signature(node)
            class_code = get_node_code(node, source_lines)
            # Add the class name and its signature
            markdown_lines.append(f"## Class `{class_name}`\n")
            markdown_lines.append("```python")
            markdown_lines.append(f"{class_signature}")
            markdown_lines.append("```\n")
            if class_docstring:
                markdown_lines.append(f"{class_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
            # Add the code to the details block
            markdown_lines.append("<details>")
            markdown_lines.append("<summary>Code:</summary>\n")
            markdown_lines.append("```python")
            markdown_lines.append(class_code.strip())
            markdown_lines.append("```\n")
            markdown_lines.append("</details>\n")

            # Process class methods
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_name = class_node.name
                    method_docstring = ast.get_docstring(class_node)
                    method_signature = get_function_signature(class_node)
                    method_code = get_node_code(class_node, source_lines)
                    # Add the method name and its signature
                    markdown_lines.append(f"### Method `{method_name}`\n")
                    markdown_lines.append("```python")
                    markdown_lines.append(f"{method_signature}")
                    markdown_lines.append("```\n")
                    if method_docstring:
                        markdown_lines.append(f"{method_docstring}\n")
                    else:
                        markdown_lines.append("_No docstring provided._\n")
                    # Add the code to the details block
                    markdown_lines.append("<details>")
                    markdown_lines.append("<summary>Code:</summary>\n")
                    markdown_lines.append("```python")
                    markdown_lines.append(method_code.strip())
                    markdown_lines.append("```\n")
                    markdown_lines.append("</details>\n")
        elif isinstance(node, ast.FunctionDef):
            # Module level function
            func_name = node.name
            func_docstring = ast.get_docstring(node)
            func_signature = get_function_signature(node)
            func_code = get_node_code(node, source_lines)
            markdown_lines.append(f"## Function `{func_name}`\n")
            markdown_lines.append("```python")
            markdown_lines.append(f"{func_signature}")
            markdown_lines.append("```\n")
            if func_docstring:
                markdown_lines.append(f"{func_docstring}\n")
            else:
                markdown_lines.append("_No docstring provided._\n")
            # Add the code to the details block
            markdown_lines.append("<details>")
            markdown_lines.append("<summary>Code:</summary>\n")
            markdown_lines.append("```python")
            markdown_lines.append(func_code.strip())
            markdown_lines.append("```\n")
            markdown_lines.append("</details>\n")
    # Join all lines
    return "\n".join(markdown_lines)


def lint_and_fix_python_code(py_content: str) -> str:
    r"""Lints and fixes the provided Python code using the `ruff` formatter.

    This function formats the given Python code content by:

    1. Writing the content to a temporary file.
    2. Running `ruff format` on the temporary file to fix any linting issues.
    3. Reading back the formatted content.
    4. Cleaning up by removing the temporary file.

    Args:

    - `py_content` (`str`): The Python code content to be linted and fixed.

    Returns:

    - `str`: The formatted and fixed Python code.

    Raises:

    - `subprocess.CalledProcessError`: If `ruff` command fails to execute or returns an error status.
    - `OSError`: If there are issues with file operations (e.g., creating or deleting the temporary file).

    Note:

    - This function assumes `ruff` is installed and accessible in the system's PATH.
    - Any exceptions from `ruff` or file operations are not caught within this function and will propagate up.

    Example:

    ```python
    import harrix_pylib as h

    python_code = "def greet(name):\n    print('Hello, ' +    name)"
    formatted_code = h.py.lint_and_fix_python_code(python_code)
    print(formatted_code)
    # def greet(name):
    #     print("Hello, " + name)
    ```

    """
    # Create a temporary file with the content of py_content
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(py_content.encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        ruff_path = shutil.which("ruff")
        if ruff_path:
            subprocess.run([ruff_path, "format", temp_file_path], capture_output=True, text=True, check=False)
        else:
            print("Ruff was not found in the system")

        # Read the fixed code from the temporary file
        with Path(temp_file_path).open(encoding="utf-8") as file:
            return file.read()

    finally:
        # Delete the temporary file
        Path(temp_file_path).unlink()


def sort_py_code(filename: str, *, is_use_ruff_format: bool = True) -> None:
    r'''Sorts the Python code in the given file by organizing classes, functions, and statements.

    This function reads a Python file, parses it, sorts classes and functions alphabetically,
    and ensures that class attributes, methods, and other statements within classes are ordered
    in a structured manner. The sorted code is then written back to the file.

    Args:

    - `filename` (`str`): The path to the Python file that needs sorting.
    - `is_use_ruff_format` (`bool`, optional): If True, use Ruff to format the sorted code. Defaults to `True`.

    Returns:

    - `None`: This function does not return a value, it modifies the file in place.

    Note:

    - This function uses `libcst` for parsing and manipulating Python ASTs.
    - Sorting prioritizes initial non-class, non-function statements, followed by sorted classes,
      then sorted functions, and finally any trailing statements.
    - Within classes, `__init__` method is placed first among methods, followed by other methods
      sorted alphabetically, with single underscore methods at the end.
    - Functions and methods starting with single underscore are placed after regular ones.

    Example:

    ```python
        import harrix_pylib as h

        h.py.sort_py_code("C:/projects/project/main.py", is_use_ruff_format=True)

    ```

    Before sorting:

    ```python
    def _helper_function():
        """Helper function."""
        pass

    def multiply(a, b):
        """Returns the product of two numbers."""
        return a * b

    def add(a, b):
        """Returns the sum of two numbers."""
        return a + b

    class Point:
        def _internal_method(self):
            """Internal method."""
            pass

        def move(self, dx, dy):
            """Moves the point by a given distance along x and y axes."""
            self.x += dx
            self.y += dy

        def __init__(self, x=0, y=0):
            """Initializes a point with coordinates (x, y)."""
            self.x = x
            self.y = y

        def distance_to_origin(self):
            """Returns the distance from the point to the origin."""
            return (self.x**2 + self.y**2) ** 0.5
    ```

    After sorting:

    ```python
    class Point:
        def __init__(self, x=0, y=0):
            """Initializes a point with coordinates (x, y)."""
            self.x = x
            self.y = y

        def distance_to_origin(self):
            """Returns the distance from the point to the origin."""
            return (self.x**2 + self.y**2) ** 0.5

        def move(self, dx, dy):
            """Moves the point by a given distance along x and y axes."""
            self.x += dx
            self.y += dy

        def _internal_method(self):
            """Internal method."""
            pass

    def add(a, b):
        """Returns the sum of two numbers."""
        return a + b

    def multiply(a, b):
        """Returns the product of two numbers."""
        return a * b

    def _helper_function():
        """Helper function."""
        pass
    ```

    '''

    def _get_sort_key(name: str) -> tuple[int, str]:
        """Return a sort key for function/method names.

        Priority:
        0. __init__ method - highest priority
        1. Other special methods (double underscore)
        2. Regular methods/functions
        3. Private methods/functions (single underscore)
        """
        if name == "__init__":
            return (0, name)  # __init__ always first
        if name.startswith("__") and name.endswith("__"):
            return (1, name)  # Other special methods like __str__, __repr__
        if name.startswith("_") and not name.startswith("__"):
            return (3, name)  # Private methods/functions with single underscore
        return (2, name)  # Regular methods/functions

    with Path(filename).open(encoding="utf-8") as f:
        code: str = f.read()

    module: cst.Module = cst.parse_module(code)

    # Split the module content into initial statements, final statements, classes, and functions
    initial_statements: list[cst.BaseStatement] = []
    final_statements: list[cst.BaseStatement] = []
    class_defs: list[cst.ClassDef] = []
    func_defs: list[cst.FunctionDef] = []

    state: str = "initial"

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            state = "collecting"
            class_defs.append(stmt)
        elif isinstance(stmt, cst.FunctionDef):
            state = "collecting"
            func_defs.append(stmt)
        elif state == "initial":
            initial_statements.append(stmt)
        else:
            final_statements.append(stmt)

    # Sort classes alphabetically and process each class
    class_defs_sorted: list[cst.ClassDef] = sorted(class_defs, key=lambda cls: cls.name.value)

    sorted_class_defs: list[cst.ClassDef] = []
    for class_def in class_defs_sorted:
        class_body_statements = class_def.body.body

        # Initialize containers
        docstring: cst.SimpleStatementLine | None = None
        class_attributes: list[cst.SimpleStatementLine] = []
        methods: list[cst.FunctionDef] = []
        other_statements: list[cst.BaseStatement] = []

        idx: int = 0
        total_statements: int = len(class_body_statements)

        # Check if there is a docstring
        if total_statements > 0:
            first_stmt = class_body_statements[0]
            if (
                isinstance(first_stmt, cst.SimpleStatementLine)
                and isinstance(first_stmt.body[0], cst.Expr)
                and isinstance(first_stmt.body[0].value, cst.SimpleString)
            ):
                docstring = first_stmt
                idx = 1  # Start from the next statement

        # Process the remaining statements in the class body
        for stmt in class_body_statements[idx:]:
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(elem, (cst.Assign, cst.AnnAssign)) for elem in stmt.body
            ):
                # This is a class attribute
                class_attributes.append(stmt)
            elif isinstance(stmt, cst.FunctionDef):
                # This is a class method
                methods.append(stmt)
            elif isinstance(stmt, cst.BaseStatement):
                # Other BaseStatement types (e.g., pass, expressions, etc.)
                other_statements.append(stmt)
            # Skip BaseSmallStatement types as they should be wrapped in SimpleStatementLine

        # Sort methods with custom priority: special methods first, then regular, then private
        methods_sorted: list[cst.FunctionDef] = sorted(methods, key=lambda m: _get_sort_key(m.name.value))

        # Assemble the new class body - all elements must be BaseStatement
        new_body: list[cst.BaseStatement] = []
        if docstring:
            new_body.append(docstring)
        new_body.extend(class_attributes)  # SimpleStatementLine inherits from BaseStatement
        new_body.extend(methods_sorted)  # FunctionDef inherits from BaseStatement
        new_body.extend(other_statements)  # Already BaseStatement

        new_class_body: cst.IndentedBlock = cst.IndentedBlock(body=new_body)

        # Update the class definition with the new body
        new_class_def: cst.ClassDef = class_def.with_changes(body=new_class_body)
        sorted_class_defs.append(new_class_def)

    # Sort functions with custom priority: regular functions first, then private
    func_defs_sorted: list[cst.FunctionDef] = sorted(func_defs, key=lambda func: _get_sort_key(func.name.value))

    # Assemble the new module body
    new_module_body: list[cst.BaseStatement] = (
        initial_statements + sorted_class_defs + func_defs_sorted + final_statements
    )

    new_module: cst.Module = module.with_changes(body=new_module_body)

    # Convert the module back to code
    new_code: str = new_module.code

    if is_use_ruff_format:
        new_code = lint_and_fix_python_code(new_code)

    # Write the sorted code back to the file
    with Path(filename).open("w", encoding="utf-8") as f:
        f.write(new_code)
