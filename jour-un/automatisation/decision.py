"""Décide si la machine doit tourner : lancement manuel, passage du matin, ou demande faite depuis le panel web."""
import os

from base import Base

QUOTIDIEN = "0 5 * * *"


def faut_il_lancer(evenement, cron, base):
    if evenement != "schedule" or cron == QUOTIDIEN:
        return True
    if base is None:
        return False
    return bool(base.lire("demandes", select="id", traitee_le="is.null", limit="1"))


if __name__ == "__main__":
    url, cle = os.environ.get("SUPABASE_URL", ""), os.environ.get("SUPABASE_SECRET", "")
    try:
        lancer = faut_il_lancer(os.environ.get("GITHUB_EVENT_NAME", ""), os.environ.get("EVENEMENT_CRON", ""),
                                Base(url, cle) if url and cle else None)
    except Exception as err:
        print(f"Base injoignable ({err}) : pas de lancement")
        lancer = False
    print(f"lancer={str(lancer).lower()}")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a", encoding="utf-8") as sortie:
        sortie.write(f"lancer={str(lancer).lower()}\n")
