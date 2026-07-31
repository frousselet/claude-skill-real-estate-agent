# Cahier des charges : questionnaire et schéma JSON

> **Le gabarit fait foi, à la lettre.** Comme pour la fiche A4, tu remplis
> uniquement le JSON décrit ici, puis tu lances `scripts/generer_cdc_pdf.py`. La
> forme (police et sa taille, graisses, couleurs, marges, sauts de page, ordre des
> sections) est fixée par `assets/cdc_template.html` et le script. Si un texte est
> trop long, tu le raccourcis, tu ne modifies ni le CSS, ni les polices, ni le
> zoom.

Le cahier des charges est le **mandat de recherche** : ce que la personne cherche,
avec quel budget, où, et surtout ce qu'elle refuse. Il se construit par un
**entretien**, pas par un formulaire envoyé d'un bloc. Deux modes :
`achat` (acquéreur) et `location` (candidat locataire).

---

## 1. Conduite de l'entretien

**Une seule règle d'or : poser peu de questions, mais les bonnes.** Un cahier des
charges utile tient en 25 à 35 réponses. Au-delà, la personne décroche et les
réponses perdent en qualité.

1. **Par blocs, pas en rafale.** Sept blocs (§2), un bloc par tour de parole,
   **3 à 5 questions à la fois au maximum**. Annonce le nombre de blocs au début
   pour que la personne sache où elle en est (« bloc 3 sur 7 »).
2. **Toujours proposer des options.** Chaque question fermée vient avec 2 à 4
   réponses possibles, formulées en langage d'acheteur, plus une porte de sortie
   (« autre », « je ne sais pas encore »). Si l'outil de questions à choix
   multiples est disponible, utilise-le, un bloc par appel, en activant le choix
   multiple quand les réponses ne s'excluent pas. Sinon, numérote les options pour
   qu'on puisse répondre « 1b, 2a ».
3. **Ne jamais redemander ce qui est déjà connu.** Ce qui a été dit dans la
   conversation, dans une annonce fournie ou dans une étude précédente est
   pré-rempli, et seulement soumis à confirmation.
4. **Proposer une valeur par défaut plutôt qu'une case vide.** « Frais de notaire :
   7,5 % dans l'ancien, 2,5 % dans le neuf, je retiens 7,5 % ? » vaut mieux que
   « quel montant de frais ? ». La personne corrige, ce qui est plus facile que
   d'inventer.
5. **Chiffrer au fil de l'eau.** Dès que budget, apport, mensualité, durée et taux
   sont connus, annonce la capacité et l'enveloppe qui en découlent, et fais-les
   valider. Un cahier des charges dont le budget est faux ne sert à rien.
6. **Faire trancher.** Le rôle n'est pas d'enregistrer une liste de souhaits, mais
   d'obtenir des arbitrages : « si vous deviez choisir entre 15 m² de plus et le
   secteur de priorité 1, vous prenez lequel ? ». C'est cette question, posée à
   froid, qui protège des décisions prises sous pression un samedi de visite.
7. **Signaler les impossibilités, sans les corriger d'office.** Si les critères
   durs et le budget sont incompatibles avec le marché local, dis-le, chiffre
   l'écart (avec DVF ou les loyers observés si tu les as), et propose deux issues :
   relever le budget, ou relâcher un critère. Le choix reste à la personne.
8. **Restituer avant de générer.** Récapitule en une dizaine de lignes, demande la
   validation, corrige, puis seulement produis le PDF.

**Ce qui est absent est une donnée.** Un critère non tranché s'écrit « à préciser »
dans le cahier des charges. On ne comble jamais un blanc par une supposition
flatteuse.

---

## 2. Les sept blocs de questions

Les formulations ci-dessous sont des trames, à adapter à la personne. Les mentions
[achat] et [location] indiquent les questions propres à un mode.

### Bloc 1 : le cadre du projet

- Achat ou location ? Résidence principale, secondaire, ou investissement locatif ?
- Qui va habiter le logement (nombre d'adultes, d'enfants et leur âge) ?
- Combien de temps comptez-vous y rester ? (moins de 3 ans, 3 à 7 ans, plus de
  8 ans, indéterminé). [achat] En dessous de 5 ans, les frais d'acquisition sont
  rarement amortis : à signaler.
- Qu'est-ce qui déclenche ce projet (naissance, mutation, séparation, fin de bail,
  premier achat, revente) ?
