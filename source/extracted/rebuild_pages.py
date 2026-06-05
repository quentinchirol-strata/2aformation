# -*- coding: utf-8 -*-
import os
import re
import unicodedata

BASE = r"C:\Users\Quentin\Documents\2aformation\2aformation_mirror - Claude"
TEMPLATE = os.path.join(BASE, "la-relation-educative-existe-t-il-de-la-confiance-dans-laccompagnement-specialise", "index.html")

with open(TEMPLATE, "r", encoding="utf-8") as f:
    template = f.read()

# Normalize template to NFC so it matches our string literals
template = unicodedata.normalize("NFC", template)

# Shared content
PUBLIC = "Cette formation s'adresse à toute personne pouvant justifier d'au moins un an d'expérience en rapport direct avec la certification visée, soit 1607 heures (continu ou non), sous un ou plusieurs statuts (salariés, travailleurs indépendants, bénévoles…)."
PREREQUIS = "Cet accompagnement s'adresse à toutes personnes ayant obtenu un accord de recevabilité de leur livret d'accessibilité (livret 1)."
CERTIFICATION = "Certificateur : Ministère de l'Enseignement supérieur et de la Recherche et Ministère chargé de la Solidarité. La VAE n'est pas une transformation automatique de l'expérience en diplôme. Seul le jury de certification reste souverain à attribuer ou non le diplôme visé."

OBJ_GENERAUX = "<ul><li>Reconnaître votre expérience acquise et la faire reconnaître par un diplôme</li><li>Mettre en cohérence votre certification avec votre niveau de responsabilité</li><li>Faire reconnaître vos compétences</li><li>Obtenir un niveau de qualification permettant d'accéder à une formation d'un niveau supérieur</li><li>Changer d'emploi</li><li>Évoluer professionnellement</li></ul>"

MOD_EVAL = "<ul><li>Évaluations individuelles à chaud et à froid</li><li>Bilan en fin d'accompagnement avec le candidat</li><li>Retour du formateur sur chaque livrable</li><li>Analyse des écrits produits</li><li>Vérification de l'atteinte des objectifs par des mises en situation</li></ul>"

