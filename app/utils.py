import os
import re
import sys
import json
import time
import shutil
import psutil
import requests
import subprocess
from . import db
from .models import GameServer
from flask import flash

# Holds the output from a running daemon thread.
class OutputContainer:
    def __init__(self, output_lines, process_lock):
        # Lines of output delievered by running daemon threat.
        self.output_lines = output_lines
        # Boolean to act as a lock and tell if process is already running and
        # output is being appended.
        self.process_lock = process_lock

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


# Kindly does the RCE.
def shell_exec(exec_dir, cmds, output):
    # Clear any previous output.
    output.output_lines.clear()

    # Set lock flag to true.
    output.process_lock = True

    proc = subprocess.Popen(cmds,
            cwd=exec_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
    )

    for stdout_line in iter(proc.stdout.readline, ""):
        output.output_lines.append(escape_ansi(stdout_line))

    for stderr_line in iter(proc.stderr.readline, ""):
        output.output_lines.append(escape_ansi(stderr_line))

    # Reset process_lock flag.
    output.process_lock = False


# Snips any lingering `watch` processes.
def kill_watchers(last_request_for_output):
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

    app_proc = psutil.Process(os.getpid())
    for child in app_proc.children(recursive=True):
        if child.name() == "watch":
            child.kill()


# Get's the list of servers that are currently turnned on.
def get_active_servers(all_game_servers):
    # List all tmux sessions for the given user by looking at /tmp/tmux-UID.
    active_servers = {}
    uid = os.getuid()
    user_tmux_sockets = os.listdir(f"/tmp/tmux-{uid}")
    for server in all_game_servers:
        for socket in user_tmux_sockets:
            if server.script_name in socket:
                cmd = ['/usr/bin/tmux', '-L', socket, 'list-session']
                proc = subprocess.run(cmd,
                        stdout = subprocess.DEVNULL,
                        stderr = subprocess.DEVNULL)

                active_servers[server.install_name] = 'inactive'

                if proc.returncode == 0:
                    active_servers[server.install_name] = 'active'

    return active_servers


# Get socket file for given game server. (Have yet to consider case of two
# installs of the same game server. Am lazy, will address that l8tr.)
def get_socket_for_gs(server):
    uid = os.getuid()
    user_tmux_sockets = os.listdir(f"/tmp/tmux-{uid}")
    for socket in user_tmux_sockets:
        if server in socket:
            return socket


# Returns list of any game server cfg listed in accepted_cfgs.json under the
# search_path.
def find_cfg_paths(search_path):
    # Try except in case problem with json files.
    try:
        cfg_whitelist = open('json/accepted_cfgs.json', 'r')
        json_data = json.load(cfg_whitelist)
        cfg_whitelist.close()
    except:
        return "failed"

    cfg_paths = []
    valid_gs_cfgs = json_data["accepted_cfgs"]

    # Find all cfgs under search_path using os.walk.
    for root, dirs, files in os.walk(search_path):
        # Ignore default cfgs.
        if 'config-default' in root:
            continue
        for file in files:
            if file in valid_gs_cfgs:
                cfg_paths.append(os.path.join(root, file))

    return cfg_paths

# Does the actual deletions for the /delete route.
def del_server(server, remove_files):
    install_path = server.install_path
    server_name = server.install_name

    GameServer.query.filter_by(install_name=server_name).delete()
    db.session.commit()

    if remove_files:
        if os.path.isdir(install_path):
            shutil.rmtree(install_path)

    flash(f'Game server, {server_name} deleted!')
    return


# Uses sudo_pass to get sudo tty ticket.
def get_tty_ticket(sudo_pass):
    # Attempt's to get sudo tty ticket. Uses try, except becaue subprocess.run
    # is called with check=True which causes any subproc failures to throw an
    # exception. This uses that password fail exception to return False.
    try:
        subprocess.run(['/usr/bin/sudo', '-S', 'apt-get', 'check'],
                       check=True,
                       input=sudo_pass,
                       stderr=subprocess.PIPE,
                       universal_newlines=True)
        return True
    except subprocess.CalledProcessError as e:
        return False


# Validates submitted cfg_file for edit route.
def is_invalid_cfg_name(cfg_file):
    gs_cfgs = open('json/accepted_cfgs.json', 'r')
    json_data = json.load(gs_cfgs)
    gs_cfgs.close()
    
    valid_gs_cfgs = json_data["accepted_cfgs"]

    for cfg in valid_gs_cfgs:
        if cfg_file == cfg:
            return False

    return True
    

# Turns data in commands.json into list of command objects that implement the
# CmdDescriptor class.
def get_commands():
    commands = []

    # Try except in case problem with json files.
    try:
        commands_json = open('json/commands.json', 'r')
        json_data = json.load(commands_json)
        commands_json.close()
    except:
        return commands

    cmds = zip(json_data["short_cmds"], json_data["long_cmds"], \
        json_data["descriptions"])

    class CmdDescriptor:
        def __init__(self):
            self.long_cmd  = ""
            self.short_cmd = ""
            self.description = ""

    for short_cmd, long_cmd, description in cmds:
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
        servers_json = open('json/game_servers.json', 'r')
        json_data = json.load(servers_json)
        servers_json.close()
        return dict(zip(json_data['servers'], json_data['server_names']))
    except:
        # Return empty dict triggers error. In python empty dict == False.
        return {}


# Validates short commands.
def is_invalid_command(cmd):
    commands = get_commands()
    for command in commands:
        # If cmd is in list of short_cmds return False.
        # Aka is not invalid command.
        if cmd == command.short_cmd:
            return False

    return True


# Validates form submitted server_script_name and server_full_name options.
def install_options_are_invalid(script_name, full_name):
    servers = get_servers()
    for server, server_name in servers.items():
        if server == script_name and server_name == full_name:
            return False
    return True


# Validates script_name.
def script_name_is_invalid(script_name):
    servers = get_servers()
    for server, server_name in servers.items():
        if server == script_name:
            return False
    return True


# Checks if linuxgsm.sh already exists and if not, wgets it.
def check_and_wget_lgsmsh(lgsmsh):
    if not os.path.isfile(lgsmsh):
        # Temporary solution. Tried using requests for download, didn't work.
        try:
            out = os.popen(f"/usr/bin/wget -O {lgsmsh} https://linuxgsm.sh").read()
            os.chmod(lgsmsh, 0o755)
        except:
            # For debug.
            print(sys.exc_info()[0])


# Removes color codes from cmd line output.
def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)


# Checks for the presense of bad chars in input.
def contains_bad_chars(i):
    bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                  "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }
    if i is None:
        return False

    for char in bad_chars:
        if char in i:
            return True

