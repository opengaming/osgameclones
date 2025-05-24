import os
from pathlib import Path

from github import Github, GithubException

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
GITHUB_BOT_LOGIN = "github-actions[bot]"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPOSITORY)
pr = repo.get_pull(PR_NUMBER)
print("PR", pr.url)

# Get PR content
content = Path(f"./pr/contents.md").read_text()
print("Comment content", content)

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
