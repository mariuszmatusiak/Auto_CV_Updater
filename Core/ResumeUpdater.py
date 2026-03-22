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
# Script to update contents of the 12_recipients.tex and 04_skills.tex files

import logging, re, time, subprocess, time, os
from datetime import datetime
from enum import StrEnum
from Core.Model.Job import Job
from Core.SkillAnalyzer import SkillAnalyzer
from Utils.FileHandler import readFile, writeFile, readJsonFile, escapeFileSystemCharacters

logger = logging.getLogger(__name__)

class LaTeXResumeField(StrEnum):
    # LaTeX commands to provide job-specific information stored in the 12_recipients.tex file
    COMPANY          = r"\\newcommand\\positionCompany"
    NAME             = r"\\newcommand\\positionName"
    LOCATION         = r"\\newcommand\\positionLocation"
    VISA             = r"\\newcommand\\positionVisa"
    LETTER_RECIPIENT = r"\\newcommand\\recipient"
    LETTER_ADDRESS   = r"\\newcommand\\recipientAddress"

class ResumeUpdater:

    LOGGING_SLEEP_TIME_SECS = 3

    def __init__(self, cv_dir, recipients_latex_file, skills_latex_file, skills_json_file, make_executable):
        self.cv_dir = cv_dir
        self.recipients_latex_file = recipients_latex_file
        self.skills_latex_file = skills_latex_file
        self.skills_json_file = skills_json_file
        self.make_executable = make_executable
        self.skillAnalyzer = SkillAnalyzer()

    def _getField(self, field: str):
        result = None
        fileContent = readFile(self.recipients_latex_file)
        pattern = re.compile(field + "{(.*)}")
        match = pattern.search(fileContent)
        if match:
            result = match[1]
        return result

    def _updateField(self, field: str, argument: str, out_file: str=None):
        fileContent = readFile(self.recipients_latex_file)
        replacement = field + "{" + argument + "}"
        pattern = re.compile(field + "{.*}")
        updatedContent = pattern.sub(replacement, fileContent)
        if out_file is None:
            out_file = self.recipients_latex_file
        logger.info(f"LaTeX -> Setting {field} to {argument}.")
        writeFile(out_file, updatedContent)

    def _updateSelectedSkills(self, jobDetails: str):
        logger.info("Highlighting selected skills according to the job details.")
        skills = readJsonFile(self.skills_json_file)
        if skills is None:
            # Nothing to do, return
            return
        else:
            # Erase file content
            f = open(self.skills_latex_file, "w")
            f.close()
            for skillSection in skills.keys():
                logger.info(f"Updating section {skillSection}...")
                skillDictList = []
                # skillSection = skills[section.value]
                for skill in skills[skillSection]:
                    skillMentioned = self.skillAnalyzer.isSkillInJobDescription(skill=skill, jobDescription=jobDetails)
                    skillLatex = skill["latex"] + "/1" if skillMentioned > 0 else skill["latex"]
                    skillLatex = "{" + skillLatex + "}"
                    skillDictList.append({"latex": skillLatex, "score": skillMentioned})
                sortedSkillDictList = sorted(skillDictList, key=lambda x: x["score"], reverse=True)
                sortedSkillList = [x["latex"] for x in sortedSkillDictList]
                with open(self.skills_latex_file, "a") as file:
                    file.write("\\newcommand\\" + skillSection + "{\n")
                    file.write(",\n".join(sortedSkillList))
                    file.write("}\n\n")

    def updateCVFiles(self, jobsData: list[Job]):
        for job in jobsData:
            logger.info(f"===== Updating CV for {job.getJob()} at {job.getCompany()} in {job.getLocation()}. =====\n"
                        f"Details: {job.getDetails()}\n\n{job.getUrl()}")
            if job.company:
                self._updateField(LaTeXResumeField.COMPANY, job.getCompany(asLatexResumeField=True))
            if job.job:
                self._updateField(LaTeXResumeField.NAME, job.getJob(True))
            if job.location:
                self._updateField(LaTeXResumeField.LOCATION, job.getLocation(True))
            if job.visaRequired:
                self._updateField(LaTeXResumeField.VISA, job.isVisaRequired(True))
            if job.letterRecipient:
                self._updateField(LaTeXResumeField.LETTER_RECIPIENT, job.getLetterRecipient(True))
            if job.letterAddress:
                self._updateField(LaTeXResumeField.LETTER_ADDRESS, job.getLetterAddress(True))
            if job.details:
                self._updateSelectedSkills(job.details)
            logger.info("Rebuilding CVs...")
            # time.sleep(ResumeUpdater.LOGGING_SLEEP_TIME_SECS)
            self._rebuildCVs()

    def _toFileName(self, arg: str):
        return escapeFileSystemCharacters(arg.lower())

    def _rebuildCVs(self) -> None:
        lowerCasedCompanyName = self._toFileName(self._getField(LaTeXResumeField.COMPANY))
        lowerCasedLocationName = self._toFileName(self._getField(LaTeXResumeField.LOCATION))
        lowerCasedJobName = self._toFileName(self._getField(LaTeXResumeField.NAME))
        timestamp = datetime.now().strftime("%Y%m%d")
        buildCmd = [self.make_executable, 'all',
            f'company={lowerCasedCompanyName}',
            f'location={lowerCasedLocationName}',
            f'job={lowerCasedJobName}',
            f'timestamp={timestamp}'
        ]
        logger.info("Running make command in the LaTeX CV directory...")
        subprocess.run(args=buildCmd, cwd=self.cv_dir)

