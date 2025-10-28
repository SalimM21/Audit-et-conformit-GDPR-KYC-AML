"""
------------------------
Tests unitaires pour tls_config.py
Vérifie la configuration TLS et la connexion sécurisée.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.security import tls_config
import ssl

class TestTLSConfig(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.tls = tls_config.TLSConfig(certfile="tests/certs/cert.pem",
                                        keyfile="tests/certs/key.pem",
                                        cafile="tests/certs/ca.pem")

    @patch("ssl.create_default_context")
    def test_create_tls_context_success(self, mock_ssl_context):
        """Vérifie que le contexte TLS est créé correctement"""
        mock_context = MagicMock()
        mock_ssl_context.return_value = mock_context

        context = self.tls.create_tls_context()
        self.assertEqual(context, mock_context)
        mock_ssl_context.assert_called_once_with(ssl.Purpose.CLIENT_AUTH)
        mock_context.load_cert_chain.assert_called_once_with(certfile="tests/certs/cert.pem",
                                                             keyfile="tests/certs/key.pem")
        mock_context.load_verify_locations.assert_called_once_with(cafile="tests/certs/ca.pem")
        mock_context.verify_mode = ssl.CERT_REQUIRED

    @patch("ssl.create_default_context")
    def test_tls_context_failure_missing_cert(self, mock_ssl_context):
        """Vérifie le comportement si le certificat est manquant"""
        mock_context = MagicMock()
        mock_ssl_context.return_value = mock_context
        mock_context.load_cert_chain.side_effect = FileNotFoundError("Certificat manquant")

        with self.assertRaises(FileNotFoundError):
            self.tls.create_tls_context()

    def test_tls_protocol_version(self):
        """Vérifie que le protocole TLS utilisé est correct"""
        context = self.tls.create_tls_context()
        self.assertIn(context.protocol, [ssl.PROTOCOL_TLS_CLIENT, ssl.PROTOCOL_TLS])

if __name__ == "__main__":
    unittest.main()
