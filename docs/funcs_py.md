---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_py.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Function `create_uv_new_project`](#function-create_uv_new_project)
- [Function `extract_functions_and_classes`](#function-extract_functions_and_classes)
- [Function `generate_md_docs`](#function-generate_md_docs)
- [Function `generate_md_docs_content`](#function-generate_md_docs_content)
- [Function `lint_and_fix_python_code`](#function-lint_and_fix_python_code)
- [Function `sort_py_code`](#function-sort_py_code)

</details>

## Function `create_uv_new_project`

```python
def create_uv_new_project(project_name: str, folder: str | Path, editor: str = "code", cli_commands: str = "") -> str
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

<details>
<summary>Code:</summary>

```python
def create_uv_new_project(project_name: str, folder: str | Path, editor: str = "code", cli_commands: str = "") -> str:
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

md = h.py.extract_functions_and_classes("C:/project/main.py", False)
```

```python
import harrix_pylib as h

filename = "C:/project/main.py"
domain = "https://github.com/Harrix/harrix-pylib"
md = h.py.extract_functions_and_classes(filename, True, domain)
```

<details>
<summary>Code:</summary>

```python
def extract_functions_and_classes(filename: Path | str, is_add_link_demo: bool = True, domain: str = "") -> str:
    filename = Path(filename)
    with Path.open(filename, encoding="utf-8") as f:
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
        name = f"Class `{class_name} ({base_classes_str})`" if base_classes_str else f"Class `{class_name}`"
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
        link = f"{domain}/tree/main/docs/{filename.stem}.md"
        output_lines.append(f"Doc: [{filename.stem}.md]({link})\n")
    output_lines.append("| Function/Class | Description |")
    output_lines.append("|----------------|-------------|")

    for name, description in entries:
        output_lines.append(f"| {name} | {description} |")

    # Combine all lines and return the result
    return "\n".join(output_lines)
```

</details>

## Function `generate_md_docs`

```python
def generate_md_docs(folder: Path | str, beginning_of_md: str, domain: str) -> str
```

Generates documentation for all Python files within a given project folder.

Args:

- `folder` (`Path | str`): The path to the project folder, can be either a `Path` object or a string. Defaults to
  the current directory if not specified.
- `beginning_of_md` (`str`): The content to prepend to each documentation file. This could include headers
  or other markdown formatting.
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
result = h.py.generate_md_docs(path, "---\\nlang: en\\n---\\n", domain)
```

<details>
<summary>Code:</summary>

```python
def generate_md_docs(folder: Path | str, beginning_of_md: str, domain: str) -> str:
    result_lines = []
    folder = Path(folder)

    docs_folder = folder / "docs"
    docs_folder.mkdir(parents=True, exist_ok=True)

    list_funcs_all = ""

    for filename in (Path(folder) / "src").rglob("*.py"):
        if not (filename.is_file() and not filename.stem.startswith("__")):
            continue

        list_funcs = h.py.extract_functions_and_classes(filename, True, domain)
        docs = generate_md_docs_content(filename)

        filename_docs = docs_folder / f"{filename.stem}.md"

        final_content = beginning_of_md + "\n" + docs
        final_content = h.md.generate_toc_with_links_content(final_content)
        final_content = h.md.generate_image_captions_content(final_content)
        Path(filename_docs).write_text(final_content, encoding="utf8")

        list_funcs_all += list_funcs + "\n\n"

        result_lines.append(f"File {filename.name} is processed.")

    if len(list_funcs_all.splitlines()) > 2:
        list_funcs_all = list_funcs_all[:-1]

    try:
        h.md.replace_section(folder / "README.md", list_funcs_all, "## List of functions")
    except Exception:
        result_lines.append("Don't find `## List of functions`.")
    index_content = beginning_of_md + "\n" + Path(folder / "README.md").read_text(encoding="utf8")
    Path(docs_folder / "index.md").write_text(index_content, encoding="utf8")
    result_lines.append("File index.md is created.")

    return "\n".join(result_lines)
```

</details>

## Function `generate_md_docs_content`

```python
def generate_md_docs_content(file_path: Path | str) -> str
```

Generates Markdown documentation for a single Python file.

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

<details>
<summary>Code:</summary>

````python
def generate_md_docs_content(file_path: Path | str) -> str:

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

    def get_node_code(node: ast.AST, source_lines: list[str]) -> str:
        start_line = node.lineno - 1  # AST line numbers start from 1
        end_line = node.end_lineno
        node_lines = source_lines[start_line:end_line]

        # Remove the docstring if it exists
        if (
            isinstance(node.body, list)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_node = node.body[0]
            docstring_start = docstring_node.lineno - 1
            docstring_end = docstring_node.end_lineno
            # Calculate the indexes of the lines related to the docstring
            docstring_lines = set(range(docstring_start, docstring_end))
            node_lines = [line for i, line in enumerate(node_lines, start=start_line) if i not in docstring_lines]

        return "".join(node_lines)

    file_path = Path(file_path)
    with Path.open(file_path, encoding="utf-8") as f:
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
````

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

Example:

```python
import harrix_pylib as h

python_code = "def greet(name):\n    print('Hello, ' +    name)"
formatted_code = h.py.lint_and_fix_python_code(python_code)
print(formatted_code)
# def greet(name):
#     print("Hello, " + name)
```

<details>
<summary>Code:</summary>

```python
def lint_and_fix_python_code(py_content: str) -> str:
    # Create a temporary file with the content of py_content
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(py_content.encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        subprocess.run(["ruff", "format", temp_file_path], capture_output=True, text=True, check=False)

        # Read the fixed code from the temporary file
        with Path.open(temp_file_path, encoding="utf-8") as file:
            return file.read()

    finally:
        # Delete the temporary file
        os.remove(temp_file_path)
```

</details>

## Function `sort_py_code`

```python
def sort_py_code(filename: str, is_use_ruff_format: bool = True) -> None
```

Sorts the Python code in the given file by organizing classes, functions, and statements.

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
  sorted alphabetically.

Example:

```python
    import harrix_pylib as h

    h.py.sort_py_code("C:/projects/project/main.py", True)

```

Before sorting:

```python
def multiply(a, b):
    \"\"\"Returns the product of two numbers.\"\"\"
    return a * b


def subtract(a, b):
    \"\"\"Returns the difference between two numbers.\"\"\"
    return a - b


def add(a, b):
    \"\"\"Returns the sum of two numbers.\"\"\"
    return a + b


class Point:
    def move(self, dx, dy):
        \"\""Moves the point by a given distance along x and y axes.\"\"\"
        self.x += dx
        self.y += dy

    def __init__(self, x=0, y=0):
        \"\"\"Initializes a point with coordinates (x, y).\"\"\"
        self.x = x
        self.y = y

    def distance_to_origin(self):
        \"\"\"Returns the distance from the point to the origin.\"\"\"
        return (self.x**2 + self.y**2) ** 0.5
```

After sorting:

```python
class Point:
    def __init__(self, x=0, y=0):
        \"\"\"Initializes a point with coordinates (x, y).\"\"\"
        self.x = x
        self.y = y

    def distance_to_origin(self):
        \"\"\"Returns the distance from the point to the origin.\"\"\"
        return (self.x**2 + self.y**2) ** 0.5

    def move(self, dx, dy):
        \"\"\"Moves the point by a given distance along x and y axes.\"\"\"
        self.x += dx
        self.y += dy


def add(a, b):
    \"\"\"Returns the sum of two numbers.\"\"\"
    return a + b


def multiply(a, b):
    \"\"\"Returns the product of two numbers.\"\"\"
    return a * b


def subtract(a, b):
    \"\"\"Returns the difference between two numbers.\"\"\"
    return a - b
```

<details>
<summary>Code:</summary>

```python
def sort_py_code(filename: str, is_use_ruff_format: bool = True) -> None:
    with Path.open(filename, encoding="utf-8") as f:
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
            else:
                # Other statements (e.g., pass, expressions, etc.)
                other_statements.append(stmt)

        # Process methods: __init__ and other methods
        init_method: cst.FunctionDef | None = None
        other_methods: list[cst.FunctionDef] = []

        for method in methods:
            if method.name.value == "__init__":
                init_method = method
            else:
                other_methods.append(method)

        other_methods_sorted: list[cst.FunctionDef] = sorted(other_methods, key=lambda m: m.name.value)

        if init_method is not None:
            methods_sorted: list[cst.FunctionDef] = [init_method, *other_methods_sorted]
        else:
            methods_sorted = other_methods_sorted

        # Assemble the new class body
        new_body: list[cst.BaseStatement] = []
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
    func_defs_sorted: list[cst.FunctionDef] = sorted(func_defs, key=lambda func: func.name.value)

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
    with Path.open(filename, "w", encoding="utf-8") as f:
        f.write(new_code)
```

</details>
