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

from Core.Fetchers.IJobsFetcherService import *
from Core.Model.WebBrowser import WebBrowser, HtmlField, SUPPORTED_WEBBROWSERS
from Utils.Encoder import Encoder
from Utils.FileHandler import writeJsonFile

from bs4 import BeautifulSoup
from urllib3.exceptions import ReadTimeoutError
import json, os, time, re, logging, getpass
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
LOGIN_PAGE_DECODED = "https://sso.rocketjobs.pl/?redirectTo=/connect/authorize?response_type=code&client_id=jjit&redirect_uri=https://profile.justjoin.it"
LOGIN_PAGE_ENCODED = "https://sso.rocketjobs.pl/?redirectTo=%2Fconnect%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3Djjit%26redirect_uri%3Dhttps%253A%252F%252Fprofile.justjoin.it"
# 1. https://sso.rocketjobs.pl/?redirectTo=/connect%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3Djjit%26redirect_uri%3Dhttps%253A%252F%252Fjustjoin.it%252Fapi%252Fauth%252Fcallback%252Fidentity%26scope%3Dopenid%2Bprofile%2Bemail%2Boffline_access%26code_challenge%3DB7xXiE7jOeZfrGiRfZF2w4hVFEnQpJ_QCpJMg903y3s%26code_challenge_method%3DS256
# 2. https://sso.rocketjobs.pl/login-by-email?redirectTo=%2Fconnect%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3Djjit%26redirect_uri%3Dhttps%253A%252F%252Fjustjoin.it%252Fapi%252Fauth%252Fcallback%252Fidentity%26scope%3Dopenid%2Bprofile%2Bemail%2Boffline_access%26code_challenge%3DB7xXiE7jOeZfrGiRfZF2w4hVFEnQpJ_QCpJMg903y3s%26code_challenge_method%3DS256
# 3. https://sso.rocketjobs.pl/login-by-email?redirectTo=%2Fconnect%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3Drj%26redirect_uri%3Dhttps%253A%252F%252Frocketjobs.pl%252Fapi%252Fauth%252Fcallback%252Fidentity%26scope%3Dopenid%2Bprofile%2Bemail%2Boffline_access%26code_challenge%3DC2hsW9v92ETn9cIpuItiRs3lPR5XqCF3772xVb_KJUg%26code_challenge_method%3DS256
# https://sso.rocketjobs.pl/login-by-email?redirectTo=%2Fconnect%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3Drj%26redirect_uri%3Dhttps%253A%252F%252Frocketjobs.pl%252Fapi%252Fauth%252Fcallback%252Fidentity%26scope%3Dopenid%2Bprofile%2Bemail%2Boffline_access%26code_challenge%3DC2hsW9v92ETn9cIpuItiRs3lPR5XqCF3772xVb_KJUg%26code_challenge_method%3DS256
POST_LOGIN_PAGE = "https://profile.justjoin.it/profile"
MY_SAVED_JOBS_PAGES = ("https://profile.justjoin.it/favorite-offers",)
EMAIL_SIGNIN_BUTTON = HtmlField(cssSelector="a.MuiButtonBase-root:nth-child(3)")
SIGNIN_USERNAME_FIELD = HtmlField(tag="input", name="username"
                                  #cssSelector="#_R_1aaqklubramivb_",
                                  #xPath="//*[@id=\"_R_1aaqklubramivb_\"]"
                                  )
SIGNIN_PASSWORD_FIELD = HtmlField(tag="input", name="password"
                                  #cssSelector="#_R_1aeqklubramivb_",
                                  #xPath="//*[@id=\"_R_1aeqklubramivb_\"]"
                                  )

SIGNIN_BUTTON = HtmlField(tag="button", type_="submit", index=1
                          #cssSelector="button.MuiButtonBase-root:nth-child(8)", # button.MuiButtonBase-root:nth-child(4)
                          #xPath="/html/body/div[2]/div/div[2]/form/button"
                          )
MY_SAVED_JOBS_ROW = HtmlField(tag="li", otherAttributes={"data-index" : re.compile("\\d+", re.IGNORECASE)})
#{
#    "TAG" : "a",
#    #"ATTRIBUTE" : {"data-view-name": "opportunity-tracker-job-details"} # A key-value pair of attributes allowing to find all job entries
#    "ATTRIBUTE" : {"href" : re.compile("https://www\\.linkedin\\.com/jobs/view/\\S*/", re.IGNORECASE)}
#}
MY_SAVED_JOBS_ROW_DETAILS = {
    "TAG" : "p"
}
JJIT_JOB_DETAILS_PAGE_DESCRIPTION = {
    "TAG" : "div",
    "ATTRIBUTE" : {"data-sdui-component" : "com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"}
}
JJIT_JOB_DETAILS_DIV_DATA_VIEW_NAME = {"data-view-name": "job-detail-page"}
KEY_SEPARATOR = "::"
DEFAULT_COOKIE_FILE = "justjoinit_cookies.json"
JJIT_AUTH_COOKIES = ("bscookie", "li_at", "li_rm",)

logger = logging.getLogger(__name__)

