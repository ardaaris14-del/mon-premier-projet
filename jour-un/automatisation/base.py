"""Accès minimal à la base Supabase (API REST PostgREST), sans dépendance externe."""
import json
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class Base:
    def __init__(self, url, cle):
        self.url = url.rstrip("/") + "/rest/v1/"
        self.entetes = {"apikey": cle, "Content-Type": "application/json"}
        if not cle.startswith("sb_"):
            self.entetes["Authorization"] = f"Bearer {cle}"

    def _requete(self, methode, table, params=None, corps=None, prefer=None):
        url = self.url + table + ("?" + urlencode(params, safe=",.()*\"") if params else "")
        entetes = {**self.entetes, **({"Prefer": prefer} if prefer else {})}
        donnees = json.dumps(corps, ensure_ascii=False).encode("utf-8") if corps is not None else None
        with urlopen(Request(url, data=donnees, headers=entetes, method=methode), timeout=60) as r:
            texte = r.read().decode("utf-8")
        return json.loads(texte) if texte else None

    def lire(self, table, **params):
        return self._requete("GET", table, {"select": "*", **params})

    def inserer(self, table, ligne):
        return self._requete("POST", table, corps=ligne, prefer="return=representation")[0]

    def upsert(self, table, lignes, conflit):
        for i in range(0, len(lignes), 200):
            self._requete("POST", table, {"on_conflict": conflit}, lignes[i:i + 200],
                          prefer="resolution=merge-duplicates,return=minimal")

    def modifier(self, table, valeurs, **filtres):
        self._requete("PATCH", table, filtres, valeurs, prefer="return=minimal")

    def supprimer_ids(self, table, ids, colonne="id"):
        ids = list(ids)
        for i in range(0, len(ids), 100):
            liste = ",".join('"' + quote(x, safe="-_.") + '"' for x in ids[i:i + 100])
            self._requete("DELETE", table, {colonne: f"in.({liste})"}, prefer="return=minimal")
