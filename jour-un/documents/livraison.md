# Livrer un kit vendu (en 48 h)

## 1. Encaisser
- [ ] Paiement reçu (CHF 290 par TWINT, virement avec facture QR ou lien Stripe) et facture envoyée.
- [ ] Statut « Client » dans le cockpit.
- [ ] S'il prend le suivi : CHF 39/mois (ordre permanent ou abonnement Stripe), puis ajout dans `automatisation/clients.json`.

## 2. Récupérer auprès du client (10 minutes au téléphone)
- [ ] Le logo choisi (1, 2 ou 3) et ses couleurs préférées.
- [ ] Son téléphone, son email et ses horaires réels.
- [ ] 3 à 6 photos (lui au travail, réalisations, local) : il peut les envoyer par WhatsApp.
- [ ] Quelques lignes sur lui : parcours, années d'expérience, ce qui le distingue.
- [ ] Le nom de domaine qu'il veut (ex. : `plomberie-durand.ch`).

## 3. Le site final
- [ ] Copier `generateur/clients/exemple-plomberie-martin.json` → `generateur/clients/<client>.json`.
- [ ] Remplir avec ses vraies informations et mettre `"maquette": false`.
- [ ] `python3 jour-un/generateur/generer_site.py jour-un/generateur/clients/<client>.json`
- [ ] Mettre en ligne le dossier `jour-un/sites/<client>/` : glisser-déposer sur **app.netlify.com/drop** (gratuit).
- [ ] Acheter son nom de domaine .ch (~CHF 15/an, chez Infomaniak, Hostpoint ou Netlify) **à son nom**, et le brancher sur Netlify.

## 4. Logo et carte de visite
- [ ] Ouvrir son kit, faire un clic droit sur le logo choisi → « Enregistrer l'image » (format SVG = qualité parfaite à toutes les tailles).
- [ ] Carte de visite : bouton « Imprimer la carte » dans son kit → enregistrer en PDF → à envoyer à l'imprimeur de son choix.

## 5. Sa fiche Google
- [ ] Avec lui (au téléphone ou sur place) : créer sa fiche sur **business.google.com** depuis **son** compte Google, jamais le tien.
- [ ] Coller la description et les catégories de son kit, ajouter ses photos, ses horaires et le lien du site.
- [ ] Il reçoit un code de validation de Google (appel, SMS ou courrier) : lui rappeler de le saisir.
- [ ] Publier les 4 premières publications de son kit (une par semaine).
- [ ] Lui donner l'affiche QR code (`outils/kit-avis.html`) pour récolter ses premiers avis.

## 6. Après la livraison
- [ ] Message une semaine après : « Tout fonctionne ? Vous avez eu vos premiers appels ? »
- [ ] Lui demander un avis ou un témoignage, et s'il connaît d'autres créateurs (parrainage : CHF 30 offerts par filleul qui achète).

## Chaque mois pour les abonnés (≈ 20 min par client)
- [ ] Publier les 4 posts préparés dans le cockpit (section « Mes clients »).
- [ ] Répondre aux nouveaux avis.
- [ ] Faire les modifications demandées sur le site.
