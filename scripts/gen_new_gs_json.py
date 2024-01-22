#!/usr/bin/env python3
# Turns the output of `./linuxgsm.sh list` into a game_servers.json file.
# Written by John R., Jan. 2024.

import os
import sys
import json

# Checks if linuxgsm.sh already exists and if not, wgets it.
def check_and_wget_lgsmsh(lgsmsh):
    if not os.path.isfile(lgsmsh):
        try:
            out = os.popen(f"/usr/bin/wget -O {lgsmsh} https://linuxgsm.sh").read()
            os.chmod(lgsmsh, 0o755)
        except:
            # For debug.
            print(sys.exc_info()[0])

lgsmsh = 'linuxgsm.sh'
check_and_wget_lgsmsh(lgsmsh)

servers_list = os.popen(f"./{lgsmsh} list").read()

short_names = []
long_names = []
gs_mapping = dict()

for line in servers_list.split('\n'):
    if len(line.strip()) == 0:
        continue
    if "serverlist.csv" in line:
        continue
    short_name = line.split()[0]
    long_name = ' '.join(line.split()[1:]).replace("'", "").replace("&", "and")

    short_names.append(short_name)
    long_names.append(long_name)
    gs_mapping[short_name] = long_name

print("Writing new test_data.json file.")
map_json = open("test_data.json", "w")
map_json.write(json.dumps(gs_mapping, indent = 4))
map_json.close()

gs_dict = {
    "servers": short_names,
    "server_names": long_names
}

print("Writing new game_servers.json file.")
gs_json = open("game_servers.json", "w")
gs_json.write(json.dumps(gs_dict, indent = 4))
gs_json.close()

