#!/usr/bin/env python3
# Unattended upgrade script for web-lgsm project.
# Rewritten by John R. Aug 2025.

import os
import sys
import subprocess
import json
import time
import getopt
import shutil
import tarfile

RAW_URL = 'https://raw.githubusercontent.com/BlueSquare23/web-lgsm'
UNINSTALL_URL =  RAW_URL + '/refs/heads/dev-1.8.5/uninstall.sh'
ROOT_INSTALL_URL =  RAW_URL + '/refs/heads/dev-1.8.5/scripts/root_install.sh'
UPDATE_PY_URL =  RAW_URL + '/refs/heads/dev-1.8.5/scripts/update.py'
INSTALL_CONF = '/usr/local/share/web-lgsm/install_conf.json'

# Global options hash.
O = {"quiet": False, "check": False, "auto": False, "noback": False}

def run_command(command, user=None, strict=True):
    """
    Subproces.run wrapper function. For running shell cmds.

    Args:
        command (list): Command to be run
        user (str): User to run as, default None (aka root)
        strict (bool): Raise exceptions on command failures
    """
    if user:
        command = ['sudo', '-u', user] + command

    if not O["quiet"]:
        cmd_str =  " ".join(command)
        print(f" [*] Running command: {cmd_str}")

    result = subprocess.run(
        command, capture_output=True, text=True, env=os.environ
    )

    # Error handling, raise exception on non-zero exits when strict.
    if result.returncode != 0:
        if not O["quiet"] or result.stderr:
            print(f" [x] Command failed (exit {result.returncode}):", file=sys.stderr)
            if result.stderr.strip():
                print(result.stderr.strip(), file=sys.stderr)
        if strict:
            raise subprocess.CalledProcessError(
                result.returncode, command, result.stdout, result.stderr
            )
        return None

    if not O["quiet"]:
        print(result.stdout.strip())

    return result.stdout.strip()


