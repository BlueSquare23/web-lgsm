#!/usr/bin/env python3
# This python3 CGI script lists and processes the lsgm game server commands for
# the supplied game server.

import os
import re
import subprocess
import cgi, cgitb
import json
import requests

def check_input(i):
    # Sanitization list.
    bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                  "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }

    for char in bad_chars:
        if char in i: 
            print("<h3 style='color:red'>NO TRY HAX!!!</h3>")
            return


def run_script(cmd, arg):
    proc = subprocess.Popen([cmd, arg], 
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
    
    return proc.communicate()


# Removes color codes from cmd line output.
def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)

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

def main():
    cgitb.enable() # For debugging.
    form = cgi.FieldStorage()
    server_name = form.getvalue('server_name')
    script_arg = form.getvalue('arg')
    refresh = form.getvalue('refresh')

    # Ctype header makes it a cgi. 
    print("Content-type: text/html\n\n")
    print("<!DOCTYPE html>")

    iframe_head = """<head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Web LGSM</title>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
            rel="stylesheet"
            integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"
            crossorigin="anonymous">
        </head>"""
    print(iframe_head)
    print("<body style='background-color:black'>")

    # Make sure cgi input is suplied.
    if server_name is None:
        print("<h3 style='color:red'>Server Name Empty!</h3>")
        return
    
    doggo_img = get_doggo()

    # For bootstrap5 spinner element.
    print(f"""<script>
      function displaySpinner(){{
        var head = '<!DOCTYPE html>' + '<head>';
        var bootstrap_html = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"' +
        ' rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"' +
        ' crossorigin="anonymous"></head>';

        var body = '<body style="background-color:black">' +
               '<h2><i style="color: green">Thinking...</i></h2><br>';

        var spinners = '<div class="spinner-border text-primary" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>' +
                  '<div class="spinner-border text-secondary" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>' +
                  '<div class="spinner-border text-success" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>' +
                  '<div class="spinner-border text-danger" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>' +
                  '<div class="spinner-border text-warning" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>' +
                  '<div class="spinner-border text-info" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>' +
                  '<div class="spinner-border text-light" role="status">' +
                    '<span class="visually-hidden">Loading...</span> </div>'; 

        var doggo = "<hr style='color:white'><p style='color:green'>Here's some puppers while you wait!</p>" +
                '<a href="{doggo_img}" alt="Random Doggo Link!" title="Click to open image in new tab." target="_blank">' +
                '<img class="img-fluid img-thumbnail" loading="lazy" src="{doggo_img}" alt="Random Dog Image"></img>' +
                '</a></body></head>';

        document.write(head);
        document.write(bootstrap_html);
        document.write(body);
        document.write(spinners);
        document.write(doggo);
      }}
    </script>""")

    server_name = server_name.strip("'")

    web_lgsm_path = os.path.abspath(os.getcwd())
    script_path = f"{web_lgsm_path}/../{server_name}"

    # Check server file exists!
    if os.path.exists(script_path) is False:
        print("<h3 style='color:red'>Server Script File Not Found!</h3>")
        return
        
    # If there's an arg, run in cmd mode, otherwise run in list mode.
    if script_arg is not None:
        # Check for hax injectypoo attempt!
        check_input(script_arg)

        # If arg is install (requires stdin (y/n) prompts) deny.
        if script_arg == "i": 
            print("<h3 style='color:red'>Install option disabled.</h3>")
            return
        # Not allowed to start in debug mode.
        if script_arg == "d": 
            print("<h3 style='color:red'>Debug option disabled.</h3>")
            return
        # Not allowed to create a skel dir.
        if script_arg == "sk": 
            print("<h3 style='color:red'>Skel dir option disabled.</h3>")
            return
        # If its live console use custom python console solution.
        if script_arg == "c":
            proc = subprocess.Popen(['tmux', 'capture-pane', '-pS', '-5'], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)
            stdout, stderr = proc.communicate()
            print("<pre style='color:red'>" + escape_ansi(stderr) + "</pre>")
            print("<pre style='color:green'>" + escape_ansi(stdout) + "</pre>")
            location_html = f"<script>window.location.href = '/cgi-bin/controls.cgi?server_name={server_name}&arg=c#bottom'\n"
            refresh_button = "<button class='btn btn-primary' onclick='refresh = window.location.reload()'>Refresh</button>"
            #auto_refresh_js = """setTimeout(function(){
            #                   window.location.reload();
            #                }, refresh);"""
            bottom_ancor = "</script> <a name='bottom'></a>"
            print(location_html + bottom_ancor + refresh_button)
            return

        stdout, stderr = run_script(script_path, script_arg)

         # For Debug.
#        if stderr != "":
#            print("<pre style='color:red'>" + escape_ansi(stderr) + "</pre>")
#            return

        print("<pre style='color:green'>" + escape_ansi(stdout) + "</pre>")

    else:
        stdout, stderr = run_script(script_path, "")

        if stderr != "":
            print(stderr)
            return

        # Drop first 6 lines of useless output.
        cmds = escape_ansi(stdout).split('\n',6)[-1]

        class CmdDescriptor:
            def __init__(self):
                self.long_cmd  = []
                self.short_cmd = []
                self.description = []

        commands = []

        for line in cmds.splitlines():
            cmd = CmdDescriptor()
            args = line.split()
            cmd.long_cmd.append(args[0])
            cmd.short_cmd.append(args[1])
            cmd.description.append(line.split("|")[1])
            commands.append(cmd)


        print('<div class="container">')

        for command in commands: 
            button_text = f"""<a onclick='displaySpinner()' class='btn btn-primary' 
            href='/cgi-bin/controls.cgi?server_name={server_name}&arg={command.short_cmd[0]}'>
            {command.long_cmd[0]}</a>"""

            container_text = f"""<div class="p-2 row align-items-center">
                   <div class="col">
                     {button_text}
                   </div>
                   <div class="col" style="color:green">
                     {command.description[0]}
                   </div>
                 </div>"""
            print(container_text)

        print("</div>")
 
    print("</body>")
    
if __name__ == '__main__':
    main()
