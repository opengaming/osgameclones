# Open Source Game Clones

[![Build and Deploy](https://github.com/opengaming/osgameclones/actions/workflows/main.yml/badge.svg)](https://github.com/opengaming/osgameclones/actions/workflows/main.yml)

This is the source of [https://osgameclones.com](https://osgameclones.com).
Feel free to add new games or improve information about those already in the database
by submitting a pull request or opening an issue.

## Games database

All of the games and their references to the original games are stored in YAML files under
[`games`][games] and [`originals`][originals]. All information is inside, and you should
more or less understand what's going on by reading it. Sorting is alphabetical, with the
exception of ScummVM, just because it's so many games at once.

## Add a clone / remake of a game

Fill in the [game form][game_form] presented when you create
a new issue. Even better if you edit the files in the [`games`][games] directory directly. Your
changes will be submitted as a pull request. All games are validated against the rules
in the [`schema/games.yaml`][schema_games] validation file.

## Add a reference to the original game

Fill in the [add original form][original_form].
All the games listed need an original game they re-implement or clone. If there is no
existing game entry in [`originals`][originals] directory you can create a new entry
for it by following the following format. All originals are validated against the rules
in the [`schema/originals.yaml`][schema_originals] validation file.

## Contributing

### Pre-requisites

* [poetry][poetry]


### Install

Clone this repository and run inside the directory:

```
poetry install
```
### Building

Simply run the following to build the project into the `_build` directory.

```
make
```

### Running the server with Docker

You must first build a Docker image

```bash
make docker-build
```

After building the docker image, run the server with Docker

```bash
make docker-run
```

The server will be available at http://localhost:80, you can choose the port with the **PORT** variable.

```bash
# The server will be available at http://localhost:3000
make docker-run PORT=3000
```

## License

See [LICENSE][license]

[games]: games/
[originals]: originals/
[schema_games]: schema/games.yaml
[schema_originals]: schema/originals.yaml
[game_form]: https://osgameclones.com/add_game.html
[original_form]: https://osgameclones.com/add_original.html
[license]: LICENSE

[python]: https://www.python.org
[poetry]: https://python-poetry.org/
