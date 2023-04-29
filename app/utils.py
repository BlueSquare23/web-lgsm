import os
import re
import sys
import json
import shutil
import psutil
import requests
import subprocess
from . import db
from .models import GameServer
from flask import flash

# Holds the output from a running daemon thread.
class OutputContainer:
    def __init__(self, output_lines, process_lock, just_finished):
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
            shell=True,
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
    output.just_finished = True


# Snips any lingering `watch` processes.
def kill_watchers():
    app_proc = psutil.Process(os.getpid())
    for child in app_proc.children(recursive=True):
        if child.name() == "watch":
            child.kill()


# Get's the list of servers that are currently turnned on.
def get_active_servers(all_game_servers):
    # Initialize active_servers dict as all inactive to begin with.
    active_servers = {}
    for server in all_game_servers:
        active_servers[server.install_name] = 'inactive'

    # Get's the paths of every active tmux session.
    cmd = ["/usr/bin/tmux", "list-sessions", "-F", "'#{session_path}'"]
    out = subprocess.run(cmd,
        capture_output=True, text=True
    )

    if out.stderr:
        # For debug.
        #print(out.stderr)

        # Stderr is probably the default tmux no servers running msg.
        # But either way if tmux errors just return no servers active.
        return active_servers

    # Find out which game server the session path(s) belong to.

    # First get list of active session paths.
    session_paths = []
    for path in out.stdout.split('\n'):
        # Only allow valid paths.
        if '/' not in path:
            continue
        session_paths.append(path.strip("'"))

    # Next compare the current tmux session paths against the installed game
    # server paths.
    for server in all_game_servers:
        for session_path in session_paths:
            # If the session_path is beneith the install_path add that server
            # to active servers list.
            path_comparitor = (os.path.realpath(session_path), server.install_path)
            if os.path.commonprefix(path_comparitor) == server.install_path:
                active_servers[server.install_name] = 'active'

    return active_servers


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
    # Attempt's to get sudo tty ticket.
    try:
        subprocess.run(['/usr/bin/sudo', '-S', 'apt-get', 'check'],
                       check=True,
                       input=sudo_pass,
                       stderr=subprocess.PIPE,
                       universal_newlines=True)
        return True
    except subprocess.CalledProcessError as e:
        return False


# Turns data in commands.json into list of command objects that implement the
# CmdDescriptor class.
def get_commands():
    commands_json = open('commands.json', 'r')
    json_data = json.load(commands_json)
    commands_json.close()

    commands = []
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
    servers_json = open('game_servers.json', 'r')
    json_data = json.load(servers_json)
    servers_json.close()
    return dict(zip(json_data['servers'], json_data['server_names']))


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
def check_and_get_lgsmsh(lgsmsh):
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


