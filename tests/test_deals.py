import unittest
from datetime import date

from services.deals import is_visible


class DealVisibilityTests(unittest.TestCase):
    def test_legacy_deal_without_expiry_is_visible(self):
        self.assertTrue(is_visible({"description": "Legacy deal"}))

    def test_expired_deal_is_hidden(self):
        self.assertFalse(is_visible({
            "status": "verified",
            "valid_until": date(2020, 1, 1),
        }))

    def test_explicitly_expired_deal_is_hidden(self):
        self.assertFalse(is_visible({"status": "expired"}))

if __name__ == "__main__":
    unittest.main()
