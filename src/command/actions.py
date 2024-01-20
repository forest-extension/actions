import os

from libs.utils import *
from connector.github_connector import GithubConnector


def run_actions(**params):
    github_connector = GithubConnector()

    repository_name = params.get("dest")
    organization_name = params.get("organization")
    destination = f"{organization_name}/{repository_name}"
    workflow_type = params.get("workflow_type")

    workflows = list_workflows(workflow_type)
    for workflow in workflows:
        _update_workflow(github_connector, destination, workflow)


def _update_workflow(github_connector, destination, workflow):
    for path, content in workflow.items():
        if github_connector.get_file_contents(destination, path):
            logging.info(f"[{destination}] file {path} already exists, try to update")

            file_vo = github_connector.get_file(destination, path)
            if not is_need_update(file_vo, content):
                logging.info(
                    f"[{destination}] There is no change, file is not updated: {path}"
                )
                continue

            try:
                pass
                # github_connector.update_file(destination, path, content)
            except Exception as e:
                logging.error(
                    f"[{destination}] Failed to update {path} to {destination} : {e}"
                )

        else:
            try:
                logging.info(f"[{destination}] Try to create {path} to {destination}")
                # github_connector.create_file(destination, path, content)
            except Exception as e:
                logging.error(
                    f"[{destination}] Failed to create {path} to {destination} : {e}"
                )
