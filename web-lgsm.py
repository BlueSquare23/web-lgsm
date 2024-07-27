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
    print(" [*] Press Ctrl + C to exit!")
    from app import main
    # For clean ctrl + c handling.
    signal.signal(signal.SIGINT, signalint_handler)
    app = main()
    app.run(debug=True, host=HOST, port=PORT)
    

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
  ║   -d, --debug       Start server in debug mode           ║
  ╚══════════════════════════════════════════════════════════╝
    """)
    exit()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hsmrqd", ["help", "start", "stop", "status", "restart", "debug"])
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

if __name__ == "__main__":
    main(sys.argv[1:])

