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
import os
import re
import shutil
import subprocess
import sys
import glob
import tempfile

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    sys.exit("jinja2 est requis : pip install jinja2 --break-system-packages")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "..", "assets", "fiche_template.html")

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

    data["marche"] = marche
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
    process_marche(data)

    return data


def render_html(data, template_path):
    template_path = os.path.abspath(template_path)
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template_path)),
        autoescape=select_autoescape(["html"]),
    )
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
            "--virtual-time-budget=8000",
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
