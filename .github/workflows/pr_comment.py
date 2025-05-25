import json
import os
import sys
import zipfile
from pathlib import Path

import httpx
from github import Github, GithubException
from github.Artifact import Artifact

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
RUN_ID = int(os.environ["RUN_ID"])
GITHUB_BOT_LOGIN = "github-actions[bot]"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPOSITORY)

# Download artifact
run = repo.get_workflow_run(RUN_ID)
print("Run", run)
artifacts = run.get_artifacts()
artifact: Artifact
for a in artifacts:
    print("Artifact", a)
    if a.name == "pr":
        artifact = a
        break
else:
    print("Could not find pr artifact")
    sys.exit(1)
resp = httpx.get(
    artifact.archive_download_url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}, follow_redirects=True)
if not resp.is_success:
    print("Download request failed", resp)
    sys.exit(1)
with(open("out.zip", "wb")) as f:
    f.write(resp.content)
with zipfile.ZipFile("out.zip", "r") as zip_ref:
    zip_ref.extractall(".")

# Get PR content
output = json.loads(Path("output.json").read_text())
print("Comment content", output)
pr = repo.get_pull(output["pr"])
print("PR", pr.url)
output["labels"] = set(output["labels"])

# Update GitHub PR
for c in pr.get_issue_comments():
    print("checking comment", c.user.login)
    if c.user.login == GITHUB_BOT_LOGIN:
        print("found bot comment", c.body)
        comment = c
        if comment.body != output["content"]:
            comment.edit(output["content"])
        break
else:
    print("bot comment not found")
    try:
        comment = pr.create_issue_comment(output["content"])
    except GithubException as e:
        print("cannot create issue comment - possibly a non-standard PR", e)

# Update labels
if output["labels"] != set(label.name for label in pr.labels):
    print("Updating labels from", pr.labels, "to", output["labels"])
    pr.set_labels(*output["labels"])