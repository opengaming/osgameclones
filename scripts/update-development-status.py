"""
This script updates games development status

To run, install from pip:
- pygithub
- python-gitlab

Add environment variables:
- GH_TOKEN (see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-token)
- GL_TOKEN (see https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token)
"""
import os
import re
import yaml

from pathlib import Path
from datetime import datetime, timedelta
from github import Github, GithubException
from gitlab import Gitlab

GH_REGEX = re.compile(r'https://github.com/([^/]+)/([^/]+)')
GL_REGEX = re.compile(r'https://gitlab.com/([^/]+/[^/]+)')


def main():
    gh = Github(os.environ["GH_TOKEN"])
    gl = Gitlab('https://gitlab.com', private_token=os.environ["GL_TOKEN"])

    for filename in Path('games').iterdir():
        if not filename.is_file() or filename.suffix != '.yaml':
            continue

        games = yaml.safe_load(open(filename, encoding='utf-8'))
        for game in games:
            repo_url = game.get('repo', '')

            if game.get('development', '') == 'complete':
                continue

            latest_commit_date = get_latest_commit_date(repo_url, gh, gl)

            if latest_commit_date is None:
                continue

            diff = datetime.now() - latest_commit_date

            if diff < timedelta(weeks=1):
                game['development'] = 'very active'
            elif diff < timedelta(weeks=4):
                game['development'] = 'active'
            elif diff < timedelta(days=365):
                game['development'] = 'sporadic'
            else:
                game['development'] = 'halted'

        yaml.dump(games, open(filename, 'w', encoding='utf-8'), sort_keys=False)
        print(filename, 'has been updated')


def is_github_repo(repo):
    return 'https://github.' in repo


def is_gitlab_repo(repo):
    return 'https://gitlab.' in repo


def get_latest_commit_date(repo_url, gh, gl):
    if is_github_repo(repo_url):
        return get_latest_commit_date_for_github(gh, repo_url)
    elif is_gitlab_repo(repo_url):
        return get_latest_commit_date_for_gitlab(gl, repo_url)

    print('The', repo_url, 'repository could not be updated')


def get_latest_commit_date_for_github(gh, repo_url):
    match = re.match(GH_REGEX, repo_url)
    if not match:
        return

    owner, repo = match.groups()
    try:
        gh_repo = gh.get_repo(f"{owner}/{repo}")
        commits = gh_repo.get_commits()
    except GithubException as e:
        print(f'Error getting repo info for {owner}/{repo}: {e}')

        return

    return list(commits)[0].committer.created_at


def get_latest_commit_date_for_gitlab(gl, repo_url):
    match = re.match(GL_REGEX, repo_url)

    if not match:
        return

    project_namespace = match.groups()[0]
    project = gl.projects.get(project_namespace)

    commits = project.commits.list()

    return datetime.strptime(
        ''.join(commits[0].committed_date.rsplit(':', 1)),
        '%Y-%m-%dT%H:%M:%S.%f%z'
    ).replace(tzinfo=None)


if __name__ == "__main__":
    main()
