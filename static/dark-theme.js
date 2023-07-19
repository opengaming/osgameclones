const DARK_THEME_CLASS = 'dark-theme';
const LIGHT_THEME_CLASS = 'light-theme';
const DARK_THEME_KEY = 'startInDarkTheme';

function setDarkTheme() {
  document.body.classList.remove(LIGHT_THEME_CLASS);
  document.body.classList.add(DARK_THEME_CLASS);
}

function setLightTheme() {
  document.body.classList.remove(DARK_THEME_CLASS);
  document.body.classList.add(LIGHT_THEME_CLASS);
}

function toggleDarkTheme() {
  if (document.body.classList.contains(DARK_THEME_CLASS)) {
    setLightTheme();
    localStorage.setItem(DARK_THEME_KEY, 'false')
  } else {
    setDarkTheme();
    localStorage.setItem(DARK_THEME_KEY, 'true')
  }
}

// enable dark theme as soon as possible so first paint is already dark mode
(function () {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    if (localStorage.getItem(DARK_THEME_KEY) === null) {
      if (event.matches) {
        setDarkTheme();
      } else {
        setLightTheme();
      }
    }
  });
  if (localStorage.getItem(DARK_THEME_KEY) === 'true' || window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setDarkTheme();
  }
})();

// handle theme button label and listener once DOM fully loaded
window.addEventListener('DOMContentLoaded', function () {
  const isDarkTheme = document.body.classList.contains(DARK_THEME_CLASS)
  document.getElementById('dark-theme-button').addEventListener('click', toggleDarkTheme)
})
