"""Génère le mini-site d'un client à partir d'un fichier JSON.

Usage :
    python3 generer_site.py clients/plomberie-dupont.json
    python3 generer_site.py clients/*.json
Le site est écrit dans ../sites/<slug>/index.html
"""
import json
import sys
from datetime import date
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import quote_plus

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent / "sites"

OBLIGATOIRES = ["slug", "nom", "metier", "ville", "telephone", "email", "adresse", "services"]


def e(valeur):
    return escape(str(valeur), quote=True)


def carte(titre, texte):
    return f'<div class="card"><h3>{e(titre)}</h3><p>{e(texte)}</p></div>'


def lien_tel(tel):
    chiffres = "".join(c for c in tel if c.isdigit() or c == "+")
    if chiffres.startswith("0") and len(chiffres) == 10:
        return "+33" + chiffres[1:]
    return chiffres


def rendre(data, origine="config"):
    manquants = [c for c in OBLIGATOIRES if not data.get(c)]
    if manquants:
        raise ValueError(f"{origine} : champs manquants -> {', '.join(manquants)}")

    tel = data["telephone"]
    tel_lien = lien_tel(tel)

    services = "".join(carte(s["titre"], s["texte"]) for s in data["services"])

    avis = data.get("avis", [])
    section_avis = ""
    if avis:
        cartes = "".join(
            f'<div class="card"><div class="etoiles">{"★" * int(a.get("note", 5))}</div>'
            f'<p>« {e(a["texte"])} »</p><div class="auteur">{e(a["auteur"])}</div></div>'
            for a in avis
        )
        section_avis = (
            '<section id="avis" class="avis"><div class="wrap"><h2>Ils nous font confiance</h2>'
            f'<p class="lead">Avis publiés sur Google.</p><div class="grid">{cartes}</div></div></section>'
        )

    badges = "".join(f"<span>✔ <b>{e(b)}</b></span>" for b in data.get("badges", []))
    horaires = "".join(f"<tr><td>{e(j)}</td><td>{e(h)}</td></tr>" for j, h in data.get("horaires", {}).items())

    whatsapp = data.get("whatsapp")
    bouton_whatsapp = (
        f'<a class="btn ghost" href="https://wa.me/{e(whatsapp)}">WhatsApp</a>' if whatsapp else ""
    )

    bandeau = ""
    if data.get("maquette"):
        bandeau = (
            f'<div class="maquette">Maquette de démonstration préparée pour {e(data["nom"])} '
            f'par {e(data.get("realise_par", "votre prestataire"))} — ce n\'est pas le site officiel de l\'entreprise</div>'
        )

    nom = data["nom"]
    mots = nom.split(" ", 1)
    nom_logo = f"{e(mots[0])} <span>{e(mots[1])}</span>" if len(mots) == 2 else e(nom)

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": data.get("type_schema", "LocalBusiness"),
        "name": nom,
        "telephone": tel,
        "email": data["email"],
        "address": data["adresse"],
        "areaServed": data["ville"],
    }, ensure_ascii=False).replace("</", "<\\/")

    valeurs = {
        "nom": e(nom),
        "nom_logo": nom_logo,
        "metier": e(data["metier"]),
        "ville": e(data["ville"]),
        "rayon": e(data.get("rayon", "20 km")),
        "titre": e(data.get("titre", f"{data['metier']} à {data['ville']}")),
        "accroche": e(data.get("accroche", "")),
        "apropos": e(data.get("apropos", "")),
        "telephone": e(tel),
        "telephone_lien": e(tel_lien),
        "email": e(data["email"]),
        "adresse": e(data["adresse"]),
        "carte_q": quote_plus(f"{nom} {data['adresse']}"),
        "couleur": e(data.get("couleur", "#1f6feb")),
        "services": services,
        "section_avis": section_avis,
        "badges": badges,
        "horaires": horaires,
        "bouton_whatsapp": bouton_whatsapp,
        "bandeau_maquette": bandeau,
        "jsonld": jsonld,
        "annee": date.today().year,
        "raison_sociale": e(data.get("raison_sociale", nom)),
        "siret": e(data.get("siret", "à compléter")),
        "responsable": e(data.get("responsable", "à compléter")),
        "hebergeur": e(data.get("hebergeur", "Netlify, Inc. — 512 2nd Street, San Francisco, CA 94107, USA")),
        "realise_par": e(data.get("realise_par", "")),
        "meta_robots": '<meta name="robots" content="noindex, nofollow">' if data.get("maquette") else "",
    }

    return Template((ICI / "template.html").read_text(encoding="utf-8")).substitute(valeurs)


def generer(chemin_json, sortie=SORTIE):
    data = json.loads(Path(chemin_json).read_text(encoding="utf-8"))
    try:
        html = rendre(data, chemin_json)
    except ValueError as err:
        raise SystemExit(str(err))
    dossier = Path(sortie) / data["slug"]
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "index.html").write_text(html, encoding="utf-8")
    print(f"OK -> {dossier / 'index.html'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for chemin in sys.argv[1:]:
        generer(chemin)
