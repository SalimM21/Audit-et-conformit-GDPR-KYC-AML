"""
anonymization_utils.py
----------------------
Ce module fournit des fonctions réutilisables pour pseudonymiser ou anonymiser
les données personnelles, en conformité avec GDPR/KYC.

Fonctionnalités :
- Hash SHA-256 pour anonymisation
- Pseudonymisation via mapping aléatoire
- Masquage partiel des données (emails, numéros de téléphone)
"""

import hashlib
import random
import string
import logging

logger = logging.getLogger("AnonymizationUtils")


def hash_sha256(value: str) -> str:
    """Retourne le hash SHA-256 d’une chaîne de caractères."""
    if not value:
        return ""
    hashed = hashlib.sha256(value.encode("utf-8")).hexdigest()
    logger.debug(f"Hashed '{value}' -> '{hashed[:8]}...'")
    return hashed


def pseudonymize(value: str, length: int = 8) -> str:
    """Retourne une version pseudonymisée aléatoire de la valeur."""
    if not value:
        return ""
    random.seed(hash(value))  # pour cohérence si nécessaire
    pseudo = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    logger.debug(f"Pseudonymized '{value}' -> '{pseudo}'")
    return pseudo


def mask_email(email: str) -> str:
    """Masque partiellement un email pour protéger l’identité."""
    if not email or "@" not in email:
        return email
    local, domain = email.split("@")
    masked_local = local[0] + "*" * (len(local) - 2) + local[-1] if len(local) > 2 else "*" * len(local)
    masked_email = f"{masked_local}@{domain}"
    logger.debug(f"Masked email '{email}' -> '{masked_email}'")
    return masked_email


def mask_phone(phone: str) -> str:
    """Masque partiellement un numéro de téléphone."""
    if not phone or len(phone) < 4:
        return "*" * len(phone)
    masked = "*" * (len(phone) - 4) + phone[-4:]
    logger.debug(f"Masked phone '{phone}' -> '{masked}'")
    return masked


if __name__ == "__main__":
    # Exemple d'utilisation
    sample_email = "ahmed.elmajid@example.com"
    sample_phone = "+212600123456"
    
    print("SHA256:", hash_sha256(sample_email))
    print("Pseudonym:", pseudonymize(sample_email))
    print("Masked Email:", mask_email(sample_email))
    print("Masked Phone:", mask_phone(sample_phone))
