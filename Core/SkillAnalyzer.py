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

import logging, sys
from enum import StrEnum

class Fields(StrEnum):
    SKILL = "skill"
    AREA = "area"
    ALIAS = "alias"
    IS_CASE_SENSITIVE = "is_case_sensitive"
    IS_FAVOURITE = "is_favourite"
    LAST_USED = "last_used"
    LVL_OF_EXPERTISE = "expertise"

SCORE_MULTIPLIER_SKILL_FAVOURITE = sys.maxsize
SCORE_MULTIPLIER_SKILL_MENTIONED = 5
SCORE_MULTIPLIER_ALIAS_MENTIONED = 4
SCORE_MULTIPLIER_AREA_MENTIONED = 1

logger = logging.getLogger(__name__)

class SkillAnalyzer:

    def __init__(self):
        pass

    def _countPreciseMatches(jsonSillObj: dict, jobDescription: str):
        # Primary - precise case-sensitive or non-case-sensitive skill matches.
        if jsonSillObj[Fields.IS_CASE_SENSITIVE]:
            count = jobDescription.count(jsonSillObj[Fields.SKILL])
        else:
            jobDescriptionLS = jobDescription.lower().strip()
            count = jobDescriptionLS.count(jsonSillObj[Fields.SKILL].lower())
        logger.info(f"- \"{jsonSillObj[Fields.SKILL]}\" mentioned {count} times.")
        return count

    def _countAliasMatches(jsonSillObj: dict, jobDescription: str):
        # Secondary - precise alias match including small and capital letters
        totalCount = 0
        jobDescriptionLS = jobDescription.lower().strip()
        for alias in jsonSillObj[Fields.ALIAS]:
            if jsonSillObj[Fields.IS_CASE_SENSITIVE]:
                count = jobDescription.count(alias)
            else:
                count = jobDescriptionLS.count(alias.lower())
            logger.info(f"- \"{jsonSillObj[Fields.SKILL]}\"\'s alias \"{alias}\" mentioned {count} times.")
            totalCount += count
        return totalCount

    def _countAreaMatches(jsonSillObj: dict, jobDescription: str):
        # Tertiary - non-precise area match ignoring small and capital letters
        totalCount = 0
        jobDescriptionLS = jobDescription.lower().strip()
        for area in jsonSillObj[Fields.AREA]:
            # Skip "generic" area
            if area == "generic":
                continue
            count = jobDescriptionLS.count(area.lower())
            logger.info(f"- \"{jsonSillObj[Fields.SKILL]}\"\'s area \"{area}\" mentioned {count} times.")
            totalCount += count
        return totalCount

    def _isSkillInJobDescription(jsonSillObj: dict, jobDescription: str) -> int:
        skillImportanceTotalScore = 0
        # Can return immediately if marked as generic/favourite
        logger.info(f"--- Checking skill \"{jsonSillObj[Fields.SKILL]}\" ---")
        if "generic" in jsonSillObj[Fields.AREA] or jsonSillObj[Fields.IS_FAVOURITE]:
            logger.info(f"- Skill \"{jsonSillObj[Fields.SKILL]}\" marked as favourite <3.")
            skillImportanceTotalScore += SCORE_MULTIPLIER_SKILL_FAVOURITE
        skillImportanceTotalScore += SkillAnalyzer._countPreciseMatches(jsonSillObj, jobDescription) * SCORE_MULTIPLIER_SKILL_MENTIONED
        skillImportanceTotalScore += SkillAnalyzer._countAliasMatches(jsonSillObj, jobDescription) * SCORE_MULTIPLIER_ALIAS_MENTIONED
        skillImportanceTotalScore += SkillAnalyzer._countAreaMatches(jsonSillObj, jobDescription) * SCORE_MULTIPLIER_AREA_MENTIONED
        logger.info(f"--- Score: {skillImportanceTotalScore}. " + ("-" * 3))
        return skillImportanceTotalScore

    def _skillSortingCallbackFunction(arg):
        # TODO Consider also last_used and expertise fields
        return arg[1] # return value from a key-value tupple

    def getScoreSortedSkillMap(jsonSkills, jobDetails):
        sectionSkillToScoreMap = {}
        for skillObj in jsonSkills:
            skillimportanceScore = SkillAnalyzer._isSkillInJobDescription(jsonSillObj=skillObj, jobDescription=jobDetails)
            sectionSkillToScoreMap.update({skillObj[Fields.SKILL] : skillimportanceScore})
        sortedSkillToScoreMap = dict(sorted(sectionSkillToScoreMap.items(), key=SkillAnalyzer._skillSortingCallbackFunction, reverse=True))
        return sortedSkillToScoreMap