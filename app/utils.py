import re
import json
import requests
import subprocess

# Kindly does the RCE.
def rce(cmd, arg):
    proc = subprocess.Popen([cmd, arg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    return proc.communicate()

# Kindly does the console read RCE.
def capture_tmux_pane(script_name):
    proc = subprocess.Popen(['/usr/bin/tmux', 'capture-pane', '-pS', '-5', '-t', script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    return proc.communicate()

# Kindly does the linuxgsm.sh wget RCE. Their site blocks python requests
# somehow. I tried changing the UA, that didn't work. Will find a better
# solution l8t3r.
def wget_lgsmsh():
    proc = subprocess.Popen(['/usr/bin/wget', '-O', 'linuxgsm.sh', 'https://linuxgsm.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    return proc.communicate()

# Kindly does the linuxgsm.sh server listing RCE.
def list_all_lgsm_servers():
    proc = subprocess.Popen(['./linuxgsm.sh', 'list'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    return proc.communicate()

# Kindly does the linuxgsm.sh server install RCE.
def pre_install_lgsm_server(script_name):
    proc = subprocess.Popen(['./linuxgsm.sh', script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    return proc.communicate()

# Removes color codes from cmd line output.
def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)

# Checks for the presense of bad chars in input.
def contains_bad_chars(i):
    bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                  "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }

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
