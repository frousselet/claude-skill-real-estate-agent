# Protocole de construction de la base DVF

Ce protocole normalise la façon de bâtir la base de mutations qui fonde la valeur
d'un bien. Il s'applique dès qu'une adresse (confirmée ou supposée) est connue :
étude complète (Fonction 4) et, à l'échelle d'un secteur, étude de marché
(Fonction 5).

Son principe directeur : **on ne supprime jamais silencieusement une mutation**.
Toute exclusion est explicite et motivée ; les valeurs extrêmes authentiques
restent dans la base brute et ne sont écartées, le cas échéant, que par un test
statistique documenté (Tukey), pas au jugé.

## 1. Périmètre de collecte

**Période.** Du 1er janvier 2023 au 31 décembre 2025, plus les mutations 2026 si
le millésime publié les couvre. Toujours indiquer le millésime DVF utilisé et sa
date de publication (mise à jour semestrielle, avril et octobre).

**Typologie.** Maisons ou appartements uniquement, et **du même type que le bien
étudié** : si l'annonce porte sur une maison, ne retenir que des maisons ; si
c'est un appartement, uniquement des appartements. Une observation = **une seule
mutation résidentielle comparable**.

**Surface de référence.** **±20 %** autour de la surface du bien étudié, en
proportion et non en mètres carrés absolus : une tolérance fixe serait trop lâche
sur un studio et trop serrée sur une grande maison. Exemple : pour un bien de
42,7 m², le panel retient les mutations de 34 à 51 m².

C'est une fourchette volontairement serrée. Elle prime sur la tolérance large
(±25 à 30 %) mentionnée dans `methode-valeur.md`, qui ne sert que de repli quand
le marché est trop mince pour produire un effectif exploitable. Si l'on élargit,
le dire et afficher les deux effectifs. Toujours rappeler la fourchette en mètres
carrés effectivement appliquée, pas seulement le pourcentage.

**Exclusions structurelles de la collecte** :

- mutations comprenant plusieurs appartements ou plusieurs maisons ;
- mutations mixtes comprenant un local commercial ou professionnel ;
- ventes dont le prix porte conjointement sur le logement et un actif non
  comparable (fonds de commerce, terrain à bâtir, immeuble entier) ;
- mutations dont l'assiette du prix ou la surface ne peut pas être reconstituée
  de façon fiable.

Les caves, greniers, garages et autres dépendances accessoires ne sont **pas**
un motif d'exclusion : on les conserve, mais on les **signale** (colonne nombre
de dépendances) car ils gonflent la valeur foncière sans surface habitable
correspondante.

## 2. Panels géographiques

Distance mesurée à vol d'oiseau depuis l'adresse (confirmée ou supposée) du bien.

| Panel | Définition | Rôle |
|---|---|---|
| **A** | distance ≤ 250 m | Micro-secteur, le plus comparable |
| **B** | distance > 250 m et ≤ 500 m | Proximité élargie, épaissit l'effectif |
| **R** | ventes de biens **neufs** (dont VEFA), isolées de A et B quelle que soit leur distance | Segment de marché distinct, jamais mélangé à l'ancien |
| **Direct** | mutations à la **même adresse ou dans le même immeuble** | Comparable le plus fort, à traiter à part |

Le panel R existe pour que le neuf ne contamine pas les statistiques de
l'ancien : ses prix au m² relèvent d'un autre marché (frais réduits, garanties,
absence de travaux). Il se calcule et se présente séparément ; il n'entre ni dans
A, ni dans B, ni dans A+B.

Le panel Direct se retient **même si sa surface sort légèrement de la fourchette
±20 %** : la valeur d'un lot du même immeuble informe plus qu'un lot exact
situé trois rues plus loin. Il s'analyse séparément et n'est pas fondu dans les
statistiques de A.

## 3. Traitement des surfaces

DVF publie une surface réelle bâtie (SRB) qui n'est pas la surface Carrez. Les
deux se traitent en parallèle, jamais par substitution :

- afficher **systématiquement** la surface DVF/SRB et la surface Carrez quand
  elle est disponible ;
- calculer **les deux** prix au m² ;
- **ne jamais** remplacer automatiquement la surface DVF par la Carrez ;
- **signaler tout écart supérieur à 10 %** entre les deux surfaces et examiner la
  mutation individuellement (lot mal ventilé, dépendance comptée, erreur de
  saisie) ;
- tenir une colonne **prix/m² retenu** pour l'analyse, avec sa **justification**
  en clair (« Carrez retenue, écart 14 % expliqué par une cave incluse en SRB »).

## 4. Colonnes de la base

Chaque mutation produit une ligne, avec ces colonnes dans cet ordre :

`id_mutation` · `date` · `adresse` · `valeur foncière` · `surface DVF/SRB` ·
`surface Carrez` · `prix/m² DVF` · `prix/m² Carrez` · `écart de surface` ·
`nombre d'appartements` · `nombre de dépendances` · `nombre de lots` ·
`distance exacte` · `panel (A/B/R/direct)` · `prix/m² retenu` ·
`statut (conservé/exclu)` · `motif`.

