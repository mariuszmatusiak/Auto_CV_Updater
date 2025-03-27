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
# Script to update target data in CVs, resumes, cover letters and research statements.
# Also supports highlighting skills based on the job description provided as CLI argument or from the supported job portal.
#
# Version 1.0, 2025-03-27 - The initial version, contains CLI and LinkedIn support.
#
# Example usage:
#   py -3 updatecv.py [-c=CompanyName] [-j=DSP Senior Engineer] [-l=Boston, MA] [-v=y] [-p=embedded] [-s]
#

import os, argparse, re, subprocess, time
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
from SavedJobsFetchers.LinkedInFetcherService import LinkedInFetcherService
from SavedJobsFetchers.IJobsFetcherService import *
from Utils.Files.FileHandler import *
from Utils.Files.LaTeXHandler import *

SCORE_MULTIPLIER_SKILL_MENTIONED = 5
SCORE_MULTIPLIER_SKILL_ALIAS_MENTIONED = 4
SCORE_MULTIPLIER_SKILL_AREA_MENTIONED = 1

class LaTeXResumeFields(Enum):
    """Enum class of user-defined LaTeX commands to provide job-specific information.
    File: 12_recipients.tex
    """
    POSITION_COMPANY = r"\\newcommand\\positionCompany"
    POSITION_NAME = r"\\newcommand\\positionName"
    POSITION_LOCATION = r"\\newcommand\\positionLocation"
    POSITION_VISA = r"\\newcommand\\positionVisa"
    POSITION_LETTER_RECIPIENT = r"\\newcommand\\recipient"
    POSITION_LETTER_ADDRESS = r"\\newcommand\\recipientAddress"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",   "--company", dest="company", help="Specify company/university name.", required=False)
    parser.add_argument("-j",   "--job", dest="job", help="Specify job/position.", required=False)
    parser.add_argument("-l",   "--location", dest="location", help="Specify location.", required=False)
    parser.add_argument("-d",   "--description", dest="details", help="Specify job description.", required=False)
    parser.add_argument("-v",   "--visa", dest="isVisaRequired", help="Specify if visa sponsorship needed, 0 - no, 1 - yes.", required=False, choices=["0", "1"])
    parser.add_argument("-r",   "--letter_recipient", dest="letterRecipient", help="Specify the cover letter recipient", required=False)
    parser.add_argument("-a",   "--letter_address", dest="letterAddress", help="Specify the cover letter address", required=False)
    parser.add_argument("-u",   "--url", dest="url", help="Specify the job URL", required=False)
    parser.add_argument("-s",   "--sync", dest="sync", help="Prepare CVs based on the list of saved jobs. Supports: LinkedIn.", required=False, action="store_true")
    parser.add_argument("-sa",  "--skill_area", help="Specify skill area(s) (groups) to include in the resume", required=False, action="append")
    parser.add_argument("-env", "--environment", help="Specify the path to the user .env file.", required=False, default=".env")
    parser.add_argument("-rf",  "--recipient_file", help="Specify the name of the LaTeX CV recipient file in the CV-Templates/data/ directory to be used.", required=False, default="12_recipients.tex")
    parser.add_argument("-sf",  "--skills_file", help="Specify the name of the LaTeX CV skills file in the CV-Templates/data/ directory to be used.", required=False, default="04_skills.tex")
    parser.add_argument("-sj",  "--skills_json", help="Specify the path to the JSON skills file to be used.", required=False, default=os.path.join("User", "skills.json"))
    parser.add_argument("-lc",  "--linkedin_cookies", help="Specify the path to the JSON file with LinkedIn authentication cookies.", required=False, default=os.path.join("User", "linkedin_cookies.json"))
    args = parser.parse_args()
    load_dotenv(args.environment)

    cv_dir = os.path.join(os.getenv("CV_DIR"))
    recipients_latex_file = os.path.join(cv_dir, "data", args.recipient_file)
    skills_latex_file = os.path.join(cv_dir, "data", args.skills_file)
    skills_json_file = args.skills_json

    if args.sync:
        savedJobs = checkMySavedJobs(args)
    else:
        savedJobs = [
            Job(
                company=args.company, 
                job=args.job,
                location=args.location,
                url=args.url,
                details=args.details,
                letterAddress=args.letterAddress, 
                letterRecipient=args.letterRecipient, 
                isVisaRequired=args.isVisaRequired)
        ]
    for job in savedJobs:
        print(f"===== Updating CV for {job.job} at {job.company} in {job.location}. =====\nDetails: {job.details}\n\n{job.url}")
        updateCVFiles(job, recipients_latex_file, skills_latex_file, skills_json_file)
        print("Rebuilding CVs...")
        time.sleep(3)
        rebuildCVs(cv_dir, recipients_latex_file)

