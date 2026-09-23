import base64
import hashlib
import json
import re
import sys
import tempfile
import unittest
import unittest.mock
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
            n = len(machine.construire_site(CONFIG, self.prospects(), sortie, AUJOURDHUI))
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
            for f in ("manifest.json", "icone-180.png", "icone-192.png", "icone-512.png"):
                self.assertTrue((sortie / "cockpit" / f).exists(), f)
            self.assertNotIn("Ancien Garage", cockpit)
            self.assertIn(CONFIG["moi"]["nom"], (sortie / "index.html").read_text(encoding="utf-8"))

    def test_publications_clients(self):
        clients = [{"nom": "Plomberie Durand", "metier": "plombier", "ville": "Villeurbanne"},
                   {"nom": "Inconnu", "metier": "astronaute", "ville": "Lyon"}]
        res = machine.publications_clients(clients, AUJOURDHUI)
        sans_ville = machine.publications({"nom": "X", "metier": "garage", "ville": ""}, AUJOURDHUI)
        self.assertTrue(all(" à  " not in x and "de  " not in x for _, x, _ in sans_ville))
        self.assertIn("dans la région", sans_ville[1][1])
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]["posts"]), 4)
        self.assertIn("chaudière", res[0]["posts"][0]["texte"])

    def test_boutons_de_paiement(self):
        import kit
        config = json.loads(json.dumps(CONFIG))
        p = {"nom": "Test Sàrl", "metier": "coiffeur", "ville": "Delémont"}
        config["offre"].update(lien_paiement="https://pay/suivi", lien_paiement_kit="https://pay/kit")
        page = kit.page_kit(p, config, "x")
        self.assertIn('href="https://pay/suivi">Kit + suivi', page)
        self.assertIn('href="https://pay/kit">Kit seul', page)
        config["offre"].update(lien_paiement="", lien_paiement_kit="")
        self.assertIn('href="tel:', kit.page_kit(p, config, "x").split('class="offre"')[1])

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


class FausseBase:
    def __init__(self, tables):
        self.t = {k: [dict(x) for x in v] for k, v in tables.items()}

    def _filtre(self, table, filtres):
        lignes = self.t.setdefault(table, [])
        for col, cond in filtres.items():
            if col in ("select", "order", "limit"):
                continue
            if cond == "is.null":
                lignes = [x for x in lignes if x.get(col) is None]
            elif cond.startswith("eq."):
                lignes = [x for x in lignes if str(x.get(col)) == cond[3:]]
        return lignes

    def lire(self, table, **params):
        return [dict(x) for x in self._filtre(table, params)]

    def inserer(self, table, ligne):
        ligne = {"id": len(self.t.setdefault(table, [])) + 1, **ligne}
        self.t[table].append(ligne)
        return ligne

    def upsert(self, table, lignes, conflit):
        cles = conflit.split(",")
        for l in lignes:
            existant = next((x for x in self.t.setdefault(table, []) if all(x.get(k) == l[k] for k in cles)), None)
            if existant:
                existant.update(l)
            else:
                self.t[table].append(dict(l))

    def modifier(self, table, valeurs, **filtres):
        for x in self._filtre(table, filtres):
            x.update(valeurs)

    def supprimer_ids(self, table, ids, colonne="id"):
        ids = set(ids)
        self.t[table] = [x for x in self.t.get(table, []) if x[colonne] not in ids]


class Supabase(unittest.TestCase):
    def test_entetes_selon_le_type_de_cle(self):
        import base
        self.assertNotIn("Authorization", base.Base("https://x.supabase.co", "sb_secret_abc").entetes)
        self.assertEqual(base.Base("https://x.supabase.co", "eyJ.jwt").entetes["Authorization"], "Bearer eyJ.jwt")

    def test_execution_complete_avec_la_base(self):
        import argparse
        prospects = Machine().prospects()
        ancien = {**{k: v for k, v in prospects[0].items() if k != "slug"}, "id": "c-999", "nom": "Vieux Client", "date_creation": "2025-01-01"}
        stoppe = next(p for p in prospects if p["id"] == "s-987654321")
        fausse = FausseBase({
            "reglages": [{"id": 1, "data": {**CONFIG, "pays": "FR"}, "meta": {}}],
            "suivi": [{"prospect_id": "c-999", "statut": "Intéressé", "stop": False},
                      {"prospect_id": stoppe["id"], "statut": "Pas intéressé", "stop": True}],
            "clients": [{"id": "u1", "nom": "Garage Test", "metier": "garage", "ville": "Delémont", "suivi": True},
                        {"id": "u2", "nom": "Kit Seul", "metier": "coiffeur", "ville": "Porrentruy", "formule": "kit", "suivi": False}],
            "prospects": [{"id": "obsolete"}],
            "demandes": [{"id": 1, "traitee_le": None}],
        })
        originaux = (machine.DONNEES,)
        with tempfile.TemporaryDirectory() as tmp:
            machine.DONNEES = Path(tmp)
            (Path(tmp) / "prospects.json").write_text(json.dumps(prospects + [ancien]), encoding="utf-8")
            try:
                args = argparse.Namespace(hors_ligne=True, sortie=str(Path(tmp) / "_site"), exiger_chiffrement=False)
                with unittest.mock.patch.dict("os.environ", {"GITHUB_REPOSITORY": "Moi/projet"}):
                    stats = machine.executer(args, AUJOURDHUI, fausse)
            finally:
                (machine.DONNEES,) = originaux
        ids = {p["id"] for p in fausse.t["prospects"]}
        self.assertIn("c-999", ids, "un prospect suivi garde son kit même ancien")
        self.assertNotIn(stoppe["id"], ids, "un stop disparaît")
        self.assertNotIn("obsolete", ids)
        self.assertEqual(stats["kits"], len(ids))
        vieux = next(p for p in fausse.t["prospects"] if p["id"] == "c-999")
        self.assertTrue(vieux["kit_url"].startswith("https://moi.github.io/projet/k/"))
        self.assertEqual([x["client_id"] for x in fausse.t["publications"]], ["u1"], "pas de publications sans suivi")
        self.assertIsNotNone(fausse.t["demandes"][0]["traitee_le"])
        self.assertIn("coiffeur", fausse.t["reglages"][0]["meta"]["metiers"])


class Decision(unittest.TestCase):
    def test_decision(self):
        import decision
        base = FausseBase({"demandes": [{"id": 1, "traitee_le": None}]})
        vide = FausseBase({"demandes": [{"id": 1, "traitee_le": "2026-09-23"}]})
        self.assertTrue(decision.faut_il_lancer("workflow_dispatch", "", None))
        self.assertTrue(decision.faut_il_lancer("push", "", None))
        self.assertTrue(decision.faut_il_lancer("schedule", "0 5 * * *", None))
        self.assertTrue(decision.faut_il_lancer("schedule", "*/15 * * * *", base))
        self.assertFalse(decision.faut_il_lancer("schedule", "*/15 * * * *", vide))
        self.assertFalse(decision.faut_il_lancer("schedule", "*/15 * * * *", None))


if __name__ == "__main__":
    unittest.main()
