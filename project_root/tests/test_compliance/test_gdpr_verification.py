"""
-----------------------------
Tests unitaires pour gdpr_verification.py
Vérifie la conformité aux règles GDPR : suppression et anonymisation des données.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.compliance import gdpr_verification

class TestGDPRVerification(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.gdpr = gdpr_verification.GDPRVerifier()

        self.user_data = {
            "user_id": "123",
            "email": "alice@example.com",
            "name": "Alice",
            "transactions": [{"id": "tx1", "amount": 100}]
        }

    def test_request_deletion_success(self):
        """Test suppression d’un utilisateur"""
        result = self.gdpr.request_deletion(self.user_data)
        self.assertTrue(result)
        self.assertNotIn("email", self.user_data)
        self.assertNotIn("name", self.user_data)

    def test_anonymize_data(self):
        """Test pseudonymisation des données personnelles"""
        anonymized = self.gdpr.anonymize_data(self.user_data)
        self.assertNotEqual(anonymized["email"], "alice@example.com")
        self.assertNotEqual(anonymized["name"], "Alice")
        self.assertIn("user_id", anonymized)  # ID conservé pour traçabilité

    @patch("src.compliance.gdpr_verification.logging.info")
    def test_log_gdpr_action(self, mock_logging_info):
        """Test journalisation des actions GDPR"""
        self.gdpr.request_deletion(self.user_data)
        mock_logging_info.assert_called_once()

    def test_request_deletion_invalid_user(self):
        """Test suppression pour données invalides"""
        invalid_user = {}
        result = self.gdpr.request_deletion(invalid_user)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
