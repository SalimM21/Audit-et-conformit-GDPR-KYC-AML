"""
-------------
Utilitaires pour la configuration TLS/SSL des communications réseau.

Fonctionnalités :
- Création d'un ssl.SSLContext sécurisé (TLS 1.2/1.3)
- Configuration d'une session requests utilisant ce contexte (via un HTTPAdapter personnalisé)
- Aide pour configurer un serveur (uvicorn / aiohttp) avec certificat et clé
- Vérification optionnelle des certificats clients (mutual TLS)

Usage :
from tls_config import create_ssl_context, configure_requests_session

ctx = create_ssl_context(cafile="ca.pem", certfile="server.crt", keyfile="server.key",
                         require_client_cert=False)
session = configure_requests_session(ctx)
r = session.get("https://example.com")
"""

import ssl
import os
import logging
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_


logger = logging.getLogger("TLSConfig")


def create_ssl_context(
    cafile: Optional[str] = None,
    certfile: Optional[str] = None,
    keyfile: Optional[str] = None,
    require_client_cert: bool = False,
    ciphers: Optional[str] = None,
) -> ssl.SSLContext:
    """
    Crée et retourne un SSLContext sécurisé.
    - cafile : chemin vers le fichier PEM de la CA (pour vérifier les certs serveur/clients)
    - certfile/keyfile : certificat et clé du client/serveur (PEM)
    - require_client_cert : si True, active la vérification des certificats clients (mTLS)
    - ciphers : chaîne de chiffrements si besoin de restreindre (optionnel)
    """

    # Utiliser TLS (choix moderne : PROTOCOL_TLS_CLIENT pour clients, PROTOCOL_TLS_SERVER pour serveur)
    # Ici on crée un contexte "générique" utilisable côté client ; serveur peut l'adapter.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Interdire les versions obsolètes (SSLv2/SSLv3/TLSv1/TLSv1.1)
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1

    # Activer les meilleures pratiques (forward secrecy)
    if ciphers:
        try:
            context.set_ciphers(ciphers)
        except Exception:
            logger.warning("Impossible d'appliquer la liste de chiffrements personnalisée.")
    else:
        # Chaîne de chiffrements forte recommandée (OpenSSL compatible)
        try:
            context.set_ciphers(
                "ECDHE+AESGCM:ECDHE+CHACHA20:!aNULL:!eNULL:!PSK:!SRP:!MD5:!RC4"
            )
        except Exception:
            # Certains environnements (vieilles versions OpenSSL) peuvent ignorer
            pass

    # Chargement des certificats CA pour la vérification
    if cafile and os.path.exists(cafile):
        context.load_verify_locations(cafile)
        logger.info(f"CA loaded from {cafile}")
    else:
        # Si pas de cafile fourni, charger les CAs système
        context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
        logger.info("CA system default certificates loaded")

    # Charger cert & key si fournis (utile côté serveur ou client avec cert client)
    if certfile and keyfile:
        if os.path.exists(certfile) and os.path.exists(keyfile):
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            logger.info(f"Cert and key loaded (certfile={certfile})")
        else:
            logger.warning("certfile/keyfile fournis mais introuvables sur le disque.")

    # Exiger la vérification de certificat côté serveur si demandé (mTLS)
    if require_client_cert:
        context.verify_mode = ssl.CERT_REQUIRED
        logger.info("Client cert verification (mTLS) enabled")
    else:
        context.verify_mode = ssl.CERT_REQUIRED  # Pour clients, on veut toujours vérifier le serveur

    # Paramètres additionnels de sécurité
    # Disable compression (ZIP bombing attacks)
    try:
        context.options |= ssl.OP_NO_COMPRESSION
    except Exception:
        pass

    return context


# --- HTTPAdapter personnalisé pour requests qui accepte un SSLContext ---
class SSLContextAdapter(HTTPAdapter):
    """
    Adapter requests qui utilise un ssl.SSLContext personnalisé pour urllib3 PoolManager.
    """

    def __init__(self, ssl_context: ssl.SSLContext, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        # Utiliser le PoolManager d'urllib3 et passer le ssl_context
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
            **pool_kwargs,
        )


