# TODO: Update trickle down imports. BAD! NEEDS FIXED!
import os
from flask import current_app
from app import cache

# Constants.
from app.utils.paths import PATHS
CONNECTOR_CMD = [
    PATHS["sudo"],
    "-n",
    "/opt/web-lgsm/bin/python",
    PATHS["ansible_connector"],
]

def log_wrap(item_name, item):
    """
    Kindly handles wrapping the debug output for logging.

    Args:
        item_name (str): Name of the thing we're debug printing.
        item (any): Item to be debug printed / logged.

    Return:
        log_msg (str): Message to be logged.
    """
    log_msg = f"{item_name} {str(type(item))}: {item}"
    return log_msg

# This is going away anyways, fine here for now. But going to be replaced when
# shell calls are replaced.
def docker_cmd_build(server):
    """
    Builds docker cmd reused all over for given GameServer.

    Args:
        server (GameServer): Game Server to build docker cmd for

    Returns:
        list: Docker command for GameServer as list.
    """
    return [
        PATHS["sudo"],
        "-n",
        PATHS["docker"],
        "exec",
        "--user",
        server.username,
        server.script_name,
    ]


# TODO: This needs a sudo password or it wont work...
def update_self():
    """
    Runs the web-lgsm self updates. Just wraps invocation of web-lgsm.py --auto
    update to run the actual update or check for updates.

    Returns:
        Str: String containing update status, based on web-lgsm.py script
             output.
    """

    from app.container import container

    cmd_id = "update_self"
    container.run_command().execute(cmd, None, cmd_id)

    proc_info = container.get_process().execute(cmd_id)
    if proc_info == None:
        return "Error: Something went wrong checking update status"

    if proc_info.exit_status > 0:
        return f"Error: {proc_info.stderr}"

    if "up to date" in proc_info.stdout:
        return "Already up to date!"

    if "Update Required" in proc_info.stdout:
        return "Web LGSM Upgraded! Restarting momentarily..."

