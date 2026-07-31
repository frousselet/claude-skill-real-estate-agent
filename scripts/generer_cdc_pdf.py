#!/usr/bin/env python3
"""
Génère un cahier des charges A4 PDF standardisé à partir d'un fichier JSON.

Usage :
    python3 scripts/generer_cdc_pdf.py cahier.json cahier.pdf
    python3 scripts/generer_cdc_pdf.py cahier.json cahier.pdf --template autre.html

Le cahier des charges est le mandat de recherche de l'acheteur (mode « achat »)
ou du candidat locataire (mode « location ») : projet, budget, localisation,
critères pondérés, grille de notation, arbitrages, calendrier.

Le schéma JSON attendu est décrit dans references/cahier-des-charges.md.
La mise en page est fixe : c'est le script qui garantit la standardisation.

Dépendances : identiques à generer_fiche_pdf.py (jinja2, puis chromium headless
ou wkhtmltopdf pour le PDF). Les briques communes (rendu, moteur PDF, barres,
formats) sont importées de generer_fiche_pdf.py.
"""

import argparse
import json
import os
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from generer_fiche_pdf import (  # noqa: E402
    _fmt_eur,
    _optnum,
    build_charges_svg,
    doc_statut_of,
    html_to_pdf,
    render_html,
)

DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "..", "assets", "cdc_template.html")

# ---------------------------------------------------------------------------
# Niveaux d'exigence d'un critère
# ---------------------------------------------------------------------------
# Trois niveaux seulement, pour que le cahier des charges reste tranchant :
# un critère dur élimine un bien, un critère important le décote, un souhait
# départage. Le rang sert au tri, le poids par défaut à la grille de notation.

NIVEAU = {
    "dur":             ("Non négociable", "niv-dur", 0, 5),
    "non_negociable":  ("Non négociable", "niv-dur", 0, 5),
    "important":       ("Important", "niv-imp", 1, 4),
    "souhait":         ("Souhaité", "niv-souhait", 2, 2),
    "bonus":           ("Bonus", "niv-bonus", 3, 1),
}

# Priorité d'un secteur géographique : 1 = cible principale.
PRIORITE = {
    1: ("Cible", "prio-1"),
    2: ("Acceptable", "prio-2"),
    3: ("Par défaut", "prio-3"),
}

# Statut d'un jalon du calendrier.
JALON_STATUT = {
    "fait":     ("Fait", "crit-faible"),
    "en_cours": ("En cours", "crit-moderee"),
    "a_faire":  ("À faire", "crit-elevee"),
    "bloquant": ("Bloquant", "crit-critique"),
}


def clamp_poids(v, default=3):
    try:
        return max(1, min(5, int(round(float(v)))))
    except (TypeError, ValueError):
        return default


def _rows(items):
    """Normalise une liste de paires clé/valeur, en acceptant soit
    [{"k": ..., "v": ...}], soit [["clé", "valeur"]]."""
    out = []
    for it in items or []:
        if isinstance(it, dict):
            k, v = it.get("k") or it.get("cle") or it.get("label"), it.get("v") or it.get("valeur")
        elif isinstance(it, (list, tuple)) and len(it) >= 2:
            k, v = it[0], it[1]
        else:
            continue
        if k and v not in (None, ""):
            out.append({"k": str(k), "v": str(v)})
    return out


def capacite_emprunt(mensualite, duree_annees, taux_pct):
    """Capacité d'emprunt indicative : mensualité constante, taux annuel
    (assurance comprise), durée en années. Formule d'annuité classique
    C = m × (1 − (1+i)^−n) / i. Ordre de grandeur, jamais un accord de prêt."""
    if not mensualite or not duree_annees:
        return None
    n = int(round(float(duree_annees) * 12))
    if n <= 0:
        return None
    i = (float(taux_pct or 0) / 100.0) / 12.0
    if i <= 0:
        return float(mensualite) * n
    return float(mensualite) * (1 - (1 + i) ** (-n)) / i


