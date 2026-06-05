$base = "C:\Users\Quentin\Documents\2aformation\2aformation_mirror - Claude"
$nosVae = Join-Path $base "nos-vae\index.html"
$lines = Get-Content $nosVae -Encoding UTF8

# Split nos-vae structure
# Top: lines 1..305 (head + header + container + h1 title line)
# Bottom: lines 645..end (closing main + footer + scripts)
$top = ($lines[0..304] -join "`n")
$bottom = ($lines[644..($lines.Count-1)] -join "`n")

# Define the 5 fiches data
$fiches = @(
    @{
        slug = "vae-24h-complet"
        title = "Accompagnement VAE - Programme 24h Complet"
        cardTitle = "VAE - Parcours Complet 24h"
        image = "../wp-content/uploads/2024/08/educateur-specialise-850.jpg"
        intro = "Cette formation accompagne l'ensemble des professionnels à l'écriture de leur livret 2 en vue de l'obtention du DEASS, DEES, DEME, DECESF, DEAES, DEEJE."
        actualise = "11/03/2026"
        duree = "24 heures"
        modalite = "Présentiel & Distanciel"
        cout = "2800 € TTC"
        modaliteDetail = "Session d'accompagnement VAE disponible à l'année pour 24h réparties entre 3 mois et 10 mois selon le calendrier de dépôt des dossiers et les besoins du candidat. Rencontres présentiel/distanciel au choix, entre 1h et 2h en fonction des nécessités + liens mails. Le temps de lecture effectué par l'accompagnant en amont des rencontres est compris dans les 24h."
        lieu = "Présentiel : A définir avec le stagiaire. Distanciel : Teams ou visio WhatsApp."
        programme = @(
            @{titre = "Étape 1 : Les étapes et outils de la VAE"; items = @("Présentation et appropriation du référentiel et du livret 2", "Présenter le référentiel professionnel, les liens entre les référentiels Fonctions/Activités et compétences", "Faciliter l'appréhension du livret 2 par l'analyse de sa structuration et de son contenu", "Rappeler les règles de la communication écrite et apporter des conseils pour la mise en forme du livret 2")},
            @{titre = "Étape 2 : Suivis individuels"; items = @("Co-construction du prévisionnel des rencontres avec le formateur, en présentiel et/ou en distanciel", "Amener le candidat à questionner et analyser son expérience pour faire le choix des activités révélatrices d'acquisition de compétences", "Apporter au candidat des outils et conseils méthodologiques", "Faire avec le candidat l'analyse et la critique constructive des écrits produits")},
            @{titre = "Étape 3 : Préparation de l'épreuve orale"; items = @("Préciser le rôle et les attributions du jury certificateur", "Rappeler les règles et les techniques de l'entretien oral", "Simulation de l'épreuve orale dans des conditions proches du jury", "Préparer le candidat à la gestion du stress, du temps et de l'argumentation", "Entretien post-jury pour échanger autour du résultat et des suites en cas de validation partielle")}
        )
        validation = "Remise d'une attestation d'accompagnement à la VAE pour une durée de 24h"
        modalitesPedago = @("Supports pédagogiques numérisés remis en amont de l'accompagnement", "Accompagnement individualisé et personnalisé", "Apports conceptuels", "Mises en pratique autour de cas concrets", "Partage d'expériences")
    },
    @{
        slug = "vae-analyse-livret-2"
        title = "VAE - Analyse du Livret 2"
        cardTitle = "Analyse du Livret 2"
        image = "../wp-content/uploads/2024/08/educateur-specialise-850-1.jpg"
        intro = "Un accompagnement ciblé pour l'analyse approfondie de votre livret 2 en vue de l'obtention du DEASS, DEES, DEME, DECESF, DEAES, DEEJE."
        actualise = "25/11/2025"
        duree = "4h30"
        modalite = "100% Distanciel"
        cout = "500 € TTC"
        modaliteDetail = "Session d'accompagnement VAE disponible à l'année pour 4h30 en distanciel à effectuer en 2 mois maximum selon le calendrier de dépôt des dossiers et les besoins du candidat."
        lieu = "Distanciel uniquement : Teams ou visio WhatsApp"
        programme = @(
            @{titre = "Lecture & analyse asynchrone (3h)"; items = @("Lecture approfondie du livret 2 par le formateur en amont des rencontres", "Analyse et préparation des retours méthodologiques")},
            @{titre = "Retour en face à face (1h)"; items = @("Échange avec le formateur sur les axes d'amélioration", "Conseils méthodologiques personnalisés")},
            @{titre = "Validation des réajustements (30min)"; items = @("Vérification des modifications apportées par le candidat", "Validation finale du livret 2")}
        )
        validation = "Remise d'une attestation d'accompagnement à la VAE pour une durée de 4h30"
        modalitesPedago = @("Accompagnement individualisé et personnalisé", "Apports conceptuels", "Mises en pratique autour de cas concrets", "Partage d'expériences")
    },
    @{
        slug = "vae-analyse-domaine-competence"
        title = "VAE - Analyse d'un Domaine de Compétence"
        cardTitle = "Analyse d'un Domaine de Compétence"
        image = "../wp-content/uploads/2024/08/formation-moniteur-educateur-1.jpg"
        intro = "Un accompagnement focalisé sur un domaine de compétence spécifique de votre livret 2 pour le DEASS, DEES, DEME, DECESF, DEAES, DEEJE."
        actualise = "25/11/2025"
        duree = "2h30"
        modalite = "100% Distanciel"
        cout = "250 € TTC"
        modaliteDetail = "Session d'accompagnement VAE disponible à l'année pour 2h30 en distanciel selon le calendrier de dépôt des dossiers et les besoins du candidat."
        lieu = "Distanciel uniquement : Teams ou visio WhatsApp"
        programme = @(
            @{titre = "Analyse asynchrone (1h30)"; items = @("Lecture et analyse du domaine de compétence par le formateur", "Préparation des retours et axes d'amélioration")},
            @{titre = "Retour en face à face (1h)"; items = @("Échange ciblé sur le domaine de compétence", "Conseils méthodologiques pour valoriser l'expérience")}
        )
        validation = "Remise d'une attestation d'accompagnement à la VAE pour une durée de 2h30"
        modalitesPedago = @("Accompagnement individualisé et personnalisé", "Apports conceptuels", "Partage d'expériences")
    },
    @{
        slug = "vae-livret-2-et-oral"
        title = "VAE - Analyse du Livret 2 + Préparation à l'Oral"
        cardTitle = "Livret 2 + Préparation Orale"
        image = "../wp-content/uploads/2024/08/educateur-specialise-850.jpg"
        intro = "Un accompagnement complet combinant l'analyse de votre livret 2 et la préparation à l'épreuve orale avec le jury, pour le DEASS, DEES, DEME, DECESF, DEAES, DEEJE."
        actualise = "25/11/2025"
        duree = "8h30"
        modalite = "100% Distanciel"
        cout = "900 € TTC"
        modaliteDetail = "Session d'accompagnement VAE disponible à l'année pour 8h30 en distanciel à effectuer en 2 mois maximum selon le calendrier de dépôt des dossiers et les besoins du candidat."
        lieu = "Distanciel uniquement : Teams ou visio WhatsApp"
        programme = @(
            @{titre = "Étape 1 : Analyse du Livret 2 (4h30)"; items = @("Lecture et analyse du livret 2 par le formateur en asynchrone (3h)", "Retour en face à face par le formateur (1h)", "Retour sur les réajustements effectués par le candidat (30 min)")},
            @{titre = "Étape 2 : Préparation à l'oral (4h)"; items = @("Recommandations et préparation à l'entretien en face à face (1h)", "Simulation d'entretien en face à face avec retour (1h30)", "Simulation d'entretien complémentaire (1h)", "Entretien post-jury pour échanger autour du résultat et des suites en cas de validation partielle (30 min)")}
        )
        validation = "Remise d'une attestation d'accompagnement à la VAE pour une durée de 8h30"
        modalitesPedago = @("Supports pédagogiques numérisés remis en amont de l'accompagnement", "Accompagnement individualisé et personnalisé", "Apports conceptuels", "Mises en pratique autour de cas concrets", "Partage d'expériences")
    },
    @{
        slug = "vae-preparation-oral"
        title = "VAE - Préparation à l'Oral du Jury"
        cardTitle = "Préparation à l'Oral"
        image = "../wp-content/uploads/2024/08/educateur-specialise-850-1.jpg"
        intro = "Un accompagnement spécifique pour vous préparer à l'épreuve orale devant le jury VAE pour le DEASS, DEES, DEME, DECESF, DEAES, DEEJE."
        actualise = "25/11/2025"
        duree = "2h30"
        modalite = "100% Distanciel"
        cout = "550 € TTC"
        modaliteDetail = "Session d'accompagnement VAE disponible à l'année pour 2h30 en distanciel à effectuer en 2 mois maximum selon le calendrier de dépôt des dossiers et les besoins du candidat."
        lieu = "Distanciel uniquement : Teams ou visio WhatsApp"
        programme = @(
            @{titre = "Recommandations & préparation (1h)"; items = @("Préciser le rôle et les attributions du jury certificateur", "Rappeler les règles et les techniques de l'entretien oral", "Conseils sur la gestion du stress, du temps et de l'argumentation devant un jury")},
            @{titre = "Simulation d'entretien (1h30)"; items = @("Mise en condition réelle d'épreuve orale face au formateur", "Retour critique sur la prestation orale", "Choix des éléments les plus pertinents pour l'oral", "Entretien post-jury pour échanger autour du résultat et des suites en cas de validation partielle")}
        )
        validation = "Remise d'une attestation d'accompagnement à la VAE pour une durée de 2h30"
        modalitesPedago = @("Accompagnement individualisé et personnalisé", "Apports conceptuels", "Partage d'expériences")
    }
)

