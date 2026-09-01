"""Exports JSON et CSV."""

import json

from docscan.export import vers_csv, vers_json
from docscan.extraction import Resultat
from docscan.modeles import Modele

MODELE = Modele.depuis_dict(
    {
        "nom": "test",
        "champs": [
            {"nom": "numero"},
            {"nom": "paye", "type": "booleen"},
            {"nom": "tags", "type": "liste"},
        ],
    }
)

RESULTAT = Resultat(
    document="a.pdf",
    modele="test",
    champs={"numero": "F-1", "paye": True, "tags": ["urgent", "relance"]},
    confiance={"numero": 1.0, "paye": 0.5, "tags": 0.9},
)


def test_json_d_un_seul_document_est_un_objet():
    donnees = json.loads(vers_json([RESULTAT]))
    assert donnees["champs"]["numero"] == "F-1"
    assert donnees["champs_manquants"] == []


def test_json_de_plusieurs_documents_est_une_liste():
    donnees = json.loads(vers_json([RESULTAT, RESULTAT]))
    assert isinstance(donnees, list) and len(donnees) == 2


def test_csv_une_colonne_par_champ():
    lignes = vers_csv([RESULTAT], MODELE).strip().splitlines()
    assert lignes[0] == "document;numero;paye;tags"
    assert lignes[1] == "a.pdf;F-1;oui;urgent | relance"


def test_csv_avec_colonnes_de_confiance():
    entete = vers_csv([RESULTAT], MODELE, confiance=True).splitlines()[0]
    assert entete.endswith("confiance_numero;confiance_paye;confiance_tags")


def test_csv_valeur_absente_reste_vide():
    vide = Resultat(document="b.pdf", modele="test", champs={"numero": None})
    assert vers_csv([vide], MODELE).splitlines()[1] == "b.pdf;;;"
