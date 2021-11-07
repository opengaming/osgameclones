"""
This script finds repos participating in hacktoberfest 2021:
- Hosted on github or gitlab
- Includes the "hacktoberfest" topic

To run, install from pip:
- pygithub
- python-gitlab

Add environment variables:
- GH_TOKEN (see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-token)
- GL_TOKEN (see https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token)
"""
import os
import re

from github import Github, GithubException
from gitlab import Gitlab
from pathlib import Path

import yaml

GH_REGEX = re.compile(r"https://github.com/([^/]+)/([^/]+)")
GL_REGEX = re.compile(r"https://gitlab.com/([^/]+/[^/]+)")


def main():
    gh = Github(os.environ["GH_TOKEN"])
    gl = Gitlab("https://gitlab.com", private_token=os.environ["GL_TOKEN"])
    hacktober_games = {}
    for p in Path('games').iterdir():
        if p.is_file() and p.suffix == ".yaml":
            games = yaml.safe_load(open(p, encoding="utf-8"))
            for game in games:
                repo_url = game.get("repo", "")
                if not repo_url:
                    continue
                match = re.match(GH_REGEX, repo_url)
                if match:
                    owner, repo = match.groups()
                    try:
                        gh_repo = gh.get_repo(f"{owner}/{repo}")
                    except GithubException as e:
                        print(f"Error getting repo info for {owner}/{repo}: {e}")
                        continue
                    topics = gh_repo.get_topics()
                    if "hacktoberfest" in topics:
                        game["platform"] = "github"
                        game["stars"] = gh_repo.stargazers_count
                        hacktober_games[game["name"]] = game
                else:
                    match = re.match(GL_REGEX, repo_url)
                    if match:
                        project_namespace = match.groups()[0]
                        project = gl.projects.get(project_namespace)
                        if "hacktoberfest" in project.topics:
                            game["platform"] = "gitlab"
                            game["stars"] = project.star_count
                            hacktober_games[game["name"]] = game
    for name, game in hacktober_games.items():
        stars_badge = f"![stars](https://img.shields.io/badge/{game['platform']}%20stars-{game['stars']}-blue)"
        langs = ", ".join(f"`{lang}`" for lang in game.get('lang', []))
        frameworks = ", ".join(f"`{fw}`" for fw in game.get('framework', []))
        print(f"- [**{name}** {stars_badge}]({game['repo']}): ({game.get('development', '')} {game.get('status', '')} {langs} {frameworks})")


if __name__ == "__main__":
    main()
