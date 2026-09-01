"""Construction du JSON Schema envoyé à Claude (structured outputs).

Le schéma décrit exactement la forme attendue de la réponse, ce qui garantit
un JSON valide et des clés qui correspondent aux champs du modèle.
"""

from __future__ import annotations

from typing import Any

from docscan.modeles import Champ, Modele

# Un champ absent du document vaut null : on n'invente jamais une valeur.
_TYPES_JSON = {
    "texte": "string",
    "date": "string",
    "choix": "string",
    "nombre": "number",
    "entier": "integer",
    "booleen": "boolean",
}

_INDICES = {
    "date": "Format AAAA-MM-JJ.",
    "nombre": "Nombre décimal, sans symbole monétaire ni séparateur de milliers.",
    "entier": "Nombre entier.",
    "liste": "Liste de valeurs textuelles.",
}


def _schema_valeur(champ: Champ, *, nullable: bool = True) -> dict[str, Any]:
    """Schéma d'une valeur unique (hors tableau)."""
    description = " ".join(p for p in (champ.libelle, champ.description, _INDICES.get(champ.type, "")) if p)

    if champ.type == "liste":
        types: Any = ["array", "null"] if nullable else "array"
        return {"type": types, "items": {"type": "string"}, "description": description}

    json_type = _TYPES_JSON[champ.type]
    schema: dict[str, Any] = {
        "type": [json_type, "null"] if nullable else json_type,
        "description": description,
    }
    if champ.type == "choix":
        schema["enum"] = [*champ.choix, None] if nullable else list(champ.choix)
    if champ.type == "date":
        schema["description"] = description
    return schema


def _schema_champ(champ: Champ) -> dict[str, Any]:
    if champ.type != "tableau":
        return _schema_valeur(champ)

    proprietes = {c.nom: _schema_valeur(c) for c in champ.colonnes}
    ligne = {
        "type": "object",
        "properties": proprietes,
        "required": list(proprietes),
        "additionalProperties": False,
    }
    return {
        "type": ["array", "null"],
        "items": ligne,
        "description": " ".join(p for p in (champ.libelle, champ.description) if p),
    }


def construire_schema(modele: Modele) -> dict[str, Any]:
    """JSON Schema complet : les champs, la confiance associée, et des notes."""
    champs = {c.nom: _schema_champ(c) for c in modele.champs}

    confiance = {
        c.nom: {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": (
                f"Confiance dans la valeur extraite pour {c.nom} "
                "(1 = lue explicitement dans le document, 0 = absente)."
            ),
        }
        for c in modele.champs
    }

    return {
        "type": "object",
        "properties": {
            "champs": {
                "type": "object",
                "properties": champs,
                "required": list(champs),
                "additionalProperties": False,
            },
            "confiance": {
                "type": "object",
                "properties": confiance,
                "required": list(confiance),
                "additionalProperties": False,
            },
            "type_document": {
                "type": ["string", "null"],
                "description": "Nature du document telle qu'observée (facture, CNI, ...).",
            },
            "remarques": {
                "type": ["string", "null"],
                "description": (
                    "Anomalies utiles à l'utilisateur : page illisible, document "
                    "tronqué, incohérence de totaux. null si rien à signaler."
                ),
            },
        },
        "required": ["champs", "confiance", "type_document", "remarques"],
        "additionalProperties": False,
    }
