# Open Source Game Clones

This is a source of [http://osgameclones.com](http://osgameclones.com). Feel
free to submit pull requests to add new games and improve information about
those already in the database.

## Games database

Check [`games.yaml`][games] out. All information is inside, and you should more or less
understand what's going on by reading it. Sorting is alphabetical, with an
exception of ScummVM, just because it's so many games at once.

## Add a clone/remake

Simplest way to contribute is to open a new issue and fill in the template.
Even better if you edit the [`games.yaml`][games] file directly. Your
changes will be submitted as a pull request.

If you're adding a new clone/remake:

```yaml
name: # required : Name of clone/remake
repo: # Link to source code
url: # Link to website
development: # One of: complete, very active, active, sporadic, halted
status: # One of: playable, semi-playable, unplayable
lang: [] # List of programming languages used
framework: [] # List of engines/tools used
license: # See licenses in schema.yaml
content: # One of: commercial, free, open, swapable # free means no cost, open means liberally licensed
info: # Notes about the game
updated: # Date when game was added or updated
images:
  - # Link(s) to screenshot(s)
video:
  youtube: # YouTube video ID
  vimeo: # Vimeo video ID
```

## Add a game parent

If you're adding a new game group:

```yaml
- name: # required : Name of the original game
  names:
    - # Other names for the game, or other games in the series
  meta:
    genre: [] # See genres in schema.yaml
    subgenre: [] # See genres in schema.yaml
    theme: [] # See genres in schema.yaml
  remakes:
    - # List of remakes, see above
  clones:
    - # List of clones, see above
```

A Wikipedia link is created for all original game names; if the article link is different, use the following syntax:

```yaml
name: [Name, Name of Wikipedia article]`
```

Please refer to the [template][template] and the [`schema.yaml`][schema] file
when adding new games.


[games]: https://github.com/piranha/osgameclones/edit/master/games.yaml
[schema]: https://github.com/piranha/osgameclones/edit/master/schema.yaml
[template]: https://github.com/piranha/osgameclones/blob/master/.github/ISSUE_TEMPLATE.md