# Originals to find
ORIG_TITLE = "La relation éducative, existe-t-il de la confiance dans l’accompagnement spécialisé"
ORIG_SLUG = "la-relation-educative-existe-t-il-de-la-confiance-dans-laccompagnement-specialise"
ORIG_INTRO = "<p>Distance, tiers, confiance, voici des mots inhérents à la relation éducative. Mais qu’en est-il au contact de public en difficulté? Combien de fois nous sommes nous posé ces questions ? Sommes-nous parvenus à instaurer une relation de confiance ? Est-ce que l’accompagnement implique nécessairement de la confiance ? En s’appuyant sur des auteurs comme Guy HARDY nous tentons de réfléchir à ces notions afin d’améliorer nos pratiques.</p>"
ORIG_PROF = "<p>Tout professionnel travaillant auprès de personnes (enfant et adulte) dans le domaine de la santé, du social et du médico-social.</p>"
ORIG_PREREQ = "<p>Être concerné par l’accompagnement de mineurs accueillis en institution (Internat, accueil de jour, travail en milieu ouvert…).</p>"
ORIG_CERTIF = "<p>Formation non-certifiante. Attestation de suivi de la formation et de validation des compétences.</p>"
ORIG_COUT1 = '<p><span style="font-size: 20px;"><strong>Inter :</strong></span></p><p>• Présentiel ou distanciel<br />• Durée : 2 jours<br />• Prix/personne : sur devis<br />• Prix/Groupe : sur devis</p><p><span style="font-size: 20px;"><strong>Intra :</strong></span></p><p>• Dans vos locaux<br />• Durée : 2 jours<br />• Prix sur devis</p>'
ORIG_COUT2 = "<p> </p><p><strong>Financements possibles :</strong> Employeur / Opérateur de compétences / Financement individuel</p>"
ORIG_OBJ_GEN = "<ul><li>Sensibiliser le professionnel à l’intervention systémique et à l’intervention systémique familiale</li><li>Expérimenter les techniques de base en approche systémique</li><li>Identifier les gestes professionnels et les outils et dispositifs associés permettant la mise en œuvre d’une relation éducative.</li></ul>"
ORIG_OBJ_SPEC = "<p><strong>Développement des compétences relationnelles</strong></p><ul><li>Apprendre à établir une relation éducative éthique et respectueuse avec les personnes accompagnées</li><li>Acquérir des techniques d&rsquo;observation, d&rsquo;entretien et de médiation éducative</li><li>Développer des capacités d&rsquo;écoute, d&#8217;empathie et de communication adaptées</li></ul><p><strong>Compréhension globale des situations</strong></p><ul><li>Analyser les besoins, ressources et interactions des personnes dans leur environnement</li><li>Adopter une vision systémique prenant en compte la personne, sa famille et son contexte social</li></ul><p><strong>Positionnement professionnel</strong></p><ul><li>Développer une posture réflexive sur sa pratique</li><li>Travailler en équipe pluridisciplinaire et en partenariat</li><li>La confiance dans la relation à l’autre</li></ul><p><strong>Approche systémique</strong></p><ul><li>Comprendre les interactions entre l&rsquo;individu, le groupe et l&rsquo;institution</li><li>Articuler l&rsquo;accompagnement individuel et l&rsquo;intervention sur le collectif</li><li>Mobiliser les ressources de l&rsquo;environnement dans l&rsquo;action éducative</li></ul>"
ORIG_NB_PERS = "<p>10 à 15 personnes</p>"
ORIG_DUREE = "<p>2 jours ( 14 heures)</p>"
ORIG_HORAIRES = "<p><strong>9h00 &#8211; 12h30</strong></p><p><strong>13h30 &#8211; 17h</strong></p>"
ORIG_DATES = "<p><strong>Date : </strong><strong>Nous consulter</strong></p>"
ORIG_MOD_EVAL = "<ul><li>Evaluations individuelles à chaud et à froid</li><li>Tour de table en fin de formation</li><li>Retour du formateur</li><li>Analyse des questionnaires</li><li>Vérification de l’atteinte des objectifs par des exercices de mise en pratique</li></ul>"
ORIG_MOD_PED = "<ul><li>Supports pédagogiques imprimés et/ou numérisés</li><li>Apports conceptuels</li><li>Mises en pratique autour de cas concrets</li><li>Partage d’expériences</li></ul>"

