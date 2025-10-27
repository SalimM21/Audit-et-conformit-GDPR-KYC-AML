"""
alerting_system.py
------------------
Ce module gère la détection et l’envoi d’alertes lorsqu’une activité suspecte
ou non conforme est identifiée (fraude, violation GDPR, dépassement de seuil KYC/AML).

Fonctionnalités :
- Surveillance en temps réel des logs depuis Elasticsearch
- Application de règles de conformité depuis `compliance_rules.yaml`
- Génération et envoi d’alertes (email, Slack, webhook, etc.)
"""

import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from elk_connector import ELKConnector
from datetime import datetime
import requests


class AlertingSystem:
    def __init__(self, elk_config_path: str, rules_path: str, smtp_config: dict, slack_webhook: str = None):
        self.connector = ELKConnector(elk_config_path)
        self.rules = self._load_rules(rules_path)
        self.smtp_config = smtp_config
        self.slack_webhook = slack_webhook

    def _load_rules(self, path: str):
        """Charge les règles AML/KYC/GDPR depuis le fichier YAML."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def check_for_alerts(self):
        """Vérifie les logs récents et déclenche des alertes selon les règles."""
        for rule in self.rules.get("rules", []):
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"@timestamp": {"gte": "now-1h"}}},
                            {"match": {"category": rule["category"]}}
                        ]
                    }
                }
            }
            logs = self.connector.search_logs(query)

            if len(logs) >= rule.get("threshold", 1):
                message = f"⚠️ Alerte {rule['category']}: {len(logs)} événements suspects détectés.\n"
                message += f"Condition: {rule['description']}\nHeure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.send_alert(rule["severity"], message)

    def send_alert(self, severity: str, message: str):
        """Envoie une alerte via email et/ou Slack."""
        subject = f"[{severity.upper()}] Alerte Conformité Détectée"

        # --- Envoi Email ---
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["sender"]
            msg["To"] = ", ".join(self.smtp_config["recipients"])
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["sender"], self.smtp_config["password"])
                server.send_message(msg)

            print(f"📧 Alerte envoyée par email : {subject}")
        except Exception as e:
            print(f"❌ Erreur d’envoi email : {e}")

        # --- Envoi Slack ---
        if self.slack_webhook:
            try:
                payload = {"text": f":rotating_light: {subject}\n{message}"}
                response = requests.post(self.slack_webhook, json=payload)
                if response.status_code == 200:
                    print("💬 Alerte envoyée sur Slack.")
                else:
                    print(f"⚠️ Erreur Slack : {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur d’envoi Slack : {e}")


if __name__ == "__main__":
    smtp_config = {
        "server": "smtp.gmail.com",
        "port": 587,
        "sender": "compliance@system.com",
        "password": "APP_PASSWORD",
        "recipients": ["security@company.com", "aml@company.com"]
    }

    alert_system = AlertingSystem(
        elk_config_path="config/elk_config.yaml",
        rules_path="config/compliance_rules.yaml",
        smtp_config=smtp_config,
        slack_webhook="https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    )

    alert_system.check_for_alerts()
