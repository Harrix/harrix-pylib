# Development

If you don't have [pipenv](https://pipenv.pypa.io/en/latest/) installed, then you can install it via the commands:

```shell
python -m pip install virtualenv
python -m pip install pipenv
```

Installing packages by file `Pipfile`:

```shell
pipenv install --dev
pipenv shell
```

Example of installing a package under development in a test project:

```shell
pipenv install -e C:/GitHub/harrix-pylib
```
