---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `funcs_py.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DocsSourceLoc`](#%EF%B8%8F-class-docssourceloc)
- [🏛️ Class `DocsSymbolIndex`](#%EF%B8%8F-class-docssymbolindex)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add`](#%EF%B8%8F-method-add)
  - [⚙️ Method `add_module`](#%EF%B8%8F-method-add_module)
  - [⚙️ Method `resolve`](#%EF%B8%8F-method-resolve)
  - [⚙️ Method `target_for_heading`](#%EF%B8%8F-method-target_for_heading)
- [🏛️ Class `DocsSymbolTarget`](#%EF%B8%8F-class-docssymboltarget)
- [🔧 Function `check_python_docstring_markdown_errors`](#-function-check_python_docstring_markdown_errors)
- [🔧 Function `create_uv_new_library`](#-function-create_uv_new_library)
- [🔧 Function `create_uv_new_notebook`](#-function-create_uv_new_notebook)
- [🔧 Function `create_uv_new_project`](#-function-create_uv_new_project)
- [🔧 Function `extract_functions_and_classes`](#-function-extract_functions_and_classes)
- [🔧 Function `generate_md_docs`](#-function-generate_md_docs)
- [🔧 Function `generate_md_docs_content`](#-function-generate_md_docs_content)
- [🔧 Function `generate_md_docs_content_with_source_map`](#-function-generate_md_docs_content_with_source_map)
- [🔧 Function `is_python_project`](#-function-is_python_project)
- [🔧 Function `lint_and_fix_python_code`](#-function-lint_and_fix_python_code)
- [🔧 Function `remap_markdown_docs_error`](#-function-remap_markdown_docs_error)
- [🔧 Function `sort_py_code`](#-function-sort_py_code)
- [🔧 Function `validate_uv_project_name`](#-function-validate_uv_project_name)

</details>

## 🏛️ Class `DocsSourceLoc`

```python
class DocsSourceLoc(NamedTuple)
```

Python source location corresponding to a generated Markdown docs line.

<details>
<summary>Code:</summary>

```python
class DocsSourceLoc(NamedTuple):

    path: Path
    line: int
    col: int
```

</details>

## 🏛️ Class `DocsSymbolIndex`

```python
class DocsSymbolIndex
```

Maps unambiguous symbol names to documentation heading targets.

<details>
<summary>Code:</summary>

```python
class DocsSymbolIndex:

    def __init__(self) -> None:
        """Create an empty symbol index."""
        self._key_to_targets: dict[str, list[DocsSymbolTarget]] = {}
        self._heading_targets: dict[tuple[str, str], DocsSymbolTarget] = {}

    def add(self, keys: list[str], target: DocsSymbolTarget, heading_title: str) -> None:
        """Register lookup keys and heading title for a documentation target."""
        self._heading_targets[(target.docs_path, heading_title)] = target
        for key in keys:
            self._key_to_targets.setdefault(key, []).append(target)

    def add_module(self, tree: ast.Module, docs_relative_path: Path, *, include_private: bool) -> None:
        """Index all documented headings from one module in emit order."""
        docs_path = docs_relative_path.as_posix()
        existing_ids: set[str] = set()
        for keys, heading_title in _iter_docs_heading_entries(tree, include_private=include_private):
            anchor = h.md.generate_id(heading_title, existing_ids)
            self.add(keys, DocsSymbolTarget(docs_path, anchor), heading_title)

    def resolve(self, key: str) -> DocsSymbolTarget | None:
        """Return the unique target for `key`, or `None` when missing or ambiguous."""
        targets = self._key_to_targets.get(key)
        if not targets:
            return None
        unique = list(dict.fromkeys(targets))
        if len(unique) != 1:
            return None
        return unique[0]

    def target_for_heading(self, docs_path: str, heading_title: str) -> DocsSymbolTarget | None:
        """Return the target registered for an exact heading title in a docs file."""
        return self._heading_targets.get((docs_path, heading_title))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create an empty symbol index.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        self._key_to_targets: dict[str, list[DocsSymbolTarget]] = {}
        self._heading_targets: dict[tuple[str, str], DocsSymbolTarget] = {}
```

</details>

### ⚙️ Method `add`

```python
def add(self, keys: list[str], target: DocsSymbolTarget, heading_title: str) -> None
```

Register lookup keys and heading title for a documentation target.

<details>
<summary>Code:</summary>

```python
def add(self, keys: list[str], target: DocsSymbolTarget, heading_title: str) -> None:
        self._heading_targets[(target.docs_path, heading_title)] = target
        for key in keys:
            self._key_to_targets.setdefault(key, []).append(target)
```

</details>

### ⚙️ Method `add_module`

```python
def add_module(self, tree: ast.Module, docs_relative_path: Path, *, include_private: bool) -> None
```

Index all documented headings from one module in emit order.

<details>
<summary>Code:</summary>

```python
def add_module(self, tree: ast.Module, docs_relative_path: Path, *, include_private: bool) -> None:
        docs_path = docs_relative_path.as_posix()
        existing_ids: set[str] = set()
        for keys, heading_title in _iter_docs_heading_entries(tree, include_private=include_private):
            anchor = h.md.generate_id(heading_title, existing_ids)
            self.add(keys, DocsSymbolTarget(docs_path, anchor), heading_title)
```

</details>

### ⚙️ Method `resolve`

```python
def resolve(self, key: str) -> DocsSymbolTarget | None
```

Return the unique target for `key`, or `None` when missing or ambiguous.

<details>
<summary>Code:</summary>

```python
def resolve(self, key: str) -> DocsSymbolTarget | None:
        targets = self._key_to_targets.get(key)
        if not targets:
            return None
        unique = list(dict.fromkeys(targets))
        if len(unique) != 1:
            return None
        return unique[0]
```

</details>

### ⚙️ Method `target_for_heading`

```python
def target_for_heading(self, docs_path: str, heading_title: str) -> DocsSymbolTarget | None
```

Return the target registered for an exact heading title in a docs file.

<details>
<summary>Code:</summary>

```python
def target_for_heading(self, docs_path: str, heading_title: str) -> DocsSymbolTarget | None:
        return self._heading_targets.get((docs_path, heading_title))
```

</details>

## 🏛️ Class `DocsSymbolTarget`

```python
class DocsSymbolTarget(NamedTuple)
```

Resolved documentation target for an API symbol cross-link.

<details>
<summary>Code:</summary>

```python
class DocsSymbolTarget(NamedTuple):

    docs_path: str
    anchor: str
```

</details>

## 🔧 Function `check_python_docstring_markdown_errors`

```python
def check_python_docstring_markdown_errors(folder: Path | str, *, include_private: bool = True, show_progress: bool = True) -> list[str]
```

Check docstring Markdown typography for Python sources; errors point at `.py` locations.

Generates ephemeral docs (including private names when `include_private` is `True`), runs
MdChecker, and remaps findings to Python path/line/column. Does not modify the project.

Args:

- `folder` (`Path | str`): Project folder that contains a `src` subfolder.
- `include_private` (`bool`): Also check docstrings of private names. Defaults to `True`.
- `show_progress` (`bool`): Show a stderr progress bar when the stream is a TTY.
  Defaults to `True`.

Returns:

- `list[str]`: Error messages pointing at `.py` locations. Empty when `src` is missing.

Example:

```python
import harrix_pylib as h

errors = h.py.check_python_docstring_markdown_errors("D:/GitHub/harrix-pylib")
for error in errors:
    print(error)
```

<details>
<summary>Code:</summary>

```python
def check_python_docstring_markdown_errors(
    folder: Path | str,
    *,
    include_private: bool = True,
    show_progress: bool = True,
) -> list[str]:
    folder = Path(folder)
    src_folder = folder / "src"
    if not src_folder.is_dir():
        return []

    # File-level / front-matter / EOF / document-structure rules do not apply to
    # ephemeral docstring extracts (API docs have dense fences/headings by design).
    exclude_rules = {
        "H001",
        "H002",
        "H003",
        "H004",
        "H005",
        "H011",
        "H046",
        "H047",
        "H082",
        "H083",
        "H086",
        "H087",
        "H089",
        "H090",
        "H091",
        "H092",
        "H093",
    }
    checker = h.md_check.MdChecker()
    errors: list[str] = []

    py_files = [py_file for py_file in sorted(src_folder.rglob("*.py")) if _is_docs_python_file(py_file)]

    with tempfile.TemporaryDirectory(prefix="hsk-py-docstring-md-") as temp_dir:
        temp_root = Path(temp_dir)
        for py_file in h.file.iter_with_progress(py_files, show_progress=show_progress):
            with py_file.open(encoding="utf-8") as source_file:
                tree = ast.parse(source_file.read(), filename=str(py_file))
            if not _has_documented_entities(tree, include_private=include_private):
                continue

            content, line_map = generate_md_docs_content_with_source_map(py_file, include_private=include_private)
            relative = _docs_g_md_relative_path(py_file, src_folder)
            md_path = temp_root / relative
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(content, encoding="utf-8", newline="\n")

            errors.extend(
                remap_markdown_docs_error(error, line_map)
                for error in checker.check(md_path, exclude_rules=exclude_rules)
            )

    return errors
```

</details>

## 🔧 Function `create_uv_new_library`

```python
def create_uv_new_library(library_name: str, folder: Path | str, editor: str = 'code', cli_commands: str = '') -> str
```

Create a new library using uv, initializes it, and sets up necessary files.

Args:

- `library_name` (`str`): The name of the new library.
- `folder` (`Path | str`): The folder path where the library will be created.
- `editor` (`str`): The name of the text editor for opening the library. Example: `code`
- `cli_commands` (`str`): The section of CLI commands for `README.md`.

Returns:

- `str`: A string containing the result of the operations performed.

Structure `C:/projects/TestLibrary`:

```text
├─ .git
├─ .gitignore
├─ .python-version
├─ .venv
├─ pyproject.toml
├─ README.md
├─ .vscode
│  ├─ settings.json
│  └─ tasks.json
├─ src
│  └─ testlibrary
│     ├─ core.py
│     ├─ py.typed
│     └─ __init__.py
└─ uv.lock
```

<details>
<summary>Code:</summary>

```python
def create_uv_new_library(library_name: str, folder: Path | str, editor: str = "code", cli_commands: str = "") -> str:
    library_name = library_name.replace("_", "-").replace(" ", "-")
    library_name_under = library_name.replace("-", "_")
    folder_path = Path(folder)
    library_path = folder_path / library_name
    package_dir = library_path / "src" / library_name_under
    core_py = package_dir / "core.py"
    init_py = package_dir / "__init__.py"

    commands = f"""
        cd {folder_path}
        uv init --lib {library_name}
        cd {library_name}
        uv sync
        uv add --dev ruff
        uv add --dev pytest
        {_POWERSHELL_APPEND_RUFF}
    """

    res = h.dev.run_powershell_script(commands)

    core_py.write_text(
        '''def hello(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"
''',
        encoding="utf-8",
    )
    init_py.write_text(
        """from .core import hello

__all__ = ["hello"]
""",
        encoding="utf-8",
    )

    _write_vscode_dev_terminal_config(library_path)
    res += _open_project_in_editor(library_path, core_py, editor)

    return _append_readme_title_and_cli(library_path, library_name, cli_commands, res)
```

</details>

## 🔧 Function `create_uv_new_notebook`

```python
def create_uv_new_notebook(notebook_name: str, folder: Path | str, editor: str = 'code', cli_commands: str = '') -> str
```

Create a new Jupyter notebook project using uv and set up necessary files.

Args:

- `notebook_name` (`str`): The name of the new notebook project.
- `folder` (`Path | str`): The folder path where the project will be created.
- `editor` (`str`): The name of the text editor for opening the project. Example: `code`
- `cli_commands` (`str`): The section of CLI commands for `README.md`.

Returns:

- `str`: A string containing the result of the operations performed.

Structure `C:/projects/jupyter-notebook-01`:

```text
├─ .git
├─ .gitignore
├─ .python-version
├─ .venv
├─ pyproject.toml
├─ README.md
├─ notebook.ipynb
├─ .vscode
│  ├─ settings.json
│  └─ tasks.json
└─ uv.lock
```

<details>
<summary>Code:</summary>

```python
def create_uv_new_notebook(notebook_name: str, folder: Path | str, editor: str = "code", cli_commands: str = "") -> str:
    notebook_name = notebook_name.replace("_", "-").replace(" ", "-")
    folder_path = Path(folder)
    notebook_path = folder_path / notebook_name
    notebook_ipynb = notebook_path / "notebook.ipynb"
    main_py = notebook_path / "main.py"

    commands = f"""
        cd {folder_path}
        uv init {notebook_name}
        cd {notebook_name}
        uv sync
        uv add --dev ruff
        uv add --dev pytest
        uv add --dev jupyter
        uv add --dev ipykernel
        {_POWERSHELL_APPEND_RUFF}
    """

    res = h.dev.run_powershell_script(commands)

    if main_py.is_file():
        main_py.unlink()

    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ['print("Hello, World!")\n'],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.13.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    notebook_ipynb.write_text(json.dumps(notebook_content, indent=1) + "\n", encoding="utf-8")

    _write_vscode_dev_terminal_config(notebook_path)
    res += _open_project_in_editor(notebook_path, notebook_ipynb, editor)

    return _append_readme_title_and_cli(notebook_path, notebook_name, cli_commands, res)
```

</details>

## 🔧 Function `create_uv_new_project`

```python
def create_uv_new_project(project_name: str, folder: Path | str, editor: str = 'code', cli_commands: str = '') -> str
```

Create a new project using uv, initializes it, and sets up necessary files.

Args:

- `project_name` (`str`): The name of the new project.
- `folder` (`Path | str`): The folder path where the project will be created.
- `editor` (`str`): The name of the text editor for opening the project. Example: `code`
- `cli_commands` (`str`): The section of CLI commands for `README.md`.

Example of `cli_commands`:

```markdown
## CLI commands

CLI commands after installation.

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries.
- `ruff check --select I --fix` — sort imports.
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

Structure `C:/projects/TestProject`:

```text
├─ .git
├─ .gitignore
├─ .python-version
├─ .venv
├─ pyproject.toml
├─ README.md
├─ .vscode
│  ├─ settings.json
│  └─ tasks.json
├─ src
│  └─ testproject
│     ├─ main.py
│     └─ __init__.py
└─ uv.lock
```

<details>
<summary>Code:</summary>

```python
def create_uv_new_project(project_name: str, folder: Path | str, editor: str = "code", cli_commands: str = "") -> str:
    project_name = project_name.replace("_", "-").replace(" ", "-")
    project_name_under = project_name.replace("-", "_")
    folder_path = Path(folder)
    project_path = folder_path / project_name
    main_py = project_path / "src" / project_name_under / "main.py"

    commands = f"""
        cd {folder_path}
        uv init --package {project_name}
        cd {project_name}
        uv sync
        uv add --dev ruff
        uv add --dev pytest
        {_POWERSHELL_APPEND_RUFF}
    """

    res = h.dev.run_powershell_script(commands)

    main_py.parent.mkdir(parents=True, exist_ok=True)
    main_py.write_text('print("Hello, World!")\n', encoding="utf-8")

    _write_vscode_dev_terminal_config(project_path)
    res += _open_project_in_editor(project_path, main_py, editor)

    return _append_readme_title_and_cli(project_path, project_name, cli_commands, res)
```

</details>

## 🔧 Function `extract_functions_and_classes`

```python
def extract_functions_and_classes(filename: Path | str, *, is_add_link_demo: bool = True, domain: str = '', src_folder: Path | str | None = None, include_private: bool = False) -> str
```

Extract all classes and functions from a Python file and formats them into a Markdown list.

Args:

- `filename` (Path | str): The path to the Python file to be parsed.
- `is_add_link_demo` (`bool`): Whether to add a link to the documentation demo. Defaults to `True`.
- `domain` (`str`): The domain for the documentation link. Defaults to an empty string.
- `src_folder` (`Path | str | None`): The project's `src` folder used to build nested `.g.md` paths. Defaults to
  `None`.
- `include_private` (`bool`): Whether to include private names (starting with `_`, except magic dunders).
  Defaults to `False`.

Returns:

- `str`: Returns the markdown-formatted list of classes and functions.

Example output:

```text
### 📄 File `extract_functions_and_classes_before.py`

| Function/Class | Description |
|----------------|-------------|
| 🏛️ Class `Cat (Animal)` | Represents a domestic cat, inheriting from the `Animal` base class. |
| 🔧 `add` | Adds two integers. |
| 🔧 `multiply` | Multiples two integers. |
```

Example:

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

<details>
<summary>Code:</summary>

```python
def extract_functions_and_classes(
    filename: Path | str,
    *,
    is_add_link_demo: bool = True,
    domain: str = "",
    src_folder: Path | str | None = None,
    include_private: bool = False,
) -> str:
    filename = Path(filename)
    if src_folder is not None:
        docs_g_md_path = _docs_g_md_relative_path(filename, Path(src_folder))
    else:
        docs_g_md_path = Path(f"{filename.stem}.g.md")
    docs_path = docs_g_md_path.as_posix()

    with Path(filename).open(encoding="utf-8") as f:
        code = f.read()

    # Parse the code into an Abstract Syntax Tree (AST)
    tree = ast.parse(code, filename)
    dunder_all = _parse_dunder_all(tree)

    # List of entries for the table (source order)
    entries: list[tuple[str, str]] = []
    existing_ids: set[str] = set()
    seen_functions: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and _should_document_module_name(
            node.name, include_private=include_private, dunder_all=dunder_all
        ):
            base_classes_str = ", ".join(ast.unparse(base) for base in node.bases)
            docstring = ast.get_docstring(node)
            summary = _strip_trailing_linter_comments(docstring.splitlines()[0]) if docstring else ""
            if is_add_link_demo and domain:
                anchor = h.md.generate_id(f"🏛️ Class `{node.name}`", existing_ids)
                class_link = f"{domain}/blob/main/docs/{docs_path}#{anchor}"
                if base_classes_str:
                    name = f"🏛️ Class [`{node.name} ({base_classes_str})`]({class_link})"
                else:
                    name = f"🏛️ Class [`{node.name}`]({class_link})"
                entries.append((name, summary))
            else:
                heading_text = (
                    f"🏛️ Class `{node.name} ({base_classes_str})`" if base_classes_str else f"🏛️ Class `{node.name}`"
                )
                entries.append((heading_text, summary))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_overload(node):
                continue
            if node.name in seen_functions:
                continue
            if not _should_document_module_name(node.name, include_private=include_private, dunder_all=dunder_all):
                continue
            seen_functions.add(node.name)
            docstring = ast.get_docstring(node)
            summary = _strip_trailing_linter_comments(docstring.splitlines()[0]) if docstring else ""
            if is_add_link_demo and domain:
                heading_text = f"🔧 Function `{node.name}`"
                anchor = h.md.generate_id(heading_text, existing_ids)
                func_link = f"{domain}/blob/main/docs/{docs_path}#{anchor}"
                entries.append((f"🔧 [`{node.name}`]({func_link})", summary))
            else:
                entries.append((f"🔧 `{node.name}`", summary))
        elif _is_ast_type_alias(node):
            alias_name = _type_alias_name(node)
            if alias_name is None or not _should_document_module_data(
                alias_name,
                include_private=include_private,
                dunder_all=dunder_all,
            ):
                continue
            heading_text = f"🏷️ Type alias `{alias_name}`"
            if is_add_link_demo and domain:
                anchor = h.md.generate_id(heading_text, existing_ids)
                link = f"{domain}/blob/main/docs/{docs_path}#{anchor}"
                entries.append((f"🏷️ Type alias [`{alias_name}`]({link})", ""))
            else:
                entries.append((heading_text, ""))
        elif isinstance(node, ast.AnnAssign):
            target = _ann_assign_name(node)
            if target is None or target == "__all__":
                continue
            is_alias = _is_type_alias_annotation(node.annotation)
            if not _should_document_module_data(target, include_private=include_private, dunder_all=dunder_all):
                continue
            kind = "Type alias" if is_alias else "Constant"
            emoji = "🏷️" if is_alias else "📎"
            heading_text = f"{emoji} {kind} `{target}`"
            if is_add_link_demo and domain:
                anchor = h.md.generate_id(heading_text, existing_ids)
                link = f"{domain}/blob/main/docs/{docs_path}#{anchor}"
                entries.append((f"{emoji} {kind} [`{target}`]({link})", ""))
            else:
                entries.append((heading_text, ""))
        elif isinstance(node, ast.Assign):
            target = _simple_assign_name(node)
            if target is None or target == "__all__":
                continue
            if not _should_document_module_data(target, include_private=include_private, dunder_all=dunder_all):
                continue
            heading_text = f"📎 Constant `{target}`"
            if is_add_link_demo and domain:
                anchor = h.md.generate_id(heading_text, existing_ids)
                link = f"{domain}/blob/main/docs/{docs_path}#{anchor}"
                entries.append((f"📎 Constant [`{target}`]({link})", ""))
            else:
                entries.append((heading_text, ""))

    if not entries:
        return ""

    # Create Markdown table
    output_lines = []
    output_lines.append(f"### 📄 File `{filename.name}`\n")
    if is_add_link_demo:
        link = f"{domain}/blob/main/docs/{docs_path}"
        output_lines.append(f"Doc: [{docs_path}]({link})\n")
    output_lines.append("| Function/Class | Description |")
    output_lines.append("|----------------|-------------|")

    for name, description in entries:
        output_lines.append(f"| {name} | {description} |")

    # Combine all lines and return the result
    return "\n".join(output_lines)
```

</details>

## 🔧 Function `generate_md_docs`

```python
def generate_md_docs(folder: Path | str, beginning_of_md: str, domain: str, *, include_private: bool = False, docs_folder: Path | str | None = None, update_readme: bool = True, copy_root_md: bool = True) -> str
```

Generate documentation for all Python files within a given project folder.

Args:

- `folder` (`Path | str`): The path to the project folder, can be either a `Path` object or a string. Defaults to
  the current directory if not specified.
- `beginning_of_md` (`str`): The content to prepend to each documentation file. This could include headers
  or other Markdown formatting.
- `domain` (`str`): The domain or context in which the project is used, which might influence how
  documentation is generated or formatted.
- `include_private` (`bool`): Whether to include private names (starting with `_`, except magic dunders).
  Defaults to `False`.
- `docs_folder` (`Path | str | None`): Output folder for generated `.g.md` files. Defaults to `folder / "docs"`.
- `update_readme` (`bool`): Whether to update `## 📚 List of functions` in README. Defaults to `True`.
- `copy_root_md` (`bool`): Whether to copy root `*.md` files into the docs folder. Defaults to `True`.

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

<details>
<summary>Code:</summary>

```python
def generate_md_docs(
    folder: Path | str,
    beginning_of_md: str,
    domain: str,
    *,
    include_private: bool = False,
    docs_folder: Path | str | None = None,
    update_readme: bool = True,
    copy_root_md: bool = True,
) -> str:
    result_lines = []
    folder = Path(folder)

    output_docs = Path(docs_folder) if docs_folder is not None else folder / "docs"

    # Remove entire docs folder and recreate it
    if output_docs.exists():
        shutil.rmtree(output_docs)
        result_lines.append("Removed entire docs folder")

    output_docs.mkdir(parents=True, exist_ok=True)
    result_lines.append("Created clean docs folder")

    list_funcs_all = ""
    src_folder = folder / "src"
    documented_modules: list[tuple[Path, Path, ast.Module]] = []

    for filename in src_folder.rglob("*.py"):
        if not _is_docs_python_file(filename):
            continue

        with filename.open(encoding="utf-8") as source_file:
            source_code = source_file.read()
        tree = ast.parse(source_code, filename)

        if not _has_documented_entities(tree, include_private=include_private):
            skip_reason = "no documented API" if include_private else "no public API"
            result_lines.append(f"File {filename.name} is skipped ({skip_reason}).")
            continue

        documented_modules.append((filename, _docs_g_md_relative_path(filename, src_folder), tree))

    symbol_index = _build_docs_symbol_index(documented_modules, include_private=include_private)

    for filename, docs_relative_path, _tree in documented_modules:
        list_funcs = h.py.extract_functions_and_classes(
            filename,
            is_add_link_demo=True,
            domain=domain,
            src_folder=src_folder,
            include_private=include_private,
        )
        docs = generate_md_docs_content(
            filename,
            include_private=include_private,
            symbol_index=symbol_index,
            docs_relative_path=docs_relative_path,
        )

        filename_docs = output_docs / docs_relative_path

        # Create parent directories if they don't exist
        filename_docs.parent.mkdir(parents=True, exist_ok=True)

        final_content = _prepend_markdown_header(beginning_of_md, docs)
        final_content = h.md.generate_toc_with_links_content(final_content)
        final_content = h.md.generate_image_captions_content(final_content)
        filename_docs.write_text(final_content, encoding="utf-8", newline="\n")

        list_funcs_all += list_funcs + "\n\n"

        result_lines.append(f"File {filename.name} is processed.")

    min_count_lines = 2
    if len(list_funcs_all.splitlines()) > min_count_lines:
        list_funcs_all = list_funcs_all[:-1]

    if update_readme:
        try:
            h.md.replace_section(folder / "README.md", list_funcs_all, "## 📚 List of functions")
        except FileNotFoundError:
            result_lines.append("❗ Don't find `## List of functions`.")
        except ValueError:
            result_lines.append("❗ Don't find `## List of functions`.")

    if not copy_root_md:
        return "\n".join(result_lines)

    # Copy all MD files from root to docs folder
    for md_file in folder.glob("*.md"):
        if md_file.is_file() and not md_file.name.startswith("."):
            # Special handling for README.md - create index.g.md
            if md_file.name.upper() == "README.MD":
                original_content = md_file.read_text(encoding="utf-8")
                final_content = _prepend_markdown_header(beginning_of_md, original_content)
                final_content = h.md.generate_toc_with_links_content(final_content)
                final_content = h.md.generate_image_captions_content(final_content)

                (output_docs / "index.g.md").write_text(final_content, encoding="utf-8", newline="\n")
                result_lines.append(f"File {md_file.name} copied as index.g.md")
            else:
                # Convert filename to lowercase for other MD files and add .g.md
                target_filename = md_file.stem.lower() + ".g.md"
                target_path = output_docs / target_filename

                # Read original content and add beginning_of_md
                original_content = md_file.read_text(encoding="utf-8")
                final_content = _prepend_markdown_header(beginning_of_md, original_content)

                # Apply additional processing
                final_content = h.md.generate_toc_with_links_content(final_content)
                final_content = h.md.generate_image_captions_content(final_content)

                # Write to docs folder
                target_path.write_text(final_content, encoding="utf-8", newline="\n")
                result_lines.append(f"File {md_file.name} copied as {target_filename}")

    return "\n".join(result_lines)
```

</details>

## 🔧 Function `generate_md_docs_content`

```python
def generate_md_docs_content(file_path: Path | str, *, include_private: bool = False, symbol_index: DocsSymbolIndex | None = None, docs_relative_path: Path | str | None = None) -> str
```

Generate Markdown documentation for a single Python file.

Args:

- `file_path` (`Path | str`): The path to the Python file to be documented, can be either
  a `Path` object or a string.
- `include_private` (`bool`): Whether to include private names (starting with `_`, except magic dunders).
  Defaults to `False`.
- `symbol_index` (`DocsSymbolIndex | None`): Optional project-wide symbol index for docstring
  cross-links. When omitted, an index is built from this file only.
- `docs_relative_path` (`Path | str | None`): Relative `.g.md` path under `docs/` for this file.
  Inferred from a `src/` parent when omitted.

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

```python
def generate_md_docs_content(
    file_path: Path | str,
    *,
    include_private: bool = False,
    symbol_index: DocsSymbolIndex | None = None,
    docs_relative_path: Path | str | None = None,
) -> str:
    content, _line_map = generate_md_docs_content_with_source_map(
        file_path,
        include_private=include_private,
        symbol_index=symbol_index,
        docs_relative_path=docs_relative_path,
    )
    return content
```

</details>

## 🔧 Function `generate_md_docs_content_with_source_map`

```python
def generate_md_docs_content_with_source_map(file_path: Path | str, *, include_private: bool = False, symbol_index: DocsSymbolIndex | None = None, docs_relative_path: Path | str | None = None) -> tuple[str, list[DocsSourceLoc | None]]
```

Generate Markdown docs for a Python file and a per-line map to Python source.

Each entry in the returned map corresponds to one line of the Markdown content
(1-based Markdown line `i` maps to `line_map[i - 1]`).

Args:

- `file_path` (`Path | str`): Path to the Python file.
- `include_private` (`bool`): Also document private names. Defaults to `False`.
- `symbol_index` (`DocsSymbolIndex | None`): Optional project-wide symbol index for docstring
  cross-links. When omitted, an index is built from this file only.
- `docs_relative_path` (`Path | str | None`): Relative `.g.md` path under `docs/` for this file.
  Inferred from a `src/` parent when omitted.

Returns:

- `tuple[str, list[DocsSourceLoc | None]]`: Markdown content and the per-line source map.
  A map entry is `None` when the line has no Python counterpart.

Example:

```python
import harrix_pylib as h

content, line_map = h.py.generate_md_docs_content_with_source_map("src/harrix_pylib/progress.py")
print(line_map[0])
```

<details>
<summary>Code:</summary>

````python
def generate_md_docs_content_with_source_map(
    file_path: Path | str,
    *,
    include_private: bool = False,
    symbol_index: DocsSymbolIndex | None = None,
    docs_relative_path: Path | str | None = None,
) -> tuple[str, list[DocsSourceLoc | None]]:
    file_path = Path(file_path).resolve()
    with file_path.open(encoding="utf-8") as f:
        source = f.read()
    source_lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    docs_rel = Path(docs_relative_path) if docs_relative_path is not None else _infer_docs_g_md_relative_path(file_path)
    docs_path_str = docs_rel.as_posix()
    if symbol_index is None:
        symbol_index = DocsSymbolIndex()
        symbol_index.add_module(tree, docs_rel, include_private=include_private)

    out_lines: list[str] = []
    line_map: list[DocsSourceLoc | None] = []

    def emit(line: str, loc: DocsSourceLoc | None) -> None:
        out_lines.append(line)
        line_map.append(loc)

    def emit_blank(loc: DocsSourceLoc | None = None) -> None:
        emit("", loc)

    def emit_structural(line: str, entity_loc: DocsSourceLoc) -> None:
        emit(line, entity_loc)

    def emit_multiline(text: str, base: DocsSourceLoc) -> None:
        parts = text.splitlines()
        if not parts:
            emit("", base)
            return
        for offset, part in enumerate(parts):
            emit(part, DocsSourceLoc(base.path, base.line + offset, base.col))

    def entity_loc(node: ast.AST) -> DocsSourceLoc:
        return DocsSourceLoc(file_path, getattr(node, "lineno", 1) or 1, (getattr(node, "col_offset", 0) or 0) + 1)

    def docstring_content_locs(node: ast.AST, docstring: str) -> list[DocsSourceLoc]:
        """Return per-line locs at the start of each docstring content line in source."""
        expr = _docstring_expr(node)
        parts = docstring.splitlines() or [""]
        if expr is None:
            fallback = entity_loc(node)
            return [fallback for _ in parts]

        first_src = source_lines[expr.lineno - 1].rstrip("\r\n")
        opener_only = bool(re.match(r"^\s*(\"\"\"|''')\s*$", first_src))
        line0 = expr.lineno + (1 if opener_only else 0)

        locs: list[DocsSourceLoc] = []
        for offset, part in enumerate(parts):
            py_line = line0 + offset
            if py_line < 1 or py_line > len(source_lines):
                locs.append(DocsSourceLoc(file_path, expr.lineno, (expr.col_offset or 0) + 1))
                continue
            src = source_lines[py_line - 1].rstrip("\r\n")
            if part:
                idx = src.find(part)
                if idx < 0:
                    idx = len(src) - len(src.lstrip())
            else:
                idx = len(src) - len(src.lstrip())
            locs.append(DocsSourceLoc(file_path, py_line, max(1, idx + 1)))
        return locs

    def get_node_code(node: ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef) -> tuple[str, int]:
        """Return code without docstring and the 1-based first source line of returned code."""
        start_line = node.lineno - 1
        end_line = node.end_lineno
        if end_line is None:
            return "", node.lineno

        node_lines = source_lines[start_line:end_line]
        code_start_lineno = node.lineno

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring_node = node.body[0]
            docstring_start = docstring_node.lineno - 1
            docstring_end = docstring_node.end_lineno
            if docstring_end is not None:
                docstring_line_indexes = set(range(docstring_start, docstring_end))
                kept: list[tuple[int, str]] = [
                    (i, line) for i, line in enumerate(node_lines, start=start_line) if i not in docstring_line_indexes
                ]
                if kept:
                    code_start_lineno = kept[0][0] + 1
                    node_lines = [line for _, line in kept]
                else:
                    node_lines = []

        return "".join(node_lines), code_start_lineno

    def append_fenced_code(content: str, code_start_lineno: int, fallback: DocsSourceLoc) -> None:
        open_fence, close_fence = _fence_for_content(content)
        emit_structural(open_fence, fallback)
        stripped = content.strip("\n")
        if stripped:
            emit_multiline(stripped, DocsSourceLoc(file_path, code_start_lineno, 1))
        emit_structural(close_fence, fallback)
        emit_blank(fallback)

    def emit_docstring_or_placeholder(
        node: ast.AST,
        docstring: str | None,
        fallback: DocsSourceLoc,
        current_target: DocsSymbolTarget | None = None,
    ) -> None:
        if docstring:
            locs = docstring_content_locs(node, docstring)
            parts = docstring.splitlines() or [""]
            in_fence = False
            for part, loc in zip(parts, locs, strict=True):
                stripped_left = part.lstrip()
                if stripped_left.startswith("```"):
                    in_fence = not in_fence
                    emit(part, loc)
                    continue
                if in_fence:
                    emit(part, loc)
                    continue
                text = _strip_trailing_linter_comments(part)
                text = _linkify_docs_symbol_line(
                    text,
                    index=symbol_index,
                    current_docs_path=docs_path_str,
                    current_target=current_target,
                )
                emit(text, loc)
            emit_blank(locs[-1] if locs else fallback)
        else:
            emit_structural("_No docstring provided._", fallback)
            emit_blank(fallback)

    def emit_callable_docs(
        heading: str,
        signature: str,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        docstring: str | None,
    ) -> None:
        loc = entity_loc(node)
        emit_structural(heading, loc)
        emit_blank(loc)
        code, code_start = get_node_code(node)
        append_fenced_code(signature, loc.line, loc)
        heading_title = heading.lstrip("#").strip()
        current_target = symbol_index.target_for_heading(docs_path_str, heading_title)
        emit_docstring_or_placeholder(node, docstring, loc, current_target)
        emit_structural("<details>", loc)
        emit_structural("<summary>Code:</summary>", loc)
        emit_blank(loc)
        append_fenced_code(code.strip(), code_start, loc)
        emit_structural("</details>", loc)
        emit_blank(loc)

    def emit_declaration_docs(heading: str, signature: str, node: ast.AST, note: str) -> None:
        loc = entity_loc(node)
        emit_structural(heading, loc)
        emit_blank(loc)
        append_fenced_code(signature, loc.line, loc)
        emit_structural(note, loc)
        emit_blank(loc)

    def emit_function_docs(
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        heading_level: int,
        *,
        kind: str,
        overload_counts: dict[str, int],
        other_counts: dict[str, int],
    ) -> None:
        hashes = "#" * heading_level
        heading_name = _next_callable_heading_name(
            func_node, overload_counts=overload_counts, other_counts=other_counts
        )
        emit_callable_docs(
            f"{hashes} {kind} `{heading_name}`",
            _get_function_signature(func_node),
            func_node,
            None if _is_overload(func_node) else ast.get_docstring(func_node),
        )

    def emit_class_docs(class_node: ast.ClassDef, heading_level: int, qualified_name: str) -> None:
        class_hashes = "#" * heading_level
        emit_callable_docs(
            f"{class_hashes} 🏛️ Class `{qualified_name}`",
            _get_class_signature(class_node),
            class_node,
            ast.get_docstring(class_node),
        )
        member_level = heading_level + 1
        overload_counts: dict[str, int] = {}
        other_counts: dict[str, int] = {}
        for body_node in class_node.body:
            if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _should_document_name(
                body_node.name, include_private=include_private
            ):
                emit_function_docs(
                    body_node,
                    member_level,
                    kind="⚙️ Method",
                    overload_counts=overload_counts,
                    other_counts=other_counts,
                )
            elif isinstance(body_node, ast.ClassDef) and _should_document_name(
                body_node.name, include_private=include_private
            ):
                emit_class_docs(body_node, member_level, f"{qualified_name}.{body_node.name}")

    dunder_all = _parse_dunder_all(tree)
    file_loc = DocsSourceLoc(file_path, 1, 1)
    emit_structural(f"# 📄 File `{file_path.name}`", file_loc)
    emit_blank(file_loc)

    module_overload_counts: dict[str, int] = {}
    module_other_counts: dict[str, int] = {}

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if not _should_document_module_name(node.name, include_private=include_private, dunder_all=dunder_all):
                continue
            emit_class_docs(node, heading_level=2, qualified_name=node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _should_document_module_name(node.name, include_private=include_private, dunder_all=dunder_all):
                continue
            emit_function_docs(
                node,
                heading_level=2,
                kind="🔧 Function",
                overload_counts=module_overload_counts,
                other_counts=module_other_counts,
            )
        elif _is_ast_type_alias(node):
            alias_name = _type_alias_name(node)
            if alias_name is None or not _should_document_module_data(
                alias_name,
                include_private=include_private,
                dunder_all=dunder_all,
            ):
                continue
            emit_declaration_docs(
                f"## 🏷️ Type alias `{alias_name}`",
                ast.unparse(node),
                node,
                "_No docstring provided._",
            )
        elif isinstance(node, ast.AnnAssign):
            target = _ann_assign_name(node)
            if target is None or target == "__all__":
                continue
            is_alias = _is_type_alias_annotation(node.annotation)
            if not _should_document_module_data(target, include_private=include_private, dunder_all=dunder_all):
                continue
            heading = f"## 🏷️ Type alias `{target}`" if is_alias else f"## 📎 Constant `{target}`"
            emit_declaration_docs(heading, ast.unparse(node), node, "_No docstring provided._")
        elif isinstance(node, ast.Assign):
            target = _simple_assign_name(node)
            if target is None or target == "__all__":
                continue
            if not _should_document_module_data(target, include_private=include_private, dunder_all=dunder_all):
                continue
            emit_declaration_docs(
                f"## 📎 Constant `{target}`",
                ast.unparse(node),
                node,
                "_No docstring provided._",
            )

    while out_lines and out_lines[-1] == "":
        out_lines.pop()
        line_map.pop()

    return "\n".join(out_lines), line_map
````

</details>

## 🔧 Function `is_python_project`

```python
def is_python_project(folder_path: Path | str) -> bool
```

Return whether `folder_path` looks like a Python project (`pyproject.toml`).

Args:

- `folder_path` (`Path | str`): Folder to inspect.

Returns:

- `bool`: `True` when the folder contains `pyproject.toml`.

Example:

```python
import harrix_pylib as h

assert h.py.is_python_project("C:/projects/harrix-pylib")
```

<details>
<summary>Code:</summary>

```python
def is_python_project(folder_path: Path | str) -> bool:
    return (Path(folder_path) / "pyproject.toml").is_file()
```

</details>

## 🔧 Function `lint_and_fix_python_code`

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
```

</details>

## 🔧 Function `remap_markdown_docs_error`

```python
def remap_markdown_docs_error(error: str, line_map: list[DocsSourceLoc | None]) -> str
```

Rewrite a MdChecker error to the corresponding Python source location.

Args:

- `error` (`str`): Error message produced by MdChecker for generated Markdown docs.
- `line_map` (`list[DocsSourceLoc | None]`): Per-line map from
  [`generate_md_docs_content_with_source_map`](#-function-generate_md_docs_content_with_source_map).

Returns:

- `str`: Error with the location rewritten to the `.py` file, or the original message
  when it cannot be remapped.

Example:

```python
import harrix_pylib as h

content, line_map = h.py.generate_md_docs_content_with_source_map("src/harrix_pylib/progress.py")
print(h.py.remap_markdown_docs_error("progress.g.md:10:1: H021 Message", line_map))
```

<details>
<summary>Code:</summary>

```python
def remap_markdown_docs_error(error: str, line_map: list[DocsSourceLoc | None]) -> str:
    match = _MD_DOCS_CODE_RE.fullmatch(error.strip("\n"))
    if match is None:
        return error

    code = match.group("code")
    message = match.group("message")
    location = match.group("location")
    parts = location.split(":")
    if len(parts) < _MIN_ERROR_LOCATION_PARTS:
        return error

    md_col = 1
    try:
        if parts[-1].isdigit() and len(parts) >= _ERROR_LOCATION_WITH_COLUMN_PARTS and parts[-2].isdigit():
            md_col = int(parts[-1])
            md_line = int(parts[-2])
        elif parts[-1].isdigit():
            md_line = int(parts[-1])
        else:
            return error
    except ValueError:
        return error

    if md_line < 1 or md_line > len(line_map):
        return error
    loc = line_map[md_line - 1]
    if loc is None:
        return error

    py_col = max(1, loc.col + md_col - 1)
    return f"{loc.path}:{loc.line}:{py_col}: {code}\n  {message}"
```

</details>

## 🔧 Function `sort_py_code`

```python
def sort_py_code(filename: Path | str, *, is_use_ruff_format: bool = True) -> str
```

Sorts the Python code in the given file by organizing classes, functions, and statements.

This function reads a Python file, parses it, sorts classes and functions alphabetically,
and ensures that class attributes, methods, and other statements within classes are ordered
in a structured manner. The sorted code is then written back to the file.

Args:

- `filename` (`str`): The path to the Python file that needs sorting.
- `is_use_ruff_format` (`bool`, optional): If `True`, use Ruff to format the sorted code. Defaults to `True`.

Returns:

- `None`: This function does not return a value, it modifies the file in place.

Note:

- This function uses `libcst` for parsing and manipulating Python ASTs.
- Sorting prioritizes initial non-class, non-function statements, followed by sorted classes,
  then sorted functions, and finally any trailing statements.
- Within classes, `_init__` method is placed first among methods, followed by other methods
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

    def _init__(self, x=0, y=0):
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
    def _init__(self, x=0, y=0):
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

<details>
<summary>Code:</summary>

```python
def sort_py_code(filename: Path | str, *, is_use_ruff_format: bool = True) -> str:

    def _get_sort_key(name: str) -> tuple[int, str]:
        r"""Return a sort key for function/method names.

        Priority:
        0\. _init_\_ method — highest priority

        1. Other special methods (double underscore)
        2. Regular methods/functions
        3. Private methods/functions (single underscore)

        """
        if name == "_init__":
            return (0, name)  # _init__ always first
        if name.startswith("__") and name.endswith("__"):
            return (1, name)  # Other special methods like _str__, _repr__
        if name.startswith("_") and not name.startswith("__"):
            return (3, name)  # Private methods/functions with single underscore
        return (2, name)  # Regular methods/functions

    def _decorator_dependency_source_name(decorator_expr: cst.BaseExpression) -> str | None:
        """If decorator looks like @Name.attr(…) then return Name; else `None`.

        This keeps runtime name resolution stable for decorator registration patterns
        (e.g. Click): `@group.command(...)` requires `group` to exist at import time.

        """
        expr: cst.BaseExpression = decorator_expr
        if isinstance(expr, cst.Call):
            expr = expr.func
        if not isinstance(expr, cst.Attribute):
            return None
        if not isinstance(expr.value, cst.Name):
            return None
        return expr.value.value

    def _toposort_stable(names: list[str], edges: dict[str, set[str]]) -> list[str]:
        """Stable topological sort using `names` as tie-breaker.

        If a cycle exists, the remaining nodes are appended in the original order.

        """
        index: dict[str, int] = {name: i for i, name in enumerate(names)}

        indegree: dict[str, int] = dict.fromkeys(names, 0)
        for src, dsts in edges.items():
            if src not in indegree:
                continue
            for dst in dsts:
                if dst in indegree:
                    indegree[dst] += 1

        ready: list[tuple[int, str]] = [(index[name], name) for name in names if indegree[name] == 0]
        ready.sort()

        out: list[str] = []
        while ready:
            _, node = ready.pop(0)
            out.append(node)
            for dst in edges.get(node, set()):
                if dst not in indegree:
                    continue
                indegree[dst] -= 1
                if indegree[dst] == 0:
                    bisect.insort(ready, (index[dst], dst))

        if len(out) != len(names):
            out_set = set(out)
            out.extend([name for name in names if name not in out_set])

        return out

    with Path(filename).open(encoding="utf-8") as f:
        code: str = f.read()

    module: cst.Module = cst.parse_module(code)

    # Split the module content into initial statements, final statements, classes, and functions
    initial_statements: list[cst.BaseStatement] = []
    final_statements: list[cst.BaseStatement] = []
    class_defs: list[cst.ClassDef] = []
    func_defs: list[cst.FunctionDef] = []
    main_def: cst.FunctionDef | None = None

    state: str = "initial"

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            state = "collecting"
            class_defs.append(stmt)
        elif isinstance(stmt, cst.FunctionDef):
            state = "collecting"
            if stmt.name.value == "main":
                main_def = stmt
            else:
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

    # Preserve decorator dependencies between top-level functions.
    # Example: @markdown_group.command(...) requires markdown_group() to be defined before the decorated function.
    click_decorator_methods: set[str] = {"command", "group", "callback"}
    func_names: set[str] = {f.name.value for f in func_defs_sorted}
    deps_edges: dict[str, set[str]] = {name: set() for name in func_names}
    for func_def in func_defs_sorted:
        current_name = func_def.name.value
        for deco in func_def.decorators:
            base_name = _decorator_dependency_source_name(deco.decorator)
            if base_name is None:
                continue

            deco_expr: cst.BaseExpression = deco.decorator
            if isinstance(deco_expr, cst.Call):
                deco_expr = deco_expr.func
            if not isinstance(deco_expr, cst.Attribute) or not isinstance(deco_expr.attr, cst.Name):
                continue
            if deco_expr.attr.value not in click_decorator_methods:
                continue

            if base_name in func_names and base_name != current_name:
                deps_edges.setdefault(base_name, set()).add(current_name)

    if any(dsts for dsts in deps_edges.values()):
        base_order = [f.name.value for f in func_defs_sorted]
        sorted_names = _toposort_stable(base_order, deps_edges)
        name_to_def: dict[str, cst.FunctionDef] = {f.name.value: f for f in func_defs_sorted}
        func_defs_sorted = [name_to_def[name] for name in sorted_names if name in name_to_def]

    if main_def is not None:
        func_defs_sorted.append(main_def)

    # Assemble the new module body
    new_module_body: list[cst.BaseStatement] = (
        initial_statements + sorted_class_defs + func_defs_sorted + final_statements
    )

    new_module: cst.Module = module.with_changes(body=new_module_body)

    # Convert the module back to code
    new_code: str = new_module.code

    if is_use_ruff_format:
        new_code = lint_and_fix_python_code(new_code)
        if new_code == code:
            return "File is not changed."
    # When skipping per-file ruff, compare against libcst round-trip so
    # on-disk ruff formatting alone does not force a rewrite.
    elif new_code == module.code:
        return "File is not changed."

    # Write the sorted code back to the file (LF endings; avoid Windows CRLF translation).
    Path(filename).write_text(new_code, encoding="utf-8", newline="\n")
    return f"✅ File {filename} sorted."
```

</details>

## 🔧 Function `validate_uv_project_name`

```python
def validate_uv_project_name(name: str) -> str | None
```

Return an error message when `name` is invalid for a uv project, otherwise `None`.

Args:

- `name` (`str`): Project or library name to validate.

Returns:

- `str | None`: Error text, or `None` when the name is valid.

Example:

```python
import harrix_pylib as h

assert h.py.validate_uv_project_name("my-library") is None
assert h.py.validate_uv_project_name("bad name") == "Name must not contain spaces."
```

<details>
<summary>Code:</summary>

```python
def validate_uv_project_name(name: str) -> str | None:
    stripped = name.strip()
    if not stripped:
        return "Name must not be empty."
    if " " in name:
        return "Name must not contain spaces."
    if not re.fullmatch(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", stripped):
        return "Name must contain only English letters, digits, hyphens, and underscores."
    return None
```

</details>
