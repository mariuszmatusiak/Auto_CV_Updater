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
# ResumeUpdater class unit tests

import pytest
from Core.ResumeUpdater import ResumeUpdater

class TestResumeUpdater:

    def test_ToLaTeXString(self):
        assert "{TCP~IP/1}" == ResumeUpdater._toLaTeXString("TCP/IP", True)
        assert "{C\\#}" == ResumeUpdater._toLaTeXString("C#", False)
        assert "{Embedded~systems/1}" == ResumeUpdater._toLaTeXString("Embedded systems", True)
        assert "{Digital Signal Processing}" == ResumeUpdater._toLaTeXString("Digital Signal Processing", False)

