# Auto CV Updater - automatize your CV modifications
# Copyright (C) 2025  Mariusz Matusiak <mariusz.m.matusiak@gmail.com>
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

from .IJobsFetcherService import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service
from selenium.common.exceptions import NoSuchElementException
import json, os, time, re

# LinkedIn HTML & CSS fields
LINKEDIN_MY_SAVED_JOBS_PAGE = "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED&start=<PAGE>0"
LINKEDIN_SIGNIN_BUTTON_CSS_SELECTOR = ".btn__primary--large"
LINKEDIN_SIGNIN_USERNAME_ID = "username"
LINKEDIN_SIGNIN_PASSWORD_ID = "password"
LINKEDIN_TFA_ID = "input__phone_verification_pin"
LINKEDIN_SAVEDJOBS_LIST_XP = "/html/body/div[6]/div[3]/div/main/section/div/div[2]/div/ul"
LINKEDIN_SAVEDJOBS_LIST_CSS = ".ilpSrejhJlrdxFOYbBAZVTWFlYDOyjAUKPGVo"
LINKEDIN_SAVEDJOBS_COMPANY_CSS = "t-14 t-black t-normal"
LINKEDIN_SAVEDJOBS_LOCATION_CSS = "t-14 t-normal"
LINKEDIN_JOB_DETAILS_ID = "job-details"

class LinkedInFetcherService(IJobsFetcherService):
    """LinkedIn Fetching Service class. Implements the IJobsFetcherService interface.

    Args:
        IJobsFetcherService (_type_): interface
    """

    def __init__(self, username: str=None, password: str=None, cookiesFileDir: str=None, webDriver: WebDriver=WebDriver.WEBDRIVER_SAFARI):
        """Create a LinkedIn Fetching service.

        Args:
            username (str): LinkedIn username. Defaults to None.
            password (str): LinkedIn password. Defaults to None.
            cookiesFileDir (str): Path to the cookies JSON file containing LinkedIn authentication cookies.
        """
        self.username = username if username is not None else input("Enter LinkedIn username: ")
        self.password = password if password is not None else input("Enter LinkedIn password: ")
        self.cookiesFileDir = cookiesFileDir if cookiesFileDir is not None else input("Enter path to the LinkedIn cookies file: ")
        self.webDriver = webDriver

    def parsePageForSavedJobs(self, savedJobsList: list, htmlPage: str):
        mySavedJobsSoup = BeautifulSoup(htmlPage, "html.parser") #lxml?
        # Get list of My Saved Jobs on LinkedIn
        htmlListOfJobs = mySavedJobsSoup.find_all(name="ul", attrs={"role": "list"})[0].find_all(name="li")
        # Iterate over list elements
        for row in htmlListOfJobs:
            # Retrieve job title and link
            htmlJobTitleAndLink = row.find_all(name="a", attrs={"data-test-app-aware-link": ""})[1] # Skip [0] - company image
            # Retrieve job company
            htmlJobCompany = row.find_all(class_=re.compile(LINKEDIN_SAVEDJOBS_COMPANY_CSS))[0]
            # Retrieve job location
            htmlJobLocation = row.find_all(class_=re.compile(LINKEDIN_SAVEDJOBS_LOCATION_CSS))[0]
            newJob = Job(
                job=htmlJobTitleAndLink.text.replace(", Verified", "").strip(),
                url=htmlJobTitleAndLink.attrs["href"].strip(),
                company=htmlJobCompany.text.strip(),
                location=htmlJobLocation.text.replace("(Hybrid)","").replace("(Remote)","").replace("(On-site)","").strip()
            )
            savedJobsList.append(newJob)

    def parseJobPageDetails(self, htmlPage: str) -> str:
        jobPageDetailsSoup = BeautifulSoup(htmlPage, "html.parser")
        htmlJobDetails = jobPageDetailsSoup.find(name="div", attrs={"id": LINKEDIN_JOB_DETAILS_ID})
        if htmlJobDetails:
            jobDetailsStrings = htmlJobDetails.strings
        else:
            jobDetailsStrings = ["No details provided."]
        return "\n".join(jobDetailsStrings)

    def getSavedJobs(self) -> list[Job]:
        savedJobs = []
        print("Initializing webdriver...")
        if self.webDriver == WebDriver.WEBDRIVER_SAFARI:
            browser = webdriver.Safari(service=Service(executable_path=WEBDRIVER_SAFARI_PATH))
        else:
            print("WebDriver not supported yet.")
            return

        time.sleep(WEBDRIVER_SETUP_SLEEP_TIME)
        # Load cookies
        print("Loading cookies...")
        with open(self.cookiesFileDir, "r") as f:
            cookies = json.load(fp=f)
            for cookie in cookies:
                browser.add_cookie(cookie_dict=cookie)
                print(f"Added cookie \"{cookie['name']}\":\"{cookie['value']}\"")

        time.sleep(WEBDRIVER_SETUP_SLEEP_TIME)
        page = 0
        # Check all My Saved Jobs pages but no more than 10 of them.
        while page < 10:
            linkedInMySavedJobsUrl = LINKEDIN_MY_SAVED_JOBS_PAGE.replace("<PAGE>", str(page))
            print(f"Opening {linkedInMySavedJobsUrl}...")
            browser.get(linkedInMySavedJobsUrl)
            # wait for page to load
            time.sleep(WEBDRIVER_PAGE_LOAD_SLEEP_TIME)
            # Wait for page opening
            try:
                # Try to sign in if needed
                usernameInput = browser.find_element(By.ID, LINKEDIN_SIGNIN_USERNAME_ID)
                usernameInput.send_keys(self.username)
                passwordInput = browser.find_element(By.ID, LINKEDIN_SIGNIN_PASSWORD_ID)
                passwordInput.send_keys(self.password)
                signInButton  = browser.find_element(By.CSS_SELECTOR, LINKEDIN_SIGNIN_BUTTON_CSS_SELECTOR)
                signInButton.click()
                time.sleep(WEBDRIVER_PAGE_LOAD_SLEEP_TIME)
            except NoSuchElementException as e:
                print("Failed to sign in. The user might be already signed in.")
            
            linkedInMySavedJobsPage = browser.page_source
            try:
                self.parsePageForSavedJobs(savedJobs, linkedInMySavedJobsPage)
            except NoSuchElementException as e:
                print("No element: {}\nStack trace: \n{}".format(e.msg, e.stacktrace))
                break
            except IndexError as e:
                print("Index out of range, no element found. No more pages to check.")
                break
            page += 1

        # Get job details
        for job in savedJobs:
            browser.get(job.url)
            time.sleep(WEBDRIVER_PAGE_LOAD_SLEEP_TIME)
            job.details = self.parseJobPageDetails(browser.page_source)
            job.letterRecipient = job.company # TODO - to update for more data
            job.letterAddress = job.location # TODO - to update for more data
            job.isVisaRequired = "0" # TODO - to update for more data

        browser.close()
        browser.quit()
        return savedJobs

def main():
    fetcherService = LinkedInFetcherService()
    fetcherService.getSavedJobs()

if __name__ == "__main__":
    main()