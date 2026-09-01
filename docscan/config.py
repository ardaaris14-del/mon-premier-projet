"""Réglages globaux, surchargeables par variables d'environnement."""

import os

# Modèle Claude utilisé pour la lecture des documents.
MODELE_IA = os.environ.get("DOCSCAN_MODELE_IA", "claude-opus-5")

# Niveau d'effort de raisonnement : low | medium | high | xhigh | max.
EFFORT = os.environ.get("DOCSCAN_EFFORT", "medium")

# Plafond de tokens en sortie (largement suffisant pour un formulaire de champs).
MAX_TOKENS = int(os.environ.get("DOCSCAN_MAX_TOKENS", "16000"))

# Taille maximale acceptée pour un document (limite API : 32 Mo par requête).
TAILLE_MAX_OCTETS = int(os.environ.get("DOCSCAN_TAILLE_MAX", str(28 * 1024 * 1024)))
