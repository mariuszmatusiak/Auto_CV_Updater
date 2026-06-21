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
# Interface for job fetcher services.
#
# Version 1.0, 2025-03-27 - The initial version.

from Core.Model.Job import Job

from abc import abstractmethod, ABCMeta

import logging

logger = logging.getLogger(__name__)

class IJobsFetcherService(metaclass=ABCMeta):
    """An interface to fetch jobs through various methods.
    Implement this interface in your class while adding support to job details gathering methods.

    Args:
        ABC (ABCMeta): Standard Python Abstract Base Class.
    """

    def __init__(self):
        self.fetcherName = "Abstract Fetcher Service Name"

    def __enter__(self):
        logger.debug(f"Entered {self.fetcherName} Fetcher Service object")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f"Cleaning up {self.fetcherName} Fetcher Service object")

    @abstractmethod
    def getSavedJobs(self) -> list[Job]:
        pass
