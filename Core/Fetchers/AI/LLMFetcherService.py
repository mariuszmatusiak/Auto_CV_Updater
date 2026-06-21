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
# LLM fetcher service implementation.
# Supports obtaining jobs data from the My Saved Jobs.
#

from Core.Fetchers.IJobsFetcherService import IJobsFetcherService
from Core.Model.Job import Job
from Core.Model.WebBrowser import WebShell, WebBrowser

from openai import OpenAI
from pydantic import BaseModel
from enum import StrEnum
from abc import abstractmethod, ABCMeta
import logging

logger = logging.getLogger(__name__)

FETCHER_NAME = "LLM-based fetcher service (experimental)"

class LLMClient(metaclass=ABCMeta):

    NAME: str = None

    INSTRUCTION = "You are an expert at structured data extraction. " \
    "You will be given unstructured text from a job offer page and should convert it into the given structure." \
    "The `job_location` value shall be in the \"City, Country\" format or \"Country\" only if the city is not specified." \
    "If any of the values cannot be found, provide the empty string."

    class JobModel(BaseModel):
        company_name: str
        job_position_title: str
        job_location: str
        job_detailed_description: str
        key_skills_required: list[str]

    @abstractmethod
    def getJobData(self, jobPage : str) -> JobModel:
        pass

class GptClient(LLMClient): # using structured text.format. Structured Outputs (new models) vs JSON mode (old models)
    NAME = "ChatGPT"
    MODELS = [
        "gpt-4o-2024-08-06",
         # Structured Outputs with json_schema available
        "gpt-5.5",
        "gpt-5.4-mini",
        "gpt-5-mini",
        "gpt-5.4-nano",
        "gpt-5-nano",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-4-*",
        "gpt-4o-*" # JSON mode models
    ]
    HIGH_TOKEN_LEVEL_ALERT = 30000

    def __init__(self, apiKey : str):
        self.client = OpenAI(api_key=apiKey)

    def test(self):
        prompt = self.client.responses.create(
            model=GptClient.MODELS[2],
            input="Write a one-sentence bedtime story about a unicorn."
        )
        return prompt.output_text

    def countTokens(self, jobPage : str):
        prompt = self.client.responses.input_tokens.count(
            model=GptClient.MODELS[2],
            input=[
                {
                    "role": "system",
                    "content": LLMClient.INSTRUCTION
                },
                {
                    "role": "user",
                    "content": jobPage
                }
            ],
        )
        return prompt.input_tokens

    def getJobData(self, jobPage : str) -> LLMClient.JobModel:
        prompt = self.client.responses.parse(
            model=GptClient.MODELS[2],
            input=[
                {
                    "role": "system",
                    "content": LLMClient.INSTRUCTION
                },
                {
                    "role": "user",
                    "content": jobPage
                }
            ],
            text_format=LLMClient.JobModel # since Gpt-4o
        )
        return prompt.output_parsed

class SUPPORTED_LLMS(StrEnum):
    CHAT_GPT = GptClient.NAME
    #CLAUDE = "Claude"
    #COPILOT = "Copilot"

class LLMFetcherService(IJobsFetcherService):

    def __init__(self, jobUrls : list[str], model : SUPPORTED_LLMS, apiKey : str):
        super().__init__()
        self.fetcherName = FETCHER_NAME
        self.llm_model = model
        self.jobUrls = jobUrls
        self.browser = WebBrowser() if jobUrls else None
        match model:
            case SUPPORTED_LLMS.CHAT_GPT:
                self.client = GptClient(apiKey=apiKey)
            case _:
                self.client = None
        logger.debug("Created LLM Fetcher Service object")

    def __enter__(self):
        logger.debug("Entered LLM Fetcher Service object")
        return self

    def _extractJobData(self, jobUrl: str) -> Job:
        if self.browser is not None and self.browser.visit(jobUrl):
            pt = self.browser.getCurrentPageText()
            logger.debug(f"Job page {jobUrl} text:\n{pt}")
            #jm = self.client.getJobData(self.browser.getCurrentPageAsSoup().prettify())
            #jm = self.client.test()
            tokens = self.client.countTokens(pt)
            jm = None
            if tokens >= self.client.HIGH_TOKEN_LEVEL_ALERT: #TODO disable for headless
                logger.warning("The number of tokens is greater than %d (%d)", self.client.HIGH_TOKEN_LEVEL_ALERT, tokens)
                resp = input("Do you wish to continue? (Y/N): ")
                if resp in ["Y", "y"]:
                    jm = self.client.getJobData(pt)
            else:
                logger.info("Estimated number of input tokens: %d", tokens)
                jm = self.client.getJobData(pt)
            if jm:
                return Job(
                    company=jm.company_name,
                    job=jm.job_position_title,
                    location=jm.job_location,
                    url=jobUrl,
                    details=jm.job_detailed_description
                )
        return None

    def getSavedJobs(self) -> list[Job]:
        savedJobs = []
        for jobUrl in self.jobUrls:
            jd = self._extractJobData(jobUrl)
            if jd:
                savedJobs.append(jd)
        return savedJobs

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Cleaning up LLM Fetcher Service object")
        if self.browser is not None:
            self.browser.dispose()
            logger.debug("WebBrowser instance closed.")