# Livraison client

## Mise en place (sous 48 h après la signature)

**Récupérer auprès du client**
- [ ] Accès **gestionnaire** à sa fiche Google Business (il t'ajoute depuis sa fiche : « Profil → Gérer les accès »). Ne jamais demander son mot de passe.
- [ ] 15 à 20 photos : devanture, intérieur, équipe, réalisations avant/après, véhicule. Si besoin, les prendre toi-même sur place avec ton téléphone.
- [ ] Liste de ses services et prix indicatifs, zone d'intervention, horaires, années d'expérience, certifications.
- [ ] SIRET et raison sociale (pour les mentions légales du mini-site).

**Fiche Google**
- [ ] Catégorie principale la plus précise possible + catégories secondaires pertinentes.
- [ ] Description de 700 caractères environ : métier, ville, zone, points forts, sans empiler les mots-clés.
- [ ] Tous les services renseignés, avec une courte description.
- [ ] Horaires, horaires spéciaux (jours fériés), zone desservie, attributs.
- [ ] Ajout des photos (en nommant les fichiers ainsi : `metier-ville-description.jpg`).
- [ ] Lien vers le mini-site.
- [ ] Répondre à **tous** les anciens avis sans réponse.

**Mini-site**
- [ ] Copier `generateur/clients/exemple-plomberie-martin.json` → `clients/<client>.json`, remplir, `"maquette": false`.
- [ ] `python3 generer_site.py clients/<client>.json` puis mettre en ligne `sites/<client>/` sur Netlify Drop.
- [ ] Nom de domaine (~10-15 €/an) payé par le client, ou adresse Netlify gratuite.

**Kit avis**
- [ ] Ouvrir `outils/kit-avis.html`, coller le lien d'avis du client, imprimer l'affiche (comptoir, caisse, camion).
- [ ] Donner au client les messages SMS/email et lui expliquer : **un message à chaque client, après chaque prestation**.
- [ ] Noter dans le suivi les chiffres de départ : note, nombre d'avis, position, appels du mois dernier (statistiques de la fiche).

## Chaque mois (≈ 2 h par client)

- [ ] Répondre à tous les nouveaux avis sous 48 h (positifs : remercier en citant la prestation ; négatifs : calme, excuses si justifié, proposer d'en parler par téléphone).
- [ ] 4 publications Google (1 par semaine) : réalisation récente avec photo, conseil saisonnier, offre, coulisses.
- [ ] Ajouter 3-5 nouvelles photos.
- [ ] Relancer le client s'il n'a pas envoyé de demandes d'avis.
- [ ] Mettre à jour le mini-site si nécessaire.
- [ ] **Envoyer le rapport mensuel** (ci-dessous).

## Rapport mensuel (à envoyer le 1er de chaque mois)

> **[Nom du client] — rapport de [mois]**
>
> | | Début | Aujourd'hui |
> |---|---|---|
> | Note Google | 4,1 | 4,5 |
> | Nombre d'avis | 12 | 27 |
> | Position sur « [métier] [ville] » | 8ᵉ | 3ᵉ |
> | Appels depuis Google (ce mois) | 14 | 31 |
>
> Ce mois-ci : 15 nouveaux avis, 4 publications, 6 photos ajoutées.
> Le mois prochain : [une action concrète].

C'est ce rapport qui fait qu'un client reste. Ne l'oublie jamais.
