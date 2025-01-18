from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h


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
