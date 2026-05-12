"""Functions for development working."""

import inspect
import json
import os
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import harrix_pylib as h


def config_load(filename: str, *, is_temp: bool = False) -> dict:
    """Load configuration from a JSON file.

    Args:

    - `filename` (`str`): Path to the JSON configuration file. Defaults to `None`.
    - `is_temp` (`bool`): If `True`, load the temporary config file (`config-temp.json`)
      instead of the main config file. Defaults to `False`.

    Returns:

    - `dict`: Configuration loaded from the file.

    Examples:

    ```python
    import harrix-pylib as h

    config = h.dev.config_load("config.json")
    ```

    ```python
    from pathlib import Path

    import harrix_pylib as h

    root_path = h.dev.get_project_root()
    Path(root_path / "config.json").write_text('{"pi": 3.14}', encoding="utf8")

    config = h.dev.config_load("config.json")
    print(config["pi"])  # 3.14
    ```

    ```python
    import harrix_pylib as h

    config = h.dev.config_load("config.json", is_temp=True)
    ```

    """
    if is_temp:
        path_obj = Path(filename)
        temp_filename = f"{path_obj.stem}-temp{path_obj.suffix}"
        filename = str(path_obj.parent / temp_filename) if path_obj.parent != Path() else temp_filename

    config_file = Path(get_project_root()) / filename
    with config_file.open("r", encoding="utf-8") as file:
        config = json.load(file)

    def process_snippet(value: object) -> object:
        if isinstance(value, str) and value.startswith("snippet:"):
            snippet_path = Path(get_project_root()) / value.split("snippet:", 1)[1].strip()
            if not snippet_path.exists():
                return ""
            with snippet_path.open("r", encoding="utf-8") as snippet_file:
                return snippet_file.read()
        return value

    for key, value in config.items():
        if isinstance(value, dict):
            config[key] = {k: process_snippet(v) for k, v in value.items()}
        else:
            config[key] = process_snippet(value)

    return config


def config_save(config: dict, filename: str, *, is_temp: bool = False) -> None:
    """Save configuration to a JSON file.

    Args:

    - `config` (`dict`): Configuration dictionary to save.
    - `filename` (`str`): Path to the JSON configuration file.
    - `is_temp` (`bool`): If `True`, save to the temporary config file (`config-temp.json`)
      instead of the main config file. Defaults to `False`.

    Examples:

    ```python
    import harrix_pylib as h

    config = {"path_github": "C:/GitHub"}
    h.dev.config_save(config, "config.json")
    ```

    ```python
    from pathlib import Path

    import harrix_pylib as h

    config = {"pi": 3.14}
    h.dev.config_save(config, "config.json")
    ```

    ```python
    import harrix_pylib as h

    config = {"path_github": "C:/GitHub/Temp"}
    h.dev.config_save(config, "config.json", is_temp=True)
    ```

    """
    if is_temp:
        path_obj = Path(filename)
        temp_filename = f"{path_obj.stem}-temp{path_obj.suffix}"
        filename = str(path_obj.parent / temp_filename) if path_obj.parent != Path() else temp_filename

    config_file = Path(get_project_root()) / filename
    with config_file.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)


def config_update_value(key: str, value: object, filename: str, *, is_temp: bool = False) -> None:
    """Update a single configuration value and save it to a JSON file.

    This function loads the configuration file, updates the specified key with the new value,
    and saves the updated configuration back to the file.

    Args:

    - `key` (`str`): Configuration key to update. Supports nested keys using dot notation
      (e.g., `"section.key"` for nested dictionaries).
    - `value` (`object`): New value to set for the configuration key.
    - `filename` (`str`): Path to the JSON configuration file.
    - `is_temp` (`bool`): If `True`, update the temporary config file (`config-temp.json`)
      instead of the main config file. Defaults to `False`.

    Examples:

    ```python
    import harrix_pylib as h

    h.dev.config_update_value("path_github", "C:/GitHub/New", "config.json")
    ```

    ```python
    import harrix_pylib as h

    h.dev.config_update_value("version", "2.0", "config.json")
    ```

    ```python
    import harrix_pylib as h

    # Update nested key
    h.dev.config_update_value("database.host", "localhost", "config.json")
    ```

    ```python
    import harrix_pylib as h

    h.dev.config_update_value("path_github", "C:/GitHub/Temp", "config.json", is_temp=True)
    ```

    """
    config = config_load(filename, is_temp=is_temp)

    # Handle nested keys (e.g., "section.key")
    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}
        current = current[k]

    # Set the value
    current[keys[-1]] = value

    # Save the updated config
    config_save(config, filename, is_temp=is_temp)


