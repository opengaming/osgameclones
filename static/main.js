'use strict';

var OSGC = window.OSGC = {};
var params = window.params = {};
// Keep track of multiple selected tags
var selectedTags = window.selectedTags = new Set();

// Lazy load badges when they become visible (avoid error 429)
function lazyloadHandler(e) {
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
}

function handleContentChanged() {
  setCount();
  lazyloadHandler();
}

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
  var toggleGallery = function(t) {
    var gallery = t.parentNode.getElementsByClassName('gallery')[0];
    var raw = t.parentNode.getElementsByClassName('gallery-raw')[0];
    var show_now = gallery.style.display == 'none';

    t.innerHTML = show_now ? '&#x25bc;' : '&#x25b6;';
    gallery.style.display = show_now ? 'block' : 'none';

    if (raw && show_now) { gallery.insertAdjacentHTML('beforeend', raw.innerHTML); }
    else { gallery.innerHTML = ''; }
  };

  document.body.addEventListener('click', function(ev) {
    if (!ev.target || !ev.target.matches("span.toggler")) return;

    toggleGallery(ev.target);
  })

  var visibleTogglers = document.querySelectorAll('span.toggler.visible');
  for (var i = 0; i < visibleTogglers.length; i++) {
    toggleGallery(visibleTogglers[i]);
  }
})();

// search handling
function getFilter(term) {
  return !term ? "" :
    '[data-index*="' + term.toLowerCase().replace(/"/g, '') + '"]';
}

var filterStyle = document.getElementById('filter-style');

