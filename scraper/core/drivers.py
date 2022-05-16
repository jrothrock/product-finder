"""Driver module used for running selenium."""
import atexit
import os

from selenium import webdriver
from selenium.webdriver.common.by import By  # noqa
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC  # noqa
from selenium.webdriver.support.ui import WebDriverWait  # noqa
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
        ] = "eager"  # don't freeze on 3rd party scripts taking a while to load.

        # Bad
        os.system("pkill -f firefox")

        self.driver = webdriver.Firefox(
            firefox_options=options,
            desired_capabilities=self.caps,
            executable_path=GeckoDriverManager().install(),
        )

        atexit.register(self._close_driver)

    def _close_driver(self) -> None:
        if hasattr(self, "driver"):
            self.driver.quit()
