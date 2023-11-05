const DARK_THEME_CLASS = 'dark-theme';
const LIGHT_THEME_CLASS = 'light-theme';
const THEME_KEY = 'theme';

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
    localStorage.setItem(THEME_KEY, 'light')
  } else {
    setDarkTheme();
    localStorage.setItem(THEME_KEY, 'dark')
  }
}

// enable dark theme as soon as possible so first paint is already dark mode
(function () {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    if (localStorage.getItem(THEME_KEY) === null) {
      if (event.matches) {
        setDarkTheme();
      } else {
        setLightTheme();
      }
    }
  });

  if (localStorage.getItem(THEME_KEY) === 'dark') {
      setDarkTheme();
  } else if (localStorage.getItem(THEME_KEY) === 'light') {
      setLightTheme();
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkTheme();
  } else {
      setLightTheme();
  }
})();

// handle theme button label and listener once DOM fully loaded
window.addEventListener('DOMContentLoaded', function () {
  const isDarkTheme = document.body.classList.contains(DARK_THEME_CLASS)
  document.getElementById('dark-theme-button').addEventListener('click', toggleDarkTheme)
})
