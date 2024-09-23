import os
import re
import sys
import pwd
import json
import glob
import time
import string
import logging
import psutil
import shutil
import getpass
import requests
import subprocess
import threading
from datetime import datetime
from threading import Thread
from . import db
from .models import GameServer
from flask import flash, current_app

# Constants.
CWD = os.getcwd()
USER = getpass.getuser()
ANSIBLE_CONNECTOR = os.path.join(CWD, "playbooks/sudo_ansible_connector.py")

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

        # Check input lengths.
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


class ProcInfoVessel:
    """
    Class used to create objects that hold information about processes launched
    via the subprocess Popen wrapper.
    """
    def __init__(self):
        """
        Args:
            stdout (list): Lines of stdout delivered by subprocess.Popen call.
            stderr (list): Lines of stderr delivered by subprocess.Popen call.
            process_lock (bool): Acts as lock to tell if process is still 
                                 running and output is being appended.
            pid (int): Process id.
            exit_status (int): Exit status of cmd in Popen call.
        """
        self.stdout = []
        self.stderr = []
        self.process_lock = None
        self.pid = None
        self.exit_status = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __str__(self):
        return f"ProcInfoVessel(stdout='{self.stdout}', stderr='{self.stderr}', process_lock='{self.process_lock}', pid='{self.pid}', exit_status='{self.exit_status}')"

    def __repr__(self):
        return f"ProcInfoVessel(stdout='{self.stdout}', stderr='{self.stderr}', process_lock='{self.process_lock}', pid='{self.pid}', exit_status='{self.exit_status}')"


def run_cmd_popen(cmd, proc_info=ProcInfoVessel(), app_context=False):
    """
    General purpose subprocess.Popen wrapper function.

    Args:
        cmd (list): Command to be run via subprocess.Popen.
        proc_info (obj): Optional object to store info about running process.
    """
    # Clear any previous output.
    proc_info.stdout.clear()
    proc_info.stderr.clear()

    # Set lock flag to true.
    proc_info.process_lock = True

    # App context needed for logging in threads.
    if app_context:
        app_context.push()

    current_app.logger.info(log_wrap('cmd', cmd))
    
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    
    proc_info.pid = proc.pid
    
    for stdout_line in iter(proc.stdout.readline, ""):
        proc_info.stdout.append(stdout_line)
        log_msg = log_wrap('stdout', stdout_line.replace('\n', ''))
        current_app.logger.debug(log_msg)
    
    for stderr_line in iter(proc.stderr.readline, ""):
        proc_info.stderr.append(stderr_line)
        log_msg = log_wrap('stderr', stderr_line.replace('\n', ''))
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
            cmd += ["/usr/bin/sudo", "-n", "-u", user]
        cmd += ["/usr/bin/kill", "-9", str(pid)]

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

    cmd = [
        "/usr/bin/sudo", "-n", 
        os.path.join(CWD, "venv/bin/python"),
        ANSIBLE_CONNECTOR
    ]
    run_cmd_popen(cmd, proc_info)


# Translates a username to a uid using pwd module.
def get_uid(username):
    try:
        user_info = pwd.getpwnam(username)
        return user_info.pw_uid
    except KeyError:
        return None


def get_server_statuses():
    """
    Uses sudo connector script to get list of active game servers.

    Returns:
        dict: Returns server_status dictionary with mapping of server name to
              active / inactive.
    """

    # Set Ansible playbook vars.
    ansible_vars = dict()
    ansible_vars["action"] = "statuses"
    write_ansible_vars_json(ansible_vars)

    cmd = [
        "/usr/bin/sudo",
        "-n",
        os.path.join(CWD, "venv/bin/python"),
        ANSIBLE_CONNECTOR
    ]
    proc_info = ProcInfoVessel()
    run_cmd_popen(cmd, proc_info)

    if proc_info.exit_status != 0:
        return dict()

    server_statuses = dict()
    for line in proc_info.stdout:
        line = line.replace('\n', '')
        server_status = json.loads(line)
        server_statuses.update(server_status)

    return server_statuses


def get_sockets():
    """
    Gets a dictionary mapping of game servers to tmux socket files via sudo
    connector script.

    Returns:
        servers_to_tmux_sockets (dict): List of socket files.
    """
    servers_to_tmux_sockets = dict()

    # Set sudo connector vars.
    ansible_vars = dict()
    ansible_vars["action"] = "tmuxsocks"
    write_ansible_vars_json(ansible_vars)

    cmd = [
        "/usr/bin/sudo",
        "-n",
        os.path.join(CWD, "venv/bin/python"),
        ANSIBLE_CONNECTOR
    ]
    proc_info = ProcInfoVessel()
    run_cmd_popen(cmd, proc_info)

    if proc_info.exit_status != 0:
        return dict()

    for line in proc_info.stdout:
        line = line.replace('\n', '')
        server_2_sock = json.loads(line)
        servers_to_tmux_sockets.update(server_2_sock)

    return servers_to_tmux_sockets 


