import os
import re
import json
import requests
import subprocess

# WARNING!!! DANGEROUS EXEC FUNCTIONS ATM!!! FUNCTIONS STILL NEEDS ADDITIONAL
# INPUT VALIDATION!!! Working on it...

def shell_exec(exec_dir, base_dir, cmd_list):

    os.chdir(exec_dir)

    proc = subprocess.Popen(cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    for stdout_line in iter(proc.stdout.readline, ""):
        yield stdout_line

    for stderr_line in iter(proc.stderr.readline, ""):
        yield "<span style='color:red'>" + stderr_line + "</span>"

    proc.stdout.close()
    proc.stderr.close()

    os.chdir(base_dir)

# Kindly does the live process read.
def read_process(exec_dir, base_dir, cmd_list, ):
    yield "<!DOCTYPE html><html lang='en'><body>"
    yield "<pre style='color:green'>"
    for line in shell_exec(exec_dir, base_dir, cmd_list):
        yield escape_ansi(line)
    yield "</pre>"
    yield "</body></html>"


#    proc = subprocess.Popen(['/usr/bin/wget', '-O', 'linuxgsm.sh', 'https://linuxgsm.sh'],
#    proc = subprocess.Popen(['./linuxgsm.sh', 'list'],
#    proc = subprocess.Popen(['./linuxgsm.sh', script_name],

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
