"""
==============================================================
 Fichier : log_collector.py
 Auteur  : Équipe Sécurité & Conformité
 Objectif: Collecte, enrichissement et envoi des logs système,
           API et base de données vers le pipeline ELK.
==============================================================
"""

import os
import json
import time
import socket
import logging
from datetime import datetime
from typing import Dict, Any, List
from logging.handlers import RotatingFileHandler

import requests  # Pour envoyer vers Logstash
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# ==========================================================
# Configuration générale
# ==========================================================
LOG_FILE = os.getenv("LOG_FILE", "logs/system_events.log")
LOGSTASH_URL = os.getenv("LOGSTASH_URL", "http://localhost:5044")
SERVICE_NAME = os.getenv("SERVICE_NAME", "compliance_audit_system")

# ==========================================================
# Initialisation du logger local
# ==========================================================
logger = logging.getLogger("LogCollector")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class LogCollector:
    """
    Classe principale de collecte des logs multi-sources :
      - API (via endpoints internes)
      - Base de données (requêtes d’audit)
      - Système (fichiers / journaux)
    """

    def __init__(self):
        self.hostname = socket.gethostname()
        self.service = SERVICE_NAME
        self.logstash_url = LOGSTASH_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ----------------------------------------------------------
    # Collecte des logs depuis API
    # ----------------------------------------------------------
    def collect_api_logs(self, api_logs: List[Dict[str, Any]]):
        for log in api_logs:
            enriched_log = self._enrich_log(log, source="api")
            self._send_to_logstash(enriched_log)

    # ----------------------------------------------------------
    # Collecte des logs depuis la base de données
    # ----------------------------------------------------------
    def collect_db_logs(self, db_records: List[Dict[str, Any]]):
        for record in db_records:
            enriched_log = self._enrich_log(record, source="database")
            self._send_to_logstash(enriched_log)

    # ----------------------------------------------------------
    # Collecte des logs systèmes (fichiers, événements OS)
    # ----------------------------------------------------------
    def collect_system_logs(self, system_events: List[str]):
        for event in system_events:
            enriched_log = self._enrich_log({"event": event}, source="system")
            self._send_to_logstash(enriched_log)

    # ----------------------------------------------------------
    # Enrichissement du log avant envoi
    # ----------------------------------------------------------
    def _enrich_log(self, log: Dict[str, Any], source: str) -> Dict[str, Any]:
        enriched = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "host": self.hostname,
            "service": self.service,
            "severity": log.get("level", "INFO"),
            "message": log.get("message", ""),
            "context": log,
        }
        logger.debug(f"Log enrichi : {json.dumps(enriched, indent=2)}")
        return enriched

    # ----------------------------------------------------------
    # Envoi du log au pipeline ELK
    # ----------------------------------------------------------
    def _send_to_logstash(self, enriched_log: Dict[str, Any]):
        try:
            response = self.session.post(self.logstash_url, json=enriched_log, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Échec d’envoi du log à Logstash : {response.text}")
        except Exception as e:
            logger.error(f"Erreur de communication avec Logstash : {e}")

    # ----------------------------------------------------------
    # Exemple d’exécution complète
    # ----------------------------------------------------------
    def run(self):
        logger.info("Démarrage de la collecte des logs...")

        # Exemple de logs simulés
        api_logs = [
            {"endpoint": "/api/v1/login", "user": "john.doe", "status": 200},
            {"endpoint": "/api/v1/payment", "user": "jane.smith", "status": 500},
        ]

        db_logs = [
            {"query": "SELECT * FROM users", "duration_ms": 12},
            {"query": "UPDATE transactions SET status='OK'", "duration_ms": 55},
        ]

        system_events = [
            "Service démarré",
            "Connexion à Elasticsearch réussie",
        ]

        # Collecte des logs
        self.collect_api_logs(api_logs)
        self.collect_db_logs(db_logs)
        self.collect_system_logs(system_events)

        logger.info("Fin de la collecte des logs.")


# ==========================================================
# Point d’entrée
# ==========================================================
if __name__ == "__main__":
    collector = LogCollector()
    while True:
        collector.run()
        time.sleep(60)  # Collecte toutes les 60 secondes
