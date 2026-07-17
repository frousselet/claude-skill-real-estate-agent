# Formats de restitution : fiche, étude, shortlist

> **Le gabarit fait foi, à la lettre.** Pour la fiche A4 PDF, tu remplis uniquement
> le JSON décrit ici, puis tu lances `scripts/generer_fiche_pdf.py`. La forme
> (police et sa taille, graisses, couleurs, interlignes, espacements, marges, sauts
> de page, ordre des sections) est fixée par `assets/fiche_template.html` et le
> script ; tu n'y touches jamais pour un bien donné. Si un texte est trop long, tu
> le raccourcis, tu ne modifies ni le CSS ni les polices.

## Barème du verdict (feu tricolore)

Le verdict synthétise l'intérêt du bien pour l'acheteur, en croisant le prix (par
rapport à la valeur défendable) et le niveau de risque global.

- **Vert (à poursuivre)** : prix proche ou inférieur à la valeur d'acquisition
  défendable, aucun risque critique non maîtrisable.
- **Orange (sous conditions)** : écart de prix négociable, ou risques élevés qui
  se lèvent par vérification, diagnostic ou provision.
- **Rouge (à écarter en l'état)** : prix très supérieur à la valeur défendable
  sans marge de négociation, ou risque critique rédhibitoire.

Une note sur 100 peut accompagner le feu, à titre indicatif (emplacement, état,
prix, risques, copropriété), mais le feu et la valeur chiffrée priment.

Dans la fiche PDF, le verdict s'affiche sur une **jauge dégradée vert → rouge** :
le curseur est positionné par la note (100/100 côté vert, 0/100 côté rouge), ou à
défaut par le feu. Juste en dessous figurent les `points_forts` (puces vertes) et
`points_faibles` (puces rouges), puis le paragraphe de synthèse (`verdict.resume`).
Renseigner **au plus 4 points de chaque côté**, chacun **110 caractères maximum**
(2 lignes). Le gabarit tronque au-delà (4 points, 2 lignes avec « … »), donc
l'essentiel doit venir en premier.

Le paragraphe de synthèse (`verdict.resume`) commence par une **brève description
du bien** (type, surface, nombre de pièces, étage, extérieur ou jardin, annexes,
état général), puis enchaîne sur le message clé (emplacement, écart de prix, risques
majeurs, recommandation). **Au plus 4 phrases, ~400 caractères** : le gabarit
tronque à 4 lignes pour garantir que toute la page 1 (jusqu'au DPE) tient sur une
seule page. Faire court et dense.

---

## Schéma JSON de la fiche A4 PDF

Le script `scripts/generer_fiche_pdf.py` lit un JSON conforme à ce schéma. Tous
les champs texte sont libres ; renseigner les inconnus par « non communiqué »
plutôt que d'inventer. Le script calcule lui-même la criticité (v × i) et les
couleurs.

```json
{
  "meta": {
    "date": "2026-07-16",
    "auteur": "Agent Immobilier, conseiller d'acquéreur sans conflit d'intérêt"
  },
  "bien": {
    "adresse": "12 rue des Lilas, 00000 Villexemple",
    "secteur": "Centre-ville",
    "type": "Appartement 2 pièces",
    "surface_m2": 42.7,
    "pieces": 2,
    "etage": "1er",
    "annee": "avant 1949",
    "dpe": "G",
    "ges": "G",
    "charges": "170 €/mois",
    "taxe_fonciere": "941 €/an",
    "copropriete": "10 lots, sans procédure",
    "annexes": "Cave"
  },
  "prix": {
    "affiche": "350 000 €",
    "prix_m2_affiche": "8 200 €/m²",
    "reference_marche": "7 000 à 8 200 €/m² (DVF secteur)",
    "valeur_defendable": "180 000 € (plafond 190 000 €)",
    "cible_negociation": "300 000 à 320 000 €",
    "decote": "9 à 14 %"
  },
  "verdict": {
    "feu": "orange",
    "note_sur_100": 58,
    "resume": "Emplacement rare, mais prix affiché au niveau d'un bien rénové pour un logement classé G à rénover intégralement."
  },
  "points_forts": ["Emplacement rare et recherché", "Séjour exposé sud"],
  "points_faibles": ["DPE G à rénover", "Prix au-dessus de la valeur défendable"],
  "risque_global": "Élevé",
  "risques": [
    {"libelle": "Retrait-gonflement des argiles", "famille": "Naturel", "v": 4, "i": 4, "commentaire": "Aléa fort, plusieurs sécheresses classées CATNAT"},
    {"libelle": "DPE G (passoire)", "famille": "Bâti", "v": 5, "i": 4, "commentaire": "Rénovation énergétique lourde, restriction de location"},
    {"libelle": "Remontée de nappe", "famille": "Naturel", "v": 3, "i": 2, "commentaire": "Cave humide à surveiller"}
  ],
  "vigilance": [
    "Argiles en aléa fort : vérifier fissures et fondations",
    "DPE G : coût de sortie de passoire à provisionner",
    "Copropriété ancienne : demander les PV d'AG et le fonds de travaux"
  ],
  "negociation": {
    "leviers": ["Classe G", "Travaux incompressibles", "Prix affiché au-dessus du marché réel"],
    "argument_cle": "Payer le prix affiché reviendrait à acheter une valeur rénovée que le bien n'a pas encore, puis à financer les travaux une seconde fois."
  },
  "sources": [
    {"nom": "Annonce (SeLoger)", "url": "https://www.seloger.com/annonces/...", "detail": "Annonce consultée le 16/07/2026"},
    {"nom": "Géorisques", "url": "https://www.georisques.gouv.fr/", "detail": "État des risques à l'adresse"},
    {"nom": "DVF (DGFiP / Etalab)", "url": "https://app.dvf.etalab.gouv.fr/", "detail": "Transactions signées, avril 2026"}
  ],
  "avertissement": "Analyse indépendante d'aide à la décision. Ni expertise judiciaire, ni conseil en investissement, ni avis juridique."
}
```

Champs `bien` (identité) : garder chaque valeur **courte, 70 caractères maximum**
(elle s'affiche sur 2 lignes au plus, le gabarit tronque avec « … » au-delà).
Placer l'essentiel en tête (ex. « Sans PPT ni DTG, règl. 1965 » plutôt qu'une
longue phrase) ; le détail complet va dans la section copropriété ou l'étude, pas
dans la grille d'identité.

Champs DPE : renseigner `dpe` et `ges` par la seule lettre de classe (A à G), et
`dpe_kwh` / `ges_kgco2` par la valeur chiffrée. Le script reste tolérant (il sait
extraire la lettre et le nombre d'une chaîne comme « D (188 kWh/m²/an) »), mais la
saisie propre est préférable. La bande correspondante est surlignée sur l'étiquette
graphique.

**Analyse : coût de revient, score, historique DVF.** Trois champs optionnels
ajoutent une page « Coût de revient et score du bien » après l'étude de risques :

- `cout_revient` : `{prix_achat, frais, travaux, aleas, vat, note?}` (nombres €).
  Le script trace une **cascade** prix + frais + travaux + aléas = coût de revient
  total, comparée à la valeur après travaux (`vat`). C'est « ne pas payer deux
  fois » rendu visuel.
- `radar` : liste de `{axe, note}` (note de 0 à 10) sur 3 à 8 axes (emplacement,
  état, prix, risques, copropriété, énergie…). Trace une toile d'araignée.
- `dvf_historique` : liste de `{date, prix, detail}` = ventes passées du bien ou de
  l'immeuble (DVF), rendues en tableau. N'y mettre que des **mutations réelles**.

**Sources et appels de note.** `sources` est une liste d'objets
`{nom, url, detail}` (une chaîne seule reste acceptée). Règles :

- **La première source est toujours l'annonce elle-même** (nom du portail + lien
  direct), suivie des sources officielles (Géorisques, DVF, PLU/ABF, DPE, etc.).
- **Ne jamais répéter une source** : le script déduplique par nom et numérote
  automatiquement (1, 2, 3…). Une source apparaît une seule fois.
- Renseigner l'`url` **exacte** dès que la source est en ligne : le lien doit
  pointer **directement sur la ressource citée** (la page précise de l'annonce, le
  rapport Géorisques de l'adresse, la recherche DVF du secteur, le DPE concerné),
  **jamais la simple page d'accueil du domaine**. Elle devient un lien cliquable
  dans la section « Sources et références » (générée sur sa propre page).

Pour **citer** une source dans le texte, écrire l'appel de note `[n]` (n = numéro
de la source dans la liste) juste après la donnée concernée ; le gabarit le rend en
exposant bleu. Les appels `[n]` sont convertis dans : synthèse, points forts et
faibles, référence marché (prix), commentaires de l'étude de risques, points de
vigilance, leviers et argument de négociation, prix et risques de l'étude de marché.
Exemple : `"Aléa fort argiles[2] ; fissures à vérifier"` avec la source 2 =
Géorisques.

**Aide à la décision (questions au vendeur).** Le champ `aide_decision` génère une
section « à remplir » sur sa propre page : l'acheteur y répond directement sur le
PDF (une ligne pointillée suit chaque question). C'est une liste de groupes
thématiques :

```json
"aide_decision": [
  {"theme": "Copropriété", "questions": [
    "Montant réel des charges annuelles et ce qu'elles couvrent ?",
    "Travaux votés ou à prévoir (PPT, ravalement, toiture) et quote-part ?",
    "Fonds de travaux disponible et procédures en cours ?"
  ]},
  {"theme": "Bâti et travaux", "questions": [
    "Nature et date des derniers travaux ; factures et garanties ?",
    "Diagnostics complets fournis (DPE, amiante, plomb, élec, gaz) ?"
  ]}
]
```

Adapter les questions au bien et aux risques identifiés (reprendre les points de
vigilance sous forme de questions). Thèmes utiles : copropriété, bâti et travaux,
diagnostics et énergie, environnement et géorisques, urbanisme, juridique et vente,
charges et fiscalité. Les appels de note `[n]` y sont aussi rendus en exposant.

**Page de notes.** Une dernière page « Notes » remplie de lignes pointillées est
ajoutée automatiquement (`notes_page`, activé par défaut ; mettre à `false` pour la
retirer).

Recommandations : lister les risques les plus critiques d'abord (le script les
retrie par criticité), viser 4 à 8 risques sur la fiche pour rester lisible (le
détail exhaustif va dans l'étude complète), et 3 à 5 points de vigilance.

### Bloc `plan` optionnel : plan du bien dans le PDF

Ajouter une clé `plan` dessine un **plan du bien** dans la fiche (après le bloc
prix). Deux modes :

- **`"mode": "estimation"`** (défaut) : schéma d'agencement estimé d'après
  l'annonce, les photos et les documents. Coordonnées sur une grille relative,
  surfaces préfixées « ~ », rendu explicitement **non métré, non contractuel**.
  À utiliser quand aucun plan coté n'est disponible.
- **`"mode": "reproduction"`** : reproduction d'un plan coté déjà fourni.
  Coordonnées **en mètres** (dessin à l'échelle), cotes `L × l` affichées par
  pièce, mètre-étalon tracé. À utiliser uniquement quand un plan à l'échelle
  existe : ne jamais inventer des cotes en mode reproduction.

Chaque pièce est un rectangle positionné `(x, y, w, h)`, `x` vers la droite, `y`
vers le bas. C'est le modèle qui calcule un agencement cohérent et non
chevauchant ; le script se contente de dessiner. `type` colore la pièce (`jour`,
`nuit`, `eau`, `service`, `circulation`, `exterieur`). `fenetres` place des
ouvertures sur les arêtes exposées (`N`, `S`, `E`, `O`, en repère écran). `nord`
oriente la boussole (`haut` par défaut, ou `bas`/`gauche`/`droite`).

```json
{
  "plan": {
    "mode": "estimation",
    "nord": "haut",
    "source": "Estimé d'après l'annonce, 9 photos et le mesurage Carrez (42,7 m²)",
    "pieces": [
      {"nom": "Chambre", "x": 0, "y": 0, "w": 4.0, "h": 2.6, "surface": "11 m²", "type": "nuit", "fenetres": ["N"]},
      {"nom": "Cuisine", "x": 4.0, "y": 0, "w": 2.0, "h": 2.6, "surface": "6 m²", "type": "service", "fenetres": ["N"]},
      {"nom": "Salle de bains", "x": 6.0, "y": 0, "w": 2.0, "h": 2.6, "surface": "5 m²", "type": "eau", "fenetres": ["E"]},
      {"nom": "Entrée", "x": 0, "y": 2.6, "w": 1.4, "h": 3.0, "surface": "4 m²", "type": "circulation", "fenetres": []},
      {"nom": "Séjour", "x": 1.4, "y": 2.6, "w": 6.6, "h": 3.0, "surface": "18 m²", "type": "jour", "fenetres": ["S", "E"]}
    ],
    "legende": ["Bien non traversant", "Cuisine séparée"]
  }
}
```

En mode `reproduction`, `w`/`h` sont les dimensions réelles en mètres (le libellé
affiche alors `L × l m`) ; `surface` sert surtout au mode estimation. Placer les
`fenetres` sur les arêtes qui donnent réellement sur l'extérieur. Le bloc est
entièrement optionnel : absent, la fiche n'a pas de plan. Toujours rappeler, dans
le message ou la légende, qu'un schéma estimé n'est pas un relevé.

### Bloc `environnement` optionnel : commerces et équipements alentours

Ajouter une clé `environnement` insère, **sous le plan du bien**, la section
« Commerces et équipements alentours » : les lieux sont **regroupés par type**
(Transports, Commerces, Écoles, Santé, Parcs et loisirs), chaque groupe avec une
**icône** de couleur, listant les lieux (nom + distance). Entièrement autonome,
**aucune carte ni réseau**.

```json
{
  "environnement": {
    "pois": [
      {"nom": "Gare de Bourges", "categorie": "transport", "distance": "400 m"},
      {"nom": "Carrefour City", "categorie": "commerce", "distance": "150 m"},
      {"nom": "École Jean-Jaurès", "categorie": "ecole", "distance": "200 m"},
      {"nom": "Pharmacie du Centre", "categorie": "sante", "distance": "180 m"}
    ]
  }
}
```

Chaque lieu a une `categorie` (`transport`, `commerce`, `ecole`, `sante`, `parc` ;
sinon rangé dans « Autres »), un `nom` qui doit être le **nom exact du lieu**
(« Carrefour City », « Gare de Bourges »), jamais une catégorie générique, et une
`distance` (à pied de préférence). Viser une **dizaine de lieux** parmi les plus
utiles. Ne renseigner que des lieux **réels et vérifiés**.

### Bloc `marche` optionnel : étude de marché dans le PDF (Fonction 5)

Ajouter une clé `marche` au JSON déclenche une **page d'étude de marché** en fin
de fiche (nouvelle page). Elle rend la Fonction 5 sous forme standardisée. Le bloc
est entièrement optionnel : sans lui, la fiche reste une fiche bien classique. On
peut aussi produire une fiche centrée sur le marché en fournissant un JSON minimal
(identité sommaire) accompagné d'un bloc `marche` complet.

```json
{
  "marche": {
    "perimetre": "Villexemple (00000), centre-ville",
    "date_donnees": "DVF millésime avril 2026 · INSEE 2023 · Observatoire des loyers 2025",
    "tendance": {
      "direction": "stable",
      "evolution_3_ans": "-3 %",
      "evolution_5_ans": "+7 %",
      "evolution_10_ans": "+38 %",
      "volume_transactions": "≈ 950 ventes/an",
      "delai_vente": "≈ 95 jours",
      "dynamique": "Marché d'acheteurs sur l'ancien à rénover"
    },
    "profil": {
      "population": "85 200 hab.",
      "demographie": "Stable",
      "emploi": "Tertiaire, administration, tourisme",
      "attractivite": "Forte",
      "desserte": "RER C, Transilien U et N, A86/A13",
      "socio": "Ménages aisés, 62 % de propriétaires"
    },
    "prix": [
      {"secteur": "Centre-ville", "typologie": "Appartement à rénover", "prix_m2_median": "5 900 €/m²", "fourchette": "5 000 à 6 800 €/m²", "volume": "≈ 60/an", "estimation_portail": "7 200 €/m²", "tendance": "baisse"}
    ],
    "evolution": [
      {"annee": 2020, "prix_m2": 6800}, {"annee": 2022, "prix_m2": 7000}, {"annee": 2024, "prix_m2": 6600}
    ],
    "boxplot": [
      {"label": "Ancien rénové", "min": 6000, "q1": 6800, "median": 7400, "q3": 8000, "max": 8600, "portail": 8300},
      {"label": "Ancien à rénover", "min": 4600, "q1": 5300, "median": 5900, "q3": 6500, "max": 7000, "bien": 8200}
    ],
    "locatif": {
      "loyer_m2": "21 à 25 €/m²",
      "rendement_brut": "3,0 à 3,6 %",
      "tension": "Forte (zone tendue)",
      "encadrement": "Non applicable"
    },
    "segments_privilegier": ["Ancien à rénover en secteur coté"],
    "segments_eviter": ["Ancien affiché au prix du rénové"],
    "risques_marche": ["Écart marqué prix affichés / prix signés"],
    "conclusion": {
      "posture": "plutot_acheteur",
      "defendable_m2_min": 5000, "defendable_m2_max": 6000,
      "fourchette_m2_defendable": "5 000 à 6 000 €/m² pour un 2-3 pièces à rénover",
      "kpis": [
        {"label": "Délai de vente", "valeur": "≈ 95 j"},
        {"label": "Évolution 3 ans", "valeur": "-3 %"},
        {"label": "Tension", "valeur": "Forte"},
        {"label": "Écart portail/réel", "valeur": "+18 %"}
      ],
      "plan_action": [
        "Viser l'ancien à rénover en secteur coté, sous 6 000 €/m²",
        "Demander une décote de 25 à 35 % sur le prix affiché",
        "Sécuriser DPE, copropriété et plancher sur porche avant l'offre"
      ],
      "pouvoir_negociation": "Modéré à fort sur l'ancien à rénover",
      "recommandation": "Viser l'ancien à rénover sous 6 000 €/m² et faire jouer le DPE."
    }
  }
}
```

Champ `tendance.direction` et `prix[].tendance` : valeurs `hausse`, `stable` ou
`baisse` (le script affiche une pastille flèche + couleur : orange en hausse, vert
en baisse, gris stable, du point de vue de l'acheteur) ; une valeur libre inconnue
est affichée telle quelle en neutre. Tous les autres champs sont du texte libre ;
`locatif` peut être omis (usage résidence principale). Renseigner honnêtement les
inconnus plutôt que d'inventer. Prix DVF réels d'abord, estimations de portails en
colonne « Est. portail » pour mémoire seulement.

**Graphiques (SVG générés).** Deux champs optionnels produisent des graphiques dans
l'étude de marché :

- `evolution` : liste de `{annee, prix_m2}` (nombres) pour une **courbe** du prix
  médian au m² dans le temps.
- `boxplot` : liste de `{label, min, q1, median, q3, max, portail?, bien?}` (nombres
  €/m²) pour des **boîtes à moustache** par secteur ou typologie. `portail` place un
  losange (estimation portail), `bien` un trait rouge (prix au m² du bien étudié)
  sur la distribution.

Les quartiles doivent être des **statistiques DVF réelles** (Q1, médiane, Q3, min,
max), jamais inventées. Si on ne dispose pas des quartiles, **omettre le boxplot**
(ou ne fournir que la courbe) plutôt que de fabriquer une distribution.

**Approfondir les DVF.** Quatre champs optionnels ajoutent une section « comparables
et distribution » à l'étude de marché :

- `comparables` : liste de `{secteur, surface, prix, prix_m2, date, distance}` = 4 à
  6 **ventes DVF réelles** retenues comme comparables. Rendu en tableau. C'est la
  base qui fonde la valeur défendable ; n'y mettre que des mutations vérifiées.
- `cible` : liste (du plus proche au plus lointain) de `{label, prix_m2, volume}`
  par anneau de distance (ex. `0-250 m`, `250-500 m`, `500-1000 m`). Trace une cible
  concentrique, le bien au centre. Chaque anneau doit être chiffré (médiane + volume).
- `scatter` : `{x_label, points: [{x, y}], bien: {x, y}}` (y = €/m², x = surface ou
  année). Nuage de points des ventes, le bien mis en évidence.
- `histogramme` : liste de `{tranche, ventes, bien?}` = répartition des ventes par
  tranche de €/m² ; mettre `"bien": true` sur la tranche du bien étudié (surlignée).

Toutes ces données viennent de **ventes DVF réelles** ; ne jamais fabriquer de
points, d'anneaux ou de comparables fictifs. Omettre un champ si la donnée manque.

**Conclusion enrichie.** Le bloc `conclusion` accepte, en plus des champs texte
(`fourchette_m2_defendable`, `pouvoir_negociation`, `recommandation`) :

- `posture` : posture du marché, mot-clé (`acheteur`, `plutot_acheteur`,
  `equilibre`, `plutot_vendeur`, `vendeur`) ou nombre 0 (acheteur) à 100 (vendeur).
  Affiche un curseur favorable acheteur → vendeur avec un libellé.
- `defendable_m2_min` / `defendable_m2_max` (nombres €/m²) : le script les multiplie
  par la surface du bien (`bien.surface_m2`) pour afficher un **prix total défendable
  pour ce bien précis**, comparé au prix affiché avec l'écart en %.
- `kpis` : liste de `{label, valeur}` (2 à 4 tuiles), tableau de bord du marché
  (délai de vente, évolution, tension, écart portail/réel…).
- `plan_action` : liste de 2 à 4 actions concrètes (segment à viser, décote à
  demander, points à sécuriser avant l'offre).

Les appels de note `[n]` fonctionnent dans le libellé de posture, le plan d'action,
le pouvoir de négociation et la recommandation.

---

## Structure de l'étude complète

Document argumenté, dans l'esprit d'une étude de valeur vénale, généralisable à
tout bien :

1. **Synthèse exécutive** : objet, verdict, valeur d'acquisition défendable,
   message clé en trois lignes.
2. **Le bien et son environnement** : localisation, desserte, description,
   atouts et contraintes permanents (séparés des défauts réparables).
3. **Étude de risques (vraisemblance × impact)** : tableau trié, matrice 5 × 5,
   synthèse des risques critiques et élevés, plan d'action.
4. **Géorisques** : risques naturels et technologiques à l'adresse, avec niveaux
   et conséquences concrètes.
5. **Urbanisme et patrimoine** : zonage PLU/PLUi, SPR/PSMV, avis ABF, servitudes,
   projets à proximité.
6. **État technique et diagnostics** : DPE, amiante, plomb, électricité, gaz,
   structure, humidité, assainissement, surface.
7. **Copropriété** : santé financière, travaux votés et à venir, gouvernance,
   analyse des PV d'AG et du règlement.
8. **Marché et valeur de référence** : transactions réelles DVF, comparables,
   tendances, écart aux estimations en ligne.
9. **Valeur d'acquisition défendable** : application de la méthode
   (`methode-valeur.md`), avec fourchettes et plafond.
10. **Stratégie de négociation** : cible, décote, leviers, argumentaire.
11. **Documents à réclamer et questions à poser** : au vendeur, à l'agence, au
    syndic.
12. **Avertissement**.

Distinguer toujours les faits (sourcés), les analyses, et les hypothèses. Pour un
livrable soigné en PDF ou Word, préparer d'abord le contenu, puis lire le SKILL.md
de la skill `pdf` ou `docx`.

---

## Structure de l'étude de marché d'une localité (Fonction 5)

Document structuré, à l'échelle d'un marché local et non d'un bien. Toujours
dater et citer le millésime des données (DVF, période).

1. **Synthèse et recommandation d'acheteur** : périmètre et segment étudiés,
   niveau de prix de référence, tendance en une phrase, où viser et quel pouvoir
   de négociation, en trois à cinq lignes.
2. **Périmètre et profil de la localité** : échelle retenue, population et
   démographie, emploi et attractivité, desserte et projets structurants, profil
   socio-économique, les moteurs de fond de la valeur.
3. **Prix réels par typologie et secteur** : tableau des prix au m² signés
   (médiane et fourchette), volumes de ventes, confrontés aux estimations des
   portails (citées pour mémoire). Source DVF en priorité.
4. **Tendance et liquidité** : évolution des prix sur 3, 5, 10 ans si disponible,
   dynamique récente, nombre de transactions, délai de vente moyen.
5. **Marché locatif** (si pertinent) : loyers au m², rendement brut indicatif par
   typologie, tension locative, encadrement éventuel. Rappeler que le rendement
   brut ignore charges, vacance et fiscalité.
6. **Micro-marchés et segmentation** : écarts internes, sous-secteurs cotés,
   typologies sur- ou sous-cotées, segments à privilégier ou à éviter.
7. **Risques de marché** : dépendance mono-employeur, suroffre neuve, géorisques
   à l'échelle communale, part de passoires énergétiques, saisonnalité, ce qui
   pèse sur la revente.
8. **Conclusion chiffrée** : fourchette de prix au m² défendable pour le segment
   ciblé, recommandation de timing et de négociation, suite proposée (recherche
   de biens ou étude complète sur une adresse).
9. **Avertissement**.

Tableau de prix recommandé :

| Secteur / quartier | Typologie | Prix/m² médian réel | Fourchette réelle | Volume | Estimation portail (pour mémoire) | Tendance |
|---|---|---|---|---|---|---|

---

## Format du shortlist de recherche (Fonction 1)

Rappeler d'abord le mandat de recherche (critères durs et souhaits), puis un
tableau comparatif :

| Bien | Annonce | Localisation | Prix | Surface | Prix/m² | Pièces | DPE | Signal risque | Avis |
|---|---|---|---|---|---|---|---|---|---|

La colonne « Annonce » porte, sur **chaque ligne**, un lien cliquable vers
l'annonce (format Markdown `[Voir l'annonce](url)`). C'est obligatoire : sans lien,
l'acheteur doit re-chercher chaque bien à la main. Si l'URL directe est
introuvable, indiquer le portail et la référence de l'annonce, et le signaler.

L'« Avis » classe chaque bien : coup de cœur sous réserve, à creuser, ou à écarter
(avec la raison). Ajouter, sous le tableau, les 2 ou 3 meilleurs candidats
commentés (chacun avec son lien), la mention de la date de recherche et de la
volatilité des annonces, et l'offre de produire une fiche A4 PDF ou une étude
complète sur les biens retenus.