# ---------------------------------------------------------------------------
# Blocs
# ---------------------------------------------------------------------------


def build_hero(data, location):
    """Bandeau des trois valeurs qui cadrent la recherche : ce que la personne
    peut mettre au maximum, ce qu'elle vise, et la surface plancher."""
    b = data.get("budget") or {}
    s = data.get("surface") or {}
    surf = s.get("min_m2")
    surf_txt = f"{surf} m²" if surf not in (None, "") else "nc"
    sub_pieces = []
    if s.get("pieces_min"):
        sub_pieces.append(f"{s['pieces_min']} pièces mini")
    if s.get("chambres_min"):
        sub_pieces.append(f"{s['chambres_min']} chambres")
    surf_sub = " · ".join(sub_pieces) or "surface plancher"

    def eur(v, unite="€", defaut="nc"):
        n = _optnum(b, v)
        return f"{_fmt_eur(n)} {unite}" if n else (str(b.get(v)) if b.get(v) else defaut)

    # Le pied du bandeau ne s'imprime que s'il porte une vraie valeur : un « nc »
    # en pied de page n'apprend rien, il occupe une ligne pour rien.
    def eur_opt(v, unite="€"):
        return eur(v, unite, defaut="")

    if location:
        return {
            "c1_label": "Loyer maximal", "c1": eur("loyer_max", "€/mois"),
            "c1_sub": "charges comprises",
            "c2_label": "Loyer cible", "c2": eur("loyer_cible", "€/mois"),
            "c2_sub": "objectif de recherche",
            "c3_label": "Surface minimale", "c3": surf_txt, "c3_sub": surf_sub,
            "f1_label": "Revenus nets du foyer", "f1": eur_opt("revenus_mensuels", "€/mois"),
            "f2_label": "Taux d'effort maximal", "f2": b.get("taux_effort") or "",
        }
    return {
        "c1_label": "Enveloppe maximale", "c1": eur("enveloppe_max"),
        "c1_sub": "tout compris (bien, frais, travaux)",
        "c2_label": "Prix du bien cible", "c2": eur("prix_cible"),
        "c2_sub": "hors frais et travaux",
        "c3_label": "Surface minimale", "c3": surf_txt, "c3_sub": surf_sub,
        "f1_label": "Apport", "f1": eur_opt("apport"),
        "f2_label": "Mensualité maximale", "f2": eur_opt("mensualite_max", "€/mois"),
    }


def process_budget(data, location):
    """Décomposition de l'enveloppe en barres, capacité d'emprunt indicative,
    et grille des paramètres de financement."""
    b = data.get("budget")
    if not b:
        data["budget"] = None
        return data

    postes = b.get("postes") or []
    if not postes and not location:
        defauts = (("prix_bien", "Prix du bien"), ("frais_notaire", "Frais de notaire"),
                   ("frais_agence", "Frais d'agence"), ("travaux", "Travaux"),
                   ("mobilier", "Mobilier et déménagement"), ("autres", "Autres frais"))
        for key, label in defauts:
            v = _optnum(b, key)
            if v:
                postes.append({"poste": label, "montant": v})
    b["postes"] = postes

    # Montants saisis en nombres : version formatée pour l'affichage (séparateur
    # de milliers). Une valeur déjà saisie en texte est reprise telle quelle.
    for key in ("apport", "mensualite_max", "revenus_mensuels", "loyer_max",
                "loyer_cible", "enveloppe_max", "prix_cible", "travaux"):
        v = _optnum(b, key)
        if v:
            b[key + "_fmt"] = _fmt_eur(v)

    taux = _optnum(b, "taux_pct")
    if taux is not None:
        b["taux_pct_fmt"] = f"{taux:.2f}".rstrip("0").rstrip(".").replace(".", ",")

    # En location, les postes se raisonnent sur l'année (loyer, charges, énergie,
    # assurance) ; à l'achat, c'est une enveloppe unique.
    b.setdefault("unite", "€/an" if location else "€")
    total = sum(v for v in (_optnum(p, "montant") for p in postes) if v)
    b["total_fmt"] = f"{_fmt_eur(total)} {b['unite']}" if total else ""
    b["svg"] = build_charges_svg(postes)

    # Capacité d'emprunt : calculée seulement si elle n'est pas fournie.
    if not b.get("emprunt"):
        cap = capacite_emprunt(_optnum(b, "mensualite_max"),
                               _optnum(b, "duree_annees"), _optnum(b, "taux_pct"))
        if cap:
            b["emprunt_calcule"] = _fmt_eur(cap) + " €"

    b["details"] = _rows(b.get("details"))
    data["budget"] = b
    return data


