"""Le JSON Schema envoyé à l'API doit rester strictement valide."""

from docscan.modeles import Modele, charger_modele
from docscan.schema import construire_schema


def _schema(champs):
    return construire_schema(Modele.depuis_dict({"nom": "t", "champs": champs}))


def test_structure_generale():
    schema = _schema([{"nom": "titre"}])
    assert schema["required"] == ["champs", "confiance", "type_document", "remarques"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["champs"]["required"] == ["titre"]
    assert schema["properties"]["confiance"]["required"] == ["titre"]


def test_tous_les_champs_acceptent_null():
    schema = _schema([
        {"nom": "a", "type": "texte"},
        {"nom": "b", "type": "nombre"},
        {"nom": "c", "type": "booleen"},
        {"nom": "d", "type": "liste"},
    ])
    for propriete in schema["properties"]["champs"]["properties"].values():
        assert "null" in propriete["type"]


def test_choix_autorise_null_dans_enum():
    schema = _schema([{"nom": "devise", "type": "choix", "choix": ["EUR", "USD"]}])
    enum = schema["properties"]["champs"]["properties"]["devise"]["enum"]
    assert enum == ["EUR", "USD", None]


def test_tableau_produit_un_tableau_d_objets_stricts():
    schema = _schema([
        {
            "nom": "lignes",
            "type": "tableau",
            "colonnes": [{"nom": "designation"}, {"nom": "montant", "type": "nombre"}],
        }
    ])
    lignes = schema["properties"]["champs"]["properties"]["lignes"]
    assert lignes["type"] == ["array", "null"]
    item = lignes["items"]
    assert item["additionalProperties"] is False
    assert item["required"] == ["designation", "montant"]


def test_confiance_bornee_entre_0_et_1():
    schema = _schema([{"nom": "titre"}])
    note = schema["properties"]["confiance"]["properties"]["titre"]
    assert (note["minimum"], note["maximum"]) == (0, 1)


def test_schema_des_modeles_integres():
    for nom in ("facture", "carte_identite", "rib", "exemple_personnalise"):
        schema = construire_schema(charger_modele(nom))
        proprietes = schema["properties"]["champs"]["properties"]
        assert proprietes and set(proprietes) == set(
            schema["properties"]["confiance"]["properties"]
        )
