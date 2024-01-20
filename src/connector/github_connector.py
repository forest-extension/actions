import os
import github
import logging

from github import Github
from github.GithubException import *

logging.basicConfig(level=logging.INFO)


class GithubConnector:
    def __init__(self):
        self.token = os.getenv("PAT_TOKEN", None)
        self.github_client = Github(self.token)
        self.committer = github.InputGitAuthor(
            name="forest-extension-admin", email="admin@forest-extension"
        )

    def list_repo(self, org):
        repositories = []
        for repo in self.github_client.get_organization(org).get_repos():
            repositories.append(repo)

        return repositories

    def search_repo(self, org, keyword):
        repositories = []
        for repo in self.github_client.search_repositories(
            query=f"org:{org} {keyword}"
        ):
            repositories.append(repo)

        logging.info(f"found {len(repositories)} repositories")
        return repositories

    def get_repo(self, destination):
        try:
            return self.github_client.get_repo(destination)
        except UnknownObjectException as e:
            if "Branch not found" in str(e):
                logging.error("UnknownObjectException: Branch not found")
            elif "Release not found" in str(e):
                logging.error("UnknownObjectException: Release not found")
            else:
                logging.error(f"UnknownObjectException: {e}")
            raise Exception(e)
        except BadCredentialsException as e:
            logging.error(f"BadCredentialsException: {destination}")
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_topics(self, destination):
        repo_vo = self.get_repo(destination)
        return repo_vo.get_topics()

    def create_topic(self, destination: str, topics: list) -> None:
        repo_vo = self.get_repo(destination)
        try:
            repo_vo.replace_topics(topics)
        except Exception as e:
            raise Exception(e)

    def get_file(self, destination, path):
        repo_vo = self.get_repo(destination)

        try:
            return repo_vo.get_contents(path=path, ref="master")
        except GithubException:
            return None
        except Exception as e:
            raise Exception(e)

    def create_file(self, destination, path, content):
        repo_vo = self.get_repo(destination)
        try:
            repo_vo.create_file(
                path=path,
                message="[CI] Deploy CI",
                content=content,
                branch="master",
                committer=self.committer,
            )
            return 200
        except Exception as e:
            raise Exception(e)

    def update_file(self, destination, path, content):
        repo_vo = self.get_repo(destination)
        file_vo = self.get_file(destination, path)

        try:
            repo_vo.update_file(
                path=path,
                message="[CI] Deploy CI",
                content=content,
                sha=file_vo.sha,
                branch="master",
                committer=self.committer,
            )
            return 200
        except Exception as e:
            raise Exception(e)

    def get_file_contents(self, destination, path):
        logging.info(f"[{destination}] get file contents: {path}")
        file_vo = self.get_file(destination, path)
        if file_vo is None:
            return None
