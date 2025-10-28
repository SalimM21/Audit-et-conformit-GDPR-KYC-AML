"""
----------------
Module d'exportation de rapports en PDF.

Fonctionnalités :
- Génération de rapports PDF à partir de données structurées (dict, CSV, JSON)
- Ajout automatique d’en-tête, pied de page et métadonnées
- Support des tableaux et styles de texte
- Journalisation des opérations d’export
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

# --- Configuration du logger --- #
logger = logging.getLogger("pdf_exporter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PDFExporter:
    """
    Classe pour générer et exporter des rapports PDF.
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name="TitleStyle", fontSize=16, leading=20, alignment=1, spaceAfter=20))
        logger.info(f"Dossier de sortie configuré : {self.output_dir}")

    def _build_table(self, data: List[Dict[str, Any]]) -> Table:
        """
        Construit un tableau PDF à partir d’une liste de dictionnaires.
        """
        if not data:
            return Table([["Aucune donnée disponible"]])

        headers = list(data[0].keys())
        rows = [headers] + [[str(item.get(h, "")) for h in headers] for item in data]

        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3954")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f9f9f9")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey)
        ]))
        return table

    def export_pdf(self,
                   title: str,
                   data: List[Dict[str, Any]],
                   filename: Optional[str] = None,
                   metadata: Optional[Dict[str, str]] = None):
        """
        Génère un rapport PDF complet avec titre, tableau et métadonnées.
        """
        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        pdf_path = os.path.join(self.output_dir, filename)
        logger.info(f"Génération du PDF : {pdf_path}")

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=title
        )

        elements = []
        elements.append(Paragraph(title, self.styles["TitleStyle"]))
        elements.append(Spacer(1, 12))

        if metadata:
            for key, value in metadata.items():
                elements.append(Paragraph(f"<b>{key} :</b> {value}", self.styles["Normal"]))
            elements.append(Spacer(1, 12))

        elements.append(self._build_table(data))
        elements.append(PageBreak())

        doc.build(elements)
        logger.info(f"Rapport PDF exporté : {pdf_path}")
        return pdf_path


# --- Exemple d’utilisation --- #
if __name__ == "__main__":
    sample_data = [
        {"Utilisateur": "John Doe", "Action": "Connexion", "Date": "2025-10-28", "Résultat": "Succès"},
        {"Utilisateur": "Jane Smith", "Action": "Téléchargement", "Date": "2025-10-28", "Résultat": "Échec"},
    ]

    exporter = PDFExporter()
    exporter.export_pdf(
        title="Rapport d'Audit Conformité",
        data=sample_data,
        metadata={
            "Auteur": "Service Conformité",
            "Date": str(datetime.now().date()),
            "Confidentialité": "Interne"
        }
    )
