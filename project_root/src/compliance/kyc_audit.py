"""
kyc_audit.py
-------------
Ce module vérifie la validité et la complétude des documents KYC des clients
afin de garantir la conformité réglementaire (KYC / AML).

Fonctionnalités :
- Validation des documents (ID, justificatifs d’adresse, preuve d’activité)
- Vérification de l’exhaustivité des champs obligatoires
- Détection des anomalies ou documents expirés
- Intégration avec Elasticsearch pour traçabilité
- Alertes en cas de non-conformité
"""

import os
import yaml
import logging
from datetime import datetime
from elk_connector import ELKConnector
from alerting_system import AlertingSystem

logger = logging.getLogger("KYCAudit")


class KYCAudit:
    def __init__(self, rules_path: str, elk_config_path: str, smtp_config: dict, slack_webhook: str = None):
        self.elk = ELKConnector(elk_config_path)
        self.alert_system = AlertingSystem(elk_config_path, rules_path, smtp_config, slack_webhook)
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path: str):
        """Charge les règles KYC depuis le fichier YAML."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f).get("kyc_rules", [])

    def audit_client(self, client_data: dict):
        """
        Vérifie un dossier client pour conformité KYC.
        :param client_data: dict contenant les champs du client
        """
        issues = []
        for rule in self.rules:
            if not self._check_rule(client_data, rule):
                issues.append(rule["description"])

        if issues:
            logger.warning(f"⚠️ Client non conforme : {client_data.get('client_id')} - Problèmes : {issues}")
            self._log_non_compliance(client_data, issues)
            message = f"Client {client_data.get('client_id')} non conforme KYC : {issues}"
            self.alert_system.send_alert("warning", message)
        else:
            logger.info(f"✅ Client conforme : {client_data.get('client_id')}")

    def _check_rule(self, client_data: dict, rule: dict) -> bool:
        """Vérifie si le client respecte une règle KYC spécifique."""
        field = rule.get("field")
        condition = rule.get("condition")
        value = client_data.get(field)

        if condition == "required":
            return value not in (None, "", [])
        elif condition == "not_expired":
            try:
                exp_date = datetime.strptime(value, "%Y-%m-%d")
                return exp_date >= datetime.today()
            except Exception:
                return False
        elif condition == "in_list":
            return value in rule.get("allowed_values", [])
        return True

    def _log_non_compliance(self, client_data: dict, issues: list):
        """Enregistre les anomalies KYC dans Elasticsearch."""
        event = {
            "@timestamp": datetime.utcnow().isoformat(),
            "category": "KYC",
            "client_id": client_data.get("client_id"),
            "issues": issues,
            "status": "non_conforme"
        }
        try:
            self.elk.send_log(event)
        except Exception as e:
            logger.error(f"Erreur d’envoi du log KYC vers ELK : {e}")


if __name__ == "__main__":
    smtp_config = {
        "server": "smtp.gmail.com",
        "port": 587,
        "sender": "kyc@system.com",
        "password": "APP_PASSWORD",
        "recipients": ["compliance@company.com"]
    }

    audit = KYCAudit(
        rules_path="config/compliance_rules.yaml",
        elk_config_path="config/elk_config.yaml",
        smtp_config=smtp_config,
        slack_webhook="https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    )

    # Exemple de dossier client
    client_example = {
        "client_id": "C12345",
        "first_name": "Ahmed",
        "last_name": "El Majid",
        "dob": "1985-06-10",
        "id_document_expiry": "2024-12-31",
        "address_proof": "scan_address.pdf",
        "country": "MA"
    }

    audit.audit_client(client_example)
