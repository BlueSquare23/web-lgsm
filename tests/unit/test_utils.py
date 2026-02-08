import os
import pytest
import json
from app.utils import *
from utils import *

# Mock current user class.
class ModCurrentUser:
    def __init__(self, role, permissions):
        self.role = role
        self.permissions = permissions


def test_get_servers():
    servers_json = open("json/game_servers.json", "r")
    json_data = json.load(servers_json)
    servers_json.close()

    servers = get_servers()
    for short, (long, img) in servers.items():
        assert short in json_data["servers"]
        assert len(short.split()) == 1
        # Short server names should NOT contain upppercase letters.
        assert any(x.isupper() for x in short) == False

        assert servers[short][0] in json_data["server_names"]
        # Long server names should contain upppercase letters.
        assert any(x.isupper() for x in servers[short][0]) == True


# TODO: REPLACE THIS WITH UNIT TESTS FOR NEW CMD_SERVICE CLASS!
#def test_valid_command():
#    commands_json = open("json/commands.json", "r")
#    json_data = json.load(commands_json)
#    commands_json.close()
#
#    current_user = ModCurrentUser("admin", json.dumps({"admin": True}))
#    os.system('cat main.conf.local')
#
#    toggle_send_cmd(True)
#
#    valid_cmds = json_data["short_cmds"]
#    for cmd in valid_cmds:
#        assert valid_command(cmd, "mcserver", current_user) == True
#
#    # Send should be invalid when no is supplied to valid_command().
#    invalid_cmds = ["fart", "blah", 777777, None, "---------", "send"]
#    for cmd in invalid_cmds:
#        assert valid_command(cmd, "mcserver", current_user) == False
#
#    # Test valid & invalid cmds for user.
#    permissions = dict()
#    permissions["controls"] = ["start", "stop"]
#    current_user2 = ModCurrentUser("user", json.dumps(permissions))
#
#    invalid_cmds = json_data["short_cmds"]
#    invalid_cmds.remove("st")
#    invalid_cmds.remove("sp")
#
#    print(current_user2.permissions)
#
#    for cmd in invalid_cmds:
#        assert valid_command(cmd, "mcserver", current_user2) == False
#
#    valid_cmds = ["st", "sp"]
#    for cmd in valid_cmds:
#        assert valid_command(cmd, "mcserver", current_user2) == True
