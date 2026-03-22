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
from enum import StrEnum

class SkillDict(StrEnum):
    SKILL = "skill"


SCORE_MULTIPLIER_SKILL_MENTIONED = 5
SCORE_MULTIPLIER_SKILL_ALIAS_MENTIONED = 4
SCORE_MULTIPLIER_SKILL_AREA_MENTIONED = 1

logger = logging.getLogger(__name__)

class SkillAnalyzer:

    def __init__(self):
        pass

    def isSkillInJobDescription(self, skill: dict, jobDescription: str) -> int:
        skillImportanceTotalScore = 0
        skillAliasMentioned = 0
        skillAreasMentioned = 0
        skillOnlyMentioned = 0
        incrementBy = 0
        jobDescriptionLS = jobDescription.lower().strip()
        # Can return immediately if marked as generic
        logger.info(f"--- Checking skill \"{skill['skill']}\" ---")
        if "generic" in skill["area"]:
            logger.info(f"\tMarked as the generic skill, adding +1 to score.")
            skillAreasMentioned += 1
        # Primary - precise skill match including small and capital letters
        incrementBy = jobDescription.count(skill["skill"]) if skill["is_case_sensitive"] else jobDescriptionLS.count(skill["skill"].lower())
        logger.info(f"\t\"{skill['skill']}\" mentioned {incrementBy} times.")
        skillOnlyMentioned += incrementBy
        # Secondary - precise alias match including small and capital letters
        for alias in skill["alias"]:
            incrementBy = jobDescription.count(alias) if skill["is_case_sensitive"] else jobDescriptionLS.count(alias.lower())
            logger.info(f"\tAlias \"{alias}\" mentioned {incrementBy} times.")
            skillAliasMentioned += incrementBy
        # Tertiary - non-precise area match ignoring small and capital letters
        for area in skill["area"]:
            # Skip "generic" area
            if area == "generic":
                continue
            incrementBy = jobDescriptionLS.count(area.lower())
            logger.info(f"\tArea \"{area}\" mentioned {incrementBy} times.")
            skillAreasMentioned += incrementBy
        skillImportanceTotalScore = (skillOnlyMentioned * SCORE_MULTIPLIER_SKILL_MENTIONED +
                                skillAliasMentioned * SCORE_MULTIPLIER_SKILL_ALIAS_MENTIONED +
                                skillAreasMentioned * SCORE_MULTIPLIER_SKILL_AREA_MENTIONED)
        logger.info(f"\tScore: {skillImportanceTotalScore}.\n" + ("-" * 66))
        return skillImportanceTotalScore