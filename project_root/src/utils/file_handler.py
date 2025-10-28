"""
----------------
Lecture et écriture sécurisées de fichiers avec chiffrement AES-256 et vérification d’intégrité.

Fonctionnalités :
- Lecture/écriture de fichiers texte ou binaires
- Hachage SHA-256 pour vérifier l’intégrité
- Chiffrement/déchiffrement AES-256 (optionnel)
- Gestion d’erreurs et logging
"""

import os
import logging
import hashlib
from typing import Optional
from encryption_utils import encrypt_data, decrypt_data

# Configuration du logger
logger = logging.getLogger("file_handler")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# --- Fonctions utilitaires --- #

def compute_file_hash(filepath: str) -> str:
    """Calcule le hachage SHA-256 d’un fichier."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        logger.error(f"Fichier introuvable : {filepath}")
        raise
    except Exception as e:
        logger.error(f"Erreur lors du calcul du hash : {e}")
        raise


# --- Lecture sécurisée --- #

def secure_read(filepath: str, encryption_key: Optional[bytes] = None, binary: bool = False) -> bytes:
    """
    Lit un fichier de manière sécurisée.
    Si une clé AES est fournie, le contenu est déchiffré avant d’être retourné.
    """
    mode = "rb" if binary else "r"
    try:
        with open(filepath, mode) as f:
            data = f.read()
        logger.info(f"Lecture réussie : {filepath}")

        # Déchiffrement si nécessaire
        if encryption_key:
            logger.info("Déchiffrement des données…")
            data = decrypt_data(data, encryption_key)

        return data

    except Exception as e:
        logger.error(f"Erreur de lecture sécurisée : {e}")
        raise


# --- Écriture sécurisée --- #

def secure_write(filepath: str, data, encryption_key: Optional[bytes] = None, binary: bool = False) -> None:
    """
    Écrit un fichier de manière sécurisée.
    Si une clé AES est fournie, le contenu est chiffré avant d’être enregistré.
    """
    mode = "wb" if binary else "w"
    try:
        if encryption_key:
            logger.info("Chiffrement des données avant écriture…")
            data = encrypt_data(data, encryption_key)

        with open(filepath, mode) as f:
            f.write(data)
        logger.info(f"Écriture réussie : {filepath}")

    except Exception as e:
        logger.error(f"Erreur d’écriture sécurisée : {e}")
        raise


# --- Vérification d’intégrité --- #

def verify_file_integrity(filepath: str, expected_hash: str) -> bool:
    """
    Vérifie que le hachage SHA-256 du fichier correspond à la valeur attendue.
    """
    actual_hash = compute_file_hash(filepath)
    if actual_hash == expected_hash:
        logger.info(f"Intégrité vérifiée pour : {filepath}")
        return True
    else:
        logger.warning(f"Intégrité compromise pour : {filepath}")
        return False


# --- Exemple d’utilisation --- #
if __name__ == "__main__":
    test_file = "secure_test.txt"
    secret_key = os.urandom(32)

    secure_write(test_file, "Texte confidentiel à protéger", encryption_key=secret_key)
    content = secure_read(test_file, encryption_key=secret_key)
    print("Contenu déchiffré :", content)
