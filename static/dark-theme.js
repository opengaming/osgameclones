const DARK_THEME_CLASS = 'darkTheme';
const DARK_THEME_KEY = 'startInDarkTheme';

function setDarkTheme() {
  document.body.classList.add(DARK_THEME_CLASS);
  setThemeButtonText("Light Theme");
}

function setLightTheme() {
  document.body.classList.remove(DARK_THEME_CLASS);
  setThemeButtonText("Dark Theme");
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

/**
 * Safely modify theme button text only if it exists
 * @param {string} text label for button
 */
function setThemeButtonText(text) {
  const button = document.getElementById('dark-theme-button')
  if (button) {
    button.innerHTML = text
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
  setThemeButtonText(isDarkTheme ? "Light Theme" : "Dark Theme")
  document.getElementById('dark-theme-button').addEventListener('click', toggleDarkTheme)
})
