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

from enum import Enum
from anyascii import anyascii
import logging

logger = logging.getLogger(__name__)

class Job:
    """Job class.
    """
    VISA_REQUIRED_COUNTRIES = ("United States", "USA", "U.S.", "U.S.A.", "US", "United Kingdom", "UK", "U.K.", "Canada", "Australia",
                               "New Zealand", "Switzerland",)
    OUTPUT_ENCODING="utf-8"
    class OUTPUT_ENCODING_ERROR_HANDLING(Enum):
        STRICT  = "strict"
        IGNORE  = "ignore"
        REPLACE = "replace"

    # Reserved LaTeX characters
    LATEX_CHARS_TO_ESCAPE_TRANSTABLE = str.maketrans({
        "\\": "\\\\",
        "%": "\\%",
        "$": "\\$",
        "{": "\\{",
        "_": "\\_",
        "#": "\\#",
        "&": "\\&",
        "}": "\\}"
    })

    def __init__(self, company: str = None, job: str = None, location: str = None, url: str = None,
                    details: str = None, letterAddress: str = None,
                    letterRecipient: str = None, isVisaRequired: bool = None):
        """Job class constructor.

        Args:
            company (str): job company
            job (str): job name
            location (str): job location
            url (str): job url
            details (str, optional): job description. Defaults to None.
            letterAddress (str, optional): cover letter recipient address. Defaults to None.
            letterRecipient (str, optional): cover letter recipient name. Defaults to None.
            isVisaRequired (str, optional): determines if job visa required ("1"). Defaults to None.
        """
        self.company = company
        self.job = job
        self.location = location
        self.url = url
        self.details = details
        self.letterAddress = location if letterAddress is None else letterAddress
        self.letterRecipient = company if letterRecipient is None else letterRecipient
        self.visaRequired = isVisaRequired if isVisaRequired is not None else True if location in Job.VISA_REQUIRED_COUNTRIES else False

    def toEncodedByteSequence(param: str) -> bytes:
        return param.encode(encoding=Job.OUTPUT_ENCODING, errors=Job.OUTPUT_ENCODING_ERROR_HANDLING.IGNORE)

    def escapeLatexCharacters(self, text: str) -> str:
        # First cast any Unicode to ascii
        asciiText = anyascii(text)
        # Secondly, cast to LaTeX compatible string
        return asciiText.translate(Job.LATEX_CHARS_TO_ESCAPE_TRANSTABLE)

    def _formatAsALatexField(self, arg: str | bool):
        # Perform a set of operations to preprocess text as a
        # LaTeX-compatible. TODO Consider appropriate encoding.
        # return self.toEncodedByteSequence(self.company)
        if isinstance(arg, bool):
            # Boolean visa field
            if arg:
                return "1"
            else:
                return "0"
        else:
            # Other string fields
            formattedText = self.escapeLatexCharacters(arg)
            if arg != formattedText:
                logger.debug(f"LaTeX -> Escaped {arg} -> {formattedText}")
            # TODO Other operations if needed...
            return formattedText

    def getCompany(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.company)
        else:
            return self.company

    def getJob(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.job)
        else:
            return self.job

    def getLocation(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.location)
        else:
            return self.location

    def getUrl(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.url)
        else:
            return self.url

    def getDetails(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.details)
        else:
            return self.details

    def setDetails(self, details : str):
        self.details = details

    def getLetterAddress(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.letterAddress)
        else:
            return self.letterAddress

    def getLetterRecipient(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.letterRecipient)
        else:
            return self.letterRecipient

    def isVisaRequired(self, asLatexResumeField: bool = False):
        if asLatexResumeField:
            return self._formatAsALatexField(self.visaRequired)
        else:
            return self.visaRequired



