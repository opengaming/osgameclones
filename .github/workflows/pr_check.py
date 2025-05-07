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
change_comment: str
if changed_files:
    change_comment = f"\nFiles in PR: {', '.join(changed_files)}"
else:
    change_comment = "\n<!--No changes found!-->"
content += f"\n<!--{change_comment}-->"


def load_games_file(filename: str, sha: str):
    try:
        contents = repo.get_contents(filename, sha)
    except GithubException as e:
        print("Cannot get file at", filename, e)
        return {}
    file = contents.decoded_content.decode()
    parsed = yaml.safe_load(file)
    return {game["name"]: game for game in parsed}


# Update issue
labels = set(pr.labels)
for file in files:
    if file.filename.endswith(".py"):
        labels.add("python")
    elif file.filename.endswith(".js"):
        labels.add("javascript")
    elif re.match(r"^games/\w+\.yaml$", file.filename):
        print("Game file changed", file)
        old_games = load_games_file(file.filename, pr.base.sha)
        new_games = load_games_file(file.filename, pr.head.sha)

        for game in old_games:
            if game not in new_games:
                print("Removed game", game)
                labels.add("game-correction")
        for game in new_games:
            if game not in old_games:
                print("Added game", game)
                labels.add("game-addition")
        for game in old_games:
            if game in new_games:
                if old_games[game] != new_games[game]:
                    print("Changed game", game)
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