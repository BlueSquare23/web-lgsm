#!/usr/bin/env python3
# Main Web LGSM Wrapper Script!
# Rewritten in Python by John R. July 2024.

import os
import sys
import signal
import subprocess

# Where we at with it, Ali?
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPTPATH)


def signalint_handler(sig, frame):
    # Suppress stderr for debug ctrl + c stack trace.
    with open(os.devnull, "w") as fnull:
        sys.stdout = fnull
        sys.stderr = fnull
        sys.stdout = sys.__stdout__
        print("\r [!] Ctrl + C received. Shutting down...")

    exit(0)


def run_command_popen(command):
    """Runs a command through a subprocess.Popen shell"""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            executable="/bin/bash",
            stdin=None,   # Connect input to the terminal.
            stdout=None,  # Direct output to the terminal.
            stderr=None,  # Direct error output to the terminal.
            text=True,
            env=os.environ,
        )

        # Wait for the process to complete.
        return_code = process.wait()
        if return_code > 0:
            exit(return_code)

    except ValueError as e:
        # Handle any specific value errors.
        print(e)
        exit(return_code)

    except Exception as e:
        # Catch any other unforeseen errors.
        print(f" [!] An unexpected error occurred: {e}")
        exit(23)


def relaunch_in_venv():
    """Activate the virtual environment and relaunch the script."""
    venv_path = "/opt/web-lgsm/bin/activate"
    if not os.path.isfile(venv_path):
        err_msg = f"""\
 [!] Virtual environment not found at {venv_path}
 [*] Create a virtual environment using the following commands:
         sudo python3 -m venv /opt/web-lgsm
 [*] Then install the required pip packages with this command:
        sudo /opt/web-lgsm/bin/pip3 install -r requirements.txt\
        """
        exit(err_msg)

    # Activate the virtual environment and re-run the script.
    activate_command = f'source {venv_path} && exec python3 {" ".join(sys.argv)}'
    signal.signal(signal.SIGINT, signalint_handler)

    run_command_popen(activate_command)


# Protection in case user is not in venv.
if os.getenv("VIRTUAL_ENV") is None:
    print(" [*] Sourcing venv!")
    relaunch_in_venv()
    exit(0)


# Continue imports once we know we're in a venv.
import json
import time
import getopt
import shutil
import string
import getpass
import tarfile
import configparser
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import db, main as appmain
from app.models import User
from app.utils import check_and_get_lgsmsh

# Import config data.
CONFIG_FILE = "main.conf"
CONFIG_LOCAL = "main.conf.local"  # Local config override.
if os.path.isfile(CONFIG_LOCAL) and os.access(CONFIG_LOCAL, os.R_OK): 
    CONFIG_FILE = CONFIG_LOCAL
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(SCRIPTPATH, CONFIG_FILE))
try:
    HOST = CONFIG["server"]["host"]
    PORT = CONFIG["server"]["port"]
    DEBUG = CONFIG["debug"].getboolean("debug")
    LOG_LEVEL = CONFIG["debug"]["log_level"]
except KeyError as e:
    print(f" [!] Configuration setting {e} not set.")
    HOST = "127.0.0.1"
    PORT = "12357"
    DEBUG = False
    LOG_LEVEL = "info"

os.environ["LOG_LEVEL"] = LOG_LEVEL

# Global options hash.
O = {"verbose": False, "check": False, "auto": False, "test_full": False, "noback": False}

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


def print_start_banner():
    bar_len = 55
    host_line_char_len = len(" http://:/") + len(HOST) + len(PORT)
    host_line_spaces_len = bar_len - host_line_char_len
    host_line_spaces = " " * host_line_spaces_len

    port_line_char_len = len("  port to the outside world and then proxy this") + len(
        PORT
    )
    port_line_spaces_len = bar_len - port_line_char_len
    port_line_spaces = " " * port_line_spaces_len

    print(
        f"""
 ╔═══════════════════════════════════════════════════════╗
 ║ Welcome to the Web LGSM! ☁️  🕹️                         ║
 ║                                                       ║
 ║ You can access the web-lgsm via the url below!        ║
 ║                                                       ║
 ║ http://{HOST}:{PORT}/{host_line_spaces}║
 ║                                                       ║
 ║ You can kill the web server with:                     ║
 ║                                                       ║
 ║ ./web-lgsm.py --stop                                  ║
 ║                                                       ║
 ║ Please Note: It is strongly advisable to firewall off ║
 ║ port {PORT} to the outside world and then proxy this{port_line_spaces}║
 ║ server to a real web server such as Apache or Nginx   ║
 ║ with SSL encryption! See the Readme for more info.    ║
 ╚═══════════════════════════════════════════════════════╝
    """
    )


