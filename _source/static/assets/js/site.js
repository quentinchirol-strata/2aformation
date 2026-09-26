/* 2aFormation — scripts du site */
(function () {
  // Menu mobile
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  // Filtre du catalogue
  var filters = document.querySelectorAll('.filters button');
  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var theme = btn.getAttribute('data-theme');
      filters.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      document.querySelectorAll('.card[data-theme]').forEach(function (card) {
        card.hidden = theme !== 'all' && card.getAttribute('data-theme') !== theme;
      });
    });
  });

  // Pré-remplissage du formulaire depuis l'adresse (ex. ?sujet=...)
  var form = document.getElementById('contact-form');
  if (!form) return;
  try {
    var params = new URLSearchParams(window.location.search);
    var sujet = params.get('sujet');
    var profil = params.get('profil');
    if (sujet) form.elements.message.value = sujet;
    if (profil && form.elements.profil) form.elements.profil.value = profil;
  } catch (e) {}

  var status = document.getElementById('form-status');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.elements.site && form.elements.site.value) return; // anti-spam
    var f = form.elements;
    if (!f.nom.value.trim() || !f.email.value.trim() || !f.message.value.trim()) {
      status.className = 'form-status error';
      status.textContent = 'Merci de renseigner votre nom, votre e-mail et votre besoin.';
      return;
    }
    var endpoint = form.getAttribute('data-endpoint');
    var corps = 'Profil : ' + f.profil.value + '\nNom : ' + f.nom.value + '\nStructure : ' + f.structure.value +
      '\nE-mail : ' + f.email.value + '\nTéléphone : ' + f.tel.value + '\n\n' + f.message.value;
    if (endpoint) {
      status.className = 'form-status';
      status.textContent = 'Envoi en cours…';
      fetch(endpoint, { method: 'POST', headers: { 'Accept': 'application/json' }, body: new FormData(form) })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          status.textContent = 'Merci, votre demande est envoyée. Nous vous répondons sous 48 h ouvrées.';
        })
        .catch(function () {
          status.className = 'form-status error';
          status.textContent = "L'envoi n'a pas abouti. Écrivez-nous directement à " + form.getAttribute('data-email') + '.';
        });
    } else {
      var sujetMail = 'Demande depuis le site : ' + f.profil.value;
      window.location.href = 'mailto:' + form.getAttribute('data-email') + '?subject=' +
        encodeURIComponent(sujetMail) + '&body=' + encodeURIComponent(corps);
      status.className = 'form-status';
      status.textContent = 'Votre messagerie s’ouvre avec la demande pré-remplie. Si rien ne se passe, écrivez-nous à ' + form.getAttribute('data-email') + '.';
    }
  });
})();
