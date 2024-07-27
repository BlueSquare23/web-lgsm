#!/usr/bin/env python3
# Main Web LGSM Wrapper Script!
# Rewritten in Python by John R. July 2024.

import os
import sys
import subprocess

# Where we at with it, Ali?
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))

def relaunch_in_venv():
    """Activate the virtual environment and relaunch the script."""
    venv_path = SCRIPTPATH + '/venv/bin/activate'
    if not os.path.isfile(venv_path):
        exit(f" [!] Virtual environment not found at {venv_path}\n" +
             "Create a virtual environment using the following command:\n" +
             "\tpython3 -m venv venv")

    # Activate the virtual environment and re-run the script.
    activate_command = f'source {venv_path} && exec python3 {" ".join(sys.argv)}'
    subprocess.run(activate_command, shell=True, executable='/bin/bash')

# Protection in case user is not in venv.
if os.getenv('VIRTUAL_ENV') is None:
    relaunch_in_venv()
    sys.exit(0)

# Continue imports once we know we're in a venv.
import time
import getopt
import configparser

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
        sys.exit()

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

def print_help():
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
  ╚══════════════════════════════════════════════════════════╝
    """)
    sys.exit()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hsmrq", ["help", "start", "stop", "status", "restart"])
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

if __name__ == "__main__":
    main(sys.argv[1:])

