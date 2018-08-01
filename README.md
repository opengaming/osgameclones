# Open Source Game Clones

This is the source of [http://osgameclones.com](http://osgameclones.com).
Feel free to add new games or improve information about those already in the database
by submitting a pull request or opening an issue.

## Games database

All of the games and their references to the original games are stored in YAML files under
[`games`][games] and [`originals`][originals]. All information is inside, and you should
more or less understand what's going on by reading it. Sorting is alphabetical, with the
exception of ScummVM, just because it's so many games at once.

## Add a clone / remake of a game

Simplest way to contribute is to fill in the [template][template] presented when you create
a new issue. Even better if you edit the files in the [`games`][games] directory directly. Your
changes will be submitted as a pull request. All games are validated against the rules
in the [`schema/games.yaml`][schema_games] validation file.

If you're adding a new clone/remake:

```yaml

name:           string     # Name of clone/remake (required)
type:           string     # One of: remake, clone
originals:      array      # Name reference to original game(s) that this game remakes/clones
repo:           string     # Link to source code
url:            string     # Link to website
feed:           string     # Link to RSS/Atom feed
development:    enum       # One of: complete, very active, active, sporadic, halted
status:         enum       # One of: playable, semi-playable, unplayable
multiplayer:    enum       # Any of: Online, LAN, Split-screen, Co-op, Hotseat, Matchmaking
lang:           array      # List of programming languages used
framework:      array      # List of engines/tools used
license:        enum       # One of licenses listed in games schema
content:        string     # One of: commercial, free, open, swappable*
info:           string     # Miscellaneous notes about the game
updated:        string     # Date when game was added or updated
images:         array      # Link(s) to screenshot(s)
video:
  youtube:      string     # YouTube video ID
  vimeo:        number     # Vimeo video ID

# * free means no cost, open means liberally licensed
```

## Add a reference to the original game

All the games listed need an original game they re-implement or clone. If there is no
existing game entry in [`originals`][originals] directory you can create a new entry
for it by following the following format. All originals are validated against the rules
in the [`schema/originals.yaml`][schema_originals] validation file.

```yaml
- name:         string     # Name of the original game (required)
  names:        array      # Other names for the game, or other games in the series
  platform:     enum       # Game platform, i.e. Amiga. See platform in orginals schema
  meta:
    genre:      enum       # Any of genres in originals schema
    subgenre:   enum       # Any of subgenres in originals schema
    theme:      enum       # Any of themes in originals schema
```

### External links to article about an original game

A Wikipedia link is created for all original game names; if the article link is different,
use the following syntax:

```yaml
name: [Name, Name of Wikipedia article]
```

If the game has a non-Wikipedia link:

```yaml
name: [Name, 'http://www.example.com']
```

## Contributing

### Pre-requisites

* [Python 2][python]
* [virtualenv][virtualenv]


### Install

Clone this repository and run inside the directory:

```
virtualenv .env
source .env/bin/activate
make install
```
### Building

Make sure the virtual env is active, if not run:

```
source .env/bin/activate
```

Then simply run the following to build the project into the `_build` directory.

```
make
```

## License

See [LICENSE][license]

[games]: games/
[originals]: originals/
[schema_games]: schema/games.yaml
[schema_originals]: schema/originals.yaml
[template]: .github/ISSUE_TEMPLATE.md
[license]: LICENSE

[python]: https://www.python.org
[virtualenv]: https://virtualenv.pypa.io
