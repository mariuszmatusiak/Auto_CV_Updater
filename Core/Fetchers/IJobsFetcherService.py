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
# Interface for job fetcher services.
#
# Version 1.0, 2025-03-27 - The initial version.

from Core.Model.Job import Job
from Core.Model.WebBrowser import WebBrowser, SUPPORTED_WEBBROWSERS, HtmlField
from Utils.Encoder import Encoder
from Utils.FileHandler import writeJsonFile
from abc import abstractmethod, ABCMeta
from enum import Enum
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

import logging, os, getpass

logger = logging.getLogger(__name__)

class IJobsFetcherService(metaclass=ABCMeta):
    """An interface to fetch jobs through various job portals.
    Implement this interface in your class while adding support to other job portals.

    Args:
        ABC (ABCMeta): Standard Python Abstract Base Class.
    """

    def __init__(self, username: str=None, password: str=None, cookiesFileDir: str = None, headless: bool = False):
        self.username = username
        self.password = password
        self.cookiesFileDir = cookiesFileDir
        self.headless = headless
        self.browser = None
        # Members to be overriden by the inheriting services:
        self.mainPage = "www.website.com"
        self.websiteName = "Abstract Website Service"
        self.mySavedJobsPages = ("",)
        self.mySavedJobsRow = HtmlField()
        self.envKeyName = ""
        self.envKeySeparator = ""
        self.validSignInTargetPage = None # A page that is displayed only when a user is signed in.

    def __del__(self):
        del self.browser

    @abstractmethod
    def _extractJobUrlFromHtml(self, htmlJobDetails) -> str:
        """Implementation to be provided by the subclasses.
        Args:
            htmlJobDetails (_type_): A html section with job details.
        Returns:
            str: A url of the job page.
        """
        pass

    @abstractmethod
    def _getCredentialsHtmlFields(self) -> tuple[HtmlField]:
        """Implementation to be provided by the subclasses.
        Returns:
            tuple[HtmlField]: A tuple with username, password and sign in button fields
        """
        pass

    @abstractmethod
    def _parseJobPagesForDetails(self, savedJobsUrls: set[str]) -> list[Job]:
        """Implementation to be provided by the subclasses.
        Args:
            savedJobsUrls (set[str]): A set of job pages urls.
        Returns:
            list[Job]: A list of objects with job details
        """
        pass

    def _initWebBrowser(self):
        if self.browser is None:
            self.browser = WebBrowser(SUPPORTED_WEBBROWSERS.FIREFOX, self.headless)
            return True
        else:
            return False

    def _isUserAuthenticated(self) -> bool:
        if self.validSignInTargetPage:
            # Check by the web-page redirection mechanism
            logger.info(f"Opening {self.validSignInTargetPage}...")
            self.browser.visit(self.validSignInTargetPage) # Visit target page and check if we get redirected
            return self.validSignInTargetPage in self.browser.getCurrentPageTitleAndUrl()["url"]
        else:
            return False

    def _authenticateWithCookies(self):
        # We must first visit the main page before adding cookies (cookie-averse document error)
        # TODO Iterate over domains stored in cookie file and visit each unique page
        logger.info(f"Opening {self.mainPage}...")
        self.browser.visit(self.mainPage)
        logger.debug(f"Adding coookies from {self.cookiesFileDir}...")
        self.browser.addCookiesFromFile(self.cookiesFileDir) # Add cookies first and try to sign in with them

    def _retrieveCredentials(self):
        if self.username is not None:
            logger.debug(f"{self.websiteName} Service initialized with the username {self.username}")
        elif os.getenv(self.envKeyName):
            logger.debug(f"Found a key for {self.websiteName} in environment variables.")
            self.username = Encoder.decodeString(os.getenv(self.envKeyName)).split(self.envKeySeparator)[0]
            logger.debug(f"{self.websiteName} Service initialized with the environment variable username {self.username}")
        else:
            self.username = input(f"Enter {self.websiteName} username: ")
            logger.debug(f"{self.websiteName} Service initialized with the user-provided username {self.username}")
        if self.password is not None:
            logger.debug(f"{self.websiteName} Service initialized with the given password")
        elif os.getenv(self.envKeyName):
            self.password = Encoder.decodeString(os.getenv(self.envKeyName)).split(self.envKeySeparator)[1]
            logger.debug(f"{self.websiteName} Service initialized with the environment variable password")
        else:
            self.password = getpass.getpass(prompt=f"Enter {self.websiteName} password: ", echo_char="*")
            logger.debug(f"{self.websiteName} Service initialized with the user-provided password")
        return self.username, self.password

    def _authenticateWithCredentials(self):
        username, password = self._retrieveCredentials()
        usernameField, passwordField, signInButton = self._getCredentialsHtmlFields()
        self.browser.fillOutField(argument=username, webElement=usernameField)
        self.browser.fillOutField(argument=password, webElement=passwordField)
        self.browser.clickField(webElement=signInButton)

    def _authenticate(self):
        if self._isUserAuthenticated():
            return True
        else:
            # Try several available authentication methods
            if self.cookiesFileDir:
                self._authenticateWithCookies()
                if self._isUserAuthenticated():
                    return True
            self._authenticateWithCredentials()
            if self._isUserAuthenticated(): # TODO Check also POST_LOGIN_PAGE
                return True
            else:
                logger.error("Failed to authenticate!")
                return False

    def _storeCookies(self):
        sessionCookies = []
        if self.authCookies:
            # Save only the known authentication cookies
            for cookieName in self.authCookies:
                cookieData = self.browser.getACookie(cookieName)
                sessionCookies.append(cookieData)
                logger.debug(f"Saved cookie {cookieName}: {cookieData}")
        else:
            # Save all cookies from the current session
            sessionCookies = self.browser.getCookies()
        writeJsonFile(self.cookiesFileDir, sessionCookies)
        logger.info(f"Stored {self.websiteName} cookies in the {self.cookiesFileDir} file")
        return True # TODO Add error handling

    def _signIn(self, storeCookies=True) -> bool:
        resultSuccess = self._initWebBrowser()
        if resultSuccess:
            resultSuccess = self._authenticate()
        if resultSuccess:
            if storeCookies:
                resultSuccess = self._storeCookies()
        return resultSuccess

    def _parseSavedJobsPage(self) -> set[str]:
        savedJobsUrls = set()
        for page in self.mySavedJobsPages:
            logger.info(f"Opening {page}...")
            self.browser.visit(page)
            mySavedJobsPage = self.browser.getCurrentPageSource()
            try:
                mySavedJobsSoup = BeautifulSoup(mySavedJobsPage, "html.parser")
                htmlListOfJobs = mySavedJobsSoup.find_all(name=self.mySavedJobsRow.tag, attrs=self.mySavedJobsRow.otherAttributes)
                if len(htmlListOfJobs) > 0:
                    # Iterate over list elements
                    for row in htmlListOfJobs:
                        # Retrieve job URL
                        jobUrl = self._extractJobUrlFromHtml(row)
                        savedJobsUrls.add(jobUrl)
                else:
                    logger.warning(f"No saved jobs found on {self.websiteName}!")
            except NoSuchElementException as e:
                logger.error("No element: {}\nStack trace: \n{}".format(e.msg, e.stacktrace))
                break
            except IndexError as e:
                logger.info("Index out of range, no element found. No more pages to check.")
                break
        return savedJobsUrls

    def getSavedJobs(self) -> list[Job]:
        if self._signIn():
            savedJobsUrls = self._parseSavedJobsPage()
            savedJobs = self._parseJobPagesForDetails(savedJobsUrls)
            return savedJobs
        else:
            return []
