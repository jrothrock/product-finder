"""Util module for handling system level utilities."""
import sys
import os


def exit():
    """Exit the process gracefully."""
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
