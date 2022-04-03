# harrix-pylib

Common functions for working in Python.

![GitHub](https://img.shields.io/github/license/Harrix/harrix-pylib) ![PyPI](https://img.shields.io/pypi/v/harrix-pylib)

## Quick start

```py
import harrixpylib as h

h.clear_directory("C:/temp_dir")
```

```py
import harrixpylib as h

md_clean = h.remove_yaml_from_markdown("""
---
categories: [it, program]
tags: [VSCode, FAQ]
---

# Installing VSCode
""")
print(md_clean)  # Installing VSCode
```

## Install

Pip: `pip install harrix-pylib`.

Pipenv: `pipenv install harrix-pylib`.

## Update

Pip: `pip update harrix-pylib`.

Pipenv: `pipenv update harrix-pylib`.

## Development

See [development.md](https://github.com/Harrix/harrix-pylib/blob/main/development.md).
