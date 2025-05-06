import os

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

# Update issue
labels = set(pr.labels)
for file in files:
    if file.filename.endswith(".py"):
        labels.add("python")
    elif file.filename.endswith(".js"):
        labels.add("javascript")
    # TODO: set game-correction, game-addition
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