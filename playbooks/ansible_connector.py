#!/usr/bin/env python3
# The Web-LGMS Sudo Ansible Connector Script!
# Used as an interface between the web-lgsm app process and its associated
# ansible playbooks. Basically this a standalone wrapper / adapter script for
# the project's ansible playbooks to allow them to be run by the web app
# process. Written by John R. August 2024

import os
import sys
import json
import yaml
import glob
import getopt
import getpass
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

## Globals.
PS = '/usr/bin/ps'
PKILL = '/usr/bin/pkill'
PLAYBOOKS = '/usr/local/share/web-lgsm'  # Playbook dir path.
VENV = '/opt/web-lgsm'  # System venv path.
APP_PATH = ''  # <-- TO ME: REMEMBER TO MAKE EMPTY STRING AGAIN WHEN THIS SCRIPT GET'S UPDATED!

# Import db classes from app.
sys.path.append(APP_PATH)
from app import db
from app.models import GameServer, Job

# Global options hash.
O = {"dry": False, "delete": False}

## Subroutines.

def print_help(msg=None):
    if msg:
        print(msg)
    """Help menu"""
    print(
        f"""Usage: {os.path.basename(__file__)} -i|-x|-d|-c <id> [-h] [-n] 
    Options:
      -h, --help            Show this help message and exit
      -n, --dry             Dry run mode, print only don't run cmd
      -i, --install <id>    Install new game server
      -x, --cancel <id>     Cancel an ongoing installation
      -d, --delete <id>     Delete an installation & its user or a cronjob
      -c, --cron <id>       Cronjob to create or edit
    """
    )
    exit()


def db_fetch(item_id, item_type='GameServer'):
    """
    Connects to app's DB and returns either GameServer or Job object that
    matches item_id.

    Args:
        item_id (str): Id of GameServer|Job obj to fetch.
        item_type (str): Type of object to fetch. Either GameServer or Job.
    Returns:
        GameServer|Job: GameServer or Job object matching ID.
    """
    engine = create_engine('sqlite:///app/database.db')
    
    # Use new db session context.
    # Can't use app context in ansible connector.
    with Session(engine) as session:
        if item_type == 'Job':
            item = session.get(Job, item_id)
        else:
            item = session.get(GameServer, item_id)

        if item == None:
            print("Error: No server with ID found.")
            exit(69)
        return item


def validate_username(username):
    """Checks supplied username is in accepted usernames."""
    yaml_file_path_default = os.path.join(PLAYBOOKS, "playbooks/vars/accepted_usernames.yml")
    yaml_file_path_custom = os.path.join(PLAYBOOKS, "../web-lgsm_custom_users.yml")

    with open(yaml_file_path_default, "r") as file:
        data_default = yaml.safe_load(file)

    if os.path.exists(yaml_file_path_custom):
        with open(yaml_file_path_custom, "r") as file:
            data_custom = yaml.safe_load(file)

    # Extract the accepted_usernames list.
    accepted_usernames = data_default.get("accepted_usernames", [])
    custom_usernames = data_custom.get("custom_usernames", [])

    valid_users = accepted_usernames + custom_usernames

    if username not in valid_users:
        print(" [!] Invalid user!")
        exit(77)


def run_cmd(cmd, exec_dir=os.getcwd()):
    """Main subprocess wrapper function, runs cmds via Popen"""
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=exec_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        for stdout_line in iter(proc.stdout.readline, ""):
            print(stdout_line, end="", flush=True)

        for stderr_line in iter(proc.stderr.readline, ""):
            print(stderr_line, end="", flush=True)

        proc.wait()
        exit_status = proc.returncode

        if exit_status != 0:
            print("\033[91mCommand failed!\033[0m")
            print(f"######### EXIT STATUS: {exit_status}")
            exit(exit_status)

        print(f"Command '{cmd}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with return code {e.returncode}.")
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print(f"Command '{cmd}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred while running '{cmd}': {str(e)}")


def mark_install_failed(server_id):
    """Mark failed with new session context."""
    # Can't use app context in ansible connector.
    engine = create_engine('sqlite:///app/database.db')
    with Session(engine) as session:
        server = session.get(GameServer, server_id)
        server.install_finished = True
        server.install_failed = True
        session.commit()


