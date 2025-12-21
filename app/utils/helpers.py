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
from functools import lru_cache

from app.models import GameServer, Audit
from app import db
from app import cache
from app.config.config_manager import ConfigManager

config = ConfigManager()

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

# Network stats globals.
prev_bytes_sent = psutil.net_io_counters().bytes_sent
prev_bytes_recv = psutil.net_io_counters().bytes_recv
prev_time = time.time()


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



def cancel_install(pid):
    """
    Calls the ansible playbook connector to kill running installs upon request.

    Args:
        pid (int): Process ID or running install to cancel.

    Returns:
        bool: True if install canceled successfully, False otherwise.
    """
    from app.services import ProcInfoService, CommandExecService

    # NOTE: For the --cancel option on the ansible connector script we pass in
    # the pid of the running install, instead of a game server's ID.
    cmd = CONNECTOR_CMD + ["--cancel", str(pid)]

    cmd_id = 'cancel_install'
    CommandExecService(ConfigManager()).run_command(cmd, None, cmd_id)
    proc_info = ProcInfoService().get_process(cmd_id)

    if proc_info == None:
        return False

    if proc_info.exit_status > 0:
        return False

    return True


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


def should_use_ssh(server):
    """
    Used to determine if SSH should be used for a particular server.

    Args:
        server (GameServer): Game server object to check.
    Returns:
        bool: True if should connect via ssh, false otherwise.
    """
    if server.install_type == "remote" or (
        server.install_type == "local" and server.username != USER
    ):
        return True

    return False


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


def get_running_installs():
    """
    Gets list of running install thread names, if any are currently running.

    Returns:
        dict: Mapping of observed running threads for game server IDs to game
              server names.
    """
    threads = threading.enumerate()
    # Get all active threads.
    running_install_threads = dict()

    for thread in threads:
        if thread.is_alive() and thread.name.startswith("web_lgsm_install_"):
            server_id = thread.name.replace("web_lgsm_install_", "")
            server = GameServer.query.filter_by(id=server_id).first()

            # Check game server exists.
            if server:
                running_install_threads[server_id] = server.install_name

    return running_install_threads



def normalize_path(path):
    """
    Little helper function used to normalize supplied path in order to check if
    two path str's are equivalent. Used by delete_server() in path comparison
    to ensure NOT deleting home dir by any other name.

    Args:
        path (str): Path to clear up

    """
    # Remove extra slashes.
    path = re.sub(r"/{2,}", "/", path)

    # Remove trailing slash unless it's the root path "/".
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    return path


def delete_server(server, remove_files, delete_user):
    """
    Does the actual deletions for the /delete route.

    Args:
        server (GameServer): Game server to delete.
        remove_file (bool): Config setting to keep/remove files on delete.
        delete_user (bool): Config setting to keep/remove user on delete.

    Returns:
        Bool: True if deletion was successful, False if something went wrong.
    """
    from app.services import ProcInfoService, CommandExecService
    if not remove_files:
        server.delete()
        flash(f"Game server, {server.install_name} deleted!")
        return True

    if server.install_type == "local":
        if server.username == USER:
            if normalize_path(f"/home/{USER}") == normalize_path(server.install_path):
                flash("Will not delete users home directories!", category="error")
                return False

            if normalize_path(CWD) == normalize_path(server.install_path):
                flash(
                    "Will not delete web-lgsm base installation directory!",
                    category="error",
                )
                return False

            if os.path.isdir(server.install_path):
                shutil.rmtree(server.install_path)

        if delete_user and server.username != USER:
            cmd = CONNECTOR_CMD + ["--delete", str(server.id)]
            CommandExecService(ConfigManager()).run_command(cmd)

    if server.install_type == "remote":
        if delete_user:
            flash(
                f"Warning: Cannot delete game server users for remote installs. Only removing files!"
            )

        # Check to ensure is not a home directory before delete. Just some
        # idiot proofing, myself being the chief idiot.
        if normalize_path(f"/home/{server.username}") == normalize_path(
            server.install_path
        ):
            flash("Will not delete remote users home directories!", category="error")
            return False

        cmd = [PATHS["rm"], "-rf", server.install_path]

        success = CommandExecService(ConfigManager()).run_command(cmd, server, server.id)
        proc_info = ProcInfoService().get_process(server.id)

        # If the ssh connection itself fails return False.
        if not success or proc_info == None:
            current_app.logger.info(log_wrap("proc_info", proc_info))
            flash("Problem connecting to remote host!", category="error")
            return False

        if proc_info.exit_status > 0:
            current_app.logger.info(proc_info)
            flash("Delete command failed! Check logs for more info.", category="error")
            return False

    flash(f"Game server, {server.install_name} deleted!")
    server.delete()
    return True


