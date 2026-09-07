import unittest

from scraper.validator import clean_deals


class ValidatorTests(unittest.TestCase):
    VENUE_ID = "venue-1"

    def test_accepts_overnight_deal(self):
        deals = [{
            "venue_id": self.VENUE_ID,
            "description": "Late night drinks",
            "start_time": "22:00",
            "end_time": "02:00",
            "days_of_week": ["friday"],
        }]

        result = clean_deals(deals, {self.VENUE_ID})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start_time"], "22:00")

    def test_rejects_equal_start_and_end(self):
        deals = [{
            "venue_id": self.VENUE_ID,
            "description": "All day offer",
            "start_time": "12:00",
            "end_time": "12:00",
            "days_of_week": ["monday"],
        }]

        self.assertEqual(clean_deals(deals, {self.VENUE_ID}), [])

    def test_deduplicates_normalized_deals(self):
        deal = {
            "venue_id": self.VENUE_ID,
            "description": "Happy hour",
            "start_time": "16:00:00",
            "end_time": "18:00",
            "days_of_week": ["friday"],
        }

        self.assertEqual(len(clean_deals([deal.copy(), deal.copy()], {self.VENUE_ID})), 1)


if __name__ == "__main__":
    unittest.main()
