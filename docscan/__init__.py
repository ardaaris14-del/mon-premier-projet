"""docscan — extraction de champs depuis des documents scannés, avec Claude.

Usage rapide :

    from docscan import charger_modele, extraire

    modele = charger_modele("facture")
    resultat = extraire("facture.pdf", modele)
    print(resultat.champs)
"""

from docscan.modeles import Champ, Modele, charger_modele, lister_modeles
from docscan.extraction import Resultat, extraire

__all__ = [
    "Champ",
    "Modele",
    "Resultat",
    "charger_modele",
    "lister_modeles",
    "extraire",
]

__version__ = "0.1.0"