def start_server():
    status_result = subprocess.run(
        ["pgrep", "-f", "gunicorn.*web-lgsm"], capture_output=True
    )
    if status_result.returncode == 0:
        print(" [!] Server Already Running!")
        exit()

    print_start_banner()

    access_log = os.path.join(SCRIPTPATH, "logs/access.log")
    error_log = os.path.join(SCRIPTPATH, "logs/error.log")

    try:
        cmd = [
            "gunicorn",
            "--access-logfile",
            access_log,
            "--disable-redirect-access-to-syslog",
            "--error-logfile",
            error_log,
            "--log-level",
            LOG_LEVEL,
            f"--bind={HOST}:{PORT}",
            "--daemon",
            "app:main()",
        ]

        cert = None
        key = None

        for key in CONFIG["server"]:
            if key == "cert":
                cert = CONFIG["server"]["cert"]

            if key == "key":
                key = CONFIG["server"]["key"]

        if cert and key:
            if os.path.isfile(cert) and os.access(cert, os.R_OK): 
                cmd.append(f"--certfile={cert}")
            else:
                print(f" [!] Error: Cant read cert file: {cert}", file=sys.stderr)
                exit(15)

            if os.path.isfile(key) and os.access(key, os.R_OK): 
                cmd.append(f"--keyfile={key}")
            else:
                print(f" [!] Error: Cant read key file: {key}", file=sys.stderr)
                exit(16)
        
        print(cmd)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        print(f" [*] Launched Gunicorn server with PID: {process.pid}")
    except Exception as e:
        print(f" [!] Failed to launch Gunicorn server: {e}")
        exit(99)
    finally:
        if "CONTAINER" in os.environ:

            # Touch the log, so tail doesn't die if it wins race.
            # Should fix: https://github.com/bluesquare23/web-lgsm/issues/44
            log = 'logs/access.log'
            with open(log, 'a'):
                os.utime(log, None)

            command = ["/usr/bin/tail", "-f", "logs/access.log"]
            
            try:
                # Tail follow access log in the foreground.
                process = subprocess.Popen(command)
                process.wait()  # Wait for the process to complete
            except KeyboardInterrupt:
                # Handle Ctrl+C to gracefully exit.
                print("\nTail follow terminated, but web-lgsm server still running!")
                exit(33)
            except Exception as e:
                # Handle any other exceptions.
                print(f"An error occurred: {e}")
                exit(55)
            finally:
                # Ensure the process is terminated.
                if process.poll() is None:
                    process.terminate()


def start_debug():
    """Starts the app in debug mode"""
    from app import main
    if DEBUG:
        os.environ["DEBUG"] = "YES"

    # For clean ctrl + c handling.
    signal.signal(signal.SIGINT, signalint_handler)
    app = main()
    app.run(debug=True, host=HOST, port=PORT)


def contains_bad_chars(input_item):
    """
    Checks for the presence of bad chars in supplied user input.

    Args:
        input_item (str): Supplied input item to check for bad chars.

    Returns:
        bool: True if item does contain one of the bad chars below, False
              otherwise.
    """
    bad_chars = {
        " ",
        "$",
        "'",
        '"',
        "\\",
        "#",
        "=",
        "[",
        "]",
        "!",
        "<",
        ">",
        "|",
        ";",
        "{",
        "}",
        "(",
        ")",
        "*",
        ",",
        "?",
        "~",
        "&",
    }

    # Its okay to skip None cause should be caught by earlier checks. Also
    # technically, None does not contain any bad chars...
    if input_item is None:
        return False

    for char in bad_chars:
        if char in input_item:
            return True

    return False


# TODO: Just import this from utils.py script. A copy of it is fine for now,
# but really shouldn't duplicate code like this.
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
        return (
            False,
            "Password doesn't meet criteria! Must contain: an upper case character, a number, and a special character",
        )

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
    user.password = generate_password_hash(password1, method="pbkdf2:sha256")
    db.session.commit()

    print("Password updated successfully!")


