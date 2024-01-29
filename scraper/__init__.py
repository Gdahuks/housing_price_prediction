from __future__ import annotations

import time
from abc import abstractmethod, ABC
from typing import Iterator, Type, Final

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from loguru import logger


class Scraper(ABC):
    FLOOR_ENDS_WITH_TEXT: Final[tuple[str, ...]] = (
        "parter",
        "parterowy",
        "parterowe",
        "parterowa",
    )

    @staticmethod
    @abstractmethod
    def run_crawler() -> Iterator[dict]:
        pass

    @staticmethod
    @abstractmethod
    def get_offers(soup: BeautifulSoup) -> ResultSet[Tag]:
        pass

    @staticmethod
    @abstractmethod
    def process_tag(tag: Tag) -> dict[str, str | None] | None:
        pass

    @staticmethod
    def process_html(  # pylint: disable=inconsistent-return-statements
        self_type: Type[Scraper], html_text: str
    ) -> Iterator[dict] | None:
        soup = BeautifulSoup(html_text, features="lxml")
        offers = self_type.get_offers(soup)

        if offers is None or len(offers) == 0:
            logger.warning("No offers found")
            return None

        for offer in offers:
            yield self_type.process_tag(offer)

    @staticmethod
    def get_html(url: str, sleep: int = 10, **kwargs: dict) -> str:
        if sleep > 150:
            raise RuntimeError("Sleep time exceeded 150 seconds")
        logger.info(f"Fetching {url}... {kwargs}")
        request = requests.get(url, timeout=10, **kwargs)
        if request.status_code == 200:
            logger.info(f"Success! {request.status_code}")
            return request.text
        if request.status_code == 429:
            logger.warning(f"Too many requests (429). Sleeping for {sleep} seconds")
            time.sleep(sleep)
            sleep *= 2
            return Scraper.get_html(url, sleep, **kwargs)

        logger.error(f"Error fetching {url}: status code {request.status_code}")
        raise RuntimeError(f"Error fetching {url}: status code {request.status_code}")
