#!/usr/bin/env python3
"""
Génère une fiche bien A4 PDF standardisée à partir d'un fichier JSON.

Usage :
    python3 scripts/generer_fiche_pdf.py donnees.json fiche.pdf
    python3 scripts/generer_fiche_pdf.py donnees.json fiche.pdf --template autre.html

Le schéma JSON attendu est décrit dans references/fiche-etude.md.
La mise en page est fixe : c'est le script qui garantit la standardisation.

Dépendances : jinja2 (rendu HTML) et, pour le PDF, chromium (headless) ou
wkhtmltopdf. Le script détecte automatiquement le moteur disponible.
"""

import argparse
import html as _html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import glob
import tempfile

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    from markupsafe import Markup, escape
except ImportError:
    sys.exit("jinja2 est requis : pip install jinja2 --break-system-packages")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "..", "assets", "fiche_template.html")

_REF_RE = re.compile(r"\[(\d{1,2})\]")


def sup_filter(value):
    """Convertit les appels de note « [n] » d'un texte en exposant HTML
    « <sup>n</sup> », le reste du texte étant échappé normalement."""
    s = str(escape(str(value if value is not None else "")))
    s = _REF_RE.sub(r'<sup class="ref">\1</sup>', s)
    return Markup(s)

FEU = {
    "vert":   {"label": "À poursuivre", "color": "#1a7f37"},
    "orange": {"label": "Sous conditions", "color": "#d97706"},
    "rouge":  {"label": "À écarter", "color": "#c0362c"},
}


def zone_of(crit):
    if crit <= 4:
        return "Faible", "crit-faible"
    if crit <= 9:
        return "Modérée", "crit-moderee"
    if crit <= 14:
        return "Élevée", "crit-elevee"
    return "Critique", "crit-critique"


def cls_from_label(label):
    l = (label or "").lower()
    if "critique" in l:
        return "crit-critique"
    if "élev" in l or "elev" in l:
        return "crit-elevee"
    if "modér" in l or "moder" in l:
        return "crit-moderee"
    return "crit-faible"


def normalize_energy(bien):
    """Rend l'étiquette DPE robuste : extrait la classe (A à G) et la valeur
    chiffrée même si le champ contient une chaîne libre du type
    'D (188 kWh/m²/an)'. Sans cela, aucune bande ne serait surlignée."""
    for letter_key, num_key in (("dpe", "dpe_kwh"), ("ges", "ges_kgco2")):
        raw = str(bien.get(letter_key, "") or "")
        m = re.search(r"\b([A-Ga-g])\b", raw)
        bien[letter_key] = m.group(1).upper() if m else ""
        if not bien.get(num_key):
            mnum = re.search(r"(\d[\d\s ]*)", raw)
            if mnum:
                digits = re.sub(r"[^\d]", "", mnum.group(1))
                if digits:
                    bien[num_key] = int(digits)
    return bien


TENDANCE = {
    "hausse": ("▲ Hausse", "mkt-up"),
    "up": ("▲ Hausse", "mkt-up"),
    "baisse": ("▼ Baisse", "mkt-down"),
    "down": ("▼ Baisse", "mkt-down"),
    "stable": ("▬ Stable", "mkt-flat"),
    "flat": ("▬ Stable", "mkt-flat"),
}


def trend_of(val):
    """Normalise une direction de tendance en (libellé + flèche, classe couleur).
    Une valeur libre inconnue est affichée telle quelle, en neutre."""
    key = str(val or "").strip().lower()
    if key in TENDANCE:
        return TENDANCE[key]
    if not key:
        return "", "mkt-flat"
    return val, "mkt-flat"


def _fmt_eur(v):
    """7400 -> '7 400' (séparateur de milliers, espace)."""
    return f"{int(round(v)):,}".replace(",", " ")


def _optnum(d, key):
    try:
        return float(d[key])
    except (KeyError, TypeError, ValueError):
        return None


