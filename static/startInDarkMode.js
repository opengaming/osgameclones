function toggleDarkTheme() {
    if (document.body.classList.contains('darkTheme')) {
      document.body.classList.remove('darkTheme');
      localStorage.setItem('startInDarkTheme', 'false')
    } else {
      document.body.classList.add('darkTheme');
      localStorage.setItem('startInDarkTheme', 'true')
    }
  }

  function checkIfShouldStartInDarkTheme() {
    if (localStorage.getItem('startInDarkTheme') === 'true') {
      toggleDarkTheme();
    }
  }

  checkIfShouldStartInDarkTheme();
