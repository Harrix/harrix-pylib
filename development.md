# Development

If you don't have [pipenv](https://pipenv.pypa.io/en/latest/) installed, then you can install it via the commands:

```console
python -m pip install virtualenv
python -m pip install pipenv
```

Installing packages by file `Pipfile`:

```console
pipenv install --dev
pipenv shell
```

Generate docs:

```console
pdoc --docformat="google" src\harrixpylib\
```

Example of installing a package under development in a test project:

```console
pipenv install -e C:/GitHub/harrix-pylib
```
