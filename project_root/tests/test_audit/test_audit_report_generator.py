"""
-------------------------------
Tests unitaires pour audit_report_generator.py
Vérifie la génération de rapports PDF et CSV pour les audits.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from src.audit import audit_report_generator

class TestAuditReportGenerator(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.generator = audit_report_generator.AuditReportGenerator(output_dir="tests/reports")
        os.makedirs("tests/reports", exist_ok=True)
        self.sample_data = [
            {"Utilisateur": "John Doe", "Action": "Connexion", "Date": "2025-10-28", "Résultat": "Succès"},
            {"Utilisateur": "Jane Smith", "Action": "Téléchargement", "Date": "2025-10-28", "Résultat": "Échec"}
        ]

    def tearDown(self):
        """Nettoyage après tests"""
        for f in os.listdir("tests/reports"):
            os.remove(os.path.join("tests/reports", f))

    @patch("src.audit.audit_report_generator.PDFExporter.export_pdf")
    def test_generate_pdf_report(self, mock_export_pdf):
        """Test de génération de rapport PDF"""
        mock_export_pdf.return_value = "tests/reports/audit_report.pdf"
        pdf_path = self.generator.generate_pdf_report("Audit Conformité", self.sample_data)
        self.assertTrue(pdf_path.endswith(".pdf"))
        mock_export_pdf.assert_called_once_with("Audit Conformité", self.sample_data)

    @patch("src.audit.audit_report_generator.CSVExporter.export_csv")
    def test_generate_csv_report(self, mock_export_csv):
        """Test de génération de rapport CSV"""
        mock_export_csv.return_value = "tests/reports/audit_report.csv"
        csv_path = self.generator.generate_csv_report("Audit Conformité", self.sample_data)
        self.assertTrue(csv_path.endswith(".csv"))
        mock_export_csv.assert_called_once_with("Audit Conformité", self.sample_data, metadata=None)

    def test_generate_report_with_empty_data(self):
        """Test génération de rapport avec données vides"""
        with self.assertRaises(ValueError):
            self.generator.generate_csv_report("Rapport Vide", [])
        with self.assertRaises(ValueError):
            self.generator.generate_pdf_report("Rapport Vide", [])

if __name__ == "__main__":
    unittest.main()
