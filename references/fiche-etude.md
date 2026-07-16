# Formats de restitution : fiche, étude, shortlist

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
    "adresse": "15 rue Sainte-Adélaïde, 78000 Versailles",
    "secteur": "Quartier Notre-Dame",
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
  "sources": ["Géorisques", "DVF (DGFiP / Etalab)", "Annonce", "DPE"],
  "avertissement": "Analyse indépendante d'aide à la décision. Ni expertise judiciaire, ni conseil en investissement, ni avis juridique."
}
```

Champs DPE : renseigner `dpe` et `ges` par la seule lettre de classe (A à G), et
`dpe_kwh` / `ges_kgco2` par la valeur chiffrée. Le script reste tolérant (il sait
extraire la lettre et le nombre d'une chaîne comme « D (188 kWh/m²/an) »), mais la
saisie propre est préférable. La bande correspondante est surlignée sur l'étiquette
graphique.

Recommandations : lister les risques les plus critiques d'abord (le script les
retrie par criticité), viser 4 à 8 risques sur la fiche pour rester lisible (le
détail exhaustif va dans l'étude complète), et 3 à 5 points de vigilance.

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

## Format du shortlist de recherche (Fonction 1)

Rappeler d'abord le mandat de recherche (critères durs et souhaits), puis un
tableau comparatif :

| Bien | Localisation | Prix | Surface | Prix/m² | Pièces | DPE | Signal risque | Avis |
|---|---|---|---|---|---|---|---|---|

L'« Avis » classe chaque bien : coup de cœur sous réserve, à creuser, ou à écarter
(avec la raison). Ajouter, sous le tableau, les 2 ou 3 meilleurs candidats
commentés, la mention de la date de recherche et de la volatilité des annonces, et
l'offre de produire une fiche A4 PDF ou une étude complète sur les biens retenus.
