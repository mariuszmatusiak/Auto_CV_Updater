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
# JustJoinIT fetcher service implementation.
# Supports obtaining jobs data from the My Saved Jobs.
#
# Version 1.0, 2025-03-27 - The initial version.
#

from Core.Fetchers.IJobsOnlineFetcherService import *
from Core.Model.WebBrowser import HtmlField

from bs4 import BeautifulSoup
from urllib3.exceptions import ReadTimeoutError
import re, logging
from selenium.common.exceptions import NoSuchElementException

# URL encoding:
# - %252F - double-encoded /
# - %253A - double-encoded :
# - %3D - =
# - %26 - &
# - %3F - ?
# - %2F - /

JOB_WEBSITE = "JustJoinIT"
MAIN_PAGE = "https://justjoin.it/"
LOGIN_PAGE = "https://sso.rocketjobs.pl/login-by-email"
POST_LOGIN_PAGE = "https://profile.justjoin.it/profile"
MY_SAVED_JOBS_PAGES = ("https://profile.justjoin.it/favorite-offers",)
EMAIL_SIGNIN_BUTTON = HtmlField(cssSelector="a.MuiButtonBase-root:nth-child(3)")
SIGNIN_USERNAME_FIELD = HtmlField(tag="input", name="username")
SIGNIN_PASSWORD_FIELD = HtmlField(tag="input", name="password")
SIGNIN_BUTTON = HtmlField(tag="button", type_="submit", index=1)
MY_SAVED_JOBS_ROW = HtmlField(tag="li", otherAttributes={"data-index" : re.compile("\\d+", re.IGNORECASE)})
ENV_KEY = "JJIT_KEY"
KEY_SEPARATOR = "::"
DEFAULT_COOKIE_FILE = "justjoinit_cookies.json"

logger = logging.getLogger(__name__)

class JustJoinITFetcherService(IJobsOnlineFetcherService):
    """JustJoinIT Fetching Service class. Implements the IJobsFetcherService interface.
    """
    def __init__(self, username: str=None, password: str=None, cookiesFileDir: str = DEFAULT_COOKIE_FILE, headless: bool = False):
        super().__init__(username, password, cookiesFileDir, headless)
        self.websiteName = JOB_WEBSITE
        self.mainPage = MAIN_PAGE
        self.mySavedJobsPages = MY_SAVED_JOBS_PAGES
        self.mySavedJobsRow = MY_SAVED_JOBS_ROW
        self.envKeyName = ENV_KEY
        self.envKeySeparator = KEY_SEPARATOR
        self.authCookies = None
        self.validSignInTargetPage = MY_SAVED_JOBS_PAGES[0]

    def _extractJobUrlFromHtml(self, htmlJobDetails) -> str:
        jobUrl = htmlJobDetails.find(name="a")["href"]
        logger.debug(f"Extracted job url: {jobUrl}")
        return jobUrl

    def _getCredentialsHtmlFields(self) -> tuple[HtmlField]:
        # TODO Assert we are on the Sign In page
        usernameField = None
        passwordField = None
        signInButton = None
        try: # Try to sign in with password
            signInViaEmailButton = self.browser.getField(fieldData=EMAIL_SIGNIN_BUTTON)
            self.browser.clickField(webElement=signInViaEmailButton)
            usernameField = self.browser.getField(fieldData=SIGNIN_USERNAME_FIELD)
            passwordField = self.browser.getField(fieldData=SIGNIN_PASSWORD_FIELD)
            signInButton  = self.browser.getField(fieldData=SIGNIN_BUTTON)
        except NoSuchElementException as e:
            logger.warning("Failed to find username/password fields. The user might be already signed in.")
        return usernameField, passwordField, signInButton

    def _parseJobPagesForDetails(self, savedJobsUrls: set[str]):
        # Get jobs details
        jobList = []
        for jobUrl in savedJobsUrls:
            try:
                self.browser.visit(jobUrl)
                jobPageDetailsSoup = BeautifulSoup(self.browser.getCurrentPageSource(), "html.parser")
                htmlJobData = jobPageDetailsSoup.find_all(name=re.compile("h\\d"))
                jobCompany, jobTitle, jobLocation, jobDescription = JustJoinITFetcherService._extractJobDataFromHtml(htmlJobData)
                newJob = Job(
                    job=jobTitle,
                    url=jobUrl,
                    company=jobCompany,
                    location=jobLocation
                )
                newJob.setDetails(jobDescription)
                jobList.append(newJob)
            except ReadTimeoutError as e:
                logger.error(f"Read timeout error on fetching {jobUrl}")
        return jobList

    def _extractJobDataFromHtml(htmlJobDetails):
        # htmlJobDetails contains a list of paragraphs/headers. Iterate to get data.
        JOB_TITLE_HTML_INDEX = 0
        JOB_COMPANY_HTML_INDEX = 1
        JOB_DESCRIPTION_HTML_INDEX = 2
        jobTitleHtml = htmlJobDetails[JOB_TITLE_HTML_INDEX]
        jobCompanyHtml = htmlJobDetails[JOB_COMPANY_HTML_INDEX]
        jobDescriptionHtml = htmlJobDetails[JOB_DESCRIPTION_HTML_INDEX].next_sibling
        jobTitle = jobTitleHtml.string
        jobCompany = jobCompanyHtml.text
        jobDescription = "\n".join(jobDescriptionHtml.stripped_strings)
        jobLocation = ""
        logger.debug(f"Extracted job title: {jobTitle}, company: {jobCompany}, location: {jobLocation}, description: {jobDescription}")
        return jobCompany, jobTitle, jobLocation, jobDescription
