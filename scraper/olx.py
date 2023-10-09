import requests


class Olx():
    url = "https://www.olx.pl/nieruchomosci/"

    def _add_page_to_params(self, params: dict, page: int) -> dict:
        params["page"] = page
        return params

