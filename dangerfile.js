const {danger, markdown} = require('danger')
const yaml = require('js-yaml')
const fs = require('fs')

markdown("Hey there! Thanks for contributing a PR to osgameclones! 🎉")

const isGame = game => /^games\/\w+\.yaml$/.test(game)

// Information summary of files in the PR
// For debug purposes only
if (danger.git.modified_files.length || danger.git.created_files.length || danger.git.deleted_files.length) {
  let changes = ""

  const getChanges = (title, files) => {
    const md = files.map(file => {
      if (isGame(file)) {
        const games = yaml.safeLoad(fs.readFileSync(file))
        const gamesList = games.map(game => `\n  - ${game.name}`)
        danger.git.diffForFile(file).then(diff => markdown(`<!-- ${diff.diff} -->`))
        return `\n- 🎮 \`${file}\`${gamesList.join()})`
      }
      return return `\n- \`${file}\``
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
