import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from api.routes.health import readiness_check
from core.config import settings


class ReadinessTests(unittest.TestCase):
    def test_rejects_missing_database_configuration(self):
        with patch.object(settings, "SUPABASE_URL", ""), patch.object(
            settings, "SUPABASE_KEY", ""
        ):
            with self.assertRaises(HTTPException) as error:
                readiness_check()
        self.assertEqual(error.exception.status_code, 503)

    def test_rejects_database_failure(self):
        client = Mock()
        client.table.side_effect = OSError("connection failed")
        with patch.object(settings, "SUPABASE_URL", "https://example.supabase.co"), patch.object(
            settings, "SUPABASE_KEY", "key"
        ), patch("api.routes.health.get_client", return_value=client):
            with self.assertRaises(HTTPException) as error:
                readiness_check()
        self.assertEqual(error.exception.status_code, 503)

    def test_reports_ready_when_database_responds(self):
        response = Mock()
        response.execute.return_value = Mock(data=[])
        client = Mock()
        client.table.return_value.select.return_value.limit.return_value = response
        with patch.object(settings, "SUPABASE_URL", "https://example.supabase.co"), patch.object(
            settings, "SUPABASE_KEY", "key"
        ), patch("api.routes.health.get_client", return_value=client):
            self.assertEqual(readiness_check(), {"status": "ready", "database": "ok"})


if __name__ == "__main__":
    unittest.main()