def get_project_root() -> Path:
    """Find the root folder of the current project.

    This function traverses up the folder tree from the caller's file location looking for a folder
    containing a `.venv` folder, which is assumed to indicate the project root. The function
    automatically detects the file that called it, making it work correctly both with PyPI
    installations and editable installs.

    Returns:

    - `Path`: The path to the project's root folder.

    Example:

    ```python
    import harrix_pylib as h

    root_path = h.dev.get_project_root()
    print(root_path)
    ```

    """
    # Get the current stack frames
    current_frame = inspect.currentframe()
    if current_frame is None:
        # Fallback when frame inspection is not available
        return Path.cwd()

    # Walk through the call stack to find the first frame outside harrix_pylib
    frame = current_frame.f_back
    while frame:
        caller_file = Path(frame.f_globals["__file__"]).resolve()

        # If the caller is not from harrix_pylib, use this frame
        if "harrix_pylib" not in str(caller_file):
            break

        frame = frame.f_back

    # If we didn't find a frame outside harrix_pylib, use the last frame
    if frame is None:
        frame = current_frame.f_back
        if frame is None:
            # Fallback when caller frame is not available
            return Path.cwd()
        caller_file = Path(frame.f_globals["__file__"]).resolve()

    # Traverse up the folder tree looking for .venv
    for parent in caller_file.parents:
        if (parent / ".venv").exists():
            return parent

    # Fallback to caller file's parent if no .venv found
    return caller_file.parent


def run_command(
    command: str,
    *,
    is_shell: bool = True,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
) -> str:
    """Run a console command and return its output.

    This function executes a console command using the system's default shell
    and returns the combined output (stdout + stderr).

    Args:

    - `command` (`str`): The command to execute.
    - `is_shell` (`bool`): Whether to run the command through the shell. Defaults to `True`.
    - `cwd` (`str | None`): Working directory for the command. Defaults to `None`.
    - `env` (`dict[str, str] | None`): Environment variables. Defaults to `None`.
    - `timeout` (`float | None`): Timeout in seconds. Defaults to `None`.

    Returns:

    - `str`: Combined output and error messages from the command execution.

    Example:

    ```python
    import harrix_pylib as h

    result = h.dev.run_command("python --version")
    print(result)

    result = h.dev.run_command("python --version && pip --version")
    print(result)

    result = h.dev.run_command("ping google.com", timeout=5)
    print(result)
    ```

    """
    try:
        process = subprocess.run(
            command,
            shell=is_shell,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd,
            env=env,
            timeout=timeout,
            check=False,
        )

        # Combine stdout and stderr, filter out empty lines (streams may be None on some platforms).
        output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
        return "\n".join(filter(None, output_parts))

    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {e!s}"


def run_powershell_script(commands: str) -> str:
    r"""Run a PowerShell script with the given commands.

    This function executes a PowerShell script by concatenating multiple commands into a single command string,
    which is then run through the `subprocess` module. It ensures that the output encoding is set to UTF-8.

    Args:

    - `commands` (`str`): A string containing PowerShell commands to execute.

    Returns:

    - `str`: Combined output and error messages from the PowerShell execution.

    Examples:

    ```python
    import harrix_pylib as h

    result_output = h.dev.run_powershell_script("python --version")
    print(result_output)  # Python 3.13.1
    ```

    ```python
    import harrix_pylib as h

    result_output = h.dev.run_powershell_script("python --version\npip --version")
    print(result_output)
    ```

    """
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    powershell_path = shutil.which("powershell")
    if powershell_path is None:
        msg = "PowerShell executable not found."
        raise RuntimeError(msg)

    process = subprocess.run(
        [
            powershell_path,
            "-Command",
            (
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$OutputEncoding = [System.Text.Encoding]::UTF8; "
                f"{command}"
            ),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return "\n".join(filter(None, [process.stdout, process.stderr]))


def run_powershell_script_as_admin(commands: str) -> str:
    r"""Execute a PowerShell script with administrator privileges and captures the output.

    Args:

    - `commands` (`str`): A string containing the PowerShell commands to execute.

    Returns:

    - `str`: The output from running the PowerShell script.

    Note:

    - This function creates temporary files to store the script and its output, which are deleted after execution.
    - Multiline scripts are written to a ``.ps1`` file as-is (not joined with ``;``), so block syntax is preserved.
    - The launcher uses ``Start-Process -Verb RunAs -Wait`` so execution finishes before the output file is read.

    Examples:

    ```python
    import harrix_pylib as h

    result_output = h.dev.run_powershell_script_as_admin("python --version")
    print(result_output)  # ﻿Python 3.11.9
    ```

    ```python
    import harrix_pylib as h

    result_output = h.dev.run_powershell_script_as_admin("python --version\npip --version")
    print(result_output)
    ```

    """
    script_body = commands.strip()
    if not script_body:
        return ""

    def _ps_single_quoted_literal(path: str) -> str:
        return "'" + str(path).replace("'", "''") + "'"

    tmp_wrapper_path: Path | None = None

    with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="wb") as tmp_script_file:
        tmp_script_file.write("\ufeff".encode("utf-8"))
        tmp_script_file.write(script_body.encode("utf-8"))
        tmp_script_path = Path(tmp_script_file.name)

    fd, out_name = tempfile.mkstemp(suffix=".txt", prefix="harrix_pylib_ps_admin_")
    os.close(fd)
    Path(out_name).unlink(missing_ok=True)
    tmp_output_path = Path(out_name)

    try:
        script_sq = _ps_single_quoted_literal(str(tmp_script_path))
        output_sq = _ps_single_quoted_literal(str(tmp_output_path))
        wrapper_script = f"& {script_sq} *>&1 | Out-File -LiteralPath {output_sq} -Encoding utf8"

        with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="wb") as tmp_wrapper_file:
            tmp_wrapper_file.write("\ufeff".encode("utf-8"))
            tmp_wrapper_file.write(wrapper_script.encode("utf-8"))
            tmp_wrapper_path = Path(tmp_wrapper_file.name)

        wrapper_sq = _ps_single_quoted_literal(str(tmp_wrapper_path))
        ps_cmd = (
            f"Start-Process -FilePath powershell.exe "
            f"-ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',{wrapper_sq} "
            f"-Verb RunAs -Wait"
        )

        powershell_path = shutil.which("powershell")
        if powershell_path is None:
            return "PowerShell executable not found."

        cmd = [
            powershell_path,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            ps_cmd,
        ]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        launcher_tail = "\n".join(filter(None, [(completed.stdout or "").strip(), (completed.stderr or "").strip()]))

        if tmp_output_path.exists():
            captured = tmp_output_path.read_text(encoding="utf-8")
            if captured.strip():
                return captured
            if launcher_tail:
                return f"{launcher_tail}\n(exit code {completed.returncode}; captured script output was empty)"
            return f"Exit code {completed.returncode} (captured script output was empty)."

        if launcher_tail:
            return (
                f"Output file was not created (UAC cancelled, elevation failed, or script did not run).\n"
                f"Exit code {completed.returncode}.\n{launcher_tail}"
            )
        return f"Output file was not created and the launcher produced no text (exit code {completed.returncode})."

    finally:
        tmp_script_path.unlink(missing_ok=True)
        tmp_output_path.unlink(missing_ok=True)
        if tmp_wrapper_path is not None:
            tmp_wrapper_path.unlink(missing_ok=True)


