"""Extraction : construction de la requête et lecture de la réponse, sans réseau."""

import json
from types import SimpleNamespace

import pytest

from docscan.extraction import ErreurExtraction, extraire
from docscan.modeles import Modele

MODELE = Modele.depuis_dict(
    {
        "nom": "test",
        "description": "Document de test",
        "champs": [
            {"nom": "numero", "libelle": "Numéro"},
            {"nom": "total", "type": "nombre"},
        ],
    }
)


class FauxClient:
    """Remplace anthropic.Anthropic : mémorise l'appel et renvoie une réponse figée."""

    def __init__(self, charge_utile=None, stop_reason="end_turn"):
        self.appel = None
        self.charge_utile = charge_utile if charge_utile is not None else {
            "champs": {"numero": "F-2024-001", "total": 120.5},
            "confiance": {"numero": 1.0, "total": 0.6},
            "type_document": "facture",
            "remarques": None,
        }
        self.stop_reason = stop_reason
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.appel = kwargs
        texte = (
            self.charge_utile
            if isinstance(self.charge_utile, str)
            else json.dumps(self.charge_utile)
        )
        return SimpleNamespace(
            stop_reason=self.stop_reason,
            stop_details=None,
            content=[SimpleNamespace(type="text", text=texte)],
            usage=SimpleNamespace(input_tokens=1200, output_tokens=90),
        )


@pytest.fixture
def document(tmp_path):
    fichier = tmp_path / "facture.png"
    fichier.write_bytes(b"\x89PNG\r\n\x1a\n")
    return fichier


def test_requete_contient_document_schema_et_consignes(document):
    client = FauxClient()
    extraire(document, MODELE, client=client)

    contenu = client.appel["messages"][0]["content"]
    assert contenu[0]["type"] == "image"
    assert "numero" in contenu[1]["text"]
    assert client.appel["output_config"]["format"]["type"] == "json_schema"
    schema = client.appel["output_config"]["format"]["schema"]
    assert set(schema["properties"]["champs"]["properties"]) == {"numero", "total"}


def test_resultat_expose_valeurs_confiance_et_usage(document):
    resultat = extraire(document, MODELE, client=FauxClient())
    assert resultat.champs["numero"] == "F-2024-001"
    assert resultat.type_document == "facture"
    assert resultat.usage["input_tokens"] == 1200


def test_champs_manquants_et_a_verifier(document):
    client = FauxClient(
        {
            "champs": {"numero": None, "total": 10},
            "confiance": {"numero": 0.0, "total": 0.4},
            "type_document": None,
            "remarques": "Page 2 illisible",
        }
    )
    resultat = extraire(document, MODELE, client=client)
    assert resultat.champs_manquants == ["numero"]
    assert resultat.champs_a_verifier(seuil=0.8) == ["total"]
    assert resultat.remarques == "Page 2 illisible"


def test_reponse_non_json_leve_une_erreur_claire(document):
    with pytest.raises(ErreurExtraction, match="illisible"):
        extraire(document, MODELE, client=FauxClient("ceci n'est pas du JSON"))


def test_reponse_tronquee_leve_une_erreur(document):
    client = FauxClient(stop_reason="max_tokens")
    with pytest.raises(ErreurExtraction, match="tronquée"):
        extraire(document, MODELE, client=client)


def test_refus_du_modele_leve_une_erreur(document):
    client = FauxClient(stop_reason="refusal")
    with pytest.raises(ErreurExtraction, match="refusé"):
        extraire(document, MODELE, client=client)