def build_line_svg(points):
    """Courbe d'évolution : prix médian €/m² par année. `points` = liste de
    {annee, prix_m2}. SVG autonome, sans dépendance."""
    pts = []
    for p in points or []:
        try:
            pts.append((int(p.get("annee")), float(p.get("prix_m2"))))
        except (TypeError, ValueError):
            continue
    pts = sorted(set(pts))
    if len(pts) < 2:
        return ""
    xs = [a for a, _ in pts]
    ys = [y for _, y in pts]
    xmin, xmax = min(xs), max(xs)
    span = (max(ys) - min(ys)) or max(ys) or 1.0
    ylo, yhi = min(ys) - span * 0.15, max(ys) + span * 0.15
    W, H = 470.0, 190.0
    ML, MR, MT, MB = 54.0, 12.0, 12.0, 24.0
    pw, ph = W - ML - MR, H - MT - MB
    fx = lambda a: ML + (a - xmin) / (xmax - xmin) * pw
    fy = lambda v: MT + (yhi - v) / (yhi - ylo) * ph
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for i in range(5):
        v = ylo + (yhi - ylo) * i / 4
        yy = fy(v)
        o.append(f'<line x1="{ML:.1f}" y1="{yy:.1f}" x2="{W-MR:.1f}" y2="{yy:.1f}" stroke="#eee"/>')
        o.append(f'<text x="{ML-6:.1f}" y="{yy+3:.1f}" text-anchor="end" font-size="8" fill="#888">{_fmt_eur(v)}</text>')
    for a in xs:
        o.append(f'<text x="{fx(a):.1f}" y="{H-7:.1f}" text-anchor="middle" font-size="8" fill="#888">{a}</text>')
    d = "M " + " L ".join(f"{fx(a):.1f} {fy(y):.1f}" for a, y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="#2f7ec4" stroke-width="2"/>')
    for a, y in pts:
        o.append(f'<circle cx="{fx(a):.1f}" cy="{fy(y):.1f}" r="2.6" fill="#2f7ec4"/>')
    o.append(f'<line x1="{ML:.1f}" y1="{MT:.1f}" x2="{ML:.1f}" y2="{H-MB:.1f}" stroke="#ccc"/>')
    o.append(f'<line x1="{ML:.1f}" y1="{H-MB:.1f}" x2="{W-MR:.1f}" y2="{H-MB:.1f}" stroke="#ccc"/>')
    o.append("</svg>")
    return "".join(o)


def build_boxplot_svg(boxes):
    """Boîtes à moustache horizontales par secteur/typologie, à partir des
    quartiles réels DVF. `boxes` = liste de {label, min, q1, median, q3, max,
    portail?, bien?} (valeurs numériques en €/m²)."""
    rows = []
    for b in boxes or []:
        try:
            v = {k: float(b[k]) for k in ("min", "q1", "median", "q3", "max")}
        except (KeyError, TypeError, ValueError):
            continue
        rows.append({"label": str(b.get("label", "")), **v,
                     "portail": _optnum(b, "portail"), "bien": _optnum(b, "bien")})
    if not rows:
        return ""
    allv = []
    for r in rows:
        allv += [r["min"], r["max"]]
        allv += [r[k] for k in ("portail", "bien") if r[k] is not None]
    lo, hi = min(allv), max(allv)
    span = (hi - lo) or hi or 1.0
    lo, hi = lo - span * 0.06, hi + span * 0.06
    W, ML, MR = 470.0, 122.0, 14.0
    rowh, top = 30.0, 8.0
    H = top + rowh * len(rows) + 24.0
    pw = W - ML - MR
    fx = lambda v: ML + (v - lo) / (hi - lo) * pw
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        xx = fx(v)
        o.append(f'<line x1="{xx:.1f}" y1="{top:.1f}" x2="{xx:.1f}" y2="{top+rowh*len(rows):.1f}" stroke="#f0f0f0"/>')
        o.append(f'<text x="{xx:.1f}" y="{H-8:.1f}" text-anchor="middle" font-size="8" fill="#888">{_fmt_eur(v)}</text>')
    for idx, r in enumerate(rows):
        cy = top + rowh * idx + rowh / 2
        bh = 13.0
        o.append(f'<text x="0" y="{cy+3:.1f}" font-size="8.5" fill="#333">{_sx(r["label"][:26])}</text>')
        xmn, xq1, xmed, xq3, xmx = (fx(r["min"]), fx(r["q1"]), fx(r["median"]), fx(r["q3"]), fx(r["max"]))
        o.append(f'<line x1="{xmn:.1f}" y1="{cy:.1f}" x2="{xmx:.1f}" y2="{cy:.1f}" stroke="#8a8a8a"/>')
        o.append(f'<line x1="{xmn:.1f}" y1="{cy-5:.1f}" x2="{xmn:.1f}" y2="{cy+5:.1f}" stroke="#8a8a8a"/>')
        o.append(f'<line x1="{xmx:.1f}" y1="{cy-5:.1f}" x2="{xmx:.1f}" y2="{cy+5:.1f}" stroke="#8a8a8a"/>')
        o.append(f'<rect x="{xq1:.1f}" y="{cy-bh/2:.1f}" width="{max(1.0, xq3-xq1):.1f}" height="{bh:.1f}" fill="#eaf0fb" stroke="#5b6b7a"/>')
        o.append(f'<line x1="{xmed:.1f}" y1="{cy-bh/2:.1f}" x2="{xmed:.1f}" y2="{cy+bh/2:.1f}" stroke="#1c1c1c" stroke-width="1.8"/>')
        if r["portail"] is not None:
            px = fx(r["portail"])
            o.append(f'<polygon points="{px:.1f},{cy-6:.1f} {px+5:.1f},{cy:.1f} {px:.1f},{cy+6:.1f} {px-5:.1f},{cy:.1f}" fill="none" stroke="#b5560d" stroke-width="1.3"/>')
        if r["bien"] is not None:
            bx = fx(r["bien"])
            o.append(f'<line x1="{bx:.1f}" y1="{cy-8:.1f}" x2="{bx:.1f}" y2="{cy+8:.1f}" stroke="#c0362c" stroke-width="1.7"/>')
    o.append("</svg>")
    return "".join(o)


def build_waterfall_svg(cr, accent="#c0362c"):
    """Cascade du coût de revient : prix + frais + travaux + aléas = coût total,
    comparé à la valeur après travaux (VAT). `cr` = {prix_achat, frais, travaux,
    aleas, vat} (nombres €). Barres horizontales."""
    try:
        prix = float(cr["prix_achat"])
    except (KeyError, TypeError, ValueError):
        return ""

    def g(k):
        try:
            return float(cr[k])
        except (KeyError, TypeError, ValueError):
            return 0.0

    frais, trav, alea = g("frais"), g("travaux"), g("aleas")
    total = prix + frais + trav + alea
    vat = None
    if cr.get("vat") not in (None, ""):
        try:
            vat = float(cr["vat"])
        except (TypeError, ValueError):
            vat = None

    rows = [("Prix d'achat", 0.0, prix, "#5b6b7a")]
    if frais:
        rows.append(("+ Frais de notaire", prix, prix + frais, "#8aa0b5"))
    if trav:
        rows.append(("+ Travaux", prix + frais, prix + frais + trav, "#d9822b"))
    if alea:
        rows.append(("+ Aléas", prix + frais + trav, total, "#c9a13f"))
    rows.append(("= Coût de revient", 0.0, total, accent))
    if vat is not None:
        rows.append(("Valeur après travaux", 0.0, vat, "#1a7f37"))

    hi = (max(total, vat or 0.0) or 1.0) * 1.12
    W, ML, MR = 470.0, 132.0, 62.0
    rowh, top = 25.0, 8.0
    H = top + rowh * len(rows) + 4
    pw = W - ML - MR
    fx = lambda v: ML + v / hi * pw
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for i, (label, a, b, color) in enumerate(rows):
        cy = top + rowh * i + rowh / 2
        x1, x2 = fx(a), fx(b)
        o.append(f'<text x="0" y="{cy+3:.1f}" font-size="8.3" fill="#333">{_sx(label)}</text>')
        o.append(f'<rect x="{x1:.1f}" y="{cy-6:.1f}" width="{max(1.0, x2-x1):.1f}" height="12" fill="{color}"/>')
        o.append(f'<text x="{x2+4:.1f}" y="{cy+3:.1f}" font-size="8" fill="#333">{_fmt_eur(b - a if a > 0 else b)} €</text>')
    o.append("</svg>")
    return "".join(o)


def build_radar_svg(axes):
    """Radar (toile d'araignée) notant le bien sur des axes 0 à 10. `axes` =
    liste de {axe, note}."""
    pts = []
    for a in axes or []:
        try:
            pts.append((str(a.get("axe", "")), max(0.0, min(10.0, float(a.get("note"))))))
        except (TypeError, ValueError):
            continue
    n = len(pts)
    if n < 3:
        return ""
    W = H = 250.0
    cx, cy, R, maxv = W / 2, H / 2 + 2, 80.0, 10.0

    def pt(i, r):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        return (cx + r * math.cos(ang), cy + r * math.sin(ang))

    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for ring in range(1, 5):
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, R * ring / 4) for i in range(n)))
        o.append(f'<polygon points="{poly}" fill="none" stroke="#e6e6e6" stroke-width="0.8"/>')
    for i, (axe, _val) in enumerate(pts):
        x, y = pt(i, R)
        o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#dcdcdc" stroke-width="0.8"/>')
        lx, ly = pt(i, R + 12)
        anchor = "middle" if abs(lx - cx) < 5 else ("end" if lx < cx else "start")
        o.append(f'<text x="{lx:.1f}" y="{ly+2:.1f}" text-anchor="{anchor}" font-size="7.5" fill="#555">{_sx(axe)}</text>')
    vpoly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, R * pts[i][1] / maxv) for i in range(n)))
    o.append(f'<polygon points="{vpoly}" fill="#2f7ec4" fill-opacity="0.22" stroke="#2f7ec4" stroke-width="1.6"/>')
    for i in range(n):
        x, y = pt(i, R * pts[i][1] / maxv)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#2f7ec4"/>')
    o.append("</svg>")
    return "".join(o)


