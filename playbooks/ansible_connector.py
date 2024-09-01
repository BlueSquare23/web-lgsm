#!/usr/bin/env python3
# The Web-LGMS Ansible Connector Script!
# Used as an interface between the web-lgsm app process and its associated
# ansible playbooks. Basically this a standalone wrapper / adapter script for
# the project's ansible playbooks to allow them to be run by the web app
# process. Written by John R. August 2024

import os
import json
import getpass
import subprocess

# Like my dad always said, you gotta come from where yer at!
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(SCRIPTPATH, '..'))
CWD = os.getcwd()

def main():
    json_vars_file = os.path.join(CWD, 'json/ansible_vars.json')
    playbook_vars_data = load_json(json_vars_file)

    if playbook_vars_data.get('action', False) == 'install':
        run_install_new_game_server(playbook_vars_data)

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def run_cmd(cmd, exec_dir=os.getcwd()):
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

        print(f"Command '{cmd}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with return code {e.returncode}.")
        print("Error output:", e.stderr)
    except FileNotFoundError:
        print(f"Command '{cmd}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred while running '{cmd}': {str(e)}")

def run_delete_user():
    pass

def run_create_sudoers_rules():
    pass

def run_install_new_game_server(vars_data):
    # TODO: Probably less of this info can be passed in. Look more closely at
    # these and see what doesn't need to be passed in and can be constructed
    # within the script.
    gs_user = vars_data.get('gs_user')
    install_path = vars_data.get('install_path')
    lgsmsh_path = vars_data.get('lgsmsh_path')
    server_script_name = vars_data.get('server_script_name')
    script_paths = vars_data.get('script_paths')
    sudo_rule_name = vars_data.get('sudo_rule_name')
    web_lgsm_user = vars_data.get('web_lgsm_user')
    same_user = vars_data.get('same_user', False)

    ansible_cmd_path = os.path.join(CWD, 'venv/bin/ansible-playbook')
    install_gs_playbook_path = os.path.join(CWD, 'playbooks/install_new_game_server.yml')

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

    # Actually run install!
    run_cmd(install_cmd, install_path)

    # Cleanup cmd.
#    run_cmd(cmd3)

if __name__ == "__main__":
    main()
