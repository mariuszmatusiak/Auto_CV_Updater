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
# LinkedIn fetcher service implementation.
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

JOB_WEBSITE = "LinkedIn"
MAIN_PAGE = "https://www.linkedin.com/"
LOGIN_PAGE = "https://www.linkedin.com/login/"
POST_LOGIN_PAGE = "https://www.linkedin.com/feed/"
MY_SAVED_JOBS_PAGES = ("https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED",
                       "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED&start=10",
                       "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED&start=20") #"https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED&start=<PAGE>0"
#SIGNIN_BUTTON = HtmlField(tag="button", type_="button")
SIGNIN_BUTTON = HtmlField(cssSelector=".btn__primary--large")
SIGNIN_USERNAME_FIELD = HtmlField(id="username")
# SIGNIN_USERNAME_FIELD = HtmlField(tag="input", index=3, type_="text", otherAttributes={"autocomplete" : "webauthn"})
SIGNIN_PASSWORD_FIELD = HtmlField(id="password")
# SIGNIN_PASSWORD_FIELD = HtmlField(tag="input", index=4, type_="password", otherAttributes={"autocomplete" : "current-password"})
MY_SAVED_JOBS_ROW = HtmlField(tag="a", otherAttributes={"href" : re.compile("https://www\\.linkedin\\.com/jobs/view/\\S*/", re.IGNORECASE)})
MY_SAVED_JOBS_ROW_DETAILS = HtmlField(tag="p")
JOB_DETAILS_PAGE_DESCRIPTION = HtmlField(tag="div", otherAttributes={"data-sdui-component" : "com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"})
ENV_KEY = "LIN_KEY"
KEY_SEPARATOR = "::"
DEFAULT_COOKIE_FILE = "linkedin_cookies.json"
AUTH_COOKIES = ("bscookie", "li_at", "li_rm",)

logger = logging.getLogger(__name__)

class LinkedInFetcherService(IJobsOnlineFetcherService):
    """LinkedIn Fetching Service class. Implements the IJobsFetcherService interface.
    """
    def __init__(self, username: str=None, password: str=None, cookiesFileDir: str = DEFAULT_COOKIE_FILE, headless: bool = False):
        super().__init__(username, password, cookiesFileDir, headless)
        self.fetcherName = JOB_WEBSITE
        self.mainPage = MAIN_PAGE
        self.mySavedJobsPages = MY_SAVED_JOBS_PAGES
        self.mySavedJobsRow = MY_SAVED_JOBS_ROW
        self.envKeyName = ENV_KEY
        self.envKeySeparator = KEY_SEPARATOR
        self.authCookies = AUTH_COOKIES
        self.validSignInTargetPage = MY_SAVED_JOBS_PAGES[0]

    def _extractJobUrlFromHtml(self, htmlJobDetails) -> str:
        """Overriden abstract method.
        """
        jobUrl = htmlJobDetails.attrs["href"].strip()
        logger.debug(f"Extracted job url: {jobUrl}")
        return jobUrl

    def _getCredentialsHtmlFields(self) -> tuple[HtmlField]:
        # TODO Assert we are on the Sign In page
        usernameField = None
        passwordField = None
        signInButton = None
        try: # Try to sign in with password
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
                htmlJobData = jobPageDetailsSoup.find_all(name=MY_SAVED_JOBS_ROW_DETAILS.tag)
                jobCompany, jobTitle, jobLocation = LinkedInFetcherService._extractJobDataFromHtml(htmlJobData)
                htmlJobDescription = jobPageDetailsSoup.find(name=JOB_DETAILS_PAGE_DESCRIPTION.tag, attrs=JOB_DETAILS_PAGE_DESCRIPTION.otherAttributes)
                if htmlJobDescription:
                    jobDescription = LinkedInFetcherService._extractJobDescriptionFromHtml(htmlJobDescription)
                else:
                    # No known approaches worked
                    jobDescription = "<No description found.>"
                    logger.warning(f"No description found about the job {jobUrl}")
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
        # htmlJobDetails contains a list of paragraphs. Iterate to get data.
        JOB_COMPANY_STRIPPED_STRING_INDEX = 0
        JOB_TITLE_STRIPPED_STRING_INDEX = 1
        JOB_LOCATION_STRIPPED_STRING_INDEX = 2
        strippedStrings = []
        for p in htmlJobDetails:
            strippedStrings.extend(p.stripped_strings)
        jobCompany  = strippedStrings[JOB_COMPANY_STRIPPED_STRING_INDEX]
        jobTitle    = strippedStrings[JOB_TITLE_STRIPPED_STRING_INDEX]
        jobLocation = strippedStrings[JOB_LOCATION_STRIPPED_STRING_INDEX].translate({"(Hybrid)": None, "(Remote)": None, "(On-site)": None})
        # do other stuff if needed, e.g. replace(", Verified", ""), encode("utf-8", errors='ignore') etc.
        logger.debug(f"Extracted job title: {jobTitle}, company: {jobCompany}, location: {jobLocation}")
        return jobCompany, jobTitle, jobLocation

    def _extractJobDescriptionFromHtml(htmlJobDescription):
        text = htmlJobDescription.stripped_strings # or just .strings or .text
        jobDescription = "\n".join(text) # .encode("utf-8", errors='ignore')
        logger.debug(f"Extracted job details:\n{jobDescription}")
        return jobDescription
