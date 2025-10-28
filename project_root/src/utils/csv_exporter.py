"""
----------------
Module d'exportation de rapports en CSV.

Fonctionnalités :
- Génération de fichiers CSV à partir de listes de dictionnaires
- Ajout de métadonnées d’en-tête (ex : auteur, date, service)
- Gestion automatique du dossier de sortie
- Validation des données et logs d’audit
"""

import os
import csv
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

# --- Configuration du logger --- #
logger = logging.getLogger("csv_exporter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CSVExporter:
    """
    Classe pour exporter des rapports ou données en CSV.
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Dossier de sortie CSV configuré : {self.output_dir}")

    def _validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Vérifie que les données sont bien structurées (liste de dictionnaires homogènes).
        """
        if not data:
            logger.warning("Aucune donnée fournie à exporter.")
            return False

        keys = list(data[0].keys())
        for row in data:
            if not isinstance(row, dict) or list(row.keys()) != keys:
                logger.error("Structure de données incohérente.")
                return False
        return True

    def export_csv(self,
                   title: str,
                   data: List[Dict[str, Any]],
                   filename: Optional[str] = None,
                   metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Exporte un rapport en CSV.
        """
        if not self._validate_data(data):
            raise ValueError("Les données fournies ne sont pas valides ou vides.")

        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        csv_path = os.path.join(self.output_dir, filename)
        logger.info(f"Génération du fichier CSV : {csv_path}")

        # --- Écriture du fichier CSV --- #
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Métadonnées en haut du fichier
            if metadata:
                writer.writerow(["# === Métadonnées ==="])
                for key, value in metadata.items():
                    writer.writerow([f"# {key}: {value}"])
                writer.writerow([])

            # Corps du rapport
            headers = list(data[0].keys())
            writer.writerow(headers)
            for row in data:
                writer.writerow([row.get(h, "") for h in headers])

        logger.info(f"Rapport CSV exporté avec succès : {csv_path}")
        return csv_path


# --- Exemple d’utilisation --- #
if __name__ == "__main__":
    sample_data = [
        {"Utilisateur": "John Doe", "Action": "Connexion", "Date": "2025-10-28", "Résultat": "Succès"},
        {"Utilisateur": "Jane Smith", "Action": "Téléchargement", "Date": "2025-10-28", "Résultat": "Échec"},
    ]

    exporter = CSVExporter()
    exporter.export_csv(
        title="Audit Conformité",
        data=sample_data,
        metadata={
            "Auteur": "Service Conformité",
            "Date": str(datetime.now().date()),
            "Confidentialité": "Interne"
        }
    )
