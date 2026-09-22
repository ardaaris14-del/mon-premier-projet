# Visibilité Locale — le business clé en main

Un service mensuel qui fait monter les commerces et artisans de ta ville sur **Google Maps**.
Démarrage à **0 €**. Tout ce qu'il faut pour vendre et livrer est dans ce dossier.

> **À lire d'abord, honnêtement.** Personne ne peut te garantir 10 000 €. Ce plan te donne un modèle
> qui *peut* y arriver, des outils prêts à l'emploi et des calculs réalistes. Le résultat dépendra
> presque entièrement d'une chose : **combien de commerçants tu contactes chaque jour.** Les outils, c'est
> 20 % du travail. Contacter des gens, c'est 80 %.

---

## 1. Le business en une phrase

« Je fais en sorte que vous ayez plus d'avis, une meilleure note et plus d'appels depuis Google Maps,
pour 149 € par mois, sans engagement. »

**Pourquoi ça marche mieux que vendre des sites web :**
- Le commerçant ne signe pas un gros chèque. 190 € puis 149 €/mois, résiliable à tout moment : **le « oui » est beaucoup plus facile**.
- Le problème est **visible en 30 secondes** : tu tapes « plombier + sa ville » devant lui, et son concurrent est au-dessus avec 3 fois plus d'avis.
- Chaque client **paie tous les mois**, donc ton revenu s'additionne au lieu de repartir de zéro chaque mois.
- Coût pour toi : **0 €**. Google Business, hébergement Netlify, outils de ce dossier : tout est gratuit.

## 2. L'offre (à ne pas modifier au début)

| | Contenu | Prix |
|---|---|---|
| **Mise en place** | Fiche Google 100 % optimisée (catégories, description, services, horaires, 15-20 photos), kit avis (affiche QR code + messages SMS/email), mini-site internet mis en ligne | **190 €** une fois |
| **Abonnement** | Réponse à tous les avis sous 48 h, 4 publications Google par mois, mise à jour photos, suivi du mini-site, rapport mensuel (avis, note, appels, position) | **149 €/mois**, sans engagement |

**Offre de lancement (tes 3 premiers clients uniquement) :** mise en place offerte, en échange d'un témoignage
et de l'autorisation de montrer leurs résultats. C'est ce qui te donnera des preuves pour tous les suivants.

