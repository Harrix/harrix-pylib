# harrix-pylib

![harrix-pylib](img/featured-image.svg)

Common functions for working in Python (>= 3.12) for [my projects](https://github.com/Harrix?tab=repositories).

![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

## Install

Pip: `pip install harrix-pylib`.

uv: `uv add harrix-pylib`.

## Quick start

Examples of using the library:

```py
import harrixpylib as h

h.file.clear_directory("C:/temp_dir")
```

```py
import harrixpylib as h

md_clean = h.file.remove_yaml_from_markdown("""
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode
""")
print(md_clean)  # Installing VSCode
```

## CLI commands

CLI commands after installation.

- `uv self update` — update uv itself (sometimes you need to call twice).
- `uv sync --upgrade` — update all project libraries.
- `isort .` — sort imports.
- `ruff format` — format the project's Python files.
- `ruff check` — lint the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `pytest` — run tests without slow tests.
- `pytest -m "slow or not slow"` — run all tests.

## List of functions
