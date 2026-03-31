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

from Core.Fetchers.IJobsFetcherService import *
from Core.Model.WebBrowser import WebBrowser, SUPPORTED_WEBBROWSERS
from Utils.Encoder import Encoder
from Utils.FileHandler import writeJsonFile

from bs4 import BeautifulSoup
from urllib3.exceptions import ReadTimeoutError
import json, os, time, re, logging, getpass
from selenium.common.exceptions import NoSuchElementException

# LinkedIn HTML & CSS fields
LINKEDIN_MAIN_PAGE = "https://www.linkedin.com/"
LINKEDIN_LOGIN_PAGE = "https://www.linkedin.com/login/"
LINKEDIN_POST_LOGIN_PAGE = "https://www.linkedin.com/feed/"
LINKEDIN_MY_SAVED_JOBS_PAGES = ("https://www.linkedin.com/my-items/saved-jobs/",) #"https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED&start=<PAGE>0"
LINKEDIN_SIGNIN_BUTTON_CSS_SELECTOR = ".btn__primary--large"
LINKEDIN_SIGNIN_USERNAME_ID = "username"
LINKEDIN_SIGNIN_PASSWORD_ID = "password"
LINKEDIN_SAVEDJOBS_JOB_ROW = {
    "TAG" : "a",
    #"ATTRIBUTE" : {"data-view-name": "opportunity-tracker-job-details"} # A key-value pair of attributes allowing to find all job entries
    "ATTRIBUTE" : {"href" : re.compile("https://www\\.linkedin\\.com/jobs/view/\\S*/", re.IGNORECASE)}
}
LINKEDIN_SAVEDJOBS_JOB_ROW_DETAILS = {
    "TAG" : "p"
}
LINKEDIN_JOB_DETAILS_PAGE_DESCRIPTION = {
    "TAG" : "div",
    "ATTRIBUTE" : {"data-sdui-component" : "com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"}
}
LINKEDIN_JOB_DETAILS_DIV_DATA_VIEW_NAME = {"data-view-name": "job-detail-page"}
LINKEDIN_KEY_SEPARATOR = "::"
LINKEDIN_DEFAULT_COOKIE_FILE = "linkedin_cookies.json"
LINKEDIN_AUTH_COOKIES = ("bscookie", "li_at", "li_rm",)

logger = logging.getLogger(__name__)

