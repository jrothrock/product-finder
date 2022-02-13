"""Module used by poetry to run various scripts."""
import os

import application.app as app


def audit():
    """Will audit the current application using various linters and stylers."""
    os.system("black --exclude=.venv --check .")
    os.system("pydocstyle --count --match-dir='[^\.venv].*'")
    os.system(
        "flake8 . --count --exclude=.venv --ignore=W605,W503,W504,E501 --max-complexity=10 --statistics"
    )
    os.system("isort .")
    os.system("python -m pytest")


def start():
    """Will start the Flask application."""
    app.start()
