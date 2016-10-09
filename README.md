# Open Source Game Clones

This is a source of [http://osgameclones.com](http://osgameclones.com). Feel
free to submit pull requests to add new games and improve information about
those already in the database.

## Games database

Check [`games.yaml`][games] out. All information is inside, and you should more or less
understand what's going on by reading it. Sorting is alphabetical, with an
exception of ScummVM, just because it's so many games at once.

## Add a game

Simplest way to contribute is to edit the [`games.yaml`][games] file. Your
changes will be submitted as a pull request.

- `name`/`names`: Name of the original game
  - If the game goes under multiple names, or if the clone is inspired by multiple related games, use `names`
  - A Wikipedia link is created for the name; if the article link is different, use the syntax `[Name, Name of Wikipedia article]`
- `clones`/`reimplementations`: List the clones/reimplementations under this heading. Multiple clones can be listed.

Please refer to the [template][template] and the [`schema.yaml`][schema] file
when adding new games.


[games]: https://github.com/piranha/osgameclones/edit/master/games.yaml
[schema]: https://github.com/piranha/osgameclones/edit/master/schema.yaml
[template]: https://github.com/piranha/osgameclones/blob/master/.github/ISSUE_TEMPLATE.md