class LinkedInFetcherService(IJobsFetcherService):
    """LinkedIn Fetching Service class. Implements the IJobsFetcherService interface.

    Args:
        IJobsFetcherService (_type_): interface
    """
    def __init__(self, username: str=None, password: str=None, cookiesFileDir: str = LINKEDIN_DEFAULT_COOKIE_FILE, headless: bool = False):
        """Create a LinkedIn Fetching service.

        Args:
            username (str): LinkedIn username. Defaults to None.
            password (str): LinkedIn password. Defaults to None.
            cookiesFileDir (str): Path to the cookies JSON file containing LinkedIn authentication cookies.
        """
        super().__init__()
        self.username = username
        self.password = password
        self.cookiesFileDir = cookiesFileDir
        self.browser = None
        self.headless = headless

    def __del__(self):
        del self.browser

    def _signIn(self, storeCookies=True):
        resultSuccess = False
        logger.info(f"Opening {LINKEDIN_MAIN_PAGE}...")
        self.browser = WebBrowser(SUPPORTED_WEBBROWSERS.FIREFOX, self.headless)
        self.browser.visit(LINKEDIN_MAIN_PAGE) # We must first visit the main page before adding cookies (cookie-averse document error)
        self.browser.addCookiesFromFile(self.cookiesFileDir) # Add cookies first and try to sign in with them
        self.browser.visit(LINKEDIN_LOGIN_PAGE) # Visit login page and check if we get redirected to post login feed page
        if self.browser.getCurrentPageTitleAndUrl()["url"] == LINKEDIN_LOGIN_PAGE:
            if self.username is not None:
                logger.debug(f"LinkedIn Service initialized with the username {self.username}")
            elif os.getenv("LIN_KEY"):
                logger.debug(f"Found a key for LinkedIn: {os.getenv("LIN_KEY")}")
                self.username = Encoder.decodeString(os.getenv("LIN_KEY")).split(LINKEDIN_KEY_SEPARATOR)[0]
                logger.debug(f"LinkedIn Service initialized with the environment variable username {self.username}")
            else:
                self.username = input("Enter LinkedIn username: ")
                logger.debug(f"LinkedIn Service initialized with the user-provided username {self.username}")
            if self.password is not None:
                logger.debug(f"LinkedIn Service initialized with the given password")
            elif os.getenv("LIN_KEY"):
                self.password = Encoder.decodeString(os.getenv("LIN_KEY")).split(LINKEDIN_KEY_SEPARATOR)[1]
                logger.debug(f"LinkedIn Service initialized with the environment variable password")
            else:
                self.password = getpass.getpass(prompt="Enter LinkedIn password: ", echo_char="*")
                logger.debug(f"LinkedIn Service initialized with the user-provided password")
            try: # Try to sign in with password
                self.browser.fillOutField(self.username, fieldId=LINKEDIN_SIGNIN_USERNAME_ID)
                self.browser.fillOutField(self.password, fieldId=LINKEDIN_SIGNIN_PASSWORD_ID)
                self.browser.clickField(fieldCssSelector=LINKEDIN_SIGNIN_BUTTON_CSS_SELECTOR)
            except NoSuchElementException as e:
                logger.warning("Failed to find username/password fields. The user might be already signed in.")
        if self.browser.getCurrentPageTitleAndUrl()["url"] == LINKEDIN_POST_LOGIN_PAGE:
            logger.info("Signed in successfully using provided cookies.")
            if storeCookies:
                sessionCookies = []
                for cookieName in LINKEDIN_AUTH_COOKIES:
                    cookieData = self.browser.getACookie(cookieName)
                    sessionCookies.append(cookieData)
                    logger.debug(f"Saved cookie {cookieName}: {cookieData}")
                writeJsonFile(self.cookiesFileDir, sessionCookies)
                logger.debug(f"Stored LinkedIn cookies in the {self.cookiesFileDir} file")
            resultSuccess = True
        else:
            logger.error("Failed to sign in!")
        return resultSuccess

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

    def _extractJobCompanyFromHtml(htmlJobDetails):
        jobCompany = htmlJobDetails[1].text.split(" · ")[0].strip()
        logger.debug(f"Extracted job ")
        return jobCompany

    def _extractJobLocationFromHtml(htmlJobDetails):
        jobLocation = htmlJobDetails[1].text.split(" · ")[1].replace("(Hybrid)","").replace("(Remote)","").replace("(On-site)","").strip()
        logger.debug(f"Extracted job ")
        return jobLocation

    def _extractJobUrlFromHtml(htmlJobDetails):
        jobUrl = htmlJobDetails.attrs["href"].strip()
        logger.debug(f"Extracted job url: {jobUrl}")
        return jobUrl

    def _extractJobDetailsFromHtml(htmlJobDetails):
        text = htmlJobDetails.stripped_strings # or just .strings or .text
        jobDetails = "\n".join(text) # .encode("utf-8", errors='ignore')
        logger.debug(f"Extracted job details:\n{jobDetails}")
        return jobDetails

    def _parseSavedJobsPage(self):
        savedJobsUrls = set()
        # Check all My Saved Jobs pages
        for page in LINKEDIN_MY_SAVED_JOBS_PAGES:
            logger.info(f"Opening {page}...")
            self.browser.visit(page)
            linkedInMySavedJobsPage = self.browser.getCurrentPageSource()
            try:
                mySavedJobsSoup = BeautifulSoup(linkedInMySavedJobsPage, "html.parser") #lxml?
                # Get list of My Saved Jobs on LinkedIn
                htmlListOfJobs = mySavedJobsSoup.find_all(name=LINKEDIN_SAVEDJOBS_JOB_ROW["TAG"], attrs=LINKEDIN_SAVEDJOBS_JOB_ROW["ATTRIBUTE"])
                if len(htmlListOfJobs) > 0:
                    # Iterate over list elements
                    for row in htmlListOfJobs:
                        # Retrieve job URL
                        jobUrl = LinkedInFetcherService._extractJobUrlFromHtml(row)
                        savedJobsUrls.add(jobUrl)
                else:
                    logger.warning("No saved jobs found on LinkedIn!")
            except NoSuchElementException as e:
                logger.error("No element: {}\nStack trace: \n{}".format(e.msg, e.stacktrace))
                break
            except IndexError as e:
                logger.info("Index out of range, no element found. No more pages to check.")
                break
        return savedJobsUrls

    def _parseJobPagesForDetails(self, savedJobsUrls: set):
        # Get jobs details
        jobList = []
        for jobUrl in savedJobsUrls:
            try:
                self.browser.visit(jobUrl)
                jobPageDetailsSoup = BeautifulSoup(self.browser.getCurrentPageSource(), "html.parser")
                htmlJobData = jobPageDetailsSoup.find_all(name=LINKEDIN_SAVEDJOBS_JOB_ROW_DETAILS["TAG"])
                jobCompany, jobTitle, jobLocation = LinkedInFetcherService._extractJobDataFromHtml(htmlJobData)
                htmlJobDetails = jobPageDetailsSoup.find(name=LINKEDIN_JOB_DETAILS_PAGE_DESCRIPTION["TAG"], attrs=LINKEDIN_JOB_DETAILS_PAGE_DESCRIPTION["ATTRIBUTE"])
                if htmlJobDetails:
                    jobDetails = LinkedInFetcherService._extractJobDetailsFromHtml(htmlJobDetails)
                else:
                    # No known approaches worked
                    jobDetails = "<No details found.>"
                    logger.warning(f"No details found about the job {jobUrl}")
                newJob = Job(
                    job=jobTitle,
                    url=jobUrl,
                    company=jobCompany,
                    location=jobLocation
                )
                newJob.setDetails(jobDetails)
                jobList.append(newJob)
            except ReadTimeoutError as e:
                logger.error(f"Read timeout error on fetching {jobUrl}")
        return jobList

    def getSavedJobs(self) -> list[Job]:
        if self.browser is None:
            self._signIn()
        savedJobsUrls = self._parseSavedJobsPage()
        savedJobs = self._parseJobPagesForDetails(savedJobsUrls)
        self.browser.dispose()
        return savedJobs

