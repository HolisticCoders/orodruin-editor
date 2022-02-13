# Orodruin Editor
A GUI editor for managing [Orodruin](https://github.com/HolisticCoders/orodruin) Graphs.

# Prerequisites
- [Poetry](https://python-poetry.org/) must be installed.
- Python 3.7+ must be installed.
    Everything should work with versions higher than 3.7 but that's never been tested.
    If you use pyenv, run `pyenv install 3.7.9` and poetry will pick up on the proper version automatically
- [Orodruin](https://github.com/HolisticCoders/orodruin) must already be cloned.

# Installation
- Clone this repository next to orodruin's repository (this is imperative, poetry uses a relative path to orodruin's folder to use it as a dependency.)
- cd in `orodruin-editor` 
- Run `poetry install -E PySide2 --no-dev` to create a new virtual env and install all the dependencies.
    Remove the `--no-dev` argument if you want the dev dependencies.
- To run the editor, run `poetry run python orodruin_editor/main.py`
    Alternatively, you can activate the virtualenv and run `python orodruin_editor/main.py`