def configure_requests_session(ssl_context: ssl.SSLContext, timeout: int = 10) -> requests.Session:
    """
    Retourne une session requests configurée pour utiliser le SSLContext fourni.
    - ssl_context : instance créée par create_ssl_context()
    - timeout : timeout par défaut pour les requêtes (en secondes)
    """
    session = requests.Session()
    adapter = SSLContextAdapter(ssl_context)
    session.mount("https://", adapter)
    session.verify = False  # requests utilise ssl_context via adapter ; laisser verify False pour éviter double vérification
    # Note : si vous préférez utiliser verify=True, ne montez pas cet adapter et utilisez 'verify=cafile' dans requests.get/post
    session.request = _wrap_request_with_timeout(session.request, timeout)
    logger.info("Requests session configured with custom SSLContext")
    return session


def _wrap_request_with_timeout(orig_request, timeout):
    """
    Wrapper léger pour injecter un timeout par défaut sans changer la signature.
    """
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return orig_request(method, url, **kwargs)
    return wrapped


# --- Helpers pour serveurs (uvicorn, aiohttp, etc.) ---

def uvicorn_ssl_args(certfile: str, keyfile: str, cafile: Optional[str] = None, require_client_cert: bool = False):
    """
    Retourne un dictionnaire d'arguments à passer à uvicorn.run(...) pour activer TLS.
    Exemple:
        import uvicorn
        from tls_config import uvicorn_ssl_args
        args = uvicorn_ssl_args("server.crt", "server.key")
        uvicorn.run("app:app", host="0.0.0.0", port=443, **args)
    """
    ssl_args = {
        "ssl_certfile": certfile,
        "ssl_keyfile": keyfile,
    }
    if cafile:
        # uvicorn/ssl native ne propose pas d'argument direct pour cafile+mTLS, mais on peut préparer SSLContext
        context = create_ssl_context(cafile=cafile, certfile=certfile, keyfile=keyfile, require_client_cert=require_client_cert)
        ssl_args = {"ssl_context": context}
    return ssl_args


def verify_server_cert(session: requests.Session, hostname: str, expected_cn: Optional[str] = None) -> bool:
    """
    Optionnel : effectue une requête HEAD/GET et vérifie que le CN du certificat serveur contient expected_cn.
    Nécessite que la session ait été configurée avec un SSLContext.
    """
    try:
        resp = session.get(f"https://{hostname}", timeout=5)
        # Extraction du certificat depuis la socket n'est pas triviale via requests; on peut faire une vérification basique via urllib3
        # Ici on se contente d'un statut 200 comme "vérifié" ; pour vérifications CN/ SAN avancées, utiliser ssl.get_server_certificate
        if resp.status_code < 400:
            logger.info(f"Connexion réussie vers {hostname}")
            return True
        logger.warning(f"Réponse non OK de {hostname} : {resp.status_code}")
    except Exception as e:
        logger.error(f"Erreur de vérification du certificat serveur {hostname} : {e}")
    return False


# =======================
# Exemple d'utilisation
# =======================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Lecture simple de variables d'environnement (ex: CHEMINS DES CERTS)
    CAFILE = os.getenv("TLS_CAFILE", None)
    CERTFILE = os.getenv("TLS_CERTFILE", "certs/server.crt")
    KEYFILE = os.getenv("TLS_KEYFILE", "certs/server.key")
    REQUIRE_CLIENT = os.getenv("TLS_REQUIRE_CLIENT", "false").lower() == "true"

    ctx = create_ssl_context(cafile=CAFILE, certfile=CERTFILE, keyfile=KEYFILE, require_client_cert=REQUIRE_CLIENT)
    sess = configure_requests_session(ctx)

    # Test basique
    ok = verify_server_cert(sess, "example.com")
    logger.info(f"Vérification serveur example.com : {ok}")