**Ce que tu ne fais JAMAIS :** faux avis, avis achetés, demander des avis uniquement aux clients contents
(Google l'interdit et peut supprimer la fiche), promettre « 1ʳᵉ place garantie ». Tu promets du travail et
des chiffres mesurés, pas un classement.

## 3. Les calculs

**Objectif « 10 000 € encaissés sur les 3 premiers mois »** (scénario ambitieux, temps plein) :

| Mois | Nouveaux clients | Clients actifs | Mises en place (190 €) | Abonnements (149 €) | Encaissé |
|---|---|---|---|---|---|
| 1 | 6 (dont 3 offerts) | 6 | 570 € | ~450 € (au prorata) | ~1 000 € |
| 2 | 10 | 16 | 1 900 € | 2 380 € | ~4 300 € |
| 3 | 12 | 28 | 2 280 € | 4 170 € | ~6 450 € |
| **Total** | | | | | **~11 750 €** |

**Scénario prudent** (moitié moins de signatures) : ~5 500 € sur 3 mois. C'est déjà un vrai revenu, et la base récurrente continue de grossir.

**Objectif « 10 000 €/mois »** = environ **67 clients à 149 €**. En signant 10 à 12 clients par mois et en en perdant ~5 % chaque mois,
tu y arrives **entre le 6ᵉ et le 9ᵉ mois**. Au-delà de ~40 clients, il faudra soit automatiser, soit payer un
freelance pour les publications (avec l'argent des clients, jamais le tien).

**D'où viennent les signatures (hypothèses à vérifier avec ton suivi) :**
100 commerçants contactés par semaine → ~15 acceptent l'audit gratuit → ~6 rendez-vous → **2 à 3 signatures**.
Si tes chiffres sont plus bas, le suivi (`documents/suivi-prospects.csv`) te dira à quelle étape ça bloque.

## 4. Plan sur 90 jours

### Semaine 1 : installation (0 €)
- [ ] Créer ta micro-entreprise sur **formalites.entreprises.gouv.fr** (gratuit, activité : « conseil en communication / marketing digital »). Il faut être majeur (ou mineur émancipé).
- [ ] Ouvrir un compte bancaire séparé en ligne gratuit, et un compte **Stripe** (gratuit, commission seulement sur les paiements) pour les prélèvements mensuels.
- [ ] Mettre ta page d'agence en ligne gratuitement : glisser le dossier `agence/` sur **app.netlify.com/drop** (changer ton nom, ton téléphone et ton email dans `agence/index.html` avant).
- [ ] Choisir **une ville + 2 métiers** (voir « niches » ci-dessous).
- [ ] Construire une liste de **200 prospects** sur Google Maps dans `documents/suivi-prospects.csv` : ceux qui ont **moins de 30 avis, peu de photos ou pas de site**.
- [ ] Apprendre par cœur le script de `documents/prospection.md` et le répéter à voix haute 10 fois.
- [ ] Faire 3 audits d'entraînement avec `outils/audit.html`.

### Semaines 2 à 4 : les 6 premiers clients
- **Chaque jour, du lundi au vendredi :** 20 contacts (10 visites en boutique le matin, 10 appels l'après-midi).
- Tout prospect intéressé reçoit **son audit personnalisé** le jour même (PDF depuis `outils/audit.html`).
- Les 3 premiers : mise en place offerte contre témoignage.
- Livrer chaque client en 48 h avec `documents/livraison.md`.

### Mois 2 : la routine (+10 clients)
- Continuer à 20 contacts/jour. C'est non négociable.
- Montrer les **résultats de tes premiers clients** (avis gagnés, appels en plus) dans chaque rendez-vous.
- **Parrainage :** 1 mois offert à tout client qui te recommande un commerçant qui signe. Les artisans se connaissent tous.
- Envoyer le premier rapport mensuel à chaque client (le rapport, c'est ce qui les fait rester).

### Mois 3 : accélérer (+12 clients)
- Te concentrer sur le métier qui signe le mieux (regarde ton suivi) et élargir aux villes voisines.
- Ajouter des services en plus aux clients existants : mini-site plus complet (+20 €/mois), gestion Instagram/Facebook (+99 €/mois).
- Passer à 25 contacts/jour si ton taux de signature est bon.

### Mois 4 et suivants : vers 10 000 €/mois
- Rythme de 10 à 12 signatures par mois, suivi du taux de départ des clients.
- Dès ~40 clients : confier les publications à un freelance (~20-30 €/client/mois) et garder la vente pour toi.

## 5. Niches recommandées

**À privilégier :** artisans du bâtiment (plombier, électricien, chauffagiste, couvreur, peintre), garages et carrosseries,
instituts de beauté, coiffeurs, barbiers, restaurants indépendants, auto-écoles.

**À éviter au début :** professions de santé (règles strictes sur la publicité), serruriers et dépanneurs (secteur plein d'arnaques
et de méfiance), chaînes et franchises (décision prise au siège).

## 6. Journée type

| Heure | Tâche |
|---|---|
| 9 h – 12 h | Visites en boutique (10 commerçants), en évitant les heures de rush |
| 12 h – 14 h | Livraison et gestion des clients (avis, publications) |
| 14 h – 16 h | Appels (10) + envoi des audits |
| 16 h – 18 h | Rendez-vous de présentation / signatures |
| 18 h – 18 h 15 | Mise à jour du fichier de suivi |

## 7. Argent, factures, impôts

- **Paiement :** abonnement mensuel par prélèvement Stripe (lien de paiement récurrent). Pas de prélèvement = pas de travail.
- **Facture** pour chaque paiement (Stripe peut les générer). Mentions obligatoires : ton nom, SIRET, « TVA non applicable, art. 293 B du CGI » tant que tu restes sous le seuil de franchise de TVA.
- **Cotisations sociales :** environ un quart de ton chiffre d'affaires, à déclarer chaque mois ou trimestre sur autoentrepreneur.urssaf.fr. **Mets de côté 25 % de chaque paiement** dès le premier euro.
- Vérifie les seuils à jour (franchise de TVA, plafond de la micro-entreprise) sur **urssaf.fr** et **impots.gouv.fr** : ils changent souvent.

## 8. Contenu du dossier

| Fichier | À quoi il sert |
|---|---|
| `outils/audit.html` | **Ton outil de vente.** Audit de fiche Google avec score sur 100, comparaison avec les concurrents et ton offre. Ouvre-le dans un navigateur, remplis, imprime en PDF. |
| `outils/kit-avis.html` | Affiche avec QR code et messages SMS/email pour obtenir des avis. Livré à chaque client. Fonctionne sans internet (garder `qrcode.js` dans le même dossier). |
| `generateur/` | Crée le mini-site d'un client en 5 minutes à partir d'un fichier de configuration (voir ci-dessous). |
| `agence/index.html` | Ta page d'agence, à mettre en ligne gratuitement sur Netlify. |
| `documents/prospection.md` | Scripts de visite, d'appel et de relance, et réponses aux objections. |
| `documents/livraison.md` | Liste de contrôle pour la mise en place et le travail de chaque mois. |
| `documents/contrat.md` | Modèle de contrat d'abonnement. |
| `documents/suivi-prospects.csv` | Ton fichier de suivi (à ouvrir dans Excel, Google Sheets ou LibreOffice). |

### Créer le mini-site d'un client

```bash
cd generateur
cp clients/exemple-plomberie-martin.json clients/nom-du-client.json   # puis modifier le fichier
python3 generer_site.py clients/nom-du-client.json
```
Le site est créé dans `agence-web/sites/nom-du-client/`. Pour le mettre en ligne : glisser ce dossier sur **app.netlify.com/drop** (gratuit).
Laisse `"maquette": true` pour montrer une maquette à un prospect, puis passe-le à `false` une fois qu'il a signé.
Les avis affichés doivent être **de vrais avis Google du client**, recopiés mot pour mot.

---

**Résumé :** 20 contacts par jour, un audit gratuit pour chaque personne intéressée, une livraison sérieuse, un rapport chaque mois.
Le reste, ce sont des détails.
