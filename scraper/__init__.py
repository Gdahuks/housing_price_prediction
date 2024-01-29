from __future__ import annotations

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
    def process_html(self: Type[Scraper], html_text: str) -> Iterator[dict] | None:
        soup = BeautifulSoup(html_text, features="lxml")
        offers = self.get_offers(soup)

        if offers is None or len(offers) == 0:
            logger.warning("No offers found")
            return

        for offer in offers:
            yield self.process_tag(offer)

    @staticmethod
    def get_html(url: str, **kwargs: dict) -> str:
        logger.info(f"Fetching {url}...")
        request = requests.get(url, timeout=10, **kwargs)
        if request.status_code == 200:
            logger.info(f"Success! {request.status_code}")
            return request.text

        logger.error(f"Error fetching {url}: status code {request.status_code}")
        raise RuntimeError(f"Error fetching {url}: status code {request.status_code}")
