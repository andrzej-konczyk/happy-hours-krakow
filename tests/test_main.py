import unittest

from main import home


class HomeRouteTests(unittest.TestCase):
    def test_home_redirects_to_preview(self):
        response = home()
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/deals/preview")


if __name__ == "__main__":
    unittest.main()
