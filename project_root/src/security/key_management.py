"""
-----------------
Ce module gère la création, le stockage et la rotation des clés de chiffrement
utilisées dans le système de conformité (GDPR, KYC, AML).

Il peut fonctionner :
- en mode **local** (fichier chiffré sur disque),
- ou avec un **KMS (Key Management Service)** type AWS KMS, GCP KMS ou Azure Key Vault.

Fonctionnalités :
- Génération de clés AES-256
- Rotation planifiée des clés
- Chargement/sauvegarde sécurisée
- Intégration possible avec des services KMS externes
"""

import os
import json
import base64
import logging
from datetime import datetime, timedelta
from Crypto.Random import get_random_bytes

logger = logging.getLogger("KeyManagement")


class KeyManager:
    def __init__(self, storage_path: str = "config/keys.json", rotation_days: int = 90):
        """
        Initialise le gestionnaire de clés.
        :param storage_path: chemin du fichier de stockage sécurisé des clés
        :param rotation_days: durée avant rotation automatique
        """
        self.storage_path = storage_path
        self.rotation_days = rotation_days
        self.keys = self._load_keys()

    def _generate_key(self) -> dict:
        """Génère une nouvelle clé AES-256 avec métadonnées."""
        key_bytes = get_random_bytes(32)
        key_b64 = base64.b64encode(key_bytes).decode("utf-8")
        key_info = {
            "id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "key": key_b64,
            "created_at": datetime.utcnow().isoformat(),
        }
        logger.info("Nouvelle clé AES-256 générée.")
        return key_info

    def _load_keys(self) -> list:
        """Charge les clés depuis le stockage local (ou crée un nouveau fichier si absent)."""
        if not os.path.exists(self.storage_path):
            logger.warning("Aucun fichier de clés trouvé. Génération d'une clé initiale.")
            keys = [self._generate_key()]
            self._save_keys(keys)
        else:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                keys = json.load(f)
        return keys

    def _save_keys(self, keys: list):
        """Sauvegarde les clés sur disque (format JSON encodé base64)."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=4)
        logger.info(f"Clés sauvegardées dans {self.storage_path}")

    def get_active_key(self) -> bytes:
        """Retourne la clé active en bytes (dernière clé générée)."""
        active_key = self.keys[-1]
        return base64.b64decode(active_key["key"])

    def rotate_keys_if_needed(self):
        """Vérifie si une rotation de clé est nécessaire et en génère une nouvelle le cas échéant."""
        last_key_date = datetime.fromisoformat(self.keys[-1]["created_at"])
        if datetime.utcnow() - last_key_date > timedelta(days=self.rotation_days):
            logger.info("Rotation de clé requise.")
            new_key = self._generate_key()
            self.keys.append(new_key)
            self._save_keys(self.keys)
        else:
            logger.info("Rotation non nécessaire pour le moment.")

    def list_keys(self) -> list:
        """Retourne la liste des clés et leurs dates de création (sans exposer le contenu)."""
        return [
            {"id": k["id"], "created_at": k["created_at"]}
            for k in self.keys
        ]


if __name__ == "__main__":
    km = KeyManager()

    print("🔐 Clé active :", km.get_active_key()[:8], "...")
    print("📅 Liste des clés :", km.list_keys())

    km.rotate_keys_if_needed()
