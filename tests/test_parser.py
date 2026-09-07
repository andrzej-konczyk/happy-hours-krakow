import unittest

from scraper.parser import parse_deal


class ParserTests(unittest.TestCase):
    def test_mock_parser_normalizes_polish_weekdays_and_times(self):
        result = parse_deal(
            "od poniedziałku do piątku w godz. 12:00 - 16:00 promocja",
            use_mock=True,
        )

        self.assertEqual(result["start_time"], "12:00")
        self.assertEqual(result["end_time"], "16:00")
        self.assertEqual(
            result["days_of_week"],
            ["monday", "tuesday", "wednesday", "thursday", "friday"],
        )

    def test_mock_parser_handles_pm_times(self):
        result = parse_deal(
            "Every Monday and Tuesday from 5pm to 7pm",
            use_mock=True,
        )

        self.assertEqual(result["start_time"], "17:00")
        self.assertEqual(result["end_time"], "19:00")


if __name__ == "__main__":
    unittest.main()