class JustJoinITFetcherService(IJobsFetcherService):
    """JustJoinIT Fetching Service class. Implements the IJobsFetcherService interface.

    Args:
        IJobsFetcherService (_type_): interface
    """
    def __init__(self, username: str=None, password: str=None, cookiesFileDir: str = DEFAULT_COOKIE_FILE, headless: bool = False):
        """Create a JustJoinIT Fetching service.

        Args:
            username (str): JustJoinIT username. Defaults to None.
            password (str): JustJoinIT password. Defaults to None.
            cookiesFileDir (str): Path to the cookies JSON file containing JustJoinIT authentication cookies.
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
        logger.info(f"Opening {MAIN_PAGE}...")
        self.browser = WebBrowser(SUPPORTED_WEBBROWSERS.FIREFOX, self.headless)
        self.browser.visit(MAIN_PAGE) # We must first visit the main page before adding cookies (cookie-averse document error)
        self.browser.addCookiesFromFile(self.cookiesFileDir) # Add cookies first and try to sign in with them
        targetPage = MY_SAVED_JOBS_PAGES[0]
        self.browser.visit(targetPage) # Visit login page and check if we get redirected to post login feed page
        if LOGIN_PAGE_ENCODED in self.browser.getCurrentPageTitleAndUrl()["url"]:
            if self.username is not None:
                logger.debug(f"JustJoinIT Service initialized with the username {self.username}")
            elif os.getenv("JJIT_KEY"):
                logger.debug("Found a key for JustJoinIT in environment variables.")
                self.username = Encoder.decodeString(os.getenv("JJIT_KEY")).split(KEY_SEPARATOR)[0]
                logger.debug(f"JustJoinIT Service initialized with the environment variable username {self.username}")
            else:
                self.username = input("Enter JustJoinIT username: ")
                logger.debug(f"JustJoinIT Service initialized with the user-provided username {self.username}")
            if self.password is not None:
                logger.debug(f"JustJoinIT Service initialized with the given password")
            elif os.getenv("JJIT_KEY"):
                self.password = Encoder.decodeString(os.getenv("JJIT_KEY")).split(KEY_SEPARATOR)[1]
                logger.debug(f"JustJoinIT Service initialized with the environment variable password")
            else:
                self.password = getpass.getpass(prompt="Enter JustJoinIT password: ", echo_char="*")
                logger.debug(f"JustJoinIT Service initialized with the user-provided password")
            try: # Try to sign in with password
                signInViaEmailButton = self.browser.getField(fieldData=EMAIL_SIGNIN_BUTTON)
                self.browser.clickField(webElement=signInViaEmailButton)
                usernameField = self.browser.getField(fieldData=SIGNIN_USERNAME_FIELD)
                passwordField = self.browser.getField(fieldData=SIGNIN_PASSWORD_FIELD)
                signInButton  = self.browser.getField(fieldData=SIGNIN_BUTTON)
                self.browser.fillOutField(argument=self.username, webElement=usernameField)
                self.browser.fillOutField(argument=self.password, webElement=passwordField)
                self.browser.clickField(webElement=signInButton)
                if self.browser.getCurrentPageTitleAndUrl()["url"] == POST_LOGIN_PAGE:
                    logger.info(f"Signed in successfully using username and password. Redirecting to {targetPage}")
                    self.browser.visit(targetPage)
            except NoSuchElementException as e:
                logger.warning("Failed to find username/password fields. The user might be already signed in.")
        if self.browser.getCurrentPageTitleAndUrl()["url"] == targetPage:
            if storeCookies:
                sessionCookies = self.browser.getCookies()
                #for cookieName in JJIT_AUTH_COOKIES:
                #    cookieData = self.browser.getACookie(cookieName)
                #    sessionCookies.append(cookieData)
                #    logger.debug(f"Saved cookie {cookieName}: {cookieData}")
                writeJsonFile(self.cookiesFileDir, sessionCookies)
                logger.debug(f"Stored JustJoinIT cookies in the {self.cookiesFileDir} file")
            resultSuccess = True
        else:
            logger.error("Failed to sign in!")
        return resultSuccess

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

    def _extractJobCompanyFromHtml(htmlJobDetails):
        jobCompany = htmlJobDetails[1].text.split(" · ")[0].strip()
        logger.debug(f"Extracted job ")
        return jobCompany

    def _extractJobLocationFromHtml(htmlJobDetails):
        jobLocation = htmlJobDetails[1].text.split(" · ")[1].replace("(Hybrid)","").replace("(Remote)","").replace("(On-site)","").strip()
        logger.debug(f"Extracted job ")
        return jobLocation

    def _extractJobUrlFromHtml(htmlJobDetails):
        jobUrl = htmlJobDetails.find(name="a")["href"]
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
        for page in MY_SAVED_JOBS_PAGES:
            logger.info(f"Opening {page}...")
            self.browser.visit(page)
            mySavedJobsPage = self.browser.getCurrentPageSource()
            try:
                mySavedJobsSoup = BeautifulSoup(mySavedJobsPage, "html.parser") #lxml?
                htmlListOfJobs = mySavedJobsSoup.find_all(name=MY_SAVED_JOBS_ROW.tag, attrs=MY_SAVED_JOBS_ROW.otherAttributes)
                if len(htmlListOfJobs) > 0:
                    # Iterate over list elements
                    for row in htmlListOfJobs:
                        # Retrieve job URL
                        jobUrl = JustJoinITFetcherService._extractJobUrlFromHtml(row)
                        savedJobsUrls.add(jobUrl)
                else:
                    logger.warning("No saved jobs found on JustJoinIT!")
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

    def getSavedJobs(self) -> list[Job]:
        if self.browser is None:
            self._signIn()
        savedJobsUrls = self._parseSavedJobsPage()
        savedJobs = self._parseJobPagesForDetails(savedJobsUrls)
        self.browser.dispose()
        return savedJobs