# Common objectifs and other shared content
$objectifsGeneraux = @(
    "Reconnaître votre expérience acquise et la faire reconnaître par un diplôme",
    "Mettre en cohérence votre certification avec votre niveau de responsabilité",
    "Faire reconnaître vos compétences",
    "Obtenir un niveau de qualification permettant d'accéder à une formation d'un niveau supérieur",
    "Changer d'emploi",
    "Évoluer professionnellement"
)
$publicConcerne = "Cette formation s'adresse à toute personne pouvant justifier d'au moins un an d'expérience en rapport direct avec la certification visée, soit 1607 heures (continu ou non), sous un ou plusieurs statuts (salariés, travailleurs indépendants, bénévoles…)."
$prerequis = "Cet accompagnement s'adresse à toutes personnes ayant obtenu un accord de recevabilité de leur livret d'accessibilité (livret 1)."
$certification = "Certificateur : Ministère de l'Enseignement supérieur et de la Recherche et Ministère chargé de la Solidarité. La VAE n'est pas une transformation automatique de l'expérience en diplôme. Seul le jury de certification reste souverain à attribuer ou non le diplôme visé."
$accessibilite = "Nous sommes à votre écoute pour toutes questions relatives à l'accessibilité aux personnes porteuses d'un handicap. Merci de contacter notre référent handicap : 2aa.formation@gmail.com"

