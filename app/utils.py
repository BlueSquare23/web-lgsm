import os
import re
import sys
import json
import requests
import subprocess

# WARNING!!! DANGEROUS EXEC FUNCTIONS ATM!!! FUNCTIONS STILL NEEDS ADDITIONAL
# INPUT VALIDATION!!! Working on it...

def shell_exec(exec_dir, base_dir, cmds):
    # Change dir context for installation.
    os.chdir(exec_dir)

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
    
    except:
        os.chdir(base_dir)

    os.chdir(base_dir)


# Kindly does the live process read.
def read_process(exec_dir, base_dir, cmds, text_color, mode):
    yield "<!DOCTYPE html><html lang='en'></head><body style='background-color: black;'>"
    yield "<link rel='stylesheet' href='/static/css/main.css'>"
    yield """<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css'
         rel='stylesheet'
         integrity='sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We'
         crossorigin='anonymous'>"""

    yield """<button id='auto-scroll-button' type='button' class='btn btn-outline-primary' 
            style='text-decoration:overline'>\/Toggle Auto-Scroll\/</button>"""

    yield "<script src='/static/js/auto-scroll-button.js'></script>"

    if mode == "install":
        yield f"""
        <script>
          // Scrolls to bottom of iframe automatically.
          // TODO: FIND BETTER SOLUTION.
          window.addEventListener('load', function(){{
            window.location.href = "/home";
          }})
        </script>
        <h2 style='color:{text_color}'>Installing Game Server<span
        class="loader__dot">.</span><span class="loader__dot">.</span><span
        class="loader__dot">.</span></h2>
        <h3 style='color:red'>Don't Click Away!</h3>
        <p style='color:{text_color}'>You'll be redirected when the installation finishes.</p>
        """

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
