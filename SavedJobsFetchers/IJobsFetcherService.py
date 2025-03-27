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
# Interface for job fetcher services.
#
# Version 1.0, 2025-03-27 - The initial version.

from abc import abstractmethod, ABCMeta
from enum import Enum

# WebDriver configurations
WEBDRIVER_SAFARI_PATH = "/usr/bin/safaridriver"
WEBDRIVER_SETUP_SLEEP_TIME = 10
WEBDRIVER_PAGE_LOAD_SLEEP_TIME = 5
#TODO Add support for other webdrivers

class WebDriver(Enum):
    WEBDRIVER_SAFARI = 1

class Job:
    """Job class.
    """
    def __init__(self, company: str, job: str, location: str, url: str, 
                    details: str = None, letterAddress: str = None, letterRecipient: str = None, isVisaRequired: str = None):
        """Job class constructor.

        Args:
            company (str): job company
            job (str): job name
            location (str): job location
            url (str): job url
            details (str, optional): job description. Defaults to None.
            letterAddress (str, optional): cover letter recipient address. Defaults to None.
            letterRecipient (str, optional): cover letter recipient name. Defaults to None.
            isVisaRequired (str, optional): determines if job visa required ("1"). Defaults to None.
        """
        self.company = company
        self.job = job
        self.location = location
        self.url = url
        self.details = details
        self.letterAddress = letterAddress
        self.letterRecipient = letterRecipient
        self.isVisaRequired = isVisaRequired

class IJobsFetcherService(metaclass=ABCMeta):
    """An interface to fetch jobs through various job portals.
    Implement this interface in your class while adding support to other job portals.

    Args:
        ABC (ABCMeta): Standard Python Abstract Base Class.
    """

    @abstractmethod
    def getSavedJobs(self) -> list[Job]:
        """Abstract method to fetch list of jobs.

        Returns:
            list[Job]: saved job list
        """
        pass