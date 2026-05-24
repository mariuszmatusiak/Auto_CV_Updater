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
from Core.Fetchers.IJobsFetcherService import IJobsFetcherService
from Utils.FileHandler import readJsonFile

import logging

logger = logging.getLogger(__name__)

JSON_FETCHER_SERVICE_NAME = "JSON file offline"

class JsonFileFetcherService(IJobsFetcherService):

    def __init__(self, jobsJsonFilePath: str):
        super().__init__()
        self.fetcherName = JSON_FETCHER_SERVICE_NAME
        self.jobsJsonFilePath = jobsJsonFilePath

    def getSavedJobs(self) -> list[Job]:
        jsonFileJobList = readJsonFile(self.jobsJsonFilePath)
        jobList = []
        for element in jsonFileJobList:
            newJob = Job(
                company=element["company"],
                job=element["job"],
                location=element["location"],
                url=element["url"],
                details=element["details"],
                letterRecipient=element["cover_letter_recipient"],
                letterAddress=element["cover_letter_address"],
                isVisaRequired=element["visa_required"]
            )
            jobList.append(newJob)
        return jobList
