#!/usr/bin/env python3
# Builds Dockerfile and docker-compose.yml file from templates based on user
# supplied game servers. Saves persistent docker server config data to
# .docker-data.json. Written by John R. September 2024.

import os
import sys
import json
import getopt
from jinja2 import Environment, FileSystemLoader

# Therefore it's all pure feeling, it's completely honest. If you can trace the
# origins of your fear, it will disappear.
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPTPATH)

docker_data = []
docker_data_file = ".docker-data.json"
if os.path.isfile(docker_data_file) and os.access(docker_data_file, os.R_OK):
    with open(docker_data_file, "r") as file:
        docker_data = json.load(file)

with open("json/game_servers.json", "r") as file:
    servers_data = json.load(file)
game_servers = dict(zip(servers_data["servers"], servers_data["server_names"]))

opts = {
    "verbose": True,
    "debug": False,
    "dry": False,
    "name": None,
    "port": None
}


def print_help():
    """Prints help menu"""
    print(
        """
  ╔══════════════════════════════════════════════════════════╗  
  ║ docker-setup.py - Builds docker-compose.yml & Dockerfile ║
  ║                                                          ║
  ║ Usage: docker-setup.py [options]                         ║
  ║                                                          ║
  ║   Options:                                               ║
  ║                                                          ║
  ║   -h, --help          Prints this help menu              ║
  ║   -v, --verbose       Prints more output (default on)    ║
  ║   -d, --debug         Prints new files contents          ║
  ║   -x, --dry           Doesn't actually change files      ║
  ║   -a, --add           Add game server to docker setup    ║
  ║   -n, --name [name]   Game server name                   ║
  ║   -p, --port [int]    Game server port number            ║
  ╚══════════════════════════════════════════════════════════╝
    """
    )
    exit()


def validate_game_server(game_server):
    """
    Check's that the supplied game server name is legit.

    Args:
        game_server (str): Name of game server to add.

    Returns:
        bool: True if game_server name is valid, False otherwise.
    """
    global game_servers

    if game_server in game_servers.values():
        return True
    else:
        return False


def already_in_docker_data(game_server):
    """
    Check's if game_server is already in docker data list to prevent users from
    adding the same game server twice.

    Args:
        game_server (str): Game server to check.

    Returns:
        bool: True game_server in docker data, False otherwise.
    """
    global docker_data

    for item in docker_data:
        if item["long_name"] == game_server:
            return True

    return False


def save_json():
    """
    Saves docker_data json to file.

    Returns:
        None: Doesn't return, just does.
    """
    global docker_data
    global opts

    with open(docker_data_file, 'w') as file:
        json.dump(docker_data, file)

    if opts["verbose"]:
        print(" [*] Game server info updated!")


def gather_info():
    """
    Gathers new game server info either from opt args or directly from stdin by
    prompting user for it.

    Returns:
        None: Simply adds user input to global docker_data structure.
    """
    global docker_data
    global game_servers
    global opts

    if opts["name"] == None:
        game_server = input("Enter game server name: ").strip()
    else:
        game_server = opts["name"]

    if not validate_game_server(game_server):
        print(" [*] Valid game servers:")
        for short_name in game_servers.keys():
            long_name = game_servers[short_name]
            print(f"  -  {long_name}")
        print(" [!] Invalid game server name!")
        print(" [*] Please enter valid game server name!")
        exit(11)

    for short_name in game_servers.keys():
        if game_servers[short_name] == game_server:
            script_name = short_name

    if opts["port"] == None:
        try:
            port = int(input("Server port to expose (int): "))
        except:
            print(" [!] Integers only!")
            exit(13)
    else:
        port = opts["port"]

    if already_in_docker_data(game_server):
        if opts["verbose"]:
            print(" [*] Game server already added. Continuing...")
        return

    context = {
        'short_name': script_name,
        'long_name': game_server,
        'port': port
    }

    docker_data.append(context)
    save_json()


def touch(fname, times=None):
    """Re-implement unix touch in python."""
    with open(fname, 'a'):
        os.utime(fname, times)


def whitelist_install_paths():
    """
    DEPRECATED: NEEDS FIXED.
    Adds install paths to allow list for sudo connector script.
    """
    global docker_data

    install_path_list = os.path.join(SCRIPTPATH, "playbooks/gs_allowed_paths.txt")
    if os.path.isfile(install_path_list):
        os.remove(install_path_list)  # Cleanup any old ones.

    for server in docker_data:
        short_name = server["short_name"]
        install_path = f"/home/{short_name}/GameServers"

        with open(install_path_list, "a") as file:
            file.write(install_path + "\n")


def build_files():
    """
    Builds new Dockerfile & docker-compose.yml file from jinja templates &
    stored docker json data.
    """
    global opts
    global docker_data

    env = Environment(loader=FileSystemLoader('app/templates'))
    docker_compose_template = env.get_template('docker-compose.jinja')
    dockerfile_template = env.get_template('Dockerfile.jinja')
    gid = os.getgid()

    config_file = "main.conf"
    config_local = "main.conf.local"  # Local config override.
    if os.path.isfile(config_local) and os.access(config_local, os.R_OK):
        config_file = config_local

    # Build from templates.
    context = {"servers": docker_data, "gid": gid, "config_file": config_file}
    docker_compose_output = docker_compose_template.render(context)
    dockerfile_output = dockerfile_template.render(context)

    if opts["debug"]:
        print(" [*] New docker-compose.yml contents:")
        print(docker_compose_output)
        print()
        print(" [*] New Dockerfile contents:")
        print(dockerfile_output)

    if not opts["dry"]:
        with open('docker-compose.yml', 'w') as file:
            file.write(docker_compose_output)

        with open('Dockerfile', 'w') as file:
            file.write(dockerfile_output)

        # Touch db file and make sure it has the right perms.
        db_file = 'app/database.db'
        touch(db_file)
        os.chmod(db_file, 0o664)

        whitelist_install_paths()

        if opts["verbose"]:
            print(" [*] New Dockerfile & docker-compose.yml files written!")
            print(" [*] Run the command below to build & start the container:")
            print("         docker-compose up --build")


def main(argv):
    global opts

    try:
        longopts = [
            "help",
            "verbose",
            "debug",
            "dry",
            "add",
            "name=",
            "port=",
        ]
        options, args = getopt.getopt(argv, "hvdxan:p:", longopts)
    except getopt.GetoptError as e:
        print(e)
        print_help()

    # First push required opts to global dict for later use.
    for opt, arg in options:
        if opt in ("-h", "--help"):
            print_help()
        if opt in ("-v", "--verbose"):
            opts["verbose"] = True
        if opt in ("-d", "--debug"):
            opts["debug"] = True
        if opt in ("-x", "--dry"):
            opts["dry"] = True
        if opt in ("-n", "--name"):
            opts["name"] = arg
        if opt in ("-p", "--port"):
            opts["port"] = arg

    # Then act based off options.
    for opt, _ in options:
        if opt in ("-a", "--add"):
            gather_info()

    # Builds new Dockerfile & docker-compose.yml files.
    build_files()


if __name__ == "__main__":
    main(sys.argv[1:])

