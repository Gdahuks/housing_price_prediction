import re
from enum import Enum
from typing import Final, Iterator

from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from loguru import logger

from scraper import Scraper


class Tyszkiewicz(Scraper):
    URL: Final[str] = "https://www.tyszkiewicz.pl/index.php"
    OFFERS_CLASS: Final[str] = "offer__box bi wow fadeInUp promote-"
    ROOMS_ENDS_WITH: Final[tuple[str, ...]] = (
        "pokój",
        "pokoj",
        "pokoje",
        "pokoi",
        "pokojowa",
        "pokojowe",
        "pokojowy",
        "pokojowych",
        "pokojowa",
    )
    FLOOR_ENDS_WITH_NUMBER: Final[tuple[str, ...]] = (
        "piętro",
        "pietro",
        "piętrowy",
        "pietrowy",
        "piętrowe",
        "pietrowe",
        "piętrowa",
        "pietrowa",
    )
    PRICE_PATTERN: Final[re.Pattern[str]] = re.compile(r"[ \d]+[,.]?\d*")

    max_pages: int = 100
    default_params: dict[str, str] = {
        "id": "9",
        "lang": "pl",
        "page": "1",
    }

    class Categories(Enum):
        MIESZKANIE = "9"
        DOMY = "10"
        DZIALKI = "11"
        KOMERCYJNE = "12"

    @staticmethod
    def run_crawler() -> Iterator[dict]:
        params = Tyszkiewicz.default_params.copy()
        for category in Tyszkiewicz.Categories:
            params["id"] = category.value
            for page in range(1, Tyszkiewicz.max_pages + 1):
                params["page"] = str(page)
                try:
                    html_text = Tyszkiewicz.get_html(Tyszkiewicz.URL, 10, **{"params": params})
                except Exception as exception:
                    logger.error(f"Error fetching {Tyszkiewicz.URL}, params: {params}. Error: {exception}")
                    continue

                try:
                    processed_html = Tyszkiewicz.process_html(Tyszkiewicz, html_text)
                    if processed_html is None:
                        break
                    first = next(processed_html)
                    first["category"] = category.name
                    first["source"] = Tyszkiewicz.URL
                    yield first
                    for offer in processed_html:
                        offer["category"] = category.name
                        offer["source"] = Tyszkiewicz.URL
                        yield offer
                except StopIteration:
                    break  # no more pages (current page with no offers). raised by next(processed_html)
                except Exception as exception:
                    logger.error(
                        f"Error processing {Tyszkiewicz.URL}, params: {params}. \n"
                        f"Page: {html_text}. \nError: {exception}"
                    )
                    continue

                logger.success(f"Successfully processed {Tyszkiewicz.URL}, params: {params}")

    @staticmethod
    def get_offers(soup: BeautifulSoup) -> ResultSet[Tag]:
        offers = soup.find_all("div", class_=Tyszkiewicz.OFFERS_CLASS)

        return offers

    @staticmethod
    def process_tag(tag: Tag) -> dict[str, str | None] | None:
        result_dict: dict[str, str | None] = {}
        Tyszkiewicz._extract_id_and_date(tag, result_dict)
        Tyszkiewicz._extract_title(tag, result_dict)
        Tyszkiewicz._extract_price(tag, result_dict)
        Tyszkiewicz._extract_area_rooms_floor_year(tag, result_dict)
        return result_dict

    @staticmethod
    def _extract_id_and_date(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <div class="offer__box--number">NR: TY129477 2023-09-11</div>
        id_and_date = offer.find("div", class_="offer__box--number")
        if id_and_date is None or id_and_date.text is None:
            logger.warning("No date and id found")
            return

        id_and_date_splitted = id_and_date.text.split(" ")
        if len(id_and_date_splitted) != 3:
            logger.warning(f"Wrong date and id format: {id_and_date.text}")
            return

        result_dict["id"], result_dict["date"] = id_and_date.text.split(" ")[1:]

    @staticmethod
    def _extract_title(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <h2 class="offer__box--name"><a href="biura-po-remoncie-generalnym-z-placem-230m2,7770782">
        # Biura po remoncie generalnym z placem 230m2 Gdańsk Letnica</a></h2>
        title = offer.find("h2", class_="offer__box--name")
        if title is None or title.text is None:
            logger.warning("No title found")
            return

        title = title.find("a")
        if title is None or title.text is None:
            logger.warning("No title found")
            return

        result_dict["title"] = title.text

    @staticmethod
    def _extract_price(offer: Tag, result_dict: dict[str, str | None]) -> None:
        # <div class="offer__box--prices">
        #     <div class="offer__box--price">5 500,00 zł</div>
        #     <div class="offer__box--pricePer">50,93 zł m<sup class="sup">2</sup></div>
        # </div>
        prices = offer.find("div", class_="offer__box--prices")
        if prices is None or prices.text is None:
            logger.warning("No prices found")
            return

        full_price = prices.find("div", class_="offer__box--price")
        if full_price is None or full_price.text is None:
            logger.warning("No full price found")
        else:
            try:
                result_dict["full_price"] = Tyszkiewicz._process_price(full_price.text)
            except ValueError:
                logger.warning(f"Could not process full price: {full_price.text}")

        price_per_m2 = prices.find("div", class_="offer__box--pricePer")

        if price_per_m2 is None or price_per_m2.text is None:
            logger.warning("No price per m2 found")
        else:
            try:
                result_dict["price_per_m2"] = Tyszkiewicz._process_price(price_per_m2.text)
            except ValueError:
                logger.warning(f"Could not process price per m2: {price_per_m2.text}")

    @staticmethod
    def _process_price(price: str) -> str:
        matches = re.search(Tyszkiewicz.PRICE_PATTERN, price)
        if matches is None or matches.group(0) is None or matches.group(0).strip() == "":
            logger.error(f"Wrong price format: {price}")
            raise ValueError(f"Wrong price format: {price}")

        return matches.group(0).replace(" ", "").replace(",", ".")

    @staticmethod
    def _extract_area_rooms_floor_year(offer: Tag, result_dict: dict[str, str | None]) -> None:
        #         <div class="offer__box--basic bi d-c-b">
        #             <div class="offer__box--basicOne bi">108.00m<sup class="sup">2</sup></div>
        #             <div class="offer__box--basicOne bi">parter</div>
        #             <div class="offer__box--basicOne bi">2000 r</div>
        #         </div>
        fields = offer.find_all("div", class_="offer__box--basicOne bi")
        if fields is None or len(fields) == 0:
            logger.warning(f"No fields found in offer: {offer}")
            return

        fields = [field.text for field in fields]
        Tyszkiewicz._extract_area_from_fields(fields, result_dict)
        Tyszkiewicz._extract_rooms_from_fields(fields, result_dict)
        Tyszkiewicz._extract_floor_from_fields(fields, result_dict)
        Tyszkiewicz._extract_year_from_fields(fields, result_dict)

    @staticmethod
    def _extract_area_from_fields(fields: list[str], result_dict: dict[str, str | None]) -> None:
        _area = [re.search(r"(\d+\.\d+)|(\d+,\d+)", field) for field in fields if field.lower().endswith("m2")]

        area = [a.group(0) for a in _area if a is not None]

        if len(area) == 1:
            result_dict["area"] = area[0].replace(",", ".")
        elif len(area) > 1:
            logger.warning(f"More than one area found: {area}")
        else:
            logger.info(f"No area found: {fields}")

    @staticmethod
    def _extract_rooms_from_fields(fields: list[str], result_dict: dict[str, str | None]) -> None:
        _rooms = [re.search(r"\d+", field) for field in fields if field.lower().endswith(Tyszkiewicz.ROOMS_ENDS_WITH)]

        rooms = [r.group(0) for r in _rooms if r is not None]

        if len(rooms) == 1:
            result_dict["rooms"] = rooms[0]
        elif len(rooms) > 1:
            logger.warning(f"More than one room found: {rooms}")
        else:
            logger.info(f"No room found: {fields}")

    @staticmethod
    def _extract_floor_from_fields(fields: list[str], result_dict: dict[str, str | None]) -> None:
        results = []
        for field in fields:
            if field.endswith(Tyszkiewicz.FLOOR_ENDS_WITH_NUMBER):
                if (result := re.search(r"\d+", field)) is not None:
                    results.append(result.group(0))
            elif field.endswith(Tyszkiewicz.FLOOR_ENDS_WITH_TEXT):
                results.append("0")

        if len(results) == 1:
            result_dict["floor"] = results[0]
        elif len(results) > 1:
            logger.warning(f"More than one floor found: {results}")
        else:
            logger.info(f"No floor found: {fields}")

    @staticmethod
    def _extract_year_from_fields(fields: list[str], result_dict: dict[str, str | None]) -> None:
        _year = [re.search(r"\d+", field) for field in fields if field.lower().endswith(("r", "y"))]

        year = [y.group(0) for y in _year if y is not None]

        if len(year) == 1:
            result_dict["year"] = year[0]
        elif len(year) > 1:
            logger.warning(f"More than one year found: {year}")
        else:
            logger.info(f"No year found: {fields}")
