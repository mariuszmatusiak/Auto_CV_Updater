# Auto CV Updater - automatize your CV modifications
# Copyright (C) 2026 Mariusz Matusiak <coffeedrivenengineer@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#

import logging, time, json
from enum import StrEnum, Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service
from selenium.common.exceptions import NoSuchElementException

from Utils.FileHandler import readJsonFile

# WebDriver configurations
WEBDRIVER_SAFARI_PATH = "/usr/bin/safaridriver"
WEBDRIVER_CHROMIUM_PATH = "/usr/bin/chromium-browser"
WEBDRIVER_CHROMIUM_DRIVER_PATH = "/usr/bin/chromedriver"
WEBDRIVER_SETUP_SLEEP_TIME = 10
WEBDRIVER_PAGE_LOAD_SLEEP_TIME = 10
#TODO Add support for other webdrivers

class WebDriver(Enum):
    WEBDRIVER_SAFARI = 0
    WEBDRIVER_FIREFOX = 1
    WEBDRIVER_CHROMIUM = 2
    WEBDRIVER_CHROME = 3
    WEBDRIVER_EDGE = 4
    WEBDRIVER_IE = 5

class SUPPORTED_WEBBROWSERS(StrEnum):
    SAFARI = "Safari"
    FIREFOX = "Firefox"
    CHROMIUM = "Chromium"

logger = logging.getLogger(__name__)

class WebBrowser:

    def __init__(self, selectedBrowser: SUPPORTED_WEBBROWSERS = None, headless: bool = False):
        self.headless = headless
        if selectedBrowser:
            self.initialize(selectedBrowser)

    def __del__(self):
        logger.debug("Disposing a created WebBrowser instance.")
        self.dispose()

    def initialize(self, selectedBrowser: SUPPORTED_WEBBROWSERS = SUPPORTED_WEBBROWSERS.FIREFOX):
        logger.info(f"Initializing webdriver, headless mode enabled: {self.headless}.")
        if selectedBrowser == SUPPORTED_WEBBROWSERS.SAFARI:
            safariOptions = webdriver.SafariOptions()
            if self.headless:
                 # TODO Add support for headless mode when available
                 logger.warning("Headless mode in Safari not available")
            self.webDriver = webdriver.Safari(service=Service(executable_path=WEBDRIVER_SAFARI_PATH), options=safariOptions)
        elif selectedBrowser == SUPPORTED_WEBBROWSERS.FIREFOX:
            firefoxOptions = webdriver.FirefoxOptions()
            if self.headless:
                firefoxOptions.add_argument("-headless")
            self.webDriver = webdriver.Firefox(options=firefoxOptions)
        elif selectedBrowser == SUPPORTED_WEBBROWSERS.CHROMIUM:
            chromium_options = webdriver.ChromeOptions()
            if self.headless:
                chromium_options.add_argument("--headless")
            chromium_options.binary_location = WEBDRIVER_CHROMIUM_PATH
            self.webDriver = webdriver.Chrome(service=Service(executable_path=WEBDRIVER_CHROMIUM_DRIVER_PATH), options=chromium_options)
        else:
            logger.error("WebDriver not supported yet.")
            self.webDriver = None
        logger.info(f"Webdriver {selectedBrowser} initialized.")

    def visit(self, url):
        self.webDriver.get(url) # We must first visit the page before adding cookies (cookie-averse document error)
        time.sleep(WEBDRIVER_PAGE_LOAD_SLEEP_TIME) # wait for page to load

    def addCookiesFromFile(self, cookiesFile):
        logger.debug(f"Loading cookies from file {cookiesFile}")
        cookies = readJsonFile(cookiesFile)
        if cookies:
            for cookie in cookies:
                self.webDriver.add_cookie(cookie_dict=cookie)
                logger.debug(f"Added cookie \"{cookie['name']}\":\"{cookie['value']}\"")
            time.sleep(WEBDRIVER_SETUP_SLEEP_TIME)
        else:
            logger.error("No cookies were added!")

    def getCookies(self):
        logger.debug("Dumping all cookies...")
        cookies = self.webDriver.get_cookies()
        return cookies

    def getACookie(self, name : str):
        logger.debug(f"Getting cookie {name}")
        return self.webDriver.get_cookie(name)

    def getField(self, fieldId: str = None, fieldCssSelector: str = None):
        field = None
        if fieldId:
            field = self.webDriver.find_element(By.ID, fieldId)
        elif fieldCssSelector:
            field = self.webDriver.find_element(By.CSS_SELECTOR, fieldCssSelector)
        else:
            logger.error("No field ID or CSS selector provided.")
        return field

    def clickField(self, fieldId: str = None, fieldCssSelector: str = None, wait=True):
        field = self.getField(fieldId, fieldCssSelector)
        if field:
            field.click()
        if wait:
            time.sleep(WEBDRIVER_PAGE_LOAD_SLEEP_TIME)

    def fillOutField(self, arg: str, fieldId: str = None, fieldCssSelector: str = None):
        field = self.getField(fieldId, fieldCssSelector)
        if field:
            field.send_keys(arg)

    def getCurrentPageSource(self):
        return self.webDriver.page_source

    def getCurrentPageTitleAndUrl(self):
        return {"title": self.webDriver.title, "url" : self.webDriver.current_url}

    def dispose(self):
        if self.webDriver is not None:
            self.webDriver.close()
            self.webDriver.quit()
            self.webDriver = None
