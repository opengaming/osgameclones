'use strict';

// screenshot handling
(function() {
  var onclick = function() {
    var screenshots = this.parentNode.getElementsByTagName("script");
    if (screenshots.length) {
        var innerHTML = '<div class="screenshots" style="display: none">' +
                        screenshots[0].innerHTML + '</div>';
        this.parentNode.insertAdjacentHTML('beforeend', innerHTML);
        this.parentNode.removeChild(screenshots[0]);
    }
    screenshots = this.parentNode.getElementsByClassName("screenshots")[0];
    var show_now = screenshots.style.display == "none";
    this.innerHTML = show_now ? "&#x25bc;" : "&#x25b6;";
    screenshots.style.display = show_now ? "block" : "none";
  }
  var els = document.getElementsByClassName("toggler");
  for (var i = 0, l = els.length; i < l; i++) {
    els[i].addEventListener("click", onclick);
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

  for (var i = 0, l = tags.length; i < l; i += 1) {
    tags[i].addEventListener('click', onclick);
  }

  function onclick(e) {
    var t = e.target.hasAttribute('data-name') ? e.target : e.target.parentNode;
    var parent;
    var game, gameTags;

    if (!hasClass(document.body, 'tags-active')) {
      document.body.className += ' tags-active';
    }

    for (var i = 0, len = games.length; i < len; i += 1) {
      game = games[i];
      gameTags = game.getAttribute('data-tags').split(' ');
      parent = document.getElementById(game.getAttribute('data-parent'));

      if (gameTags && gameTags.indexOf(t.getAttribute('data-name')) > -1) {
        highlightTags(t.getAttribute('data-name'));

        if (!hasClass(game, 'active')) {
          game.className += ' active';
          parent.className += ' active';
        }
      } else if (hasClass(game, 'active')) {
        game.className = game.className.replace('active', '').trim();
        parent.className = parent.className.replace('active', '').trim();
      }
    }
  }

  function highlightTags(tag) {
    var style = document.getElementById('tag-style');
    var lines = [
      '[data-name=\"' + tag + '\"] { color: #ccc; background: #444; };'
    ];

    if (tag) {
      style.innerHTML = lines.join('\n');
    } else {
      style.innerHTML = '';
    }
  }

  function hasClass(node, name) {
    return node.className.indexOf(name) === -1 ? false : true;
  }
})();
