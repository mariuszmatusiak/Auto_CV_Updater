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
# Script to update target data in CVs, resumes, cover letters and research statements.
# Also supports highlighting skills based on the job description provided as CLI argument or from the supported job portal.
#

import logging
from Core.Model.Job import Job
from Core.Model.EnvironmentConfig import EnvironmentConfig
from Core.Fetchers.IJobsOnlineFetcherService import IJobsOnlineFetcherService
from Core.Fetchers.LinkedIn.LinkedInFetcherService import LinkedInFetcherService
from Core.Fetchers.JustJoinIT.JustJoinITFetcherService import JustJoinITFetcherService
# To define and import more services here if needed

class JobFetcher:

    def __init__(self, args: EnvironmentConfig):
        self.services = []
        self.logger = logging.getLogger().getChild("Core.JobFetcher")
        self.services.append(LinkedInFetcherService(
            username=args.services["linkedIn"]["login"],
            password=args.services["linkedIn"]["password"],
            cookiesFileDir=args.services["linkedIn"]["cookies"],
            headless=args.headless
        ))
        self.services.append(JustJoinITFetcherService(
            username=args.services["justJoinIt"]["login"],
            password=args.services["justJoinIt"]["password"],
            cookiesFileDir=args.services["justJoinIt"]["cookies"],
            headless=args.headless
        ))
        # TODO Add other services if needed like Indeed, pracuj.pl, etc.

    def checkMySavedJobs(self) -> list[Job]:
        savedJobs = []
        for fetcherService in self.services:
            self.logger.info(f"Getting My Saved Jobs from {fetcherService.websiteName}...\n")
            savedJobs.extend(fetcherService.getSavedJobs())
        return savedJobs

    def prepareJobDataOffline(self, args) -> list[Job]:
        savedJobs = []
        return savedJobs