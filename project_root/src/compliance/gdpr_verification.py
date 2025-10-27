"""
gdpr_verification.py
--------------------
Ce module assure la conformité GDPR (droit à l’oubli, anonymisation) en traitant
les demandes des utilisateurs et en appliquant les règles de protection des données.

Fonctionnalités :
- Anonymisation des données sensibles (emails, noms, identifiants)
- Suppression ou anonymisation des données sur demande (droit à l’oubli)
- Traçabilité via Elasticsearch et logs
- Alertes en cas d’échec ou de tentative de non-conformité
"""

import hashlib
import logging
from datetime import datetime
from elk_connector import ELKConnector
from alerting_system import AlertingSystem

logger = logging.getLogger("GDPRVerification")


class GDPRVerification:
    def __init__(self, elk_config_path: str, smtp_config: dict, slack_webhook: str = None):
        self.elk = ELKConnector(elk_config_path)
        self.alert_system = AlertingSystem(elk_config_path, rules_path=None, smtp_config=smtp_config, slack_webhook=slack_webhook)

    @staticmethod
    def anonymize_value(value: str) -> str:
        """Anonymise un champ sensible via hash SHA-256."""
        if not value:
            return ""
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def anonymize_record(self, record: dict, fields_to_anonymize: list) -> dict:
        """Anonymise les champs sensibles d’un enregistrement."""
        for field in fields_to_anonymize:
            if field in record:
                original = record[field]
                record[field] = self.anonymize_value(record[field])
                logger.info(f"Champ anonymisé : {field} ({original} -> {record[field][:8]}...)")
        return record

    def delete_or_anonymize(self, record: dict, fields_to_anonymize: list, delete: bool = False):
        """
        Applique le droit à l’oubli :
        - delete=True : suppression totale
        - delete=False : anonymisation des champs sensibles
        """
        if delete:
            record.clear()
            logger.info("✅ Enregistrement supprimé conformément au droit à l’oubli.")
        else:
            record = self.anonymize_record(record, fields_to_anonymize)

        self._log_gdpr_action(record, delete)
        return record

    def _log_gdpr_action(self, record: dict, deleted: bool):
        """Envoie un log GDPR vers Elasticsearch."""
        event = {
            "@timestamp": datetime.utcnow().isoformat(),
            "category": "GDPR",
            "action": "deleted" if deleted else "anonymized",
            "record_snapshot": record
        }
        try:
            self.elk.send_log(event)
        except Exception as e:
            logger.error(f"Erreur d’envoi du log GDPR vers ELK : {e}")
            self.alert_system.send_alert("critical", f"Échec log GDPR : {e}")


if __name__ == "__main__":
    smtp_config = {
        "server": "smtp.gmail.com",
        "port": 587,
        "sender": "gdpr@system.com",
        "password": "APP_PASSWORD",
        "recipients": ["compliance@company.com"]
    }

    gdpr = GDPRVerification(
        elk_config_path="config/elk_config.yaml",
        smtp_config=smtp_config,
        slack_webhook="https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    )

    # Exemple de record utilisateur
    user_record = {
        "user_id": "U12345",
        "email": "ahmed.elmajid@example.com",
        "full_name": "Ahmed El Majid",
        "phone": "+212600000000"
    }

    # Anonymisation
    gdpr.delete_or_anonymize(user_record, fields_to_anonymize=["email", "full_name"], delete=False)
