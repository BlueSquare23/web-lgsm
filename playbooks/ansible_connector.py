#!/usr/bin/env python3
# The Web-LGMS Ansible Connector Script!
# Used as an interface between the web-lgsm app process and its associated
# ansible playbooks. Basically this a standalone wrapper / adapter script for
# the project's ansible playbooks to allow them to be run by the web app
# process. Written by John R. August 2024

import os
import sys
import json
import yaml
import getopt
import getpass
import subprocess

## Globals.
# Plabook dir path.
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(SCRIPTPATH, '..'))
CWD = os.getcwd()
JSON_VARS_FILE = os.path.join(CWD, 'json/ansible_vars.json')

# Global options hash.
O = { "debug": False,
       "keep": False }

## Subroutines.

def print_help():
    """Help menu"""
    print(f"""Usage: {os.path.basename(__file__)}  [-h] [-d] [-k]
    Options:
      -h, --help      Show this help message and exit
      -d, --debug     Debug mode - print only don't run cmd
      -k, --keep      Keep json file, don't delete after run
    """)
    exit()

# Main.
def main(argv):
    """Process getopts, loads json vars, runs appropriate playbook"""
    try:
        opts, args = getopt.getopt(argv, "hdk", ["help", "debug", "keep"])
    except getopt.GetoptError:
        print_help()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
        if opt in ("-d", "--debug"):
            O["debug"] = True
        if opt in ("-k", "--keep"):
            O["keep"] = True

    playbook_vars_data = load_json(JSON_VARS_FILE)

    if playbook_vars_data.get('action') == 'install':
        run_install_new_game_server(playbook_vars_data)
        cleanup()

    if playbook_vars_data.get('action') == 'delete':
        run_delete_user(playbook_vars_data)
        cleanup()

    if playbook_vars_data.get('action') == 'create':
        run_create_sudoers_rules(playbook_vars_data)
        cleanup()

    print(' [!] No action taken! Are you sure you supplied valid json?')

# Cleans up json & exits.
def cleanup(exit_status=0):
    if not O['keep']:
        try:
            os.remove(JSON_VARS_FILE)    
        except OSError as e:
            print(f" [!] An error occurred deleting json: {e}")
            exit(1) 
    exit(exit_status)

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f" [!] Error: The file '{file_path}' was not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f" [!] Error: The file '{file_path}' contains invalid JSON.")
        exit(1)
    except Exception as e:
        print(f" [!] An unexpected error occurred: {e}")
        exit(1)

def run_cmd(cmd, exec_dir=os.getcwd()):
    """Main subprocess wrapper function, runs cmds via Popen"""
    try:
        proc = subprocess.Popen(cmd,
                cwd=exec_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
        )

        for stdout_line in iter(proc.stdout.readline, ""):
            print(stdout_line, end="", flush=True)

        for stderr_line in iter(proc.stderr.readline, ""):
            print(stderr_line, end="", flush=True)

        proc.wait()
        exit_status = proc.returncode

        if exit_status != 0:
            print("\033[91mInstall command failed!\033[0m")
            cleanup(exit_status)

        print(f"Command '{cmd}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with return code {e.returncode}.")
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print(f"Command '{cmd}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred while running '{cmd}': {str(e)}")

def check_required_vars_are_set(vars_dict, required_vars):
    """Checks that required json var values are supplied. DOES NOT VALIDATE
    CONTENT! Just checks that the required var is set."""
    for var in required_vars:
        if vars_dict.get(var) is None:
            print(f" [!] Required var '{var}' is missing from json!")
            cleanup(11)

def validate_gs_user(gs_user):
    yaml_file_path = os.path.join(CWD, 'playbooks/vars/accepted_gs_users.yml')

    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Extract the accepted_gs_users variable into a list.
    accepted_gs_users = data.get('accepted_gs_users', [])

    if gs_user not in accepted_gs_users:
        print(" [!] Invalid user!")
        cleanup(77)

def run_delete_user(vars_data):
    """Wraps the invocation of the delete_user.yml playbook"""
    required_vars = ['gs_user', 'sudo_rule_name']
    check_required_vars_are_set(vars_data, required_vars)

    gs_user = vars_data.get('gs_user')
    validate_gs_user(gs_user)
    sudo_rule_name = vars_data.get('sudo_rule_name')

    ansible_cmd_path = os.path.join(CWD, 'venv/bin/ansible-playbook')
    del_user_path = os.path.join(CWD, 'playbooks/delete_user.yml')
    cmd = [ '/usr/bin/sudo', '-n', ansible_cmd_path, del_user_path,
            '-e', f'sudo_rule_name={sudo_rule_name}',
            '-e', f'gs_user={gs_user}' ]

    if O['debug']:
        print(cmd)
        exit()

    run_cmd(cmd)

