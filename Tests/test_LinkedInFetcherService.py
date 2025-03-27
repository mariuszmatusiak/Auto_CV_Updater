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
# Test script for the LinkedInFetcherService.
#
# Version 0.1, 2025-03-27 - The initial version
#

import pytest

from SavedJobsFetchers.LinkedInFetcherService import LinkedInFetcherService

@pytest.fixture
def SetUp():
    print("Setting up for a test...")
    return True

def test_CreateLinkedInFetcherServiceObject():
    fetcherService = LinkedInFetcherService()
    print(fetcherService)
    assert fetcherService is not None

def test_CreateLinkedInFetcherServiceObject():
    fetcherService = LinkedInFetcherService(username="aaa", password="bbb")
    assert fetcherService is not None

def test_GetSavedJobs():
    fetcherService = LinkedInFetcherService()
    savedJobs = fetcherService.getSavedJobs()
    assert type(savedJobs) is list