def checkMySavedJobs(args) -> list[Job]:
    savedJobs = []
    print("Getting My Saved Jobs from LinkedIn...\n")
    fetcherService = LinkedInFetcherService(
        username=os.getenv("LIN_LOGIN"),
        password=os.getenv("LIN_KEY"),
        cookiesFileDir=args.linkedin_cookies)
    savedJobs.extend(fetcherService.getSavedJobs())
    # TODO Add other services if needed like Indeed, pracuj.pl, etc.
    return savedJobs

def updateCVFiles(job: Job, recipients_latex_file: str, skills_latex_file: str, skills_json_file: str):
    if job.company:
        print(f"LaTeX -> Seting {LaTeXResumeFields.POSITION_COMPANY.value} to {job.company}.")
        updateField(LaTeXResumeFields.POSITION_COMPANY, job.company, recipients_latex_file)

    if job.job:
        print(f"LaTeX -> Seting {LaTeXResumeFields.POSITION_NAME.value} to {job.job}.")
        updateField(LaTeXResumeFields.POSITION_NAME, job.job, recipients_latex_file)

    if job.location:
        print(f"LaTeX -> Seting {LaTeXResumeFields.POSITION_LOCATION.value} to {job.location}.")
        updateField(LaTeXResumeFields.POSITION_LOCATION, job.location, recipients_latex_file)

    if job.isVisaRequired:
        print(f"LaTeX -> Seting {LaTeXResumeFields.POSITION_VISA.value} to {job.isVisaRequired}.")
        updateField(LaTeXResumeFields.POSITION_VISA, job.isVisaRequired, recipients_latex_file)

    if job.letterRecipient:
        print(f"LaTeX -> Seting {LaTeXResumeFields.POSITION_LETTER_RECIPIENT.value} to {job.letterRecipient}.")
        updateField(LaTeXResumeFields.POSITION_LETTER_RECIPIENT, job.letterRecipient, recipients_latex_file)

    if job.letterAddress:
        print(f"LaTeX -> Seting {LaTeXResumeFields.POSITION_LETTER_ADDRESS.value} to {job.letterAddress}.")
        updateField(LaTeXResumeFields.POSITION_LETTER_ADDRESS, job.letterAddress, recipients_latex_file)

    if job.details:
        print("LaTeX -> Highlighting skills according to the job details.")
        updateJobSkills(job.details, skills_json_file, skills_latex_file)

def getField(field: LaTeXResumeFields, latex_file: str):
    result = ""
    fileContent = readFile(latex_file)
    pattern = re.compile(field.value + "{(.*)}")
    match = pattern.search(fileContent)
    if match:
        result = match[1]
    return result

def updateField(field: LaTeXResumeFields, argument: str, in_file: str, out_file: str=None):
    fileContent = readFile(in_file)
    escapedArgument = escapeLatexCharacters(argument)
    replacement = field.value + "{" + escapedArgument + "}"
    if argument != escapedArgument:
        print(f"LaTeX -> Escaped {argument} -> {escapedArgument}")
    pattern = re.compile(field.value + "{.*}")
    updatedContent = pattern.sub(replacement, fileContent)
    if out_file is None:
        out_file = in_file
    writeFile(out_file, updatedContent)

