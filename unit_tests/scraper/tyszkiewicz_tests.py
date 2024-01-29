import unittest
from scraper.tyszkiewicz import Tyszkiewicz


# pylint: disable=protected-access
class TyszkiewiczTests(unittest.TestCase):
    def test_process_price_comma(self) -> None:
        text = "50 000,93 zł m2"
        expected_prices = "50000.93"
        self.assertEqual(Tyszkiewicz._process_price(text), expected_prices)

    def test__process_price_with_dot(self) -> None:
        text = "50 000.93 zł m2"
        expected_prices = "50000.93"
        self.assertEqual(Tyszkiewicz._process_price(text), expected_prices)

    def test__process_price_with_small_price(self) -> None:
        text = "50.93 zł m2"
        expected_prices = "50.93"
        self.assertEqual(Tyszkiewicz._process_price(text), expected_prices)

    def test__process_price_with_huge_price(self) -> None:
        text = "500 000000.93 zł m2"
        expected_prices = "500000000.93"
        self.assertEqual(Tyszkiewicz._process_price(text), expected_prices)

    def test__process_price_with_no_price(self) -> None:
        text = "zł m2"
        self.assertRaises(ValueError, Tyszkiewicz._process_price, text)


if __name__ == "__main__":
    unittest.main()
