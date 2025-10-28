"""
----------------------
Tests unitaires pour kyc_audit.py
Vérifie la validité et la complétude des documents KYC.
"""

import unittest
from src.compliance import kyc_audit

class TestKYCAudit(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.audit = kyc_audit.KYCAudit()

        self.valid_user = {
            "user_id": "123",
            "name": "Alice",
            "dob": "1990-01-01",
            "documents": ["passport", "utility_bill"]
        }

        self.incomplete_user = {
            "user_id": "124",
            "name": "Bob",
            "dob": "1985-05-12",
            "documents": ["passport"]
        }

        self.invalid_user = {
            "user_id": "125",
            "name": "Charlie",
            "dob": "",
            "documents": []
        }

    def test_check_completeness_valid_user(self):
        """Utilisateur avec tous les documents requis"""
        result = self.audit.check_completeness(self.valid_user)
        self.assertTrue(result["is_complete"])
        self.assertEqual(result["missing_documents"], [])

    def test_check_completeness_incomplete_user(self):
        """Utilisateur avec documents manquants"""
        result = self.audit.check_completeness(self.incomplete_user)
        self.assertFalse(result["is_complete"])
        self.assertIn("utility_bill", result["missing_documents"])

    def test_check_completeness_invalid_user(self):
        """Utilisateur avec informations invalides"""
        result = self.audit.check_completeness(self.invalid_user)
        self.assertFalse(result["is_complete"])
        self.assertIn("passport", result["missing_documents"])
        self.assertIn("utility_bill", result["missing_documents"])

    def test_validate_dob_format(self):
        """Vérifie la validité de la date de naissance"""
        self.assertTrue(self.audit.validate_dob("1990-01-01"))
        self.assertFalse(self.audit.validate_dob("01-01-1990"))
        self.assertFalse(self.audit.validate_dob(""))

if __name__ == "__main__":
    unittest.main()
