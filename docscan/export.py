"""Export des résultats : JSON ou CSV (pour Excel / LibreOffice)."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable

from docscan.extraction import Resultat
from docscan.modeles import Modele


def _cellule(valeur: Any) -> str:
    """Aplatit une valeur pour une cellule de tableur."""
    if valeur is None:
        return ""
    if isinstance(valeur, bool):
        return "oui" if valeur else "non"
    if isinstance(valeur, list):
        if valeur and isinstance(valeur[0], dict):
            return json.dumps(valeur, ensure_ascii=False)
        return " | ".join(str(v) for v in valeur)
    return str(valeur)


def vers_json(resultats: Iterable[Resultat], *, indent: int = 2) -> str:
    liste = [r.to_dict() for r in resultats]
    donnees = liste[0] if len(liste) == 1 else liste
    return json.dumps(donnees, ensure_ascii=False, indent=indent)


def vers_csv(resultats: Iterable[Resultat], modele: Modele, *, confiance: bool = False) -> str:
    """Une ligne par document, une colonne par champ."""
    noms = [c.nom for c in modele.champs]
    entetes = ["document", *noms]
    if confiance:
        entetes += [f"confiance_{n}" for n in noms]

    tampon = io.StringIO()
    writer = csv.writer(tampon, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(entetes)
    for resultat in resultats:
        ligne = [resultat.document, *(_cellule(resultat.champs.get(n)) for n in noms)]
        if confiance:
            ligne += [_cellule(resultat.confiance.get(n)) for n in noms]
        writer.writerow(ligne)
    return tampon.getvalue()