def update_gs_list():
    """Updates game server json by parsing latest `linuxgsm.sh list` output"""
    lgsmsh = SCRIPTPATH + "/scripts/linuxgsm.sh"
    check_and_get_lgsmsh(lgsmsh)

    servers_list = os.popen(f"{lgsmsh} list").read()

    short_names = []
    long_names = []
    gs_mapping = dict()

    for line in servers_list.split("\n"):
        if len(line.strip()) == 0:
            continue
        if "serverlist.csv" in line:
            continue
        short_name = line.split()[0]
        long_name = " ".join(line.split()[1:]).replace("'", "").replace("&", "and")

        short_names.append(short_name)
        long_names.append(long_name)
        gs_mapping[short_name] = long_name

    test_json = "test_data.json"
    test_src = os.path.join(SCRIPTPATH, test_json)
    test_dst = os.path.join(SCRIPTPATH, f"json/{test_json}")
    map_json = open(test_json, "w")
    map_json.write(json.dumps(gs_mapping, indent=4))
    map_json.close()
    compare_and_move(test_src, test_dst)

    gs_dict = {"servers": short_names, "server_names": long_names}

    servers_json = "game_servers.json"
    gs_src = os.path.join(SCRIPTPATH, servers_json)
    gs_dst = os.path.join(SCRIPTPATH, f"json/{servers_json}")
    gs_json = open(servers_json, "w")
    gs_json.write(json.dumps(gs_dict, indent=4))
    gs_json.close()
    compare_and_move(gs_src, gs_dst)


def compare_and_move(src_file, dst_file):
    """Diff's two files and moves src to dst if they differ."""
    file_name = os.path.basename(src_file)
    try:
        with open(src_file, "r") as file1, open(dst_file, "r") as file2:
            src_content = file1.read()
            dst_content = file2.read()

        if src_content != dst_content:
            print(f" [*] Backing up {file_name} to {file_name}.bak")
            shutil.copy(dst_file, dst_file + ".bak")
            shutil.move(src_file, dst_file)
            print(f" [!] File {file_name} JSON updated!")
        else:
            os.remove(src_file)
            print(f" [*] File {file_name} JSON already up to date.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except IOError as e:
        print(f"Error: {e}")


def run_command(command):
    if O["verbose"]:
        print(f" [*] Running command: {command}")

    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, env=os.environ
    )

    if O["verbose"]:
        print(result.stdout.strip())

    return result.stdout.strip()


def backup_file(filename):
    if not os.path.isfile(filename):
        print(f" [!] Warning: The file '{filename}' does not exist. No backup created!")
        return None

    epoc = int(time.time())
    backup_filename = f"{filename}.{epoc}.bak"
    os.rename(filename, backup_filename)
    print(f" [*] Backing up {filename} to {backup_filename}")
    return backup_filename


def backup_dir(dirname, tar=False):
    """Back's up directories using shutil.copydirtree, optionally tar's them too"""
    if not os.path.isdir(dirname):
        print(
            f" [!] Warning: The directory '{dirname}' does not exist. No backup created!"
        )
        return None

    epoc = int(time.time())
    backup_dirname = f"{dirname}.{epoc}.bak"
    print(f" [*] Backing up {dirname} to {backup_dirname}")
    shutil.copytree(dirname, backup_dirname)

    if tar:
        tar_filename = f"{backup_dirname}.tar.gz"
        print(f" [*] Creating tar file {tar_filename}")
        with tarfile.open(tar_filename, "w:gz") as tar_handle:
            tar_handle.add(backup_dirname, arcname=os.path.basename(backup_dirname))
        shutil.rmtree(backup_dirname)
        return tar_filename

    return backup_dirname


def is_up_to_date():
    """
    Check's if web-lgsm already up-to-date or not.
    """
    run_command('git fetch --quiet')
    output = run_command('git status -sb')
    if 'ahead' in output or 'behind' in output:
        return False

    return True


def update_weblgsm():
    """
    Update's the web-lgsm itself.
    """
    if is_up_to_date():
        print(" [*] Web LGSM already up to date!")
        return

    print(" [!] Update Available!")
    if O["check"]:
        return

    if not O["auto"]:
        resp = input(" [*] Would you like to update now? (y/n): ")
        if resp.lower() != "y":
            exit()

    # Backup whole web-lgsm folder.
    if not O["noback"]:
        print(" [*] Backing up and tarring, this may take a while...")
        backup_dir(SCRIPTPATH, tar=True)
        backup_file("main.conf")

    print(" [*] Pulling update from github...")
    run_command("git fetch --all")
    run_command("git reset --hard origin/master")

    print(" [*] Uninstalling old web-lgsm...")
    install_script = os.path.join(SCRIPTPATH, 'uninstall.sh')
    run_command(f"{uninstall_script} -d")

    print(" [*] Reinstalling newest web-lgsm...")
    install_script = os.path.join(SCRIPTPATH, 'install.sh')
    run_command(f"{install_script} -d")

    # Green check!
    print(f" [\033[32m✓\033[0m] Update Complete!")
    return


