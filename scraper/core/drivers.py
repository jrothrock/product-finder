"""Driver module used for running selenium."""
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # noqa
from selenium.webdriver.common.by import By  # noqa
from selenium.webdriver.support import expected_conditions as EC  # noqa
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.firefox import GeckoDriverManager


class Driver(object):
    """Parent class used for deriving the selenium instance."""

    def __init__(self):
        """Create web driver with configured options."""
        headless = os.environ.get("RUN_HEADLESS", False)
        options = webdriver.FirefoxOptions()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")

        self.caps = DesiredCapabilities().FIREFOX
        self.caps[
            "pageLoadStrategy"
        ] = "eager"  # don't freeze on 3rd party scripts taking awhile to load.

        self.driver = webdriver.Firefox(
            firefox_options=options,
            desired_capabilities=self.caps,
            executable_path=GeckoDriverManager().install(),
        )

    # TODO: Further investigate implications of removal or changing to __exit__ dunder method.
    def __del__(self, *exc):
        """Close driver when all references to class have been removed."""
        if self.driver:
            self.driver.quit()
