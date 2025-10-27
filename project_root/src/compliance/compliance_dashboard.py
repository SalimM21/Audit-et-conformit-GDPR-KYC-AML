"""
compliance_dashboard.py
-----------------------
Ce module permet de créer un tableau de bord centralisé pour la conformité
en agrégeant les données AML, KYC et GDPR depuis Elasticsearch.

Fonctionnalités :
- Connexion à Elasticsearch pour récupérer les logs de conformité
- Agrégation et analyse par type (AML, KYC, GDPR)
- Export des métriques et graphiques pour visualisation
- Préparation de dashboards JSON pour Kibana ou autres outils
"""

import json
import logging
from datetime import datetime
from elk_connector import ELKConnector

logger = logging.getLogger("ComplianceDashboard")


class ComplianceDashboard:
    def __init__(self, elk_config_path: str):
        self.elk = ELKConnector(elk_config_path)

    def fetch_logs(self, category: str, start_date: str = None, end_date: str = None):
        """Récupère les logs d’une catégorie pour une période donnée."""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"category": category}}
                    ]
                }
            }
        }

        if start_date and end_date:
            query["query"]["bool"]["must"].append(
                {"range": {"@timestamp": {"gte": start_date, "lte": end_date}}}
            )

        logs = self.elk.search_logs(query)
        logger.info(f"{len(logs)} logs récupérés pour la catégorie {category}")
        return logs

    def aggregate_logs(self, logs: list):
        """Agrège les logs pour générer des métriques simples."""
        total = len(logs)
        by_client = {}
        for log in logs:
            client_id = log.get("client_id") or log.get("user_id") or "unknown"
            by_client[client_id] = by_client.get(client_id, 0) + 1
        return {
            "total_events": total,
            "events_by_client": by_client
        }

    def generate_kibana_dashboard(self, output_path: str, metrics: dict, category: str):
        """Génère un JSON de dashboard pour Kibana."""
        dashboard = {
            "title": f"Dashboard {category} - {datetime.now().strftime('%Y-%m-%d')}",
            "description": f"Tableau de bord de conformité {category}",
            "metrics": metrics
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=4)
        logger.info(f"✅ Dashboard {category} généré : {output_path}")


if __name__ == "__main__":
    dashboard = ComplianceDashboard("config/elk_config.yaml")

    # Exemple pour AML
    aml_logs = dashboard.fetch_logs("AML", start_date="2025-10-01", end_date="2025-10-27")
    aml_metrics = dashboard.aggregate_logs(aml_logs)
    dashboard.generate_kibana_dashboard("dashboards/kibana/aml_kyc_dashboard.json", aml_metrics, "AML")

    # Exemple pour KYC
    kyc_logs = dashboard.fetch_logs("KYC", start_date="2025-10-01", end_date="2025-10-27")
    kyc_metrics = dashboard.aggregate_logs(kyc_logs)
    dashboard.generate_kibana_dashboard("dashboards/kibana/kyc_dashboard.json", kyc_metrics, "KYC")

    # Exemple pour GDPR
    gdpr_logs = dashboard.fetch_logs("GDPR", start_date="2025-10-01", end_date="2025-10-27")
    gdpr_metrics = dashboard.aggregate_logs(gdpr_logs)
    dashboard.generate_kibana_dashboard("dashboards/kibana/gdpr_dashboard.json", gdpr_metrics, "GDPR")
