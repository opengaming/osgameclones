import os
import re
import yaml
from github import Github, GithubException

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
GITHUB_BOT_LOGIN = "github-actions[bot]"
content = "Hey there! Thanks for contributing a PR to osgameclones! 🎉"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPOSITORY)
pr = repo.get_pull(PR_NUMBER)
print("PR", pr.url)

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

# Scan files for changes
games_added = set()
games_changed = set()
games_removed = set()
has_py = False
has_js = False
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
        for game in old_games:
            if game in new_games:
                if old_games[game] != new_games[game]:
                    games_changed.add(game)

# Update comment based on changed games
if games_added:
    content += f"\nGame{'s'[:len(games_added) ^ 1]} added: {', '.join(games_added)} 🎊"
if games_changed:
    content += f"\nGame{'s'[:len(games_changed) ^ 1]} updated: {', '.join(games_changed)} 👏"
if games_removed:
    content += f"\nGame{'s'[:len(games_removed) ^ 1]} removed: {', '.join(games_removed)} 😿"

# Update issue labels
labels = set(pr.labels)
if has_py:
    labels.add("python")
if has_js:
    labels.add("javascript")
if games_added:
    labels.add("game-addition")
if games_changed or games_removed:
    labels.add("game-correction")
if labels != set(pr.labels):
    print("Updating labels from", pr.labels, "to", labels)
    pr.set_labels(*labels)

# Update GitHub PR
for c in pr.get_issue_comments():
    print("checking comment", c.user.login)
    if c.user.login == GITHUB_BOT_LOGIN:
        print("found bot comment", c.body)
        comment = c
        if comment.body != content:
            comment.edit(content)
        break
else:
    print("bot comment not found")
    try:
        comment = pr.create_issue_comment(content)
    except GithubException as e:
        print("cannot create issue comment - possibly a non-standard PR", e)

"""
Ideas for more PR suggestions
- If repo is github, suggest releases feed
- Scrape repo and url and look for screenshot candidates
"""