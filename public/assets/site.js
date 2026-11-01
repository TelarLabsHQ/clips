(function () {
  // Hover previews on cards (desktop with a real pointer only, to save mobile data)
  var canHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (canHover) {
    document.querySelectorAll('.card').forEach(function (card) {
      var v = card.querySelector('video');
      if (!v) return;
      card.addEventListener('mouseenter', function () {
        if (!v.src) v.src = v.dataset.src;
        var p = v.play(); if (p && p.catch) p.catch(function () {});
        v.classList.add('on');
      });
      card.addEventListener('mouseleave', function () { v.pause(); v.classList.remove('on'); });
    });
  }

  // Search + category filter (home page)
  var q = document.getElementById('q');
  var chips = document.querySelectorAll('#browse .chip');
  var browse = document.getElementById('browse');
  if (browse) {
    var cards = browse.querySelectorAll('.card');
    var count = document.getElementById('count');
    var empty = document.getElementById('empty');
    var cat = '';
    var apply = function () {
      var words = (q && q.value || '').toLowerCase().trim().split(/\s+/).filter(Boolean);
      var shown = 0;
      cards.forEach(function (c) {
        var okCat = !cat || c.dataset.cats.split('|').indexOf(cat) >= 0;
        var okText = words.every(function (w) { return c.dataset.text.indexOf(w) >= 0; });
        var on = okCat && okText; c.hidden = !on; if (on) shown++;
      });
      browse.querySelectorAll('.ad-grid').forEach(function (a) { a.hidden = !!(cat || words.length); });
      if (count) count.textContent = shown + (shown === 1 ? ' clip' : ' clips');
      if (empty) empty.hidden = shown > 0;
    };
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        chips.forEach(function (x) { x.classList.remove('is-on'); });
        ch.classList.add('is-on'); cat = ch.dataset.cat; apply();
      });
    });
    if (q) {
      var params = new URLSearchParams(location.search);
      if (params.get('q')) { q.value = params.get('q'); apply(); }
      q.addEventListener('input', apply);
      q.form.addEventListener('submit', function (e) {
        e.preventDefault(); apply(); browse.scrollIntoView({ behavior: 'smooth' });
      });
    }
  }

  // Download: the media server sends the file as an attachment, so a normal link starts the download.
  document.querySelectorAll('[data-download]').forEach(function (a) {
    a.addEventListener('click', function () {
      var label = a.lastChild, old = label.textContent;
      label.textContent = ' Download starting…';
      setTimeout(function () { label.textContent = old; }, 4000);
    });
  });
})();
