from pathlib import Path

import harrix_pylib as h


def py_create_uv_new_project(project_name: str, path: str | Path, editor: str = "code", cli_commands: str = "") -> str:
    """
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
    """
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
