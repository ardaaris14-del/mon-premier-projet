"""Lecture d'un document et conversion en blocs de contenu pour l'API."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any

from docscan.config import TAILLE_MAX_OCTETS

IMAGES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
PDF = {".pdf": "application/pdf"}
TEXTE = {".txt", ".md", ".csv", ".json"}

EXTENSIONS_SUPPORTEES = sorted(set(IMAGES) | set(PDF) | TEXTE)


class ErreurDocument(ValueError):
    """Le document ne peut pas être envoyé à l'API."""


def _encoder(chemin: Path) -> str:
    return base64.standard_b64encode(chemin.read_bytes()).decode("utf-8")


def bloc_document(chemin: str | Path) -> dict[str, Any]:
    """Transforme un fichier local en bloc de contenu (image, PDF ou texte)."""
    chemin = Path(chemin)
    if not chemin.is_file():
        raise ErreurDocument(f"Document introuvable : {chemin}")

    taille = chemin.stat().st_size
    if taille == 0:
        raise ErreurDocument(f"Document vide : {chemin}")
    if taille > TAILLE_MAX_OCTETS:
        raise ErreurDocument(
            f"Document trop volumineux ({taille / 1_048_576:.1f} Mo). "
            f"Limite : {TAILLE_MAX_OCTETS / 1_048_576:.0f} Mo. "
            "Découpez le PDF ou réduisez la résolution de l'image."
        )

    extension = chemin.suffix.lower()

    if extension in IMAGES:
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": IMAGES[extension],
                "data": _encoder(chemin),
            },
        }

    if extension in PDF:
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": _encoder(chemin),
            },
        }

    if extension in TEXTE:
        return {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": chemin.read_text(encoding="utf-8", errors="replace"),
            },
        }

    devine, _ = mimetypes.guess_type(chemin.name)
    raise ErreurDocument(
        f"Format non pris en charge : {extension or devine or 'inconnu'}. "
        f"Formats acceptés : {', '.join(EXTENSIONS_SUPPORTEES)}."
    )


def fichiers_du_dossier(dossier: str | Path) -> list[Path]:
    """Tous les documents lisibles d'un dossier, triés par nom."""
    dossier = Path(dossier)
    if not dossier.is_dir():
        raise ErreurDocument(f"Dossier introuvable : {dossier}")
    return sorted(
        f for f in dossier.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSIONS_SUPPORTEES
    )