def isSkillInJobDescription(skill: dict, jobDetails: str) -> int:
    skillMentionedScore = 0
    skillAliasMentioned = 0
    skillAreasMentioned = 0
    skillOnlyMentioned = 0
    incrementBy = 0
    jobDetailsLS = jobDetails.lower().strip()
    # Can return immediately if marked as generic
    print(f"--- Checking skill \"{skill['skill']}\" ---")
    if "generic" in skill["area"]:
        print(f"\tMarked as the generic skill, adding +1 to score.")
        skillAreasMentioned += 1
    # Primary - precise skill match including small and capital letters
    incrementBy = jobDetails.count(skill["skill"]) if skill["is_case_sensitive"] else jobDetailsLS.count(skill["skill"].lower())
    print(f"\t\"{skill['skill']}\" mentioned {incrementBy} times.")
    skillOnlyMentioned += incrementBy
    # Secondary - precise alias match including small and capital letters
    for alias in skill["alias"]:
        incrementBy = jobDetails.count(alias) if skill["is_case_sensitive"] else jobDetailsLS.count(alias.lower())
        print(f"\tAlias \"{alias}\" mentioned {incrementBy} times.")
        skillAliasMentioned += incrementBy
    # Tertiary - non-precise area match ignoring small and capital letters
    for area in skill["area"]:
        # Skip "generic" area
        if area == "generic":
            continue
        incrementBy = jobDetailsLS.count(area.lower())
        print(f"\tArea \"{area}\" mentioned {incrementBy} times.")
        skillAreasMentioned += incrementBy
    skillMentionedScore = (skillOnlyMentioned * SCORE_MULTIPLIER_SKILL_MENTIONED +
                            skillAliasMentioned * SCORE_MULTIPLIER_SKILL_ALIAS_MENTIONED + 
                            skillAreasMentioned * SCORE_MULTIPLIER_SKILL_AREA_MENTIONED)
    print(f"\tScore: {skillMentionedScore}.\n" + ("-" * 66))
    return skillMentionedScore

def updateJobSkills(jobDetails: str, skills_json_file: str, skills_latex_file: str):
    skills = readJsonFile(skills_json_file)
    if skills is None:
        # Nothing to do, return
        return
    else:
        # Erase file content
        f = open(skills_latex_file, "w")
        f.close()
        for skillSection in skills.keys():
            print(f"Updating section {skillSection}...")
            skillDictList = []
            # skillSection = skills[section.value]
            for skill in skills[skillSection]:
                skillMentioned = isSkillInJobDescription(skill, jobDetails)
                skillLatex = skill["latex"] + "/1" if skillMentioned > 0 else skill["latex"]
                skillLatex = "{" + skillLatex + "}"
                skillDictList.append({"latex": skillLatex, "score": skillMentioned})
            sortedSkillDictList = sorted(skillDictList, key=lambda x: x["score"], reverse=True)
            sortedSkillList = [x["latex"] for x in sortedSkillDictList]
            with open(skills_latex_file, "a") as file:
                file.write("\\newcommand\\" + skillSection + "{\n")
                file.write(",\n".join(sortedSkillList))
                file.write("}\n\n")

def rebuildCVs(cv_dir : str, recipient_file: str) -> None:
    companyName = getField(LaTeXResumeFields.POSITION_COMPANY, recipient_file)
    companyNameLC = escapeFileSystemCharacters(companyName.lower())
    locationName = getField(LaTeXResumeFields.POSITION_LOCATION, recipient_file)
    locationNameLC = escapeFileSystemCharacters(locationName.lower())
    jobName = getField(LaTeXResumeFields.POSITION_NAME, recipient_file)
    jobNameLC = escapeFileSystemCharacters(jobName.lower())
    date = datetime.now().strftime("%Y%m%d")
    cmd = ['gmake', 'all', 
           f'company={companyNameLC}',
           f'location={locationNameLC}', 
           f'job={jobNameLC}',
           f'timestamp={date}'
    ]
    print("Running gmake command in the LaTeX CV directory...")
    subprocess.run(args=cmd, cwd=cv_dir)

if __name__ == "__main__":
    main()