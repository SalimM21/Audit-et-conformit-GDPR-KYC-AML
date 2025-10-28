"""
-----------------------------
Tests unitaires pour anonymization_utils.py
Vérifie la pseudonymisation et l’anonymisation des données sensibles.
"""

import unittest
from src.compliance import anonymization_utils

class TestAnonymizationUtils(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.sample_data = {
            "user_id": "123",
            "email": "alice@example.com",
            "name": "Alice",
            "phone": "+1234567890"
        }

    def test_hash_email(self):
        """Test de hachage de l'email"""
        hashed = anonymization_utils.hash_email(self.sample_data["email"])
        self.assertNotEqual(hashed, self.sample_data["email"])
        self.assertIsInstance(hashed, str)
        self.assertTrue(len(hashed) > 0)

    def test_mask_name(self):
        """Test de masquage du nom"""
        masked = anonymization_utils.mask_name(self.sample_data["name"])
        self.assertNotEqual(masked, self.sample_data["name"])
        self.assertTrue(all(c.isalpha() or c == "*" for c in masked))

    def test_anonymize_phone(self):
        """Test d’anonymisation du numéro de téléphone"""
        anonymized = anonymization_utils.anonymize_phone(self.sample_data["phone"])
        self.assertNotEqual(anonymized, self.sample_data["phone"])
        self.assertTrue(anonymized.endswith(self.sample_data["phone"][-2:]))

    def test_anonymize_full_data(self):
        """Test anonymisation complète d’un dictionnaire"""
        anonymized_data = anonymization_utils.anonymize_record(self.sample_data)
        self.assertNotEqual(anonymized_data["email"], self.sample_data["email"])
        self.assertNotEqual(anonymized_data["name"], self.sample_data["name"])
        self.assertNotEqual(anonymized_data["phone"], self.sample_data["phone"])
        self.assertEqual(anonymized_data["user_id"], self.sample_data["user_id"])

if __name__ == "__main__":
    unittest.main()
