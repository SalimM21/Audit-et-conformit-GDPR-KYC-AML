"""
---------------------
Tests unitaires pour aml_monitor.py
Vérifie la détection des transactions suspectes et le déclenchement des alertes AML.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.compliance import aml_monitor

class TestAMLMonitor(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.monitor = aml_monitor.AMLMonitor(threshold_amount=10000, watchlist=["John Doe", "Jane Smith"])

    def test_detect_large_transaction(self):
        """Test détection d’une transaction dépassant le seuil"""
        transaction = {"user": "Alice", "amount": 15000, "country": "US"}
        alerts = self.monitor.check_transaction(transaction)
        self.assertEqual(len(alerts), 1)
        self.assertIn("Transaction exceeds threshold", alerts[0])

    def test_detect_watchlist_user(self):
        """Test détection d’une transaction d’un utilisateur dans la watchlist"""
        transaction = {"user": "John Doe", "amount": 5000, "country": "UK"}
        alerts = self.monitor.check_transaction(transaction)
        self.assertEqual(len(alerts), 1)
        self.assertIn("User is on watchlist", alerts[0])

    def test_no_alerts_for_normal_transaction(self):
        """Test qu’une transaction normale ne déclenche pas d’alerte"""
        transaction = {"user": "Bob", "amount": 2000, "country": "FR"}
        alerts = self.monitor.check_transaction(transaction)
        self.assertEqual(len(alerts), 0)

    @patch("src.compliance.aml_monitor.logging.warning")
    def test_log_alerts_called(self, mock_logging_warning):
        """Test que les alertes sont correctement loguées"""
        transaction = {"user": "John Doe", "amount": 15000, "country": "US"}
        alerts = self.monitor.check_transaction(transaction)
        for alert in alerts:
            self.monitor.log_alert(alert)
        self.assertEqual(mock_logging_warning.call_count, len(alerts))

if __name__ == "__main__":
    unittest.main()
