"""
-----------------------------
Script pour générer automatiquement les rapports de conformité
AML, KYC et GDPR en PDF et CSV.
"""

import os
from datetime import datetime
from src.audit import audit_report_generator
from src.utils import pdf_exporter, csv_exporter

# Dossier de sortie des rapports
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# Récupérer la date du rapport
report_date = datetime.now().strftime("%Y%m%d_%H%M%S")

# Génération du rapport AML
aml_data = audit_report_generator.get_aml_data()
aml_pdf_file = os.path.join(REPORTS_DIR, f"aml_report_{report_date}.pdf")
aml_csv_file = os.path.join(REPORTS_DIR, f"aml_report_{report_date}.csv")
pdf_exporter.export_pdf(aml_data, aml_pdf_file, title="AML Report")
csv_exporter.export_csv(aml_data, aml_csv_file)
print(f"[INFO] Rapports AML générés : {aml_pdf_file}, {aml_csv_file}")

# Génération du rapport KYC
kyc_data = audit_report_generator.get_kyc_data()
kyc_pdf_file = os.path.join(REPORTS_DIR, f"kyc_report_{report_date}.pdf")
kyc_csv_file = os.path.join(REPORTS_DIR, f"kyc_report_{report_date}.csv")
pdf_exporter.export_pdf(kyc_data, kyc_pdf_file, title="KYC Report")
csv_exporter.export_csv(kyc_data, kyc_csv_file)
print(f"[INFO] Rapports KYC générés : {kyc_pdf_file}, {kyc_csv_file}")

# Génération du rapport GDPR
gdpr_data = audit_report_generator.get_gdpr_data()
gdpr_pdf_file = os.path.join(REPORTS_DIR, f"gdpr_report_{report_date}.pdf")
gdpr_csv_file = os.path.join(REPORTS_DIR, f"gdpr_report_{report_date}.csv")
pdf_exporter.export_pdf(gdpr_data, gdpr_pdf_file, title="GDPR Report")
csv_exporter.export_csv(gdpr_data, gdpr_csv_file)
print(f"[INFO] Rapports GDPR générés : {gdpr_pdf_file}, {gdpr_csv_file}")

print("[INFO] Tous les rapports de conformité ont été générés avec succès.")
