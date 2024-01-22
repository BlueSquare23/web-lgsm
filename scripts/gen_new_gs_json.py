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

for line in servers_list.split('\n'):
    if len(line.strip()) == 0:
        continue
    if "serverlist.csv" in line:
        continue
    short_names.append(line.split()[0])
    long_names.append(' '.join(line.split()[1:]).strip("'"))

gs_dict = {
    "servers": short_names,
    "server_names": long_names
}

print(json.dumps(gs_dict, indent = 4))

