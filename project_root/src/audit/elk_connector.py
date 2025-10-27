"""
==============================================================
 Fichier : elk_connector.py
 Auteur  : Équipe Sécurité & Conformité
 Objectif: Fournir une interface fiable pour envoyer les logs
           vers la stack ELK (Elasticsearch / Logstash / Kibana)
==============================================================
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, List
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

# ==========================================================
# Configuration globale
# ==========================================================
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
LOGSTASH_URL = os.getenv("LOGSTASH_URL", "http://localhost:5044")
INDEX_NAME = os.getenv("ELK_INDEX", "compliance-logs-2025")
USE_TLS = os.getenv("USE_TLS", "false").lower() == "true"
API_KEY = os.getenv("ELK_API_KEY", "")
TIMEOUT = int(os.getenv("ELK_TIMEOUT", "10"))

logger = logging.getLogger("ElkConnector")
logger.setLevel(logging.INFO)


class ElkConnector:
    """
    Classe de connexion et d’envoi des logs vers la stack ELK.
    Supporte :
      - Transmission directe à Logstash (HTTP)
      - Indexation directe dans Elasticsearch
      - Reconnexion automatique en cas d’échec réseau
    """

    def __init__(self):
        self.elastic_url = ELASTIC_URL.rstrip("/")
        self.logstash_url = LOGSTASH_URL.rstrip("/")
        self.index_name = INDEX_NAME
        self.session = self._init_session()

    # ----------------------------------------------------------
    # Configuration de la session HTTP avec retry
    # ----------------------------------------------------------
    def _init_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        if API_KEY:
            session.headers.update({"Authorization": f"ApiKey {API_KEY}"})
        session.headers.update({"Content-Type": "application/json"})

        logger.info("Session HTTP initialisée avec retry et sécurité.")
        return session

    # ----------------------------------------------------------
    # Envoi d’un log unique vers Logstash
    # ----------------------------------------------------------
    def send_to_logstash(self, log: Dict[str, Any]) -> bool:
        try:
            response = self.session.post(self.logstash_url, json=log, timeout=TIMEOUT)
            if response.status_code in [200, 201]:
                logger.debug("Log envoyé à Logstash avec succès.")
                return True
            else:
                logger.warning(f"Échec Logstash : {response.status_code} - {response.text}")
        except requests.RequestException as e:
            logger.error(f"Erreur réseau vers Logstash : {e}")
        return False

    # ----------------------------------------------------------
    # Indexation directe dans Elasticsearch
    # ----------------------------------------------------------
    def index_to_elasticsearch(self, log: Dict[str, Any]) -> bool:
        """
        Envoie un log directement dans Elasticsearch (optionnel).
        """
        url = f"{self.elastic_url}/{self.index_name}/_doc"
        try:
            response = self.session.post(url, json=log, timeout=TIMEOUT)
            if response.status_code in [200, 201]:
                logger.debug("Log indexé dans Elasticsearch.")
                return True
            else:
                logger.warning(f"Erreur d’indexation Elasticsearch : {response.text}")
        except requests.RequestException as e:
            logger.error(f"Erreur réseau Elasticsearch : {e}")
        return False

    # ----------------------------------------------------------
    # Envoi par lot (batch)
    # ----------------------------------------------------------
    def bulk_send(self, logs: List[Dict[str, Any]], method: str = "logstash"):
        """
        Envoi en batch vers Logstash ou Elasticsearch.
        """
        success_count = 0
        for log in logs:
            sent = (
                self.send_to_logstash(log)
                if method == "logstash"
                else self.index_to_elasticsearch(log)
            )
            if sent:
                success_count += 1
            else:
                logger.warning(f"Log non transmis : {json.dumps(log)[:200]}")
            time.sleep(0.05)  # léger délai anti-surcharge

        logger.info(f"Envoi terminé : {success_count}/{len(logs)} logs envoyés avec succès.")

    # ----------------------------------------------------------
    # Vérification de la connexion ELK
    # ----------------------------------------------------------
    def test_connection(self) -> bool:
        """
        Vérifie que les services Elasticsearch / Logstash sont accessibles.
        """
        try:
            elastic_ok = requests.get(self.elastic_url, timeout=3).status_code == 200
            logstash_ok = requests.get(self.logstash_url, timeout=3).status_code == 200
            if elastic_ok or logstash_ok:
                logger.info("Connexion ELK vérifiée avec succès ✅")
                return True
        except requests.RequestException:
            pass

        logger.error("Échec de connexion à la stack ELK ❌")
        return False


# ==========================================================
# Exemple d’utilisation
# ==========================================================
if __name__ == "__main__":
    elk = ElkConnector()

    # Test de connexion
    elk.test_connection()

    # Exemple de log
    log_example = {
        "timestamp": "2025-10-27T13:25:00Z",
        "level": "INFO",
        "source": "compliance_audit",
        "message": "Nouvelle transaction vérifiée via module KYC",
        "context": {"user_id": 1234, "country": "MA"},
    }

    elk.send_to_logstash(log_example)
    elk.index_to_elasticsearch(log_example)