FICHES = [
    {
        "slug": "vae-24h-complet",
        "title": "Accompagnement VAE - Programme 24h Complet",
        "intro": "Cette formation accompagne l'ensemble des professionnels à l'écriture de leur livret 2 en vue de l'obtention du DEASS, DEES, DEME, DECESF, DEAES, DEEJE. Programme actualisé le 11/03/2026.",
        "cout": '<p><span style="font-size: 20px;"><strong>Tarif :</strong></span></p><p>• Coût de la formation : <strong>2800 € TTC</strong><br />• Durée : 24 heures</p><p><strong>Financements possibles :</strong> Employeur / Opérateur de compétences / Financement individuel / France Travail / CPF</p><p>Pas de frais d\'inscription ou de dossier.</p>',
        "obj_spec": "<p><strong>Étape 1 : Les étapes et outils de la VAE</strong></p><ul><li>Présentation et appropriation du référentiel et du livret 2</li><li>Présenter le référentiel professionnel, les liens entre les référentiels Fonctions/Activités et compétences</li><li>Faciliter l'appréhension du livret 2 par l'analyse de sa structuration et de son contenu</li><li>Rappeler les règles de la communication écrite et apporter des conseils pour la mise en forme du livret 2</li></ul><p><strong>Étape 2 : Suivis individuels</strong></p><ul><li>Co-construction du prévisionnel des rencontres avec le formateur, en présentiel et/ou en distanciel</li><li>Amener le candidat à questionner et analyser son expérience pour faire le choix des activités révélatrices d'acquisition de compétences</li><li>Apporter au candidat des outils et conseils méthodologiques</li><li>Faire avec le candidat l'analyse et la critique constructive des écrits produits</li></ul><p><strong>Étape 3 : Préparation de l'épreuve orale</strong></p><ul><li>Préciser le rôle et les attributions du jury certificateur</li><li>Rappeler les règles et les techniques de l'entretien oral</li><li>Simulation de l'épreuve orale dans des conditions proches du jury</li><li>Préparer le candidat à la gestion du stress, du temps et de l'argumentation</li><li>Entretien post-jury pour échanger autour du résultat et des suites en cas de validation partielle</li></ul>",
        "nb_pers": "Accompagnement individuel",
        "duree": "24 heures",
        "horaires": "Présentiel ou Distanciel",
        "dates": "Sessions à l'année - Nous consulter",
        "mod_ped": "<ul><li>Supports pédagogiques numérisés remis en amont de l'accompagnement</li><li>Accompagnement individualisé et personnalisé</li><li>Apports conceptuels</li><li>Mises en pratique autour de cas concrets</li><li>Partage d'expériences</li><li>Matériel : ordinateur, connexion internet, livret 2 au format numérique</li></ul>",
    },
    {
        "slug": "vae-analyse-livret-2",
        "title": "VAE - Analyse du Livret 2",
        "intro": "Cet accompagnement ciblé vous aide à analyser en profondeur votre livret 2 en vue de l'obtention du DEASS, DEES, DEME, DECESF, DEAES, DEEJE. Programme actualisé le 25/11/2025.",
        "cout": '<p><span style="font-size: 20px;"><strong>Tarif :</strong></span></p><p>• Coût de la formation : <strong>500 € TTC</strong><br />• Durée : 4h30 en distanciel</p><p><strong>Financements possibles :</strong> Employeur / Opérateur de compétences / Financement individuel / France Travail</p><p>Pas de frais d\'inscription ou de dossier.</p>',
        "obj_spec": "<p><strong>Étape 1 : Lecture et analyse asynchrone (3h)</strong></p><ul><li>Lecture approfondie du livret 2 par le formateur en amont des rencontres</li><li>Analyse et préparation des retours méthodologiques</li><li>Identification des axes d'amélioration</li></ul><p><strong>Étape 2 : Retour en face à face (1h)</strong></p><ul><li>Échange avec le formateur sur les axes d'amélioration</li><li>Conseils méthodologiques personnalisés</li><li>Analyse et critique constructive des écrits produits</li></ul><p><strong>Étape 3 : Validation des réajustements (30 min)</strong></p><ul><li>Vérification des modifications apportées par le candidat</li><li>Validation finale du livret 2 avant dépôt</li></ul>",
        "nb_pers": "Accompagnement individuel",
        "duree": "4h30",
        "horaires": "100% Distanciel (Teams ou WhatsApp visio)",
        "dates": "Sessions à l'année - À effectuer en 2 mois maximum",
        "mod_ped": "<ul><li>Accompagnement individualisé et personnalisé</li><li>Apports conceptuels</li><li>Mises en pratique autour de cas concrets</li><li>Partage d'expériences</li><li>Matériel : ordinateur ou téléphone mobile + connexion internet</li></ul>",
    },
    {
        "slug": "vae-analyse-domaine-competence",
        "title": "VAE - Analyse d'un Domaine de Compétence",
        "intro": "Un accompagnement focalisé sur un domaine de compétence spécifique de votre livret 2 pour le DEASS, DEES, DEME, DECESF, DEAES, DEEJE. Programme actualisé le 25/11/2025.",
        "cout": '<p><span style="font-size: 20px;"><strong>Tarif :</strong></span></p><p>• Coût de la formation : <strong>250 € TTC</strong><br />• Durée : 2h30 en distanciel</p><p><strong>Financements possibles :</strong> Employeur / Opérateur de compétences / Financement individuel / France Travail</p><p>Pas de frais d\'inscription ou de dossier.</p>',
        "obj_spec": "<p><strong>Étape 1 : Analyse asynchrone (1h30)</strong></p><ul><li>Lecture et analyse du domaine de compétence par le formateur</li><li>Préparation des retours et axes d'amélioration</li><li>Identification des situations professionnelles à valoriser</li></ul><p><strong>Étape 2 : Retour en face à face (1h)</strong></p><ul><li>Échange ciblé sur le domaine de compétence</li><li>Conseils méthodologiques pour valoriser l'expérience</li><li>Soutien à l'analyse descriptive des activités</li></ul>",
        "nb_pers": "Accompagnement individuel",
        "duree": "2h30",
        "horaires": "100% Distanciel (Teams ou WhatsApp visio)",
        "dates": "Sessions à l'année - Nous consulter",
        "mod_ped": "<ul><li>Accompagnement individualisé et personnalisé</li><li>Apports conceptuels</li><li>Partage d'expériences</li><li>Matériel : ordinateur ou téléphone mobile + connexion internet</li></ul>",
    },
    {
        "slug": "vae-livret-2-et-oral",
        "title": "VAE - Analyse du Livret 2 + Préparation à l'Oral",
        "intro": "Un accompagnement complet combinant l'analyse de votre livret 2 et la préparation à l'épreuve orale avec le jury, pour le DEASS, DEES, DEME, DECESF, DEAES, DEEJE. Programme actualisé le 25/11/2025.",
        "cout": '<p><span style="font-size: 20px;"><strong>Tarif :</strong></span></p><p>• Coût de la formation : <strong>900 € TTC</strong><br />• Durée : 8h30 en distanciel</p><p><strong>Financements possibles :</strong> Employeur / Opérateur de compétences / Financement individuel / France Travail</p><p>Pas de frais d\'inscription ou de dossier.</p>',
        "obj_spec": "<p><strong>Partie 1 : Analyse du Livret 2 (4h30)</strong></p><ul><li>Lecture et analyse du livret 2 par le formateur en asynchrone (3h)</li><li>Retour en face à face par le formateur (1h)</li><li>Retour sur les réajustements effectués par le candidat (30 min)</li></ul><p><strong>Partie 2 : Préparation à l'oral (4h)</strong></p><ul><li>Recommandations et préparation à l'entretien en face à face (1h)</li><li>Simulation d'entretien en face à face avec retour critique (1h30)</li><li>Mettre le candidat dans des conditions proches du jury certificateur (1h)</li><li>Entretien post-jury pour échanger autour du résultat et des suites en cas de validation partielle (30 min)</li></ul><p><strong>Objectifs transverses</strong></p><ul><li>Préciser le rôle et les attributions du jury certificateur</li><li>Rappeler les règles et techniques de l'entretien oral</li><li>Préparer le candidat à la gestion du stress, du temps et de l'argumentation</li></ul>",
        "nb_pers": "Accompagnement individuel",
        "duree": "8h30",
        "horaires": "100% Distanciel (Teams ou WhatsApp visio)",
        "dates": "Sessions à l'année - À effectuer en 2 mois maximum",
        "mod_ped": "<ul><li>Supports pédagogiques numérisés remis en amont de l'accompagnement</li><li>Accompagnement individualisé et personnalisé</li><li>Apports conceptuels</li><li>Mises en pratique autour de cas concrets</li><li>Partage d'expériences</li><li>Matériel : ordinateur ou téléphone mobile + connexion internet</li></ul>",
    },
    {
        "slug": "vae-preparation-oral",
        "title": "VAE - Préparation à l'Oral du Jury",
        "intro": "Un accompagnement spécifique pour vous préparer à l'épreuve orale devant le jury VAE pour le DEASS, DEES, DEME, DECESF, DEAES, DEEJE. Programme actualisé le 25/11/2025.",
        "cout": '<p><span style="font-size: 20px;"><strong>Tarif :</strong></span></p><p>• Coût de la formation : <strong>550 € TTC</strong><br />• Durée : 2h30 en distanciel</p><p><strong>Financements possibles :</strong> Employeur / Opérateur de compétences / Financement individuel / France Travail</p><p>Pas de frais d\'inscription ou de dossier.</p>',
        "obj_spec": "<p><strong>Étape 1 : Recommandations et préparation (1h)</strong></p><ul><li>Préciser le rôle et les attributions du jury certificateur</li><li>Rappeler les règles et les techniques de l'entretien oral</li><li>Conseils sur la gestion du stress, du temps et de l'argumentation devant un jury</li></ul><p><strong>Étape 2 : Simulation d'entretien (1h30)</strong></p><ul><li>Mise en condition réelle d'épreuve orale face au formateur</li><li>Retour critique sur la prestation orale</li><li>Choix des éléments les plus pertinents pour l'oral</li><li>Entretien post-jury pour échanger autour du résultat et des suites en cas de validation partielle</li></ul>",
        "nb_pers": "Accompagnement individuel",
        "duree": "2h30",
        "horaires": "100% Distanciel (Teams ou WhatsApp visio)",
        "dates": "Sessions à l'année - À effectuer en 2 mois maximum",
        "mod_ped": "<ul><li>Accompagnement individualisé et personnalisé</li><li>Apports conceptuels</li><li>Partage d'expériences</li><li>Matériel : ordinateur ou téléphone mobile + connexion internet</li></ul>",
    },
]

