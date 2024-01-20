import logging
import os

_LOGGER = logging.getLogger(__name__)


def list_workflows(workflow_type="plugin"):
    try:
        workflow_files = []

        base_common_path = "./workflows/common"
        workflow_files += _read_workflow_files(base_common_path)

        base_path = f"./workflows/{workflow_type}"
        workflow_files += _read_workflow_files(base_path)

        return workflow_files
    except Exception as e:
        logging.info(f"Failed to list workflows data(invalid or lack of topics): {e}")
        raise Exception(e)


def is_need_update(file_vo, workflow):
    contents = file_vo.decoded_content.decode("utf-8")

    if contents == workflow:
        return False

    return True


def _read_workflow_files(base_path):
    ret = []

    list_dir = os.listdir(base_path)
    for workflow_name in list_dir:
        with open(f"{base_path}/{workflow_name}", "r") as f:
            workflow_contents = f.read()

        ret.append({f".github/workflows/{workflow_name}": workflow_contents})

    return ret