def process_localisation(data):
    loc = data.get("localisation")
    if not loc:
        data["localisation"] = None
        return data
    secteurs = []
    for s in loc.get("secteurs") or []:
        try:
            p = int(s.get("priorite", 2))
        except (TypeError, ValueError):
            p = 2
        p = max(1, min(3, p))
        label, cls = PRIORITE[p]
        secteurs.append({**s, "priorite": p, "prio_label": label, "prio_cls": cls})
    secteurs.sort(key=lambda s: (s["priorite"], str(s.get("nom", ""))))
    loc["secteurs"] = secteurs
    loc["ancrages"] = loc.get("ancrages") or []
    loc["exclus"] = loc.get("exclus") or []
    data["localisation"] = loc
    return data


def process_criteres(data):
    """Normalise les critères (niveau, poids, tri) puis en déduit la liste des
    non négociables et la grille de notation pondérée."""
    criteres = []
    for c in data.get("criteres") or []:
        key = str(c.get("niveau", "souhait")).strip().lower()
        label, cls, rang, poids_def = NIVEAU.get(key, NIVEAU["souhait"])
        c = dict(c)
        c["niveau_label"], c["niveau_cls"], c["_rang"] = label, cls, rang
        c["poids"] = clamp_poids(c.get("poids"), poids_def)
        c["famille"] = c.get("famille") or ""
        c["exigence"] = c.get("exigence") or ""
        criteres.append(c)
    criteres.sort(key=lambda c: (c["_rang"], -c["poids"], c.get("famille", "")))
    data["criteres"] = criteres

    if not data.get("non_negociables"):
        data["non_negociables"] = [
            (f"{c.get('critere', '')} : {c['exigence']}" if c["exigence"] else c.get("critere", ""))
            for c in criteres if c["_rang"] == 0
        ][:4]

    # Grille de notation : les critères qui départagent réellement les biens.
    # Les non négociables en sont exclus (ils éliminent, ils ne notent pas).
    grille = data.get("grille")
    if grille is None:
        grille = {"criteres": [c for c in criteres if c["_rang"] > 0][:14]}
    elif isinstance(grille, list):
        grille = {"criteres": grille}
    lignes = []
    for c in grille.get("criteres") or []:
        lignes.append({"critere": c.get("critere", ""), "poids": clamp_poids(c.get("poids"), 3)})
    if lignes:
        grille["criteres"] = lignes
        grille["total_poids"] = sum(l["poids"] for l in lignes)
        grille["max_points"] = grille["total_poids"] * 5
        grille.setdefault("colonnes", ["Bien 1", "Bien 2", "Bien 3"])
        data["grille"] = grille
    else:
        data["grille"] = None
    return data


def process_arbitrages(data):
    arbs = []
    for i, a in enumerate(data.get("arbitrages") or [], start=1):
        a = dict(a)
        try:
            a["rang"] = int(a.get("rang", i))
        except (TypeError, ValueError):
            a["rang"] = i
        arbs.append(a)
    arbs.sort(key=lambda a: a["rang"])
    data["arbitrages"] = arbs
    return data


