import logging
import os

from jinja2 import Environment, FileSystemLoader

from libs.utils import *
from connector.github_connector import GithubConnector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")


def run_template(**params):
    repository_name = params.get("dest")
    organization_name = params.get("organization")
    destination = f"{organization_name}/{repository_name}"
    workflow_type = params.get("workflow_type")
    resource_type = params.get("resource_type")
    core_version = params.get("core_version")

    github_connector = GithubConnector()

    service, resource = resource_type.lower().split(".")
    logging.info(f"[destination] {destination}")

    # Create Topics
    topics = [service, resource, workflow_type]
    topics.extend(github_connector.get_topics(destination))
    topics = list(set(topics))
    github_connector.create_topic(destination, topics)
    logging.info(f"[{destination}] Topics: {topics}")

    # Create Dockerfile
    _update_dockerfile(
        github_connector, destination, workflow_type, core_version, service
    )

    # Create setup.py
    _create_setup_py(github_connector, destination, service, workflow_type)

    # Create VERSION
    _create_version_file(github_connector, destination)

    # Create empty pip_requirements.txt
    _create_empty_pkg_file(github_connector, destination)


def _update_dockerfile(
    github_connector, destination, workflow_type, core_version, service
):
    path = "Dockerfile"

    # Create Dockerfile
    jinja_env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(TEMPLATE_DIR, workflow_type)),
        trim_blocks=True,
    )

    template = jinja_env.get_template("Dockerfile.tmpl")
    content = template.render(
        core_version=core_version,
        service=service,
    )

    if github_connector.get_file_contents(destination, path):
        logging.info(f"[{destination}] file {path} already exists, try to update")

        file_vo = github_connector.get_file(destination, path)
        if not is_need_update(file_vo, content):
            logging.info(
                f"[{destination}] There is no change, file is not updated: {path}"
            )

        try:
            github_connector.update_file(destination, path, content)
        except Exception as e:
            logging.error(
                f"[{destination}] Failed to update {path} to {destination} : {e}"
            )

    else:
        try:
            logging.info(f"[{destination}] Try to create {path} to {destination}")
            github_connector.create_file(destination, path, content)
        except Exception as e:
            logging.error(
                f"[{destination}] Failed to create {path} to {destination} : {e}"
            )


def _create_setup_py(github_connector, destination, service, workflow_type):
    path = "src/setup.py"

    # Create Dockerfile
    jinja_env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(TEMPLATE_DIR, workflow_type)),
        trim_blocks=True,
    )

    template = jinja_env.get_template("setup.py.tmpl")
    content = template.render(
        destination=destination,
        repository_name=destination.split("/")[1],
        plugin_package=f"spaceone-{service.lower()}",
    )

    if github_connector.get_file_contents(destination, path):
        logging.info(f"[{destination}] file {path} already exists, pass to create")
    else:
        try:
            logging.info(f"[{destination}] Try to create {path} to {destination}")
            github_connector.create_file(destination, path, content)
        except Exception as e:
            logging.error(
                f"[{destination}] Failed to create {path} to {destination} : {e}"
            )


def _create_version_file(github_connector, destination):
    path = "src/VERSION"

    if github_connector.get_file_contents(destination, path):
        logging.info(f"[{destination}] file {path} already exists, pass to create")
    else:
        try:
            logging.info(f"[{destination}] Try to create {path} to {destination}")
            github_connector.create_file(destination, path, "")
        except Exception as e:
            logging.error(
                f"[{destination}] Failed to create {path} to {destination} : {e}"
            )


def _create_empty_pkg_file(github_connector, destination):
    path = "pkg/pip_requirements.txt"

    if github_connector.get_file_contents(destination, path):
        logging.info(f"[{destination}] file {path} already exists, pass to create")
    else:
        try:
            logging.info(f"[{destination}] Try to create {path} to {destination}")
            github_connector.create_file(destination, path, "")
        except Exception as e:
            logging.error(
                f"[{destination}] Failed to create {path} to {destination} : {e}"
            )