def run_tests():
    # If in container don't backup db.
    if "CONTAINER" not in os.environ:
        # Backup Database.
        db_file = os.path.join(SCRIPTPATH, "app/database.db")
        db_backup = backup_file(db_file)

    local_conf = 'main.conf.local'
    if os.path.exists(local_conf):
        local_conf_bak = backup_file(local_conf)

    # Enable verbose even if disabled by default just for test printing.
    if not O["verbose"]:
        O["verbose"] = True

    try:
        if O["test_full"]:
            # Backup Existing MC install, if one exists.
            mcdir = os.path.join(SCRIPTPATH, "Minecraft")
            if os.path.isdir(mcdir):
                backup_dir(mcdir)

                # Then torch dir.
                shutil.rmtree(mcdir)

            cmd = "coverage run -m pytest -v tests/"
            run_command_popen(cmd)

        else:
            cmd = "coverage run -m pytest -vvv tests/ -m 'not integration'"
            run_command_popen(cmd)

    finally:
        if db_backup:
            shutil.move(db_backup, db_file)

        shutil.move(local_conf_bak, local_conf)
        print("Restored database and main.conf.local")


def add_valid_gs_user(gs_user):
    cmd = f"/usr/bin/sudo echo '  - {gs_user}' >> playbooks/vars/accepted_gs_users.yml"
    run_command(cmd)


def print_help():
    """Prints help menu"""
    print(
        """
  ╔══════════════════════════════════════════════════════════╗  
  ║ Usage: web-lgsm.py [options]                             ║
  ║                                                          ║
  ║   Options:                                               ║
  ║                                                          ║
  ║   -h, --help          Prints this help menu              ║
  ║   -s, --start         Starts the server (default no args)║
  ║   -q, --stop          Stop the server                    ║
  ║   -r, --restart       Restart the server                 ║
  ║   -m, --status        Show server status                 ║
  ║   -d, --debug         Start server in debug mode         ║
  ║   -v, --verbose       More verbose output                ║
  ║   -p, --passwd        Change web user password           ║
  ║   -u, --update        Update web-lgsm version            ║
  ║   -c, --check         Check if an update is available    ║
  ║   -n, --noback        Don't backup web-lgsm for updates  ║
  ║   -a, --auto          Run an auto update                 ║
  ║   -f, --fetch_json    Fetch latest game servers json     ║
  ║   -t, --test          Run project's pytest tests (short) ║
  ║   -x, --test_full     Run ALL project's pytest tests     ║
  ║   -j, --valid [user]  Add valid gs_user to allow list    ║
  ╚══════════════════════════════════════════════════════════╝
    """
    )
    exit()


def main(argv):
    try:
        longopts = [
            "help",
            "start",
            "stop",
            "status",
            "restart",
            "debug",
            "verbose",
            "passwd",
            "update",
            "check",
            "noback",
            "auto",
            "fetch_json",
            "test",
            "test_full",
            "valid=",
        ]
        opts, args = getopt.getopt(argv, "hsmrqdvpucnaftxj:", longopts)
    except getopt.GetoptError as e:
        print(e)
        print_help()

    # If no flags, start the server.
    if not opts and not args:
        start_server()
        return

    # Push required opts to global dict.
    for opt, _ in opts:
        if opt in ("-v", "--verbose"):
            O["verbose"] = True
        if opt in ("-c", "--check"):
            O["check"] = True
        if opt in ("-a", "--auto"):
            O["auto"] = True
        if opt in ("-x", "--test_full"):
            O["test_full"] = True
        if opt in ("-n", "--noback"):
            O["noback"] = True

    # Do the needful based on opts.
    for opt, arg in opts:
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
        elif opt in ("-u", "--update", "-c", "--check", "-a", "--auto"):
            update_weblgsm()
            return
        elif opt in ("-p", "--passwd"):
            # Technically, needs run in app context.
            app = appmain()
            with app.app_context():
                change_password()
            return
        elif opt in ("-f", "--fetch_json"):
            print("Disabled till can fix to also update imgs")
#            update_gs_list()
            return
        elif opt in ("-t", "--test", "-x", "--test_full"):
            run_tests()
            return
        elif opt in ("-j", "--valid"):
            print(opt)
            print(arg)
            add_valid_gs_user(arg)
            return
        elif opt in ("-d", "--debug") or DEBUG:
            # Put debug last because main.conf var.
            # Just because I have debug set in the conf doesn't mean I want to
            # start the server in debug mode when just trying to run tests or
            # change passwd or something.
            start_debug()
            return


if __name__ == "__main__":
    main(sys.argv[1:])