function Build-ContentSection {
    param($fiche)

    $progHtml = ""
    foreach($p in $fiche.programme){
        $itemsHtml = ""
        foreach($i in $p.items){
            $itemsHtml += "<li style=`"padding:6px 0;display:flex;align-items:flex-start;gap:12px;font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;`"><svg aria-hidden=`"true`" style=`"width:8px;height:12px;fill:var(--e-global-color-blocksy_palette_2);flex-shrink:0;margin-top:6px;`" viewBox=`"0 0 320 512`" xmlns=`"http://www.w3.org/2000/svg`"><path d=`"M285.476 272.971L91.132 467.314c-9.373 9.373-24.569 9.373-33.941 0l-22.667-22.667c-9.357-9.357-9.375-24.522-.04-33.901L188.505 256 34.484 101.255c-9.335-9.379-9.317-24.544.04-33.901l22.667-22.667c9.373-9.373 24.569-9.373 33.941 0L285.475 239.03c9.373 9.372 9.373 24.568.001 33.941z`"/></svg><span>$i</span></li>"
        }
        $progHtml += @"
<div style="background:#ffffff;border-radius:8px;padding:25px 30px;margin-bottom:20px;border-left:4px solid var(--e-global-color-blocksy_palette_2);box-shadow:0 2px 8px rgba(0,0,0,0.04);">
<h3 style="font-family:'Raleway',Sans-serif;font-size:22px;font-weight:700;color:#1d2f52;margin:0 0 15px 0;">$($p.titre)</h3>
<ul style="list-style:none;padding:0;margin:0;">$itemsHtml</ul>
</div>
"@
    }

    $objGenHtml = ""
    foreach($o in $objectifsGeneraux){
        $objGenHtml += "<li style=`"padding:8px 0;display:flex;align-items:flex-start;gap:12px;font-family:'Work Sans',Sans-serif;font-size:17px;line-height:1.5em;color:#1d2f52;`"><svg aria-hidden=`"true`" style=`"width:8px;height:12px;fill:var(--e-global-color-blocksy_palette_2);flex-shrink:0;margin-top:6px;`" viewBox=`"0 0 320 512`" xmlns=`"http://www.w3.org/2000/svg`"><path d=`"M285.476 272.971L91.132 467.314c-9.373 9.373-24.569 9.373-33.941 0l-22.667-22.667c-9.357-9.357-9.375-24.522-.04-33.901L188.505 256 34.484 101.255c-9.335-9.379-9.317-24.544.04-33.901l22.667-22.667c9.373-9.373 24.569-9.373 33.941 0L285.475 239.03c9.373 9.372 9.373 24.568.001 33.941z`"/></svg>$o</li>"
    }

    $modPedHtml = ""
    foreach($m in $fiche.modalitesPedago){
        $modPedHtml += "<li style=`"padding:6px 0;display:flex;align-items:flex-start;gap:12px;font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;`"><svg aria-hidden=`"true`" style=`"width:8px;height:12px;fill:var(--e-global-color-blocksy_palette_2);flex-shrink:0;margin-top:6px;`" viewBox=`"0 0 320 512`" xmlns=`"http://www.w3.org/2000/svg`"><path d=`"M285.476 272.971L91.132 467.314c-9.373 9.373-24.569 9.373-33.941 0l-22.667-22.667c-9.357-9.357-9.375-24.522-.04-33.901L188.505 256 34.484 101.255c-9.335-9.379-9.317-24.544.04-33.901l22.667-22.667c9.373-9.373 24.569-9.373 33.941 0L285.475 239.03c9.373 9.372 9.373 24.568.001 33.941z`"/></svg>$m</li>"
    }

    return @"
<div data-elementor-type="wp-page" class="elementor">

<section style="background:#10101A;padding:60px 0 50px 0;width:100vw;position:relative;left:50%;right:50%;margin:0 -50vw;box-sizing:border-box;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;text-align:center;">
<p style="font-family:'Work Sans',Sans-serif;font-size:14px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#a0a3b0;margin:0 0 15px 0;">Programme de formation actualisé le $($fiche.actualise)</p>
<h2 style="font-family:'Raleway',Sans-serif;font-size:42px;font-weight:700;color:#ffffff;margin:0 0 25px 0;line-height:1.2em;">$($fiche.title)</h2>
<p style="font-family:'Work Sans',Sans-serif;font-size:18px;line-height:1.6em;color:#d8dae0;margin:0 auto;max-width:850px;">$($fiche.intro)</p>
</div>
</section>

<section style="background:#ffffff;padding:50px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:25px;">
<div style="background:#F7F8FA;border-radius:8px;padding:25px;text-align:center;">
<div style="width:50px;height:50px;border-radius:50%;background:var(--e-global-color-blocksy_palette_2);margin:0 auto 15px auto;display:flex;align-items:center;justify-content:center;">
<svg width="22" height="22" fill="#ffffff" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8zm0 448c-110.5 0-200-89.5-200-200S145.5 56 256 56s200 89.5 200 200-89.5 200-200 200zm61.8-104.4l-84.9-61.7c-3.1-2.3-4.9-5.9-4.9-9.7V116c0-6.6 5.4-12 12-12h32c6.6 0 12 5.4 12 12v141.7l66.8 48.6c5.4 3.9 6.5 11.4 2.6 16.8L334.6 349c-3.9 5.3-11.4 6.5-16.8 2.6z"/></svg>
</div>
<p style="font-family:'Work Sans',Sans-serif;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:#606a7c;margin:0 0 5px 0;">Durée</p>
<p style="font-family:'Raleway',Sans-serif;font-size:22px;font-weight:700;color:#1d2f52;margin:0;">$($fiche.duree)</p>
</div>
<div style="background:#F7F8FA;border-radius:8px;padding:25px;text-align:center;">
<div style="width:50px;height:50px;border-radius:50%;background:var(--e-global-color-blocksy_palette_2);margin:0 auto 15px auto;display:flex;align-items:center;justify-content:center;">
<svg width="22" height="22" fill="#ffffff" viewBox="0 0 640 512" xmlns="http://www.w3.org/2000/svg"><path d="M96 224c35.3 0 64-28.7 64-64s-28.7-64-64-64-64 28.7-64 64 28.7 64 64 64zm448 0c35.3 0 64-28.7 64-64s-28.7-64-64-64-64 28.7-64 64 28.7 64 64 64zm32 32h-64c-17.6 0-33.5 7.1-45.1 18.6 40.3 22.1 68.9 62 75.1 109.4h66c17.7 0 32-14.3 32-32v-32c0-35.3-28.7-64-64-64zm-256 0c61.9 0 112-50.1 112-112S381.9 32 320 32 208 82.1 208 144s50.1 112 112 112zm76.8 32h-8.3c-20.8 10-43.9 16-68.5 16s-47.6-6-68.5-16h-8.3C179.6 288 128 339.6 128 403.2V432c0 26.5 21.5 48 48 48h288c26.5 0 48-21.5 48-48v-28.8c0-63.6-51.6-115.2-115.2-115.2zm-223.7-13.4C161.5 263.1 145.6 256 128 256H64c-35.3 0-64 28.7-64 64v32c0 17.7 14.3 32 32 32h65.9c6.3-47.4 34.9-87.3 75.2-109.4z"/></svg>
</div>
<p style="font-family:'Work Sans',Sans-serif;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:#606a7c;margin:0 0 5px 0;">Modalité</p>
<p style="font-family:'Raleway',Sans-serif;font-size:18px;font-weight:700;color:#1d2f52;margin:0;">$($fiche.modalite)</p>
</div>
<div style="background:#F7F8FA;border-radius:8px;padding:25px;text-align:center;">
<div style="width:50px;height:50px;border-radius:50%;background:var(--e-global-color-blocksy_palette_2);margin:0 auto 15px auto;display:flex;align-items:center;justify-content:center;">
<svg width="22" height="22" fill="#ffffff" viewBox="0 0 384 512" xmlns="http://www.w3.org/2000/svg"><path d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zm384 64H256V0L384 128z"/></svg>
</div>
<p style="font-family:'Work Sans',Sans-serif;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:#606a7c;margin:0 0 5px 0;">Coût</p>
<p style="font-family:'Raleway',Sans-serif;font-size:22px;font-weight:700;color:#1d2f52;margin:0;">$($fiche.cout)</p>
</div>
</div>
</div>
</section>

<section style="background:#ffffff;padding:30px 0 50px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
<div style="background:#F7F8FA;border-radius:8px;padding:30px;">
<h3 style="font-family:'Raleway',Sans-serif;font-size:24px;font-weight:700;color:#1d2f52;margin:0 0 15px 0;">Professionnels concernés</h3>
<p style="font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;margin:0;">$publicConcerne</p>
</div>
<div style="background:#F7F8FA;border-radius:8px;padding:30px;">
<h3 style="font-family:'Raleway',Sans-serif;font-size:24px;font-weight:700;color:#1d2f52;margin:0 0 15px 0;">Prérequis</h3>
<p style="font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;margin:0;">$prerequis</p>
</div>
</div>
</div>
</section>

<section style="background:#F1F1F1;padding:60px 0;width:100vw;position:relative;left:50%;right:50%;margin:0 -50vw;box-sizing:border-box;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<h2 style="font-family:'Raleway',Sans-serif;font-size:32px;font-weight:700;color:#1d2f52;margin:0 0 30px 0;text-align:center;">Modalités et durée</h2>
<div style="background:#ffffff;border-radius:8px;padding:30px;">
<p style="font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;margin:0 0 15px 0;"><strong>Durée, dates et horaires :</strong> $($fiche.modaliteDetail)</p>
<p style="font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;margin:0;"><strong>Lieu d'accompagnement :</strong> $($fiche.lieu)</p>
</div>
</div>
</section>

<section style="background:#ffffff;padding:60px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<h2 style="font-family:'Raleway',Sans-serif;font-size:32px;font-weight:700;color:#1d2f52;margin:0 0 30px 0;text-align:center;">Objectifs pédagogiques généraux</h2>
<ul style="list-style:none;padding:0;margin:0;max-width:750px;margin:0 auto;">$objGenHtml</ul>
</div>
</section>

<section style="background:#F1F1F1;padding:60px 0;width:100vw;position:relative;left:50%;right:50%;margin:0 -50vw;box-sizing:border-box;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<h2 style="font-family:'Raleway',Sans-serif;font-size:32px;font-weight:700;color:#1d2f52;margin:0 0 30px 0;text-align:center;">Programme de l'accompagnement</h2>
$progHtml
</div>
</section>

<section style="background:#ffffff;padding:60px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
<div style="background:#F7F8FA;border-radius:8px;padding:30px;border-top:4px solid var(--e-global-color-blocksy_palette_2);">
<h3 style="font-family:'Raleway',Sans-serif;font-size:22px;font-weight:700;color:#1d2f52;margin:0 0 15px 0;">Certification des compétences</h3>
<p style="font-family:'Work Sans',Sans-serif;font-size:15px;line-height:1.6em;color:#1d2f52;margin:0;">$certification</p>
</div>
<div style="background:#F7F8FA;border-radius:8px;padding:30px;border-top:4px solid var(--e-global-color-blocksy_palette_2);">
<h3 style="font-family:'Raleway',Sans-serif;font-size:22px;font-weight:700;color:#1d2f52;margin:0 0 15px 0;">Validation de l'accompagnement</h3>
<p style="font-family:'Work Sans',Sans-serif;font-size:15px;line-height:1.6em;color:#1d2f52;margin:0;">$($fiche.validation)</p>
</div>
</div>
</div>
</section>

<section style="background:#10101A;padding:60px 0;width:100vw;position:relative;left:50%;right:50%;margin:0 -50vw;box-sizing:border-box;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;text-align:center;">
<h2 style="font-family:'Raleway',Sans-serif;font-size:32px;font-weight:700;color:#ffffff;margin:0 0 15px 0;">Coût & Financements</h2>
<p style="font-family:'Raleway',Sans-serif;font-size:48px;font-weight:700;color:var(--e-global-color-blocksy_palette_2);margin:0 0 20px 0;">$($fiche.cout)</p>
<p style="font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#d8dae0;margin:0 0 25px 0;"><strong style="color:#ffffff;">Financements possibles :</strong> Employeur · Opérateur de compétences · Financement individuel · France Travail · CPF</p>
<p style="font-family:'Work Sans',Sans-serif;font-size:14px;color:#a0a3b0;margin:0;">Pas de frais d'inscription ou de dossier</p>
</div>
</section>

<section style="background:#ffffff;padding:60px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<h2 style="font-family:'Raleway',Sans-serif;font-size:32px;font-weight:700;color:#1d2f52;margin:0 0 30px 0;text-align:center;">Modalités pédagogiques</h2>
<ul style="list-style:none;padding:0;margin:0 auto;max-width:750px;">$modPedHtml</ul>
</div>
</section>

<section style="background:#F1F1F1;padding:50px 0;width:100vw;position:relative;left:50%;right:50%;margin:0 -50vw;box-sizing:border-box;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;">
<div style="background:#ffffff;border-radius:8px;padding:30px;text-align:center;">
<h3 style="font-family:'Raleway',Sans-serif;font-size:22px;font-weight:700;color:#1d2f52;margin:0 0 15px 0;">Accessibilité aux personnes porteuses de handicap</h3>
<p style="font-family:'Work Sans',Sans-serif;font-size:15px;line-height:1.6em;color:#1d2f52;margin:0;">$accessibilite</p>
</div>
</div>
</section>

<section style="background:#ffffff;padding:60px 0 80px 0;">
<div style="max-width:1100px;margin:0 auto;padding:0 30px;text-align:center;">
<h2 style="font-family:'Raleway',Sans-serif;font-size:32px;font-weight:700;color:#1d2f52;margin:0 0 20px 0;">Vous êtes intéressé(e) ?</h2>
<p style="font-family:'Work Sans',Sans-serif;font-size:16px;line-height:1.6em;color:#1d2f52;margin:0 0 30px 0;">Contactez-nous pour échanger sur votre projet VAE et construire ensemble votre accompagnement personnalisé.</p>
<a href="../contact/index.html" style="display:inline-block;background:var(--e-global-color-blocksy_palette_2);color:#ffffff;font-family:'Work Sans',Sans-serif;font-size:17px;font-weight:600;padding:16px 40px;border-radius:6px;text-decoration:none;border:2px solid var(--e-global-color-blocksy_palette_2);transition:all 0.3s;">Nous contacter →</a>
</div>
</section>

</div>
"@
}

