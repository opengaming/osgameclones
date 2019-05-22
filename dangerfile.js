const {danger, markdown, message, warn} = require('danger')
const http = require('http')
const url = require('url')
const yaml = require('js-yaml')
const fs = require('fs')

markdown("Hey there! Thanks for contributing a PR to osgameclones! 🎉")

let namesAdded = []
let namesChanged = []
let namesRemoved = []

const isGame = game => /^games\/\w+\.yaml$/.test(game)

// -----------
// Game checks
// -----------

// Check that updated is within one day of today
const isDateWithinOneDayToday = d => {
  if (!d) {
    return false
  }
  const timeDiff = Math.abs(new Date().getTime() - d.getTime())
  return Math.ceil(timeDiff / (1000 * 3600 * 24)) <= 1
}
const checkGameUpdated = game => {
  if (!isDateWithinOneDayToday(game.updated)) {
    const gameUpdated = game.updated && game.updated.toISOString().slice(0, 10)
    const updated = new Date().toISOString().slice(0, 10)
    warn(`${game.name}'s "updated" value should be ${updated}; got ${gameUpdated} instead`)
  }
}

const checkRepoGoogleCode = game => {
  if (game.repo && (game.repo.indexOf('googlecode') >= 0 || game.repo.indexOf('code.google') >= 0)) {
    warn(`${game.name}'s repo is Google Code, a dead service. Please check if there is an updated repo elsewhere.`)
  }
}

// -----------

const onGameAdded = game => {
  namesAdded.push(game.name)
  checkGameUpdated(game)
  checkRepoGoogleCode(game)
}
const onGameChanged = game => {
  namesChanged.push(game.name)
  checkGameUpdated(game)
  checkRepoGoogleCode(game)
}
const onGameRemoved = game => {
  namesRemoved.push(game.name)
}

const getGameChanges = files => {
  Promise.all(files.filter(isGame).map(file => danger.git.diffForFile(file)))
  .then(diffs => {
    diffs.forEach(diff => {
      const gamesBefore = yaml.safeLoad(diff.before)
      // Compare any changes in games metadata
      const stringsBefore = gamesBefore.map(game => JSON.stringify(game))
      const gamesAfter = yaml.safeLoad(diff.after)
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
    if (namesAdded.length > 0) {
      message(`Game(s) added: ${danger.utils.sentence(namesAdded)} 🎊`)
    }
    if (namesChanged.length > 0) {
      message(`Game(s) updated: ${danger.utils.sentence(namesChanged)} 👏`)
    }
    if (namesRemoved.length > 0) {
      message(`Game(s) removed: ${danger.utils.sentence(namesRemoved)} 😿`)
    }
  })
}
getGameChanges(danger.git.modified_files.concat(danger.git.created_files, danger.git.deleted_files))

// Information summary of files in the PR
// For debug purposes only
if (danger.git.modified_files.length || danger.git.created_files.length || danger.git.deleted_files.length) {
  let changes = ""

  const getChanges = (title, files) => {
    const md = files.map(file => {
      if (isGame(file)) {
        const games = yaml.safeLoad(fs.readFileSync(file))
        const gamesList = games.map(game => `\n  - ${game.name}`)
        return `\n- 🎮 \`${file}\`${gamesList.join()}`
      }
      return `\n- \`${file}\``
    })
    if (md.length > 0) {
      return `\n\n${title}:${md}`
    }
    return ""
  }

  changes += getChanges("Changed", danger.git.modified_files)
  changes += getChanges("Added", danger.git.created_files)
  changes += getChanges("Deleted", danger.git.deleted_files)

  markdown(`<details><summary>Files in PR...</summary><p>${changes}</p></details>`)
}