La colonne `motif` est renseignée pour toute ligne exclue, et pour toute ligne
conservée qui appelle une réserve (écart de surface, dépendances nombreuses,
prix atypique conservé).

## 5. Statistiques par panel

Calculer **séparément** pour A, B, **A+B** et R :

| Indicateur | Définition |
|---|---|
| N | effectif du panel |
| min, Q1, médiane, Q3, max | statistiques d'ordre sur le prix/m² retenu |
| seuil inférieur de Tukey | Q1 − 1,5 × (Q3 − Q1) |
| seuil supérieur de Tukey | Q3 + 1,5 × (Q3 − Q1) |
| moustache basse réelle | plus petite observation **supérieure ou égale** au seuil inférieur |
| moustache haute réelle | plus grande observation **inférieure ou égale** au seuil supérieur |
| observations atypiques | liste nominative des mutations hors des deux seuils |

Les seuils de Tukey sont des bornes théoriques ; les moustaches réelles sont des
valeurs observées. Les deux se présentent, car leur écart dit à quel point la
queue de distribution est peuplée.

**Fournir les résultats en double lecture** : avec, puis sans les observations
atypiques de Tukey. Une mutation authentique au prix très bas ou très élevé
**n'est pas exclue pour cette seule raison** : elle reste dans la base brute et
figure dans la lecture « avec outliers ». Un écart marqué entre les deux
lectures est en soi une information sur l'hétérogénéité du micro-marché.

Le panel Direct se commente ligne à ligne (effectif généralement trop faible pour
des quartiles).

## 6. Courbe de tendance dans le temps

La courbe d'évolution du prix au m² se construit avec **exactement les mêmes
critères de sélection que l'analyse** : même type de bien, surface ±20 %, panels
**A et B réunis**. Seule la période change : **5 ans glissants**, au lieu de la
fenêtre 2023-2025 des panels.

C'est ce qui rend la courbe lisible : une tendance calculée sur un autre
périmètre (toute la commune, toutes surfaces, toutes typologies) décrirait un
autre marché que celui des panels, et son inflexion ne dirait rien du bien
étudié. Point par année, prix médian au m² du panel A+B de l'année.

Si une année compte trop peu de mutations pour une médiane robuste (moins de 5),
le signaler sur la courbe ou en légende plutôt que de lisser silencieusement. Le
panel R (neuf) n'entre jamais dans la courbe de l'ancien.

## 7. Restitution

Trois livrables, toujours dans cet ordre :

1. **La base brute complète**, une ligne par mutation, colonnes de la section 4,
   panels compris, lignes exclues incluses avec leur statut.
2. **Le tableau statistique** par panel (A, B, A+B, R), en double lecture avec et
   sans outliers, plus la liste nominative des atypiques.
3. **La liste séparée des mutations exclues**, chacune avec son motif précis.

Puis l'interprétation : quel prix au m² le protocole retient pour la valeur après
travaux, sur quel panel il s'appuie, et pourquoi.

## 8. Alimentation de la fiche PDF

Les champs DVF du bloc `marche` (voir `fiche-etude.md`) se dérivent directement
de ce protocole :

- `cible` : anneaux `0-250 m` (panel A) et `250-500 m` (panel B), médiane et
  volume de chacun. Un anneau plus large ne s'ajoute que s'il a été collecté.
- `boxplot` : les quartiles réels par panel, jamais reconstitués.
- `comparables` : 4 à 6 lignes **conservées**, choisies d'abord dans le panel
  Direct puis dans A, jamais une ligne exclue.
- `scatter` et `histogramme` : les observations conservées, le bien étudié mis en
  évidence.
- `evolution` : la courbe de tendance de la section 6, un point par année sur
  5 ans, panel A+B aux mêmes critères de sélection.

Le panel R ne se mélange jamais aux graphiques de l'ancien ; s'il est présenté,
c'est comme série distincte et libellée.

Dans la fiche, ces éléments s'impriment **regroupés sous un même chapeau
« Analyses DVF »**, dans cet ordre : boîtes à moustache, comparables, cible et
nuage de points, répartition, historique DVF du bien, courbe de tendance. Les
lire d'affilée est ce qui permet de vérifier qu'ils racontent la même histoire ;
dispersés dans la fiche, ils invitent à en retenir un seul.

## 9. Quand la donnée manque

Si l'effectif d'un panel est trop faible pour des quartiles (indicativement moins
de 5 observations), le dire et donner les observations brutes plutôt que des
statistiques fragiles. Élargir la fourchette de surface ou le rayon est possible,
mais alors : l'annoncer, afficher l'effectif avant et après, et ne pas présenter
le résultat élargi comme équivalent au périmètre nominal.
