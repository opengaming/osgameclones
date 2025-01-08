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
const knownLanguages = Object.keys(require('linguist-languages')).concat(['Delphi', 'TorqueScript'])

let unknownFrameworkDetected = false
const knownFrameworks = [
  '.NET',
  'Adobe AIR',
  'Adventure Game Studio',
  'Allegro',
  'angular',
  'Avalonia',
  'BackBone.js',
  'bgfx',
  'Box2D',
  'Bullet3',
  'Carbon',
  'Castle Game Engine',
  'CreateJS',
  'Cocos2d',
  'Construct',
  'Construct2',
  'Crystal Space',
  'Cube 2 Engine',
  'Daemon Engine',
  'DirectX',
  'DIV Games Studio',
  'Duality',
  'Ebitengine',
  'EntityX',
  'EnTT',
  'Flash',
  'Fyne',
  'FMOD',
  'FNA',
  'GameMaker Studio',
  'GameSprockets',
  'gLib2D',
  'Godot',
  'Graphics32',
  'GTK',
  'HaxeFlixel',
  'Impact',
  'Inform',
  'Irrlicht',
  'JavaFX',
  'JMonkeyEngine',
  'jQuery',
  'Kylix',
  'Laravel',
  'Lazarus',
  'libGDX',
  'libretro',
  'LÖVE',
  'LowRes NX',
  'Luanti',
  'LWJGL',
  'macroquad',
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
  'OpenFL',
  'OpenGL',
  'OpenRA',
  'OpenSceneGraph',
  'OpenTK',
  'OpenXR',
  'osu!framework',
  'Oxygine',
  'Panda3D',
  'PandaJS',
  'Phaser',
  'PICO-8',
  'Piston',
  'PixiJS',
  'pygame',
  'QB64',
  'Qt',
  'raylib',
  'React',
  'Redux',
  'rot.js',
  'Rx.js',
  'SDL',
  'SDL2',
  'SDL.NET',
  'Sea3D',
  'SFML',
  'Slick2D',
  'Solarus',
  'Source SDK',
  'Spring RTS Engine',
  'Starling',
  'Swing',
  'SWT',
  'three.js',
  'TGUI',
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

const checkFrameworkKnown = game => {
  if (!game.frameworks) return
  const unknownFrameworks = game.frameworks.filter(l => !knownFrameworks.includes(l))
  if (unknownFrameworks.length) {
    warn(
      `🌇 ${game.name} contains "${unknownFrameworks}" as frameworks, which is not known by us. ` +
      `Please check for spelling errors.`
    )
    unknownFrameworkDetected = true
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

const checkHasImagesOrVideos = game => {
  if (!game.images && !game.video) {
    warn(`🖼 ${game.name} has no images or videos. Please help improve the entry by finding one!`)
  }
}

const checkHasAdded = game => {
  if (!game.added) {
    warn(`📅 ${game.name} has no added date`)
  }
}

const commonChecks = game => {
  checkRepoGoogleCode(game)
  checkRepoGit(game)
  checkRepoSVN(game)
  checkRepoFTP(game)
  checkLanguageKnown(game)
  checkFrameworkKnown(game)
  checkFrameworkUsesLang(game)
  checkHasImagesOrVideos(game)
  checkHasAdded(game)
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
getGameChanges([].concat(danger.git.modified_files || [], danger.git.created_files || [], danger.git.deleted_files || []))
