"""
encryption_utils.py
-------------------
Ce module fournit des fonctions pour chiffrer et déchiffrer des données sensibles
en utilisant l’algorithme AES-256 (mode CBC) avec gestion des clés et IV.

Fonctionnalités :
- Chiffrement AES-256
- Déchiffrement AES-256
- Génération et stockage sécurisé de clés
- Compatible avec les données au repos et en transit
"""

import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import logging

logger = logging.getLogger("EncryptionUtils")


class EncryptionUtils:
    def __init__(self, key: bytes = None):
        """
        Initialise l'utilitaire de chiffrement.
        :param key: clé AES 32 bytes. Si None, une nouvelle clé sera générée.
        """
        if key and len(key) == 32:
            self.key = key
        else:
            self.key = get_random_bytes(32)
            logger.info("Nouvelle clé AES-256 générée.")
    
    def encrypt(self, plaintext: str) -> str:
        """Chiffre une chaîne de caractères et retourne le résultat en base64."""
        cipher = AES.new(self.key, AES.MODE_CBC)
        plaintext_bytes = plaintext.encode('utf-8')
        # Padding PKCS7
        pad_len = 16 - len(plaintext_bytes) % 16
        plaintext_bytes += bytes([pad_len]) * pad_len
        ciphertext = cipher.encrypt(plaintext_bytes)
        result = base64.b64encode(cipher.iv + ciphertext).decode('utf-8')
        logger.debug(f"Chiffrement réussi pour : {plaintext[:8]}...")
        return result

    def decrypt(self, b64_ciphertext: str) -> str:
        """Déchiffre une chaîne base64 chiffrée avec AES-256."""
        data = base64.b64decode(b64_ciphertext)
        iv = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext_bytes = cipher.decrypt(ciphertext)
        # Retirer padding PKCS7
        pad_len = plaintext_bytes[-1]
        plaintext_bytes = plaintext_bytes[:-pad_len]
        plaintext = plaintext_bytes.decode('utf-8')
        logger.debug(f"Déchiffrement réussi : {plaintext[:8]}...")
        return plaintext


if __name__ == "__main__":
    util = EncryptionUtils()
    secret = "Données très sensibles"
    
    encrypted = util.encrypt(secret)
    print("Encrypted:", encrypted)
    
    decrypted = util.decrypt(encrypted)
    print("Decrypted:", decrypted)
