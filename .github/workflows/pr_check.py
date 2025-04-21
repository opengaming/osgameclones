import os

import httpx
from github import Github
from unidiff import PatchSet

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
GITHUB_BOT_LOGIN = "github-actions[bot]"
content = "Hey there! Thanks for contributing a PR to osgameclones! 🎉"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPOSITORY)
pr = repo.get_pull(PR_NUMBER)

# Get game changes
patchset = PatchSet(httpx.get(pr.diff_url).read().decode())
added = [patch.target_file for patch in patchset.added_files]
modified = [patch.target_file for patch in patchset.modified_files]
removed = [patch.target_file for patch in patchset.removed_files]
change_comment = ""
if added:
    change_comment += f"\nAdded files: {', '.join(added)}"
if modified:
    change_comment += f"\nModified files: {', '.join(modified)}"
if removed:
    change_comment += f"\nRemoved files: {', '.join(removed)}"
if change_comment:
    content += f"\n<!--{change_comment}-->"
else:
    content += f"\n<!--No changes found!-->"

# Update GitHub PR
for c in pr.get_comments():
    if c.user.login == GITHUB_BOT_LOGIN:
        comment = c
        if comment.body != content:
            comment.edit(content)
        break
else:
    comment = pr.create_issue_comment(content)
