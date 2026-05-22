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

import os, argparse, logging, shutil, subprocess
from sys import exit
from dotenv import load_dotenv
from Utils.FileHandler import fileExists, dirExists
from Core.Model.EnvironmentConfig import EnvironmentConfig, SUPPORTED_VARIABLES
from Core.Model.WebBrowser import SUPPORTED_WEBBROWSERS
from Core.Model.Job import Job
from Core.Model.ErrorCodes import ERROR_CODES

logger = logging.getLogger(__name__)

class CmdLineParser:

    def __init__(self):
        self.envFilePath = None
        self.environmentConfig = None
        self.jobDetails = None

    def getJobDetails(self):
        return self.jobDetails

    def getEnvironmentConfig(self):
        return self.environmentConfig

    def parseCmdLineArgumentsAndEnvVariables(self):
        parser = argparse.ArgumentParser()
        # Get job details
        parser.add_argument("-c",   "--company", help="Specify company/university name.", required=False)
        parser.add_argument("-j",   "--job", help="Specify job/position.", required=False)
        parser.add_argument("-l",   "--location", help="Specify location.", required=False)
        parser.add_argument("-d",   "--description", help="Specify job description.", required=False)
        parser.add_argument("-v",   "--visa", dest="isVisaRequired", help="Specify if visa sponsorship is needed.", required=False, action="store_true")
        parser.add_argument("-r",   "--letter_recipient", dest="letterRecipient", help="Specify the cover letter recipient", required=False)
        parser.add_argument("-a",   "--letter_address", dest="letterAddress", help="Specify the cover letter address", required=False)
        parser.add_argument("-u",   "--url", help="Specify the job URL", required=False)
        parser.add_argument("-sa",  "--skill_area", help="Specify skill area(s) (groups) to include in the resume", required=False, action="append")
        # Get environment config details
        parser.add_argument("-s",   "--sync", help="Prepare CVs based on the list of saved jobs. Supports: LinkedIn, JustJoinIT", required=False, action="store_true")
        parser.add_argument("-jb",  "--job_file", help="Prepare CVs based on the list of jobs saved in the JSON file.", required=False, action="store_true")
        parser.add_argument("-env", "--environment", help="Specify the path to the user .env file. This will overwrite existing environment variables.", required=False)
        parser.add_argument("-cv",  "--cv_dir", help="Specify the path to the <CV_Templates_dir> directory", required=False)
        parser.add_argument("-rf",  "--recipient_file", help="Specify the name of the LaTeX CV recipient file in the <CV_Templates_dir>/data/ directory to be used.", required=False, default="12_recipients.tex")
        parser.add_argument("-sf",  "--skills_file", help="Specify the name of the LaTeX CV skills file in the <CV_Templates_dir>/data/ directory to be used.", required=False, default="04_skills.tex")
        parser.add_argument("-sj",  "--skills_json", help="Specify the path to the JSON skills file to be used.", required=False, default=os.path.join("User", "skills.json"))
        parser.add_argument("-lc",  "--linkedin_cookies", help="Specify the path to the JSON file with LinkedIn authentication cookies.", required=False, default=os.path.join("User", "linkedin_cookies.json"))
        parser.add_argument("-jc",  "--justJoinIt_cookies", help="Specify the path to the JSON file with JustJoinIT authentication cookies.", required=False, default=os.path.join("User", "justjoinit_cookies.json"))
        parser.add_argument("-b",   "--browser", help="Specify the web browser to use. Default=%(default)s", choices=SUPPORTED_WEBBROWSERS, default=SUPPORTED_WEBBROWSERS.FIREFOX)
        parser.add_argument("-hl",  "--headless", help="Specify if you want to run process in the background (no display)", action="store_true")
        args = parser.parse_args()
        # Store job details
        self.jobDetails = Job(
            company=args.company,
            job=args.job,
            location=args.location,
            url=args.url,
            details=args.description,
            letterAddress=args.letterAddress,
            letterRecipient=args.letterRecipient,
            isVisaRequired=args.isVisaRequired
        )
        logger.debug(self.jobDetails)
        # Store environment details
        if args.environment and fileExists(args.environment):
            load_dotenv(dotenv_path=args.environment, override=True)
            logger.info(f"Imported environment variables from file {args.environment}")

        cv_dir = self._locateCVTemplatesDirectory(args.cv_dir)
        make_exec = self._locateMakeExecutable(os.getenv(SUPPORTED_VARIABLES.MAKE_EXEC))

        self.environmentConfig = EnvironmentConfig(
            sync=args.sync,
            skill_areas=args.skill_area,
            recipient_file=os.path.join(cv_dir, "data", args.recipient_file),
            skills_file=os.path.join(cv_dir, "data", args.skills_file),
            skills_json=args.skills_json,
            browser=args.browser,
            headless=args.headless,
            cv_dir=cv_dir,
            make_exec=make_exec,
            linkedInCookies=args.linkedin_cookies,
            justJoinItCookies=args.justJoinIt_cookies
        )
        logger.debug(self.environmentConfig)

    def _locateMakeExecutable(self, arg : str):
        m = shutil.which("make")
        if m:
            logger.info("Found make executable: ")
            subprocess.run([m, "--version"])
            return m
        gm = shutil.which("gmake")
        if gm:
            logger.info("Found gmake executable: ")
            subprocess.run([gm, "--version"])
            return gm
        other = os.getenv(SUPPORTED_VARIABLES.MAKE_EXEC)
        if other and fileExists(other):
            logger.info("Found executable in environment variables: ")
            subprocess.run([other, "--version"])
            return other
        if arg and fileExists(arg):
            logger.info("Found executable: ")
            subprocess.run([arg, "--version"])
            return arg
        logger.error("Cannot find the make/gmake executable!")
        exit(ERROR_CODES.DIRECTORY_OR_FILE_NOT_EXISTS)

    def _locateCVTemplatesDirectory(self, arg : str):
        if arg and dirExists(arg):
            return arg
        elif os.getenv(SUPPORTED_VARIABLES.CV_DIR) and dirExists(os.getenv(SUPPORTED_VARIABLES.CV_DIR)):
            return os.getenv(SUPPORTED_VARIABLES.CV_DIR)
        else:
            logger.error("Cannot find the CV Templates directory!")
            exit(ERROR_CODES.DIRECTORY_OR_FILE_NOT_EXISTS)



