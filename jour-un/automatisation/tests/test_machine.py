import base64
import hashlib
import json
import re
import sys
import tempfile
import unittest
from xml.sax.saxutils import escape
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import machine  # noqa: E402
import sources  # noqa: E402

AUJOURDHUI = date(2026, 9, 22)

SIRENE = [
    {"siren": "912345678", "nom_complet": "PLOMBERIE DURAND", "date_creation": "2026-09-01",
     "etat_administratif": "A", "nombre_etablissements_ouverts": 1,
     "siege": {"code_postal": "69100", "adresse": "12 RUE DES LILAS 69100 VILLEURBANNE",
               "libelle_commune": "VILLEURBANNE", "siret": "91234567800011", "etat_administratif": "A",
               "date_creation": "2026-09-01", "liste_enseignes": None}},
    {"siren": "111111111", "nom_complet": "[NON-DIFFUSIBLE]", "etat_administratif": "A", "siege": {}},
    {"siren": "222222222", "nom_complet": "GRANDE CHAINE", "etat_administratif": "A",
     "nombre_etablissements_ouverts": 40, "siege": {"code_postal": "69100"}},
    {"siren": "333333333", "nom_complet": "ANCIEN GARAGE", "date_creation": "2001-01-01", "etat_administratif": "A",
     "siege": {"code_postal": "69100", "libelle_commune": "VILLEURBANNE", "etat_administratif": "A"}},
]

INSEE = {"etablissements": [
    {"siren": "987654321", "siret": "98765432100019", "dateCreationEtablissement": "2026-09-15",
     "statutDiffusionEtablissement": "O",
     "uniteLegale": {"statutDiffusionUniteLegale": "O", "nomUniteLegale": "MARTIN", "prenomUsuelUniteLegale": "LEA"},
     "adresseEtablissement": {"numeroVoieEtablissement": "3", "typeVoieEtablissement": "RUE",
                              "libelleVoieEtablissement": "DE LA REPUBLIQUE", "codePostalEtablissement": "69002",
                              "libelleCommuneEtablissement": "LYON 2E ARRONDISSEMENT"},
     "periodesEtablissement": [{"enseigne1Etablissement": "L'ATELIER DE LEA"}]},
    {"siren": "555555555", "statutDiffusionEtablissement": "P", "uniteLegale": {}},
]}

OSM = {"elements": [
    {"type": "node", "id": 42, "tags": {"name": "Plomberie Durand", "craft": "plumber", "phone": "06 12 34 56 78",
                                         "addr:city": "Villeurbanne"}},
    {"type": "way", "id": 7, "tags": {"name": "Coiffure Soleil", "shop": "hairdresser", "website": "https://soleil.fr"}},
    {"type": "node", "id": 8, "tags": {"shop": "hairdresser"}},
]}

CONFIG = json.loads((Path(machine.ICI) / "config.json").read_text(encoding="utf-8"))


class Sources(unittest.TestCase):
    def test_sirene_filtre_et_normalise(self):
        ps = sources.parse_sirene(SIRENE, "plombier", "69100")
        self.assertEqual([p["nom"] for p in ps], ["Plomberie Durand", "Ancien Garage"])
        self.assertEqual(ps[0]["ville"], "Villeurbanne")
        self.assertEqual(ps[0]["date_creation"], "2026-09-01")

    def test_insee_utilise_enseigne_et_ignore_non_diffusibles(self):
        ps = sources.parse_insee(INSEE, "coiffeur")
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0]["nom"], "L'Atelier de Lea")
        self.assertEqual(ps[0]["id"], "s-987654321")
        self.assertIn("69002", ps[0]["adresse"])

    def test_osm(self):
        tags = {("craft", "plumber"): "plombier", ("shop", "hairdresser"): "coiffeur"}
        ps = sources.parse_osm(OSM, tags, "Villeurbanne")
        self.assertEqual(len(ps), 2)
        self.assertEqual(ps[0]["telephone"], "06 12 34 56 78")
        self.assertEqual(ps[1]["site_web"], "https://soleil.fr")