def process_analyse(data):
    """Prépare les visuels d'analyse : cascade du coût de revient, radar de score,
    et normalisation de l'historique DVF du bien."""
    cr = data.get("cout_revient") or {}
    data["cout_revient"] = cr
    accent = (data.get("verdict") or {}).get("feu_color", "#c0362c")
    data["cout_revient_svg"] = build_waterfall_svg(cr, accent)
    data["radar_svg"] = build_radar_svg(data.get("radar") or [])
    dvf = data.get("dvf_historique") or []
    for m in dvf:
        m.setdefault("date", "")
        m.setdefault("prix", "")
        m.setdefault("detail", "")
    data["dvf_historique"] = dvf
    return data


def build_cible_svg(rings):
    """Cible chiffrée : anneaux concentriques par distance autour du bien (★ au
    centre), du plus proche au plus lointain. `rings` = liste (proche -> loin) de
    {label, prix_m2, volume}. Une légende à droite donne médiane et volume."""
    rr = [r for r in (rings or []) if isinstance(r, dict)]
    n = len(rr)
    if n < 1:
        return ""
    W, H = 380.0, 232.0
    cx, cy, Rmax = 104.0, H / 2, 94.0
    palette = ["#5b83b8", "#89a9d0", "#b3c8e2", "#d7e2f0", "#eaf0f7"]
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for i in range(n - 1, -1, -1):
        R = Rmax * (i + 1) / n
        col = palette[min(i, len(palette) - 1)]
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="{col}" stroke="#ffffff" stroke-width="1.2"/>')
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="#c0362c" stroke="#fff" stroke-width="1.5"/>')
    o.append(f'<text x="{cx:.1f}" y="{cy+2.9:.1f}" text-anchor="middle" font-size="8" fill="#fff">★</text>')
    lx = 224.0
    ly0 = cy - (n * 22) / 2 + 12
    for i, r in enumerate(rr):
        yy = ly0 + i * 22
        col = palette[min(i, len(palette) - 1)]
        o.append(f'<rect x="{lx:.1f}" y="{yy-8:.1f}" width="9" height="9" rx="2" fill="{col}"/>')
        o.append(f'<text x="{lx+14:.1f}" y="{yy:.1f}" font-size="8.5" font-weight="bold" fill="#333">{_sx(r.get("label",""))}</text>')
        line2 = _sx(str(r.get("prix_m2", "")))
        if r.get("volume"):
            line2 += "  ·  " + _sx(str(r.get("volume")))
        o.append(f'<text x="{lx+14:.1f}" y="{yy+11:.1f}" font-size="8.5" fill="#555">{line2}</text>')
    o.append("</svg>")
    return "".join(o)


