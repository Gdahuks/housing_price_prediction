import re
from typing import Final, Iterator

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag
from loguru import logger

from scraper import Scraper


class OgloszeniaTrojmiasto(Scraper):
    URL_NEW: Final[str] = "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-pierwotny/mieszkanie/"
    URL_SECONDARY: Final[str] = "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-wtorny/mieszkanie"

    OFFERS_CLASS: Final[str] = "list--item--withPrice"

    max_pages: int = 300
    default_params: dict[str, str] = {
        "strona": "0",
    }

    @staticmethod
    def run_crawler() -> Iterator[dict]:
        params = OgloszeniaTrojmiasto.default_params.copy()
        for url in (OgloszeniaTrojmiasto.URL_NEW, OgloszeniaTrojmiasto.URL_SECONDARY):
            for page in range(1, OgloszeniaTrojmiasto.max_pages + 1):
                params["strona"] = str(page)
                try:
                    html_text = OgloszeniaTrojmiasto.get_html(url, 10, **{"params": params})
                except Exception as exception:
                    logger.error(f"Error fetching {url}, params: {params}. Error: {exception}")
                    continue

                try:
                    processed_html = OgloszeniaTrojmiasto.process_html(OgloszeniaTrojmiasto, html_text)
                    if processed_html is None:
                        break
                    first = next(processed_html)
                    first["source"] = url
                    yield first
                    for offer in processed_html:
                        offer["source"] = url
                        yield offer
                except StopIteration:
                    break  # no more pages (current page with no offers). raised by next(processed_html)
                except Exception as exception:
                    logger.error(f"Error processing {url}, params: {params}. \nPage: {html_text}. \nError: {exception}")
                    continue

                logger.success(f"Successfully processed {url}, params: {params}")

    @staticmethod
    def get_offers(soup: BeautifulSoup) -> ResultSet[Tag]:
        offers = soup.find_all("div", class_=OgloszeniaTrojmiasto.OFFERS_CLASS)

        return offers

    @staticmethod
    def process_tag(tag: Tag) -> dict[str, str | None] | None:
        result_dict: dict[str, str | None] = {}
        OgloszeniaTrojmiasto._extract_id(tag, result_dict)
        OgloszeniaTrojmiasto._extract_title(tag, result_dict)
        OgloszeniaTrojmiasto._extract_address(tag, result_dict)
        OgloszeniaTrojmiasto._extract_price(tag, result_dict)
        OgloszeniaTrojmiasto._extract_area_rooms_floor_year(tag, result_dict)
        return result_dict

    @staticmethod
    def _extract_id(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <div class="list__item list--item--special list--item--withPrice list--item--big"
        # data-ajax-prolongation="item" data-id="65567873" id="ogl-65567873">
        _id = offer.get("id")
        if _id is None:
            logger.warning("No id found")
            return

        result_dict["id"] = _id

    @staticmethod
    def _extract_title(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <a class="list__item__content__title__name link" data-stats-kat-id="106" data-stats-ogl="true"
        # data-stats-ogl-id="64305919" data-stats-place="ogl_list" href="https://ogloszenia.trojmiasto.pl/
        # nieruchomosci-rynek-pierwotny/pruszcz-park-3-a-39-narozne-3-pok-z-balkonem-na-iii-pietrze-ogl64305919.html"
        # title="Pruszcz Park 3.A.39 narożne 3 pok z balkonem na III piętrze">
        # Pruszcz Park 3.A.39 narożne 3 pok z balkonem na III piętrze</a>
        title = offer.find("a", class_="list__item__content__title__name link")
        if title is None or title.text is None:
            logger.warning("No title found")
            return

        result_dict["title"] = title.text

    @staticmethod
    def _extract_address(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <p class="list__item__content__subtitle">Pruszcz Gdański, Powstańców Warszawy 79</p>
        address = offer.find("p", class_="list__item__content__subtitle")

        if address is None or address.text is None:
            logger.warning("No address found")
            return

        result_dict["address"] = address.text

    @staticmethod
    def _extract_price(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <div class="list__item__picture__price">
        # <p>350 000 zł</p>
        # </div>

        price = offer.find("div", class_="list__item__picture__price")
        if price is None or price.text is None:
            logger.warning("No price found")
            return

        price = price.find("p")
        if price is None or price.text is None:
            logger.warning("No price found")
            return

        result_dict["full_price"] = OgloszeniaTrojmiasto._process_price(price.text)

    @staticmethod
    def _process_price(price: str) -> str:
        return re.sub("[^0-9]", "", price)

    @staticmethod
    def _extract_area_rooms_floor_year(offer: Tag, result_dict: dict[str, str | None]) -> None:
        context = offer.find("ul", class_="list__item__details__icons")
        if context is None or context.text is None:
            logger.warning("No context found")
            return

        OgloszeniaTrojmiasto._extract_area(context, result_dict)
        OgloszeniaTrojmiasto._extract_rooms(context, result_dict)
        OgloszeniaTrojmiasto._extract_floor(context, result_dict)
        OgloszeniaTrojmiasto._extract_year(context, result_dict)

    @staticmethod
    def _extract_area(offer_context: Tag, result_dict: dict[str, str | None]) -> None:
        area = offer_context.find(
            "li", class_="list__item__details__icons__element details--icons--element--powierzchnia"
        )
        if area is None or area.text is None:
            logger.warning(f"No area found {offer_context.text}")
            return

        area = area.find("p", class_="list__item__details__icons__element__desc")
        if area is None or area.text is None:
            logger.warning(f"No area found {offer_context.text}")
            return

        result_dict["area"] = area.text.strip()

    @staticmethod
    def _extract_rooms(offer_context: Tag, result_dict: dict[str, str | None]) -> None:
        rooms = offer_context.find("li", class_="list__item__details__icons__element details--icons--element--l_pokoi")
        if rooms is None or rooms.text is None:
            logger.warning(f"No rooms found {offer_context.text}")
            return

        rooms = rooms.find("p", class_="list__item__details__icons__element__desc")
        if rooms is None or rooms.text is None:
            logger.warning(f"No rooms found {offer_context.text}")
            return

        result_dict["rooms"] = rooms.text.strip()

    @staticmethod
    def _extract_floor(offer_context: Tag, result_dict: dict[str, str | None]) -> None:
        floor = offer_context.find("li", class_="list__item__details__icons__element details--icons--element--pietro")
        if floor is None or floor.text is None:
            logger.warning(f"No floor found {offer_context.text}")
            return

        floor = floor.find("p", class_="list__item__details__icons__element__desc")
        if floor is None or floor.text is None:
            logger.warning(f"No floor found {offer_context.text}")
            return

        floor = floor.text.strip()

        if floor.lower().endswith(OgloszeniaTrojmiasto.FLOOR_ENDS_WITH_TEXT):
            floor = "0"
        elif re.fullmatch(r"\d+", floor):
            result_dict["floor"] = floor
        else:
            logger.warning(f"Invalid floor: {floor}")

    @staticmethod
    def _extract_year(offer_context: Tag, result_dict: dict[str, str | None]) -> None:
        year = offer_context.find(
            "li", class_="list__item__details__icons__element details--icons--element--rok_budowy"
        )
        if year is None or year.text is None:
            logger.warning(f"No year found {offer_context.text}")
            return

        year = year.find("p", class_="list__item__details__icons__element__desc")
        if year is None or year.text is None:
            logger.warning(f"No year found {offer_context.text}")
            return

        result_dict["year"] = year.text.strip()
