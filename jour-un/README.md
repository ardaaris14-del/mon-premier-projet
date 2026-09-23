# web-design.ch

**Le lendemain de la naissance d'une entreprise, son site, son logo, sa carte de visite et sa fiche Google sont déjà prêts, à son nom.**

Une machine gratuite lit chaque jour la **Feuille officielle suisse du commerce (FOSC)**, où sont publiées toutes les
nouvelles inscriptions au registre du commerce. Pour chaque nouvelle entreprise de Suisse romande, elle fabrique
automatiquement un **kit de lancement complet** et le met en ligne sur un lien privé. Ton travail : appeler le créateur et lui
montrer son kit. S'il dit oui, il paie **CHF 290**.

> **Honnêtement :** personne ne peut te garantir 10 000 CHF. Ce qui est garanti, c'est que la machine te fournit chaque
> jour des entreprises à contacter, avec leur kit déjà prêt. Le résultat dépend du nombre de créateurs que tu appelles
> et de la façon dont tu leur présentes le kit. C'est une idée nouvelle : les chiffres ci-dessous sont des hypothèses,
> à vérifier dès les premières semaines.

---

## Pourquoi c'est différent

| Une agence web classique | web-design.ch |
|---|---|
| Cherche des clients, puis fait le travail | **Fait le travail d'abord**, puis le montre |
| Vend une promesse (« je vais vous faire un site ») | Montre le résultat (« voici **votre** site ») |
| Contacte des entreprises qui ont déjà un prestataire | Arrive **au moment précis** où l'entreprise n'a encore rien |
| Un site coûte CHF 2 000 à 5 000 | Kit complet à **CHF 290**, en ligne en 48 h |

## Ce que fait la machine, chaque matin à 7 h (toute seule)

1. **Lit les nouvelles inscriptions** au registre du commerce (FOSC) dans les cantons JU, NE, VD, GE, FR et VS (publications en français).
   On en observe environ **1 000 par mois** en Suisse romande.
