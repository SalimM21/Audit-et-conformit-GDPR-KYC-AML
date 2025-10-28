"""
------------------------
Tests unitaires pour alerting_system.py
Vérifie l’envoi d’alertes et la génération correcte des messages.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.audit import alerting_system

class TestAlertingSystem(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.alert_system = alerting_system.AlertingSystem()

    @patch("src.audit.alerting_system.smtplib.SMTP")
    def test_send_email_alert_success(self, mock_smtp):
        """Test envoi d’alerte email avec succès"""
        mock_server = mock_smtp.return_value
        mock_server.sendmail.return_value = {}

        result = self.alert_system.send_email_alert(
            subject="Alerte Critique",
            message="Une activité suspecte a été détectée",
            to_addresses=["security@example.com"]
        )
        self.assertTrue(result)
        mock_server.sendmail.assert_called_once()

    @patch("src.audit.alerting_system.smtplib.SMTP")
    def test_send_email_alert_failure(self, mock_smtp):
        """Test gestion d’échec d’envoi d’email"""
        mock_server = mock_smtp.return_value
        mock_server.sendmail.side_effect = Exception("SMTP Error")

        result = self.alert_system.send_email_alert(
            subject="Alerte Critique",
            message="Erreur détectée",
            to_addresses=["security@example.com"]
        )
        self.assertFalse(result)

    def test_format_alert_message(self):
        """Test génération du message d’alerte formaté"""
        alert_info = {"user": "John", "action": "login", "level": "HIGH"}
        message = self.alert_system.format_alert_message(alert_info)
        self.assertIn("John", message)
        self.assertIn("login", message)
        self.assertIn("HIGH", message)

    @patch("src.audit.alerting_system.logging.info")
    def test_log_alert(self, mock_logging_info):
        """Test journalisation de l’alerte"""
        alert_info = {"user": "Jane", "action": "download", "level": "CRITICAL"}
        self.alert_system.log_alert(alert_info)
        mock_logging_info.assert_called_once()

if __name__ == "__main__":
    unittest.main()
