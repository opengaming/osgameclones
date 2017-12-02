# Open Source Game Clones

This is a source of [http://osgameclones.com](http://osgameclones.com). Feel
free to submit pull requests to add new games and improve information about
those already in the database.

## Games database

Check out the YAML files under [`/games`][games] and [`/originals`][originals]. All information is inside, and you should more or less
understand what's going on by reading it. Sorting is alphabetical, with the
exception of ScummVM, just because it's so many games at once.

## Add a clone/remake

Simplest way to contribute is to open a new issue and fill in the template.
Even better if you edit the [`/games`][games] files directly. Your
changes will be submitted as a pull request.

If you're adding a new clone/remake:

```yaml

name: string            # Name of clone/remake (required)
remakes: array          # Reference to original games that this game remakes
clones: array           # Reference to original games that this game clones
repo: string            # Link to source code
url: string             # Link to website
feed: string            # Link to RSS/Atom feed
development: enum       # One of: complete, very active, active, sporadic, halted
status: enum            # One of: playable, semi-playable, unplayable
lang: array             # List of programming languages used
framework: array        # List of engines/tools used
license: array          # See licenses in schema_clones.yaml
content: string         # One of: commercial, free, open, swapable
                        # free means no cost, open means liberally licensed
info: string            # Notes about the game
updated: string         # Date when game was added or updated
images: array           # Link(s) to screenshot(s)
video:
  youtube: string       # YouTube video ID
  vimeo: number         # Vimeo video ID
```

## Add a game parent

If you're adding a new game group:

```yaml
- name: string          # Name of the original game (required)
  names: array          # Other names for the game, or other games in the series
  meta:
    genre: array        # See genres in schema_originals.yaml
    subgenre: array     # See genres in schema_originals.yaml
    theme: array        # See genres in schema_originals.yaml
```

A Wikipedia link is created for all original game names; if the article link is different, use the following syntax:

```yaml
name: [Name, Name of Wikipedia article]
```

If the game has a non-Wikipedia link:

```yaml
name: [Name, 'http://www.example.com']
```

Please refer to the [template][template] and the schema files ([originals][schema_originals], [clones][schema_clones])
when adding new games.


[games]: games/
[originals]: originals/
[schema_originals]: schema_originals.yaml
[schema_clones]: schema_clones.yaml
[template]: .github/ISSUE_TEMPLATE.md
