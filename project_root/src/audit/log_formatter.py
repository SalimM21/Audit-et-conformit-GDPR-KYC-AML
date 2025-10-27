"""
==============================================================
 Fichier : log_formatter.py
 Auteur  : Équipe Sécurité & Conformité
 Objectif: Normalisation et mise en forme des logs avant
           leur envoi vers le pipeline ELK.
==============================================================
"""

import re
import json
import hashlib
from datetime import datetime
from typing import Dict, Any


class LogFormatter:
    """
    Classe responsable de la normalisation des logs :
      - format JSON uniforme
      - ajout de métadonnées standard
      - masquage et hachage des PII (emails, numéros, IBAN)
      - conversion des timestamps
    """

    EMAIL_PATTERN = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    PHONE_PATTERN = re.compile(r"\b(\+?\d{2,3}[-.\s]??\d{6,12})\b")
    IBAN_PATTERN = re.compile(r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b")

    def __init__(self, hash_salt: str = "secure_salt_2025"):
        self.hash_salt = hash_salt

    # ----------------------------------------------------------
    # Normalisation complète du log
    # ----------------------------------------------------------
    def normalize(self, log: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Nettoie, enrichit et formate un log brut avant stockage.
        """
        normalized_log = {
            "timestamp": self._normalize_timestamp(log.get("timestamp")),
            "source": source,
            "level": log.get("level", "INFO").upper(),
            "message": self._sanitize_message(log.get("message", "")),
            "context": self._mask_pii_fields(log),
        }
        return normalized_log

    # ----------------------------------------------------------
    # Nettoyage du message
    # ----------------------------------------------------------
    def _sanitize_message(self, message: str) -> str:
        """
        Supprime les caractères indésirables et limite la taille du message.
        """
        clean_msg = re.sub(r"[\r\n\t]+", " ", message).strip()
        return clean_msg[:1000]  # limite à 1000 caractères

    # ----------------------------------------------------------
    # Masquage / hachage des champs sensibles (PII)
    # ----------------------------------------------------------
    def _mask_pii_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche et masque les PII dans les champs textuels.
        """
        masked_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                value = self._mask_pii_text(value)
            elif isinstance(value, dict):
                value = self._mask_pii_fields(value)
            masked_data[key] = value
        return masked_data

    def _mask_pii_text(self, text: str) -> str:
        """
        Applique un masquage ou un hachage sur les informations sensibles.
        """
        # Masquage des adresses e-mail
        text = self.EMAIL_PATTERN.sub(lambda m: self._hash_value(m.group(1)), text)

        # Masquage des numéros de téléphone
        text = self.PHONE_PATTERN.sub(lambda m: self._hash_value(m.group(1)), text)

        # Masquage des IBAN / numéros de compte
        text = self.IBAN_PATTERN.sub(lambda m: self._hash_value(m.group(0)), text)

        return text

    def _hash_value(self, value: str) -> str:
        """
        Retourne une empreinte hachée (SHA256) d’une donnée sensible.
        """
        salted_value = (value + self.hash_salt).encode("utf-8")
        hashed = hashlib.sha256(salted_value).hexdigest()
        return f"<HASHED:{hashed[:10]}...>"

    # ----------------------------------------------------------
    # Conversion du timestamp
    # ----------------------------------------------------------
    def _normalize_timestamp(self, timestamp: Any) -> str:
        """
        Convertit ou génère un timestamp ISO 8601 standardisé.
        """
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp).isoformat()
            except ValueError:
                pass
        return datetime.utcnow().isoformat()

    # ----------------------------------------------------------
    # Formatage JSON final
    # ----------------------------------------------------------
    def to_json(self, normalized_log: Dict[str, Any]) -> str:
        """
        Convertit le log normalisé en JSON propre pour Logstash.
        """
        return json.dumps(normalized_log, ensure_ascii=False)


# ==========================================================
# Exemple d’utilisation
# ==========================================================
if __name__ == "__main__":
    formatter = LogFormatter()

    raw_log = {
        "timestamp": "2025-10-27T10:23:15",
        "level": "warning",
        "message": "Connexion suspecte depuis 192.168.0.10 pour l’utilisateur john.doe@example.com",
        "user_phone": "+212661234567",
        "iban": "FR7630006000011234567890189"
    }

    normalized = formatter.normalize(raw_log, source="api_gateway")
    print(formatter.to_json(normalized))
