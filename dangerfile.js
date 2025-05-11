const {danger, message, warn} = require('danger')
const yaml = require('js-yaml')

const isGame = game => /^games\/\w+\.yaml$/.test(game)

let unknownLanguageDetected = false
const knownLanguages = Object.keys(require('linguist-languages')).concat(['Delphi', 'TorqueScript'])

// -----------
// Game checks
// -----------

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

const commonChecks = game => {
  checkLanguageKnown(game)
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