def build_scatter_svg(sc):
    """Nuage de points DVF : chaque vente = un point (x, €/m²), avec le bien mis
    en évidence. `sc` = {x_label, points:[{x, y}], bien:{x, y}}."""
    if not isinstance(sc, dict):
        return ""
    pts = []
    for p in sc.get("points", []) or []:
        try:
            pts.append((float(p["x"]), float(p["y"])))
        except (KeyError, TypeError, ValueError):
            continue
    if len(pts) < 3:
        return ""
    bien = None
    b = sc.get("bien")
    if isinstance(b, dict):
        try:
            bien = (float(b["x"]), float(b["y"]))
        except (KeyError, TypeError, ValueError):
            bien = None
    allx = [p[0] for p in pts] + ([bien[0]] if bien else [])
    ally = [p[1] for p in pts] + ([bien[1]] if bien else [])
    xmin, xmax = min(allx), max(allx)
    ymin, ymax = min(ally), max(ally)
    xs = (xmax - xmin) or 1.0
    ysp = (ymax - ymin) or (ymax or 1.0)
    xlo, xhi = xmin - xs * 0.08, xmax + xs * 0.08
    ylo, yhi = ymin - ysp * 0.10, ymax + ysp * 0.10
    W, H = 470.0, 210.0
    ML, MR, MT, MB = 56.0, 12.0, 10.0, 30.0
    pw, ph = W - ML - MR, H - MT - MB
    fx = lambda v: ML + (v - xlo) / (xhi - xlo) * pw
    fy = lambda v: MT + (yhi - v) / (yhi - ylo) * ph
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for i in range(5):
        v = ylo + (yhi - ylo) * i / 4
        yy = fy(v)
        o.append(f'<line x1="{ML:.1f}" y1="{yy:.1f}" x2="{W-MR:.1f}" y2="{yy:.1f}" stroke="#eee"/>')
        o.append(f'<text x="{ML-6:.1f}" y="{yy+3:.1f}" text-anchor="end" font-size="8" fill="#888">{_fmt_eur(v)}</text>')
    for x, y in pts:
        o.append(f'<circle cx="{fx(x):.1f}" cy="{fy(y):.1f}" r="2.6" fill="#8aa0b5" fill-opacity="0.85"/>')
    if bien:
        bx, by = fx(bien[0]), fy(bien[1])
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="5" fill="#c0362c" stroke="#fff" stroke-width="1.4"/>')
        o.append(f'<text x="{bx+7:.1f}" y="{by-5:.1f}" font-size="8" font-weight="bold" fill="#c0362c">le bien</text>')
    o.append(f'<line x1="{ML:.1f}" y1="{MT:.1f}" x2="{ML:.1f}" y2="{H-MB:.1f}" stroke="#ccc"/>')
    o.append(f'<line x1="{ML:.1f}" y1="{H-MB:.1f}" x2="{W-MR:.1f}" y2="{H-MB:.1f}" stroke="#ccc"/>')
    o.append(f'<text x="{ML+pw/2:.1f}" y="{H-6:.1f}" text-anchor="middle" font-size="8" fill="#888">{_sx(sc.get("x_label","Surface (m²)"))}</text>')
    o.append(f'<text x="10" y="{MT+8:.1f}" font-size="8" fill="#888">€/m²</text>')
    o.append("</svg>")
    return "".join(o)


def build_histogramme_svg(bins):
    """Histogramme des ventes par tranche de €/m². `bins` = liste ordonnée de
    {tranche, ventes, bien?} ; la tranche du bien (bien=true) est surlignée."""
    bb = []
    for b in bins or []:
        if not isinstance(b, dict):
            continue
        try:
            bb.append((str(b.get("tranche", "")), int(round(float(b.get("ventes", 0)))), bool(b.get("bien"))))
        except (TypeError, ValueError):
            continue
    if len(bb) < 2:
        return ""
    vmax = max(v for _, v, _ in bb) or 1
    W, H = 470.0, 172.0
    ML, MR, MT, MB = 34.0, 10.0, 10.0, 30.0
    pw, ph = W - ML - MR, H - MT - MB
    n = len(bb)
    slot = pw / n
    bw = slot * 0.66
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="100%" style="max-width:{W:.0f}px" '
         f'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">']
    for i in range(4):
        v = vmax * i / 3
        yy = MT + ph - (v / vmax) * ph
        o.append(f'<line x1="{ML:.1f}" y1="{yy:.1f}" x2="{W-MR:.1f}" y2="{yy:.1f}" stroke="#eee"/>')
        o.append(f'<text x="{ML-4:.1f}" y="{yy+3:.1f}" text-anchor="end" font-size="7.5" fill="#888">{int(round(v))}</text>')
    for i, (tr, v, is_bien) in enumerate(bb):
        x = ML + slot * i + (slot - bw) / 2
        h = (v / vmax) * ph
        y = MT + ph - h
        col = "#c0362c" if is_bien else "#8aa0b5"
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(0.5,h):.1f}" fill="{col}"/>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{y-3:.1f}" text-anchor="middle" font-size="7.5" fill="#555">{v}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{H-8:.1f}" text-anchor="middle" font-size="7" fill="#888">{_sx(tr)}</text>')
    o.append(f'<line x1="{ML:.1f}" y1="{H-MB:.1f}" x2="{W-MR:.1f}" y2="{H-MB:.1f}" stroke="#ccc"/>')
    o.append("</svg>")
    return "".join(o)


