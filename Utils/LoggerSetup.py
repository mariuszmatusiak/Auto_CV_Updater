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

import logging, os
from datetime import datetime

class LoggerSetup:

    FILE_LOGGING_ENCODING = "utf-8"

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d")

    def init(self, toConsole: bool, toFile: bool, level=logging.DEBUG):
        # Get and configure the root logger
        rootLogger = logging.getLogger()
        rootLogger.setLevel(level)
        if toConsole:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setLevel(logging.INFO)
            consoleHandler.setFormatter(
                logging.Formatter("%(name)s %(levelname)s %(message)s")
            )
            rootLogger.addHandler(consoleHandler)
        if toFile:
            fileHandler = logging.FileHandler(
                filename=os.path.join("Logs", "updatecv_" + self.timestamp + ".log"),
                encoding=LoggerSetup.FILE_LOGGING_ENCODING
            )
            fileHandler.setFormatter(
                logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
            )
            rootLogger.addHandler(fileHandler)
        rootLogger.info("Root logger initialized.")
