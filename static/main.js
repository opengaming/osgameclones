'use strict';

var OSGC = window.OSGC = {};
var params = window.params = {};
var activeTag = window.activeTag = null;

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
function getFilter(term) {
  return !term ? "" :
    '[data-index*="' + term.toLowerCase().replace('"', '') + '"]';
}

var filterStyle = document.getElementById('filter-style');

function filter(filter_value) {
  if (!filter_value) {
    setQueryParams('filter', null);
    filterStyle.innerHTML = "";
    setCount();
    return;
  }
  setQueryParams('filter', filter_value);
  filterStyle.innerHTML =
    ".searchable {display: none} .searchable" +
    filter_value.split(' ').map(getFilter).join('') +
    "{display: block}";
  setCount();
}

(function() {
  // collect indexes on dt
  var nodes = document.getElementsByTagName('dt');
  for (var i = 0, l = nodes.length; i < l; i++) {
    var el = nodes[i], next = el, index = [];
    while ((next = next.nextElementSibling) && !next.id) {
      if (next.tagName != 'DIV')
        continue;
      var childs = next.children;
      for (var child of childs) {
        index.push(child.getAttribute('data-index'));
      }
    }
    el.setAttribute('data-index', index.join(' '));
  };

  document.getElementById('filter').addEventListener('input', function() {
    filter(this.value);
  });
})();

// tag handling
function filterByTag(curTag) {
  var games = document.getElementsByTagName('dd');
  var game, gameTags;
  var parent;

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
  setCount();
}

function highlightTags(tag) {
  var style = document.getElementById('tag-style');
  var line = '.tag[data-name=\"' + tag + '\"] { color: #ccc; background-color: #444; }';
  line += '.darkTheme .tag[data-name=\"' + tag + '\"] { color: #444; background-color: #ccc; }';
  style.innerHTML = tag ? line : '';
}

(function() {
  var tags = document.getElementsByClassName('tag');

  for (var i = 0, l = tags.length; i < l; i += 1) {
    tags[i].addEventListener('click', onclick);
  }

  function onclick(e) {
    var t = e.target.hasAttribute('data-name') ? e.target : e.target.parentNode;
    var curTag = t.getAttribute('data-name');

    if (curTag === activeTag) {
      activeTag = null;
      document.body.classList.remove('tags-active');
      highlightTags(null);
      setQueryParams('tag', null);
    } else {
      activeTag = curTag;
      document.body.classList.add('tags-active');
      highlightTags(curTag);
      setQueryParams('tag', curTag);
    }
    
    filterByTag(curTag);
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

  // Dark theme
  function toggleDarkTheme() {
    if (document.body.classList.contains('darkTheme')) {
      document.body.classList.remove('darkTheme');
      localStorage.setItem('startInDarkTheme', 'false')
    } else {
      document.body.classList.add('darkTheme');
      localStorage.setItem('startInDarkTheme', 'true')
    }
  }

  document.getElementById('darkThemeButton').addEventListener('click', toggleDarkTheme)

  // Lazy load badges when they become visible (avoid error 429)
  var lazyloadHandler = function(e) {
    var elements = document.querySelectorAll("img.lazyload");
    for (var i = 0; i < elements.length; i++) {
      var boundingClientRect = elements[i].getBoundingClientRect();
      if (
        elements[i].hasAttribute("data-src") &&
        boundingClientRect.top < window.innerHeight &&
        // Ensure parent game is not hidden
        elements[i].offsetParent != null
      ) {
        elements[i].setAttribute("src", elements[i].getAttribute("data-src"));
        elements[i].removeAttribute("data-src");
      }
    }
  };

  window.addEventListener('scroll', lazyloadHandler);
  window.addEventListener('load', lazyloadHandler);
  window.addEventListener('resize', lazyloadHandler);
})();


function getQueryParams() {
    var queryParams = window.location.search.substr(1).split('&').reduce(function (q, query) {
      var chunks = query.split('=');
      var key = chunks[0];
      if (typeof(chunks[1]) == 'undefined') {
          return ({}, q);
      }
      var value = decodeURIComponent(chunks[1]);
      value = isNaN(Number(value))? value : Number(value);
      return (q[key] = value, q);
    }, {});
    
    return queryParams;
}

function setQueryParams(key, value) {
  if (value === null) {
    params = Object.keys(params).reduce(function(object, key_it) {
      if (key_it !== key) {
          object[key] = params[key];
      }
      return object;
    }, {});
  }
  else {
    params[key] = value;
  }
  var url = '?';
  Object.keys(params).map(function(key, i) {
    if (i !== 0) {
        url += '&';
    }
    url += encodeURIComponent(key) + '=' + encodeURIComponent(params[key]);
  });
  history.replaceState({}, null, url);
}

function setCount() {
  var count = ' games';
  var total = document.getElementsByTagName('dd').length;
  var hidden = Array.prototype.slice.call(document.getElementsByTagName('dd')).reduce(function(count_hidden, game) {
      if (game.getBoundingClientRect().width + game.getBoundingClientRect().height === 0) {
          return count_hidden + 1
      }
      return count_hidden;
  }, 0);
  
  document.getElementsByClassName('nav-count')[0].innerHTML = (total - hidden) + "/" + total + count;
}

(function () {
  setCount();
  params = getQueryParams();
  if (params.hasOwnProperty('tag')) {
    activeTag = params['tag'];
    document.body.classList.add('tags-active');
    highlightTags(params['tag']);
    setQueryParams('tag', params['tag']);
    
    filterByTag(params['tag']);
  }
  
  if (params.hasOwnProperty('filter')) {
    filter(params['filter']);
    document.getElementById('filter').value = params['filter'];
  }
})(); 
