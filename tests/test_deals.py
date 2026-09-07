import unittest
from datetime import date
from unittest.mock import Mock, patch

from services.deals import get_all_deals, is_visible


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

    def test_deals_are_paginated_after_filters(self):
        rows = [
            {"id": index, "description": f"Deal {index}"}
            for index in range(5)
        ]
        response = Mock(data=rows)
        client = Mock()
        client.table.return_value.select.return_value.execute.return_value = response
        with patch("services.deals.get_client", return_value=client):
            result = get_all_deals(limit=2, offset=1)
        self.assertEqual([deal["id"] for deal in result], [1, 2])

if __name__ == "__main__":
    unittest.main()
