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

from Core.Model.WebBrowser import SUPPORTED_WEBBROWSERS
from enum import StrEnum

class SUPPORTED_VARIABLES:
    CV_DIR = "CV_DIR"
    LINKEDIN_KEY = "LIN_KEY"
    MAKE_EXEC = "MAKE_BIN"

class EnvironmentConfig:
    def __init__(self, sync: bool, skill_areas : list, recipient_file : str,
                 skills_file : str, skills_json : str, browser: SUPPORTED_WEBBROWSERS, headless : bool, cv_dir : str, make_exec : str,
                 linkedInCookies, justJoinItCookies):
        self.cv_dir = cv_dir
        self.sync = sync
        self.skill_areas = skill_areas
        self.recipient_file = recipient_file
        self.skills_file = skills_file
        self.skills_json = skills_json
        self.browser = browser
        self.headless = headless
        self.make_exec = make_exec
        self.services = {
            "linkedIn" : {
                "login": None,
                "password": None,
                "cookies": linkedInCookies
            },
            "justJoinIt" : {
                "login": None,
                "password": None,
                "cookies": justJoinItCookies
            }
        }