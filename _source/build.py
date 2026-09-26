#!/usr/bin/env python3
"""Construit le site 2aFormation dans le dossier _site/.

Les textes se modifient dans contenu/ (fichiers .yml et .md).
La mise en page se modifie dans gabarits/ et static/assets/css/site.css.
Lancement : python3 build.py
"""
import datetime
import glob
import json
import os
import shutil
import sys

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "_site")
THEMES = ["Protection de l’enfance", "Violences et situations de danger", "Posture et pratiques"]


def lire_yaml(chemin):
    with open(os.path.join(ICI, chemin), encoding="utf-8") as f:
        return yaml.safe_load(f)


def lire_md(chemin):
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    entete, corps = {}, texte
    if texte.startswith("---"):
        _, bloc, corps = texte.split("---", 2)
        entete = yaml.safe_load(bloc)
    entete["corps"] = markdown.markdown(corps, extensions=["extra", "nl2br"])
    return entete


def main():
    site = lire_yaml("contenu/site.yml")
    vae = lire_yaml("contenu/vae.yml")
    formations = [lire_yaml(p) for p in sorted(glob.glob(os.path.join(ICI, "contenu/formations/*.yml")))]
    formations = [f for f in formations if f.get("publie", True)]
    formations.sort(key=lambda f: (THEMES.index(f["theme"]) if f["theme"] in THEMES else 99, f.get("ordre", 99)))

    erreurs = []
    for f in formations:
        for champ in ("slug", "titre", "theme", "jours", "heures", "intro", "public", "prerequis", "objectifs", "programme"):
            if not f.get(champ):
                erreurs.append(f"Formation « {f.get('titre', '?')} » : le champ « {champ} » est vide.")
        f.setdefault("titre_court", f["titre"])
    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)

    themes = [(t, [f for f in formations if f["theme"] == t]) for t in THEMES]
    themes = [(t, l) for t, l in themes if l]
    res = site["chiffres"].get("vae_resultats") or []
    vae_tot = {k: sum(r[k] for r in res) for k in ("presentes", "diplomes", "partielles", "abandons")}

    env = Environment(loader=FileSystemLoader(os.path.join(ICI, "gabarits")), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    commun = dict(site=site, vae=vae, formations=formations, themes=themes, nb_formations=len(formations),
                  vae_tot=vae_tot, annee=datetime.date.today().year,
                  annee_catalogue=site.get("annee_catalogue", datetime.date.today().year + 1),
                  version=datetime.datetime.now().strftime("%Y%m%d%H%M"))

    if os.path.isdir(SORTIE):
        shutil.rmtree(SORTIE)
    shutil.copytree(os.path.join(ICI, "static"), SORTIE)
    pages = []

    def ecrire(chemin, gabarit, **ctx):
        profondeur = chemin.count("/")
        html = env.get_template(gabarit).render(**commun, chemin=chemin.replace("index.html", ""),
                                                R="../" * profondeur, **ctx)
        cible = os.path.join(SORTIE, chemin)
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        with open(cible, "w", encoding="utf-8") as fh:
            fh.write(html)
        pages.append(chemin)

    ecrire("index.html", "accueil.html", rubrique="accueil",
           titre_page="2aFormation · Formations en protection de l'enfance et accompagnement VAE",
           description="Organisme de formation certifié Qualiopi : formations en intra pour les équipes du social et de la protection de l'enfance, analyse des pratiques et accompagnement VAE (DEES, DEASS, DEME…). Interventions dans toute la France.")
    ecrire("formations/index.html", "formations.html", rubrique="formations",
           titre_page="Nos formations · 2aFormation",
           description=f"{len(formations)} formations en intra pour les équipes du social, du médico-social et de la protection de l'enfance. Deux formateurs de terrain, partout en France.")
    for f in formations:
        jsonld = {
            "@context": "https://schema.org", "@type": "Course", "name": f["titre"], "description": f["intro"],
            "inLanguage": "fr",
            "provider": {"@type": "Organization", "name": "2aFormation", "url": site["url"]},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite",
                                  "courseWorkload": f"PT{f['heures']}H"},
        }
        ecrire(f"{f['slug']}/index.html", "formation.html", rubrique="formations", f=f,
               jsonld=json.dumps(jsonld, ensure_ascii=False),
               titre_page=f"{f['titre_court']} · Formation · 2aFormation",
               description=f"Formation de {f['jours']} jours ({f['heures']} h) en intra : {f['intro'][:120]}…")
    ecrire("nos-vae/index.html", "vae.html", rubrique="vae",
           titre_page="Accompagnement VAE · DEES, DEASS, DEME, DEEJE, DECESF, DEAES · 2aFormation",
           description="Accompagnement VAE pour les diplômes d'État du travail social : parcours complet, relecture du livret 2, préparation à l'oral. Architectes accompagnateurs de parcours.")
    ecrire("analyse-des-pratiques/index.html", "gapp.html", rubrique="gapp",
           titre_page="Analyse des pratiques professionnelles (GAPP) · 2aFormation",
           description="Groupes d'analyse des pratiques professionnelles pour les équipes du social et du médico-social : une séance mensuelle pour prendre du recul et prévenir l'épuisement.")
    ecrire("catalogue/index.html", "catalogue.html", rubrique="", titre_page="", description="")
    ecrire("contact/index.html", "contact.html", rubrique="contact",
           titre_page="Contact et devis · 2aFormation",
           description="Contactez 2aFormation pour une formation en intra, une analyse des pratiques ou un accompagnement VAE. Réponse sous 48 h ouvrées.")
    for p in sorted(glob.glob(os.path.join(ICI, "contenu/pages/*.md"))):
        page = lire_md(p)
        ecrire(page["chemin"], "page.html", rubrique="", corps=page["corps"],
               titre_page=f"{page['titre']} · 2aFormation", description=page["description"])
    ecrire("404.html", "page.html", rubrique="", titre_page="Page introuvable · 2aFormation",
           description="Cette page n'existe pas.",
           corps='<h1>Page introuvable</h1><p>Cette page n\'existe pas ou a été déplacée.</p>'
                 '<p style="margin-top:16px"><a class="btn primary" href="/index.html">Retour à l\'accueil</a> '
                 '<a class="btn ghost" href="/formations/index.html">Voir les formations</a></p>')

    # Anciennes adresses redirigées vers les nouvelles pages
    redirections = {
        "vae-24h-complet": "nos-vae/index.html#parcours-complet",
        "vae-livret-2-et-oral": "nos-vae/index.html#lecture-livret-oral",
        "vae-analyse-livret-2": "nos-vae/index.html#analyse-livret",
        "vae-preparation-oral": "nos-vae/index.html#preparation-oral",
        "vae-analyse-domaine-competence": "nos-vae/index.html#analyse-bloc",
        "informations-sur-les-vae": "nos-vae/index.html",
        "mentions-legales": "mention/index.html",
    }
    for ancien, nouveau in redirections.items():
        cible = os.path.join(SORTIE, ancien, "index.html")
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        with open(cible, "w", encoding="utf-8") as fh:
            fh.write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Page déplacée</title>'
                     f'<link rel="canonical" href="{site["url"]}/{nouveau}"><meta name="robots" content="noindex">'
                     f'<meta http-equiv="refresh" content="0; url=../{nouveau}"></head>'
                     f'<body><p>Cette page a été déplacée : <a href="../{nouveau}">continuer</a>.</p></body></html>')

    aujourdhui = datetime.date.today().isoformat()
    with open(os.path.join(SORTIE, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for c in pages:
            if c not in ("404.html", "catalogue/index.html"):
                fh.write(f"  <url><loc>{site['url']}/{c}</loc><lastmod>{aujourdhui}</lastmod></url>\n")
        fh.write("</urlset>\n")
    with open(os.path.join(SORTIE, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
    print(f"Site construit : {len(pages)} pages dans _site/")


if __name__ == "__main__":
    main()
