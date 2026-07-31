# Claude Skill : Agent Immobilier

> 🇫🇷 Cette skill est conçue pour le **marché immobilier français** : sources et
> méthodes françaises (DVF, Géorisques, PLU/ABF, diagnostics, copropriété).
>
> 🇬🇧 This skill is designed for the **French real estate market**: French data
> sources and methods (DVF, Géorisques, PLU/ABF, diagnostics, co-ownership). The
> rest of this README is in French.

Skill [Claude](https://claude.com/claude-code) qui met une expertise immobilière
**du côté de l'acheteur**. Elle n'est rémunérée par personne et n'a aucun intérêt à
ce que la vente se fasse : son seul objectif est que l'acquéreur achète le bon
bien, au prix le plus bas défendable, en connaissant tous les risques avant de
signer. C'est un second avis indépendant, complémentaire des conseils de l'agent ou
du notaire.

Sa méthode est factuelle : elle recoupe chaque annonce avec les sources officielles
et, surtout, avec les transactions réellement signées (DVF en France, ventes
comparables ailleurs), plutôt qu'avec les estimations des portails, souvent
au-dessus des prix réels.

## Les six fonctions

| L'utilisateur demande | Fonction |
| --- | --- |
| Cadrer son projet : critères, budget, secteurs (questionnaire interactif, PDF) | 6. Cahier des charges |
| Trouver / comparer des biens à vendre selon un cahier des charges | 1. Recherche |
| Une fiche récap A4 en PDF sur un bien | 2. Fiche A4 PDF |
| Les risques d'un bien (vraisemblance × impact, matrice) | 3. Étude de risques |
| Une analyse complète à partir d'une adresse (géorisques, PLU/ABF, DPE, copropriété, marché DVF, valeur, négociation) | 4. Étude complète |
| Le marché d'une commune ou d'un quartier (prix réels, tendances, locatif) | 5. Étude de marché |

Les fonctions s'enchaînent : le cahier des charges alimente la recherche, une étude
complète contient une étude de risques et peut produire une fiche.

## Utilisation

C'est une skill Claude. Elle se déclenche sur des demandes du type « analyse cette
annonce », « que vaut cet appartement », « quels risques pour ce bien »,
« prix de l'immobilier à … », « aide-moi à négocier ». Le comportement complet est
décrit dans [`SKILL.md`](SKILL.md).

Réponses dans la langue de l'utilisateur (français par défaut), adaptées au pays du
bien : socle France très détaillé (Géorisques, DVF, PLU/PSMV, ABF, diagnostics),
équivalents officiels à l'international.

## Générer une fiche A4 PDF

La **Fonction 2** produit une fiche standardisée d'une à deux pages, toujours
structurée à l'identique pour comparer les biens d'un coup d'œil. La mise en page
est fixée par le gabarit ; on ne remplit qu'un fichier de données JSON.

```bash
python3 scripts/generer_fiche_pdf.py chemin/vers/donnees.json chemin/vers/fiche.pdf
```

Un exemple complet et fictif est fourni : [`assets/fiche_exemple.json`](assets/fiche_exemple.json).

```bash
python3 scripts/generer_fiche_pdf.py assets/fiche_exemple.json fiche_exemple.pdf
```

**Dépendances** : `jinja2` (`pip install jinja2`) pour le rendu HTML, et pour le
PDF un moteur détecté automatiquement : Chromium headless (y compris les
navigateurs installés en `.app` sur macOS) ou `wkhtmltopdf`. Le rendu est toujours
à l'échelle 1, jamais dézoomé.

Le schéma JSON complet et toutes les options sont documentés dans
[`references/fiche-etude.md`](references/fiche-etude.md).

## Structure de la fiche PDF

La page 1 est une synthèse (verdict en jauge, points forts et faibles, prix en
trois valeurs, identité, DPE). Les pages suivantes sont organisées en **grandes
parties** (rang 1) regroupant des **sections** (rang 2) ; chaque partie commence
sur une nouvelle page :

1. **Le bien et son environnement** : caractéristiques et exposition, espaces et
   annexes, plan du bien, cadre de vie et nuisances, commerces alentours
2. **Copropriété** (ou lotissement) : santé financière, travaux, gouvernance, PV
   d'AG, règlement, documents
3. **Étude de marché** : profil de la localité, prix réels DVF, analyses DVF
   (boîtes à moustache, comparables, cible, histogramme), locatif, segments
4. **Risques et négociation** : étude vraisemblance × impact, points de vigilance,
   leviers de négociation
5. **Conclusion pour l'acheteur** : coût de revient réel contre valeur défendable,
   synthèse et recommandation chiffrée
6. **Sources et références**, **Aide à la décision** (questions au vendeur),
   **Notes**

Chaque bloc du JSON est optionnel : absent, sa section ne s'imprime pas. Le **plan
du bien** accepte des pièces rectangulaires ou polygonales (formes en L), avec murs
hiérarchisés, portes à arc de débattement, mobilier par type de pièce et boussole,
en mode estimation (non métré) ou reproduction (cotes réelles).

## Définir son cahier des charges (questionnaire interactif)

La **Fonction 6** cadre le projet avant de chercher : un entretien en sept blocs
(projet, budget, localisation, le bien, tolérances, rédhibitoires et arbitrages,
logistique), mené par blocs de 3 à 5 questions avec des options proposées, puis un
PDF standardisé de 5 à 6 pages. Elle vaut pour un achat comme pour une recherche de
location.

Le document contient la synthèse du projet (non négociables, rédhibitoires,
enveloppe et surface de cadrage, curseur d'arbitrage), le budget décomposé et la
capacité d'emprunt, les secteurs ciblés et les temps de trajet, les critères
pondérés par niveau (non négociable, important, souhaité), une **grille de notation
à remplir en visite**, la table des arbitrages décidés à froid, le calendrier, le
dossier et les questions à poser.

```bash
python3 scripts/generer_cdc_pdf.py chemin/vers/cahier.json chemin/vers/cahier.pdf
```

Deux exemples fictifs sont fournis, un par mode :

```bash
python3 scripts/generer_cdc_pdf.py assets/cdc_exemple.json cdc_achat.pdf
python3 scripts/generer_cdc_pdf.py assets/cdc_exemple_location.json cdc_location.pdf
```

La conduite de l'entretien, la banque de questions et le schéma JSON sont
documentés dans [`references/cahier-des-charges.md`](references/cahier-des-charges.md).

## Arborescence

```text
SKILL.md                       Comportement de la skill (les 6 fonctions, principes)
references/
  cahier-des-charges.md        Questionnaire, pondération, schéma JSON du cahier
  fiche-etude.md               Schéma JSON de la fiche, structure des études
  methode-valeur.md            Valeur d'acquisition défendable, DVF vs estimations
  protocole-dvf.md             Construction de la base DVF (panels, Tukey, exclusions)
  risques.md                   Catalogue des risques par famille, échelles V × I
  sources-donnees.md           Où trouver l'information, par pays
scripts/
  generer_fiche_pdf.py         Génère la fiche A4 PDF depuis un JSON
  generer_cdc_pdf.py           Génère le cahier des charges A4 PDF depuis un JSON
assets/
  fiche_template.html          Gabarit de la fiche (mise en page fixe)
  fiche_exemple.json           Exemple complet (données fictives)
  cdc_template.html            Gabarit du cahier des charges (mise en page fixe)
  cdc_exemple.json             Exemple de cahier des charges, mode achat
  cdc_exemple_location.json    Exemple de cahier des charges, mode location
```

## Packaging

Le paquet distribuable de la skill est `agent-immobilier.zip` (artefact non
versionné) : un dossier `agent-immobilier/` contenant `SKILL.md`, `references/`,
`scripts/` et les gabarits `assets/*.html`.

Pousser un tag de version `vX.X.X` (ex. `v1.0.0`) déclenche le workflow
[`.github/workflows/release.yml`](.github/workflows/release.yml), qui reconstruit ce
zip et le publie dans une Release GitHub :

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Principes directeurs

1. **Primauté des faits** : chaque affirmation est sourcée ou présentée comme
   hypothèse, jamais péremptoire.
2. **Les prix réels priment sur les estimations** : les transactions signées (DVF)
   sont la référence, pas les modélisations des portails.
3. **Séparer le permanent du réparable** : l'emplacement, l'étage, l'exposition ne
   se valorisent pas comme la cuisine ou le DPE.
4. **Ne jamais compter deux fois** : un défaut est soit dans le prix, soit dans le
   budget travaux, jamais dans les deux.
5. **Toujours conclure par un chiffre et une action** : une valeur défendable, une
   cible de négociation, les prochaines vérifications.
6. **Dire ce qu'on ignore** : l'absence d'information est elle-même un facteur de
   risque.

## Avertissement

Cette skill est une aide à la décision indépendante. Elle ne constitue ni une
expertise judiciaire, ni un conseil en investissement, ni un avis juridique, ni un
diagnostic réglementaire. La décision finale et le prix offert relèvent du seul
acquéreur, qui doit faire confirmer les points déterminants par des professionnels
(notaire, diagnostiqueur, bureau d'études, avis de valeur local).
