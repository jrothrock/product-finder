"""Driver module used for running selenium."""
import os

from selenium import webdriver
from selenium.webdriver.common.by import By  # noqa
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC  # noqa
from selenium.webdriver.support.ui import WebDriverWait  # noqa
from webdriver_manager.firefox import GeckoDriverManager


class Driver:
    """Parent class used for deriving the selenium instance."""

    def _options(self):
        headless = os.environ.get("RUN_HEADLESS", False)
        options = webdriver.FirefoxOptions()
        options.add_argument("start-maximized")
        if headless:
            options.add_argument("--headless")
        
        return options

    def _capabilities(self):
        capabilities = DesiredCapabilities().FIREFOX
        capabilities[
            "pageLoadStrategy"
        ] = "eager"  # don't freeze on 3rd party scripts taking a while to load.

        return capabilities

    def get_driver(self):
        """Will return the driver if it exists, if not it will create one."""
        if not hasattr(self, "driver"):
            self.driver = webdriver.Firefox(
                firefox_options=self._options(),
                desired_capabilities=self._capabilities(),
                executable_path=GeckoDriverManager().install(),
            )

        return self.driver

    def cleanup(self):
        """Need to cleanup the driver session if it still exists."""
        if hasattr(self, "driver"):
            self.driver.quit()


driver_instance = Driver()
