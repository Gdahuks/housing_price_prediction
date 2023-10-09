from abc import abstractmethod

import requests
from loguru import logger


class Scraper:

    def __init__(self):
        if self.url is None:
            raise NotImplementedError("You must set url in subclass")
        if self.default_params is None:
            raise NotImplementedError("You must set default_params in subclass")

    @staticmethod
    @abstractmethod
    def _add_page_to_params(page: int, params: dict) -> dict:
        pass

    def get_page(self, page: int) -> str:
        params = self._add_page_to_params(page, self.default_params)
        try:
            html_text = Scraper.get_html(self.url, **{"params": params})
            return html_text
        except Exception as e:
            logger.error(f"Error fetching {self.url}, params: {params}")
            raise e from e

    @staticmethod
    def get_html(url: str, **kwargs: dict) -> str:
        logger.info(f"Fetching {url}...")
        request = requests.get(url, **kwargs)
        if request.status_code == 200:
            logger.info(f"Success! {request.status_code}")
            return request.text

        logger.error(f"Error fetching {url}: status code {request.status_code}")
        raise RuntimeError(f"Error fetching {url}: status code {request.status_code}")
