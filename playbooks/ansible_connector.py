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

# Main.
def main():
    json_vars_file = os.path.join(CWD, 'json/ansible_vars.json')
    playbook_vars_data = load_json(json_vars_file)

    if playbook_vars_data.get('action') == 'install':
        run_install_new_game_server(playbook_vars_data)
        exit()

    if playbook_vars_data.get('action') == 'delete':
        run_delete_user(playbook_vars_data)
        exit()

    if playbook_vars_data.get('action') == 'create':
        run_create_sudoers_rules(playbook_vars_data)
        exit()

    print(' [!] No action taken! Are you sure you supplied valid json?')


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f" [!] Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f" [!] Error: The file '{file_path}' contains invalid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f" [!] An unexpected error occurred: {e}")
        sys.exit(1)


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
            exit(11)


def run_delete_user(vars_data):
    """Wraps the invocation of the delete_user.yml playbook"""
    required_vars = ['gs_user', 'sudo_rule_name']
    check_required_vars_are_set(vars_data, required_vars)

    gs_user = vars_data.get('gs_user')
    sudo_rule_name = vars_data.get('sudo_rule_name')


    ansible_cmd_path = os.path.join(CWD, 'venv/bin/ansible-playbook')
    del_user_path = os.path.join(CWD, 'playbooks/delete_user.yml')
    cmd = [ '/usr/bin/sudo', '-n', ansible_cmd_path, del_user_path,
            '-e', f'sudo_rule_name={sudo_rule_name}',
            '-e', f'gs_user={gs_user}' ]

#    print(cmd)
    run_cmd(cmd)


def run_create_sudoers_rules(vars_data):
    """Wraps the invocation of the create_sudoers_rules.yml playbook"""
    required_vars = ['gs_user', 'sudo_rule_name', 'script_paths', 'web_lgsm_user']
    check_required_vars_are_set(vars_data, required_vars)

    gs_user = vars_data.get('gs_user')
    sudo_rule_name = vars_data.get('sudo_rule_name')
    script_paths = vars_data.get('script_paths')
    web_lgsm_user = vars_data.get('web_lgsm_user')

    ansible_cmd_path = os.path.join(CWD, 'venv/bin/ansible-playbook')
    create_sudoers_rules_playbook_path = os.path.join(CWD, 'playbooks/create_sudoers_rules.yml')

    sudo_pre_cmd = ['/usr/bin/sudo', '-n']

    create_rules_cmd = sudo_pre_cmd + [ ansible_cmd_path,
                      create_sudoers_rules_playbook_path,
                      '-e', f'gs_user={gs_user}',
                      '-e', f'sudo_rule_name={sudo_rule_name}',
                      '-e', f'script_paths={script_paths}',
                      '-e', f'web_lgsm_user={web_lgsm_user}' ]

#    print(create_rules_cmd)
    run_cmd(create_rules_cmd)


def run_install_new_game_server(vars_data):
    """Wraps the invocation of the install_new_game_server.yml playbook"""
    required_vars = ['gs_user', 'install_path', 'server_script_name',
                     'script_paths', 'sudo_rule_name', 'web_lgsm_user']
    check_required_vars_are_set(vars_data, required_vars)

    # TODO: Probably less of this info can be passed in. Look more closely at
    # these and see what doesn't need to be passed in and can be constructed
    # within the script.
    gs_user = vars_data.get('gs_user')
    install_path = vars_data.get('install_path')
    server_script_name = vars_data.get('server_script_name')
    script_paths = vars_data.get('script_paths')
    sudo_rule_name = vars_data.get('sudo_rule_name')
    # TODO: Validate this carefully!!!
    web_lgsm_user = vars_data.get('web_lgsm_user')
    same_user = vars_data.get('same_user', False)

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

    # Actually run install!
    run_cmd(install_cmd, install_path)

    # Cleanup cmd.
#    run_cmd(cmd3)

if __name__ == "__main__":
    main()