def process_calendrier(data):
    cal = []
    for j in data.get("calendrier") or []:
        j = dict(j)
        label, cls = JALON_STATUT.get(str(j.get("statut", "")).strip().lower(), ("", ""))
        j["statut_label"], j["statut_cls"] = label, cls
        cal.append(j)
    data["calendrier"] = cal
    return data


def process_dossier(data):
    docs = []
    for d in data.get("dossier") or []:
        mark, cls, label = doc_statut_of(d.get("statut"))
        docs.append({**d, "mark": mark, "cls": cls, "statut_label": label})
    data["dossier"] = docs
    return data


def process(data):
    """Complète et normalise les données avant rendu."""
    mode = str(data.get("mode", "achat")).strip().lower()
    if mode not in ("achat", "location"):
        mode = "achat"
    data["mode"] = mode
    location = mode == "location"

    data.setdefault("meta", {})
    data["meta"].setdefault("date", "")
    data["meta"].setdefault(
        "auteur",
        "Agent Immobilier, conseiller de locataire sans conflit d'intérêt" if location
        else "Agent Immobilier, conseiller d'acquéreur sans conflit d'intérêt",
    )

    projet = data.setdefault("projet", {})
    projet.setdefault("titre", "Cahier des charges")
    projet.setdefault("resume", "")
    data.setdefault("surface", {})
    data.setdefault("redhibitoires", [])
    data.setdefault("questions", [])
    data["identite"] = _rows(data.get("identite"))
    data["tolerances"] = _rows(data.get("tolerances"))
    data.setdefault(
        "avertissement",
        "Cahier des charges établi avec le candidat locataire : il formalise un "
        "besoin, il n'engage aucun bailleur et ne vaut pas dossier de candidature."
        if location else
        "Cahier des charges établi avec l'acquéreur : il formalise un besoin et une "
        "capacité déclarée. Les montants de financement sont indicatifs et ne valent "
        "ni accord de prêt, ni engagement d'achat.",
    )

    data["hero"] = build_hero(data, location)

    # Curseur d'arbitrage : où se place le projet entre l'emplacement (à gauche,
    # irréversible) et la surface ou le prix (à droite, rattrapable).
    arb = data.get("arbitrage")
    if arb:
        pos = _optnum(arb, "position")
        if pos is None:
            pos = 50.0
        arb["pos"] = round(max(5.0, min(95.0, pos)), 1)
        data["arbitrage"] = arb

    process_budget(data, location)
    process_localisation(data)
    process_criteres(data)
    process_arbitrages(data)
    process_calendrier(data)
    process_dossier(data)
    return data


def main():
    ap = argparse.ArgumentParser(description="Génère un cahier des charges A4 PDF standardisé.")
    ap.add_argument("input_json", help="Fichier JSON du cahier des charges")
    ap.add_argument("output_pdf", help="Chemin du PDF de sortie")
    ap.add_argument("--template", default=DEFAULT_TEMPLATE, help="Gabarit HTML (optionnel)")
    ap.add_argument("--keep-html", action="store_true", help="Conserver le HTML intermédiaire")
    args = ap.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    data = process(data)
    html = render_html(data, args.template)

    out_pdf = os.path.abspath(args.output_pdf)
    out_dir = os.path.dirname(out_pdf)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if args.keep_html:
        html_path = os.path.splitext(out_pdf)[0] + ".html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        fd, html_path = tempfile.mkstemp(suffix=".html")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html)

    ok, engine = html_to_pdf(html_path, out_pdf)

    if not args.keep_html:
        try:
            os.remove(html_path)
        except OSError:
            pass

    if not ok:
        sys.exit(
            "Échec de la génération PDF : aucun moteur disponible (chromium ou "
            "wkhtmltopdf). Le HTML a pu être conservé avec --keep-html."
        )

    print(f"Cahier des charges généré : {out_pdf} (moteur : {engine})")


if __name__ == "__main__":
    main()
