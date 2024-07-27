#!/usr/bin/env python3
# Main Web LGSM Wrapper Script!
# Rewritten in Python by John R. July 2024.

import os
import sys
import signal
import subprocess

# Where we at with it, Ali?
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))

def signalint_handler(sig, frame):
    # Suppress stderr for debug ctrl + c stack trace.
    with open(os.devnull, 'w') as fnull:
        sys.stdout = fnull
        sys.stderr = fnull
        sys.stdout = sys.__stdout__
        print('\r [!] Ctrl + C received. Shutting down...')

    exit(0)

def relaunch_in_venv():
    """Activate the virtual environment and relaunch the script."""
    venv_path = SCRIPTPATH + '/venv/bin/activate'
    if not os.path.isfile(venv_path):
        exit(f" [!] Virtual environment not found at {venv_path}\n" +
             "Create a virtual environment using the following command:\n" +
             "\tpython3 -m venv venv")

    # Activate the virtual environment and re-run the script.
    activate_command = f'source {venv_path} && exec python3 {" ".join(sys.argv)}'
    signal.signal(signal.SIGINT, signalint_handler)

    # Use subprocess.Popen for real-time output
    process = subprocess.Popen(
        activate_command,
        shell=True,
        executable='/bin/bash',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Read the output in real-time.
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Wait for the process to complete.
    process.wait()

# Protection in case user is not in venv.
if os.getenv('VIRTUAL_ENV') is None:
    relaunch_in_venv()
    exit(0)

# Continue imports once we know we're in a venv.
import time
import getopt
import string
import getpass
import configparser
from werkzeug.security import generate_password_hash
from app import db, main as appmain
from app.models import User
from app.utils import contains_bad_chars

# Import config data.
config = configparser.ConfigParser()
config.read(os.path.join(SCRIPTPATH, 'main.conf'))
HOST = config['server']['host']
PORT = config['server']['port']

os.environ['COLUMNS'] = '80'
os.environ['LINES'] = '50'
os.environ['TERM'] = 'xterm-256color'

def stop_server():
    result = subprocess.run(["pkill", "gunicorn"], capture_output=True)
    if result.returncode == 0:
        print(" [*] Server Killed!")
    else:
        print(" [!] Server Not Running!")

def check_status():
    result = subprocess.run(["pgrep", "-f", "gunicorn.*web-lgsm"], capture_output=True)
    if result.returncode == 0:
        print(" [*] Server Currently Running.")
    else:
        print(" [*] Server Not Running.")

def start_server():
    status_result = subprocess.run(["pgrep", "-f", "gunicorn.*web-lgsm"], capture_output=True)
    if status_result.returncode == 0:
        print("Server Already Running!")
        exit()

    print(f"""
 ╔═══════════════════════════════════════════════════════╗
 ║ Welcome to the Web LGSM! ☁️  🕹️                         ║
 ║                                                       ║
 ║ You can access the web-lgsm via the url below!        ║
 ║                                                       ║
 ║ http://{HOST}:{PORT}/                               ║
 ║                                                       ║
 ║ You can kill the web server with:                     ║
 ║                                                       ║
 ║ ./web-lgsm.py --stop                                  ║
 ║                                                       ║
 ║ Please Note: It is strongly advisable to firewall off ║
 ║ port {PORT} to the outside world and then proxy this   ║
 ║ server to a real web server such as Apache or Nginx   ║
 ║ with SSL encryption! See the Readme for more info.    ║
 ╚═══════════════════════════════════════════════════════╝
    """)

    # Try to start the gunicorn server as a detached proc.
    try:
        process = subprocess.Popen(
            ["gunicorn", 
             "--access-logfile", f"{SCRIPTPATH}/web-lgsm.log",
             f"--bind={HOST}:{PORT}",
             "--daemon",
             "--worker-class", "gevent",
             "app:main()"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f" [*] Launched Gunicorn server with PID: {process.pid}")
    except Exception as e:
        print(f" [!] Failed to launch Gunicorn server: {e}")

def start_debug():
    """Starts the app in debug mode"""
    from app import main
    # For clean ctrl + c handling.
    signal.signal(signal.SIGINT, signalint_handler)
    app = main()
    app.run(debug=True, host=HOST, port=PORT)

def validate_password(username, password1, password2):
    # Make sure required form items are supplied.
    for form_item in (username, password1, password2):
        if form_item is None or form_item == "":
            return False, "Missing required form field(s)!"

        # Check input lengths.
        if len(form_item) > 150:
            return False, "Form field too long!"

    # Setup rudimentary password strength counter.
    lower_alpha_count = 0
    upper_alpha_count = 0
    number_count = 0
    special_char_count = 0

    # Adjust password strength values.
    for char in list(password1):
        if char in string.ascii_lowercase:
            lower_alpha_count += 1
        elif char in string.ascii_uppercase:
            upper_alpha_count += 1
        elif char in string.digits:
            number_count += 1
        else:
            special_char_count += 1

    # Verify password passes basic strength tests.
    if upper_alpha_count < 1 and number_count < 1 and special_char_count < 1:
        return False, "Password doesn't meet criteria! Must contain: an upper case character, a number, and a special character"

    # To try to nip xss & template injection in the bud.
    if contains_bad_chars(username):
        return False, "Username contains illegal character(s)"

    if password1 != password2:
        return False, "Passwords don't match!"

    if len(password1) < 12:
        return False, "Password is too short!"

    return True, ""

def change_password():
    """Change the password for a given user."""

    username = input("Enter username: ")
    password1 = getpass.getpass("Enter new password: ")
    password2 = getpass.getpass("Confirm new password: ")

    # Validate the new password
    is_valid, message = validate_password(username, password1, password2)

    if not is_valid:
        print(f"Error: {message}")
        return

    # Find the user in the database
    user = User.query.filter_by(username=username).first()

    if user is None:
        print("Error: User not found!")
        return

    # Update the user's password hash
    user.password = generate_password_hash(password1, method='pbkdf2:sha256')
    db.session.commit()

    print("Password updated successfully!")



def print_help():
    """Prints help menu"""
    print("""
  ╔══════════════════════════════════════════════════════════╗  
  ║ Usage: web-lgsm.py [options]                             ║
  ║                                                          ║
  ║   Options:                                               ║
  ║                                                          ║
  ║   -h, --help        Prints this help menu                ║
  ║   -s, --start       Starts the server (default no args)  ║
  ║   -q, --stop        Stop the server                      ║
  ║   -r, --restart     Restart the server                   ║
  ║   -m, --status      Show server status                   ║
  ║   -d, --debug       Start server in debug mode           ║
  ║   -p, --passwd      Change web user password             ║
  ╚══════════════════════════════════════════════════════════╝
    """)
    exit()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hsmrqdp", ["help", "start", "stop", "status", "restart", "debug", "passwd"])
    except getopt.GetoptError:
        print_help()

    if not opts and not args:
        start_server()
        return

    for opt, _ in opts:
        if opt in ("-h", "--help"):
            print_help()
        elif opt in ("-s", "--start"):
            start_server()
            return
        elif opt in ("-m", "--status"):
            check_status()
            return
        elif opt in ("-r", "--restart"):
            stop_server()
            time.sleep(2)
            start_server()
            return
        elif opt in ("-q", "--stop"):
            stop_server()
            return
        elif opt in ("-d", "--debug"):
            start_debug()
            return
        elif opt in ("-p", "--passwd"):
            # Technically, needs run in app context.
            app = appmain()
            with app.app_context():
                change_password()
            return

if __name__ == "__main__":
    main(sys.argv[1:])

