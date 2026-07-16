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


def clamp(x, lo=1, hi=5):
    try:
        x = int(round(float(x)))
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, x))


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
