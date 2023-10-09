import requests
from loguru import logger

from scraper import Scraper


class Tyszkiewicz(Scraper):
    url = "https://www.tyszkiewicz.pl/index.php"
    default_params = {
        "id": "9",
        "lang": "pl",
        "page": "1",
    }

    @staticmethod
    def _add_page_to_params(page: int, params: dict) -> dict:
        params["page"] = page
        return params

    def process_html(self, html_text: str) -> list[dict]:
        pass