def process_marche(data):
    """Normalise le bloc étude de marché s'il est présent (Fonction 5).
    Absent, la fiche reste une fiche bien classique."""
    marche = data.get("marche")
    if not marche:
        data["marche"] = None
        return data

    marche.setdefault("perimetre", "")
    marche.setdefault("date_donnees", "")
    marche.setdefault("profil", {})
    marche.setdefault("locatif", None)
    marche.setdefault("segments_privilegier", [])
    marche.setdefault("segments_eviter", [])
    marche.setdefault("risques_marche", [])
    marche.setdefault("conclusion", {})

    tendance = marche.setdefault("tendance", {})
    if isinstance(tendance, dict):
        label, cls = trend_of(tendance.get("direction"))
        tendance["badge"], tendance["cls"] = label, cls

    prix = marche.get("prix", []) or []
    for row in prix:
        for k in ("secteur", "typologie", "prix_m2_median", "fourchette",
                  "volume", "estimation_portail"):
            row.setdefault(k, "")
        row["tendance_badge"], row["tendance_cls"] = trend_of(row.get("tendance"))
    marche["prix"] = prix

    marche["evolution_svg"] = build_line_svg(marche.get("evolution"))
    marche["boxplot_svg"] = build_boxplot_svg(marche.get("boxplot"))
    marche["cible_svg"] = build_cible_svg(marche.get("cible"))
    marche["scatter_svg"] = build_scatter_svg(marche.get("scatter"))
    marche["histogramme_svg"] = build_histogramme_svg(marche.get("histogramme"))

    comps = marche.get("comparables") or []
    for c in comps:
        for k in ("secteur", "surface", "prix", "prix_m2", "date", "distance"):
            c.setdefault(k, "")
    marche["comparables"] = comps

    data["marche"] = marche
    return data


def process_sources(data):
    """Normalise et numérote les sources, en dédupliquant. Chaque source peut
    être une chaîne (nom seul) ou un objet {nom, url, detail}. Les doublons
    (même nom) sont retirés en conservant le premier. La numérotation obtenue
    sert d'appels de note « [n] » dans le texte."""
    raw = data.get("sources", []) or []
    seen, out = set(), []
    for s in raw:
        if isinstance(s, dict):
            nom = str(s.get("nom", "")).strip()
            url = str(s.get("url", "")).strip()
            detail = str(s.get("detail", "")).strip()
        else:
            nom, url, detail = str(s).strip(), "", ""
        if not nom:
            continue
        key = nom.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"n": len(out) + 1, "nom": nom, "url": url, "detail": detail})
    data["sources"] = out
    return data


POSTURE = {
    "acheteur":        (12.0, "Marché très favorable à l'acheteur"),
    "plutot_acheteur": (30.0, "Marché plutôt favorable à l'acheteur"),
    "equilibre":       (50.0, "Marché équilibré"),
    "plutot_vendeur":  (70.0, "Marché plutôt favorable au vendeur"),
    "vendeur":         (88.0, "Marché favorable au vendeur"),
}


def _parse_amount(s):
    """Extrait un montant entier d'une chaîne (« 350 000 € » -> 350000)."""
    digits = re.sub(r"[^\d]", "", str(s or ""))
    return int(digits) if digits else None


def process_conclusion(data):
    """Enrichit la conclusion de l'étude de marché : posture de marché (curseur),
    traduction de la fourchette €/m² défendable en prix total pour le bien,
    indicateurs (KPIs) et plan d'action."""
    marche = data.get("marche")
    if not marche:
        return data
    c = marche.setdefault("conclusion", {})
    c.setdefault("kpis", [])
    c.setdefault("plan_action", [])

    # Posture de marché : mot-clé ou nombre 0 (acheteur) à 100 (vendeur)
    p = c.get("posture")
    if isinstance(p, (int, float)):
        c["posture_pos"] = round(max(4.0, min(96.0, float(p))), 1)
        c["posture_label"] = c.get("posture_label", "")
    else:
        pos, deflabel = POSTURE.get(str(p or "").strip().lower(), (None, ""))
        c["posture_pos"] = pos
        c["posture_label"] = c.get("posture_label") or deflabel

    # Prix total défendable pour ce bien = fourchette €/m² × surface
    c["bien_total"] = None
    try:
        mn = float(c["defendable_m2_min"])
        mx = float(c["defendable_m2_max"])
        surf = float(data.get("bien", {}).get("surface_m2"))
    except (KeyError, TypeError, ValueError):
        mn = mx = surf = None
    if mn and mx and surf:
        tmin = round(mn * surf / 1000) * 1000
        tmax = round(mx * surf / 1000) * 1000
        bt = {
            "total_fmt": f"{_fmt_eur(tmin)} à {_fmt_eur(tmax)} €",
            "m2_fmt": f"{_fmt_eur(mn)} à {_fmt_eur(mx)} €/m²",
            "surface": surf,
        }
        affiche = _parse_amount(data.get("prix", {}).get("affiche"))
        if affiche:
            bt["affiche_fmt"] = f"{_fmt_eur(affiche)} €"
            hi = round((tmax - affiche) / affiche * 100)
            lo = round((tmin - affiche) / affiche * 100)
            bt["ecart_fmt"] = f"{hi:+d} % à {lo:+d} %" if hi != lo else f"{hi:+d} %"
        marche["conclusion"]["bien_total"] = bt
    return data


