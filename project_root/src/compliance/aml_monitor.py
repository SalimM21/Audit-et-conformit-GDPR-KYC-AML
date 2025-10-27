"""
aml_monitor.py
---------------
Ce module effectue la surveillance des transactions afin de détecter des activités
potentiellement liées au blanchiment d’argent (AML - Anti Money Laundering).

Fonctionnalités :
- Collecte et analyse de transactions depuis la base de données ou le pipeline Kafka
- Application de règles de détection basées sur les seuils AML définis dans `compliance_rules.yaml`
- Génération d’alertes et enregistrement dans les logs de conformité
- Intégration avec ELK pour corrélation et visualisation
"""

import yaml
import pandas as pd
import logging
from datetime import datetime
from elk_connector import ELKConnector
from alerting_system import AlertingSystem


class AMLMonitor:
    def __init__(self, rules_path: str, elk_config_path: str, smtp_config: dict, slack_webhook: str = None):
        self.rules = self._load_rules(rules_path)
        self.elk = ELKConnector(elk_config_path)
        self.alert_system = AlertingSystem(elk_config_path, rules_path, smtp_config, slack_webhook)
        self.logger = logging.getLogger("AMLMonitor")

    def _load_rules(self, path: str):
        """Charge les règles AML depuis le fichier YAML."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f).get("aml_rules", [])

    def analyze_transactions(self, transactions: pd.DataFrame):
        """
        Analyse un lot de transactions pour détecter des comportements suspects.

        transactions : DataFrame contenant au minimum :
            - transaction_id
            - sender_id
            - receiver_id
            - amount
            - timestamp
            - country
        """
        suspicious = []

        for _, tx in transactions.iterrows():
            for rule in self.rules:
                if self._check_rule(tx, rule):
                    suspicious.append(tx.to_dict())
                    self.logger.warning(f"🚨 Transaction suspecte détectée : {tx.to_dict()} (règle: {rule['name']})")
                    self._log_suspicious_activity(tx, rule)

        if suspicious:
            message = f"{len(suspicious)} transactions suspectes détectées ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})."
            self.alert_system.send_alert("critical", message)
        else:
            self.logger.info("✅ Aucune activité suspecte détectée.")

    def _check_rule(self, tx, rule):
        """Vérifie si une transaction enfreint une règle AML donnée."""
        # Exemple : Montant supérieur au seuil ou transfert vers pays à risque
        if tx["amount"] > rule.get("max_amount", float("inf")):
            return True
        if tx["country"] in rule.get("blacklisted_countries", []):
            return True
        if rule.get("sender_repeated", False):
            # Exemple : détecter plusieurs transactions du même sender dans un court laps de temps
            # Ici simplifié — à implémenter selon la source de données
            return False
        return False

    def _log_suspicious_activity(self, tx, rule):
        """Enregistre les transactions suspectes dans Elasticsearch et le log local."""
        event = {
            "@timestamp": datetime.utcnow().isoformat(),
            "category": "AML",
            "transaction_id": tx["transaction_id"],
            "sender": tx["sender_id"],
            "receiver": tx["receiver_id"],
            "amount": tx["amount"],
            "country": tx["country"],
            "rule_triggered": rule["name"]
        }
        try:
            self.elk.send_log(event)
        except Exception as e:
            self.logger.error(f"Erreur d’envoi du log AML vers ELK : {e}")


if __name__ == "__main__":
    # Exemple d’exécution de surveillance AML
    smtp_config = {
        "server": "smtp.gmail.com",
        "port": 587,
        "sender": "aml@system.com",
        "password": "APP_PASSWORD",
        "recipients": ["compliance@company.com"]
    }

    monitor = AMLMonitor(
        rules_path="config/compliance_rules.yaml",
        elk_config_path="config/elk_config.yaml",
        smtp_config=smtp_config,
        slack_webhook="https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    )

    # Exemple de jeu de données (mock)
    data = pd.DataFrame([
        {"transaction_id": "TX001", "sender_id": "U001", "receiver_id": "U100", "amount": 95000, "timestamp": "2025-10-27T10:00:00", "country": "NG"},
        {"transaction_id": "TX002", "sender_id": "U002", "receiver_id": "U200", "amount": 1200, "timestamp": "2025-10-27T10:10:00", "country": "FR"},
    ])

    monitor.analyze_transactions(data)