2. **Écarte ce qui n'est pas une cible** : holdings, sociétés de participations, succursales, associations, fondations.
3. **Devine le métier** à partir du but social (« exploitation d'un salon de coiffure » → coiffeur). 17 métiers sont
   reconnus. Les autres entreprises reçoivent un kit générique, construit à partir de leur propre activité.
4. **Fabrique le kit** : site adapté aux téléphones, 3 logos, carte de visite, texte de fiche Google, 4 premières publications.
5. **Met tout en ligne** gratuitement sur GitHub Pages. Les liens sont impossibles à deviner et invisibles sur Google.
6. **Remplit ton appli web-design.ch** (base Supabase) : pour chaque entreprise, son activité et des boutons
   *Voir son kit*, *Annuaire*, *Google*, *Appeler*, *SMS* et *WhatsApp*, avec le message déjà rempli.
7. **Rédige les 4 publications du mois** de chacun de tes clients abonnés (onglet « Clients » de l'appli).

## Mise en route (15 minutes, 0 CHF)

1. **Activer le site des kits** : sur GitHub, *Settings → Pages → Build and deployment → Source : **GitHub Actions***.
2. **Relier la machine à ta base** : dans Supabase, projet **jour-un** → *Project Settings → API Keys* → copie la
   **secret key**. Puis sur GitHub : *Settings → Secrets and variables → Actions → New repository secret*,
   Name : `SUPABASE_SECRET`, Secret : la clé copiée. Ne la donne à personne.
3. **Créer ton mot de passe de secours** : même endroit, Name : `COCKPIT_MOT_DE_PASSE`, Secret : un mot de passe long.
   Il protège le cockpit de secours et rend les liens des kits impossibles à deviner.
4. **Créer ton compte dans l'appli** : ouvre `https://web-design-ch.vercel.app`, tape ton email
   (ardaaris14@gmail.com) et un mot de passe d'au moins 8 caractères, puis **« Première fois ? Créer mon compte »**.
   Seul ton email est autorisé : personne d'autre ne peut créer de compte.
5. **Lancer la machine** : dans l'appli, onglet *Machine → Lancer maintenant* (elle démarre dans les 15 minutes).
   Au premier lancement, elle lit les 45 derniers jours, ce qui peut prendre 10 à 20 minutes.

## Ton appli web-design.ch (téléphone et ordinateur)

`https://web-design-ch.vercel.app` : connecte-toi, puis installe-la comme une appli
(iPhone : Partager → « Sur l'écran d'accueil » ; Android : menu ⋮ → « Installer l'application »).

| Onglet | Ce que tu y fais |
|---|---|
| **Prospects** | Les nouvelles entreprises et leur kit : Annuaire, Appeler, SMS après accord, statut, bouton **Stop** (retire définitivement l'entreprise et supprime son kit) |
| **Clients** | Tes clients (avec suivi ou kit seul), arrêter ou reprendre un suivi, copier les 4 publications du mois |
| **Ventes** | Tes statistiques : kit + suivi, kit seul, part avec suivi, abonnements actifs, encaissé du mois ; tes 2 liens de paiement ; ajout d'une vente payée par TWINT ou en espèces |
| **Réglages** | Tes coordonnées, tes prix, ton lien de paiement, tes cantons, tes métiers, tes messages, les exclusions, ton mot de passe |
| **Machine** | Voir les derniers passages du robot, le relancer d'un bouton |

Tout est enregistré dans ta base Supabase (projet **jour-un**, hébergé à Zurich). La machine tourne gratuitement sur
GitHub chaque matin, lit tes réglages dans la base et y dépose les nouveaux prospects. Chaque modification de réglages
la relance automatiquement dans les 15 minutes.

Le cockpit de secours reste disponible sur `https://ardaaris14-del.github.io/mon-premier-projet/cockpit/` (même mot de
passe que `COCKPIT_MOT_DE_PASSE`), au cas où l'appli serait indisponible.

## La règle d'or en Suisse : appeler d'abord

La loi contre la concurrence déloyale (LCD) encadre la prospection :
- **SMS, WhatsApp, email publicitaires sans accord préalable : interdits** (art. 3 al. 1 let. o LCD). C'est pour ça que les
  boutons de l'appli disent « après accord ».
- **Appeler un numéro marqué d'un astérisque (\*) dans l'annuaire : interdit** (art. 3 al. 1 let. u LCD). Vérifie avec le bouton *Annuaire* avant d'appeler.
- **Appeler un numéro sans astérisque et passer en personne : autorisé.**

**Le bon enchaînement :** annuaire → appel → « Je vous envoie le lien par SMS ? » → **oui** → bouton SMS.
Bonus : un créateur qui a dit oui au téléphone ouvre le lien beaucoup plus souvent.

## Ta journée (environ 1 h 30)

1. Ouvre l'appli sur ton téléphone et filtre sur **« Arrivés cette semaine »**.
2. Pour chaque entreprise : bouton **Annuaire** (search.ch), sinon **Google**, pour trouver son numéro (1 minute).
3. **Appelle** (script dans `documents/prospection.md`). S'il est d'accord, envoie le kit par SMS en un clic.
4. **Relance à J+3** (« Vous avez pu regarder votre kit ? »), puis une dernière fois à J+10. Jamais plus.
5. S'il dit oui : encaisse, puis suis `documents/livraison.md`.

Objectif : **15 appels par jour**. Pour les entreprises proches de chez toi (Franches-Montagnes, Delémont, La Chaux-de-Fonds…),
tu peux aussi **passer les voir**, téléphone en main avec leur kit ouvert.

## L'offre

| | Prix | Contenu |
|---|---|---|
| **Kit de lancement** | **CHF 290** une fois | Site en ligne sur son nom de domaine .ch (1 an inclus), logo en haute définition, carte de visite prête à imprimer, fiche Google créée avec lui + 4 publications |
| **Suivi** (option) | **CHF 39/mois** sans engagement | Hébergement, modifications, 4 publications par mois (rédigées par la machine), réponse aux avis |

**Encaisser :** deux liens de paiement Stripe sont en place, **Kit + suivi** (CHF 290 + CHF 39/mois) et **Kit seul**
(CHF 290). Ils apparaissent sur chaque kit et se modifient dans l'appli (onglet Réglages). Chaque paiement arrive tout
seul dans l'appli : la vente est enregistrée, le client est créé (retrouvé parmi tes prospects par son téléphone ou son
nom) et, s'il résilie son abonnement dans Stripe, son suivi s'arrête. Seuls les paiements passés par ces 2 liens sont
comptés. Un client qui paie par TWINT ou en espèces s'ajoute à la main dans l'onglet Ventes.

**Ton coût par vente :** environ CHF 15 de nom de domaine .ch, payés avec les CHF 290 du client.

## Les chiffres (hypothèses à vérifier)

- Environ **1 000 nouvelles inscriptions par mois** en Suisse romande, dont peut-être 600 à 700 cibles une fois les holdings et succursales écartées.
- Tu trouveras un numéro pour environ la moitié.
- Hypothèse : sur 100 créateurs appelés, **3 à 6** achètent le kit, car ils voient le résultat avant de payer.

**Scénario ambitieux** (15 appels par jour ouvré, 3 à 5 % de ventes) :

| | Mois 1 | Mois 2 | Mois 3 | Total |
|---|---|---|---|---|
| Créateurs appelés | 300 | 330 | 330 | 960 |
| Kits vendus | 8 | 12 | 15 | **35** |
| Kits × CHF 290 | 2 320 | 3 480 | 4 350 | **10 150 CHF** |
| Abonnés à CHF 39/mois (1 kit sur 3) | 3 | 7 | 12 | ~850 CHF |

**Scénario prudent** (2 %) : environ 19 kits vendus, soit **~5 500 CHF** sur 3 mois.

Pour **10 000 CHF/mois** ensuite : environ **25 kits par mois** (7 250 CHF) + **70 abonnés** (2 730 CHF). Le levier qui rend
ça atteignable, ce sont les **partenaires** (ci-dessous).

**Ton premier indicateur :** après 100 appels, compte les ventes. En dessous de 2, change ton message, ton prix ou les métiers visés avant de continuer.

## Les partenaires : ton accélérateur

En Suisse, presque toutes les Sàrl et SA passent par un **notaire** (acte de fondation) et souvent par une **fiduciaire**.
Ces professionnels voient des créateurs chaque semaine. Propose-leur d'**offrir le kit** à leurs nouveaux clients : c'est un
cadeau de bienvenue qui ne leur coûte rien, et tu leur reverses **CHF 50 par kit activé**. Pense aussi aux banques
cantonales et aux structures d'aide à la création (Créapole dans le Jura, par exemple). Script dans `documents/prospection.md`.

## Démarches en Suisse (gratuit pour commencer)

- **Statut :** tu démarres en **entreprise individuelle**. L'inscription au registre du commerce n'est obligatoire qu'à partir de
  CHF 100 000 de chiffre d'affaires par an.
- **AVS :** dès tes premiers revenus, annonce-toi comme indépendant à la **caisse de compensation du canton du Jura**. Les cotisations
  d'indépendant représentent environ 10 % du revenu.
- **Impôts :** tes bénéfices s'ajoutent à ta déclaration d'impôt. **Mets de côté 25 à 30 % de chaque vente** (AVS + impôts).
- **TVA :** seulement à partir de CHF 100 000 de chiffre d'affaires par an. En dessous, tu n'en factures pas.
- **Si tu as moins de 18 ans**, il te faut l'accord de tes parents pour signer des contrats avec des clients.
- Vérifie ces points auprès de la caisse de compensation et de l'administration fiscale jurassienne : les règles et les taux évoluent.

## Les règles (non négociables)

- **« Stop » = supprimé.** Ajoute son numéro IDE (les 9 chiffres, sans « CHE ») dans `"exclus"` de `config.json` : il n'est plus jamais contacté et son kit disparaît au passage suivant de la machine.
- Les données viennent de sources publiques officielles (FOSC) et d'OpenStreetMap. Tu ne contactes que des entreprises, pour une offre liée à leur activité.
- Chaque kit indique clairement qu'il s'agit d'un **aperçu non officiel**. Il n'est pas référencé sur Google et son lien est impossible à deviner.
- Le cockpit est chiffré : sans ton mot de passe, personne ne peut lire la liste. Ne partage jamais ce mot de passe.
- Jamais de faux avis, jamais de promesse de première place sur Google.

## Contenu du dossier

| Chemin | Rôle |
|---|---|
| `automatisation/config.json` | Réglages de départ, copiés dans la base au premier lancement. Ensuite, modifie-les dans l'appli (onglet Réglages). |
| `automatisation/machine.py` | La machine : prospection, kits, cockpit, publications des clients |
| `automatisation/sources.py` | Les sources : FOSC (Suisse), OpenStreetMap, et SIRENE/INSEE si tu passes `"pays"` à `"FR"` |
| `automatisation/metiers.py` | Contenu et mots-clés de chaque métier. Pour en ajouter un, copie un bloc. |
| `automatisation/kit.py`, `kit.html` | Le kit de lancement (logos, carte de visite, fiche Google, publications) |
| `automatisation/base.py`, `decision.py` | Lien avec la base Supabase, et décision de lancer la machine (matin ou demande depuis l'appli) |
| `automatisation/cockpit.html` | Le cockpit de secours |
| `webapp/` | Ton appli web-design.ch, en ligne sur Vercel |
| `supabase/functions/stripe-webhook/` | Reçoit les paiements Stripe et les enregistre dans ta base |
| `generateur/` | Le générateur de site (utilisé par la machine, ou à la main pour le site final d'un client) |
| `agence/index.html` | Ta page publique web-design.ch |
| `outils/kit-avis.html` | Affiche QR code pour que tes clients récoltent des avis Google |
| `documents/` | Scripts d'appel, livraison d'un kit, conditions de vente |
| `../.github/workflows/` | L'automatisation : `machine.yml` (tous les jours) et `tests.yml` |

Lancer la machine sur ton ordinateur (facultatif) :
```bash
pip install -r jour-un/requirements.txt
python3 jour-un/automatisation/machine.py            # le site est créé dans _site/
python3 -m unittest discover -s jour-un/automatisation/tests
```