foreach($fiche in $fiches){
    $folder = Join-Path $base $fiche.slug
    if(-not (Test-Path $folder)){ New-Item -ItemType Directory -Path $folder | Out-Null }

    # Customize top: change title and h1
    $customTop = $top -replace [regex]::Escape('<title>Nos VAE - 2aFormation</title>'), "<title>$($fiche.title) - 2aFormation</title>"
    $customTop = $customTop -replace [regex]::Escape('<meta property="og:title" content="Nos VAE - 2aFormation" />'), "<meta property=`"og:title`" content=`"$($fiche.title) - 2aFormation`" />"
    $customTop = $customTop -replace [regex]::Escape('<link rel="canonical" href="../nos-vae/index.html" />'), "<link rel=`"canonical`" href=`"../$($fiche.slug)/index.html`" />"
    $customTop = $customTop -replace [regex]::Escape('<meta property="og:url" content="https://2aformation.com/nos-vae/" />'), "<meta property=`"og:url`" content=`"https://2aformation.com/$($fiche.slug)/`" />"
    $customTop = $customTop -replace [regex]::Escape('<h1 class="page-title" itemprop="headline">Nos VAE</h1>'), "<h1 class=`"page-title`" itemprop=`"headline`">$($fiche.cardTitle)</h1>"

    $contentHtml = Build-ContentSection -fiche $fiche

    $outFile = Join-Path $folder "index.html"
    $fullHtml = $customTop + "`n" + $contentHtml + "`n" + $bottom
    [System.IO.File]::WriteAllText($outFile, $fullHtml, [System.Text.UTF8Encoding]::new($false))
    Write-Output "Created: $outFile"
}
