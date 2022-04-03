"""Module for setting up additional pytest configurations."""
import _pytest.skipping
import pytest


def pytest_addoption(parser):
    """Add no skips addoptation."""
    parser.addoption(
        "--no-skips", action="store_true", default=False, help="disable skip marks"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_preparse(config, args):
    """If no skip found in args, overwrite skip method."""
    if "--no-skips" not in args:
        return

    def no_skip(*args, **kwargs):
        return

    _pytest.skipping.skip = no_skip
