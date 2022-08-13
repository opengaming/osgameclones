const DARK_THEME_CLASS = 'darkTheme';
const DARK_THEME_KEY = 'startInDarkTheme';

function setDarkTheme() {
  document.body.classList.add(DARK_THEME_CLASS);
  document.getElementById('dark-theme-button').innerHTML = "Light Theme";
}

function setLightTheme() {
  document.body.classList.remove(DARK_THEME_CLASS);
  document.getElementById('dark-theme-button').innerHTML = "Dark Theme";
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

window.addEventListener('load', function() {
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

  document.getElementById('dark-theme-button').addEventListener('click', toggleDarkTheme)
});
