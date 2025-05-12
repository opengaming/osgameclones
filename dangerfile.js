const {danger, message} = require('danger')
const yaml = require('js-yaml')

const isGame = game => /^games\/\w+\.yaml$/.test(game)

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

// -----------

const onGameAdded = game => {
  checkRepoAdded(game)
}

const getGameChanges = files => {
  Promise.all(files.filter(isGame).map(file => danger.git.diffForFile(file)))
  .then(diffs => {
    diffs.forEach(diff => {
      const gamesBefore = yaml.load(diff.before)
      const gamesAfter = yaml.load(diff.after)
      const namesBefore = gamesBefore.map(game => game.name)
      gamesAfter.forEach(game => {
        if (!namesBefore.includes(game.name)) {
          onGameAdded(game)
        }
      })
    })
  })
}
getGameChanges([].concat(danger.git.modified_files || [], danger.git.created_files || [], danger.git.deleted_files || []))