def run_create_sudoers_rules(vars_data):
    """Wraps the invocation of the create_sudoers_rules.yml playbook"""
    required_vars = ['gs_user', 'script_paths', 'web_lgsm_user']
    check_required_vars_are_set(vars_data, required_vars)

    gs_user = vars_data.get('gs_user')
    validate_gs_user(gs_user)

    script_paths = vars_data.get('script_paths')
    web_lgsm_user = vars_data.get('web_lgsm_user')

    sudo_rule_name = f'{web_lgsm_user}-{gs_user}'
    ansible_cmd_path = os.path.join(CWD, 'venv/bin/ansible-playbook')
    create_sudoers_rules_playbook_path = os.path.join(CWD, 'playbooks/create_sudoers_rules.yml')

    sudo_pre_cmd = ['/usr/bin/sudo', '-n']

    create_rules_cmd = sudo_pre_cmd + [ ansible_cmd_path,
                      create_sudoers_rules_playbook_path,
                      '-e', f'gs_user={gs_user}',
                      '-e', f'sudo_rule_name={sudo_rule_name}',
                      '-e', f'script_paths={script_paths}',
                      '-e', f'web_lgsm_user={web_lgsm_user}' ]

    if O['debug']:
        print(create_rules_cmd)
        exit()

    run_cmd(create_rules_cmd)

def run_install_new_game_server(vars_data):
    """Wraps the invocation of the install_new_game_server.yml playbook"""
    required_vars = ['gs_user', 'install_path', 'server_script_name',
                     'script_paths', 'web_lgsm_user']
    check_required_vars_are_set(vars_data, required_vars)

    gs_user = vars_data.get('gs_user')
    validate_gs_user(gs_user)

    install_path = vars_data.get('install_path')
    server_script_name = vars_data.get('server_script_name')
    script_paths = vars_data.get('script_paths')
    web_lgsm_user = vars_data.get('web_lgsm_user')
    same_user = vars_data.get('same_user', False)

    sudo_rule_name = f'{web_lgsm_user}-{gs_user}'
    ansible_cmd_path = os.path.join(CWD, 'venv/bin/ansible-playbook')
    install_gs_playbook_path = os.path.join(CWD, 'playbooks/install_new_game_server.yml')
    lgsmsh_path = os.path.join(CWD, f'scripts/linuxgsm.sh')

    sudo_pre_cmd = ['/usr/bin/sudo', '-n']

    pre_install_cmd = sudo_pre_cmd + [ ansible_cmd_path,
                      install_gs_playbook_path,
                      '-e', f'gs_user={gs_user}',
                      '-e', f'install_path={install_path}',
                      '-e', f'lgsmsh_path={lgsmsh_path}',
                      '-e', f'server_script_name={server_script_name}',
                      '-e', f'script_paths={script_paths}',
                      '-e', f'sudo_rule_name={sudo_rule_name}',
                      '-e', f'web_lgsm_user={web_lgsm_user}' ]

    # Set playbook flag to not run user / sudo setup steps.
    if same_user == 'true':
        pre_install_cmd += ['-e', 'same_user=true']

    # Run pre-install playbook.
    run_cmd(pre_install_cmd)

    subcmd1 = sudo_pre_cmd + ['-u', gs_user]
    subcmd2 = [f'{install_path}/{server_script_name}', 'auto-install']
    install_cmd = subcmd1 + subcmd2

    if O['debug']:
        print(install_cmd)
        exit()

    # Actually run install!
    run_cmd(install_cmd, install_path)

    # Post install cfg fix.
    post_install_cfg_fix(install_path, gs_user)

    # Remove temp sudoers rule for new user.
    try:
        os.remove(f'/etc/sudoers.d/{gs_user}-temp-auto-install')
    except OSError as e:
        print(f" [!] An error occurred deleting temp sudoers rule: {e}")

    print(f"\033[92m ✓  Game server successfully installed!\033[0m")

def post_install_cfg_fix(gs_dir, gs_user):
    """Sets up persistent game server cfg files post install"""
    # Find the default and common configs.
    default_cfg = next(os.path.join(root, name) \
        for root, _, files in os.walk(f"{gs_dir}/lgsm/config-lgsm") \
            for name in files if name == "_default.cfg")
    common_cfg = next(os.path.join(root, name) \
        for root, _, files in os.walk(f"{gs_dir}/lgsm/config-lgsm") \
            for name in files if name == "common.cfg")

    # Strip the first 9 lines of warning comments from _default.cfg and write
    # the rest to the common.cfg.
    with open(default_cfg, 'r') as default_file, open(common_cfg, 'w') as common_file:
        for _ in range(9):
            next(default_file)  # Skip the first 9 lines
        for line in default_file:
            common_file.write(line)

    print("Configuration file common.cgf updated!")

if __name__ == "__main__":
    main(sys.argv[1:])
