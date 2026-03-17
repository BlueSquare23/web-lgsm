import os
import io
import re
import pwd
import json
import time
import uuid
import shlex
import psutil
import shutil
import socket
import getpass
import paramiko
import requests
import subprocess
import threading

from datetime import datetime, timedelta
from flask import flash, current_app, send_file, send_from_directory, url_for, redirect

from app import db
from app import cache

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
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


def get_uid(username):
    """
    Translates a username to a uid using pwd module.

    Args:
        username(str): User to get uid for

    Returns:
        uid (str): Either returns the uid for user or None if can't get uid
    """
    try:
        user_info = pwd.getpwnam(username)
        return user_info.pw_uid
    except KeyError:
        return None


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



# TODO/NOTE: This can stay for now, but its on the chopping block. This
# validation should now be handled by flask-wtf/wtforms classes. Once I get
# this fixed up in the controls route, this can go.
def valid_command(ctrl, server, current_user):
    """
    Validates short commands from controls route form for game server. Some
    game servers may have specific game server command exemptions. This
    function basically just checks if supplied cmd is in list of accepted cmds
    from get_controls().

    Args:
        ctrl (str): Short ctrl string to validate.
        server (GameServer): Game server to check command against.
        current_user (LocalProxy): Currently logged in flask user object.

    Returns:
        bool: True if cmd is valid for user & game server, False otherwise.
    """

    from app.container import container
    controls = container.list_controls().execute(server, current_user)
    for control in controls:
        # Aka is valid control.
        if ctrl == control.short_ctrl:
            return True

    return False


def update_self():
    """
    Runs the web-lgsm self updates. Just wraps invocation of web-lgsm.py --auto
    update to run the actual update or check for updates.

    Returns:
        Str: String containing update status, based on web-lgsm.py script
             output.
    """

    from app.container import container
    update_cmd = ["./web-lgsm.py", "--auto"]

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


def is_ssh_accessible(hostname):
    """
    Checks if a hostname/IP has an accessible SSH server on port 22.

    Args:
        hostname (str): The hostname or IP address to check.

    Returns:
        bool: True if SSH is accessible, False otherwise.
    """
    port = 22
    timeout = 5

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((hostname, port))

        # Check the result: 0 means the port is open.
        if result == 0:
            return True
        else:
            return False
    except socket.gaierror:
        return False
    except socket.error as e:
        return False
    finally:
        sock.close()


def read_changelog():
    """
    Reads in the local CHANGELOG.md file and returns its contents.

    Args:
        None

    Returns:
        str: Contents of CHANGELOG.md file or err str.
    """
    try:
        with open("CHANGELOG.md", "r") as file:
            contents = file.read()
        return contents

    except Exception as e:
        return f"Problem reading CHANGELOG.md: {e}"

