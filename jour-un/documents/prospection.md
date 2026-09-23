# Scripts Jour Un (Suisse)

Règle d'or : **tu ne vends rien, tu montres.** Le kit fait la vente. Ton seul objectif au téléphone : obtenir un
« oui, envoyez-moi le lien ».

Règle légale : **on appelle d'abord, on envoie ensuite.** Pas de SMS, de WhatsApp ou d'email publicitaire sans accord
(art. 3 al. 1 let. o LCD), et jamais d'appel vers un numéro marqué d'un astérisque dans l'annuaire (let. u).

Les messages envoyés après l'appel sont **déjà remplis dans le cockpit** (modifiables dans `automatisation/config.json`, section `messages`).

## 1. Trouver le numéro (1 minute)

Dans le cockpit, sur la fiche de l'entreprise :
1. bouton **Annuaire** (search.ch) : cherche le nom de l'entreprise ou du fondateur. **Un astérisque (\*) = on n'appelle pas.**
2. sinon, bouton **Google** : site existant, page Facebook ou Instagram, annonce.
3. rien trouvé, mais un commerce, un atelier ou un restaurant proche de chez toi → **visite**.

Ne cherche pas plus de 2 minutes : passe à la suivante.

## 2. L'appel (le cœur du métier)

> « Bonjour, je suis Arda, de Jour Un. J'ai vu dans la Feuille officielle du commerce que [Nom] venait d'être inscrite :
> félicitations !
>
> J'aide les nouvelles entreprises de la région à trouver leurs premiers clients, et j'ai pris l'initiative de vous préparer
> un site internet, un logo et une carte de visite, déjà à votre nom. Ça ne vous engage à rien de regarder.
> Je vous envoie le lien par SMS ? »

- **Oui** → bouton **SMS (après accord)** pendant l'appel, puis : « C'est envoyé. Je vous rappelle jeudi pour avoir votre avis ? »
- **Non** → « Pas de souci, belle réussite pour votre lancement ! » et statut « Pas intéressé ».
- **Messagerie** → ne laisse pas de message commercial. Rappelle un autre jour, à une autre heure.

Meilleurs créneaux : 8 h 30 – 11 h et 14 h – 16 h 30. Évite les lundis matin et l'heure du repas.

## 3. La visite (commerces, restaurants, ateliers proches)

> « Bonjour ! Je suis Arda. Vous venez d'ouvrir, c'est ça ? Félicitations. Regardez, je vous ai préparé quelque chose. »
>
> *(Tendre le téléphone, kit ouvert sur le site.)*
>
> « C'est votre site, avec votre nom. Il y a aussi trois logos et votre carte de visite. Si ça vous plaît, je le mets en ligne cette semaine. »

## 4. Les relances (seulement si la personne a accepté de recevoir le kit)

- **J+3** : « Bonjour, c'est Arda de Jour Un. Vous avez pu jeter un œil à votre kit ? Je peux changer les couleurs ou le logo si vous voulez. »
- **J+10** : « Dernier message de ma part : votre kit reste disponible cette semaine, ensuite je le retire. Belle continuation ! »
- Rien après ça. Au moindre « stop », ajoute son numéro IDE dans `exclus`.

## 5. Réponses aux objections

| Il dit | Tu réponds |
|---|---|
| « Comment vous avez eu mes infos ? » | « Les nouvelles inscriptions au registre du commerce sont publiées officiellement dans la FOSC. Si vous préférez, je supprime votre kit tout de suite. » |
| « C'est une arnaque ? » | « Vous ne payez rien pour regarder, et vous ne payez que si vous le gardez. Vous recevez une facture en bonne et due forme. » |
| « C'est trop cher. » | « C'est CHF 290 une fois : site, nom de domaine pour un an, logo et carte de visite. Une agence demande souvent plus de CHF 2 000 rien que pour le site. » |
| « Je vais le faire moi-même avec Wix. » | « Vous pouvez ! Wix coûte environ CHF 20 par mois, et il faut y passer des soirées. Ici, c'est déjà fait et en ligne en 48 h. » |
| « Je n'ai pas le temps. » | « Justement : vous n'avez rien à faire. Dites-moi juste quel logo vous préférez. » |
| « Le logo ne me plaît pas. » | « On le change, c'est compris. Quelles couleurs vous imaginez ? » |
| « J'ai déjà quelqu'un pour ça. » | « Parfait, alors vous êtes entre de bonnes mains. Belle réussite ! » (et statut « Pas intéressé ») |

## 6. Démarcher des partenaires (fiduciaires, notaires, banques)

**Email :**

> Objet : Un cadeau de bienvenue pour vos clients qui créent leur entreprise
>
> Bonjour,
>
> Je m'appelle Arda Aris et j'ai créé Jour Un : pour chaque nouvelle entreprise, je prépare un kit de lancement complet
> (site internet, logo, carte de visite, fiche Google), à son nom, avant même qu'elle le demande.
>
> Je vous propose de l'**offrir à vos clients qui créent leur société** : vous me transmettez le nom de l'entreprise, je prépare
> le kit sous 24 h avec la mention « offert par [votre fiduciaire] », et je vous reverse CHF 50 pour chaque kit activé.
>
> Voici un exemple de kit : [lien vers un kit réel ou de démonstration]
>
> Seriez-vous d'accord pour en parler 15 minutes cette semaine ?
>
> Arda Aris — 076 698 40 59

Un email à un professionnel pour lui proposer un partenariat, envoyé personnellement et une seule fois, reste une démarche
individuelle, pas de la publicité de masse. Écris à chacun personnellement, jamais en copie groupée.

**Qui cibler :** fiduciaires de la région (Franches-Montagnes, Delémont, Porrentruy, La Chaux-de-Fonds), études de notaires,
conseillers « entreprises » de la Banque cantonale du Jura, Créapole.

Une seule fiduciaire qui crée 5 sociétés par mois, c'est potentiellement 5 kits par mois, sans chercher.
