import os
import re
import sys
import json
import psutil
import requests
import subprocess

# Kindly does the RCE.
def shell_exec(exec_dir, base_dir, cmds):
    # Change dir context for installation.
    os.chdir(exec_dir)

    proc = None

    # Try, except in case user leave while generator's outputting.
    try:
        proc = subprocess.Popen(cmds,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True)
    
        for stdout_line in iter(proc.stdout.readline, ""):
            yield stdout_line
    
        for stderr_line in iter(proc.stderr.readline, ""):
            yield "<span style='color:red'>" + stderr_line + "</span>"
    
        proc.stdout.close()
        proc.stderr.close()
        proc.kill()
    
    except:
        proc.stdout.close()
        proc.stderr.close()
        proc.kill()

        os.chdir(base_dir)

    os.chdir(base_dir)

# Kills any running sub procs and resets the apps dir context in case user
# leaves a page while generator proc is still executing.
def reset_app(base_dir):
    app_proc = psutil.Process(os.getpid())
    for child in app_proc.children(recursive=True):
        print(child)
        child.kill()

    os.chdir(base_dir)

# Kindly does the live process read.
def read_process(exec_dir, base_dir, cmds, text_color, mode):
    with open(f'{base_dir}/app/templates/generator_head.html') as header_file:
        for line in header_file:
            yield line

    if mode == "install":
        with open(f'{base_dir}/app/templates/install_mode.html') as html_file:
            for line in html_file:
                yield line

    yield f"<pre style='color:{text_color}'>"

    for line in shell_exec(exec_dir, base_dir, cmds):
        yield escape_ansi(line)

    yield "</pre>"
    yield "</body></html>"

## Probably not the best solution.
## Potentially vulnerable, will look into better options.
# Uses sudo_pass to get sudo tty ticket.
def get_tty_ticket(sudo_pass):
    escaped_password = sudo_pass.replace('"', '\\"')
    
    # Attempt's to get sudo tty ticket.
    proc = subprocess.Popen('/usr/bin/sudo -S apt-get check', 
                shell=True, 
                stdin=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True)
    stdout, stderr = proc.communicate(input=escaped_password)

    print(proc.returncode)
    if proc.returncode != 0:
        print(stderr)
        return False

    # For debug.
    print(stdout)
    return True

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
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]|[(B]')
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

# Get's random doggo pic.
def get_doggo():
	url = "https://random.dog/woof.json"

	s = requests.Session()
	g = s.get(url)

	doggo_json = json.loads(g.text)
	doggo_url = doggo_json["url"]
	doggo_size = doggo_json["fileSizeBytes"]

	# If the img is larger than 3mb...
	if doggo_size > 3000000:
        # Then recurse to find better link and return the link.
		doggo_url = get_doggo()

	# Or if the link is to an mp4 webm video...
	if "mp4" in doggo_url or "webm" in doggo_url:
        # Then recurse to find better link and return the link.
		doggo_url = get_doggo()

	return doggo_url
