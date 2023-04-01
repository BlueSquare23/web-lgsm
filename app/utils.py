import os
import re
import json
import requests
import subprocess

# WARNING!!! DANGEROUS EXEC FUNCTIONS ATM!!! FUNCTIONS STILL NEEDS ADDITIONAL
# INPUT VALIDATION!!! Working on it...

def shell_exec(exec_dir, base_dir, cmds):

    os.chdir(exec_dir)

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

    os.chdir(base_dir)

# Kindly does the live process read.
def read_process(exec_dir, base_dir, cmds, mode):
    yield "<!DOCTYPE html><html lang='en'></head><body style='background-color: black;'>"
    yield "<link rel='stylesheet' href='/static/css/main.css'>"
    yield """<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css'
         rel='stylesheet'
         integrity='sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We'
         crossorigin='anonymous'>"""

    yield """<button id='auto-scroll-button' type='button' class='btn btn-primary' 
            style='text-decoration:overline'>\/Toggle Auto-Scroll\/</button>"""

    yield "<script src='/static/js/auto-scroll-button.js'></script>"

    if mode == "install":
        yield """
        <script>
          // Scrolls to bottom of iframe automatically.
          // TODO: FIND BETTER SOLUTION.
          window.addEventListener('load', function(){
            window.location.href = "/home";
          })
        </script>
        <h2 style='color:green'>Installing Game Server<span
        class="loader__dot">.</span><span class="loader__dot">.</span><span
        class="loader__dot">.</span></h2>
        <h3 style='color:red'>Don't Click Away!</h3>
        <p style='color:green'>You'll be redirected when the installation finishes.</p>
        """

    yield "<pre style='color:green'>"

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
