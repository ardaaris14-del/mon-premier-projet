# Jour Un

**Le lendemain de la naissance d'une entreprise, son site, son logo, sa carte de visite et sa fiche Google sont déjà prêts, à son nom.**

Une machine gratuite lit chaque jour le registre officiel des entreprises. Pour chaque nouvel artisan, coiffeur,
garage…, elle fabrique automatiquement un **kit de lancement complet** et le met en ligne sur un lien privé.
Ton travail : envoyer ce lien. Le créateur voit **son** site, **son** logo, **sa** carte de visite. S'il dit oui, il paie 149 €.

> **Honnêtement :** personne ne peut te garantir 10 000 €. Ce qui est garanti, c'est que la machine te fournit chaque
> jour des entreprises à contacter, avec leur kit déjà prêt. Le résultat dépend du nombre de kits que tu envoies et
> de la façon dont tu relances. Une idée nouvelle, ça veut aussi dire que personne n'a encore prouvé qu'elle marche :
> les chiffres ci-dessous sont des hypothèses, à vérifier dès les premières semaines.

---

## Pourquoi c'est différent

| Une agence classique | Jour Un |
|---|---|
| Cherche des clients, puis fait le travail | **Fait le travail d'abord**, puis le montre |
| Vend une promesse (« je vais vous faire un site ») | Montre le résultat (« voici **votre** site ») |
| Contacte des entreprises qui ont déjà un prestataire | Arrive **au moment précis** où l'entreprise n'a encore rien |
| Chaque maquette coûte des heures | Chaque kit coûte **0 € et 0 minute** : la machine le fabrique |

## Ce que fait la machine, chaque matin à 7 h (toute seule)

1. **Trouve les entreprises nées ces derniers jours** dans ta zone et tes métiers : API Sirene de l'INSEE (gratuite),
   API Recherche d'entreprises de l'État, et OpenStreetMap pour les téléphones.
2. **Fabrique leur kit** : site internet adapté aux téléphones, 3 logos, carte de visite, description de fiche Google, 4 premières publications.
3. **Met tout en ligne** gratuitement sur GitHub Pages. Les liens sont impossibles à deviner et invisibles sur Google.
4. **Met à jour ton cockpit** (protégé par mot de passe) : pour chaque entreprise, des boutons *Voir son kit*, *Google*,
   *Appeler*, *SMS*, *WhatsApp*. Le message contient déjà le lien de son kit.
5. **Rédige les 4 publications du mois** de chacun de tes clients abonnés (onglet *Mes clients* du cockpit).

## Mise en route (15 minutes, 0 €)

1. **Fusionner** la pull request sur GitHub (bouton *Merge*).
2. **Activer le site** : sur GitHub, *Settings → Pages → Source : **GitHub Actions***.
3. **Créer ton mot de passe** : *Settings → Secrets and variables → Actions → New repository secret*.
   Nom : `COCKPIT_MOT_DE_PASSE`, valeur : un mot de passe long que toi seul connais.
4. **Clé INSEE (fortement recommandé, gratuit)** : crée un compte sur **portail-api.insee.fr**, crée une application,
   abonne-la à l'**API Sirene** (plan public), copie la clé, puis ajoute le secret `INSEE_API_KEY`.
   Sans cette clé, la machine utilise seulement les codes postaux listés dans la configuration, et trouve moins de nouvelles entreprises.
5. **Remplir `automatisation/config.json`** : ton nom, ton téléphone, ton email, ton SIRET, tes départements
   (`"69"`), tes codes postaux, tes métiers et ton lien de paiement Stripe (voir plus bas).
6. **Lancer la machine** : onglet *Actions → Machine Jour Un → Run workflow*. Environ 5 minutes plus tard :
   - ta page publique : `https://ardaaris14-del.github.io/mon-premier-projet/`
   - ton cockpit : `https://ardaaris14-del.github.io/mon-premier-projet/cockpit/`

Ensuite, la machine tourne toute seule chaque matin.

**Métiers disponibles :** `plombier`, `electricien`, `peintre`, `menuisier`, `couvreur`, `coiffeur`, `estheticienne`, `garage`.

## Ta journée (environ 1 h 30)

1. Ouvre le cockpit sur ton téléphone et filtre sur **« Arrivés cette semaine »**.
2. Pour chaque entreprise : bouton **Google** pour trouver son téléphone, son Instagram ou son email (1 minute).
3. Envoie le kit : **SMS** ou **WhatsApp** en un clic, sinon appel. Le statut passe tout seul à « Kit envoyé ».
4. **Relance à J+3** (« Vous avez pu regarder votre kit ? »), puis une dernière fois à J+10. Jamais plus.
5. S'il dit oui : envoie ton lien de paiement, puis suis `documents/livraison.md`.

Objectif : **15 kits envoyés par jour**. Pas de contact trouvable ? S'il a une boutique, passe le voir, téléphone en main avec son kit ouvert.

## L'offre

| | Prix | Contenu |
|---|---|---|
| **Kit de lancement** | **149 €** une fois | Site en ligne sur son nom de domaine (1 an inclus), logo en haute définition, carte de visite prête à imprimer, fiche Google créée avec lui + 4 publications |
| **Suivi** (option) | **29 €/mois** sans engagement | Hébergement, modifications, 4 publications par mois (rédigées par la machine), réponse aux avis |

