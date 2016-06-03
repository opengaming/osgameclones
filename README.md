# Open Source Game Clones

This is a source of [http://osgameclones.com](http://osgameclones.com). Feel
free to submit pull requests to add new games and improve information about
those already in the database.

## How

Check `games.yaml` out. All information is inside, and you should more or less
understand what's going on by reading it. Sorting is alphabetical, with an
exception of ScummVM, just because it's so many games at once.

Simplest way to contribute:
[edit games.yaml](https://github.com/piranha/osgameclones/edit/master/games.yaml),
and then your changes will be submitted as a pull request.

Please refer to [this template](https://github.com/piranha/osgameclones/blob/master/.github/ISSUE_TEMPLATE.md).

- `name`/`names`: Name of the original game
  - If the game goes under multiple names, or if the clone is inspired by multiple related games, use `names`
  - A Wikipedia link is created for the name; if the article link is different, use the syntax `[Name, Name of Wikipedia article]`
- `clones`/`reimplementations`: List the clones/reimplementations under this heading. Multiple clones can be listed.
  - `name`: Name of the clone
  - `url`: URL of clone main page
  - `repo`: (optional) if the clone has an online code repository (e.g. GitHub), link here
  - `info`: free text, but try to use terms already used in the list. Should include code details. HTML is supported
  - `status`: (string) status of the project (active, halted)
  - `license`: (string) project license
  - `lang`: (string|list) programming languages used in the project
  - `framework`: (string|list) programming frameworks and/or engines used in the project
  - `added`: (optional) date when this clone was first added. Newly added clones are highlighted
  - `media`: (optional) list of screenshots or videos for the clone
    - `image`: URL of an image to display, preferrably a thumbnail
    - `url`: (optional) link to a bigger image, when the user clicks the thumbnail
    - `raw`: to embed raw HTML, e.g. to embed a video, use this tag followed by raw HTML
