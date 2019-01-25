const {danger, markdown, message} = require('danger')
const yaml = require('js-yaml')
const fs = require('fs')

markdown("Hey there! Thanks for contributing a PR to osgameclones! 🎉")

const isGame = game => /^games\/\w+\.yaml$/.test(game)

const getGameChanges = files => {
  Promise.all(files.filter(isGame).map(file => danger.git.diffForFile(file)))
  .then(diffs => diffs.forEach(diff => {
    const gamesBefore = yaml.safeLoad(diff.before)
    const gamesAfter = yaml.safeLoad(diff.after)
    const namesBefore = gamesBefore.map(game => game.name)
    const namesAfter = gamesAfter.map(game => game.name)
    let namesAdded = []
    let namesChanged = []
    let namesRemoved = []
    gamesBefore.forEach(game => {
      if (!namesAfter.includes(game.name)) {
        namesRemoved.push(game.name)
      } else if (namesAfter.includes(game.name) && !gamesAfter.includes(game)) {
        namesChanged.push(game.name)
      }
    })
    gamesAfter.forEach(game => {
      if (!namesBefore.includes(game.name)) {
        namesAdded.push(game.name)
      }
    })
    if (namesAdded.length > 0) {
      message(`Games added: ${danger.utils.sentence(namesAdded)} 🎊`)
    }
    if (namesChanged.length > 0) {
      message(`Games updated: ${danger.utils.sentence(namesChanged)} 👏`)
    }
    if (namesRemoved.length > 0) {
      message(`Games removed: ${danger.utils.sentence(namesRemoved)} 😿`)
    }
  }))
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
        return `\n- 🎮 \`${file}\`${gamesList.join()})`
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
