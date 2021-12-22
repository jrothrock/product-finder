from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.firefox import GeckoDriverManager


class Driver(object):
    def __init__(self):
        self.caps = DesiredCapabilities().FIREFOX
        self.caps[
            "pageLoadStrategy"
        ] = "eager"  # don't freeze on 3rd party scripts taking awhile to load
        self.driver = webdriver.Firefox(
            desired_capabilities=self.caps,
            executable_path=GeckoDriverManager().install(),
        )

    def __del__(self, *exc):
        if self.driver:
            self.driver.quit()
