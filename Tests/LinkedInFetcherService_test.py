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
# LinkedInFetcherService class unit tests

import pytest, os
from Core.Fetchers.LinkedIn.LinkedInFetcherService import LinkedInFetcherService, DEFAULT_COOKIE_FILE
import User

class TestLinkedInFetcherService:

    @pytest.fixture
    def SetUp(self):
        return True

    def test_CreateDefaultLinkedInFetcherServiceObject(self):
        fetcherService = LinkedInFetcherService()
        assert fetcherService is not None
        assert fetcherService.username is None
        assert fetcherService.password is None
        assert fetcherService.browser is None

    def test_CreateLinkedInFetcherServiceObject(self):
        fetcherService = LinkedInFetcherService(username="aaa", password="bbb")
        assert fetcherService is not None
        assert fetcherService.username == "aaa"
        assert fetcherService.password == "bbb"

    #@pytest.mark.skip(reason="Speed up")
    def test_SignIn(self):
        fetcherService = LinkedInFetcherService()
        resultSuccess = fetcherService._signIn(storeCookies=False)
        assert resultSuccess

    #@pytest.mark.skip(reason="Speed up")
    def test_SignInWithCookies(self):
        cookieFile = os.path.join(os.path.dirname(User.__file__), DEFAULT_COOKIE_FILE)
        fetcherService = LinkedInFetcherService(cookiesFileDir=cookieFile)
        resultSuccess = fetcherService._signIn(storeCookies=True)
        assert resultSuccess

    #@pytest.mark.skip(reason="Speed up")
    def test_ParseSavedJobsPage(self):
        fetcherService = LinkedInFetcherService()
        fetcherService._signIn(storeCookies=True)
        savedJobs = fetcherService._parseSavedJobsPage()
        assert type(savedJobs) is list

    #@pytest.mark.skip(reason="Speed up")
    def test_ParseJobPagesForDetails(self):
        fetcherService = LinkedInFetcherService()
        fetcherService._signIn(storeCookies=True)
        savedJobs = fetcherService._parseSavedJobsPage()
        fetcherService._parseJobPagesForDetails(savedJobs)
        assert type(savedJobs) is list

    #@pytest.mark.skip(reason="Speed up")
    def test_GetSavedJobs(self):
        cookieFile = os.path.join(os.path.dirname(User.__file__), DEFAULT_COOKIE_FILE)
        fetcherService = LinkedInFetcherService(cookiesFileDir=cookieFile)
        savedJobs = fetcherService.getSavedJobs()
        assert type(savedJobs) is list