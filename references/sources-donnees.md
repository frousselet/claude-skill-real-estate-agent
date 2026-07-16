# Sources de données, par pays

Où chercher l'information fiable pour analyser un bien. Toujours privilégier les
sources officielles et les prix réels, dater chaque donnée, et recouper.

## France (socle détaillé)

### Risques
- **Géorisques** (georisques.gouv.fr) : risques naturels et technologiques à
  l'adresse, génère l'État des Risques et Pollutions (ERP). Retrait-gonflement
  des argiles, inondation, remontée de nappe, séisme, radon, ICPE, TMD, pollution.
- **Cavités et mouvements de terrain** : inventaires BRGM (Infoterre), Géorisques.
- **Sites pollués** : CASIAS (anciens sites industriels et de service), BASOL
  (sites appelant une action), SIS (secteurs d'information sur les sols).
- **Sismicité et radon** : zonages nationaux, intégrés à Géorisques.

### Prix réels et marché
- **DVF, Demandes de Valeurs Foncières** (app.dvf.etalab.gouv.fr, ou explore.data.gouv.fr,
  ou fichiers files.data.gouv.fr) : toutes les mutations signées chez le notaire,
  la référence la plus fiable. Prix, surface, date, adresse, parcelle. Mise à jour
  semestrielle (avril et octobre). C'est la base à citer en priorité.
- **Portails d'estimation** (MeilleursAgents, PAP, SeLoger, efficity) : utiles
  pour la tendance et le prix au m² indicatif du quartier, mais ce sont des
  modélisations, généralement 10 à 25 % au-dessus des prix réellement signés. À
  citer pour mémoire, jamais comme référence de valeur.
- **Notaires de France, indices INSEE** : tendances de marché, évolutions.

### Marché à l'échelle d'une localité (étude de marché, Fonction 5)
- **DVF** (voir ci-dessus) : agréger les mutations par commune, quartier et
  typologie pour des prix au m² médians et des volumes réels. La base de référence.
- **INSEE** (insee.fr, statistiques locales / dossier complet commune) :
  population, démographie, emploi, revenus, composition du parc de logements,
  part de résidences principales / secondaires / vacantes.
- **Observatoires locaux des loyers (OLL) et encadrement des loyers** : loyers de
  référence au m², zones tendues, plafonds là où l'encadrement s'applique (Paris,
  Lille, Lyon, etc.).
- **Notaires (bases BIEN / PERVAL), MeilleursAgents, SeLoger** : tendances et
  indices d'évolution ; modélisations à recouper avec DVF, jamais seules.

### Annonces (recherche)
SeLoger, Bien'ici, Leboncoin, PAP, Logic-Immo, Green-Acres, et les sites
d'agences locales.

### Urbanisme et cadastre
- **Géoportail de l'Urbanisme** (geoportail-urbanisme.gouv.fr) : PLU/PLUi, PSMV,
  SPR, servitudes.
- **Cadastre** (cadastre.gouv.fr, ou Géoportail) : parcelles, contenance.
- **Atlas des patrimoines** : monuments historiques, périmètres de protection,
  covisibilité, avis ABF.
- **Mairie et service urbanisme** : certificat d'urbanisme, projets à proximité.

### Énergie et copropriété
- **Observatoire DPE (ADEME)** (observatoire-dpe-audit.ademe.fr) : consultation
  des DPE existants par adresse.
- **Registre national des copropriétés** (registre-coproprietes.gouv.fr) : fiche
  d'immatriculation, données financières de base.

### Diagnostics attendus du vendeur (DDT)
DPE, ERP (moins de 6 mois), amiante, plomb (CREP, avant 1949), électricité et gaz
(installations de plus de 15 ans), termites (selon zone), mesurage Carrez,
assainissement. En copropriété : PV d'AG (3 ans), règlement et état descriptif de
division, carnet d'entretien, pré-état daté, fonds de travaux.

## États-Unis

- **Risques naturels** : FEMA Flood Map Service Center (zones inondables), USGS
  (aléa sismique), EPA (radon zones), Cal Fire et équivalents (feux). 
- **Pollution** : EPA (Superfund, brownfields, TRI).
- **Prix réels et comparables** : registres publics de comté (recorded sales),
  Zillow, Redfin, Realtor.com, StreetEasy (New York) pour les « sold comps » et
  le prix au pied carré.
- **Urbanisme** : zoning de la municipalité, planning department.
- **Copropriété et charges** : HOA / condo board financials, reserve study,
  minutes, monthly dues, special assessments.
- **Fiscalité** : property tax du comté.
- **Obligations d'information** : seller's disclosure (varie par État, ex. NY
  Property Condition Disclosure, California TDS), title report, liens.

## Autre pays (méthode générique)

Quand le bien est ailleurs, reconstituer les quatre piliers :

1. **Registre officiel des risques** : chercher l'équivalent national ou régional
   (inondation, séisme, sols pollués, industriels). Termes utiles : « flood map »,
   « seismic hazard », « contaminated land register », « natural hazard disclosure ».
2. **Source de prix réels** : registre foncier ou cadastre transactionnel, sinon
   les portails dominants du pays pour les ventes conclues et le prix au m².
3. **Autorité d'urbanisme** : plan local de zonage, protections patrimoniales,
   servitudes.
4. **Informations obligatoires du vendeur** : diagnostics, disclosures, documents
   de copropriété ou d'association de propriétaires.

Toujours préciser le degré de fiabilité et la date. Si une donnée officielle est
introuvable, le dire et l'inscrire comme incertitude dans l'étude de risques.

## Note sur les outils

Si un connecteur immobilier (MCP) ou un navigateur piloté (Claude in Chrome) est
disponible, l'utiliser pour des données plus riches et à jour. Sinon, WebSearch
et WebFetch suffisent pour la plupart des sources officielles. Ne jamais
contourner une restriction d'accès : si une source est inaccessible, le signaler
et proposer une alternative.
