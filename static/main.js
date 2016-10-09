'use strict';

// gallery handling
(function() {
  var els = document.getElementsByClassName('toggler');
  
  for (var i = 0, l = els.length; i < l; i++) {
    els[i].addEventListener('click', onclick);
  }

  function onclick(ev) {
    var t = ev.target;
    var gallery = t.parentNode.getElementsByClassName('gallery')[0];
    var raw = t.parentNode.getElementsByClassName('gallery-raw')[0];
    var show_now = gallery.style.display == 'none';

    t.innerHTML = show_now ? '&#x25bc;' : '&#x25b6;';
    gallery.style.display = show_now ? 'block' : 'none';

    if (raw && show_now) { gallery.insertAdjacentHTML('beforeend', raw.innerHTML); }
    else { gallery.innerHTML = ''; }
  }
})();

// search handling
(function() {
    // collect indexes on dt
    var nodes = document.getElementsByTagName('dt');
    for (var i = 0, l = nodes.length; i < l; i++) {
        var el = nodes[i], next = el, index = [];
        while ((next = next.nextElementSibling) && !next.id) {
            if (next.tagName != 'DD')
                continue;
            index.push(next.getAttribute('data-index'));
        }
        el.setAttribute('data-index', index.join(' '));
    };

    var getfilter = function(term) {
        return !term ? "" :
            '[data-index*="' + term.toLowerCase().replace('"', '') + '"]';
    }

    var style = document.getElementById('filter-style');
    document.getElementById('filter').addEventListener('input', function() {
        if (!this.value) {
            style.innerHTML = "";
            return;
        }
        style.innerHTML =
            ".searchable {display: none} .searchable" +
            this.value.split(' ').map(getfilter).join('') +
            "{display: block}";
    });
})();

// tag handling
(function() {
  var games = document.getElementsByTagName('dd');
  var tags = document.getElementsByClassName('tag');
  var activeTag;

  for (var i = 0, l = tags.length; i < l; i += 1) {
    tags[i].addEventListener('click', onclick);
  }

  function onclick(e) {
    var t = e.target.hasAttribute('data-name') ? e.target : e.target.parentNode;
    var curTag = t.getAttribute('data-name');
    var parent;
    var game, gameTags;

    if (curTag === activeTag) {
      activeTag = null;
      document.body.classList.remove('tags-active');
      highlightTags(null);
    } else {
      activeTag = curTag;
      document.body.classList.add('tags-active');
      highlightTags(curTag);
    }

    for (var i = 0, len = games.length; i < len; i += 1) {
      game = games[i];
      gameTags = game.getAttribute('data-tags').split(' ');
      parent = document.getElementById(game.getAttribute('data-parent'));

      if (gameTags && gameTags.indexOf(curTag) > -1) {
        if (!game.classList.contains('active')) {
          game.classList.add('active');
          parent.classList.add('active');
        }
      } else if (game.classList.contains('active')) {
        game.classList.remove('active');
        parent.classList.remove('active');
      }
    }
  }

  function highlightTags(tag) {
    var style = document.getElementById('tag-style');
    var line = '[data-name=\"' + tag + '\"] { color: #ccc; background: #444; }';
    style.innerHTML = tag ? line : '';
  }
})();
