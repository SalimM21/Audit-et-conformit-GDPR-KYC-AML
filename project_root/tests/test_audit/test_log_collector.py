"""
----------------------
Tests unitaires pour log_collector.py
Vérifie la collecte des logs depuis API, DB et systèmes.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.audit import log_collector


class TestLogCollector(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.collector = log_collector.LogCollector()

    @patch("src.audit.log_collector.requests.get")
    def test_collect_api_logs_success(self, mock_get):
        """Test de collecte des logs depuis API"""
        # Préparer la réponse simulée
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"event": "login", "user": "John"}]
        mock_get.return_value = mock_response

        logs = self.collector.collect_api_logs("http://fake-api.com/logs")
        self.assertIsInstance(logs, list)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["event"], "login")

    @patch("src.audit.log_collector.requests.get")
    def test_collect_api_logs_failure(self, mock_get):
        """Test comportement si l'API échoue"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        logs = self.collector.collect_api_logs("http://fake-api.com/logs")
        self.assertEqual(logs, [])

    @patch("src.audit.log_collector.psycopg2.connect")
    def test_collect_db_logs_success(self, mock_connect):
        """Test collecte des logs depuis la DB"""
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [("login", "Jane")]
        
        logs = self.collector.collect_db_logs()
        self.assertIsInstance(logs, list)
        self.assertEqual(logs[0]["event"], "login")
        self.assertEqual(logs[0]["user"], "Jane")

    @patch("src.audit.log_collector.os.listdir")
    @patch("src.audit.log_collector.open")
    def test_collect_system_logs(self, mock_open, mock_listdir):
        """Test collecte des logs systèmes"""
        mock_listdir.return_value = ["syslog1.log"]
        mock_file = MagicMock()
        mock_file.__enter__.return_value.readlines.return_value = ["2025-10-28 INFO Started"]
        mock_open.return_value = mock_file

        logs = self.collector.collect_system_logs("/var/logs")
        self.assertIsInstance(logs, list)
        self.assertIn("2025-10-28 INFO Started", logs[0])

if __name__ == "__main__":
    unittest.main()
