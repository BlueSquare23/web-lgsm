import os
import re
import sys
import pwd
import json
import glob
import time
import psutil
import shutil
import getpass
import requests
import subprocess
from . import db
from .models import GameServer
from flask import flash

# Network stats globals.
PREV_BYTES_SENT = psutil.net_io_counters().bytes_sent
PREV_BYTES_RECV = psutil.net_io_counters().bytes_recv
PREV_TIME = time.time()

# Misc Globals.
CWD = os.getcwd()
USER = getpass.getuser()

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


# Shell executor subprocess.Popen wrapper generator function. Runs a command
# through the shell and returns output in realtime by appending it to output
# object, which is read by output api.
def shell_exec(cmd, output, gs_dir=None):
    # Clear any previous output.
    output.output_lines.clear()

    # Set lock flag to true.
    output.process_lock = True

    print(cmd)
    print(" ".join(cmd))

    proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
    )

    for stdout_line in iter(proc.stdout.readline, ""):
        output.output_lines.append(stdout_line)

    for stderr_line in iter(proc.stderr.readline, ""):
        output.output_lines.append(stderr_line)

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

    # Get all processes named 'watch'
    watch_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info['name'] == 'watch':
            watch_processes.append((proc.pid, proc.username()))
    
    for pid, user in watch_processes:
        cmd = []
        if user != getpass.getuser():
            cmd += ['/usr/bin/sudo', '-n', '-u', user]
        cmd += ['/usr/bin/kill', '-9', str(pid)]

        proc = subprocess.run(cmd,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL)

        if proc.returncode != 0:
#            print("Cant kill proc")
            pass


# Translates a username to a uid using pwd module.
def get_uid(username):
    try:
        user_info = pwd.getpwnam(username)
        return user_info.pw_uid
    except KeyError:
        return None


# Get's game server ids from id file path, if id file exists. If it doesn't
# returns empty string.
def get_gs_id(id_file_path):
    if os.path.isfile(id_file_path):
        with open(id_file_path, 'r') as file:
            return file.read()
    else:
        return ""


# Get's the list of servers that are currently turned on.
def get_server_statuses(all_game_servers):
    # Initialize all servers inactive to start with.
    server_statuses = {}
    for server in all_game_servers:
        server_statuses[server.install_name] = 'inactive'

    # List all tmux sessions for all users.
    tmux_socdir_regex = '/tmp/tmux-*'
    socket_dirs = [d for d in glob.glob(tmux_socdir_regex) if os.path.isdir(d)]

    # Handle no sockets yet.
    if not socket_dirs:
        return server_statuses

    # Find all unique server ids.
    gs_ids = {}
    for server in all_game_servers:
        id_file_path = server.install_path + f'/lgsm/data/{server.script_name}.uid'
        gs_id = get_gs_id(id_file_path).strip()
        gs_ids[server.install_name] = gs_id

    # Now that we have all gs_ids, we can check if those tmux socket sessions
    # are running.
    for server in all_game_servers:
        socket = server.script_name + '-' + gs_ids[server.install_name]
        cmd = []
        if server.username != getpass.getuser():
            cmd += ['/usr/bin/sudo', '-n', '-u', server.username]

        cmd += ['/usr/bin/tmux', '-L', socket, 'list-session']
        proc = subprocess.run(cmd,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL)

        if proc.returncode == 0:
            server_statuses[server.install_name] = 'active'

    return server_statuses


# Get's socket file name for a given game server name.
def get_socket_for_gs(server):
    id_file_path = os.path.join(server.install_path, f'lgsm/data/{server.script_name}.uid')
    gs_id = get_gs_id(id_file_path).strip()
    socket_file_path = server.script_name + '-' + gs_id
    return socket_file_path


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
def del_server(server, remove_files, output):
    install_path = server.install_path
    server_name = server.install_name
    username = server.username

    GameServer.query.filter_by(install_name=server_name).delete()
    db.session.commit()

    if not remove_files:
        flash(f'Game server, {server_name} deleted!')
        return

    web_lgsm_user = getpass.getuser()

    if username == web_lgsm_user:
        if os.path.isdir(install_path):
            shutil.rmtree(install_path)
    else:
        sudo_rule_name = f'{web_lgsm_user}-{username}'
        # Set Ansible playbook vars.
        ansible_vars = dict()
        ansible_vars['action'] = 'delete'
        ansible_vars['gs_user'] = username
        ansible_vars['sudo_rule_name'] = sudo_rule_name
        write_ansible_vars_json(ansible_vars)

        cmd = ['/usr/bin/sudo', '-n', os.path.join(CWD, 'playbooks/ansible_connector.py')]
        shell_exec(cmd, output)

    flash(f'Game server, {server_name} deleted!')
    return

def write_ansible_vars_json(ansible_vars):
    ansible_vars_json_file = os.path.join(CWD, 'json/ansible_vars.json')
    # Write json to file.
    with open(ansible_vars_json_file, 'w') as json_file:
        json.dump(ansible_vars, json_file, indent=4)