def clamp(x, lo=1, hi=5):
    try:
        x = int(round(float(x)))
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# Plan du bien (schéma d'agencement estimatif, ou reproduction cotée d'un plan)
# ---------------------------------------------------------------------------

ROOM_FILL = {
    "jour":        "#fdf3e3",  # séjour, salon, salle à manger
    "nuit":        "#eaf0fb",  # chambres, bureau
    "eau":         "#e6f4f4",  # salle de bains, WC, cuisine ouverte sur eau
    "service":     "#eef0f2",  # cuisine, cellier, buanderie, rangements
    "circulation": "#f4f4f2",  # entrée, couloir, dégagement
    "exterieur":   "#eaf6ea",  # balcon, terrasse, loggia, jardin
    "":            "#f4f4f2",
}
ROOM_STROKE = "#3a3a3a"
WINDOW_COLOR = "#2f7ec4"
NORD_DIR = {"haut": (0, -1), "bas": (0, 1), "gauche": (-1, 0), "droite": (1, 0)}


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _sx(s):
    return _html.escape(str(s), quote=True)


def build_plan_svg(plan):
    """Construit un SVG inline du plan à partir de pièces rectangulaires
    positionnées (x, y, w, h) sur une grille. En mode 'reproduction', les
    coordonnées sont en mètres et un mètre-étalon est tracé ; en mode
    'estimation', la grille est relative et le rendu est explicitement non métré.
    Le SVG est autonome (aucune dépendance externe)."""
    rooms = []
    for p in plan.get("pieces") or []:
        w, h = _num(p.get("w")), _num(p.get("h"))
        if w <= 0 or h <= 0:
            continue
        rooms.append({
            "x": _num(p.get("x")), "y": _num(p.get("y")), "w": w, "h": h,
            "nom": p.get("nom", ""), "surface": p.get("surface", ""),
            "fenetres": [str(f).strip().upper()[:1] for f in (p.get("fenetres") or [])],
            "type": (p.get("type") or "").lower(),
        })
    if not rooms:
        return ""
    max_x = max(r["x"] + r["w"] for r in rooms)
    max_y = max(r["y"] + r["h"] for r in rooms)
    if max_x <= 0 or max_y <= 0:
        return ""

    PAD, TARGET_W, MAX_H = 14.0, 344.0, 300.0
    scale = (TARGET_W - 2 * PAD) / max_x
    if max_y * scale + 2 * PAD > MAX_H:
        scale = (MAX_H - 2 * PAD) / max_y
    W = max_x * scale + 2 * PAD
    H = max_y * scale + 2 * PAD
    repro = plan.get("mode") == "reproduction"

    out = [
        '<svg viewBox="0 0 {:.0f} {:.0f}" width="100%" style="max-width:{:.0f}px" '
        'xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans, Arial, sans-serif">'
        .format(W, H, W)
    ]
    for r in rooms:
        X, Y = PAD + r["x"] * scale, PAD + r["y"] * scale
        RW, RH = r["w"] * scale, r["h"] * scale
        fill = ROOM_FILL.get(r["type"], ROOM_FILL[""])
        out.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" '
                   'fill="{}" stroke="{}" stroke-width="1.4"/>'
                   .format(X, Y, RW, RH, fill, ROOM_STROKE))
        # Fenêtres : segment épais bleu, centré sur 55 % de l'arête
        for edge in r["fenetres"]:
            if edge in ("N", "S"):
                y = Y if edge == "N" else Y + RH
                x1, x2 = X + RW * 0.22, X + RW * 0.78
                out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                           'stroke="{}" stroke-width="3"/>'.format(x1, y, x2, y, WINDOW_COLOR))
            elif edge in ("E", "O"):
                x = X + RW if edge == "E" else X
                y1, y2 = Y + RH * 0.22, Y + RH * 0.78
                out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                           'stroke="{}" stroke-width="3"/>'.format(x, y1, x, y2, WINDOW_COLOR))
        # Étiquettes
        cx, cy = X + RW / 2, Y + RH / 2
        if RW > 34 and RH > 18:
            two = RH > 30
            name_y = cy - 4 if two else cy + 3
            out.append('<text x="{:.1f}" y="{:.1f}" text-anchor="middle" '
                       'font-size="8.2" font-weight="bold" fill="#242424">{}</text>'
                       .format(cx, name_y, _sx(r["nom"])))
            if two:
                sub = "{:.1f} × {:.1f} m".format(r["w"], r["h"]) if repro else (
                    "~" + _sx(r["surface"]) if r["surface"] else "")
                if sub:
                    out.append('<text x="{:.1f}" y="{:.1f}" text-anchor="middle" '
                               'font-size="7" fill="#777">{}</text>'
                               .format(cx, cy + 7, sub))
    # Mètre-étalon en mode reproduction
    if repro:
        bx, by = PAD, H - 4
        out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                   'stroke="#555" stroke-width="1.2"/>'.format(bx, by, bx + scale, by))
        out.append('<text x="{:.1f}" y="{:.1f}" font-size="7" fill="#555">1 m</text>'
                   .format(bx + scale + 4, by + 2))
    # Boussole (Nord)
    dx, dy = NORD_DIR.get(str(plan.get("nord", "haut")).lower(), (0, -1))
    ncx, ncy, L = W - 16, 18, 11
    tx, ty = ncx + dx * L, ncy + dy * L
    px, py = -dy, dx  # perpendiculaire pour la pointe de flèche
    out.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="#333" '
               'stroke-width="1.3"/>'.format(ncx - dx * L, ncy - dy * L, tx, ty))
    out.append('<polygon points="{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f}" fill="#333"/>'
               .format(tx, ty, tx - dx * 5 + px * 3, ty - dy * 5 + py * 3,
                       tx - dx * 5 - px * 3, ty - dy * 5 - py * 3))
    out.append('<text x="{:.1f}" y="{:.1f}" text-anchor="middle" font-size="7.5" '
               'font-weight="bold" fill="#333">N</text>'.format(tx + dx * 5, ty + dy * 6 + 2))
    out.append('</svg>')
    return "".join(out)


