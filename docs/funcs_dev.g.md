---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `funcs_dev.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_project_root`](#-function-get_project_root)
- [🔧 Function `load_config`](#-function-load_config)
- [🔧 Function `run_command`](#-function-run_command)
- [🔧 Function `run_powershell_script`](#-function-run_powershell_script)
- [🔧 Function `run_powershell_script_as_admin`](#-function-run_powershell_script_as_admin)
- [🔧 Function `write_in_output_txt`](#-function-write_in_output_txt)

</details>

## 🔧 Function `get_project_root`

```python
def get_project_root() -> Path
```

Find the root folder of the current project.

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

<details>
<summary>Code:</summary>

```python
def get_project_root() -> Path:
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
```

</details>

## 🔧 Function `load_config`

```python
def load_config(filename: str) -> dict
```

Load configuration from a JSON file.

Args:

- `filename` (`str`): Path to the JSON configuration file. Defaults to `None`.

Returns:

- `dict`: Configuration loaded from the file.

Examples:

```python
import harrix-pylib as h

config = h.dev.load_config("config.json")
```

```python
from pathlib import Path

import harrix_pylib as h

root_path = h.dev.get_project_root()
Path(root_path / "config.json").write_text('{"pi": 3.14}', encoding="utf8")

config = h.dev.load_config("config.json")
print(config["pi"])  # 3.14
```

<details>
<summary>Code:</summary>

```python
def load_config(filename: str) -> dict:
    config_file = Path(get_project_root()) / filename
    with config_file.open("r", encoding="utf-8") as file:
        config = json.load(file)

    def process_snippet(value: object) -> object:
        if isinstance(value, str) and value.startswith("snippet:"):
            snippet_path = Path(get_project_root()) / value.split("snippet:", 1)[1].strip()
            with snippet_path.open("r", encoding="utf-8") as snippet_file:
                return snippet_file.read()
        return value

    for key, value in config.items():
        if isinstance(value, dict):
            config[key] = {k: process_snippet(v) for k, v in value.items()}
        else:
            config[key] = process_snippet(value)

    return config
```

</details>

## 🔧 Function `run_command`

```python
def run_command(command: str) -> str
```

Run a console command and return its output.

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

<details>
<summary>Code:</summary>

```python
def run_command(
    command: str,
    *,
    is_shell: bool = True,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
) -> str:
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

        # Combine stdout and stderr, filter out empty lines
        output_parts = [process.stdout.strip(), process.stderr.strip()]
        return "\n".join(filter(None, output_parts))

    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {e!s}"
```

</details>

## 🔧 Function `run_powershell_script`

```python
def run_powershell_script(commands: str) -> str
```

Run a PowerShell script with the given commands.

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

<details>
<summary>Code:</summary>

```python
def run_powershell_script(commands: str) -> str:
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
```

</details>

## 🔧 Function `run_powershell_script_as_admin`

```python
def run_powershell_script_as_admin(commands: str) -> str
```

Execute a PowerShell script with administrator privileges and captures the output.

Args:

- `commands` (`str`): A string containing the PowerShell commands to execute.

Returns:

- `str`: The output from running the PowerShell script.

Raises:

- `subprocess.CalledProcessError`: If the PowerShell script execution fails.

Note:

- This function creates temporary files to store the script and its output, which are deleted after execution.
- The function waits for the script to finish and ensures the output file exists before reading from it.

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

<details>
<summary>Code:</summary>

```python
def run_powershell_script_as_admin(commands: str) -> str:
    res_output = []
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    # Create a temporary file with the PowerShell script
    with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as tmp_script_file:
        tmp_script_file.write(command.encode("utf-8"))
        tmp_script_path = Path(tmp_script_file.name)

    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_output_file:
        tmp_output_path = Path(tmp_output_file.name)

    try:
        # Wrapper script that runs the main script and writes the output to a file
        wrapper_script = f"& '{tmp_script_path}' | Out-File -FilePath '{tmp_output_path}' -Encoding UTF8"

        # Save the wrapper script to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as tmp_wrapper_file:
            tmp_wrapper_file.write(wrapper_script.encode("utf-8"))
            tmp_wrapper_path = Path(tmp_wrapper_file.name)

        # Command to run PowerShell with administrator privileges
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                f"Start-Process powershell.exe -ArgumentList "
                f"'-NoProfile -ExecutionPolicy Bypass -File \"{tmp_wrapper_path}\"' "
                f"-Verb RunAs"
            ),
        ]

        # Start the process
        process = subprocess.Popen(cmd)

        # Wait for the process to finish
        process.wait()

        # Ensure the output file has been created
        while not tmp_output_path.exists():
            time.sleep(0.1)

        # Wait until the file is fully written (can adjust wait time as needed)
        time.sleep(1)  # Delay to complete writing to the file

        # Read the output data from the file
        with tmp_output_path.open("r", encoding="utf-8") as f:
            output = f.read()
            res_output.append(output)

    finally:
        # Delete temporary files after execution
        tmp_script_path.unlink(missing_ok=True)
        tmp_output_path.unlink(missing_ok=True)
        tmp_wrapper_path.unlink(missing_ok=True)

    return "\n".join(filter(None, res_output))
```

</details>

## 🔧 Function `write_in_output_txt`

```python
def write_in_output_txt() -> Callable
```

Decorate to write function output to a temporary file and optionally display it.

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

<details>
<summary>Code:</summary>

```python
def write_in_output_txt(*, is_show_output: bool = True) -> Callable:

    def decorator(func: Callable) -> Callable:
        output_lines = []

        def wrapper(*args: Any, **kwargs: Any) -> None:
            output_lines.clear()
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            wrapper.add_line(f"Execution time: {elapsed_time:.4f} seconds")
            temp_path = get_project_root() / "temp"
            if not temp_path.exists():
                temp_path.mkdir(parents=True, exist_ok=True)
            file = Path(temp_path / "output.txt")
            output_text = "\n".join(output_lines) if output_lines else ""

            file.write_text(output_text, encoding="utf8")
            if is_show_output:
                h.file.open_file_or_folder(file)

        def add_line(line: str) -> None:
            output_lines.append(line)
            print(line)

        wrapper.add_line = add_line
        return wrapper

    return decorator
```

</details>
