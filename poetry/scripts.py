"""Module used by poetry to run various scripts."""
import os

import application.app as app


def audit():
    """Will audit the current application using various linters and stylers."""
    os.system("black .")
    os.system("pydocstyle --count --match-dir='[^env].*'")
    os.system(
        "flake8 . --count --exclude=env --ignore=W605,W503,W504,E501 --max-complexity=10 --statistics"
    )
    os.system("python -m pytest")


def start():
    """Will start the Flask application."""
    app.start()
