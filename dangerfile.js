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

let unknownLanguageDetected = false
// Follow https://github.com/github/linguist/blob/master/lib/linguist/languages.yml for a list of languages
const knownLanguages = [
  'AGS Script',
  'ActionScript',
  'Ada',
  'AngelScript',
  'Assembly',
  'Blitz BASIC',
  'C',
  'C#',
  'C++',
  'CoffeeScript',
  'D',
  'Delphi',
  'Elm',
  'F#',
  'GDScript',
  'GML',
  'Go',
  'Haskell',
  'Haxe',
  'Java',
  'JavaScript',
  'Kotlin',
  'Lisp',
  'Lua',
  'Nim',
  'Object Pascal',
  'Objective-C',
  'ooc',
  'Pascal',
  'Perl',
  'PHP',
  'Python',
  'QBasic',
  'QuakeC',
  'QuickBASIC',
  'Ruby',
  'Rust',
  'Scala',
  'Squirrel',
  'Swift',
  'TorqueScript',
  'TypeScript',
  'Vala',
  'Visual FoxPro'
]

let unknownFrameworkDetected = false
const knownFrameworks = [
  '.NET Core',
  'Adobe AIR',
  'Adventure Game Studio',
  'Allegro',
  'BackBone.js',
  'Box2D',
  'Bullet3',
  'Construct',
  'Construct2',
  'Cube 2 Engine',
  'Daemon Engine',
  'DirectX',
  'DIV Games Studio',
  'Duality',
  'Ebiten',
  'EntityX',
  'EnTT',
  'Flash',
  'GameMaker Studio',
  'Godot',
  'Graphics32',
  'GTK+',
  'Inform',
  'Irrlicht',
  'JavaFX',
  'JMonkeyEngine',
  'jQuery',
  'Kylix',
  'Laravel',
  'LibGDX',
  'Love3D',
  'LÖVE',
  'melonJS',
  'Mono',
  'MonoGame',
  'ncurses',
  'NeoAxis Engine',
  'Netty.io',
  'nya-engine',
  'OGRE',
  'Open Dynamics Engine',
  'OpenAL',
  'OpenGL',
  'OpenRA',
  'OpenSceneGraph',
  'Panda3D',
  'PandaJS',
  'Phaser',
  'PICO-8',
  'pixi.js',
  'pygame',
  'QB64',
  'Qt',
  'React',
  'Redux',
  'rot.js',
  'Rx.js',
  'SDL',
  'SDL2',
  'Sea3D',
  'SFML',
  'Slick2D',
  'Source SDK',
  'Spring RTS Engine',
  'Starling',
  'SWT',
  'three.js',
  'TIC-80',
  'Torque 3D',
  'Tween.js',
  'Unity',
  'VDrift Engine',
  'Vue.js',
  'Vulkan',
  'WebGL',
  'wxWidgets',
  'XNA'
]

// -----------
// Game checks
// -----------

const checkRepoGoogleCode = game => {
  if (game.repo && (game.repo.indexOf('googlecode') >= 0 || game.repo.indexOf('code.google') >= 0)) {
    warn(`⚰️ ${game.name}'s repo is Google Code, a dead service. Please check if there is an updated repo elsewhere.`)
  }
}

const checkRepoGit = game => {
  if (game.repo && game.repo.startsWith("git://")) {
    warn(`🔗 ${game.name}'s repo is a git repo, which cannot be opened in browsers by default. Please change it to the project's developer web page.`)
  }
}

const checkRepoSVN = game => {
  if (game.repo && game.repo.startsWith("svn://")) {
    warn(`🔗 ${game.name}'s repo is an SVN repo, which cannot be opened in browsers by default. Please change it to the project's developer web page.`)
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
  if (!game.lang) return
  const unknownLanguages = game.lang.filter(l => !knownLanguages.includes(l))
  if (unknownLanguages.length) {
    warn(
      `🔢 ${game.name} contains "${unknownLanguages}" as language, which is not known by us. ` +
      `Please check for spelling errors.`
    )
    unknownLanguageDetected = true
  }
}

const checkFrameworkKnown = game => {
  if (!game.framework) return
  const unknownFrameworks = game.framework.filter(l => !knownFrameworks.includes(l))
  if (unknownFrameworks.length) {
    warn(
      `🌇 ${game.name} contains "${unknownFrameworks}" as framework, which is not known by us. ` +
      `Please check for spelling errors.`
    )
    unknownFrameworkDetected = true
  }
}

const checkHasImagesOrVideos = game => {
  if (!game.images && !game.video) {
    warn(`🖼 ${game.name} has no images or videos. Please help improve the entry by finding one!`)
  }
}

const checkHasStatus = game => {
  if (!game.status) {
    warn(`🕹️ ${game.name} has no "status" field. Please add so users know whether the game is playable!`)
  }
}

const commonChecks = game => {
  checkRepoGoogleCode(game)
  checkRepoGit(game)
  checkRepoSVN(game)
  checkLanguageKnown(game)
  checkFrameworkKnown(game)
  checkHasImagesOrVideos(game)
  checkHasStatus(game)
}

// -----------

const onGameAdded = game => {
  namesAdded.push(game.name)
  checkRepoAdded(game)
  commonChecks(game)
}
const onGameChanged = game => {
  namesChanged.push(game.name)
  commonChecks(game)
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
    if (unknownLanguageDetected) message(`Known languages are ${knownLanguages.join(", ")}.`)
    if (unknownFrameworkDetected) message(`Known frameworks are ${knownFrameworks.join(", ")}.`)
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
