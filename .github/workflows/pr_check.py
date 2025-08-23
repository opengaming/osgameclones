import json
import os
import re
from pathlib import Path

import yaml
from github import Github, GithubException
from thefuzz import process

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
GH_PATH = Path(__file__).parent.parent
# https://github.com/github-linguist/linguist/blob/main/lib/linguist/languages.yml
GH_LANGUAGES = set(yaml.safe_load(open(GH_PATH / "languages.yml")).keys()) | {"Delphi"}
KNOWN_FRAMEWORKS = [
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
  'SDL3',
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
  'Unreal Engine 5',
  'VDrift Engine',
  'Vue.js',
  'Vulkan',
  'WebGL',
  'wxWidgets',
  'XNA'
]
FRAMEWORK_LANGUAGES = {
  "Allegro": {"C++", "C"},
  "Fyne": {"Go"},
  "OGRE": {"C++"},
  "OpenGL": {"C++", "C"},
  "Qt": {"C++"},
  "SDL": {"C++", "C"},
  "SDL.NET": {"C#"},
  "SDL2": {"C++", "C"},
  "SFML": {"C++"},
  "Unity": {"C#"},
  "libGDX": {"Java", "Kotlin"},
  "pygame": {"Python"},
  "Vue.js": {"JavaScript"},
}
MIN_FUZZ_SCORE = 95
unknown_languages = False
unknown_frameworks = False

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPOSITORY)
pr = repo.get_pull(PR_NUMBER)
print("PR", pr.url)
output = {
    "content": "Hey there! Thanks for contributing a PR to osgameclones! 🎉",
    "labels": set(label.name for label in pr.labels),
    "pr": PR_NUMBER,
}

# Get game changes
files = pr.get_files()
changed_files = [str(file) for file in files]
print("Changed files", changed_files)


def load_games_file(filename: str, sha: str):
    try:
        contents = repo.get_contents(filename, sha)
    except GithubException as e:
        print("Cannot get file at", filename, e)
        return {}
    file = contents.decoded_content.decode()
    parsed = yaml.safe_load(file)
    return {game["name"]: game for game in parsed}


def added_checks(game):
    if match := re.search(r"github.com/([^/]+)/", game.get("repo", "")):
        author = match[1]
        yield f"💌 Hey @{author}, we're adding your game to osgameclones!"


def common_checks(game):
    yield from check_has_added(game)
    yield from check_not_same_repo_and_url(game)
    yield from check_has_images_or_videos(game)
    yield from check_has_language(game)
    yield from check_language_known(game)
    yield from check_framework_known(game)
    yield from check_framework_language(game)
    yield from check_repo_google_code(game)


def check_has_added(game):
    if "added" not in game:
        yield f"📅 {game['name']} has no added date"


def check_not_same_repo_and_url(game):
    if game.get("url") == game.get("repo"):
        yield f"👯 {game['name']}'s url and repo are the same - " \
              "please use repo for the development project page (such as GitHub) " \
              "and url as the public-facing page, if any"


def check_has_images_or_videos(game):
    if not game.get("images") and not game.get("video"):
        yield f"🖼 {game['name']} has no images or videos. " \
              "Please help improve the entry by finding some!"


def check_has_language(game):
    if not game.get("langs"):
        yield f"🔡 {game['name']} has no languages. " \
              "Please help improve the entry by finding some!"


def check_language_known(game):
    if u := {lang for lang in game.get("langs", []) if lang not in GH_LANGUAGES}:
        yield f"🔢 {game['name']} has unknown language{'s'[:len(u)^1]} \"{', '.join(u)}\". " \
              "Please check for spelling errors."
        for ul in u:
            choice, score = process.extractOne(ul, GH_LANGUAGES)
            print("Fuzz match language", ul, "->", choice, ":", score)
            if score >= MIN_FUZZ_SCORE:
                yield f"- Suggested fix: {ul} -> **{choice}**"
        global unknown_languages
        unknown_languages = True


