import unittest
from unittest.mock import Mock, patch

from api.routes.preview import deals_preview


class PreviewFilterTests(unittest.TestCase):
    def test_day_filter_is_passed_to_deal_service_and_preserved(self):
        venue_response = Mock(data=[])
        client = Mock()
        client.table.return_value.select.return_value.execute.return_value = venue_response
        with patch(
            "api.routes.preview.get_all_deals",
            return_value=[],
        ) as get_deals, patch("api.routes.preview.get_client", return_value=client):
            response = deals_preview(deal_type=None, tag=None, day="friday")

        get_deals.assert_called_once_with(
            deal_type=None,
            tag=None,
            day="friday",
        )
        self.assertIn('name="day"', response.body.decode())
        self.assertIn('value="friday" selected', response.body.decode())


if __name__ == "__main__":
    unittest.main()
