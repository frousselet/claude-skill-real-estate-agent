# Méthode de la valeur d'acquisition défendable

Cette méthode donne un prix, pas une impression. Elle protège l'acheteur contre
la principale erreur : payer aujourd'hui une valeur que le bien n'aura qu'après
travaux, puis financer ces travaux une seconde fois.

## Principe

La valeur d'acquisition défendable se construit à rebours de la valeur du bien
rénové, en retranchant tout ce que l'acheteur devra dépenser et supporter pour
atteindre cet état.

```
Valeur après travaux (VAT, d'après les prix réels de comparables rénovés)
  −  Travaux de remise à niveau (ordres de grandeur par poste)
  −  Aléas techniques (bâti ancien, structure, humidité, plomb, amiante)
  −  Incertitudes de copropriété (travaux collectifs probables)
  −  Coûts de portage (frais, immobilisation, maîtrise d'œuvre)
  =  Valeur économique stricte (état actuel)
  +  Prime bornée pour rareté / emplacement (justifiée et plafonnée)
  =  Valeur d'acquisition défendable
```

## Étape 1 : la valeur après travaux (VAT)

Partir des transactions réelles de biens comparables RÉNOVÉS dans le même
micro-secteur (DVF en France, sold comps ailleurs), pas des estimations de
portails. Ajuster pour les caractéristiques permanentes qui ne changeront pas
avec les travaux : étage, ascenseur, exposition, vis-à-vis, nuisances, qualité et
santé de la copropriété, absence de stationnement.

La VAT n'est pas le haut de fourchette du quartier : c'est ce que VAUDRAIT CE
bien-là, une fois rénové, avec ses contraintes permanentes. Retenir une
fourchette (basse, centrale, haute) plutôt qu'un point.

### Choisir des comparables valides (règle de comparabilité)

Un comparable mal choisi fausse toute l'évaluation. Ne retenir que des ventes DVF
réellement comparables au bien, sur ces critères :

En France, quand une adresse est connue, ces critères se déclinent en un
protocole opératoire complet (période, panels par distance, double surface
DVF/Carrez, seuils de Tukey, table des exclusions motivées) :
`references/protocole-dvf.md`. Il fait référence dès qu'on bâtit une base de
mutations ; les critères ci-dessous en sont la lecture qualitative.

- **Même type de bien que celui étudié.** Comparer à des ventes du **même type** que
  le bien : un appartement avec des appartements, une maison avec des maisons. Écarter
  les biens d'un autre type et les cas hors marché résidentiel courant (local
  commercial, château, terrain, parking, dépendance), dont le prix au m² n'a rien à
  voir. En France, s'appuyer sur le type de local DVF.
- **Surface et nombre de pièces proches.** On ne compare pas un 250 m² à un 50 m², ni
  un studio à un 4 pièces. Viser une fourchette serrée (**±20 %** autour de la
  surface du bien, règle du protocole DVF) et une typologie voisine (T2 avec T2/T3),
  car le prix au m² décroît avec la surface. Élargir à ±30 % seulement si
  l'effectif est trop faible, en signalant l'élargissement et les deux effectifs.
- **Même segment neuf / ancien et état comparable.** Ne pas mélanger neuf et ancien,
  ni un bien rénové et un bien à rénover : ce sont des marchés différents. Comparer à
  état équivalent, ou ajuster explicitement l'écart (et ne pas compter deux fois).
- **Emplacement et prestige.** Tenir compte des **adresses de prestige** : vue
  dégagée ou sur monument, étage élevé avec ascenseur, immeuble de standing, rue
  cotée. Ces atouts commandent une prime qui ne se transpose pas à un bien qui ne les
  a pas (et inversement, une adresse dévalorisée décote). Ne pas aligner un bien
  ordinaire sur une vente d'exception voisine.
- **Ventes récentes.** Privilégier le millésime le plus récent ; réajuster les ventes
  plus anciennes de l'évolution du marché depuis leur date.

Quand aucun comparable n'est parfait, en retenir plusieurs et **ajuster** poste par
poste (surface, étage, état, exposition), en explicitant chaque correction.

**Ne jamais écarter une vente au seul motif que son prix au m² surprend.** Une
mutation authentique très basse ou très haute reste dans la base brute ; les valeurs
aberrantes s'identifient statistiquement (méthode de Tukey, voir
`protocole-dvf.md`), pas à l'intuition, et toute exclusion est motivée par écrit.