def post_install_cfg_fix(install_path):
    """Sets up persistent game server cfg files post install"""
    # Find the default and common configs.
    default_cfg = next(
        os.path.join(root, name)
        for root, _, files in os.walk(f"{install_path}/lgsm/config-lgsm")
        for name in files
        if name == "_default.cfg"
    )
    common_cfg = next(
        os.path.join(root, name)
        for root, _, files in os.walk(f"{install_path}/lgsm/config-lgsm")
        for name in files
        if name == "common.cfg"
    )

    # Strip the first 9 lines of warning comments from _default.cfg and write
    # the rest to the common.cfg.
    with open(default_cfg, "r") as default_file, open(common_cfg, "w") as common_file:
        for _ in range(9):
            next(default_file)  # Skip the first 9 lines
        for line in default_file:
            common_file.write(line)

    print("Configuration file common.cgf updated!")


def run_install_new_game_server(server_id):
    """
    Wraps the invocation of the install_new_game_server.yml playbook

    Args:
        server_id (uuid): Id of GameServer to install.
    """
    server = db_fetch(server_id)

    if server.install_finished:
        print("Installation for server already completed!")
        exit(123)

    ansible_cmd_path = os.path.join(VENV, "bin/ansible-playbook")
    install_gs_playbook_path = os.path.join(
        PLAYBOOKS, "playbooks/install_new_game_server.yml"
    )

    sudo_pre_cmd = ["/usr/bin/sudo", "-n"]

    pre_install_cmd = sudo_pre_cmd + [
        ansible_cmd_path,
        install_gs_playbook_path,
        "-e",
        f"username={server.username}",
        "-e",
        f"server_install_path={server.install_path}",
        "-e",
        f"server_script_name={server.script_name}",
    ]

    # Run pre-install playbook.
    if O["dry"]:
        print(pre_install_cmd)
    else:
        run_cmd(pre_install_cmd)

    install_reqs = [f"{server.install_path}/{server.script_name}", "auto-install"]

    # Then run as user to install actual game server.
    user_prepend = sudo_pre_cmd + ["-u", server.username]
    install_cmd = user_prepend + install_reqs

    if O["dry"]:
        print(install_cmd)
    else:
        # Actually run install!
        run_cmd(install_cmd, server.install_path)

        # Post install cfg fix.
        post_install_cfg_fix(server.install_path)

    if O["dry"]:
        print(install_reqs)
        exit()
    else:
        # After game server install, install required apt reqs as root.
        try:
            run_cmd(install_reqs, server.install_path)
        except:
            mark_install_failed(server_id)
            exit()

    # Mark finished with new session context.
    # Can't use app context in ansible connector.
    engine = create_engine('sqlite:///app/database.db')
    with Session(engine) as session:
        server = session.get(GameServer, server_id)
        server.install_finished = True
        server.install_failed = False
        session.commit()

    # Same neon green as default color scheme in ansi escape.
    print("\033[38;2;9;255;0m ✓  Game server successfully installed!\033[0m")
    exit()