def verify(template_str, original, label):
    if original not in template_str:
        print(f"  WARNING: not found - {label}")

# Verify all originals exist in template
print("Verifying originals exist in template...")
for label, orig in [
    ("TITLE", ORIG_TITLE), ("SLUG", ORIG_SLUG), ("INTRO", ORIG_INTRO),
    ("PROF", ORIG_PROF), ("PREREQ", ORIG_PREREQ), ("CERTIF", ORIG_CERTIF),
    ("COUT1", ORIG_COUT1), ("COUT2", ORIG_COUT2), ("OBJ_GEN", ORIG_OBJ_GEN),
    ("OBJ_SPEC", ORIG_OBJ_SPEC), ("NB_PERS", ORIG_NB_PERS), ("DUREE", ORIG_DUREE),
    ("HORAIRES", ORIG_HORAIRES), ("DATES", ORIG_DATES),
    ("MOD_EVAL", ORIG_MOD_EVAL), ("MOD_PED", ORIG_MOD_PED),
]:
    verify(template, orig, label)

for fiche in FICHES:
    html = template

    # Title / metadata
    html = html.replace(f"<title>{ORIG_TITLE} - 2aFormation</title>", f"<title>{fiche['title']} - 2aFormation</title>")
    html = html.replace(f'<meta property="og:title" content="{ORIG_TITLE} - 2aFormation" />', f'<meta property="og:title" content="{fiche["title"]} - 2aFormation" />')
    html = html.replace(f'<link rel="canonical" href="../{ORIG_SLUG}/index.html" />', f'<link rel="canonical" href="../{fiche["slug"]}/index.html" />')
    html = html.replace(f'<meta property="og:url" content="https://2aformation.com/{ORIG_SLUG}/" />', f'<meta property="og:url" content="https://2aformation.com/{fiche["slug"]}/" />')

    # H2 hero title
    html = html.replace(f'<h2 class="elementor-heading-title elementor-size-default">{ORIG_TITLE}</h2>', f'<h2 class="elementor-heading-title elementor-size-default">{fiche["title"]}</h2>')

    # Content sections
    html = html.replace(ORIG_INTRO, f"<p>{fiche['intro']}</p>")
    html = html.replace(ORIG_PROF, f"<p>{PUBLIC}</p>")
    html = html.replace(ORIG_PREREQ, f"<p>{PREREQUIS}</p>")
    html = html.replace(ORIG_CERTIF, f"<p>{CERTIFICATION}</p>")
    html = html.replace(ORIG_COUT1, fiche['cout'])
    html = html.replace(ORIG_COUT2, "")
    html = html.replace(ORIG_OBJ_GEN, OBJ_GENERAUX)
    html = html.replace(ORIG_OBJ_SPEC, fiche['obj_spec'])
    html = html.replace(ORIG_NB_PERS, f"<p>{fiche['nb_pers']}</p>")
    html = html.replace(ORIG_DUREE, f"<p>{fiche['duree']}</p>")
    html = html.replace(ORIG_HORAIRES, f"<p><strong>{fiche['horaires']}</strong></p>")
    html = html.replace(ORIG_DATES, f"<p><strong>{fiche['dates']}</strong></p>")
    html = html.replace(ORIG_MOD_EVAL, MOD_EVAL)
    html = html.replace(ORIG_MOD_PED, fiche['mod_ped'])

    folder = os.path.join(BASE, fiche['slug'])
    os.makedirs(folder, exist_ok=True)
    outpath = os.path.join(folder, "index.html")
    with open(outpath, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print(f"Built: {fiche['slug']}")
