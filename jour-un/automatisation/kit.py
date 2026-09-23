"""Kit Jour Un : logo, carte de visite, texte de fiche Google et premières publications, générés pour une entreprise."""
from html import escape
from string import Template
from pathlib import Path

from metiers import METIERS

ICI = Path(__file__).resolve().parent


def e(v):
    return escape(str(v), quote=True)


def initiales(nom):
    mots = [m for m in nom.replace("-", " ").split() if m[:1].isalnum() and m.lower() not in {"de", "du", "des", "la", "le", "les", "et", "l'", "d'"}]
    return ("".join(m[0] for m in mots[:2]) or nom[:1] or "?").upper()


def logos(nom, couleur):
    """Trois propositions de logo en SVG : pastille, carré, bandeau."""
    ini = e(initiales(nom))
    n = e(nom)
    f = max(11, min(22, 350 // max(len(nom), 1)))
    fb = max(12, min(26, 520 // max(len(nom), 1)))
    return [
        f'<svg viewBox="0 0 320 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{n}">'
        f'<circle cx="60" cy="60" r="44" fill="{couleur}"/><text x="60" y="75" text-anchor="middle" font-family="Georgia,serif" '
        f'font-size="40" font-weight="700" fill="#fff">{ini}</text><text x="118" y="70" font-family="Inter,Arial,sans-serif" '
        f'font-size="{f}" font-weight="700" fill="#14161a">{n}</text></svg>',
        f'<svg viewBox="0 0 320 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{n}">'
        f'<rect x="16" y="16" width="88" height="88" rx="18" fill="none" stroke="{couleur}" stroke-width="6"/>'
        f'<text x="60" y="74" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="36" font-weight="800" '
        f'fill="{couleur}">{ini}</text><text x="118" y="70" font-family="Inter,Arial,sans-serif" font-size="{f}" '
        f'font-weight="600" fill="#14161a">{n}</text></svg>',
        f'<svg viewBox="0 0 320 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{n}">'
        f'<rect width="320" height="120" rx="16" fill="{couleur}"/><text x="160" y="68" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="{fb}" font-weight="700" fill="#fff">{n}</text>'
        f'<rect x="130" y="82" width="60" height="3" fill="#fff" opacity=".7"/></svg>',
    ]


def description_google(p):
    m = METIERS[p["metier"]]
    services = ", ".join(s[0].lower() for s in m["services"])
    ville = p.get("ville") or "votre ville"
    texte = (f"{p['nom']} — {m['libelle'].lower()} à {ville}. "
             f"Nos prestations : {services}. {m['accroche']} "
             f"Nous intervenons à {ville} et dans les communes voisines. "
             f"Contactez-nous pour un devis gratuit et une réponse rapide.")
    return texte[:750]


def premieres_publications(p):
    m = METIERS[p["metier"]]
    ville = p.get("ville") or "votre ville"
    s1, s2 = m["services"][0], m["services"][1]
    return [
        ("Bienvenue !", f"{p['nom']} ouvre ses portes à {ville} ! {m['accroche']} Nous avons hâte de vous rencontrer."),
        (s1[0], f"{s1[1]} Devis gratuit à {ville} et dans les environs."),
        (s2[0], f"{s2[1]} Une question ? Écrivez-nous ou appelez-nous."),
        ("Votre avis compte", f"Vous avez fait appel à {p['nom']} ? Votre avis Google aide d'autres habitants de {ville} à nous découvrir. Merci !"),
    ]


def page_kit(p, config, lien_site):
    m = METIERS[p["metier"]]
    moi = config["moi"]
    offre = config["offre"]
    appel = f"tel:{''.join(c for c in moi['telephone'] if c.isdigit() or c == '+')}"
    devise = offre.get("devise", "€")
    lien_suivi, lien_kit = offre.get("lien_paiement"), offre.get("lien_paiement_kit")
    if lien_suivi and lien_kit:
        boutons = (f'<a class="btn" href="{e(lien_suivi)}">Kit + suivi : {e(offre["prix_kit"])} {e(devise)} '
                   f'+ {e(offre["prix_mois"])} {e(devise)}/mois</a>'
                   f'<a class="btn" href="{e(lien_kit)}">Kit seul : {e(offre["prix_kit"])} {e(devise)}</a>')
    else:
        boutons = f'<a class="btn" href="{e(lien_suivi or lien_kit or appel)}">Je prends mon kit</a>'
    tel = p.get("telephone") or "Votre numéro"
    email = p.get("email") or "votre-email@exemple.fr"
    svgs = logos(p["nom"], m["couleur"])
    valeurs = {
        "nom": e(p["nom"]),
        "metier": e(m["libelle"]),
        "ville": e(p.get("ville") or ""),
        "couleur": e(m["couleur"]),
        "lien_site": e(lien_site),
        "logos": "".join(f'<div class="logo">{s}</div>' for s in svgs),
        "logo_carte": svgs[0],
        "tel": e(tel),
        "email": e(email),
        "adresse": e(p.get("adresse") or p.get("ville") or ""),
        "description": e(description_google(p)),
        "categories": "".join(f"<li>{e(c)}</li>" for c in [m["libelle"]] + [s[0] for s in m["services"][:3]]),
        "posts": "".join(f'<div class="post"><b>{e(t)}</b><p>{e(x)}</p></div>' for t, x in premieres_publications(p)),
        "prix_kit": e(offre["prix_kit"]),
        "prix_mois": e(offre["prix_mois"]),
        "devise": e(devise),
        "boutons_paiement": boutons,
        "moi": e(moi["nom"]),
        "moi_tel": e(moi["telephone"]),
        "moi_email": e(moi["email"]),
        "agence": e(moi["agence"]),
    }
    return Template((ICI / "kit.html").read_text(encoding="utf-8")).substitute(valeurs)