- Pour quand ? Y a-t-il une date impérative (rentrée scolaire, prise de poste, fin
  de bail) ?
- Où en êtes-vous aujourd'hui (locataire avec préavis, propriétaire à vendre,
  hébergé) ?

### Bloc 2 : le budget

[achat]
- Quelle enveloppe maximale, tout compris (bien, frais, travaux, mobilier) ?
- Quel apport disponible, et quelle épargne voulez-vous conserver après l'achat ?
- Quelle mensualité maximale supportable, sur quelle durée ?
- Où en est le financement : rien d'engagé, simulation, accord de principe, offre
  éditée ? Avec ou sans courtier ?
- Êtes-vous éligible à un dispositif (PTZ, prêt employeur, prêt familial) ?
- Quel budget de travaux acceptez-vous, en argent et en mois de chantier ?

[location]
- Quel loyer maximal, charges comprises ?
- Quels revenus nets du foyer, et quel taux d'effort acceptez-vous (repère usuel :
  33 % maximum, souvent exigé par les bailleurs) ?
- Quelle garantie pouvez-vous présenter (garant physique, Visale, garantie
  d'entreprise, aucune) ?
- Le dépôt de garantie et les honoraires d'agence sont-ils provisionnés ?

Rappelle les repères, sans les asséner comme des vérités : frais de notaire de 7
à 8 % dans l'ancien, 2 à 3 % dans le neuf ; taux d'endettement usuellement plafonné
à 35 % assurance comprise ; honoraires de location plafonnés par la loi en zone
tendue. Ces repères se vérifient à la date de l'entretien.

### Bloc 3 : la localisation

- Quels secteurs visez-vous, par ordre de préférence ? Y en a-t-il un que vous
  refusez ?
- Quels lieux devez-vous rejoindre régulièrement (travail, école, crèche, famille,
  gare), par quel moyen, et en combien de temps au maximum ?
- Voulez-vous pouvoir vous passer de voiture ?
- Qu'est-ce qui compte dans l'environnement immédiat (commerces, écoles, parc,
  calme, vie de quartier) ?
- Y a-t-il des nuisances que vous ne supporterez pas (axe passant, voie ferrée,
  aéroport, bar de nuit, chantier) ?

Les temps de trajet se vérifient **aux heures réelles de déplacement**, jamais sur
un itinéraire calculé à midi. Le secteur scolaire se vérifie en mairie, jamais sur
l'annonce.

### Bloc 4 : le bien

- Quelle typologie et quelle surface minimale ? Combien de chambres réelles ?
- Appartement, maison, ou les deux ? Ancien, récent, neuf ?
- Étage souhaité, ascenseur exigé ou non ?
- Extérieur : indispensable, souhaité, indifférent ? Quelle surface minimale
  utilisable ?
- Stationnement : place, garage, ou stationnement de rue suffisant ?
- Annexes nécessaires (cave, cellier, local vélo, buanderie) ?
- Exposition et luminosité : quelle exigence sur le séjour ?
- Besoin d'un espace de travail (télétravail, profession libérale) ?
- [achat] Copropriété acceptée ? Jusqu'à quelle taille, quel niveau de charges ?
- [location] Meublé ou non meublé ? Type de bail attendu ?

### Bloc 5 : l'état et les tolérances

- Quel niveau de travaux acceptez-vous : rien, rafraîchissement, rénovation
  partielle, rénovation lourde ?
- Quel budget et quelle durée de chantier au maximum ?
- Quels travaux refusez-vous catégoriquement (structure, toiture, réseaux,
  ravalement voté) ?
- Quel DPE minimum ? (rappel : G interdit à la location depuis 2025, F en 2028,
  E en 2034 ; le DPE pèse sur la facture, la revente et la location future)
- Quelles contraintes sur le vis-à-vis, le bruit, le rez-de-chaussée ?

### Bloc 6 : rédhibitoires et arbitrages

- Qu'est-ce qui vous ferait quitter une visite au bout de deux minutes ? (3 à 5
  réponses : ce sont les rédhibitoires)
