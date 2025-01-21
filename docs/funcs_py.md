---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_py.py`

## Function `create_uv_new_project`

```python
def create_uv_new_project(project_name: str, path: str | Path, editor: str = "code", cli_commands: str = "") -> str
```

Creates a new project using uv, initializes it, and sets up necessary files.

Args:

- `name_project` (`str`): The name of the new project.
- `path` (`str` | `Path`): The folder path where the project will be created.
- `editor` (`str`): The name of the text editor for opening the project. Example: `code`
- `cli_commands` (`str` | `Path`): The section of CLI commands for `README.md`.

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

<details>
<summary>Code:</summary>

```python
def create_uv_new_project(project_name: str, path: str | Path, editor: str = "code", cli_commands: str = "") -> str:
    commands = f"""
        cd {path}
        uv init --package {project_name}
        cd {project_name}
        uv sync
        uv add --dev isort
        uv add --dev ruff
        uv add --dev pytest
        New-Item -ItemType File -Path src/{project_name}/main.py -Force
        New-Item -ItemType File -Path src/{project_name}/__init__.py -Force
        Add-Content -Path pyproject.toml -Value "`n[tool.ruff]"
        Add-Content -Path pyproject.toml -Value "line-length = 120"
        {editor} {path}/{project_name}"""

    res = h.dev.run_powershell_script(commands)

    readme_path = Path(path) / project_name / "README.md"
    try:
        with readme_path.open("a", encoding="utf-8") as file:
            file.write(f"# {project_name}\n\n{cli_commands}")
        res += f"Content successfully added to {readme_path}"
    except FileNotFoundError:
        res += f"File not found: {readme_path}"
    except IOError as e:
        res += f"I/O error: {e}"
    except Exception as e:
        res += f"An unexpected error occurred: {e}"

    return res
```

</details>

## Function `extract_functions_and_classes`

```python
def extract_functions_and_classes(filename: Path | str, is_add_link_demo: bool = True, domain: str = "") -> str
```

Extracts all classes and functions from a Python file and formats them into a markdown list.

Args:

- `filename` (Path | str): The path to the Python file to be parsed.
- `is_add_link_demo` (`bool`): Whether to add a link to the documentation demo. Defaults to `True`.
- `domain` (`str`): The domain for the documentation link. Defaults to an empty string.

Returns:

- `str`: Returns the markdown-formatted list of classes and functions.

Example output:

```markdown
### File `extract_functions_and_classes__before.py`

| Function/Class | Description |
|----------------|-------------|
| Class `Cat (Animal)` | Represents a domestic cat, inheriting from the `Animal` base class. |
| `add` | Adds two integers. |
| `multiply` | Multiples two integers. |
```

<details>
<summary>Code:</summary>

```python
def extract_functions_and_classes(filename: Path | str, is_add_link_demo: bool = True, domain: str = "") -> str:
    filename = Path(filename)
    with open(filename, "r", encoding="utf-8") as f:
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
        # Format the class entry
        if base_classes_str:
            name = f"Class `{class_name} ({base_classes_str})`"
        else:
            name = f"Class `{class_name}`"
        description = summary
        entries.append((name, description))

    # Process functions
    for func_node in functions:
        func_name = f"`{func_node.name}`"
        # Retrieve docstring and extract the first line (summary)
        docstring = ast.get_docstring(func_node)
        summary = docstring.splitlines()[0] if docstring else ""
        # Format the function entry
        entries.append((func_name, summary))

    # Create Markdown table
    output_lines = []
    output_lines.append(f"### File `{filename.name}`\n")
    if is_add_link_demo:
        link = f"{domain}/docs/{filename.stem}.md"
        output_lines.append(f"Doc: [{filename.stem}.md]({link})\n")
    output_lines.append("| Function/Class | Description |")
    output_lines.append("|----------------|-------------|")

    for name, description in entries:
        output_lines.append(f"| {name} | {description} |")

    # Combine all lines and return the result
    result = "\n".join(output_lines)
    return result