def check_framework_known(game):
    if not (frameworks := game.get("frameworks")):
        return
    if u := [f for f in frameworks if f not in KNOWN_FRAMEWORKS]:
        yield f"🌇 {game['name']} has unknown framework{'s'[:len(u)^1]} \"{', '.join(u)}\". " \
              "Please check for spelling errors."
        for uf in u:
            choice, score = process.extractOne(uf, KNOWN_FRAMEWORKS)
            print("Fuzz match framework", uf, "->", choice, ":", score)
            if score >= MIN_FUZZ_SCORE:
                yield f"- Suggested fix: {uf} -> **{choice}**"
        global unknown_frameworks
        unknown_frameworks = True


def check_framework_language(game):
    if not (frameworks := game.get("frameworks")):
        return
    for framework in frameworks:
        if not (framework_langs := FRAMEWORK_LANGUAGES.get(framework, set())):
            continue
        if not set(game.get("langs", [])) & framework_langs:
            yield f"🏗 {game['name']} uses \"{framework}\" as a framework, " \
                  f"but doesn't have {', '.join(framework_langs)} in its languages."


def check_repo_google_code(game):
    if "code.google" in game.get("repo", ""):
        yield f"⚰️ {game['name']}'s repo is Google Code, a dead service. " \
              "Please check if there is an updated repo elsewhere."


# Scan files for changes
games_added = set()
games_changed = set()
games_removed = set()
has_py = False
has_js = False
check_messages = []
for file in files:
    if file.filename.endswith(".py"):
        has_py = True
    elif file.filename.endswith(".js"):
        has_js = True
    elif re.match(r"^games/\w+\.yaml$", file.filename):
        print("Game file changed", file)
        old_games = load_games_file(file.filename, pr.base.sha)
        new_games = load_games_file(file.filename, pr.head.sha)

        for game in old_games:
            if game not in new_games:
                games_removed.add(game)
        for game in new_games:
            if game not in old_games:
                games_added.add(game)
                for message in added_checks(new_games[game]):
                    check_messages.append(message)
                for message in common_checks(new_games[game]):
                    check_messages.append(message)
        for game in old_games:
            if game in new_games:
                if old_games[game] != new_games[game]:
                    games_changed.add(game)
                    for message in common_checks(new_games[game]):
                        check_messages.append(message)

# Update comment based on changed games and checks
if games_added:
    output["content"] += f"\nGame{'s'[:len(games_added) ^ 1]} added: {', '.join(games_added)} 🎊"
if games_changed:
    output["content"] += f"\nGame{'s'[:len(games_changed) ^ 1]} updated: {', '.join(games_changed)} 👏"
if games_removed:
    output["content"] += f"\nGame{'s'[:len(games_removed) ^ 1]} removed: {', '.join(games_removed)} 😿"
if check_messages:
    output["content"] += "\n### Issues found\n- " + "\n- ".join(check_messages)
if unknown_languages:
    output["content"] += "\n### Known Languages\n" + ", ".join(sorted(GH_LANGUAGES, key=str.casefold))
if unknown_frameworks:
    output["content"] += "\n### Known Frameworks\n" + ", ".join(sorted(KNOWN_FRAMEWORKS, key=str.casefold))

# Update issue labels
if has_py:
    output["labels"].add("python")
if has_js:
    output["labels"].add("javascript")
if games_added:
    output["labels"].add("game-addition")
if games_changed or games_removed:
    output["labels"].add("game-correction")

# Update GitHub PR
path = Path("./pr/output.json")
path.parent.mkdir(exist_ok=True, parents=True)
output["labels"] = list(output["labels"])
path.write_text(json.dumps(output))

"""
Ideas for more PR suggestions
- Scrape repo and url and look for screenshot candidates
- Scrape github repo to find
  - matching license
  - dev status
  - releases feed
  - languages
- Make suggested changes in PR
"""