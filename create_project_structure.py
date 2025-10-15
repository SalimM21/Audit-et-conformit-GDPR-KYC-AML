import os

# Définition de la structure du projet
project_structure = {
    "config": [
        "logging.yaml",
        "elk_config.yaml",
        "gdpr_config.yaml",
        "compliance_rules.yaml"
    ],

    "src": {
        "audit": [
            "__init__.py",
            "log_collector.py",
            "log_formatter.py",
            "elk_connector.py",
            "audit_report_generator.py",
            "alerting_system.py"
        ],
        "compliance": [
            "__init__.py",
            "aml_monitor.py",
            "kyc_audit.py",
            "gdpr_verification.py",
            "anonymization_utils.py",
            "compliance_dashboard.py"
        ],
        "security": [
            "encryption_utils.py",
            "key_management.py",
            "tls_config.py"
        ],
        "utils": [
            "file_handler.py",
            "email_notifier.py",
            "pdf_exporter.py",
            "csv_exporter.py"
        ]
    },

    "dashboards": {
        "kibana": [
            "audit_dashboard.json",
            "aml_kyc_dashboard.json",
            "gdpr_dashboard.json"
        ],
        "screenshots": []
    },

    "tests": {
        "test_audit": [
            "test_log_collector.py",
            "test_audit_report_generator.py",
            "test_alerting_system.py"
        ],
        "test_compliance": [
            "test_aml_monitor.py",
            "test_kyc_audit.py",
            "test_gdpr_verification.py",
            "test_anonymization_utils.py"
        ],
        "test_security": [
            "test_encryption_utils.py",
            "test_tls_config.py"
        ]
    },

    "logs": {
        "access_logs": [
            "access_2025-10-14.log"
        ],
        "compliance_logs": [
            "aml_alerts.log",
            "gdpr_events.log",
            "kyc_exceptions.log"
        ],
        "system_events.log": None
    },

    "reports": [
        "aml_report_2025Q4.pdf",
        "kyc_report_2025Q4.pdf",
        "gdpr_audit_2025Q4.csv",
        "compliance_summary.json"
    ],

    "scripts": [
        "run_elasticsearch.sh",
        "deploy_kibana_dashboard.sh",
        "generate_audit_reports.py",
        "gdpr_cleanup_job.py"
    ],

    "README.md": None
}


def create_structure(base_path, structure):
    """Crée récursivement les dossiers et fichiers du projet"""
    for name, content in structure.items() if isinstance(structure, dict) else []:
        path = os.path.join(base_path, name)

        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            print(f"[Dossier] {path}")
            create_structure(path, content)

        elif isinstance(content, list):
            os.makedirs(path, exist_ok=True)
            print(f"[Dossier] {path}")
            for file in content:
                file_path = os.path.join(path, file)
                if "." in file:
                    open(file_path, "a").close()
                    print(f"  [Fichier] {file_path}")
        elif content is None:
            open(path, "a").close()
            print(f"[Fichier] {path}")


if __name__ == "__main__":
    root_dir = "project_root"
    os.makedirs(root_dir, exist_ok=True)
    print(f"Création de la structure du projet dans : {os.path.abspath(root_dir)}\n")
    create_structure(root_dir, project_structure)
    print("\n✅ Arborescence créée avec succès !")