def write_in_output_txt(*, is_show_output: bool = True) -> Callable:
    """Decorate to write function output to a temporary file and optionally display it.

    This decorator captures all output of the decorated function into a list,
    measures execution time, and writes this information into an `output.txt` file
    in a temporary folder within the project root. It also offers the option
    to automatically open this file after writing.

    Args:

    - `is_show_output` (`bool`): If `True`, automatically open the output file
      after writing. Defaults to `True`.

    Returns:

    - `Callable`: A decorator function that wraps another function.

    The decorator adds the following methods to the wrapped function:

    - `add_line` (`Callable`): A method to add lines to the output list, which
      will be written to the file.

    Note:

    - This decorator changes the behavior of the decorated function by capturing
      its output and timing its execution.
    - The `output.txt` file is created in a `temp` folder under the project root.
      If the folder does not exist, it will be created.

    Examples:

    ```python
    import harrix_pylib as h


    @h.dev.write_in_output_txt(is_show_output=True)
    def f():
        f.add_line("Test")
        return 42


    f()
    # Test
    # Execution time: 0.0000 seconds
    ```

    ```python
    import harrix_pylib as h


    class ActionBase:
        icon: str = ""
        title: str = ""
        is_show_output: bool = False

        def __init__(self, **kwargs): ...

        def __call__(self, *args, **kwargs):
            decorated_execute = h.dev.write_in_output_txt(is_show_output=self.is_show_output)(self.execute)
            self.add_line = decorated_execute.add_line
            return decorated_execute(*args, **kwargs)

        def execute(self, *args, **kwargs):
            raise NotImplementedError("The execute method must be implemented in subclasses")
    ```

    """

    def decorator(func: Callable) -> Callable:
        class Wrapper:
            def __init__(self) -> None:
                self.output_lines = []

            def __call__(self, *args: Any, **kwargs: Any) -> None:
                self.output_lines.clear()
                start_time = time.time()
                func(*args, **kwargs)
                end_time = time.time()
                elapsed_time = end_time - start_time
                self.add_line(f"Execution time: {elapsed_time:.4f} seconds")
                temp_path = get_project_root() / "temp"
                if not temp_path.exists():
                    temp_path.mkdir(parents=True, exist_ok=True)
                file = Path(temp_path / "output.txt")
                output_text = "\n".join(self.output_lines) if self.output_lines else ""
                file.write_text(output_text, encoding="utf8")
                if is_show_output:
                    h.file.open_file_or_folder(file)

            def add_line(self, line: str) -> None:
                self.output_lines.append(line)
                print(line)

        return Wrapper()

    return decorator