def compare_and_move(src_file, dst_file):
    """Diff's two files and moves src to dst if they differ."""
    file_name = os.path.basename(src_file)
    try:
        with open(src_file, "r") as file1, open(dst_file, "r") as file2:
            src_content = file1.read()
            dst_content = file2.read()

        if src_content != dst_content:
            if not O["quiet"]:
                print(f" [*] Backing up {file_name} to {file_name}.bak")
            shutil.copy(dst_file, dst_file + ".bak")
            shutil.move(src_file, dst_file)
            if not O["quiet"]:
                print(f" [!] File {file_name} JSON updated!")
        else:
            os.remove(src_file)
            if not O["quiet"]:
                print(f" [*] File {file_name} JSON already up to date.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except IOError as e:
        print(f"Error: {e}")


def backup_file(filename):
    if not os.path.isfile(filename):
        if not O["quiet"]:
            print(f" [!] Warning: The file '{filename}' does not exist. No backup created!")
        return None

    epoc = int(time.time())
    backup_filename = f"{filename}.{epoc}.bak"
    os.rename(filename, backup_filename)

    if not O["quiet"]:
        print(f" [*] Backing up {filename} to {backup_filename}")
    return backup_filename


def backup_dir(dirname, tar=False):
    """Back's up directories using shutil.copydirtree, optionally tar's them too"""
    if not os.path.isdir(dirname):
        if not O["quiet"]:
            print(
                f" [!] Warning: The directory '{dirname}' does not exist. No backup created!"
            )
        return None

    epoc = int(time.time())
    backup_dirname = f"{dirname}.{epoc}.bak"
    if not O["quiet"]:
        print(f" [*] Backing up {dirname} to {backup_dirname}")
    shutil.copytree(dirname, backup_dirname)

    if tar:
        tar_filename = f"{backup_dirname}.tar.gz"

        if not O["quiet"]:
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
    run_command(['git', 'fetch', '--quiet'])
    output = run_command(['git', 'status', '-sb'])
    if 'ahead' in output or 'behind' in output:
        return False

    return True


def read_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def update_weblgsm():
    """
    Upgrades the web-lgsm itself.
    """
    conf = read_json_file(INSTALL_CONF);
    app_path = conf['APP_PATH']
    username = conf['USERNAME']

    # Change dir to web-lgsm install path.
    os.chdir(app_path)

    if is_up_to_date():
        if not O["quiet"]:
            print(" [*] Web LGSM already up to date!")
        return

    if not O["quiet"]:
        print(" [!] Update Available!")

    if O["check"]:
        return

    if not O["auto"]:
        resp = input(" [*] Would you like to update now? (y/n): ")
        if resp.lower() != "y":
            exit()

    # TODO: Make chown backups to user.

    # Backup whole web-lgsm folder.
    if not O["noback"]:
        if not O["quiet"]:
            print(" [*] Backing up and tarring, this may take a while...")
        backup_dir(app_path, tar=True)
        backup_file("main.conf")

    uninst_opt = '-h'  # Headless
    if not O["quiet"]:
        print(" [*] Uninstalling old web-lgsm...")
        uninst_opt = '-d'  # Debug

    # Run uninstall.sh.
    uninst_script = '/opt/web-lgsm/bin/uninstall.sh'
    run_command([uninst_script, uninst_opt])

    # Have to write install_conf back to disk.
    os.makedirs('/usr/local/share/web-lgsm')
    with open(INSTALL_CONF, 'w') as json_file:
        json.dump(conf, json_file, indent=4)

    # Fetch new uninstall.sh for future updates / uninstalls.
    os.makedirs('/opt/web-lgsm/bin')
    run_command(['/usr/bin/wget', '-O', uninst_script, UNINSTALL_URL])
    os.chmod(uninst_script, 0o750)

    if not O["quiet"]:
        print(" [*] Installing root components...")

    # Fetch and run new root_install.sh.
    root_inst_script = '/opt/web-lgsm/bin/root_install.sh'
    run_command(['/usr/bin/wget', '-O', root_inst_script, ROOT_INSTALL_URL])
    os.chmod(root_inst_script, 0o750)
    run_command([root_inst_script, '-d'])

    # Fetch new update.py.
    update_py = '/opt/web-lgsm/bin/update.py'
    run_command(['/usr/bin/wget', '-O', update_py, UPDATE_PY_URL])
    os.chmod(update_py, 0o750)

    if not O["quiet"]:
        print(" [*] Pulling update from github...")
    run_command(['git', 'fetch', '--all'], username)
    run_command(['git', 'reset', '--hard', 'origin/master'], username)

    if not O["quiet"]:
        print(" [*] Installing user components...")

    install_script = os.path.join(app_path, 'install.sh')
    run_command([install_script, '--skiproot'], username)

    # Green check!
    if not O["quiet"]:
        print(f" [\033[32m✓\033[0m] Update Complete!")
    return


def print_help():
    """Prints help menu"""
    print(
        """
  ╔══════════════════════════════════════════════════════════╗  
  ║ Usage:  update.py [options]                              ║
  ║                                                          ║
  ║   Options:                                               ║
  ║                                                          ║
  ║   -h, --help          Prints this help menu              ║
  ║   -q, --quiet         No output (for headless)           ║
  ║   -u, --update        Update web-lgsm version            ║
  ║   -c, --check         Check if an update is available    ║
  ║   -n, --noback        Don't backup web-lgsm for updates  ║
  ║   -a, --auto          Run an auto update                 ║
  ╚══════════════════════════════════════════════════════════╝
    """
    )
    exit()


def main(argv):
    try:
        longopts = [
            "help",
            "quiet",
            "update",
            "check",
            "noback",
            "auto",
        ]
        opts, args = getopt.getopt(argv, "hqucna", longopts)
    except getopt.GetoptError as e:
        print(e)
        print_help()

    # Push required opts to global dict.
    for opt, _ in opts:
        if opt in ("-q", "--quiet"):
            O["quiet"] = True
        if opt in ("-c", "--check"):
            O["check"] = True
        if opt in ("-a", "--auto"):
            O["auto"] = True
        if opt in ("-n", "--noback"):
            O["noback"] = True

    # Do the needful based on opts.
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
        elif opt in ("-u", "--update", "-c", "--check", "-a", "--auto"):
            update_weblgsm()
            return
        else:
            print_help()


if __name__ == "__main__":
    main(sys.argv[1:])


