"""Appel à Claude : lecture du document et remplissage des champs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

from docscan import config
from docscan.documents import bloc_document
from docscan.modeles import Modele
from docscan.schema import construire_schema

INSTRUCTIONS_SYSTEME = """\
Tu es un moteur d'extraction documentaire. On te fournit un document scanné \
(photo, PDF ou texte) et une liste de champs à remplir.

Règles impératives :
1. Ne recopie que ce qui figure réellement dans le document. N'invente jamais \
une valeur, ne complète jamais par des connaissances extérieures.
2. Si une information est absente, illisible ou incertaine au point d'être \
inutilisable, mets null — et non une valeur approchée.
3. Recopie les identifiants (numéros, IBAN, SIRET, références) caractère par \
caractère, sans reformatage ni correction.
4. Normalise les dates au format AAAA-MM-JJ. Si l'année est ambiguë (format \
JJ/MM/AA), déduis-la du contexte du document ; en cas de doute, mets null.
5. Les montants sont des nombres décimaux : ni symbole monétaire, ni espace, \
ni séparateur de milliers. Le séparateur décimal est le point.
6. Pour chaque champ, indique dans « confiance » une note entre 0 et 1 : 1 si \
la valeur est lue explicitement, ~0.5 si elle est déduite ou partiellement \
lisible, 0 si le champ est resté null.
7. Signale dans « remarques » ce que l'utilisateur doit vérifier (page \
illisible, document tronqué, total incohérent). null si tout va bien.
"""


class ErreurExtraction(RuntimeError):
    """L'extraction a échoué."""


@dataclass
class Resultat:
    """Résultat d'une extraction sur un document."""

    document: str
    modele: str
    champs: dict[str, Any]
    confiance: dict[str, float] = field(default_factory=dict)
    type_document: str | None = None
    remarques: str | None = None
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def champs_manquants(self) -> list[str]:
        """Champs restés vides."""
        return [nom for nom, valeur in self.champs.items() if valeur in (None, "", [])]

    def champs_a_verifier(self, seuil: float = 0.8) -> list[str]:
        """Champs remplis mais dont la confiance est basse."""
        return [
            nom
            for nom, valeur in self.champs.items()
            if valeur not in (None, "", []) and self.confiance.get(nom, 1.0) < seuil
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": self.document,
            "modele": self.modele,
            "type_document": self.type_document,
            "champs": self.champs,
            "confiance": self.confiance,
            "remarques": self.remarques,
            "champs_manquants": self.champs_manquants,
            "usage": self.usage,
        }


def _consigne_utilisateur(modele: Modele) -> str:
    lignes = [
        f"Type de document attendu : {modele.description or modele.nom}.",
        "",
        "Champs à remplir :",
    ]
    for champ in modele.champs:
        details = [f"- {champ.nom} ({champ.type}) : {champ.libelle}"]
        if champ.description:
            details.append(f"— {champ.description}")
        if champ.choix:
            details.append(f"— valeurs possibles : {', '.join(champ.choix)}")
        if champ.type == "tableau":
            colonnes = ", ".join(f"{c.nom} ({c.type})" for c in champ.colonnes)
            details.append(f"— une ligne par entrée, colonnes : {colonnes}")
        if champ.obligatoire:
            details.append("— champ important")
        lignes.append(" ".join(details))

    if modele.instructions:
        lignes += ["", "Consignes spécifiques à ce type de document :", modele.instructions]

    lignes += ["", "Lis le document ci-dessus et renvoie les valeurs trouvées."]
    return "\n".join(lignes)


def _client(api_key: str | None = None) -> anthropic.Anthropic:
    try:
        return anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    except anthropic.AnthropicError as err:
        raise ErreurExtraction(
            "Impossible d'initialiser le client Anthropic. Définissez la variable "
            f"d'environnement ANTHROPIC_API_KEY. Détail : {err}"
        ) from err


def extraire(
    document: str | Path,
    modele: Modele,
    *,
    client: anthropic.Anthropic | None = None,
    modele_ia: str = config.MODELE_IA,
    effort: str = config.EFFORT,
    api_key: str | None = None,
) -> Resultat:
    """Lit `document` et renvoie les champs de `modele` remplis par Claude."""
    contenu = [bloc_document(document), {"type": "text", "text": _consigne_utilisateur(modele)}]
    client = client or _client(api_key)

    try:
        reponse = client.messages.create(
            model=modele_ia,
            max_tokens=config.MAX_TOKENS,
            system=INSTRUCTIONS_SYSTEME,
            messages=[{"role": "user", "content": contenu}],
            output_config={
                "effort": effort,
                "format": {"type": "json_schema", "schema": construire_schema(modele)},
            },
        )
    except anthropic.AuthenticationError as err:
        raise ErreurExtraction(
            "Clé API refusée. Vérifiez ANTHROPIC_API_KEY."
        ) from err
    except anthropic.RateLimitError as err:
        delai = err.response.headers.get("retry-after", "60")
        raise ErreurExtraction(
            f"Limite de débit atteinte. Réessayez dans {delai} s."
        ) from err
    except anthropic.BadRequestError as err:
        raise ErreurExtraction(f"Requête refusée par l'API : {err.message}") from err
    except anthropic.APIStatusError as err:
        raise ErreurExtraction(
            f"Erreur API ({err.status_code}) : {err.message}"
        ) from err
    except anthropic.APIConnectionError as err:
        raise ErreurExtraction("Connexion à l'API impossible. Vérifiez le réseau.") from err

    if reponse.stop_reason == "refusal":
        detail = getattr(reponse.stop_details, "explanation", "") or ""
        raise ErreurExtraction(f"Le modèle a refusé de traiter ce document. {detail}".strip())
    if reponse.stop_reason == "max_tokens":
        raise ErreurExtraction(
            "Réponse tronquée (max_tokens atteint). Réduisez le nombre de champs "
            "ou augmentez DOCSCAN_MAX_TOKENS."
        )

    texte = next((b.text for b in reponse.content if b.type == "text"), "")
    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError as err:
        raise ErreurExtraction(f"Réponse illisible du modèle : {err}") from err

    return Resultat(
        document=str(document),
        modele=modele.nom,
        champs=donnees.get("champs", {}),
        confiance=donnees.get("confiance", {}) or {},
        type_document=donnees.get("type_document"),
        remarques=donnees.get("remarques"),
        usage={
            "input_tokens": reponse.usage.input_tokens,
            "output_tokens": reponse.usage.output_tokens,
        },
    )


def extraire_lot(
    documents: list[str | Path],
    modele: Modele,
    *,
    client: anthropic.Anthropic | None = None,
    **kwargs: Any,
) -> list[tuple[Path, Resultat | Exception]]:
    """Traite plusieurs documents ; une erreur sur l'un n'interrompt pas le lot."""
    client = client or _client(kwargs.pop("api_key", None))
    resultats: list[tuple[Path, Resultat | Exception]] = []
    for doc in documents:
        try:
            resultats.append((Path(doc), extraire(doc, modele, client=client, **kwargs)))
        except (ErreurExtraction, ValueError) as err:
            resultats.append((Path(doc), err))
    return resultats
