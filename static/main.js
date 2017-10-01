'use strict';

var OSGC = window.OSGC = {};

// menu
(function() {
  const nav = document.getElementById('nav');
  const btns = Array.from(document.getElementsByClassName('nav-btn'));
  nav.addEventListener('click', menuclick);

  function menuclick(ev) {
    const t = ev.target;

    if (t.classList.contains('nav-btn')) {
      const wasActive = t.parentNode.classList.contains('active');
      btns.forEach((btn) => btn.parentNode.classList.remove('active'));
      if (!wasActive) { t.parentNode.classList.add('active') };
    }
  }
})();

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

// image validation
(function() {
  OSGC.getImages = getImages;
  OSGC.downloadImage = downloadImage;
  OSGC.validate = validate;

  function init() {
    OSGC.brokenLinks = {};
    OSGC.invalidImages = {
      forAnts: [],
      tooSmall: [],
      tooBig: [],
      tooSlow: []
    };
  }

  init();

  function getImages() {
    let galleries = document.getElementsByClassName('gallery-json');
    let galleries_len = galleries.length;
    let images = [];

    for (let i = 0; i < galleries_len; i += 1) {
      let g = galleries[i];
      let game = g.getAttribute('data-game');
      let cur = g.innerHTML.trim().split(', ').map(
        function addGameName(url) {
          return { url: url, name: game };
        }
      );
      images = images.concat(cur);
    }

    console.info('Galleries:', galleries.length);
    console.info('Images:', images.length);

    return images;
  }

  function validateImage(image, loadTime) {
    let width = image.naturalWidth;
    if (width < 200) { OSGC.invalidImages.forAnts.push(image.src); }
    else if (width < 400) { OSGC.invalidImages.tooSmall.push(image.src); }
    else if (width > 2000) { OSGC.invalidImages.tooBig.push(image.src); }

    if (loadTime > 5000) { OSGC.invalidImages.tooSlow.push(image.src); }
  }

  function downloadImage(dimage) {
    return new Promise(function (resolve, reject) {
      let timeStart = new Date().getTime();
      let image = new Image();
      image.onload = onload;
      image.onerror = onerror;
      image.src = dimage.url;

      function time() { return new Date().getTime() - timeStart; }
      function onload() { resolve({image: image, time: time()}); }
      function onerror() {
        reject({
          name: dimage.name,
          url: dimage.url,
          time: time()
        });
      }
    });
  }

  function reflect(promise){
      function resolved(value) { validateImage(value.image, value.time); }
      function rejected(err) {
        let bad = OSGC.brokenLinks[err.name];
        if (!bad) { bad = OSGC.brokenLinks[err.name] = []; }
        bad.push(err.url);
      }

      return promise.then(resolved, rejected);
  }

  function downloadImages(images) {
    return Promise.all(images.map(downloadImage).map(reflect));
  }

  function showResults() {
    console.group('Results');
    console.log('Invalid images: %O', OSGC.invalidImages);
    console.log('Bad links: %O', OSGC.brokenLinks);
    console.groupEnd();
  }

  function validate(beginAt, turnsMax, concurrentMax) {
    let images = getImages();
    let images_len = images.length;

    let cur = beginAt - 1 || -1;
    let turns = cur && turnsMax ? cur + turnsMax : -2;
    let max = concurrentMax || 10;

    let arrBegin, arrEnd;
    init(); // reset

    function next() {
      cur += 1;
      arrBegin = cur * max;
      arrEnd = cur * max + max;
      console.log('Progress:', arrEnd, '/', images_len);
      return downloadImages(images.slice(arrBegin, arrEnd));
    }

    function queue() {
      if (cur === turns || cur >= images_len / max) {
        return Promise.resolve();
      } else {
        return next().then(queue);
      }
    }

    return Promise.resolve().then(queue).then(showResults);
  }

  function toggleDarkMode() {
    if (document.body.classList.contains('darkMode')) {
      document.body.classList.remove('darkMode');
    } else {
      document.body.classList.add('darkMode');
    }
  }

  document.getElementById('darkModeButton').addEventListener('click', toggleDarkMode)
})();
