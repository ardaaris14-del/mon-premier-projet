"""Validation des modèles de champs."""

import json

import pytest

from docscan.modeles import Champ, ErreurModele, Modele, charger_modele, lister_modeles


def test_tous_les_modeles_integres_se_chargent():
    modeles = lister_modeles()
    assert "facture" in modeles
    for nom in modeles:
        modele = charger_modele(nom)
        assert modele.champs


def test_libelle_par_defaut_derive_du_nom():
    champ = Champ(nom="numero_facture")
    assert champ.libelle == "Numero facture"


def test_nom_de_champ_invalide_est_rejete():
    with pytest.raises(ErreurModele):
        Champ(nom="numéro facture")


def test_type_inconnu_est_rejete():
    with pytest.raises(ErreurModele):
        Champ(nom="x", type="monnaie")


def test_choix_sans_valeurs_est_rejete():
    with pytest.raises(ErreurModele):
        Champ(nom="devise", type="choix")


def test_tableau_sans_colonnes_est_rejete():
    with pytest.raises(ErreurModele):
        Champ(nom="lignes", type="tableau")


def test_tableau_imbrique_est_rejete():
    with pytest.raises(ErreurModele):
        Champ.depuis_dict(
            {
                "nom": "lignes",
                "type": "tableau",
                "colonnes": [
                    {"nom": "sous", "type": "tableau", "colonnes": [{"nom": "a"}]}
                ],
            }
        )


def test_champs_en_double_sont_rejetes():
    with pytest.raises(ErreurModele):
        Modele.depuis_dict({"champs": [{"nom": "a"}, {"nom": "a"}]})


def test_modele_sans_champ_est_rejete():
    with pytest.raises(ErreurModele):
        Modele.depuis_dict({"nom": "vide", "champs": []})


def test_cle_inconnue_est_signalee():
    with pytest.raises(ErreurModele, match="oblligatoire"):
        Champ.depuis_dict({"nom": "a", "oblligatoire": True})


def test_chargement_depuis_un_fichier(tmp_path):
    fichier = tmp_path / "mon_modele.json"
    fichier.write_text(
        json.dumps({"nom": "perso", "champs": [{"nom": "titre"}]}), encoding="utf-8"
    )
    modele = charger_modele(fichier)
    assert modele.nom == "perso"
    assert modele.champs[0].nom == "titre"


def test_modele_inconnu_liste_les_disponibles():
    with pytest.raises(ErreurModele, match="facture"):
        charger_modele("modele_qui_nexiste_pas")
