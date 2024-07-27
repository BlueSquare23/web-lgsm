#!/usr/bin/env python3
# Main Web LGSM Wrapper Script!
# Rewritten in Python by John R. July 2024.

import os
import sys
import getopt
import subprocess
import time
import configparser

# Setup Globals.
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))

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
        print("Server Killed!")
    else:
        print("Server Not Running.")

def check_status():
    result = subprocess.run(["pgrep", "-f", "gunicorn.*web-lgsm"], capture_output=True)
    if result.returncode == 0:
        print("Server Already Running!")
    else:
        print("Server Not Running.")

def start_server():
    status_result = subprocess.run(["pgrep", "-f", "gunicorn.*web-lgsm"], capture_output=True)
    if status_result.returncode == 0:
        print("Server Already Running!")
        sys.exit()

    print(f"""
    Welcome to the Web LGSM!

    You can access the web-lgsm via the url below!

    http://{HOST}:{PORT}/

    You can kill the web server with:

    {SCRIPTPATH}/web-lgsm.py --stop

    Please Note: It is strongly advisable to firewall off port {PORT} to the
    outside world and then proxy this server to a real web server such as
    Apache or Nginx with SSL encryption! See the Readme for more info.
    """)

    # Activate virtual environment
    activate_script = os.path.join(SCRIPTPATH, "venv", "bin", "activate")
    if "VIRTUAL_ENV" not in os.environ:
        command = f"source {activate_script} && gunicorn --access-logfile web-lgsm.log --bind={HOST}:{PORT} --daemon --worker-class gevent 'app:main()'"
        subprocess.run(command, shell=True, executable='/bin/bash')
    else:
        subprocess.run(["gunicorn", "--access-logfile", os.path.join(SCRIPTPATH, "web-lgsm.log"),
                        "--bind={}:{}".format(HOST, PORT),
                        "--daemon",
                        "--worker-class", "gevent", "'app:main()'"])

def print_help():
    print("""
    Usage: web-lgsm.py [options]

      Options:

      -h, --help        Prints this help menu
      -s, --start       Starts the server (default no args)
      -q, --stop        Stop the server
      -r, --restart     Restart the server
      -m, --status      Show server status

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