```

</details>

## Function `lint_and_fix_python_code`

```python
def lint_and_fix_python_code(py_content: str) -> str
```

Lints and fixes the provided Python code using the `ruff` formatter.

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

<details>
<summary>Code:</summary>

```python
def lint_and_fix_python_code(py_content: str) -> str:
    # Create a temporary file with the content of py_content
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(py_content.encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        subprocess.run(["ruff", "format", temp_file_path], capture_output=True, text=True)

        # Read the fixed code from the temporary file
        with open(temp_file_path, "r", encoding="utf-8") as file:
            fixed_content = file.read()

        return fixed_content

    finally:
        # Delete the temporary file
        os.remove(temp_file_path)
```

</details>

## Function `sort_py_code`

```python
def sort_py_code(filename: str, is_use_ruff_format = True) -> None
```

Sorts the Python code in the given file by organizing classes, functions, and statements.

This function reads a Python file, parses it, sorts classes and functions alphabetically,
and ensures that class attributes, methods, and other statements within classes are ordered
in a structured manner. The sorted code is then written back to the file.

Args:

- `filename` (`str`): The path to the Python file that needs sorting.

Returns:

- `None`: This function does not return a value, it modifies the file in place.

Note:

- This function uses `libcst` for parsing and manipulating Python ASTs.
- Sorting prioritizes initial non-class, non-function statements, followed by sorted classes,
  then sorted functions, and finally any trailing statements.
- Within classes, `__init__` method is placed first among methods, followed by other methods
  sorted alphabetically.

<details>
<summary>Code:</summary>

```python
def sort_py_code(filename: str, is_use_ruff_format=True) -> None:
    with open(filename, "r", encoding="utf-8") as f:
        code: str = f.read()

    module: cst.Module = cst.parse_module(code)

    # Split the module content into initial statements, final statements, classes, and functions
    initial_statements: List[cst.BaseStatement] = []
    final_statements: List[cst.BaseStatement] = []
    class_defs: List[cst.ClassDef] = []
    func_defs: List[cst.FunctionDef] = []

    state: str = "initial"

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            state = "collecting"
            class_defs.append(stmt)
        elif isinstance(stmt, cst.FunctionDef):
            state = "collecting"
            func_defs.append(stmt)
        else:
            if state == "initial":
                initial_statements.append(stmt)
            else:
                final_statements.append(stmt)

    # Sort classes alphabetically and process each class
    class_defs_sorted: List[cst.ClassDef] = sorted(class_defs, key=lambda cls: cls.name.value)

    sorted_class_defs: List[cst.ClassDef] = []
    for class_def in class_defs_sorted:
        class_body_statements = class_def.body.body

        # Initialize containers
        docstring: Optional[cst.SimpleStatementLine] = None
        class_attributes: List[cst.SimpleStatementLine] = []
        methods: List[cst.FunctionDef] = []
        other_statements: List[cst.BaseStatement] = []

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
            else:
                # Other statements (e.g., pass, expressions, etc.)
                other_statements.append(stmt)

        # Process methods: __init__ and other methods
        init_method: Optional[cst.FunctionDef] = None
        other_methods: List[cst.FunctionDef] = []

        for method in methods:
            if method.name.value == "__init__":
                init_method = method
            else:
                other_methods.append(method)

        other_methods_sorted: List[cst.FunctionDef] = sorted(other_methods, key=lambda m: m.name.value)

        if init_method is not None:
            methods_sorted: List[cst.FunctionDef] = [init_method] + other_methods_sorted
        else:
            methods_sorted = other_methods_sorted

        # Assemble the new class body
        new_body: List[cst.BaseStatement] = []
        if docstring:
            new_body.append(docstring)
        new_body.extend(class_attributes)  # Class attributes remain at the top in original order
        new_body.extend(methods_sorted)
        new_body.extend(other_statements)

        new_class_body: cst.IndentedBlock = cst.IndentedBlock(body=new_body)

        # Update the class definition with the new body
        new_class_def: cst.ClassDef = class_def.with_changes(body=new_class_body)
        sorted_class_defs.append(new_class_def)

    # Sort functions alphabetically
    func_defs_sorted: List[cst.FunctionDef] = sorted(func_defs, key=lambda func: func.name.value)

    # Assemble the new module body
    new_module_body: List[cst.BaseStatement] = (
        initial_statements + sorted_class_defs + func_defs_sorted + final_statements
    )

    new_module: cst.Module = module.with_changes(body=new_module_body)

    # Convert the module back to code
    new_code: str = new_module.code

    if is_use_ruff_format:
        new_code = lint_and_fix_python_code(new_code)

    # Write the sorted code back to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_code)
```

</details>