**Paiement sans frais fixes :** crée un compte Stripe (gratuit, commission seulement sur les ventes), puis un
*Payment Link* à 149 € et un autre à 29 €/mois. Colle le premier dans `offre.lien_paiement` : il apparaît sur chaque kit.

**Ton coût par vente :** environ 10 € de nom de domaine, payés avec les 149 € du client.

## Les chiffres (hypothèses à vérifier)

- Un département comme le Rhône voit naître **plusieurs centaines d'entreprises par mois** dans les métiers ciblés.
- Sur 10 kits, tu trouveras un contact pour **4 à 6**.
- Hypothèse : entre **3 et 9 %** des kits envoyés sont achetés, car le créateur voit le résultat avant de payer. Le taux monte à mesure que tu améliores ton message.

**Scénario ambitieux** (taux qui passe de 5 à 9 %) :

| | Mois 1 | Mois 2 | Mois 3 | Total |
|---|---|---|---|---|
| Kits envoyés (15/jour ouvré) | 300 | 330 | 330 | 960 |
| Kits vendus | 15 | 25 | 30 | **70** |
| Kits × 149 € | 2 235 € | 3 725 € | 4 470 € | **10 430 €** |
| Abonnés à 29 €/mois (1 kit sur 3) | 5 | 13 | 23 | ~1 200 € |

**Scénario prudent** (3 %) : environ 29 kits vendus, soit **~4 300 €** sur 3 mois.

Pour **10 000 €/mois** ensuite : environ **40 kits par mois** (5 960 €) + **140 abonnés** (4 060 €). Le levier qui rend
ça atteignable, ce sont les **partenaires** (ci-dessous) : ils t'envoient les créateurs sans que tu aies à les chercher.

**Ton premier indicateur :** après 100 kits envoyés, compte les ventes. En dessous de 2, change le message, le prix ou les métiers visés avant de continuer.

## Les partenaires : ton accélérateur

Les experts-comptables, les banques, les sociétés de domiciliation et les réseaux d'aide à la création voient passer
des créateurs tous les jours. Propose-leur d'**offrir le kit** à leurs nouveaux clients : c'est un cadeau de bienvenue
qui ne leur coûte rien, et tu leur reverses **30 € par kit activé**. Script dans `documents/prospection.md`.

## Les règles (non négociables)

- **« Stop » = supprimé.** Ajoute son numéro SIREN dans `"exclus"` de `config.json` : il n'est plus jamais contacté et son kit disparaît au passage suivant de la machine.
- Les données viennent de registres publics (SIRENE, OpenStreetMap). L'INSEE retire déjà les entrepreneurs qui ont refusé la diffusion. Tu ne contactes que des professionnels, pour une offre liée à leur activité, et chaque message propose de dire « stop ».
- Chaque kit indique clairement qu'il s'agit d'un **aperçu non officiel**. Il n'est pas référencé sur Google et son lien est impossible à deviner.
- Le cockpit est chiffré : sans ton mot de passe, personne ne peut lire la liste. Ne partage jamais ce mot de passe.
- Jamais de faux avis, jamais de promesse de première place sur Google.

## Démarches (gratuit)

- Micro-entreprise sur **formalites.entreprises.gouv.fr** (activité : création de sites internet / communication). Il faut être majeur ou mineur émancipé.
- Mets de côté **environ 25 %** de chaque vente pour les cotisations (déclaration sur autoentrepreneur.urssaf.fr).
- Sur les factures : « TVA non applicable, art. 293 B du CGI » tant que tu restes sous le seuil de franchise. Vérifie les seuils à jour sur urssaf.fr et impots.gouv.fr.

## Contenu du dossier

| Chemin | Rôle |
|---|---|
| `automatisation/machine.py` | La machine : prospection, kits, cockpit, publications des clients |
| `automatisation/config.json` | **Tes réglages** : coordonnées, zone, métiers, prix, messages, exclusions |
| `automatisation/clients.json` | Tes clients abonnés, pour leurs publications du mois (ex. : `[{"nom": "Plomberie Durand", "metier": "plombier", "ville": "Villeurbanne", "telephone": "06…"}]`) |
| `automatisation/metiers.py` | Contenu par métier (textes, services, couleurs, conseils de saison). Pour ajouter un métier, copie un bloc. |
| `automatisation/sources.py` | Les API gratuites (INSEE, Recherche d'entreprises, OpenStreetMap) |
| `automatisation/kit.py`, `kit.html` | Le kit de lancement (logos, carte de visite, fiche Google, publications) |
| `automatisation/cockpit.html` | Ton cockpit |
| `generateur/` | Le générateur de site (utilisé par la machine, ou à la main pour le site final d'un client) |
| `agence/index.html` | Ta page publique Jour Un |
| `outils/kit-avis.html` | Affiche QR code pour que tes clients récoltent des avis Google |
| `documents/` | Messages et scripts, livraison d'un kit, contrat |
| `../.github/workflows/` | L'automatisation : `machine.yml` (tous les jours) et `tests.yml` |

Lancer la machine sur ton ordinateur (facultatif) :
```bash
pip install -r jour-un/requirements.txt
python3 jour-un/automatisation/machine.py            # le site est créé dans _site/
python3 -m unittest discover -s jour-un/automatisation/tests
```
