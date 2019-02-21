const {danger, markdown, message, warn} = require('danger')
const http = require('http')
const url = require('url')
const yaml = require('js-yaml')
const fs = require('fs')

markdown("Hey there! Thanks for contributing a PR to osgameclones! 🎉")

const isURL = s => /^https?:\/\//.test(s)

const checkLink = link => {
  let parsedLink;
  try {
    parsedLink = url.parse(link)
  } catch (TypeError) {
    return
  }
  console.log(`Checking link ${parsedLink}`)
  /*const options = {method: 'HEAD', host: parsedLink.host, port: 80, path: parsedLink.pathname}
  const req = http.request(options, res => {
    if (res.statusCode < 200 || res.statusCode >= 300) {
      warn(`Broken link detected: ${link} returned HTTP ${res.statusCode}`)
    }
    req.end()
  }).on('error', e => {
    warn(`Broken link detected: ${link} timed out`)
  })*/
}

const detectAndCheckLinks = obj => {
  for (let key in obj) {
    if (isURL(obj[key])) {
      checkLink(obj[key])
    } else if (typeof obj[key] === 'object' && obj[key] != null) {
      detectAndCheckLinks(obj[key])
    }
  }
}  

const isGame = game => /^games\/\w+\.yaml$/.test(game)

const getGameChanges = files => {
  Promise.all(files.filter(isGame).map(file => danger.git.diffForFile(file)))
  .then(diffs => diffs.forEach(diff => {
    const gamesBefore = yaml.safeLoad(diff.before)
    const gamesAfter = yaml.safeLoad(diff.after)
    const stringsAfter = gamesAfter.map(game => JSON.stringify(game))
    const namesBefore = gamesBefore.map(game => game.name)
    const namesAfter = gamesAfter.map(game => game.name)
    let namesAdded = []
    let namesChanged = []
    let namesRemoved = []
    gamesBefore.forEach(game => {
      if (!namesAfter.includes(game.name)) {
        namesRemoved.push(game.name)
      } else if (namesAfter.includes(game.name) && !stringsAfter.includes(JSON.stringify(game))) {
        namesChanged.push(game.name)
      }
    })
    gamesAfter.forEach(game => {
      if (!namesBefore.includes(game.name)) {
        namesAdded.push(game.name)
      }
      detectAndCheckLinks(game)
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
