import os
import re
import sys
import pwd
import json
import glob
import time
import shlex
import string
import logging
import psutil
import shutil
import socket
import getpass
import paramiko
import requests
import subprocess
import threading
import configparser

from datetime import datetime, timedelta
from threading import Thread
from flask import flash, current_app

from . import db
from .models import GameServer
from .proc_info_vessel import ProcInfoVessel
from .cmd_descriptor import CmdDescriptor

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
ANSIBLE_CONNECTOR = os.path.join(CWD, "playbooks/ansible_connector.py")
PATHS = {
    "docker": "/usr/bin/docker",
    "sudo": "/usr/bin/sudo",
    "tmux": "/usr/bin/tmux",
    "cat": "/usr/bin/cat",
    "kill": "/usr/bin/kill",
    "find": "/usr/bin/find",
    "ssh-keygen": "/usr/bin/ssh-keygen"
}
CONNECTOR_CMD = [
    PATHS['sudo'], '-n',
    os.path.join(CWD, 'venv/bin/python'),
    ANSIBLE_CONNECTOR
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


def check_require_auth_setup_fields(username, password1, password2):
    """Ensure supplied auth fields for creating a new user are supplied.
    Returns True if they're all good, False if there's a problem with them."""
    # Make sure required form items are supplied.
    for form_item in (username, password1, password2):
        if form_item == None or form_item == "":
            flash("Missing required form field(s)!", category="error")
            return False

        if len(form_item) > 150:
            flash("Form field too long!", category="error")
            return False

    # To try to nip sql, xss, template injections in the bud.
    if contains_bad_chars(username):
        flash("Username Contains Illegal Character(s)", category="error")
        flash(
            r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &""",
            category="error",
        )
        return False

    return True


def valid_password(password1, password2):
    """Runs supplied auth route passwords against some basic checks. Returns
    False if passwords bad, True if all good."""
    # Setup rudimentary password strength counter.
    lower_alpha_count = 0
    upper_alpha_count = 0
    number_count = 0
    special_char_count = 0

    # Adjust password strength values.
    for char in list(password1):
        if char in string.ascii_lowercase:
            lower_alpha_count += 1
        elif char in string.ascii_uppercase:
            upper_alpha_count += 1
        elif char in string.digits:
            number_count += 1
        else:
            special_char_count += 1

    ## Check if submitted form data for issues.
    # Verify password passes basic strength tests.
    if upper_alpha_count < 1 and number_count < 1 and special_char_count < 1:
        flash("Passwords doesn't meet criteria!", category="error")
        flash(
            "Must contain: an upper case character, a number, and a \
                                special character",
            category="error",
        )
        return False

    elif password1 != password2:
        flash("Passwords don't match!", category="error")
        return False

    elif len(password1) < 12:
        flash("Password is too short!", category="error")
        return False

    return True


def run_cmd_popen(cmd, proc_info=ProcInfoVessel(), app_context=False):
    """
    General purpose subprocess.Popen wrapper function.

    Args:
        cmd (list): Command to be run via subprocess.Popen.
        proc_info (obj): Optional object to store info about running process.
    """
    config = configparser.ConfigParser()
    config.read("main.conf")
    end_in_newlines = get_config_value(config, "settings", "end_in_newlines", True, True)
    clear_output_on_reload = get_config_value(config, "settings", "clear_output_on_reload", True, True)

#    if clear_output_on_reload:
#        proc_info.stdout.clear()
#        proc_info.stderr.clear()

    # Set lock flag to true.
    proc_info.process_lock = True

    # App context needed for logging in threads.
    if app_context:
        app_context.push()

    current_app.logger.info(log_wrap('cmd', cmd))
    
    # subproc call, Bytes mode, not buffered.
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False, bufsize=-1
    )
    
    proc_info.pid = proc.pid

    # TODO: Refactor duplicate code below into one `process_output` function.
    # Just from after break on down. Can reuse code for stdout & stderr.
    while True:
        stdout_line = proc.stdout.read1().decode("utf-8")

        if not stdout_line:
            break

        for rline in stdout_line.split('\r'):
            if rline == "":
                continue

            # Add back in carriage returns, ignoring lines terminated with a newline.
            if not rline.endswith('\r') and not rline.endswith('\n'):
                rline = rline + '\r'

            for line in rline.split('\n'):
                if line == "":
                    continue

                # Add back in newlines, ignoring lines terminated with a carriage return.
                if not line.endswith('\n') and not line.endswith('\r'):
                    line = line + '\n'

                # Add the newlines for optional old-style setting.
                if end_in_newlines:
                    if not line.endswith('\n'):
                        line = line + '\n'

                proc_info.stdout.append(line)
                log_msg = log_wrap('stdout', line.replace('\n', ''))
                current_app.logger.debug(log_msg)

    while True:
        stderr_line = proc.stderr.read1().decode("utf-8")

        if not stderr_line:
            break

        for rline in stderr_line.split('\r'):
            if rline == "":
                continue

            # Add back in carriage returns, ignoring lines terminated with a newline.
            if not rline.endswith('\r') and not rline.endswith('\n'):
                rline = rline + '\r'

            for line in rline.split('\n'):
                if line == "":
                    continue

                # Add back in newlines, ignoring lines terminated with a carriage return.
                if not line.endswith('\n') and not line.endswith('\r'):
                    line = line + '\n'

                # Add the newlines for optional old-style setting.
                if end_in_newlines:
                    if not line.endswith('\n'):
                        line = line + '\n'

                proc_info.stderr.append(line)
                log_msg = log_wrap('stderr', line.replace('\n', ''))
                current_app.logger.debug(log_msg)

    proc_info.exit_status = proc.wait()

    # Reset process_lock flag.
    proc_info.process_lock = False


# Snips any lingering `watch` processes.
def kill_watchers(last_request_for_output):
    # TODO: Refactor this whole thing. We can keep track of watch pid's now so
    # use that do do the snipping I think.
    # Add three minutes to last_request_for_output time as a timeout. In other
    # words, only kill lingering watch processes if output page hasn't been
    # requested for past three minutes.
    three_minutes = 180
    ouput_page_timeout = last_request_for_output + three_minutes

    # Greater than because of the natural flow of time. Epoch time now is a
    # larger integer than epoch time three minutes ago. So if the page timeout
    # is great than the now time the timeout has not been hit yet.
    if ouput_page_timeout > int(time.time()):
        return

    # Get all processes named 'watch'
    watch_processes = []
    for proc in psutil.process_iter(["pid", "name", "username"]):
        if proc.info["name"] == "watch":
            watch_processes.append((proc.pid, proc.username()))

    for pid, user in watch_processes:
        cmd = []
        if user != getpass.getuser():
            cmd += [PATHS['sudo'], "-n", "-u", user]
        cmd += [PATHS['kill'], "-9", str(pid)]

        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if proc.returncode != 0:
            #            print("Cant kill proc")
            pass


def cancel_install(proc_info):
    """Calls the ansible playbook connector to kill running installs"""
    pid = proc_info.pid

    # Set Ansible playbook vars.
    ansible_vars = dict()
    ansible_vars["action"] = "cancel"
    ansible_vars["pid"] = pid
    write_ansible_vars_json(ansible_vars)

    run_cmd_popen(CONNECTOR_CMD, proc_info)


# Translates a username to a uid using pwd module.
def get_uid(username):
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
    if server.install_type == 'remote' or \
        (server.install_type == 'local' and server.username != USER):
        return True
    
    return False


def purge_tmux_socket_cache():
    """
    Deletes local cache of sock file names for installs. Used by setting page
    option. Useful for when game server has been re-installed to get status
    indicators working again.
    """
    socket_file_name_cache = os.path.join(CWD, 'json/tmux_socket_name_cache.json')
    if os.path.exists(socket_file_name_cache):
        os.remove(socket_file_name_cache)


def get_tmux_socket_name_docker(server, gs_id_file_path):
    """
    Gets tmux socket name for docker type installs by running commands through
    run_cmd_popen().

    Args:
        server (GameServer): Game Server to get tmux socket name for.
        gs_id_file_path (str): Path to gs_id file for game server.

    Returns:
        str: Returns the socket name for game server. None if can't get
             socket name.
    """
    proc_info = ProcInfoVessel()
    cmd = [PATHS['docker'], 'exec', server.script_name, PATHS['cat'], gs_id_file_path]

    run_cmd_popen(cmd, proc_info)

    if proc_info.exit_status > 0:
        current_app.logger.info(proc_info)
        return None

    gs_id = proc_info.stdout[0].strip()

    if len(gs_id) == 0:
        return None

    return server.script_name + "-" + gs_id


def get_tmux_socket_name_over_ssh(server, gs_id_file_path):
    """
    Uses SSH to get tmux socket name for remote and non-same user installs.

    Args:
        server (GameServer): Game Server to get tmux socket name for.
        gs_id_file_path (str): Path to gs_id file for game server.

    Returns:
        str: Returns the socket name for game server. None if can't get
             socket name.
    """
    proc_info = ProcInfoVessel()
    cmd = [PATHS['cat'], gs_id_file_path]
    keyfile = get_ssh_key_file(server.username, server.install_host)

    success = run_cmd_ssh(
        cmd,
        server.install_host,
        server.username,
        keyfile, 
        proc_info
    )

    # If the ssh connection itself fails return None.
    if not success:
        current_app.logger.info(proc_info)
        return None

    if proc_info.exit_status > 0:
        current_app.logger.info(proc_info)
        return None

    gs_id = proc_info.stdout[0].strip()

    if len(gs_id) == 0:
        return None

    return server.script_name + "-" + gs_id


def update_tmux_socket_name_cache(server_id, socket_name):
    """
    Writes to tmux socket name cache with fresh data.
    """
    cache_file = os.path.join(CWD, 'json/tmux_socket_name_cache.json')
    cache_data = dict()

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cache_data = json.load(file)

    cache_data[server_id] = socket_name

    with open(cache_file, 'w') as file:
        json.dump(cache_data, file)


def get_tmux_socket_name_from_cache(server, gs_id_file_path):
    """
    Get's the tmux socket name for remote, docker, and non-same user installs
    from the cache. If there is no cache file get socket for server and create
    cache. If the cache file is older than a week get socket name and update
    cache. Otherwise just pull the socket name value from the json cache.

    Args:
        server (GameServer): Game Server to get tmux socket name for.
        gs_id_file_path (str): Path to gs_id file for game server.

    Returns:
        str: Returns the socket name for game server. None if cant get
             one.
    """
    cache_file = os.path.join(CWD, 'json/tmux_socket_name_cache.json')

    if not os.path.exists(cache_file):
        if server.install_type == 'docker':
            socket_name = get_tmux_socket_name_docker(server, gs_id_file_path)
        else:
            socket_name = get_tmux_socket_name_over_ssh(server, gs_id_file_path)
        update_tmux_socket_name_cache(server.id, socket_name)
        return socket_name

    # Check if cache has expired.
    cache_mtime = os.path.getmtime(cache_file)

    # Convert the mtime to a datetime object.
    cache_time = datetime.fromtimestamp(cache_mtime)

    current_time = datetime.now()
    one_week_ago = current_time - timedelta(weeks=1)

    # Time comparisons always confuse me. With Epoch time, bigger number ==
    # more recent. Aka if the epoch time of one week ago is larger than the
    # epoch timestamp of cache file than the cache must be older than a week.
    if cache_time < one_week_ago:
        if server.install_type == 'docker':
            socket_name = get_tmux_socket_name_docker(server, gs_id_file_path)
        else:
            socket_name = get_tmux_socket_name_over_ssh(server, gs_id_file_path)

        update_tmux_socket_name_cache(server.id, socket_name)
        return socket_name

    with open(cache_file, 'r') as file:
        cache_data = json.load(file)

    if str(server.id) not in cache_data:
        if server.install_type == 'docker':
            socket_name = get_tmux_socket_name_docker(server, gs_id_file_path)
        else:
            socket_name = get_tmux_socket_name_over_ssh(server, gs_id_file_path)

        update_tmux_socket_name_cache(server.id, socket_name)
        return socket_name

    socket_name = cache_data[str(server.id)]
    return socket_name


def get_tmux_socket_name(server):
    """
    Get's the tmux socket file name for a given game server. Will call
    get_tmux_socket_name_from_cache() for remote, docker, & non-same user
    installs, otherwise will just read the gs_id value from the local file
    system to build the socket name.

    Args:
        server (GameServer): Game Server to get tmux socket name for.

    Returns:
        str: Returns the socket name for game server. None if can't get socket
             name.
    """
    gs_id_file_path = os.path.join(server.install_path, f"lgsm/data/{server.script_name}.uid")

    if should_use_ssh(server) or server.install_type == 'docker':
        return get_tmux_socket_name_from_cache(server, gs_id_file_path)

    if not os.path.isfile(gs_id_file_path):
        return None

    with open(gs_id_file_path, "r") as file:
        gs_id = file.read()

    return server.script_name + "-" + gs_id


def get_server_status(server):
    """
    Get's the game server status (on/off) for a specific game server. For
    install_type local same user, does so by running tmux cmd locally. For
    install_type remote and local not same user, fetches status by running tmux
    cmd over SSH. For install_type docker, uses docker cmd to fetch status.

    Args:
        server (GameServer): Game server object to check status of.
    Returns:
        bool|None: True if game server is active, False if inactive, None if
                   indeterminate.
    """
    proc_info = ProcInfoVessel()

    socket = get_tmux_socket_name(server)
    if socket == None:
        return None

    cmd = [PATHS['tmux'], "-L", socket, "list-session"]

    if should_use_ssh(server):
        gs_id_file_path = os.path.join(server.install_path, f"lgsm/data/{server.script_name}.uid")
        keyfile = get_ssh_key_file(server.username, server.install_host)
        success = run_cmd_ssh(
            cmd,
            server.install_host,
            server.username,
            keyfile, 
            proc_info
        )

        # If the ssh connection itself fails return None.
        if not success:
            current_app.logger.info(proc_info)
            return None

    elif server.install_type == 'docker':
        cmd = [PATHS['docker'], 'exec', server.script_name, PATHS['sudo'], '-u', server.username] + cmd
        run_cmd_popen(cmd, proc_info)

    # Else type local same user.
    else:
        run_cmd_popen(cmd, proc_info)

    current_app.logger.info(proc_info)
    if proc_info.exit_status > 0:
        return False

    return True


def get_all_server_statuses(all_game_servers):
    """
    Get's a list of game server statuses (on/off) for all installed game
    servers. Does so by wrapping get_server_status().

    Args:
        all_game_servers (list): List of all installed/added game servers.

    Returns:
        dict: Dictionary of game server names to status (on/off = True/False).
    """

    server_statuses = dict()

    for server in all_game_servers:
        # Initialize all servers False (aka inactive) to start with.
        server_statuses[server.install_name] = False
        server_statuses[server.install_name] = get_server_status(server)

    return server_statuses


def get_running_installs():
    threads = threading.enumerate()
    # Get all active threads.
    thread_names = []
    for thread in threads:
        if thread.is_alive() and thread.name.startswith("Install_"):
            thread_names.append(thread.name)

    return thread_names


def find_cfg_paths(server):
    """
    Finds a list of all valid cfg files for a given game server.

    Args:
        server (GameServer): Game server to find cfg files for.

    Returns:
        cfg_paths (list): List of found valid config files.
    """
    cfg_paths = []

    # Try except in case problem with json files.
    try:
        cfg_whitelist = open("json/accepted_cfgs.json", "r")
        json_data = json.load(cfg_whitelist)
        cfg_whitelist.close()
    except:
        return cfg_paths

    valid_gs_cfgs = json_data["accepted_cfgs"]

    if server.install_type == 'local':
        # Find all cfgs under install_path using os.walk.
        for root, dirs, files in os.walk(server.install_path):
            # Ignore default cfgs.
            if "config-default" in root:
                continue
            for file in files:
                if file in valid_gs_cfgs:
                    cfg_paths.append(os.path.join(root, file))

    if server.install_type == 'remote':
        proc_info = ProcInfoVessel()
        keyfile = get_ssh_key_file(server.username, server.install_host)
        wanted = []
        for cfg in valid_gs_cfgs:
            wanted += ['-name', cfg, '-o']
        cmd = [PATHS['find'], server.install_path, '-name', 'config-default', '-prune', '-type', 'f'] + wanted[:-1]

        success = run_cmd_ssh(
            cmd,
            server.install_host,
            server.username,
            keyfile, 
            proc_info
        )

        # If the ssh connection itself fails return False.
        if not success:
            current_app.logger.info(proc_info)
            flash("Problem connecting to remote host!", category="error")
            return cfg_paths

        if proc_info.exit_status > 0:
            current_app.logger.info(proc_info)
            flash("Problem running find cfg cmd. Check logs for more details.", category="error")
            return cfg_paths

        for item in proc_info.stdout:
            item = item.strip()
            current_app.logger.info(item)

            # Check str coming back is valid cfg name str.
            if os.path.basename(item) in valid_gs_cfgs:
                cfg_paths.append(item)

    return cfg_paths


def normalize_path(path):
    """
    Little helper function used to normalize supplied path in order to check if
    two path str's are equivalent.
    """
    # Remove extra slashes.
    path = re.sub(r'/{2,}', '/', path)

    # Remove trailing slash unless it's the root path "/".
    if path != '/' and path.endswith('/'):
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
    if not remove_files:
        server.delete()
        flash(f"Game server, {server.install_name} deleted!")
        return True

    if server.install_type == 'local':
        if server.username == USER:
            if os.path.isdir(server.install_path):
                shutil.rmtree(server.install_path)

        if delete_user and server.username != USER:
            cmd = CONNECTOR_CMD + ['--delete', str(server.id)]
            run_cmd_popen(cmd)

    if server.install_type == 'remote':
        if delete_user:
            flash(f"Warning: Cannot delete game server users for remote installs. Only removing files!")

        # Check to ensure is not a home directory before delete. Just some
        # idiot proofing, myself being the chief idiot.
        if normalize_path(f'/home/{server.username}') == normalize_path(server.install_path):
            flash("Will not delete remote users home directories!", category="error")
            return False

        proc_info = ProcInfoVessel()
        keyfile = get_ssh_key_file(server.username, server.install_host)
        cmd = ['rm', '-rf', server.install_path]

        success = run_cmd_ssh(
            cmd,
            server.install_host,
            server.username,
            keyfile, 
            proc_info
        )

        # If the ssh connection itself fails return False.
        if not success:
            current_app.logger.info(proc_info)
            flash("Problem connecting to remote host!", category="error")
            return False

        if proc_info.exit_status > 0:
            current_app.logger.info(proc_info)
            flash("Delete command failed! Check logs for more info.", category="error")
            return False

    flash(f"Game server, {server.install_name} deleted!")
    server.delete()
    return True


# Validates submitted cfg_file for edit route.
def valid_cfg_name(cfg_file):
    gs_cfgs = open("json/accepted_cfgs.json", "r")
    json_data = json.load(gs_cfgs)
    gs_cfgs.close()

    valid_gs_cfgs = json_data["accepted_cfgs"]

    for cfg in valid_gs_cfgs:
        if cfg_file == cfg:
            return True

    return False


def get_commands(server, send_cmd, current_user):
    """
    Turns data in commands.json into list of command objects that implement the
    CmdDescriptor class. This list of commands is used to validate user input
    and populate the buttons on the controls page.

    Args:
        server (string): Name of game server to get commands for.
        send_cmd (bool): Whether or not send cmd button is enabled.
        current_user (object): Currently logged in flask user object.
    """
    commands = []

    with open("json/commands.json", "r") as commands_json:
        json_data = json.load(commands_json)

    with open("json/ctrl_exemptions.json", "r") as exemptions_json:
        exemptions_data = json.load(exemptions_json)

    # Remove send cmd if option disabled in main.conf.
    if send_cmd == False:
        json_data["short_cmds"].remove("sd")
        json_data["long_cmds"].remove("send")
        json_data["descriptions"].remove("Send command to game server console.")

    # Remove exempted cmds.
    if server in exemptions_data:
        for short_cmd in exemptions_data[server]["short_cmds"]:
            json_data["short_cmds"].remove(short_cmd)
        for long_cmd in exemptions_data[server]["long_cmds"]:
            json_data["long_cmds"].remove(long_cmd)
        for desc in exemptions_data[server]["descriptions"]:
            json_data["descriptions"].remove(desc)

    cmds = zip(
        json_data["short_cmds"], json_data["long_cmds"], json_data["descriptions"]
    )

    # Remove commands for non-admin users. Part of permissions controls.
    user_perms = json.loads(current_user.permissions)

    for short_cmd, long_cmd, description in cmds:
        if current_user.role != "admin":
            if long_cmd not in user_perms["controls"]:
                continue

        cmd = CmdDescriptor()
        cmd.long_cmd = long_cmd
        cmd.short_cmd = short_cmd
        cmd.description = description
        commands.append(cmd)

    return commands


# Turns data in games_servers.json into servers list for install route.
def get_servers():
    # Try except in case problem with json files.
    try:
        with open("json/game_servers.json", "r") as file:
            json_data = json.load(file)

        return dict(zip(json_data["servers"], json_data["server_names"]))
    except:
        # Return empty dict triggers error. In python empty dict == False.
        return {}


# Validates short commands.
def valid_command(cmd, server, send_cmd, current_user):
    commands = get_commands(server, send_cmd, current_user)
    for command in commands:
        # Aka is valid command.
        if cmd == command.short_cmd:
            return True

    return False


## Install Page Utils.


# Validates form submitted server_script_name and server_full_name options.
def valid_install_options(script_name, full_name):
    servers = get_servers()
    for server, server_name in servers.items():
        if server == script_name and server_name == full_name:
            return True
    return False


# Validates script_name.
def valid_script_name(script_name):
    servers = get_servers()
    for server, server_name in servers.items():
        if server == script_name:
            return True
    return False


# Validates server_name.
def valid_server_name(server_name):
    servers = get_servers()
    for server, s_name in servers.items():
        # Convert s_name to a unix friendly directory name.
        s_name = s_name.replace(" ", "_")
        s_name = s_name.replace(":", "")

        if s_name == server_name:
            return True
    return False


# Checks if linuxgsm.sh already exists and if not, gets it.
def check_and_get_lgsmsh(lgsmsh):
    if not os.path.isfile(lgsmsh):
        get_lgsmsh(lgsmsh)
        return

    three_weeks_in_seconds = 1814400
    if int(time.time() - os.path.getmtime(lgsmsh)) > three_weeks_in_seconds:
        get_lgsmsh(lgsmsh)


# Wget's newest lgsm script.
def get_lgsmsh(lgsmsh):
    # Pretend to be wget to fetch linuxgsm.sh.
    try:
        headers = {"User-Agent": "Wget/1.20.3 (linux-gnu)"}
        response = requests.get("https://linuxgsm.sh", headers=headers)
        with open(lgsmsh, "wb") as f:
            f.write(response.content)
        os.chmod(lgsmsh, 0o755)
    except Exception as e:
        # For debug.
        print(e)
    print("Got linuxgsm.sh!")


# Checks for the presense of bad chars in input.
def contains_bad_chars(i):
    bad_chars = {
        " ",
        "$",
        "'",
        '"',
        "\\",
        "#",
        "=",
        "[",
        "]",
        "!",
        "<",
        ">",
        "|",
        ";",
        "{",
        "}",
        "(",
        ")",
        "*",
        ",",
        "?",
        "~",
        "&",
    }
    if i is None:
        return False

    for char in bad_chars:
        if char in i:
            return True

    return False


# Run's self update script.
# TODO: Rewrite this to use run_cmd_popen.
def update_self():
    update_cmd = ["./web-lgsm.py", "--auto"]
    proc = subprocess.run(
        update_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    if proc.returncode != 0:
        return f"Error: {proc.stderr}"

    if "up to date" in proc.stdout:
        return "Already up to date!"

    if "Update Required" in proc.stdout:
        return "Web LGSM Upgraded! Restarting momentarily..."


# Sleep's 5 seconds then restarts the app.
# TODO: Rewrite this to use run_cmd_popen.
def restart_self(restart_cmd):
    time.sleep(5)
    proc = subprocess.run(
        restart_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )


# Gets bytes in/out per second. Stores last value in global.
def get_network_stats():
    global prev_bytes_sent, prev_bytes_recv, prev_time

    # Get current counters and timestamp.
    net_io = psutil.net_io_counters()
    current_bytes_sent = net_io.bytes_sent
    current_bytes_recv = net_io.bytes_recv
    current_time = time.time()

    # Calculate the rate of bytes sent and received per second.
    bytes_sent_rate = (current_bytes_sent - prev_bytes_sent) / (
        current_time - prev_time
    )
    bytes_recv_rate = (current_bytes_recv - prev_bytes_recv) / (
        current_time - prev_time
    )

    # Update previous counters and timestamp.
    prev_bytes_sent = current_bytes_sent
    prev_bytes_recv = current_bytes_recv
    prev_time = current_time

    return {"bytes_sent_rate": bytes_sent_rate, "bytes_recv_rate": bytes_recv_rate}


# Returns disk, cpu, mem, and network stats. Later turned into json for home
# page resource usage charts.
def get_server_stats():
    stats = dict()

    # Disk
    total, used, free = shutil.disk_usage("/")
    # Add ~4% for ext4 filesystem metadata usage.
    percent_used = (((total * 0.04) + used) / total) * 100
    stats["disk"] = {
        "total": total,
        "used": used,
        "free": free,
        "percent_used": percent_used,
    }

    # CPU
    load1, load5, load15 = psutil.getloadavg()
    cpu_usage = (load1 / os.cpu_count()) * 100
    stats["cpu"] = {
        "load1": load1,
        "load5": load5,
        "load15": load15,
        "cpu_usage": cpu_usage,
    }

    # Mem
    mem = psutil.virtual_memory()
    # Total, used, available, percent_used.
    stats["mem"] = {
        "total": mem[0],
        "used": mem[3],
        "free": mem[1],
        "percent_used": mem[2],
    }

    # Network
    stats["network"] = get_network_stats()

    return stats


def get_verbosity(verbostiy):
    """Tries to cast config verbosity to int. Also checks if below three."""
    try:
        v = int(verbostiy)
    except ValueError as verr:
        v = 1
    except Exception as ex:
        v = 1

    # Only allow levels 1-3.
    if v > 3:
        v = 1

    return v


def user_has_permissions(current_user, route, server_name=None):
    """
    Check's if current user has permissions to various routes.

    Args:
        current_user (object): The currently logged in user object.
        route (string): The route to apply permissions controls to.
        server_name (string): Game server name to check user has access to.
                              Only matters for controls & delete routes.

    Returns:
        bool: True if user has appropriate perms, False otherwise.

    """
    # Admins can always do anything.
    if current_user.role == "admin":
        return True

    user_perms = json.loads(current_user.permissions)

    if route == "install":
        if not user_perms["install_servers"]:
            flash(
                "Your user does NOT have permission access the install page!",
                category="error",
            )
            return False

    if route == "add":
        if not user_perms["add_servers"]:
            flash(
                "Your user does NOT have permission access the add page!",
                category="error",
            )
            return False

    if route == "delete":
        if not user_perms["delete_server"]:
            flash(
                "Your user does NOT have permission to delete servers!",
                category="error",
            )
            return False

        if server_name not in user_perms["servers"]:
            flash(
                "Your user does NOT have permission to delete this game server!",
                category="error",
            )
            return False

    if route == "settings":
        if not user_perms["mod_settings"]:
            flash(
                "Your user does NOT have permission access the settings page!",
                category="error",
            )
            return False

    if route == "controls":
        if server_name not in user_perms["servers"]:
            flash(
                "Your user does NOT have permission access this game server!",
                category="error",
            )
            return False

    return True


def local_install_path_exists(server):
    """
    Check's that the game server install_path exists for install_type local
    same user, everything else return true.

    Args:
        server (GameServer): Game server to check.
    Returns:
        bool: True if path exists, False otherwise.
    """
    if server.install_type == 'local' and server.username == USER:
        if os.path.isdir(server.install_path):
            return True

        return False

    return True


def valid_install_type(install_type):
    """
    Check's install type is one of the allowed three types.

    Args:
        install_type (str): User supplied install_type

    Returns:
        bool: True if valid install_type, False otherwise.
    """
    valid_install_types = ['local', 'remote', 'docker']

    if install_type in valid_install_types:
        return True

    return False


def is_ssh_accessible(hostname):
    """
    Checks if a hostname/IP has an accessible SSH server on port 22.

    Args:
        hostname (str): The hostname or IP address to check.
    Returns:
        bool: True if SSH is accessible, False otherwise.
    """
    port=22
    timeout=5

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


def generate_ecdsa_ssh_keypair(key_name):
    """
    Wraps the ssh-keygen shell util to generate a 256 bit ecdsa ssh key.

    Args:
        key_name (str): Name of key files to be generated.
    Returns:
        bool: True if key files created successfully, False otherwise.
    """
    key_path = os.path.expanduser(f"~/.ssh/{key_name}")
    key_size = 256

    # Build ssh-keygen command.
    cmd = [
        PATHS['ssh-keygen'],
        "-t", "ecdsa",
        "-b", str(key_size),
        "-f", key_path,
        "-N", ""
    ]

    proc_info = ProcInfoVessel()
    run_cmd_popen(cmd, proc_info)
    if proc_info.exit_status > 0:
        return False

    return True


def get_ssh_key_file(user, host):
    """
    Fetches ssh private key file for user:host from ~/.ssh. If user:host key
    does not exist yet, it creates one.

    Args:
        user (str): Username of remote user.
        host (str): Hostname of remote server.
    Returns:
        str: Path to public ssh key file for user:host.
    """
    home_dir = os.path.expanduser("~")
    ssh_dir = os.path.join(home_dir, ".ssh")
    all_pub_keys = [f for f in os.listdir(ssh_dir) if f.endswith('.pub')]

    key_name = f"id_ecdsa_{user}_{host}"

    # If no key files for user@server yet, create new one.
    if key_name + '.pub' not in all_pub_keys:
        # Log keygen failures.
        if not generate_ecdsa_ssh_keypair(key_name):
            log_msg = f"Failed to generate new key pair for {user}:{server}!"
            current_app.logger.info(log_msg)
            return
    
    keyfile = os.path.join(ssh_dir, key_name)
    return keyfile


# TODO: Finish this!
def gen_ssh_rule(pub_key):
    """
    Creates an ssh rule for a specified key.

    Args:
        pub_key (str): Public key to use to generate rule.
    Returns:
        ssh_rule (str): Ssh rule string. 
    """
    return f'{pub_key} command="/path/to/ssh_connector.sh"'

    # TODO: Finish this.


def run_cmd_ssh(cmd, hostname, username, key_filename, proc_info=ProcInfoVessel(), app_context=False, timeout=5.0):
    """
    Runs remote commands over ssh to admin game servers.

    Args:
        cmd (list): Command to run over SSH.
        hostname (str): The hostname or IP address of the server.
        username (str): The username to use for the SSH connection.
        key_filename (str): The path to the private key file.
        proc_info (ProcInfoVessel): Optional ProcInfoVessel object to capture
                                    process information in a thread.
        app_context (AppContext): Optional Current app context needed for
                                  logging in a thread.
        timeout (float): Timeout in seconds for ssh command. None = no timeout.
    Returns:
        bool: True if command runs successfully, False otherwise.
    """
    config = configparser.ConfigParser()
    config.read("main.conf")
    end_in_newlines = get_config_value(config, "settings", "end_in_newlines", True, True)
    clear_output_on_reload = get_config_value(config, "settings", "clear_output_on_reload", True, True)

    if clear_output_on_reload:
        proc_info.stdout.clear()
        proc_info.stderr.clear()

    # App context needed for logging in threads.
    if app_context:
        app_context.push()

    safe_cmd = shlex.join(cmd)

    # Log info.
    current_app.logger.info(cmd)
    current_app.logger.info(safe_cmd)
    current_app.logger.info(hostname)
    current_app.logger.info(username)
    current_app.logger.info(key_filename)
    current_app.logger.info('pre stdout: ' + str(proc_info.stdout))
    current_app.logger.info('pre stderr: ' + str(proc_info.stderr))
    
    # Initialize SSH client.
    client = paramiko.SSHClient()
    # Automatically add the host key.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, key_filename=key_filename, timeout=3)
        current_app.logger.debug(cmd)

        proc_info.process_lock = True
        # Open a new session and request a PTY.
        channel = client.get_transport().open_session()
#        channel.get_pty()  # This shut's off the stderr stream for some reason... Not sure if pty still needed.
        channel.set_combine_stderr(False)
        channel.exec_command(safe_cmd)

        # Optionally set timeout (if provided).
        if timeout:
            channel.settimeout(timeout)

        while True:
            # Read stdout if data is available.
            if channel.recv_ready():
                stdout_chunk = channel.recv(8192).decode('utf-8')
                stdout_lines = stdout_chunk.splitlines(keepends=True)
                for line in stdout_lines:
                    if line == '\r\n':
                        continue
                    if line not in proc_info.stdout:
                        if end_in_newlines and not (line.endswith('\n') or line.endswith('\r')):
                            line += '\n'
                        proc_info.stdout.append(line)
                        log_msg = log_wrap('stdout', line.strip())
                        current_app.logger.debug(log_msg)

            if channel.recv_stderr_ready():
                stderr_chunk = channel.recv_stderr(8192).decode('utf-8')
                stderr_lines = stderr_chunk.splitlines(keepends=True)
                for line in stderr_lines:
                    if line == '\r\n':
                        continue
                    if line not in proc_info.stderr:
                        if end_in_newlines and not (line.endswith('\n') or line.endswith('\r')):
                            line += '\n'
                        proc_info.stderr.append(line)
                        log_msg = log_wrap('stderr', line.strip())
                        current_app.logger.debug(log_msg)

            # Break the loop if the command has finished.
            if channel.exit_status_ready():
                # Ensure any remaining stderr and stdout are captured.
                while channel.recv_stderr_ready():
                    stderr_chunk = channel.recv_stderr(8192).decode('utf-8')
                    proc_info.stderr.append(stderr_chunk)

                while channel.recv_ready():
                    stdout_chunk = channel.recv(8192).decode('utf-8')
                    proc_info.stdout.append(stdout_chunk)

                break

            # Keep CPU from burning.
            time.sleep(0.1)

        # Wait for the command to finish and get the exit status.
        proc_info.exit_status = channel.recv_exit_status()
        proc_info.process_lock = False
        ret_status = True 

    except paramiko.SSHException as e:
        current_app.logger.debug(str(e))
        proc_info.stderr.append(str(e))
        proc_info.exit_status = 5
        proc_info.process_lock = False
        ret_status = False

    except TimeoutError as e:
        current_app.logger.debug(str(e))
        proc_info.stderr.append(str(e))
        proc_info.exit_status = 7
        proc_info.process_lock = False
        ret_status = False

    finally:
        client.close()
        return ret_status

    
def read_file_over_ssh(server, file_path):
    """
    Reads a file from a remote server over SSH and returns its content. Used
    for updating config files for remote installs. However, its been built as a
    general purpose read file over ssh using paramiko sftp.

    Args:
        server (GameServer): Server to get file for.
        file_path: The path of the file to read on the remote machine.

    Returns:
        str: Returns the contents of the file as a string.
    """
    current_app.logger.info(log_wrap('file_path', file_path))
    pub_key_file = get_ssh_key_file(server.username, server.install_host)

    try:
        # Open ssh client conn.
        with paramiko.SSHClient() as ssh:
            # Automatically add the host key.
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server.install_host, username=server.username, key_filename=pub_key_file, timeout=3)

            # Open sftp session.
            with ssh.open_sftp() as sftp:
                # Open file over sftp.
                with sftp.open(file_path, "r") as file:
                    content = file.read()

            return content.decode()

    except Exception as e:
        current_app.logger.debug(e) 
        return None


def write_file_over_ssh(server, file_path, content):
    """
    Writes a string to a file on a remote server over SSH. Similarly to
    read_file_over_ssh(), this function is used to update cfg files for remote
    game servers. However, it is written as a general purpose write over ssh
    using paramiko sftp.

    Parameters:
        server (GameServer): Game Server to write the cfg file changes for.
        file_path (str): The path of the file to write on the remote server.
        content (str): The string content to write to the file.

    Returns:
        Bool: True if the write was successful, False otherwise.
    """
    current_app.logger.info(log_wrap('file_path', file_path))
    pub_key_file = get_ssh_key_file(server.username, server.install_host)

    try:
        with paramiko.SSHClient() as ssh:
            # Automatically add the host key.
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server.install_host, username=server.username, key_filename=pub_key_file, timeout=3)

            with ssh.open_sftp() as sftp:
                with sftp.open(file_path, "w") as file:
                    file.write(content)
        
        return True

    except Exception as e:
        current_app.logger.debug(e) 
        return False


def get_config_value(config, section, option, default, is_bool=False):
    """
    Wraps checking config object for option. If no config option found return
    default value.

    Args:
        config (ConfigParser): Config object to read & get options from.
        section (str): Section of config to fetch option from.
        option (str): The option to fetch value of.
        default (str): Default value if can't find option in config.
        is_bool (bool): Option type is a boolean (different option fetch method).

    Returns:
        str|bool: Value of configured option in config or default value if
                  can't one get from config.
    """
    try:
        if config and config.has_section(section):
            if is_bool:
                return config[section].getboolean(option)

            return config[section][option]

        else: 
            return default

    except (ValueError, IndexError, KeyError) as e:
        return default

    except configparser.NoOptionError:
        return default



def read_config(route):
    """
    Reads in relevant main config parameters for a given route. Also protects
    against empty config options.

    Args:
        route (str): Name of route to fetch config parameters for.
    Returns:
        config_options (dict): Configuration options for route.
    """
    # Import config data.
    config = configparser.ConfigParser()
    config.read("main.conf")

    config_options = dict() 

    if route == 'home':
        config_options["text_color"] = get_config_value(config, "aesthetic", "text_color", "#09ff00")
        config_options["graphs_primary"] = get_config_value(config, "aesthetic", "graphs_primary", "#e01b24")
        config_options["graphs_secondary"] = get_config_value(config, "aesthetic", "graphs_secondary", "#0d6efd")
        config_options["show_stats"] = get_config_value(config, "aesthetic", "show_stats", True, True)
        config_options["show_barrel_roll"] = get_config_value(config, "aesthetic", "show_barrel_roll", True, True)
        return config_options

    if route == 'controls':
        config_options["text_color"] = get_config_value(config, "aesthetic", "text_color", "#09ff00")
        config_options["terminal_height"] = get_config_value(config, "aesthetic", "terminal_height", 10)
        config_options["cfg_editor"] = get_config_value(config, "settings", "cfg_editor", False, True)
        config_options["send_cmd"] = get_config_value(config, "settings", "send_cmd", False, True)
        config_options["show_stderr"] = get_config_value(config, "settings", "show_stderr", True, True)
        return config_options











