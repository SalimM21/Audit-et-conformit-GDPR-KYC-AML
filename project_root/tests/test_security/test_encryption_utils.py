"""
-----------------------------
Tests unitaires pour encryption_utils.py
Vérifie le chiffrement et le déchiffrement AES-256.
"""

import unittest
from src.security import encryption_utils

class TestEncryptionUtils(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.key = encryption_utils.generate_key()
        self.plain_text = "Données sensibles à protéger"

    def test_encrypt_decrypt(self):
        """Test que le texte chiffré peut être correctement déchiffré"""
        cipher_text = encryption_utils.encrypt_aes(self.plain_text, self.key)
        self.assertNotEqual(cipher_text, self.plain_text)
        
        decrypted_text = encryption_utils.decrypt_aes(cipher_text, self.key)
        self.assertEqual(decrypted_text, self.plain_text)

    def test_encrypt_returns_bytes(self):
        """Vérifie que le chiffrement retourne des bytes"""
        cipher_text = encryption_utils.encrypt_aes(self.plain_text, self.key)
        self.assertIsInstance(cipher_text, bytes)

    def test_decrypt_with_wrong_key(self):
        """Vérifie que le déchiffrement avec une mauvaise clé échoue"""
        wrong_key = encryption_utils.generate_key()
        cipher_text = encryption_utils.encrypt_aes(self.plain_text, self.key)
        with self.assertRaises(Exception):
            encryption_utils.decrypt_aes(cipher_text, wrong_key)

    def test_generate_key_length(self):
        """Vérifie que la clé générée a la bonne longueur (32 bytes pour AES-256)"""
        self.assertEqual(len(self.key), 32)

if __name__ == "__main__":
    unittest.main()
