/* ==========================================================================
   CHIFFRES DU SITE PILOTÉS PAR GOOGLE SHEETS (API v4)
   --------------------------------------------------------------------------
   Pour CHANGER les chiffres : modifie ton Google Sheet, c'est tout.
   Ce fichier est partagé entre la page d'accueil et la page nos-vae.

   À REMPLIR UNE SEULE FOIS (voir la notice) :
   ========================================================================== */
(function(){
  var ID_DU_SHEET = '13XfHYoZKJhLaXY16LzKZKDypJ41miS_D9qGTq4OAENs';   // ex: 1AbCdEf...XyZ
  var CLE_API     = 'AIzaSyDBlxFvJq9Prw6DIaOBzpbk2lu4HiNgcI4';       // ex: AIzaSy...
  var PLAGE       = 'Chiffre!A1:D40';            // onglet!plage (renomme l'onglet en Feuille1, ou adapte ici)

  /* --------------------------------------------------------------------------
     CORRESPONDANCE : étiquette de la page  ->  [ligne, colonne] dans le Sheet
     (ligne et colonne comptées à partir de 1, comme dans Google Sheets :
      colonne A=1, B=2, C=3, D=4 ; ligne 1 = première ligne)
     NE PAS modifier sauf si tu changes la disposition du Sheet.
     -------------------------------------------------------------------------- */
  var CORRESPONDANCE = {
    // En-tête
    annee:                 [1, 2],   // A1 label, B1 valeur

    // Tableau "Résultat" : colonnes DE ASS=B(2), DE ES=C(3), DE ME=D(4)
    ass_inscrits:          [3, 2],  es_inscrits:           [3, 3],  me_inscrits:           [3, 4],
    ass_presentes:         [4, 2],  es_presentes:          [4, 3],  me_presentes:          [4, 4],
    ass_diplome:           [5, 2],  es_diplome:            [5, 3],  me_diplome:            [5, 4],
    ass_validation:        [6, 2],  es_validation:         [6, 3],  me_validation:         [6, 4],
    ass_abandon:           [7, 2],  es_abandon:            [7, 3],  me_abandon:            [7, 4],
    ass_poursuite:         [8, 2],  es_poursuite:          [8, 3],  me_poursuite:          [8, 4],
    ass_taux_reussite:     [9, 2],  es_taux_reussite:      [9, 3],  me_taux_reussite:      [9, 4],
    ass_taux_abandon:      [10, 2], es_taux_abandon:       [10, 3], me_taux_abandon:       [10, 4],
    ass_taux_satisfaction: [11, 2], es_taux_satisfaction:  [11, 3], me_taux_satisfaction:  [11, 4],

    // Bloc "Nos résultats VAU" (les 3 compteurs du haut de la page nos-vae)
    inscrits:              [14, 2],
    taux_reussite:         [15, 2],
    taux_satisfaction:     [16, 2],

    // Bloc "Formation" (les 3 compteurs de la page d'accueil)
    stagiaires:               [19, 2],
    formations:               [20, 2],
    satisfaction_formation:   [21, 2]
  };
  /* ===================== FIN DE LA CONFIGURATION ============================ */


  // ---- Animation des compteurs "maison" (.vae-counter) de la page nos-vae ----
  var counters = document.querySelectorAll('.vae-counter');
  var animated = false;
  function animate(el){
    var target = parseInt(el.getAttribute('data-target'), 10) || 0;
    var duration = 2000, start = null;
    function step(ts){
      if(!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      el.textContent = Math.floor(progress * target);
      if(progress < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  }
  function check(){
    if(animated || !counters.length) return;
    var rect = counters[0].getBoundingClientRect();
    if(rect.top < window.innerHeight && rect.bottom > 0){
      animated = true;
      counters.forEach(animate);
    }
  }
  function demarrerCompteurs(){
    if(!counters.length) return;
    window.addEventListener('scroll', check, {passive:true});
    window.addEventListener('load', check);
    check();
  }

  // ---- Pose une valeur sur tous les éléments portant l'étiquette donnée ----
  function poser(cle, valeur){
    document.querySelectorAll('[data-cle="' + cle + '"]').forEach(function(el){
      if(el.classList.contains('vae-counter')){
        el.setAttribute('data-target', parseInt(valeur, 10) || 0);
      } else if(el.classList.contains('elementor-counter-number')){
        var n = String(valeur).replace(/[^0-9.,]/g, '');   // Elementor n'anime que le nombre
        el.setAttribute('data-to-value', n);
        // si Elementor a déjà animé ce compteur, on corrige directement l'affichage
        if(el.textContent && el.textContent.trim() !== '0'){ el.textContent = n; }
      } else {
        el.textContent = valeur;                            // cellule de tableau / texte
      }
    });
  }

  function cellule(values, ligne, colonne){
    var r = values[ligne - 1];
    if(!r) return undefined;
    var v = r[colonne - 1];
    return (v != null) ? String(v).trim() : undefined;
  }

  function appliquer(values){
    Object.keys(CORRESPONDANCE).forEach(function(cle){
      var pos = CORRESPONDANCE[cle];
      var v = cellule(values, pos[0], pos[1]);
      if(v !== undefined && v !== '') poser(cle, v);
    });
  }

  function charger(){
    if(ID_DU_SHEET.indexOf('COLLE_ICI') === 0 || CLE_API.indexOf('COLLE_ICI') === 0){
      demarrerCompteurs();   // pas encore configuré : on garde les valeurs écrites dans les pages
      return;
    }
    var url = 'https://sheets.googleapis.com/v4/spreadsheets/' + ID_DU_SHEET +
              '/values/' + encodeURIComponent(PLAGE) + '?key=' + CLE_API;
    fetch(url)
      .then(function(r){ return r.json(); })
      .then(function(data){ if(data && data.values) appliquer(data.values); })
      .catch(function(){ /* échec réseau : on garde les valeurs par défaut des pages */ })
      .then(function(){ demarrerCompteurs(); });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', charger);
  } else {
    charger();
  }
})();
