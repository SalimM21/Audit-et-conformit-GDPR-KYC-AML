"""
audit_report_generator.py
-------------------------
Ce module permet de générer des rapports de conformité (GDPR / KYC / AML)
en formats PDF et CSV à partir des logs collectés dans Elasticsearch.

Fonctionnalités :
- Extraction des logs pertinents selon la période et le type d’audit
- Agrégation et analyse des événements
- Génération de rapports horodatés (PDF, CSV)
"""

import csv
import os
from datetime import datetime
from fpdf import FPDF
from elk_connector import ELKConnector


class AuditReportGenerator:
    def __init__(self, elk_config_path: str):
        """Initialise le connecteur Elasticsearch."""
        self.connector = ELKConnector(elk_config_path)

    def fetch_logs(self, start_date: str, end_date: str, category: str):
        """
        Récupère les logs d’audit pour une période donnée.
        :param start_date: date début (YYYY-MM-DD)
        :param end_date: date fin (YYYY-MM-DD)
        :param category: catégorie de conformité (GDPR, KYC, AML, Access, etc.)
        :return: liste de logs
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {"gte": start_date, "lte": end_date}}},
                        {"match": {"category": category}}
                    ]
                }
            }
        }
        return self.connector.search_logs(query)

    def export_csv(self, logs: list, output_path: str):
        """Exporte les logs sous format CSV."""
        if not logs:
            print("Aucun log à exporter.")
            return

        fieldnames = logs[0].keys()
        with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in logs:
                writer.writerow(log)
        print(f"✅ Rapport CSV généré : {output_path}")

    def export_pdf(self, logs: list, output_path: str, title="Rapport de conformité"):
        """Génère un rapport PDF synthétique."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=title, ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(200, 10, txt=f"Nombre d’entrées : {len(logs)}", ln=True)
        pdf.ln(10)

        for log in logs[:20]:  # aperçu limité
            pdf.multi_cell(0, 10, txt=str(log))
            pdf.ln(2)

        pdf.output(output_path)
        print(f"✅ Rapport PDF généré : {output_path}")

    def generate_compliance_report(self, start_date, end_date, category, output_dir="reports"):
        """Pipeline complet de génération de rapport."""
        os.makedirs(output_dir, exist_ok=True)
        logs = self.fetch_logs(start_date, end_date, category)

        csv_path = os.path.join(output_dir, f"rapport_{category}_{start_date}_{end_date}.csv")
        pdf_path = os.path.join(output_dir, f"rapport_{category}_{start_date}_{end_date}.pdf")

        self.export_csv(logs, csv_path)
        self.export_pdf(logs, pdf_path, title=f"Rapport conformité {category.upper()}")


if __name__ == "__main__":
    generator = AuditReportGenerator("config/elk_config.yaml")
    generator.generate_compliance_report(
        start_date="2025-10-01",
        end_date="2025-10-27",
        category="KYC"
    )
