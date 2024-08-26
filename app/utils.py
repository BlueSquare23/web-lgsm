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
def shell_exec(exec_dir, cmd, output):
    # Clear any previous output.
    output.output_lines.clear()

    # Set lock flag to true.
    output.process_lock = True

    print(cmd)

    proc = subprocess.Popen(cmd,
            cwd=exec_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
    )

    for stdout_line in iter(proc.stdout.readline, ""):
        output.output_lines.append(escape_ansi(stdout_line))

    for stderr_line in iter(proc.stderr.readline, ""):
        output.output_lines.append(escape_ansi(stderr_line))

    # If run in auto-install mode, do cfg fix after install finishes.
    if ('auto-install' in cmd):
        # TODO: Make this work for multi system user setup!
        post_install_cfg_fix(exec_dir)

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
    id_file_path = server.install_path + f'/lgsm/data/{server.script_name}.uid'
    gs_id = get_gs_id(id_file_path).strip()
    socket = server.script_name + '-' + gs_id
    return socket


# Cleans up old dead tmux socket files.
def purge_user_tmux_sockets():
    uid = os.getuid()
    socket_dir = f"/tmp/tmux-{uid}"
    # Handle no sockets yet.
    if os.path.exists(socket_dir):
        user_tmux_sockets = os.listdir(socket_dir)
        for socket in user_tmux_sockets:
            os.remove(socket_dir + '/' + socket)


# After installation fixes lgsm cfg files.
def post_install_cfg_fix(gs_dir):
    # Find the default and common configs.
    default_cfg = next(os.path.join(root, name) \
        for root, _, files in os.walk(f"{gs_dir}/lgsm/config-lgsm") \
            for name in files if name == "_default.cfg")
    common_cfg = next(os.path.join(root, name) \
        for root, _, files in os.walk(f"{gs_dir}/lgsm/config-lgsm") \
            for name in files if name == "common.cfg")

    # Strip the first 9 lines of warning comments from _default.cfg and write
    # the rest to the common.cfg.
    with open(default_cfg, 'r') as default_file, open(common_cfg, 'w') as common_file:
        for _ in range(9):
            next(default_file)  # Skip the first 9 lines
        for line in default_file:
            common_file.write(line)


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
        here = os.getcwd()
        apb_path = os.path.join(here, 'venv/bin/ansible-playbook')
        del_usr_path = os.path.join(here, 'playbooks/delete_user.yml')
        cmd = [ 'sudo', '-n', apb_path, del_usr_path,
                '-e', f'sudo_rule_name={sudo_rule_name}',
                '-e', f'gs_user={username}' ]

        shell_exec(os.getcwd(),cmd,output)

    flash(f'Game server, {server_name} deleted!')
    return


# Uses sudo_pass to get sudo tty ticket.
def get_tty_ticket(sudo_pass):
    # Attempt's to get sudo tty ticket. Uses try, except because subprocess.run
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
def is_invalid_command(cmd, server, send_cmd):
    commands = get_commands(server, send_cmd)
    for command in commands:
        # If cmd is in list of short_cmds return False.
        # Aka is not invalid command.
        if cmd == command.short_cmd:
            return False

    return True


## Install Page Utils.

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

# Removes color codes from cmd line output.
def escape_ansi(line):
    # TODO: If I use xterm.js, I wont need this anymore... Escape sequences can be
    # passed right to the web term and will be rendered in true color.
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

    return False


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



