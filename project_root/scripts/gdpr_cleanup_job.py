"""
-----------------------------
Script pour exécuter périodiquement la suppression et l'anonymisation
des données sensibles conformément au GDPR.
"""

import os
from datetime import datetime, timedelta
from src.compliance import gdpr_verification, anonymization_utils
from src.utils import csv_exporter

# Paramètres
DATA_DIR = "data"
ARCHIVE_DIR = "archive"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Définir la période après laquelle les données doivent être anonymisées/supprimées
RETENTION_DAYS = 365  # 1 an
cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)

def process_gdpr_cleanup():
    """Exécute le nettoyage GDPR pour tous les fichiers de données"""
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            filepath = os.path.join(DATA_DIR, filename)
            print(f"[INFO] Traitement GDPR du fichier : {filepath}")

            # Charger les données
            with open(filepath, "r") as f:
                lines = f.readlines()

            # Séparer les en-têtes et les données
            headers = lines[0].strip().split(",")
            records = [dict(zip(headers, line.strip().split(","))) for line in lines[1:]]

            updated_records = []
            for record in records:
                record_date = datetime.strptime(record.get("created_at", "1970-01-01"), "%Y-%m-%d")
                if record_date < cutoff_date:
                    # Anonymiser les champs sensibles
                    record = anonymization_utils.anonymize_record(record)
                updated_records.append(record)

            # Exporter les données anonymisées
            output_file = os.path.join(ARCHIVE_DIR, f"{filename.replace('.csv','')}_gdpr_{datetime.now().strftime('%Y%m%d')}.csv")
            csv_exporter.export_csv(updated_records, output_file)
            print(f"[INFO] Fichier GDPR nettoyé exporté : {output_file}")

if __name__ == "__main__":
    print("[INFO] Démarrage du job GDPR Cleanup...")
    process_gdpr_cleanup()
    print("[INFO] GDPR Cleanup terminé avec succès !")