def get_running_installs():
    threads = threading.enumerate()
    # Get all active threads.
    thread_names = []
    for thread in threads:
        if thread.is_alive() and thread.name.startswith("Install_"):
            thread_names.append(thread.name)

    return thread_names


# Returns list of any game server cfg listed in accepted_cfgs.json under the
# search_path.
def find_cfg_paths(search_path):
    # Try except in case problem with json files.
    try:
        cfg_whitelist = open("json/accepted_cfgs.json", "r")
        json_data = json.load(cfg_whitelist)
        cfg_whitelist.close()
    except:
        return "failed"

    cfg_paths = []
    valid_gs_cfgs = json_data["accepted_cfgs"]

    # Find all cfgs under search_path using os.walk.
    for root, dirs, files in os.walk(search_path):
        # Ignore default cfgs.
        if "config-default" in root:
            continue
        for file in files:
            if file in valid_gs_cfgs:
                cfg_paths.append(os.path.join(root, file))

    return cfg_paths


# Does the actual deletions for the /delete route.
def del_server(server, remove_files):
    install_path = server.install_path
    server_name = server.install_name
    username = server.username

    GameServer.query.filter_by(install_name=server_name).delete()
    db.session.commit()

    if not remove_files:
        flash(f"Game server, {server_name} deleted!")
        return

    web_lgsm_user = getpass.getuser()

    if username == web_lgsm_user:
        if os.path.isdir(install_path):
            shutil.rmtree(install_path)
    else:
        sudo_rule_name = f"{web_lgsm_user}-{username}"
        # Set Ansible playbook vars.
        ansible_vars = dict()
        ansible_vars["action"] = "delete"
        ansible_vars["gs_user"] = username
        ansible_vars["sudo_rule_name"] = sudo_rule_name
        write_ansible_vars_json(ansible_vars)

        cmd = [
            "/usr/bin/sudo",
            "-n",
            os.path.join(CWD, "venv/bin/python"),
            ANSIBLE_CONNECTOR
        ]
        run_cmd_popen(cmd)

    flash(f"Game server, {server_name} deleted!")
    return


def write_ansible_vars_json(ansible_vars):
    ansible_vars_json_file = os.path.join(CWD, "json/ansible_vars.json")
    # Write json to file.
    with open(ansible_vars_json_file, "w") as json_file:
        json.dump(ansible_vars, json_file, indent=4)


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

    class CmdDescriptor:
        def __init__(self):
            self.long_cmd = ""
            self.short_cmd = ""
            self.description = ""

        def __str__(self):
            return f"CmdDescriptor(long_cmd='{self.long_cmd}', short_cmd='{self.short_cmd}', description='{self.description}')"

        def __repr__(self):
            return f"CmdDescriptor(long_cmd='{self.long_cmd}', short_cmd='{self.short_cmd}', description='{self.description}')"

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
        print(command.short_cmd)
        print(command.long_cmd)
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


# Returns a string comma separated game server script paths for a given user.
def get_user_script_paths(install_path, script_name):
    paths_query_result = (
        GameServer.query.filter_by(username=script_name)
        .with_entities(GameServer.install_path)
        .all()
    )
    game_server_paths = [path[0] for path in paths_query_result]
    user_script_paths = os.path.join(install_path, script_name)

    # Add any other game server paths for gs_user.
    for path in game_server_paths:
        user_script_paths += f",{path}"

    return user_script_paths


# Run's self update script.
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


def install_path_exists(install_path):
    """
    Check's that the install_path exists via connector.

    Args:
        install_path (str): Installation path to check.

    Returns:
        bool: True if path exists, False otherwise.
    """
    # Set sudo connector vars.
    ansible_vars = dict()
    ansible_vars["action"] = "checkdir"
    ansible_vars["install_path"] = install_path
    write_ansible_vars_json(ansible_vars)

    proc_info = ProcInfoVessel()
    cmd = [
        "/usr/bin/sudo", "-n", 
        os.path.join(CWD, "venv/bin/python"),
        ANSIBLE_CONNECTOR
    ]
    run_cmd_popen(cmd, proc_info)
    for line in proc_info.stdout:
        if "Path exists" in line:
            return True

    print(proc_info.stdout)

    return False