- Parmi vos critères, lesquels sont vraiment non négociables ? (limiter à 4 ou 5 :
  au-delà, ce ne sont plus des critères durs, c'est une liste de souhaits)
- Si le bien parfait n'existe pas dans le budget, dans quel ordre lâchez-vous :
  surface, secteur, étage, extérieur, stationnement, état, DPE ?
- Pour chaque concession, quelle contrepartie exigez-vous en échange (baisse de
  prix, secteur meilleur, travaux faits) ?

Ce bloc est le cœur de l'exercice : c'est lui qui produit la table des arbitrages,
décidée à froid.

### Bloc 7 : la logistique

- Quelles sont vos disponibilités pour visiter, et sous quel délai pouvez-vous vous
  déplacer ?
- Qui décide, et en combien de temps après une visite ?
- Quel préavis avez-vous à poser, et à partir de quel événement ?
- Quelles pièces de dossier avez-vous déjà réunies, lesquelles manquent ?

Sur un marché tendu, la rapidité de réaction et un dossier complet valent parfois
plus qu'un budget supérieur : à dire clairement.

---

## 3. Pondération et grille de notation

**Trois niveaux d'exigence, jamais plus** :

| Niveau | Effet sur un bien | Champ JSON |
|---|---|---|
| Non négociable | élimine le bien, sans discussion | `"niveau": "dur"` |
| Important | décote le bien, se négocie ou se répare | `"niveau": "important"` |
| Souhaité | départage deux biens comparables | `"niveau": "souhait"` |
| Bonus | agrément, ne pèse presque rien | `"niveau": "bonus"` |

Chaque critère porte un **poids de 1 à 5** (5 = décisif). Poids par défaut si non
précisé : dur 5, important 4, souhait 2, bonus 1. Vise **12 à 16 critères** au
total : moins, le cahier des charges ne discrimine rien ; plus, la page déborde et
la grille devient illisible.

**La grille de notation** reprend les critères non éliminatoires (important,
souhait, bonus) et s'imprime avec des colonnes vierges, à remplir à la main pendant
la visite : note de 0 (absent) à 5 (parfait) par critère.

    score = Σ (note × poids) ÷ (5 × Σ poids) × 100

Un bien qui échoue sur un seul critère non négociable est écarté, quel que soit son
score : les critères durs ne se compensent pas. Repères de lecture : au-dessus de
75 % le bien mérite une étude complète (Fonction 4), entre 55 et 75 % il se discute
sur le prix, en dessous de 55 % il ne vaut pas une seconde visite.

---

## 4. Schéma JSON

Tous les blocs sont optionnels sauf `projet` : un bloc absent ne s'imprime pas.
Les montants se donnent en **nombres** (sans espace ni symbole) quand le champ le
permet : le script les formate. Les textes suivent la règle de style de la skill
(pas de tiret cadratin).

```json
{
  "mode": "achat",
  "meta": { "date": "12 mars 2026", "auteur": "…" },

  "projet": {
    "titre": "Résidence principale familiale, Nantes ouest",
    "porteur": "Camille et Alex D.",
    "composition": "2 adultes, 2 enfants (4 et 7 ans)",
    "usage": "Résidence principale",
    "resume": "5 phrases maximum, ~500 caractères : qui, quoi, où, combien, quand, et l'arbitrage central.",
    "motivation": "3 phrases maximum : ce qui déclenche le projet.",
    "horizon": "8 à 10 ans"
  },

  "identite": [ { "k": "Type de projet", "v": "Primo-accession" } ],

  "arbitrage": { "position": 28, "label": "Emplacement prioritaire" },

  "surface": { "min_m2": 85, "cible_m2": 100, "pieces_min": 4, "chambres_min": 3 },

  "non_negociables": ["4 au maximum, 110 caractères chacun"],
  "redhibitoires":   ["4 au maximum, 110 caractères chacun"],

  "budget": {
    "enveloppe_max": 420000, "prix_cible": 365000,
    "apport": 78000, "mensualite_max": 1450,
    "duree_annees": 22, "taux_pct": 3.45,
    "taux_endettement": "31 % (avant travaux)",
    "financement_statut": "Accord de principe du 4 mars 2026, valable 3 mois",
    "dispositifs": "PTZ éligible, à confirmer",

    "loyer_max": 1050, "loyer_cible": 950,
    "revenus_mensuels": 3750, "taux_effort": "28 % maximum",
    "garant": "Garantie Visale obtenue",
    "depot_garantie": "1 mois hors charges, disponible",
    "honoraires_max": "12 €/m² (plafond zone tendue)",

    "postes": [ { "poste": "Prix du bien", "montant": 365000 } ],
    "unite": "€",
    "details": [ { "k": "Épargne conservée", "v": "12 000 €" } ],
    "note": "Une ou deux phrases sur la lecture du budget."
  },

  "localisation": {
    "secteurs": [ { "nom": "Hauts-Pavés", "priorite": 1, "commentaire": "Pourquoi" } ],
    "ancrages": [ { "lieu": "Travail", "mode": "Vélo", "duree_max": "25 min", "commentaire": "…" } ],
    "exclus": ["Bord de rocade"],
    "note": "…"
  },

  "criteres": [
    { "famille": "Le bien", "critere": "Chambres", "exigence": "3 minimum, principale ≥ 11 m²",
      "niveau": "dur", "poids": 5, "commentaire": "précision courte, optionnelle" }
  ],

  "tolerances": [ { "k": "Travaux acceptés", "v": "Jusqu'à 25 000 € et 3 mois" } ],

  "grille": { "criteres": [ { "critere": "Calme", "poids": 5 } ],
              "colonnes": ["Bien 1", "Bien 2", "Bien 3"] },

  "arbitrages": [ { "rang": 1, "concession": "Surface : 85 m² au lieu de 100 m²",
                    "contrepartie": "Secteur de priorité 1" } ],

  "calendrier": [ { "jalon": "Phase de visites", "date": "mars à juin 2026",
                    "statut": "en_cours", "commentaire": "…" } ],

  "dossier": [ { "piece": "Accord de principe", "statut": "obtenu" } ],

  "questions": ["Questions à poser à chaque visite, 5 à 8"],
  "avertissement": "Repris par défaut selon le mode."
}
```

**Champs calculés par le script**, à ne pas renseigner à la main : le bandeau des
trois valeurs, le total et les barres de l'enveloppe, la capacité d'emprunt
indicative (déduite de `mensualite_max`, `duree_annees` et `taux_pct` par annuité
constante, si `emprunt` n'est pas donné), le tri des critères, la déduction des
`non_negociables` depuis les critères durs, et la grille de notation si `grille`
est absent.

**Valeurs admises** : `mode` = `achat` | `location` ; `niveau` = `dur` |
`important` | `souhait` | `bonus` ; `priorite` de secteur = 1 (cible) | 2
(acceptable) | 3 (par défaut) ; `statut` de jalon = `fait` | `en_cours` |
`a_faire` | `bloquant` ; `statut` de pièce = `obtenu` | `manquant` |
`sans_objet`. `arbitrage.position` va de 0 (l'emplacement prime sur tout) à 100
(la surface et le prix priment sur tout).

En mode `location`, les `postes` du budget se donnent **en euros par an** (loyer,
charges, énergie estimée, assurance) : c'est le coût réel d'occupation, celui qui
compare deux logements, et non le loyer affiché.

---

## 5. Limites de longueur (pour que la mise en page tienne)

| Bloc | Limite |
|---|---|
| `projet.resume` | 5 phrases, ~500 caractères (tronqué à 5 lignes) |
| `non_negociables`, `redhibitoires` | 4 items, 110 caractères chacun (tronqués à 2 lignes) |
| `identite` | 8 lignes (2 colonnes de 4) |
| `criteres` | 16 lignes maximum, commentaires très courts |
| `tolerances` | 6 lignes, une ligne de texte chacune |
| `localisation.secteurs` | 6 lignes |
| `arbitrages` | 5 lignes |
| `calendrier` | 6 jalons |
| `questions` | 8 questions |

Le document fait typiquement 5 à 6 pages : synthèse, budget, localisation,
critères, grille et suite. Si un bloc déborde, **on raccourcit le texte ou on
réduit le nombre d'items** : jamais de zoom, jamais de changement de police ou de
marges (même règle que la fiche A4).

---

## 6. Après le cahier des charges

Le cahier des charges est le point d'entrée de la **Fonction 1 (recherche)** : les
critères durs deviennent les filtres, les souhaits pondérés deviennent le
classement, les rédhibitoires deviennent les motifs d'élimination explicites. Il
alimente aussi la **Fonction 2 (fiche A4)**, où le score pondéré de la grille se
confronte au verdict du bien.

Propose ensuite, dans cet ordre : lancer la recherche sur les secteurs de
priorité 1, ou, si le marché local est mal connu, une étude de marché (Fonction 5)
pour vérifier que l'enveloppe et les critères sont compatibles avec les prix
réellement signés.
