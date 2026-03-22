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
# Example usage:
#   py -3 updatecv.py [-c=CompanyName] [-j=DSP Senior Engineer] [-l=Boston, MA] [-v=y] [-p=embedded] [-s]
#

import logging

from Utils.LoggerSetup import LoggerSetup
from Core.CmdLineParser import CmdLineParser
from Core.JobFetcher import JobFetcher
from Core.ResumeUpdater import ResumeUpdater

logger = logging.getLogger(__name__)

def main():
    # 0. Initialize logging service
    loggerSetup = LoggerSetup()
    loggerSetup.init(toConsole=True, toFile=True)
    # 1. Get cmd line arguments and environment variables
    cmdLineParser = CmdLineParser()
    cmdLineParser.parseCmdLineArgumentsAndEnvVariables()
    config = cmdLineParser.getEnvironmentConfig()
    # 2a. Get jobs data from online services
    if config.sync:
        jobsFetcher = JobFetcher(config)
        jobsData = jobsFetcher.checkMySavedJobs()
    # 2b. Get jobs data from cmd line arguments
    else:
        jobsData = [ cmdLineParser.getJobDetails() ]
    # 3. Update CV files
    resumeUpdater = ResumeUpdater(cv_dir=config.cv_dir, recipients_latex_file=config.recipient_file,
                                  skills_latex_file=config.skills_file, skills_json_file=config.skills_json, make_executable=config.make_exec)
    resumeUpdater.updateCVFiles(jobsData)

if __name__ == "__main__":
    main()