# Validates submitted cfg_file for edit route.
def valid_cfg_name(cfg_file):
    gs_cfgs = open('json/accepted_cfgs.json', 'r')
    json_data = json.load(gs_cfgs)
    gs_cfgs.close()
    
    valid_gs_cfgs = json_data["accepted_cfgs"]

    for cfg in valid_gs_cfgs:
        if cfg_file == cfg:
            return True

    return False
    

# Turns data in commands.json into list of command objects that implement the
# CmdDescriptor class.
def get_commands(server, send_cmd):
    commands = []

    # Try except in case problem with json files.
    try:
        commands_json = open('json/commands.json', 'r')
        json_data = json.load(commands_json)
        commands_json.close()

        exemptions_json = open('json/ctrl_exemptions.json', 'r')
        exemptions_data = json.load(exemptions_json)
        exemptions_json.close()
    except:
        return commands

    # Remove send cmd if option disabled in main.conf.
    if send_cmd == "no":
        json_data["short_cmds"].remove("sd")
        json_data["long_cmds"].remove("send")
        json_data["descriptions"].remove("Send command to game server console.")

    # Remove exempted cmds.
    if server in exemptions_data:
        for short_cmd in exemptions_data[server]['short_cmds']:
            json_data["short_cmds"].remove(short_cmd)
        for long_cmd in exemptions_data[server]['long_cmds']:
            json_data["long_cmds"].remove(long_cmd)
        for desc in exemptions_data[server]['descriptions']:
            json_data["descriptions"].remove(desc)

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
def valid_command(cmd, server, send_cmd):
    commands = get_commands(server, send_cmd)
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
        headers = {'User-Agent': 'Wget/1.20.3 (linux-gnu)'}
        response = requests.get('https://linuxgsm.sh', headers=headers)
        with open(lgsmsh, 'wb') as f:
            f.write(response.content)
        os.chmod(lgsmsh, 0o755)
    except Exception as e:
        # For debug.
        print(e)
    print("Got linuxgsm.sh!")

# Checks for the presense of bad chars in input.
def contains_bad_chars(i):
    bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                  "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }
    if i is None:
        return False

    for char in bad_chars:
        if char in i:
            return True

    return False


# Returns a string comma separated game server script paths for a given user.
def get_user_script_paths(install_path, script_name):
    paths_query_result = GameServer.query.filter_by(username=script_name).with_entities(GameServer.install_path).all()
    game_server_paths = [path[0] for path in paths_query_result]
    user_script_paths = os.path.join(install_path, script_name)

    # Add any other game server paths for gs_user.
    for path in game_server_paths:
        user_script_paths += f",{path}"

    return user_script_paths


# Run's self update script.
def update_self():
    update_cmd = ['./web-lgsm.py', '--auto']
    proc = subprocess.run(update_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines=True)

    if proc.returncode != 0:
        return f"Error: {proc.stderr}"

    if 'up to date' in proc.stdout:
        return 'Already up to date!'

    if 'Update Required' in proc.stdout:
        return 'Web LGSM Upgraded! Restarting momentarily...'


# Sleep's 5 seconds then restarts the app.
def restart_self(restart_cmd):
    time.sleep(5)
    proc = subprocess.run(restart_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines=True)


# Gets bytes in/out per second. Stores last value in global.
def get_network_stats():
    global PREV_BYTES_SENT, PREV_BYTES_RECV, PREV_TIME

    # Get current counters and timestamp.
    net_io = psutil.net_io_counters()
    current_bytes_sent = net_io.bytes_sent
    current_bytes_recv = net_io.bytes_recv
    current_time = time.time()

    # Calculate the rate of bytes sent and received per second.
    bytes_sent_rate = (current_bytes_sent - PREV_BYTES_SENT) / (current_time - PREV_TIME)
    bytes_recv_rate = (current_bytes_recv - PREV_BYTES_RECV) / (current_time - PREV_TIME)

    # Update previous counters and timestamp.
    PREV_BYTES_SENT = current_bytes_sent
    PREV_BYTES_RECV = current_bytes_recv
    PREV_TIME = current_time

    return {
        'bytes_sent_rate': bytes_sent_rate,
        'bytes_recv_rate': bytes_recv_rate
    }


# Returns disk, cpu, mem, and network stats. Later turned into json for home
# page resource usage charts.
def get_server_stats():
    stats = dict() 

    # Disk
    total, used, free = shutil.disk_usage("/")
    # Add ~4% for ext4 filesystem metadata usage.
    percent_used = (((total * .04) + used) / total) * 100
    stats["disk"] = {
        'total': total, 
        'used': used, 
        'free': free, 
        'percent_used': percent_used
    }

    # CPU
    load1, load5, load15 = psutil.getloadavg()
    cpu_usage = (load1/os.cpu_count()) * 100
    stats["cpu"] = {
        'load1': load1,
        'load5': load5,
        'load15': load15,
        'cpu_usage': cpu_usage
    }

    # Mem
    mem = psutil.virtual_memory()
    # Total, used, available, percent_used.
    stats["mem"] = {
        'total': mem[0], 
        'used': mem[3],
        'free': mem[1],
        'percent_used': mem[2]
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
