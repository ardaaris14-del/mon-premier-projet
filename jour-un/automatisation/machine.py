"""La machine Jour Un : trouve les entreprises nouvelles, prépare leur kit de lancement et le cockpit.

Usage :
    python3 machine.py               # tout (avec recherche de nouveaux prospects)
    python3 machine.py --hors-ligne  # reconstruit le site sans appeler les API
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import shutil
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
sys.path.insert(0, str(RACINE / "generateur"))

import generer_site  # noqa: E402
import kit  # noqa: E402
import sources  # noqa: E402
from metiers import METIERS, SAISONS, classer  # noqa: E402

DONNEES = ICI / "donnees"
ITERATIONS = 250_000
INDICATIFS = {"FR": "33", "CH": "41"}


def lire_json(chemin, defaut):
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else defaut


def ecrire_json(chemin, valeur):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def log(*args):
    print(*args, flush=True)


# ---------- Prospection ----------

def metiers_actifs(config):
    choix = config["zone"].get("metiers", "tous")
    return list(METIERS) if choix == "tous" else [m for m in choix if m in METIERS]


def collecter(config, aujourdhui):
    if config.get("pays", "FR") == "CH":
        return collecter_suisse(config, aujourdhui)
    trouves = []
    metiers = metiers_actifs(config)
    tag_vers_metier = {tag: m for m in metiers for tag in METIERS[m]["osm"]}
    cle = os.environ.get("INSEE_API_KEY", "").strip()
    depuis = (aujourdhui - timedelta(days=config.get("age_max_jours", 90))).isoformat()
    for dep in config["zone"].get("departements", []) if cle else []:
        for m in metiers:
            for naf in METIERS[m]["naf"]:
                try:
                    trouves += sources.parse_insee(sources.insee(naf, dep, depuis, cle), m)
                except Exception as err:
                    log(f"  INSEE {m} {dep} : échec ({err})")
                time.sleep(2.1)
    if config["zone"].get("departements") and not cle:
        log("  Départements ignorés : ajoute le secret INSEE_API_KEY (gratuit) pour les activer")
    for cp in config["zone"].get("codes_postaux", []):
        for m in metiers:
            try:
                bruts = sources.sirene(",".join(METIERS[m]["naf"]), cp, config.get("pages_sirene", 4))
                trouves += sources.parse_sirene(bruts, m, cp)
            except Exception as err:
                log(f"  SIRENE {m} {cp} : échec ({err})")
        try:
            liste_communes = sources.communes(cp)
        except Exception as err:
            log(f"  Communes {cp} : échec ({err})")
            liste_communes = []
        for c in liste_communes:
            try:
                trouves += sources.parse_osm(sources.osm(c["code"], list(tag_vers_metier)), tag_vers_metier, c["nom"])
            except Exception as err:
                log(f"  OpenStreetMap {c['nom']} : échec ({err})")
    log(f"  {len(trouves)} fiches récupérées")
    return trouves


def collecter_suisse(config, aujourdhui):
    trouves = []
    zone = config["zone"]
    langues = set(zone.get("langues", ["fr"]))
    depuis = (aujourdhui - timedelta(days=config.get("age_max_jours", 45))).isoformat()
    vus = set(lire_json(DONNEES / "fosc_vus.json", []))
    budget = config.get("fosc_max_details", 1500)
    for canton in zone["cantons"]:
        try:
            metas = sources.fosc_liste(canton, depuis, aujourdhui.isoformat())
        except Exception as err:
            log(f"  FOSC {canton} : échec ({err})")
            continue
        nouvelles = [m for m in metas if m.get("subRubric") == "HR01" and m.get("language") in langues and m["id"] not in vus]
        log(f"  FOSC {canton} : {len(metas)} publications, {len(nouvelles)} nouvelles inscriptions à lire")
        for meta in nouvelles:
            if budget <= 0:
                break
            budget -= 1
            try:
                p = sources.parse_fosc(sources.fosc_detail(meta["id"]), classer)
            except Exception as err:
                log(f"  FOSC détail {meta['id']} : échec ({err})")
                continue
            vus.add(meta["id"])
            if p:
                trouves.append(p)
            time.sleep(0.25)
    ecrire_json(DONNEES / "fosc_vus.json", sorted(vus))

    tags = sorted({tag for m in metiers_actifs(config) for tag in METIERS[m]["osm"]})
    tag_vers_metier = {tag: m for m in metiers_actifs(config) for tag in METIERS[m]["osm"]}
    for canton in zone["cantons"]:
        try:
            trouves += sources.parse_osm(sources.osm_canton(canton, tags), tag_vers_metier, "")
        except Exception as err:
            log(f"  OpenStreetMap {canton} : échec ({err})")
    log(f"  {len(trouves)} fiches récupérées")
    return trouves


REGISTRES = {"sirene", "fosc"}


def meme_entreprise(a, b):
    na, nb = sources.normaliser(a["nom"]), sources.normaliser(b["nom"])
    if len(na) < 4 or len(nb) < 4 or a["metier"] != b["metier"]:
        return False
    if sources.normaliser(a["ville"]) != sources.normaliser(b["ville"]):
        return False
    return na in nb or nb in na


def fusionner(existants, nouveaux, aujourdhui):
    parid = {p["id"]: p for p in existants}
    for n in sorted(nouveaux, key=lambda p: not REGISTRES & set(p["sources"])):
        cible = parid.get(n["id"])
        if cible is None and "osm" in n["sources"]:
            cible = next((p for p in parid.values() if REGISTRES & set(p["sources"]) and meme_entreprise(p, n)), None)
        if cible is None:
            if REGISTRES & set(n["sources"]):
                parid[n["id"]] = {**n, "premiere_detection": aujourdhui}
            continue
        for champ in ("telephone", "email", "site_web", "adresse", "date_creation", "siret"):
            if n.get(champ) and not cible.get(champ):
                cible[champ] = n[champ]
        cible["sources"] = sorted(set(cible["sources"]) | set(n["sources"]))
    return list(parid.values())


def jours_depuis(iso, aujourdhui):
    try:
        return (aujourdhui - date.fromisoformat(iso[:10])).days
    except ValueError:
        return None


def noter(p, aujourdhui):
    score, raisons = 0, []
    if not p.get("site_web"):
        score += 3
        raisons.append("Pas de site")
    if p.get("telephone"):
        score += 2
        raisons.append("Téléphone connu")
    if p.get("email"):
        score += 1
        raisons.append("Email connu")
    jours = jours_depuis(p.get("date_creation") or "", aujourdhui)
    if jours is not None and jours <= 365:
        score += 6 if jours <= 30 else 4 if jours <= 90 else 2
        raisons.append(f"Créée il y a {max(jours, 0)} jours" if jours <= 90 else f"Créée il y a {jours // 30} mois")
    p["score"], p["raisons"] = score, raisons
    return p


def eligible_kit(p, aujourdhui, age_max):
    jours = jours_depuis(p.get("date_creation") or "", aujourdhui)
    return not p.get("site_web") and jours is not None and 0 <= jours <= age_max


def slug(p, secret=""):
    base = re.sub(r"[^a-z0-9]+", "-", sources.normaliser(p["nom"]).lower()).strip("-")[:40] or "entreprise"
    return f"{base}-{hmac.new(secret.encode(), p['id'].encode(), 'sha256').hexdigest()[:12]}"


# ---------- Construction du site ----------

def accroche(p, m):
    if p["metier"] == "generique" and p.get("activite"):
        phrase = re.split(r"(?<=[.;])\s", p["activite"].strip())[0].rstrip(".;")
        return phrase[:1].upper() + phrase[1:220] + "."
    return m["accroche"]


def config_maquette(p, config):
    m = METIERS[p["metier"]]
    ville = p.get("ville") or "votre ville"
    generique = p["metier"] == "generique"
    return {
        "slug": p["slug"],
        "maquette": True,
        "realise_par": config["moi"]["agence"],
        "nom": p["nom"],
        "metier": m["libelle"],
        "type_schema": m["schema"],
        "ville": ville,
        "rayon": "20 km",
        "titre": f"{p['nom']}, à {ville}" if generique else f"{m['libelle']} à {ville}",
        "accroche": accroche(p, m),
        "indicatif": INDICATIFS[config.get("pays", "FR")],
        "apropos": f"{p['nom']}, {m['libelle'].lower()} à {ville}. Ici, votre histoire : vos années d'expérience, "
                   "votre façon de travailler, ce qui vous distingue. C'est ce qui donne confiance à vos futurs clients.",
        "telephone": p.get("telephone") or "Votre numéro",
        "email": p.get("email") or "votre-email@exemple.fr",
        "adresse": p.get("adresse") or ville,
        "couleur": m["couleur"],
        "badges": m["badges"],
        "services": [{"titre": t, "texte": x} for t, x in m["services"]],
        "horaires": m["horaires"],
        "raison_sociale": p["nom"],
        "siret": p.get("siret") or "à compléter",
    }


def construire_site(config, prospects, sortie, aujourdhui, clients=(), mot_de_passe="", exiger_chiffrement=False):
    if sortie.exists():
        shutil.rmtree(sortie)
    (sortie / "outils").mkdir(parents=True)
    for f in ("kit-avis.html", "qrcode.js"):
        shutil.copy(RACINE / "outils" / f, sortie / "outils" / f)

    agence = (RACINE / "agence" / "index.html").read_text(encoding="utf-8")
    moi = {k: config["moi"].get(k, "") for k in ("nom", "telephone", "email", "ville", "siret")}
    moi.update({k: config["offre"][k] for k in ("prix_kit", "prix_mois")}, devise=config["offre"].get("devise", "€"))
    moi_js = json.dumps(moi, ensure_ascii=False).replace("</", "<\\/")
    agence = re.sub(r"const MOI = \{.*?\};", lambda _: f"const MOI = {moi_js};", agence, count=1, flags=re.S)
    (sortie / "index.html").write_text(agence, encoding="utf-8")

    age_max = config.get("age_max_jours", 90)
    candidats = [p for p in prospects if eligible_kit(p, aujourdhui, age_max)]
    candidats.sort(key=lambda p: (-p["score"], p["nom"]))
    candidats = candidats[: config.get("kits_max", 300)]
    for p in candidats:
        site = sortie / "m" / p["slug"]
        site.mkdir(parents=True)
        (site / "index.html").write_text(generer_site.rendre(config_maquette(p, config), p["id"]), encoding="utf-8")
        page = sortie / "k" / p["slug"]
        page.mkdir(parents=True)
        (page / "index.html").write_text(kit.page_kit(p, config, f"../../m/{p['slug']}/"), encoding="utf-8")
        p["kit"] = f"k/{p['slug']}/"

    champs = ("id", "nom", "metier", "activite", "ville", "adresse", "telephone", "email", "site_web",
              "date_creation", "premiere_detection", "score", "raisons", "kit")
    donnees = {
        "genere_le": aujourdhui.isoformat(),
        "moi": config["moi"],
        "messages": config["messages"],
        "metiers": {k: v["libelle"] for k, v in METIERS.items()},
        "pays": config.get("pays", "FR"),
        "indicatif": INDICATIFS[config.get("pays", "FR")],
        "prospects": [{c: p.get(c, "") for c in champs} for p in candidats],
        "clients": publications_clients(clients, aujourdhui),
    }
    if mot_de_passe:
        charge = {"chiffre": chiffrer(json.dumps(donnees, ensure_ascii=False), mot_de_passe)}
    elif exiger_chiffrement:
        charge = {"manquant": True}
        log("  Cockpit vide : ajoute le secret COCKPIT_MOT_DE_PASSE pour le remplir")
    else:
        charge = donnees
    cockpit = (ICI / "cockpit.html").read_text(encoding="utf-8").replace(
        "__DONNEES__", json.dumps(charge, ensure_ascii=False).replace("</", "<\\/"))
    (sortie / "cockpit").mkdir()
    (sortie / "cockpit" / "index.html").write_text(cockpit, encoding="utf-8")
    (sortie / ".nojekyll").write_text("")
    return len(candidats)


def chiffrer(texte, mot_de_passe):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    sel, iv = os.urandom(16), os.urandom(12)
    cle = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode(), sel, ITERATIONS, 32)
    donnees = AESGCM(cle).encrypt(iv, texte.encode("utf-8"), None)
    b64 = lambda b: base64.b64encode(b).decode()  # noqa: E731
    return {"sel": b64(sel), "iv": b64(iv), "iterations": ITERATIONS, "donnees": b64(donnees)}


# ---------- Publications mensuelles des clients ----------

def publications(client, aujourdhui):
    m = METIERS[client["metier"]]
    saison = SAISONS[aujourdhui.month]
    service, texte = m["services"][aujourdhui.month % len(m["services"])]
    ville = client["ville"]
    contact = f" Contactez-nous au {client['telephone']}." if client.get("telephone") else ""
    return [
        ("Conseil de saison", f"{m['conseils'][saison]}{contact}", "Photo de vous en intervention ou de votre équipe."),
        (f"Service à la une : {service}", f"{texte} Nous intervenons à {ville} et dans les environs. Devis gratuit.{contact}",
         f"Photo d'une réalisation « {service.lower()} »."),
        ("Réalisation du mois", f"[À compléter avec le client : ce qui a été fait, où, en combien de temps.] "
         f"Encore merci à notre client de {ville} pour sa confiance !", "Photos avant / après (demander au client)."),
        ("Merci pour vos avis", f"Merci à tous nos clients qui prennent le temps de laisser un avis : c'est grâce à vous que "
         f"d'autres habitants de {ville} nous découvrent. Votre avis compte !", "Capture d'un avis récent ou photo de l'affiche QR code."),
    ]


def publications_clients(clients, aujourdhui):
    resultat = []
    for c in clients:
        if c.get("metier") not in METIERS:
            log(f"  Client {c.get('nom')} : métier inconnu ({c.get('metier')}), ignoré")
            continue
        resultat.append({"nom": c["nom"], "posts": [{"titre": t, "texte": x, "visuel": v}
                                                     for t, x, v in publications(c, aujourdhui)]})
    return resultat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hors-ligne", action="store_true")
    parser.add_argument("--sortie", default=str(RACINE.parent / "_site"))
    parser.add_argument("--date", help="date du jour AAAA-MM-JJ (tests)")
    parser.add_argument("--exiger-chiffrement", action="store_true",
                        help="ne jamais publier le cockpit en clair (utilisé par GitHub Actions)")
    args = parser.parse_args()

    aujourdhui = date.fromisoformat(args.date) if args.date else date.today()
    config = json.loads((ICI / "config.json").read_text(encoding="utf-8"))
    exclus = {str(x).replace(" ", "") for x in config.get("exclus", [])}
    prospects = lire_json(DONNEES / "prospects.json", [])
    avant = len(prospects)

    if not args.hors_ligne:
        log("Recherche de prospects…")
        prospects = fusionner(prospects, collecter(config, aujourdhui), aujourdhui.isoformat())
    prospects = [p for p in prospects if p["id"].split("-", 1)[1] not in exclus]
    secret = os.environ.get("COCKPIT_MOT_DE_PASSE", "")
    for p in prospects:
        p.pop("kit", None)
        noter(p, aujourdhui)
        p.setdefault("slug", slug(p, secret))
    ecrire_json(DONNEES / "prospects.json", sorted(prospects, key=lambda p: p["id"]))
    log(f"Prospects : {len(prospects)} (dont {len(prospects) - avant} nouveaux)")

    n = construire_site(config, prospects, Path(args.sortie), aujourdhui, lire_json(ICI / "clients.json", []),
                        secret, args.exiger_chiffrement)
    log(f"Kits de lancement générés : {n}")


if __name__ == "__main__":
    main()
