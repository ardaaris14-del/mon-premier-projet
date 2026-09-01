"""Modèles de champs : la liste des informations à extraire d'un document.

Un modèle est un simple fichier JSON, ce qui permet d'en créer un nouveau sans
toucher au code. Voir docscan/modeles/*.json pour des exemples.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DOSSIER_MODELES = Path(__file__).parent / "modeles"

TYPES_SIMPLES = {"texte", "nombre", "entier", "booleen", "date", "liste", "choix"}
TYPES_VALIDES = TYPES_SIMPLES | {"tableau"}

_NOM_VALIDE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class ErreurModele(ValueError):
    """Le fichier de modèle est invalide."""


@dataclass
class Champ:
    """Un champ à remplir à partir du document."""

    nom: str
    libelle: str = ""
    type: str = "texte"
    description: str = ""
    obligatoire: bool = False
    choix: list[str] = field(default_factory=list)
    colonnes: list["Champ"] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not _NOM_VALIDE.match(self.nom):
            raise ErreurModele(
                f"Nom de champ invalide : {self.nom!r}. "
                "Utilisez des lettres, chiffres et underscores, sans espace."
            )
        if self.type not in TYPES_VALIDES:
            raise ErreurModele(
                f"Type inconnu pour le champ {self.nom!r} : {self.type!r}. "
                f"Types acceptés : {', '.join(sorted(TYPES_VALIDES))}."
            )
        if self.type == "choix" and not self.choix:
            raise ErreurModele(
                f"Le champ {self.nom!r} est de type 'choix' mais aucune valeur "
                "n'est proposée dans 'choix'."
            )
        if self.type == "tableau" and not self.colonnes:
            raise ErreurModele(
                f"Le champ {self.nom!r} est de type 'tableau' mais aucune "
                "colonne n'est définie dans 'colonnes'."
            )
        if self.type != "tableau" and self.colonnes:
            raise ErreurModele(
                f"Le champ {self.nom!r} définit des colonnes alors qu'il n'est "
                "pas de type 'tableau'."
            )
        if not self.libelle:
            self.libelle = self.nom.replace("_", " ").capitalize()

    @classmethod
    def depuis_dict(cls, donnees: dict[str, Any]) -> "Champ":
        if "nom" not in donnees:
            raise ErreurModele(f"Champ sans clé 'nom' : {donnees!r}")
        inconnues = set(donnees) - {
            "nom", "libelle", "type", "description", "obligatoire", "choix", "colonnes",
        }
        if inconnues:
            raise ErreurModele(
                f"Clés inconnues pour le champ {donnees['nom']!r} : "
                f"{', '.join(sorted(inconnues))}"
            )
        colonnes = [cls.depuis_dict(c) for c in donnees.get("colonnes", [])]
        for colonne in colonnes:
            if colonne.type == "tableau":
                raise ErreurModele(
                    "Un tableau ne peut pas contenir un autre tableau "
                    f"(colonne {colonne.nom!r})."
                )
        return cls(
            nom=donnees["nom"],
            libelle=donnees.get("libelle", ""),
            type=donnees.get("type", "texte"),
            description=donnees.get("description", ""),
            obligatoire=bool(donnees.get("obligatoire", False)),
            choix=list(donnees.get("choix", [])),
            colonnes=colonnes,
        )


@dataclass
class Modele:
    """Un ensemble de champs, pour un type de document donné."""

    nom: str
    champs: list[Champ]
    description: str = ""
    instructions: str = ""
    source: Path | None = None

    @classmethod
    def depuis_dict(cls, donnees: dict[str, Any], source: Path | None = None) -> "Modele":
        if not isinstance(donnees, dict):
            raise ErreurModele("Le fichier de modèle doit contenir un objet JSON.")
        champs_bruts = donnees.get("champs")
        if not champs_bruts:
            raise ErreurModele("Le modèle ne définit aucun champ (clé 'champs').")
        champs = [Champ.depuis_dict(c) for c in champs_bruts]
        noms = [c.nom for c in champs]
        doublons = {n for n in noms if noms.count(n) > 1}
        if doublons:
            raise ErreurModele(f"Champs en double : {', '.join(sorted(doublons))}")
        return cls(
            nom=donnees.get("nom") or (source.stem if source else "sans_nom"),
            champs=champs,
            description=donnees.get("description", ""),
            instructions=donnees.get("instructions", ""),
            source=source,
        )

    @classmethod
    def depuis_fichier(cls, chemin: str | Path) -> "Modele":
        chemin = Path(chemin)
        try:
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise ErreurModele(f"Modèle introuvable : {chemin}") from None
        except json.JSONDecodeError as err:
            raise ErreurModele(f"JSON invalide dans {chemin} : {err}") from None
        return cls.depuis_dict(donnees, source=chemin)


def _dossiers_de_recherche() -> list[Path]:
    """Dossiers où chercher un modèle nommé, du plus spécifique au plus général."""
    return [Path.cwd() / "modeles", DOSSIER_MODELES]


def charger_modele(reference: str | Path) -> Modele:
    """Charge un modèle par nom ('facture') ou par chemin ('./mon_modele.json')."""
    chemin = Path(reference)
    if chemin.suffix == ".json" or chemin.exists():
        return Modele.depuis_fichier(chemin)

    for dossier in _dossiers_de_recherche():
        candidat = dossier / f"{reference}.json"
        if candidat.exists():
            return Modele.depuis_fichier(candidat)

    disponibles = ", ".join(sorted(lister_modeles())) or "aucun"
    raise ErreurModele(
        f"Modèle {reference!r} introuvable. Modèles disponibles : {disponibles}. "
        "Vous pouvez aussi passer le chemin d'un fichier JSON."
    )


def lister_modeles() -> dict[str, Path]:
    """Nom -> chemin de tous les modèles trouvés (le local l'emporte sur l'intégré)."""
    trouves: dict[str, Path] = {}
    for dossier in reversed(_dossiers_de_recherche()):
        if not dossier.is_dir():
            continue
        for fichier in sorted(dossier.glob("*.json")):
            trouves[fichier.stem] = fichier
    return trouves
