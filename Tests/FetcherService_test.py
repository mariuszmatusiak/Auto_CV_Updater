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
from Core.Fetchers.JustJoinIT.JustJoinITFetcherService import JustJoinITFetcherService
from Core.Fetchers.JustJoinIT.JustJoinITFetcherService import DEFAULT_COOKIE_FILE as JJIT_DEFAULT_COOKIE_FILE
from Core.Fetchers.LinkedIn.LinkedInFetcherService import LinkedInFetcherService
from Core.Fetchers.LinkedIn.LinkedInFetcherService import DEFAULT_COOKIE_FILE as LIN_DEFAULT_COOKIE_FILE
from urllib.parse import urlparse
import User

@pytest.mark.parametrize("FetcherClassName,DEFAULT_COOKIE_FILE", [(JustJoinITFetcherService, JJIT_DEFAULT_COOKIE_FILE), (LinkedInFetcherService, LIN_DEFAULT_COOKIE_FILE)])
class TestFetcherService:

    @pytest.fixture
    def SetUp(self):
        return True

    def test_CreateDefaultFetcherServiceObject(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        fetcherService = FetcherClassName()
        assert fetcherService is not None
        assert fetcherService.username is None
        assert fetcherService.password is None
        assert fetcherService.browser is None

    def test_CreateFetcherServiceObject(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        fetcherService = FetcherClassName(username="aaa", password="bbb")
        assert fetcherService is not None
        assert fetcherService.username == "aaa"
        assert fetcherService.password == "bbb"

    # @pytest.mark.skip(reason="Speed up")
    def test_SignIn(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        fetcherService = FetcherClassName()
        resultSuccess = fetcherService._signIn(storeCookies=False)
        assert resultSuccess

    # @pytest.mark.skip(reason="Speed up")
    def test_SignInWithCookies(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        cookieFile = os.path.join(os.path.dirname(User.__file__), DEFAULT_COOKIE_FILE)
        fetcherService = FetcherClassName(cookiesFileDir=cookieFile)
        resultSuccess = fetcherService._signIn(storeCookies=True)
        assert resultSuccess

    # @pytest.mark.skip(reason="Speed up")
    def test_ParseSavedJobsPage(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        cookieFile = os.path.join(os.path.dirname(User.__file__), DEFAULT_COOKIE_FILE)
        fetcherService = FetcherClassName(cookiesFileDir=cookieFile)
        resultSuccess = fetcherService._signIn(storeCookies=True)
        savedJobUrls = fetcherService._parseSavedJobsPage()
        assert type(savedJobUrls) is set
        for jobUrl in savedJobUrls:
            parseResult = urlparse(url=jobUrl)
            assert parseResult.netloc
            assert parseResult.scheme

    # @pytest.mark.skip(reason="Speed up")
    def test_ParseJobPagesForDetails(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        cookieFile = os.path.join(os.path.dirname(User.__file__), DEFAULT_COOKIE_FILE)
        fetcherService = FetcherClassName(cookiesFileDir=cookieFile)
        resultSuccess = fetcherService._signIn(storeCookies=True)
        savedJobUrls = fetcherService._parseSavedJobsPage()
        savedJobs = fetcherService._parseJobPagesForDetails(savedJobUrls)
        assert type(savedJobs) is list
        for job in savedJobs:
            assert job.company
            assert job.job
            assert job.url
            assert job.details

    #@pytest.mark.skip(reason="Speed up")
    def test_GetSavedJobs(self, FetcherClassName, DEFAULT_COOKIE_FILE):
        cookieFile = os.path.join(os.path.dirname(User.__file__), DEFAULT_COOKIE_FILE)
        fetcherService = FetcherClassName(cookiesFileDir=cookieFile)
        savedJobs = fetcherService.getSavedJobs()
        assert type(savedJobs) is list
        for job in savedJobs:
            assert job.company
            assert job.job
            assert job.url
            assert job.details