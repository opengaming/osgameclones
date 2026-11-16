'use strict';

let OSGC = window.OSGC = {};
let params = window.params = {};
// Keep track of multiple selected tags, including negative exclusions
let selectedTags = window.selectedTags = new Set();
let excludedTags = window.excludedTags = new Set();

function normalizeTagName(rawTag) {
  return String(rawTag || '').trim().replace(/^[-!]+/, '');
}

function isNegativeTagName(rawTag) {
  return /^[-!]/.test(String(rawTag || ''));
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
function escapeCssAttributeValue(value) {
  return value
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/]/g, '\\]');
}

function getFilter(term) {
  return !term ? "" :
    '[data-index*="' + escapeCssAttributeValue(term.toLowerCase()) + '"]';
}

var filterStyle = document.getElementById('filter-style');

function filter(filter_value) {
  if (!filter_value) {
    setQueryParams('filter', null);
    if (filterStyle) filterStyle.innerHTML = "";
  } else {
    setQueryParams('filter', filter_value);
    if (filterStyle) {
      filterStyle.innerHTML =
        ".searchable {display: none} .searchable" +
        String(filter_value).split(' ').map(getFilter).join('') +
        "{display: block}";
    }
  }
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
function filterBySelectedTags() {
  const games = document.getElementsByTagName('dd');
  let parentHasActive = {};
  const hasActiveFilters = selectedTags.size > 0 || excludedTags.size > 0;

  // If no tags selected, show all games by removing tags-active flag
  if (!hasActiveFilters) {
    document.body.classList.remove('tags-active');
    // Clear active classes to avoid stale state
    for (let k = 0; k < games.length; k++) {
      games[k].classList.remove('active');
    }
    // Clear all dt active
    const dts = document.getElementsByTagName('dt');
    for (let d = 0; d < dts.length; d++) {
      dts[d].classList.remove('active');
    }
    setCount();
    return;
  }

  document.body.classList.add('tags-active');

  for (let i = 0, len = games.length; i < len; i += 1) {
    const game = games[i];
    const tagsAttr = game.getAttribute('data-tags') || '';
    const gameTags = tagsAttr.split(' ').filter(Boolean);
    const parentId = game.getAttribute('data-parent');

    let matchesAll = true;
    selectedTags.forEach(function(t){
      if (gameTags.indexOf(t) === -1) { matchesAll = false; }
    });

    let matchesExcluded = true;
    excludedTags.forEach(function(t){
      if (gameTags.indexOf(t) !== -1) { matchesExcluded = false; }
    });

    if (matchesAll && matchesExcluded) {
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

  setCount();
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
        if (!game.classList.contains('more-clones') && !gameNames.has(game.dataset.name)) {
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
  const style = document.getElementById('tag-style');
  if (!style) return;
  const total = selectedTags.size + excludedTags.size;
  if (total === 0) { style.innerHTML = ''; return; }
  let rules = '';
  selectedTags.forEach(function(tag){
    const safe = escapeCssAttributeValue(tag);
    rules += '.tag[data-name=\"' + safe + '\"] { color: #ccc; background-color: #444; }';
    rules += '.dark-theme .tag[data-name=\"' + safe + '\"] { color: #444; background-color: #ccc; }';
  });
  excludedTags.forEach(function(tag){
    const safe = escapeCssAttributeValue(tag);
    rules += '.tag[data-name=\"' + safe + '\"] { color: #f8b4b4; background-color: #602020; }';
    rules += '.dark-theme .tag[data-name=\"' + safe + '\"] { color: #f5d5d5; background-color: #4a1a1a; }';
  });
  style.innerHTML = rules;
}

function renderSelectedTagsBar() {
  const container = document.getElementById('selected-tags');
  if (!container) return;
  container.innerHTML = '';
  const total = selectedTags.size + excludedTags.size;
  if (total === 0) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'block';
  // Label
  const label = document.createElement('span');
  label.textContent = 'Tags (Shift-click to exclude):';
  label.style.marginRight = '8px';
  container.appendChild(label);

  const renderTag = function(tag, excluded) {
    const el = document.createElement('span');
    el.className = 'tag';
    const rawTag = normalizeTagName(tag);
    if (excluded) {
      el.setAttribute('data-negative', 'true');
    } else {
      el.setAttribute('data-name', rawTag);
    }
    if (rawTag === 'ai') {
      const icon = document.createElement('img');
      icon.className = 'tag-ai-icon';
      icon.src = '/static/eu-ai-icon.png';
      icon.alt = '';
      icon.width = 15;
      icon.height = 15;
      el.appendChild(icon);
      if (excluded) {
        const neg = document.createElement('span');
        neg.textContent = '−';
        neg.style.marginLeft = '4px';
        neg.style.fontWeight = '700';
        el.appendChild(neg);
      }
    } else {
      const sourceSelector = '.tag[data-name="' + escapeCssAttributeValue(rawTag) + '"]';
      const source = document.querySelector(sourceSelector);
      const sourceText = source && source.textContent.trim();
      const text = sourceText ? sourceText.replace(/\s*\d+\s*$/, '') : rawTag.replace(/-/g,' ');
      el.textContent = excluded ? '-' + text : text;
    }
    el.title = excluded ? 'Click to remove exclusion' : 'Click to remove';
    container.appendChild(el);
  };

  selectedTags.forEach(function(tag){ renderTag(tag, false); });
  excludedTags.forEach(function(tag){ renderTag(tag, true); });
}

function updateTagsUI() {
  // Highlights + selected tags bar + filter + URL
  highlightTagsMulti();
  renderSelectedTagsBar();
  filterBySelectedTags();
  // Update URL query param
  const allTags = Array.from(selectedTags).concat(Array.from(excludedTags).map(function(tag){ return '-' + tag; }));
  if (allTags.length === 0) setQueryParams('tag', null);
  else setQueryParams('tag', allTags.join(','));
}

function toggleTagByName(curTag) {
  if (!curTag) return;
  const tag = normalizeTagName(curTag);
  if (!tag) return;
  const exclude = isNegativeTagName(curTag);
  if (exclude) {
    if (excludedTags.has(tag)) {
      excludedTags.delete(tag);
      selectedTags.delete(tag);
    } else {
      excludedTags.add(tag);
      selectedTags.delete(tag);
    }
  } else {
    if (selectedTags.has(tag)) {
      selectedTags.delete(tag);
    } else {
      selectedTags.add(tag);
      excludedTags.delete(tag);
    }
  }
  updateTagsUI();
}

(function() {
  function onTagClick(e) {
    const t = e.target.closest && e.target.closest('.tag');
    if (!t || !t.hasAttribute('data-name')) return;
    const curTag = t.getAttribute('data-name');
    const shouldExclude = e.shiftKey || isNegativeTagName(curTag);
    toggleTagByName(shouldExclude ? '-' + normalizeTagName(curTag) : curTag);
  }

  document.body.addEventListener('click', onTagClick);
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

function getQueryParams() {
    return window.location.search.substr(1).split('&').reduce(function (q, query) {
      if (!query) return q;
      const chunks = query.split('=');
      const key = chunks[0];
      if (!key) return q;
      if (typeof(chunks[1]) == 'undefined') {
          return q;
      }
      let value = chunks.slice(1).join('=');
      value = decodeURIComponent(value);
      if (value !== '' && value.trim() !== '' && !Number.isNaN(Number(value)) && value === String(Number(value))) {
        value = Number(value);
      }
      q[key] = value;
      return q;
    }, {});
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
  let url = '?';
  const paramKeys = Object.keys(params);
  if (paramKeys.length === 0) {
    url = '';
  } else {
    url += paramKeys.map(function(pkey) {
        return encodeURIComponent(pkey) + '=' + encodeURIComponent(params[pkey]);
    }).join('&');
  }
  history.replaceState({}, null, url);
}

function setCount() {
  const list = document.getElementById('list');
  const sorted = document.getElementById('sorted');

  if (!list || !sorted) return;

  let total = 0;
  let dds = null;
  if (list.style.display === "none") {
    dds = Array.from(sorted.getElementsByTagName('dd'));
    total = dds.length;
  } else {
    dds = Array.from(list.getElementsByTagName('dd'));
    total = new Set(dds.map(dd => dd.getAttribute('data-name'))).size;
  }
  const shownGames = dds.filter(dd => dd.getBoundingClientRect().width + dd.getBoundingClientRect().height > 0)
  const shown = new Set(shownGames.map(dd => dd.getAttribute('data-name'))).size;

  const navCount = document.getElementsByClassName('nav-count')[0];
  if (navCount) navCount.innerHTML = shown + "/" + total + " games";
}

(function () {
  params = getQueryParams();
  const filterInput = document.getElementById('filter');
  const sortButtonLabel = document.getElementById('sort-button-label');

  if (params.hasOwnProperty('tag')) {
    const raw = (params['tag'] + '').split(',').map(function(s){ return s.trim(); }).filter(Boolean);
    raw.forEach(function(t){
      const tag = normalizeTagName(t);
      if (!tag) return;
      if (isNegativeTagName(t)) toggleTagByName('-' + tag);
      else toggleTagByName(tag);
    });
    updateTagsUI();
  }

  if (params.hasOwnProperty('filter')) {
    filter(params['filter']);
    if (filterInput) filterInput.value = params['filter'];
  }

  if (sortButtonLabel) sortButtonLabel.addEventListener('click', sortByUpdated);
})(); 