class Machine(unittest.TestCase):
    def prospects(self):
        tags = {("craft", "plumber"): "plombier", ("shop", "hairdresser"): "coiffeur"}
        bruts = (sources.parse_sirene(SIRENE, "plombier", "69100") + sources.parse_insee(INSEE, "coiffeur")
                 + sources.parse_osm(OSM, tags, "Villeurbanne"))
        ps = machine.fusionner([], bruts, AUJOURDHUI.isoformat())
        for p in ps:
            machine.noter(p, AUJOURDHUI)
            p["slug"] = machine.slug(p)
        return ps

    def test_fusion_recupere_le_telephone_osm(self):
        ps = {p["id"]: p for p in self.prospects()}
        self.assertEqual(ps["s-912345678"]["telephone"], "06 12 34 56 78")
        self.assertNotIn("o-n42", ps)

    def test_fusion_conserve_la_date_de_premiere_detection(self):
        anciens = [{**p, "premiere_detection": "2026-01-01"} for p in self.prospects()]
        ps = machine.fusionner(anciens, sources.parse_sirene(SIRENE, "plombier", "69100"), AUJOURDHUI.isoformat())
        self.assertTrue(all(p["premiere_detection"] == "2026-01-01" for p in ps))

    def test_eligibilite_kit(self):
        ps = {p["id"]: p for p in self.prospects()}
        self.assertTrue(machine.eligible_kit(ps["s-912345678"], AUJOURDHUI, 90))
        self.assertFalse(machine.eligible_kit(ps["s-333333333"], AUJOURDHUI, 90))
        self.assertNotIn("o-w7", ps)

    def test_construction_du_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            sortie = Path(tmp) / "_site"
            n = machine.construire_site(CONFIG, self.prospects(), sortie, AUJOURDHUI)
            self.assertEqual(n, 2)
            pages = list(sortie.glob("k/*/index.html")) + list(sortie.glob("m/*/index.html"))
            self.assertEqual(len(pages), 4)
            for page in pages + [sortie / "index.html", sortie / "cockpit" / "index.html"]:
                html = page.read_text(encoding="utf-8")
                self.assertIsNone(re.search(r"\$[a-z_]+|__DONNEES__", html), page)
            for page in pages:
                self.assertIn('name="robots" content="noindex', page.read_text(encoding="utf-8"))
            cockpit = (sortie / "cockpit" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Plomberie Durand", cockpit)
            self.assertNotIn("Ancien Garage", cockpit)
            self.assertIn(CONFIG["moi"]["nom"], (sortie / "index.html").read_text(encoding="utf-8"))

    def test_publications_clients(self):
        clients = [{"nom": "Plomberie Durand", "metier": "plombier", "ville": "Villeurbanne"},
                   {"nom": "Inconnu", "metier": "astronaute", "ville": "Lyon"}]
        res = machine.publications_clients(clients, AUJOURDHUI)
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]["posts"]), 4)
        self.assertIn("chaudière", res[0]["posts"][0]["texte"])

    def test_cockpit_chiffre(self):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        with tempfile.TemporaryDirectory() as tmp:
            sortie = Path(tmp) / "_site"
            machine.construire_site(CONFIG, self.prospects(), sortie, AUJOURDHUI, [], "secret-123", True)
            html = (sortie / "cockpit" / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("Plomberie Durand", html)
            charge = json.loads(re.search(r"const CHARGE = (.*);", html).group(1))["chiffre"]
            cle = hashlib.pbkdf2_hmac("sha256", b"secret-123", base64.b64decode(charge["sel"]), charge["iterations"], 32)
            clair = AESGCM(cle).decrypt(base64.b64decode(charge["iv"]), base64.b64decode(charge["donnees"]), None)
            self.assertIn("Plomberie Durand", clair.decode("utf-8"))

    def test_cockpit_jamais_en_clair_si_chiffrement_exige(self):
        with tempfile.TemporaryDirectory() as tmp:
            sortie = Path(tmp) / "_site"
            machine.construire_site(CONFIG, self.prospects(), sortie, AUJOURDHUI, [], "", True)
            html = (sortie / "cockpit" / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("Plomberie Durand", html)
            self.assertIn('"manquant": true', html)

    def test_liens_de_kit_dependent_du_secret(self):
        p = {"nom": "Plomberie Durand", "id": "s-912345678"}
        self.assertNotEqual(machine.slug(p, "a"), machine.slug(p, "b"))
        self.assertTrue(machine.slug(p, "a").startswith("plomberie-durand-"))


def xml_fosc(nom, but, forme="0107", uid="123456789", ville="Saignelégier", date_pub="2026-09-21"):
    nom, but = escape(nom), escape(but)
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<HR01:publication xmlns:HR01="https://shab.ch/shab/HR01-export">
<meta><id>x</id><subRubric>HR01</subRubric><language>fr</language><publicationDate>{date_pub}</publicationDate></meta>
<content><commonsNew><company><name>{nom}</name><uid>CHE-{uid[:3]}.{uid[3:6]}.{uid[6:]}</uid>
<uidOrganisationId>{uid}</uidOrganisationId><seat>{ville}</seat><legalForm>{forme}</legalForm>
<address><street>Rue de la Gare</street><houseNumber>4</houseNumber><swissZipCode>2350</swissZipCode><town>{ville}</town></address>
</company><purpose>{but} (cf. statuts pour but complet).</purpose></commonsNew></content></HR01:publication>"""


class Suisse(unittest.TestCase):
    def test_parse_fosc(self):
        p = sources.parse_fosc(xml_fosc("Salon Léa, Léa Martin", "Exploitation d'un salon de coiffure", forme="0101"), machine.classer)
        self.assertEqual(p["id"], "c-123456789")
        self.assertEqual(p["nom"], "Salon Léa")
        self.assertEqual(p["metier"], "coiffeur")
        self.assertEqual(p["adresse"], "Rue de la Gare 4, 2350 Saignelégier")
        self.assertEqual(p["date_creation"], "2026-09-21")
        self.assertNotIn("cf. statuts", p["activite"])

    def test_fosc_exclusions(self):
        self.assertIsNone(sources.parse_fosc(xml_fosc("Alpha Holding SA", "Prise de participations", "0106"), machine.classer))
        self.assertIsNone(sources.parse_fosc(xml_fosc("X SA, succursale de Delémont", "Vente", "0151"), machine.classer))
        self.assertIsNone(sources.parse_fosc(xml_fosc("Club des amis", "Promotion du sport", "0109"), machine.classer))

    def test_generique_utilise_le_but_social(self):
        p = sources.parse_fosc(xml_fosc("C&S Epicerie", "Achat et vente de produits alimentaires; exploitation d'une épicerie"), machine.classer)
        self.assertEqual(p["metier"], "generique")
        p["slug"] = "x"
        conf = machine.config_maquette(p, CONFIG)
        self.assertEqual(conf["accroche"], "Achat et vente de produits alimentaires.")
        self.assertEqual(conf["titre"], "C&S Epicerie, à Saignelégier")

    def test_classement_des_metiers(self):
        cas = {"Installations sanitaires et chauffage": "plombier", "Travaux de nettoyage et conciergerie": "nettoyage",
               "Exploitation d'un café-restaurant": "restaurant", "Entretien et création de jardins": "paysagiste",
               "Salon de coiffure pour hommes (barbier)": "coiffeur"}
        for texte, attendu in cas.items():
            self.assertEqual(machine.classer(texte), attendu, texte)

    def test_numeros_suisses(self):
        import generer_site
        self.assertEqual(generer_site.lien_tel("076 698 40 59", "41"), "+41766984059")
        self.assertEqual(generer_site.lien_tel("0041 32 123 45 67", "41"), "+41321234567")

    def test_collecte_suisse_de_bout_en_bout(self):
        metas = [{"id": "a", "subRubric": "HR01", "language": "fr"}, {"id": "b", "subRubric": "HR02", "language": "fr"},
                 {"id": "c", "subRubric": "HR01", "language": "de"}]
        details = {"a": xml_fosc("Salon Léa, Léa Martin", "Exploitation d'un salon de coiffure", forme="0101")}
        osm = {"elements": [{"type": "node", "id": 1, "tags": {"name": "Salon Léa", "shop": "hairdresser",
                                                                  "phone": "+41 32 000 00 00", "addr:city": "Saignelégier"}}]}
        originaux = (sources.fosc_liste, sources.fosc_detail, sources.osm_canton, machine.DONNEES, machine.time.sleep)
        with tempfile.TemporaryDirectory() as tmp:
            sources.fosc_liste = lambda *a, **k: metas
            sources.fosc_detail = lambda i: details[i]
            sources.osm_canton = lambda *a, **k: osm
            machine.DONNEES, machine.time.sleep = Path(tmp), lambda s: None
            try:
                conf = {**CONFIG, "zone": {**CONFIG["zone"], "cantons": ["JU"]}}
                trouves = machine.collecter(conf, AUJOURDHUI)
                self.assertEqual(json.loads((Path(tmp) / "fosc_vus.json").read_text()), ["a"])
                self.assertEqual(len(machine.collecter(conf, AUJOURDHUI)), 1)
            finally:
                sources.fosc_liste, sources.fosc_detail, sources.osm_canton, machine.DONNEES, machine.time.sleep = originaux
        ps = machine.fusionner([], trouves, AUJOURDHUI.isoformat())
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0]["telephone"], "+41 32 000 00 00")


if __name__ == "__main__":
    unittest.main()