def get_servers():
    """
    Turns data in games_servers.json into servers list for install route.

    Returns:
        dict: Dictionary mapping short server names to long server names.
    """

    # Try except in case problem with json files.
    try:
        with open("json/game_servers.json", "r") as file:
            json_data = json.load(file)

        return {
            key: (value1, value2)
            for key, value1, value2 in zip(
                json_data["servers"],
                json_data["server_names"],
                json_data["app_imgs"]
            )
        }
    except:
        # Return empty dict triggers error. In python empty dict == False.
        return {}


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

    from app.services import ControlService
    control_service = ControlService()
    controls = control_service.get_controls(server, current_user)
    for control in controls:
        # Aka is valid control.
        if ctrl == control.short_ctrl:
            return True

    return False


def get_lgsmsh(lgsmsh):
    """
    Function for pulling down the latest linuxgsm.sh script from their URL when
    needed. Fakes wget's user agent to get requests to work.

    Args:
        lgsmsh (str): Path to linuxgsm.sh script file (aka web-lgsm/scripts/).

    Returns:
        None: Just fetches latest file if needed, returns nothing.
    """
    try:
        headers = {"User-Agent": "Wget/1.20.3 (linux-gnu)"}
        response = requests.get("https://linuxgsm.sh", headers=headers)
        with open(lgsmsh, "wb") as f:
            f.write(response.content)
        os.chmod(lgsmsh, 0o755)
    except Exception as e:
        # For debug.
        current_app.logger.debug(e)

    current_app.logger.info("Latest linuxgsm.sh script fetched!")


def check_and_get_lgsmsh(lgsmsh):
    """
    Checks if linuxgsm.sh already exists and if not, gets it. Also checks if
    current version is older than 3 weeks old and if so get's a fresh copy.

    Args:
        lgsmsh (str): Path to linuxgsm.sh script file (aka web-lgsm/scripts/).

    Returns:
        None: Just fetches latest file if needed, returns nothing.
    """
    if not os.path.isfile(lgsmsh):
        get_lgsmsh(lgsmsh)
        return

    three_weeks_in_seconds = 1814400
    if int(time.time() - os.path.getmtime(lgsmsh)) > three_weeks_in_seconds:
        get_lgsmsh(lgsmsh)


def update_self():
    """
    Runs the web-lgsm self updates. Just wraps invocation of web-lgsm.py --auto
    update to run the actual update or check for updates.

    Returns:
        Str: String containing update status, based on web-lgsm.py script
             output.
    """

    from app.services import ProcInfoService, CommandExecService
    update_cmd = ["./web-lgsm.py", "--auto"]

    cmd_id = "update_self"
    CommandExecService(ConfigManager()).run_command(cmd, None, cmd_id)

    proc_info = ProcInfoService().get_process(cmd_id)
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


def clear_proc_info_post_install(server_id, app_context):
    """
    Clears the stdout & stderr buffers for proc_info after install finishes.
    Does so by checking running install threads, if thread for ID is gone from
    running list and game server install marked finished, clear buffers.

    Args:
        server_id (str): UUID for game server.
        app_context (AppContext): Optional Current app context needed for
                                  logging in a thread.
    """

    from app.services import ProcInfoService
    # App context needed for logging in threads.
    if app_context:
        app_context.push()

    max_lifetime = 3600  # 1 Hour TTL
    runtime = 0

    # Little buffer to make sure install daemon thread starts first.
    time.sleep(5)
    current_app.logger.info("<CLEAR DAEMON> - Starting clear thread")

    while runtime < max_lifetime:
        all_installs = get_running_installs()

        # Aka install finished or died.
        if server_id not in all_installs:
            server = GameServer.query.filter_by(id=server_id).first()

            # Rare edge case if server deleted before thread dies.
            if server == None:
                return

            # If install thread not running anymore and install marked
            # finished, clear out the old proc_info object.
            if server.install_finished and not server.install_failed:
                current_app.logger.info("<CLEAR DAEMON> - Thread Cleared!")
                ProcInfoService().remove_process(server_id)
                return

        time.sleep(5)
        runtime += 5


def validation_errors(form):
    """
    Flashes messages for validation errors if there are any.

    Args:
        form (FlaskForm): Flask form object to check.

    Returns:
        dict: Returns dictionary of errors and fields.
    """
    form_name = type(form).__name__
    current_app.logger.info(f"{form_name} submission invalid!")
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.debug(f"{field}: {error}")
                flash(f"{field}: {error}", "error")



def audit_log_event(user_id, message):
    """
    Helper function to create new audit log entries. Adds new messages to
    database and logs them using custom audit_logger.
    """
    audit_entry = Audit(
        user_id=user_id,
        message=message
    )
    db.session.add(audit_entry)
    db.session.commit()

    current_app.audit_logger.info(message)