def process_plan(data):
    """Prépare le plan du bien si présent (schéma estimatif ou reproduction cotée)."""
    plan = data.get("plan")
    if not plan:
        data["plan"] = None
        return data
    plan.setdefault("mode", "estimation")
    plan.setdefault("source", "")
    plan.setdefault("legende", [])
    if plan.get("mode") == "reproduction":
        plan.setdefault("note", "Plan reproduit d'un document fourni. Cotes reportées "
                                "du plan source, à vérifier sur place ; non contractuel.")
    else:
        plan.setdefault("note", "Schéma d'agencement estimatif d'après l'annonce, les photos "
                                "et les documents disponibles. Non métré, non contractuel : "
                                "surfaces et proportions approximatives.")
    plan["svg"] = build_plan_svg(plan)
    data["plan"] = plan if plan["svg"] else None
    return data


# Catégories de commerces/équipements : synonymes -> clé normalisée
ENV_KEY = {
    "commerce": "commerce", "commerces": "commerce", "alimentation": "commerce",
    "ecole": "ecole", "education": "ecole", "creche": "ecole",
    "transport": "transport", "transports": "transport", "gare": "transport",
    "sante": "sante", "medecin": "sante", "pharmacie": "sante", "hopital": "sante",
    "parc": "parc", "loisir": "parc", "loisirs": "parc", "vert": "parc",
}
# Ordre d'affichage : (clé, libellé, couleur)
ENV_META = [
    ("transport", "Transports", "#6b4fbb"),
    ("commerce", "Commerces", "#d9822b"),
    ("ecole", "Écoles", "#2f7ec4"),
    ("sante", "Santé", "#c0362c"),
    ("parc", "Parcs et loisirs", "#1a7f37"),
    ("autre", "Autres", "#888888"),
]
_ENV_ICONS = {
    "transport": '<rect x="3" y="2.5" width="10" height="8.5" rx="2" fill="{c}"/><rect x="4.6" y="4.3" width="2.6" height="2.4" fill="#fff"/><rect x="8.8" y="4.3" width="2.6" height="2.4" fill="#fff"/><circle cx="5.6" cy="12.4" r="1.2" fill="{c}"/><circle cx="10.4" cy="12.4" r="1.2" fill="{c}"/>',
    "commerce": '<path d="M4 5.2h8l-.7 8a1 1 0 0 1-1 .9H5.7a1 1 0 0 1-1-.9l-.7-8z" fill="{c}"/><path d="M6 5.6V4.4a2 2 0 0 1 4 0v1.2" fill="none" stroke="{c}" stroke-width="1.2"/>',
    "ecole": '<path d="M8 3l6 2.4-6 2.4-6-2.4L8 3z" fill="{c}"/><path d="M4.5 6.6v2.8c0 1 1.6 1.9 3.5 1.9s3.5-.9 3.5-1.9V6.6" fill="none" stroke="{c}" stroke-width="1.2"/>',
    "sante": '<rect x="3" y="3" width="10" height="10" rx="2.5" fill="{c}"/><rect x="7" y="5" width="2" height="6" fill="#fff"/><rect x="5" y="7" width="6" height="2" fill="#fff"/>',
    "parc": '<circle cx="8" cy="6" r="4" fill="{c}"/><rect x="7.2" y="9" width="1.6" height="4.5" rx="0.4" fill="{c}"/>',
    "autre": '<path d="M8 2a4 4 0 0 0-4 4c0 3 4 8 4 8s4-5 4-8a4 4 0 0 0-4-4z" fill="{c}"/><circle cx="8" cy="6" r="1.5" fill="#fff"/>',
}


def _env_icon(key, color):
    body = _ENV_ICONS.get(key, _ENV_ICONS["autre"]).replace("{c}", color)
    return ('<svg viewBox="0 0 16 16" width="13" height="13" '
            'style="vertical-align:-2px" xmlns="http://www.w3.org/2000/svg">' + body + "</svg>")


