import unittest
from unittest.mock import patch

from fastapi import HTTPException

from api.routes.admin import require_admin
from core.config import settings


class AdminAuthTests(unittest.TestCase):
    def test_rejects_missing_configuration(self):
        with patch.object(settings, "ADMIN_TOKEN", ""):
            with self.assertRaises(HTTPException) as error:
                require_admin("token")
        self.assertEqual(error.exception.status_code, 503)

    def test_rejects_invalid_token(self):
        with patch.object(settings, "ADMIN_TOKEN", "correct"):
            with self.assertRaises(HTTPException) as error:
                require_admin("wrong")
        self.assertEqual(error.exception.status_code, 401)

    def test_accepts_correct_token(self):
        with patch.object(settings, "ADMIN_TOKEN", "correct"):
            require_admin("correct")


if __name__ == "__main__":
    unittest.main()
