"""Sources de prospects gratuites et légales : API Recherche d'entreprises (SIRENE, data.gouv) et OpenStreetMap."""
import json
import re
import time
import unicodedata
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = "jour-un/1.0 (kits de lancement; github.com/ardaaris14-del/mon-premier-projet)"
FORMES = {"SARL", "SAS", "SASU", "EURL", "SA", "SNC", "EI", "EIRL", "ETS", "ETABLISSEMENTS", "SCI", "SELARL"}


def http_json(url, data=None, essais=3):
    corps = urlencode(data).encode() if data else None
    for essai in range(essais):
        try:
            with urlopen(Request(url, data=corps, headers={"User-Agent": UA}), timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if essai == essais - 1:
                raise
            time.sleep(5 * (essai + 1))


def normaliser(nom):
    s = unicodedata.normalize("NFKD", nom or "").encode("ascii", "ignore").decode().upper()
    mots = "".join(c if c.isalnum() else " " for c in s).split()
    return " ".join(m for m in mots if m not in FORMES)


PETITS_MOTS = {"de", "du", "des", "la", "le", "les", "et", "en", "sur", "au", "aux", "d", "l"}


def joli(nom):
    mots = []
    for i, mot in enumerate(nom.lower().split()):
        parties = mot.split("'")
        mots.append("'".join(p if (p in PETITS_MOTS and (i or j)) or p[:1].isdigit() else p.capitalize()
                             for j, p in enumerate(parties)))
    return " ".join(mots)


def ville_courte(ville):
    return re.sub(r"\s+\d+(er|e|eme)?\s+arrondissement$", "", ville, flags=re.I)


def communes(code_postal):
    url = "https://geo.api.gouv.fr/communes?" + urlencode({"codePostal": code_postal, "fields": "nom,code"})
    return http_json(url)


def sirene(naf, code_postal, pages_max=4):
    resultats = []
    for page in range(1, pages_max + 1):
        url = "https://recherche-entreprises.api.gouv.fr/search?" + urlencode({
            "activite_principale": naf, "code_postal": code_postal,
            "etat_administratif": "A", "per_page": 25, "page": page,
        })
        reponse = http_json(url)
        resultats.extend(reponse.get("results", []))
        if page >= reponse.get("total_pages", 1):
            break
        time.sleep(0.3)
    return resultats


def parse_sirene(resultats, metier, code_postal):
    prospects = []
    for r in resultats:
        etablissements = [e for e in (r.get("matching_etablissements") or []) if e.get("code_postal") == code_postal]
        etab = etablissements[0] if etablissements else (r.get("siege") or {})
        nom_brut = ((etab.get("liste_enseignes") or [None])[0]) or r.get("nom_complet") or ""
        if not nom_brut or "NON-DIFFUSIBLE" in nom_brut.upper():
            continue
        if (etab.get("etat_administratif") or r.get("etat_administratif")) not in (None, "A"):
            continue
        if (r.get("nombre_etablissements_ouverts") or 1) > 5:
            continue
        prospects.append({
            "id": f"s-{r['siren']}",
            "nom": joli(nom_brut),
            "metier": metier,
            "adresse": joli(etab.get("adresse") or ""),
            "code_postal": etab.get("code_postal") or code_postal,
            "ville": ville_courte(joli(etab.get("libelle_commune") or "")),
            "siret": etab.get("siret") or "",
            "date_creation": etab.get("date_creation") or r.get("date_creation") or "",
            "telephone": "", "email": "", "site_web": "",
            "sources": ["sirene"],
        })
    return prospects


def insee(naf, departement, depuis, cle):
    """Établissements créés depuis une date (API Sirene de l'INSEE, clé gratuite sur portail-api.insee.fr)."""
    q = (f"dateCreationEtablissement:[{depuis} TO *] AND codePostalEtablissement:{departement}* "
         f"AND periode(activitePrincipaleEtablissement:{naf} AND etatAdministratifEtablissement:A)")
    url = "https://api.insee.fr/api-sirene/3.11/siret?" + urlencode({"q": q, "nombre": 1000})
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json", "X-INSEE-Api-Key-Integration": cle})
    try:
        with urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except HTTPError as err:
        if err.code == 404:
            return {"etablissements": []}
        raise


def parse_insee(reponse, metier):
    prospects = []
    for et in reponse.get("etablissements", []):
        ul = et.get("uniteLegale") or {}
        if "P" in (ul.get("statutDiffusionUniteLegale"), et.get("statutDiffusionEtablissement")):
            continue
        per = (et.get("periodesEtablissement") or [{}])[0]
        personne = " ".join(x for x in [ul.get("prenomUsuelUniteLegale"), ul.get("nomUniteLegale")] if x)
        nom = (per.get("enseigne1Etablissement") or per.get("denominationUsuelleEtablissement")
               or ul.get("denominationUniteLegale") or personne)
        if not nom or "[ND]" in nom:
            continue
        a = et.get("adresseEtablissement") or {}
        rue = " ".join(x for x in [a.get("numeroVoieEtablissement"), a.get("typeVoieEtablissement"),
                                   a.get("libelleVoieEtablissement")] if x)
        cp, ville = a.get("codePostalEtablissement") or "", a.get("libelleCommuneEtablissement") or ""
        prospects.append({
            "id": f"s-{et['siren']}",
            "nom": joli(nom),
            "metier": metier,
            "adresse": joli(" ".join(x for x in [rue, cp, ville] if x)),
            "code_postal": cp,
            "ville": ville_courte(joli(ville)),
            "siret": et.get("siret") or "",
            "date_creation": et.get("dateCreationEtablissement") or "",
            "telephone": "", "email": "", "site_web": "",
            "sources": ["sirene"],
        })
    return prospects


def osm(code_insee, tags):
    filtres = "".join(f'nwr["{k}"="{v}"](area.a);' for k, v in tags)
    requete = (f'[out:json][timeout:90];area["ref:INSEE"="{code_insee}"]["boundary"="administrative"]->.a;'
               f"({filtres});out center tags;")
    return http_json("https://overpass-api.de/api/interpreter", data={"data": requete})


def parse_osm(reponse, tag_vers_metier, ville):
    prospects = []
    for el in reponse.get("elements", []):
        t = el.get("tags", {})
        if not t.get("name"):
            continue
        metier = next((m for (k, v), m in tag_vers_metier.items() if t.get(k) == v), None)
        if not metier:
            continue
        rue = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
        cp = t.get("addr:postcode", "")
        prospects.append({
            "id": f"o-{el['type'][0]}{el['id']}",
            "nom": t["name"],
            "metier": metier,
            "adresse": ", ".join(x for x in [rue, " ".join(x for x in [cp, t.get("addr:city", ville)] if x)] if x),
            "code_postal": cp,
            "ville": t.get("addr:city", ville),
            "siret": "",
            "date_creation": "",
            "telephone": t.get("phone") or t.get("contact:phone") or "",
            "email": t.get("email") or t.get("contact:email") or "",
            "site_web": t.get("website") or t.get("contact:website") or "",
            "sources": ["osm"],
        })
    return prospects