function filter(filter_value) {
  if (!filter_value) {
    setQueryParams('filter', null);
    filterStyle.innerHTML = "";
  } else {
    setQueryParams('filter', filter_value);
    filterStyle.innerHTML =
      ".searchable {display: none} .searchable" +
      filter_value.split(' ').map(getFilter).join('') +
      "{display: block}";
  }
  handleContentChanged();
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
function filterBySelectedTags() {
  var games = document.getElementsByTagName('dd');
  var parentHasActive = {};

  // If no tags selected, show all games by removing tags-active flag
  if (selectedTags.size === 0) {
    document.body.classList.remove('tags-active');
    // Clear active classes to avoid stale state
    for (var k = 0; k < games.length; k++) {
      games[k].classList.remove('active');
    }
    // Clear all dt active
    var dts = document.getElementsByTagName('dt');
    for (var d = 0; d < dts.length; d++) {
      dts[d].classList.remove('active');
    }
    handleContentChanged();
    return;
  }

  document.body.classList.add('tags-active');

  for (var i = 0, len = games.length; i < len; i += 1) {
    var game = games[i];
    var tagsAttr = game.getAttribute('data-tags') || '';
    var gameTags = tagsAttr.split(' ').filter(Boolean);
    var parentId = game.getAttribute('data-parent');

    // Check if game contains all selected tags
    var matchesAll = true;
    selectedTags.forEach(function(t){
      if (gameTags.indexOf(t) === -1) { matchesAll = false; }
    });

    if (matchesAll) {
      game.classList.add('active');
      parentHasActive[parentId] = true;
    } else {
      game.classList.remove('active');
    }
  }

  // Update parent dt active state
  var dts = document.getElementsByTagName('dt');
  for (var j = 0; j < dts.length; j++) {
    var dt = dts[j];
    if (parentHasActive[dt.id]) dt.classList.add('active');
    else dt.classList.remove('active');
  }

  handleContentChanged();
}

function sortByUpdated(e) {
  const btn = e.target;
  var list = document.getElementById('list');
  var sorted = document.getElementById('sorted');

  if (list.style.display == "none") {
    list.style.display = "block";
    sorted.style.display = "none";
    btn.innerHTML = "Updated";
  } else {
    list.style.display = "none";
    sorted.style.display = "block";
    btn.innerHTML = "Originals";

    if (!sorted.hasChildNodes()) {
      const games = [...document.getElementsByTagName('dd')];
      var gameList = [];
      let gameNames = new Set();
      games.forEach(game => {
        if (!gameNames.has(game.dataset.name)) {
          gameNames.add(game.dataset.name);
          gameList.push(game.cloneNode(true));
        }
      });
      gameList.sort(function(a,b) {
        return b.dataset.updated.localeCompare(a.dataset.updated);
      });

      gameList.forEach(game => {
        sorted.appendChild(game);
      });
    }
  }
}

function highlightTagsMulti() {
  var style = document.getElementById('tag-style');
  if (!style) return;
  if (selectedTags.size === 0) { style.innerHTML = ''; return; }
  var rules = '';
  selectedTags.forEach(function(tag){
    var safe = (tag + '').replace(/"/g, '');
    rules += '.tag[data-name=\"' + safe + '\"] { color: #ccc; background-color: #444; }';
    rules += '.dark-theme .tag[data-name=\"' + safe + '\"] { color: #444; background-color: #ccc; }';
  });
  style.innerHTML = rules;
}

function renderSelectedTagsBar() {
  var container = document.getElementById('selected-tags');
  if (!container) return;
  container.innerHTML = '';
  if (selectedTags.size === 0) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'block';
  // Label
  var label = document.createElement('span');
  label.textContent = 'Selected tags:';
  label.style.marginRight = '8px';
  container.appendChild(label);

  selectedTags.forEach(function(tag){
    var el = document.createElement('span');
    el.className = 'tag';
    el.setAttribute('data-name', tag);
    // Try to use existing tag text casing if available
    var source = document.querySelector('.tag[data-name="' + tag + '"]');
    el.textContent = source ? source.textContent.replace(/\s*\d+\s*$/, '') : tag.replace(/-/g,' ');
    el.title = 'Click to remove';
    el.addEventListener('click', function() { toggleTagByName(tag); });
    container.appendChild(el);
  });
}

function updateTagsUI() {
  // Highlights + selected tags bar + filter + URL
  highlightTagsMulti();
  renderSelectedTagsBar();
  filterBySelectedTags();
  // Update URL query param
  if (selectedTags.size === 0) setQueryParams('tag', null);
  else setQueryParams('tag', Array.from(selectedTags).join(','));
}

function toggleTagByName(curTag) {
  if (!curTag) return;
  if (selectedTags.has(curTag)) {
    selectedTags.delete(curTag);
  } else {
    selectedTags.add(curTag);
  }
  updateTagsUI();
}

(function() {
  function onTagClick(e) {
    var t = e.target.closest && e.target.closest('.tag');
    if (!t || !t.hasAttribute('data-name')) return;
    var curTag = t.getAttribute('data-name');
    toggleTagByName(curTag);
  }

  // Attach to all existing tags
  var tags = document.getElementsByClassName('tag');
  for (var i = 0, l = tags.length; i < l; i += 1) {
    tags[i].addEventListener('click', onTagClick);
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
})();

// Lazy load badges
(function() {
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
          object[key_it] = params[key_it];
      }
      return object;
    }, {});
  }
  else {
    params[key] = value;
  }
  var url = '?';
  Object.keys(params).map(function(pkey, i) {
    if (i !== 0) {
        url += '&';
    }
    url += encodeURIComponent(pkey) + '=' + encodeURIComponent(params[pkey]);
  });
  history.replaceState({}, null, url);
}

function setCount() {
  var list = document.getElementById('list');
  var sorted = document.getElementById('sorted');

  if (list.style.display == "none") {
    var dds = Array.from(sorted.getElementsByTagName('dd'));
    var total = dds.length;
  } else {
    var dds = Array.from(list.getElementsByTagName('dd'));
    var total = new Set(dds.map(dd => dd.getAttribute('data-name'))).size;
  }
  var shownGames = dds.filter(dd => dd.getBoundingClientRect().width + dd.getBoundingClientRect().height > 0)
  var shown = new Set(shownGames.map(dd => dd.getAttribute('data-name'))).size;

  document.getElementsByClassName('nav-count')[0].innerHTML = shown + "/" + total + " games";
}

(function () {
  setCount();
  params = getQueryParams();
  if (params.hasOwnProperty('tag')) {
    var raw = (params['tag'] + '').split(',').map(function(s){ return s.trim(); }).filter(Boolean);
    raw.forEach(function(t){ selectedTags.add(t); });
    updateTagsUI();
  }
  
  if (params.hasOwnProperty('filter')) {
    filter(params['filter']);
    document.getElementById('filter').value = params['filter'];
  }

  const sortBtnLbl = document.getElementById('sort-button-label');
  sortBtnLbl.innerHTML = "Updated";
  sortBtnLbl.addEventListener('click', sortByUpdated);
})(); 
