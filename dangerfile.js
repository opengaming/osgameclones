const {danger, markdown, message, warn} = require('danger')
const http = require('http')
const url = require('url')
const yaml = require('js-yaml')
const fs = require('fs')

const isGame = game => /^games\/\w+\.yaml$/.test(game)

let unknownLanguageDetected = false
const knownLanguages = Object.keys(require('linguist-languages')).concat(['Delphi', 'TorqueScript'])
const frameworkLangs = {
  'SDL2': ['C++', 'C'],
  'SDL': ['C++', 'C'],
  'SDL.NET': ['C#'],
  'OpenGL': ['C++', 'C'],
  'Unity': ['C#'],
  'SFML': ['C++'],
  'libGDX': ['Java', 'Kotlin'],
  'Qt': ['C++'],
  'Allegro': ['C++', 'C'],
  'pygame': ['Python'],
  'OGRE': ['C++'],
  'Fyne': ['Go'],
}

// -----------
// Game checks
// -----------

const checkRepoFTP = game => {
  if (game.repo && game.repo.startsWith("ftp://")) {
    warn(`🔗 ${game.name}'s repo is on a FTP server, which cannot be opened in some browsers by default. Please change it to the project's developer web page.`)
  }
}

const checkRepoAdded = game => {
  if (!game.repo) return
  const match = game.repo.match(/github.com\/([^/]+)\//)
  if (!match) return
  const author = match[1]
  message(`💌 Hey @${author}, we're adding your game to osgameclones!`)
}

const checkLanguageKnown = game => {
  if (!game.langs) return
  const unknownLanguages = game.langs.filter(l => !knownLanguages.includes(l))
  if (unknownLanguages.length) {
    warn(
      `🔢 ${game.name} contains "${unknownLanguages}" as language, which is not known by us. ` +
      `Please check for spelling errors.`
    )
    unknownLanguageDetected = true
  }
}

const checkFrameworkUsesLang = game => {
  if (!game.frameworks) return
  const commonFrameworks = game.frameworks.filter(frameworks => Object.keys(frameworkLangs).includes(frameworks))
  commonFrameworks.forEach(framework => {
    const langs = frameworkLangs[framework]
    if (!game.langs || game.langs.filter(lang => langs.includes(lang)).length === 0) {
      message(
        `🏗 ${game.name} uses "${framework}" as a framework, but doesn't have ${langs} in its languages.`
      )
    }
  })
}

const commonChecks = game => {
  checkRepoFTP(game)
  checkLanguageKnown(game)
  checkFrameworkUsesLang(game)
}

// -----------

const onGameAdded = game => {
  checkRepoAdded(game)
  commonChecks(game)
}
const onGameChanged = game => {
  commonChecks(game)
}
const onGameRemoved = game => {
}

const getGameChanges = files => {
  Promise.all(files.filter(isGame).map(file => danger.git.diffForFile(file)))
  .then(diffs => {
    diffs.forEach(diff => {
      const gamesBefore = yaml.load(diff.before)
      // Compare any changes in games metadata
      const stringsBefore = gamesBefore.map(game => JSON.stringify(game))
      const gamesAfter = yaml.load(diff.after)
      const namesBefore = gamesBefore.map(game => game.name)
      const namesAfter = gamesAfter.map(game => game.name)
      gamesBefore.forEach(game => {
        if (!namesAfter.includes(game.name)) {
          onGameRemoved(game)
        }
      })
      gamesAfter.forEach(game => {
        if (!namesBefore.includes(game.name)) {
          onGameAdded(game)
        } else if (namesBefore.includes(game.name) && !stringsBefore.includes(JSON.stringify(game))) {
          onGameChanged(game)
        }
      })
    })
    if (unknownLanguageDetected) message(`Known languages are ${knownLanguages.join(", ")}.`)
  })
}
getGameChanges([].concat(danger.git.modified_files || [], danger.git.created_files || [], danger.git.deleted_files || []))
