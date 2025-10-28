"""
-----------------
Module d’envoi de mails pour alertes et rapports automatisés.

Fonctionnalités :
- Envoi de mails via SMTP (TLS ou SSL)
- Support des messages texte et HTML
- Envoi de pièces jointes (rapports, logs, etc.)
- Journalisation complète et gestion des erreurs
"""

import os
import smtplib
import logging
from email.message import EmailMessage
from typing import List, Optional

# --- Configuration du logger --- #
logger = logging.getLogger("email_notifier")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class EmailNotifier:
    """
    Classe utilitaire pour l’envoi de mails de notification.
    """

    def __init__(self,
                 smtp_server: str,
                 smtp_port: int,
                 username: str,
                 password: str,
                 use_tls: bool = True):
        """
        Initialise la connexion SMTP sécurisée.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls

        logger.info(f"Initialisation EmailNotifier pour {smtp_server}:{smtp_port} (TLS={use_tls})")

    def _connect(self):
        """
        Établit une connexion SMTP sécurisée.
        """
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"Échec de la connexion SMTP : {e}")
            raise

    def send_email(self,
                   subject: str,
                   body: str,
                   to: List[str],
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   attachments: Optional[List[str]] = None,
                   html: bool = False):
        """
        Envoie un email avec support HTML et pièces jointes.
        """
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        if html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        # Ajout des pièces jointes
        if attachments:
            for path in attachments:
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                    filename = os.path.basename(path)
                    msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=filename)
                    logger.info(f"Pièce jointe ajoutée : {filename}")
                except Exception as e:
                    logger.warning(f"Impossible d’ajouter la pièce jointe {path} : {e}")

        # Envoi du mail
        try:
            with self._connect() as server:
                recipients = to + (cc or []) + (bcc or [])
                server.send_message(msg, from_addr=self.username, to_addrs=recipients)
            logger.info(f"Mail envoyé à {', '.join(to)} (Cc: {cc or []}, Bcc: {bcc or []})")

        except Exception as e:
            logger.error(f"Erreur lors de l’envoi du mail : {e}")
            raise


# --- Exemple d’utilisation --- #
if __name__ == "__main__":
    notifier = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="exemple@gmail.com",
        password="motdepasse_app",  # utiliser un mot de passe d’application !
        use_tls=True
    )

    notifier.send_email(
        subject="[ALERTE] Anomalie détectée",
        body="Une anomalie a été détectée dans le système de conformité. Consultez le rapport joint.",
        to=["admin@example.com"],
        attachments=["rapport_conformite.pdf"]
    )