def get_script_cmd_from_pid(pid):
    try:
        # Get script name from ps cmd output.
        proc = subprocess.run(
            [PS, "-o", "cmd=", str(pid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        stderr = proc.stderr.strip()
        proc.check_returncode()

        script_path = proc.stdout.strip()

        # If the script path is empty, it might mean the PID does not exist
        if not script_path:
            print(f" [!] Error No script found for PID {pid}")
            exit(23)

        return script_path

    except subprocess.CalledProcessError as e:
        # Handle errors during command execution.
        print(f" [!] Error running ps command: {e}")
        exit(23)

    except ValueError as e:
        # Handle any specific value errors.
        print(e)
        exit(23)

    except Exception as e:
        # Catch any other unforeseen errors.
        print(f" [!] An unexpected error occurred: {str(e)}")
        exit(23)


def cancel_install(pid):
    """
    Cancels a running installation via its pid.

    Args:
        pid (int): pid to kill.
    """
    pid_cmd = get_script_cmd_from_pid(pid)
    self_path = os.path.join(os.getcwd(), __file__)
    self_venv = os.path.join(VENV, 'bin/python')
    self_cmd = f"/usr/bin/sudo -n {self_venv} {self_path}"

    # Validate to ensure only killing instances of own script pid.
    if self_cmd not in pid_cmd:
        print(f"Error: Not allowed to kill pid: {pid}!")
        exit(4)

    cmd = [PKILL, "-P", str(pid)]
    run_cmd(cmd)
    exit()


def run_cron_edit(job_id):
    """
    Handles invocation of cronjob edit playbook.

    Args:
        job_id (str(shortuuid)): Id of job to edit.
    """
    job = db_fetch(job_id, 'Job')
    server = db_fetch(job.server_id)

    ansible_cmd_path = os.path.join(VENV, "bin/ansible-playbook")
    edit_jobs_path = os.path.join(PLAYBOOKS, "playbooks/edit_jobs.yml")

    comment = f"{job.server_id}, {job.id}, {job.comment}"
    job_str = f"{server.install_path}/{server.script_name} {job.command}"
    state = 'absent' if O["delete"] else 'present'

    custom_job_prefix = 'custom: '
    if job.command.startswith(custom_job_prefix):
        job_str = job.command.replace(custom_job_prefix, '')

    cmd = [
        "/usr/bin/sudo",
        "-n",
        ansible_cmd_path,
        edit_jobs_path,
        "-e",
        f"comment='{comment}'",
        "-e",
        f"username={server.username}",
        "-e",
        f"job='{job_str}'",
        "-e",
        f"schedule='{job.expression}'",
        "-e",
        f"state='{state}'",
    ]

    if O["dry"]:
        print(cmd)
        exit()

    run_cmd(cmd)
    exit()


def run_delete_user(server_id):
    """
    Wraps the invocation of the delete_user.yml playbook.

    Args:
       server_id (uuid): Id of server to delete. 
    """
    server = db_fetch(server_id)

    validate_username(server.username)

    ansible_cmd_path = os.path.join(VENV, "bin/ansible-playbook")
    del_user_path = os.path.join(PLAYBOOKS, "playbooks/delete_user.yml")
    cmd = [
        "/usr/bin/sudo",
        "-n",
        ansible_cmd_path,
        del_user_path,
        "-e",
        f"username={server.username}",
    ]

    if O["dry"]:
        print(cmd)
        exit()

    run_cmd(cmd)
    exit()


def run_add_sudoers(username):
    """
    Adds the sudoers rule for the supplied username.
    """
    ansible_cmd_path = os.path.join(VENV, "bin/ansible-playbook")
    add_user_sudoers_rules_playbook_path = os.path.join(
        PLAYBOOKS, "playbooks/add_user_sudoers_rules.yml"
    )

    cmd = [
        "/usr/bin/sudo", "-n",
        ansible_cmd_path,
        add_user_sudoers_rules_playbook_path,
        "-e",
        f"username={username}",
    ]

    if O["dry"]:
        print(cmd)
        exit()

    run_cmd(cmd)
    exit()


# Main.
def main(argv):
    """Process getopts, loads json vars, runs appropriate playbook"""
    try:
        opts, args = getopt.getopt(argv, "hni:x:c:d:u:", ["help", "dry", "install=", "cancel=", "cron=", "delete=", "user="])
    except getopt.GetoptError:
        print_help("Invalid option!")

    # First store global options.
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
        if opt in ("-n", "--dry"):
            O["dry"] = True
        if opt in ("-d", "--delete"):
            O["delete"] = True

    # Then parse opts to determine action.
    for opt, arg in opts:
        if opt in ("-h", "--help", "-n", "--dry"):
            continue

        if opt in ("-i", "--install"):
            run_install_new_game_server(arg)

        if opt in ("-x", "--cancel"):
            cancel_install(arg)

        if opt in ("-c", "--cron"):
            run_cron_edit(arg)

        if opt in ("-d", "--delete"):
            run_delete_user(arg)

        if opt in ("-u", "--user"):
            run_add_sudoers(arg)


    print(" [!] No action taken!")


if __name__ == "__main__":
    main(sys.argv[1:])