def process_environnement(data):
    """Regroupe les commerces et équipements alentours par type (transports,
    commerces, écoles, santé, parcs) avec une icône par catégorie. Rendu 100 %
    autonome (aucune carte, aucun réseau)."""
    env = data.get("environnement")
    if not env:
        data["environnement"] = None
        return data
    pois = env.get("pois", []) or []
    for p in pois:
        p.setdefault("nom", "")
        p.setdefault("distance", "")
    groups = []
    for key, label, color in ENV_META:
        members = [p for p in pois
                   if ENV_KEY.get(str(p.get("categorie", "")).strip().lower(), "autre") == key]
        if members:
            groups.append({"label": label, "icon": _env_icon(key, color), "pois": members})
    env["groups"] = groups
    data["environnement"] = env if groups else None
    return data


def process(data):
    """Complète et normalise les données avant rendu."""
    data.setdefault("meta", {})
    data["meta"].setdefault("date", "")
    data["meta"].setdefault(
        "auteur",
        "Agent Immobilier, conseiller d'acquéreur sans conflit d'intérêt",
    )
    data.setdefault("bien", {})
    normalize_energy(data["bien"])
    data.setdefault("prix", {})
    data.setdefault("negociation", {})
    data.setdefault("vigilance", [])
    data.setdefault("sources", [])
    data.setdefault("aide_decision", [])
    data.setdefault("notes_page", True)
    data.setdefault(
        "avertissement",
        "Analyse indépendante d'aide à la décision. Ni expertise judiciaire, "
        "ni conseil en investissement, ni avis juridique. La décision et le prix "
        "relèvent de l'acquéreur.",
    )

    verdict = data.setdefault("verdict", {})
    feu = str(verdict.get("feu", "orange")).lower()
    if feu not in FEU:
        feu = "orange"
    verdict["feu"] = feu
    verdict["feu_label"] = FEU[feu]["label"]
    verdict["feu_color"] = FEU[feu]["color"]
    verdict.setdefault("note_sur_100", None)
    verdict.setdefault("resume", "")

    # Position du curseur sur la jauge dégradée vert (0 %) → rouge (100 %).
    # Pilotée par la note si elle existe (100/100 = vert, 0/100 = rouge),
    # sinon par le feu. Bornée pour que l'étiquette ne déborde pas.
    note = verdict.get("note_sur_100")
    if isinstance(note, (int, float)):
        pos = 100.0 - max(0.0, min(100.0, float(note)))
    else:
        pos = {"vert": 12.0, "orange": 50.0, "rouge": 86.0}.get(feu, 50.0)
    verdict["pos"] = round(max(5.0, min(95.0, pos)), 1)

    data.setdefault("points_forts", [])
    data.setdefault("points_faibles", [])

    # Risques : criticité, tri, classe couleur
    risques = data.get("risques", []) or []
    for r in risques:
        r["v"] = clamp(r.get("v"))
        r["i"] = clamp(r.get("i"))
        r["crit"] = r["v"] * r["i"]
        r["zone"], r["cls"] = zone_of(r["crit"])
        r.setdefault("famille", "")
        r.setdefault("commentaire", "")
        r.setdefault("libelle", "")
    risques.sort(key=lambda r: r["crit"], reverse=True)
    data["risques"] = risques

    # Risque global : fourni, sinon dérivé du plus critique
    if not data.get("risque_global"):
        if risques:
            data["risque_global"] = risques[0]["zone"]
        else:
            data["risque_global"] = "Faible"
    data["risque_global_cls"] = cls_from_label(data["risque_global"])

    process_plan(data)
    process_environnement(data)
    process_analyse(data)
    process_marche(data)
    process_conclusion(data)
    process_sources(data)

    return data


def render_html(data, template_path):
    template_path = os.path.abspath(template_path)
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["sup"] = sup_filter
    template = env.get_template(os.path.basename(template_path))
    return template.render(**data)


def find_chromium():
    env_bin = os.environ.get("CHROMIUM_BIN")
    if env_bin and os.path.exists(env_bin):
        return env_bin
    patterns = [
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome", "chrome-headless-shell"):
        found = shutil.which(name)
        if found:
            return found
    return None


def html_to_pdf(html_path, pdf_path):
    """Convertit le HTML en PDF. Retourne (ok, moteur)."""
    chromium = find_chromium()
    if chromium:
        base = [
            chromium, "--headless=new", "--no-sandbox", "--disable-gpu",
            "--disable-dev-shm-usage", "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            "--force-device-scale-factor=1",  # rendu à 100 %, jamais de zoom
            "--virtual-time-budget=15000",
        ]
        variants = [
            base + ["--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
            base + [f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
            [chromium, "--headless", "--no-sandbox", "--disable-gpu",
             f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
        ]
        for cmd in variants:
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=90)
            except Exception:
                continue
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1200:
                return True, "chromium"

    wk = shutil.which("wkhtmltopdf")
    if wk:
        cmd = [wk, "--enable-local-file-access", "--page-size", "A4",
               "--zoom", "1.0",
               "--margin-top", "10mm", "--margin-bottom", "10mm",
               "--margin-left", "11mm", "--margin-right", "11mm",
               "--quiet", html_path, pdf_path]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=90)
        except Exception:
            pass
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1200:
            return True, "wkhtmltopdf"

    return False, None


def main():
    ap = argparse.ArgumentParser(description="Génère une fiche bien A4 PDF standardisée.")
    ap.add_argument("input_json", help="Fichier JSON des données du bien")
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

    print(f"Fiche générée : {out_pdf} (moteur : {engine})")


if __name__ == "__main__":
    main()
