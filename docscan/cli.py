"""Interface en ligne de commande.

    python -m docscan modeles
    python -m docscan scan facture.pdf --modele facture
    python -m docscan lot ./scans --modele facture --csv resultats.csv
    python -m docscan web
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docscan import config
from docscan.documents import ErreurDocument, fichiers_du_dossier
from docscan.export import vers_csv, vers_json
from docscan.extraction import ErreurExtraction, Resultat, extraire, extraire_lot
from docscan.modeles import ErreurModele, charger_modele, lister_modeles

VERT, JAUNE, ROUGE, GRIS, RAZ = "\033[32m", "\033[33m", "\033[31m", "\033[90m", "\033[0m"


def _couleurs_actives() -> bool:
    return sys.stdout.isatty()


def _c(texte: str, couleur: str) -> str:
    return f"{couleur}{texte}{RAZ}" if _couleurs_actives() else texte


def _afficher_resultat(resultat: Resultat, seuil: float) -> None:
    largeur = max((len(n) for n in resultat.champs), default=10)
    print(f"\n{_c(resultat.document, VERT)}")
    if resultat.type_document:
        print(_c(f"  document reconnu : {resultat.type_document}", GRIS))
    for nom, valeur in resultat.champs.items():
        note = resultat.confiance.get(nom)
        if valeur in (None, "", []):
            affichage = _c("— non trouvé —", ROUGE)
        elif isinstance(valeur, list):
            affichage = f"{len(valeur)} entrée(s)"
        else:
            affichage = str(valeur)
        suffixe = ""
        if note is not None and valeur not in (None, "", []):
            couleur = VERT if note >= seuil else JAUNE
            suffixe = _c(f"  ({note:.0%})", couleur)
        print(f"  {nom.ljust(largeur)} : {affichage}{suffixe}")

    a_verifier = resultat.champs_a_verifier(seuil)
    if a_verifier:
        print(_c(f"  À vérifier : {', '.join(a_verifier)}", JAUNE))
    if resultat.remarques:
        print(_c(f"  Remarque : {resultat.remarques}", JAUNE))


def _ecrire(chemin: str | None, contenu: str) -> None:
    if chemin:
        Path(chemin).write_text(contenu, encoding="utf-8")
        print(f"\nÉcrit : {chemin}")
    else:
        print(contenu)


def _cmd_modeles(args: argparse.Namespace) -> int:
    trouves = lister_modeles()
    if not trouves:
        print("Aucun modèle trouvé.")
        return 1
    for nom, chemin in sorted(trouves.items()):
        modele = charger_modele(chemin)
        print(f"{_c(nom, VERT)} — {modele.description or 'sans description'}")
        print(_c(f"  {len(modele.champs)} champs : "
                 f"{', '.join(c.nom for c in modele.champs)}", GRIS))
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    modele = charger_modele(args.modele)
    resultat = extraire(
        args.document, modele, modele_ia=args.modele_ia, effort=args.effort
    )
    if args.json is not None:
        _ecrire(args.json or None, vers_json([resultat]))
    elif args.csv is not None:
        _ecrire(args.csv or None, vers_csv([resultat], modele, confiance=args.confiance))
    else:
        _afficher_resultat(resultat, args.seuil)
    return 0


def _cmd_lot(args: argparse.Namespace) -> int:
    modele = charger_modele(args.modele)
    fichiers = fichiers_du_dossier(args.dossier)
    if not fichiers:
        print(f"Aucun document lisible dans {args.dossier}.")
        return 1

    print(f"{len(fichiers)} document(s) à traiter…")
    paires = extraire_lot(
        list(fichiers), modele, modele_ia=args.modele_ia, effort=args.effort
    )

    reussis = [r for _, r in paires if isinstance(r, Resultat)]
    for chemin, issue in paires:
        if isinstance(issue, Resultat):
            _afficher_resultat(issue, args.seuil)
        else:
            print(_c(f"\n{chemin} : échec — {issue}", ROUGE))

    if args.csv is not None:
        _ecrire(args.csv or None, vers_csv(reussis, modele, confiance=args.confiance))
    if args.json is not None:
        _ecrire(args.json or None, vers_json(reussis))

    echecs = len(paires) - len(reussis)
    print(f"\n{len(reussis)} réussite(s), {echecs} échec(s).")
    return 1 if echecs else 0


def _cmd_web(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError:
        print(
            "L'interface web nécessite des dépendances supplémentaires :\n"
            "    pip install fastapi uvicorn python-multipart",
            file=sys.stderr,
        )
        return 1
    print(f"Interface web : http://{args.hote}:{args.port}")
    uvicorn.run("docscan.web:app", host=args.hote, port=args.port, log_level="warning")
    return 0


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docscan",
        description="Scanne des documents et remplit automatiquement vos champs.",
    )
    sous = parser.add_subparsers(dest="commande", required=True)

    commun = argparse.ArgumentParser(add_help=False)
    commun.add_argument("-m", "--modele", required=True,
                        help="nom d'un modèle intégré ou chemin d'un fichier JSON")
    commun.add_argument("--modele-ia", default=config.MODELE_IA,
                        help=f"modèle Claude à utiliser (défaut : {config.MODELE_IA})")
    commun.add_argument("--effort", default=config.EFFORT,
                        choices=["low", "medium", "high", "xhigh", "max"],
                        help=f"effort de raisonnement (défaut : {config.EFFORT})")
    commun.add_argument("--seuil", type=float, default=0.8,
                        help="seuil de confiance sous lequel un champ est à vérifier")
    commun.add_argument("--confiance", action="store_true",
                        help="ajoute les colonnes de confiance à l'export CSV")
    commun.add_argument("--json", nargs="?", const="", metavar="FICHIER",
                        help="sortie JSON (vers un fichier, ou l'écran si vide)")
    commun.add_argument("--csv", nargs="?", const="", metavar="FICHIER",
                        help="sortie CSV (vers un fichier, ou l'écran si vide)")

    p_modeles = sous.add_parser("modeles", help="liste les modèles de champs disponibles")
    p_modeles.set_defaults(func=_cmd_modeles)

    p_scan = sous.add_parser("scan", parents=[commun], help="analyse un document")
    p_scan.add_argument("document", help="image, PDF ou fichier texte")
    p_scan.set_defaults(func=_cmd_scan)

    p_lot = sous.add_parser("lot", parents=[commun], help="analyse tous les documents d'un dossier")
    p_lot.add_argument("dossier")
    p_lot.set_defaults(func=_cmd_lot)

    p_web = sous.add_parser("web", help="lance l'interface web")
    p_web.add_argument("--hote", default="127.0.0.1")
    p_web.add_argument("--port", type=int, default=8000)
    p_web.set_defaults(func=_cmd_web)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ErreurModele, ErreurDocument, ErreurExtraction) as err:
        print(_c(f"Erreur : {err}", ROUGE), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nInterrompu.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
