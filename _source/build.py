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

    # Bilan cumulé des formations réalisées (page d'accueil, catalogue)
    inter = lire_yaml("contenu/interventions.yml")["sessions"]
    bilan = {"sessions": len(inter), "stagiaires": sum(x.get("stagiaires") or 0 for x in inter),
             "departements": len({str(x["departement"]) for x in inter}), "debut": min(int(str(x["date"])[:4]) for x in inter)}

    env = Environment(loader=FileSystemLoader(os.path.join(ICI, "gabarits")), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    commun = dict(site=site, vae=vae, formations=formations, themes=themes, nb_formations=len(formations),
                  vae_tot=vae_tot, bilan=bilan, annee=datetime.date.today().year,
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
    ecrire("guide-livret-2/index.html", "guide_livret2.html", rubrique="vae",
           titre_page="Pack Réussir son livret 2 de VAE (travail social) · 2aFormation",
           description="Guide PDF, trames Word et checklist pour rédiger son livret 2 de VAE : DEES, DEME, DEASS, DEEJE, DEETS, DECESF, DEAES. Mise à jour réforme 2026.")
    jeton = site["produits"]["guide_livret2"]["jeton"]
    ecrire(f"guide-livret-2/merci-{jeton}/index.html", "merci_livret2.html", rubrique="vae", jeton=jeton,
           titre_page="Merci pour votre commande · 2aFormation", description="Téléchargement du pack livret 2.")
    ecrire("guide-memoire/index.html", "guide_memoire.html", rubrique="etudiants",
           titre_page="Pack Réussir son mémoire de pratique professionnelle (DEES, DEASS, DEEJE, DEETS, DECESF) · 2aFormation",
           description="Guide PDF, 8 trames Word et checklist pour réussir son mémoire de pratique professionnelle en travail social, de la question de départ à la soutenance.")
    jm = site["produits"]["guide_memoire"]["jeton"]
    ecrire(f"guide-memoire/merci-{jm}/index.html", "merci_memoire.html", rubrique="etudiants", jeton=jm,
           titre_page="Merci pour votre commande · 2aFormation", description="Téléchargement du pack mémoire.")
    ecrire("preparer-son-entree/index.html", "guide_entree.html", rubrique="etudiants",
           titre_page="Réussir son entrée en formation sociale : projet motivé et entretien (DEES, DEASS, DEEJE, DEETS, DECESF) · 2aFormation",
           description="Guide PDF et 8 trames Word pour préparer son projet de formation motivé Parcoursup et son entretien d'admission en école du travail social. À jour de la réforme 2026.")
    je = site["produits"]["guide_entree"]["jeton"]
    ecrire(f"preparer-son-entree/merci-{je}/index.html", "merci_entree.html", rubrique="etudiants", jeton=je,
           titre_page="Merci pour votre commande · 2aFormation", description="Téléchargement du pack entrée en formation.")
    js = site["produits"]["selection"]["jeton"]
    ecrire(f"preparer-son-entree/envoi-{js}/index.html", "merci_selection.html", rubrique="etudiants",
           titre_page="Merci pour votre commande · 2aFormation", description="Démarrer votre accompagnement.")
    ecrire("relecture-ecrits/index.html", "relecture.html", rubrique="etudiants",
           titre_page="Relecture de mémoire et d'écrits de certification · travail social · 2aFormation",
           description="Relecture de votre mémoire ou de votre dossier de certification (DEES, DEASS, DEME, DEEJE…) par des professionnels formateurs : retour écrit détaillé et entretien en visio.")
    jr = site["produits"]["relecture"]["jeton"]
    ecrire(f"relecture-ecrits/merci-{jr}/index.html", "merci_relecture.html", rubrique="etudiants",
           titre_page="Merci pour votre commande · 2aFormation", description="Envoi de votre écrit pour relecture.")
    # Carte « Nos interventions »
    carte = json.load(open(os.path.join(ICI, "contenu/carte_france.json"), encoding="utf-8"))
    par_slug = {f["slug"]: f for f in formations}
    mois = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
    sessions = []
    for x in lire_yaml("contenu/interventions.yml")["sessions"]:
        a, m = str(x["date"]).split("-")[:2]
        f = par_slug.get(x.get("formation") or "")
        sessions.append({"dep": str(x["departement"]), "annee": int(a), "mois": f"{mois[int(m) - 1]} {a}", "cle": f"{a}-{m}",
                         "titre": x["titre"], "theme": x.get("theme") or (f["theme"] if f else ""),
                         "lien": f"formations/{f['slug']}/index.html" if f else "", "stagiaires": x.get("stagiaires"), "estime": bool(x.get("estime"))})
    sessions.sort(key=lambda s: s["cle"], reverse=True)
    deps_actifs = sorted({s["dep"] for s in sessions})
    carte_stats = {"sessions": len(sessions), "departements": len(deps_actifs),
                   "stagiaires": sum(s["stagiaires"] or 0 for s in sessions),
                   "debut": min(s["annee"] for s in sessions), "themes": len({s["theme"] for s in sessions if s["theme"]})}
    ecrire("nos-interventions/index.html", "interventions.html", rubrique="interventions", carte=carte,
           sessions=sessions, deps_actifs=deps_actifs, carte_stats=carte_stats,
           annees=sorted({s["annee"] for s in sessions}), themes_carte=[t for t in THEMES if any(s["theme"] == t for s in sessions)],
           sessions_json=json.dumps(sessions, ensure_ascii=False),
           noms_json=json.dumps({k: v["nom"] for k, v in carte["departements"].items()}, ensure_ascii=False),
           titre_page="Nos interventions en France · formations réalisées · 2aFormation",
           description="La carte des formations réalisées par 2aFormation auprès des établissements du social, du médico-social et de la protection de l'enfance, département par département.")
    # Questionnaires d'évaluation Qualiopi (pages non référencées, liens envoyés aux stagiaires et aux établissements)
    questionnaires = [
        ("a-chaud", {"type": "chaud", "nom": "Évaluation à chaud", "surtitre": "Évaluation à chaud · fin de formation",
                     "titre": "Votre avis sur la formation", "intro": "Environ 5 minutes. Vos réponses nous aident à faire évoluer nos formations."}),
        ("a-froid", {"type": "froid", "nom": "Évaluation à froid stagiaire", "surtitre": "Évaluation à froid · environ 3 mois après",
                     "titre": "Et trois mois après ?", "intro": "Environ 5 minutes. Vos réponses nous disent ce que la formation a changé dans votre pratique."}),
        ("etablissement", {"type": "etablissement", "nom": "Évaluation à froid établissement", "surtitre": "Évaluation à froid · établissement",
                           "titre": "Votre regard sur la formation", "intro": "Environ 5 minutes. Votre avis de responsable complète celui des participants."}),
    ]
    for chemin_q, q in questionnaires:
        ecrire(f"evaluation/{chemin_q}/index.html", "evaluation.html", rubrique="", q=q,
               titre_page=f"{q['titre']} · 2aFormation", description=q["intro"])
    ecrire("evaluation/liens-675b945645/index.html", "evaluation_liens.html", rubrique="",
           titre_page="Liens des questionnaires d'évaluation · 2aFormation", description="Outil interne.")
    ecrire("catalogue/index.html", "catalogue.html", rubrique="", titre_page="", description="")
    ecrire("contact/index.html", "contact.html", rubrique="contact",
           titre_page="Contact et devis · 2aFormation",
           description="Contactez 2aFormation pour une formation en intra, une analyse des pratiques ou un accompagnement VAE. Réponse sous 48 h ouvrées.")
    for p in sorted(glob.glob(os.path.join(ICI, "contenu/pages/*.md"))):
        page = lire_md(p)
        ecrire(page["chemin"], "page.html", rubrique="", corps=page["corps"],
               titre_page=f"{page['titre']} · 2aFormation", description=page["description"])
    # Trouver son stage : ressource gratuite pour les étudiants (données FINESS, un fichier par région dans contenu/stages/)
    import unicodedata
    regions = [json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(ICI, "contenu/stages/*.json"))]
    regions.sort(key=lambda r: (r["slug"] == "outre-mer", unicodedata.normalize("NFD", r["region"]).encode("ascii", "ignore").decode()))
    for st in regions:
        for d in st["departements"]:
            donnees = json.dumps({"data": d["structures"], "sect": st["secteurs"]}, ensure_ascii=False).replace("</", "<\\/")
            from collections import Counter
            nb_sect = Counter(s["s"] for s in d["structures"])
            par_secteur = [(lib, nb_sect[cle]) for cle, lib, _ in st["secteurs"] if nb_sect[cle]]
            villes = Counter(s["v"] for s in d["structures"] if s.get("v")).most_common(3)
            ecrire(f"trouver-son-stage/{d['slug']}/index.html", "stages_departement.html", rubrique="etudiants", st=st, d=d,
                   data_json=donnees, par_secteur=par_secteur, villes=villes,
                   titre_page=f"Stage éducateur, ME, ASS {d['en']} : {d['n']} structures · 2aFormation",
                   description=f"{d['n']} structures sociales et médico-sociales {d['de']} où chercher un stage d'éducateur, de moniteur-éducateur ou d'assistant de service social, avec la méthode et un tableau de suivi gratuit.")
    nb_dep = sum(len(r["departements"]) for r in regions)
    ecrire("trouver-son-stage/index.html", "stages_region.html", rubrique="etudiants", regions=regions,
           total=sum(d["n"] for r in regions for d in r["departements"]), nb_dep=nb_dep,
           secteurs=regions[0]["secteurs"] if regions else [],
           titre_page="Stage éducateur, ME, ASS : " + f"{sum(d['n'] for r in regions for d in r['departements']):,}".replace(",", " ") + " lieux de stage en France · 2aFormation",
           description=f"Méthode, conseils de terrain et structures sociales et médico-sociales de {nb_dep} départements pour trouver un stage en travail social. Gratuit, par des éducateurs spécialisés.")
    # Bibliographie commentée (contenu/bibliographie.yml)
    biblio = lire_yaml("contenu/bibliographie.yml")
    nb_refs = sum(len(t["references"]) for t in biblio["themes"])
    ecrire("bibliographie/index.html", "bibliographie.html", rubrique="etudiants", b=biblio, nb_refs=nb_refs,
           titre_page="Bibliographie commentée du travail social · 2aFormation",
           description=f"{nb_refs} références vérifiées et commentées pour les écrits en travail social : protection de l'enfance, attachement, relation éducative, méthodologie du mémoire, textes officiels. Gratuit.")
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
            if c not in ("404.html", "catalogue/index.html") and "/merci-" not in c and "/envoi-" not in c and not c.startswith("evaluation/"):
                fh.write(f"  <url><loc>{site['url']}/{c}</loc><lastmod>{aujourdhui}</lastmod></url>\n")
        fh.write("</urlset>\n")
    with open(os.path.join(SORTIE, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
    print(f"Site construit : {len(pages)} pages dans _site/")


if __name__ == "__main__":
    main()