## Étape 2 : les coûts à retrancher

**Travaux de remise à niveau.** Estimer en ordres de grandeur, poste par poste ou
au global. Repères France 2026, fourniture et pose comprises, à confirmer par
devis :

| Niveau de rénovation | Ordre de grandeur |
|---|---|
| Rafraîchissement (peintures, sols, petits travaux) | 300 à 600 €/m² |
| Rénovation moyenne (cuisine, salle de bains, électricité partielle) | 800 à 1 200 €/m² |
| Rénovation complète (tous corps d'état, réseaux, isolation) | 1 200 à 1 800 €/m² |
| Rénovation lourde ou haut de gamme | 1 800 à 2 800 €/m² et plus |

Postes indicatifs : électricité complète 80 à 120 €/m² ; cuisine équipée 5 000 à
15 000 € ; salle de bains 5 000 à 12 000 € ; menuiseries 500 à 1 000 € par
fenêtre ; isolation intérieure 50 à 120 €/m² ; ventilation VMC 2 000 à 6 000 €.
Toujours signaler que ces montants sont indicatifs et à confirmer par devis.

**Aléas techniques.** Provision pour les surprises du bâti ancien : structure,
humidité, présence de plomb ou d'amiante, sujétions patrimoniales. Typiquement
10 000 à 30 000 € selon l'ampleur, ou un pourcentage du budget travaux.

**Incertitudes de copropriété.** Provision pour les travaux collectifs probables
non encore chiffrés (toiture, ravalement, réseaux communs), surtout en l'absence
de PPT ou de DTG.

**Coûts de portage.** Frais de notaire (voir plus bas), maîtrise d'œuvre et
coordination, immobilisation pendant le chantier, double loyer éventuel.

## Étape 3 : la valeur économique stricte

VAT moins l'ensemble des coûts. C'est un plancher théorique : il suppose que
l'acheteur capte en décote la totalité du coût des travaux et des risques. En
pratique, sur un bien rare et bien situé, le vendeur conserve une part du pouvoir
de négociation.

## Étape 4 : la prime bornée et la valeur défendable

Ajouter, si justifié, une prime délibérée au-dessus de la valeur économique
stricte pour la rareté de l'emplacement ou la sécurisation d'un achat (par
exemple un locataire déjà en place qui évite un déménagement). Cette prime doit
rester bornée et explicitée. Fixer aussi un plafond absolu à ne pas dépasser :
au-delà, l'acheteur supporte une part excessive du coût de remise en état.

## Positionnement et négociation

Présenter clairement les repères, dans cet ordre :

| Repère | Rôle |
|---|---|
| Prix affiché par le vendeur | Point de départ de la discussion, pas sa conclusion |
| Valeur de référence une fois rénové (VAT) | Ce que le bien vaudra, pas ce qu'il vaut |
| Valeur économique stricte (état actuel) | Plancher théorique |
| Valeur d'acquisition défendable | La cible raisonnable, avec son plafond |

**Cible de négociation** : exprimer une fourchette et une décote en pourcentage
par rapport au prix affiché. **Leviers** : état réel et travaux incompressibles,
écart au prix réel du secteur (DVF), risques identifiés (criticité), coûts de
détention, contraintes de copropriété, délai de vente local. **Argumentaire** :
factuel, chiffré, jamais agressif. Le meilleur levier est la démonstration que le
prix demandé fait payer une valeur que le bien n'a pas encore.

## Frais et repères utiles (France)

- **Frais de notaire** : environ 7 à 8 % dans l'ancien, 2 à 3 % dans le neuf.
- **Règle de l'acquéreur avisé** : prix d'achat + frais + travaux ne doivent pas
  dépasser la valeur après travaux. Au-delà, on investit plus que ce que le bien
  vaudra.
- **Délai de vente** : un délai local long renforce le pouvoir de négociation de
  l'acheteur.

## À l'international

La logique est identique : partir des ventes réelles comparables (sold comps),
retrancher travaux et risques, ajouter une prime bornée. Adapter les repères de
coûts et de frais au pays. Toujours signaler que les ordres de grandeur de
travaux sont locaux et à confirmer.
