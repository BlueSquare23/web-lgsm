import os
import pytest
import json
from app.utils import *


# Mock current user class.
class ModCurrentUser:
    def __init__(self, role, permissions):
        self.role = role
        self.permissions = permissions


# For now just test that the cmds in commands.json make it through. Will write
# tests for cmd exemptions another time.
def test_get_commands():
    commands_json = open("json/commands.json", "r")
    json_data = json.load(commands_json)
    commands_json.close()

    current_user = ModCurrentUser("admin", json.dumps({"admin": True}))

    for command in get_commands("mcserver", "no", current_user):
        assert command.short_cmd in json_data["short_cmds"]
        assert len(command.short_cmd) < 3
        assert command.long_cmd in json_data["long_cmds"]
        assert len(command.long_cmd) >= 4
        assert command.description in json_data["descriptions"]
        assert len(command.description.split()) >= 2  # Count words.


def test_get_servers():
    servers_json = open("json/game_servers.json", "r")
    json_data = json.load(servers_json)
    servers_json.close()

    servers = get_servers()
    for key in servers:
        assert key in json_data["servers"]
        assert len(key.split()) == 1
        # Short server names should NOT contain upppercase letters.
        assert any(x.isupper() for x in key) == False

        assert servers[key] in json_data["server_names"]
        # Long server names should contain upppercase letters.
        assert any(x.isupper() for x in servers[key]) == True


def test_valid_command():
    commands_json = open("json/commands.json", "r")
    json_data = json.load(commands_json)
    commands_json.close()

    current_user = ModCurrentUser("admin", json.dumps({"admin": True}))

    valid_cmds = json_data["short_cmds"]
    for cmd in valid_cmds:
        assert valid_command(cmd, "mcserver", "yes", current_user) == True

    # Send should be invalid when no is supplied to valid_command().
    invalid_cmds = ["fart", "blah", 777777, None, "---------", "send"]
    for cmd in invalid_cmds:
        assert valid_command(cmd, "mcserver", "no", current_user) == False

    # Test valid & invalid cmds for user.
    permissions = dict()
    permissions["controls"] = ["start", "stop"]
    current_user2 = ModCurrentUser("user", json.dumps(permissions))

    invalid_cmds = json_data["short_cmds"]
    invalid_cmds.remove("st")
    invalid_cmds.remove("sp")

    print(current_user2.permissions)

    for cmd in invalid_cmds:
        assert valid_command(cmd, "mcserver", "no", current_user2) == False

    valid_cmds = ["st", "sp"]
    for cmd in valid_cmds:
        assert valid_command(cmd, "mcserver", "no", current_user2) == True


def test_get_network_stats():
    stats = get_network_stats()

    assert isinstance(stats, dict)
    assert "bytes_sent_rate" in stats
    assert "bytes_recv_rate" in stats
    assert isinstance(stats["bytes_sent_rate"], float)
    assert isinstance(stats["bytes_recv_rate"], float)


def test_get_server_stats():
    stats = get_server_stats()

    assert isinstance(stats, dict)
    assert "disk" in stats
    assert "cpu" in stats
    assert "mem" in stats
    assert "network" in stats

    assert isinstance(stats["disk"], dict)
    assert isinstance(stats["cpu"], dict)
    assert isinstance(stats["mem"], dict)
    assert isinstance(stats["network"], dict)

    # Check types of values in 'disk' dictionary
    disk = stats["disk"]
    assert isinstance(disk["total"], int)
    assert isinstance(disk["used"], int)
    assert isinstance(disk["free"], int)
    assert isinstance(disk["percent_used"], float)

    # Check types of values in 'cpu' dictionary, excluding 'cpu_usage'
    cpu = stats["cpu"]
    assert isinstance(cpu["load1"], float)
    assert isinstance(cpu["load5"], float)
    assert isinstance(cpu["load15"], float)

    # Check type of 'cpu_usage'
    assert isinstance(cpu["cpu_usage"], float)

    # Check types of values in 'mem' dictionary
    mem = stats["mem"]
    assert isinstance(mem["total"], int)
    assert isinstance(mem["used"], int)
    assert isinstance(mem["free"], int)
    assert isinstance(mem["percent_used"], float)

    # Check types of values in 'network' dictionary
    network = stats["network"]
    assert isinstance(network["bytes_sent_rate"], float)
    assert isinstance(network["bytes_recv_rate"], float)

    # Ensure the result can be serialized to JSON
    json_string = json.dumps(stats)
    assert isinstance(json_string, str)
