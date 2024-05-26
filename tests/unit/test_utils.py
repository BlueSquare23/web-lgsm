import os
import pytest
import json
from app.utils import *

def test_is_invalid_cfg_name():
    gs_cfgs = open('json/accepted_cfgs.json', 'r')
    json_data = json.load(gs_cfgs)
    gs_cfgs.close()

    valid_gs_cfgs = json_data["accepted_cfgs"]
    for cfg in valid_gs_cfgs:
        assert is_invalid_cfg_name(cfg) == False

    invalid_gs_cfgs = ["fart", "blah", 777777, None, "---------"]
    for cfg in invalid_gs_cfgs:
        assert is_invalid_cfg_name(cfg) == True


# For now just test that the cmds in commands.json make it through. Will write
# tests for cmd exemptions another time.
def test_get_commands():
    commands_json = open('json/commands.json', 'r')
    json_data = json.load(commands_json)
    commands_json.close()

    for command in get_commands('mcserver', 'no'):
        assert command.short_cmd in json_data["short_cmds"]
        assert len(command.short_cmd) < 3
        assert command.long_cmd in json_data["long_cmds"]
        assert len(command.long_cmd) >= 4
        assert command.description in json_data["descriptions"]
        assert len(command.description.split()) >= 2    # Count words.


def test_get_servers():
    servers_json = open('json/game_servers.json', 'r')
    json_data = json.load(servers_json)
    servers_json.close()

    servers = get_servers()
    for key in servers:
        assert key in json_data['servers']
        assert len(key.split()) == 1
        # Short server names should NOT contain upppercase letters.
        assert any(x.isupper() for x in key) == False

        assert servers[key] in json_data['server_names']
        # Long server names should contain upppercase letters.
        assert any(x.isupper() for x in servers[key]) == True


def test_is_invalid_command():
    commands_json = open('json/commands.json', 'r')
    json_data = json.load(commands_json)
    commands_json.close()

    valid_cmds = json_data["short_cmds"]
    for cmd in valid_cmds:
        assert is_invalid_command(cmd, 'mcserver', 'yes') == False

    # Send should be invalid when no is supplied to is_invalid_command().
    invalid_cmds = ["fart", "blah", 777777, None, "---------", 'send']
    for cmd in invalid_cmds:
        assert is_invalid_command(cmd, 'mcserver', 'no') == True
    

def test_install_options_are_invalid():
    servers_json = open('json/game_servers.json', 'r')
    json_data = json.load(servers_json)
    servers_json.close()

    # Valid install options.
    for script_name, full_name in zip(json_data["servers"], json_data["server_names"]):
        assert install_options_are_invalid(script_name, full_name) == False

    # Invalid install options.
    servers = ["fart", "blah", 777777, None, "---------"]
    server_names = ["fart", "blah", 777777, None, "---------"]
    for script_name, full_name in zip(servers, server_names):
        assert install_options_are_invalid(script_name, full_name) == True


def script_name_is_invalid():
    servers_json = open('json/game_servers.json', 'r')
    json_data = json.load(servers_json)
    servers_json.close()

    # Valid servers.
    for script_name in json_data["servers"]:
        assert script_name_is_invalid(script_name) == False

    garbage = ["fart", "blah", 777777, None, "---------"]
    for script_name in garbage:
        assert script_name_is_invalid(script_name) == True

def test_contains_bad_chars():
    bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                  "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }

    # Actual bad char.
    for char in bad_chars:
        assert contains_bad_chars(char) == True

    # Perfectly fine chars.
    for char in ['a', '5', 'q', '.', '/', None]:
        assert contains_bad_chars(char) == False


def test_get_network_stats():
    stats = get_network_stats()

    assert isinstance(stats, dict)
    assert 'bytes_sent_rate' in stats
    assert 'bytes_recv_rate' in stats
    assert isinstance(stats['bytes_sent_rate'], float)
    assert isinstance(stats['bytes_recv_rate'], float)

def test_get_server_stats():
    stats = get_server_stats()

    assert isinstance(stats, dict)
    assert 'disk' in stats
    assert 'cpu' in stats
    assert 'mem' in stats
    assert 'network' in stats

    assert isinstance(stats['disk'], dict)
    assert isinstance(stats['cpu'], dict)
    assert isinstance(stats['mem'], dict)
    assert isinstance(stats['network'], dict)

    # Check types of values in 'disk' dictionary
    disk = stats['disk']
    assert isinstance(disk['total'], int)
    assert isinstance(disk['used'], int)
    assert isinstance(disk['free'], int)
    assert isinstance(disk['percent_used'], float)

    # Check types of values in 'cpu' dictionary, excluding 'cpu_usage'
    cpu = stats['cpu']
    assert isinstance(cpu['load1'], float)
    assert isinstance(cpu['load5'], float)
    assert isinstance(cpu['load15'], float)

    # Check type of 'cpu_usage'
    assert isinstance(cpu['cpu_usage'], float)

    # Check types of values in 'mem' dictionary
    mem = stats['mem']
    assert isinstance(mem['total'], int)
    assert isinstance(mem['used'], int)
    assert isinstance(mem['free'], int)
    assert isinstance(mem['percent_used'], float)

    # Check types of values in 'network' dictionary
    network = stats['network']
    assert isinstance(network['bytes_sent_rate'], float)
    assert isinstance(network['bytes_recv_rate'], float)

    # Ensure the result can be serialized to JSON
    json_string = json.dumps(stats)
    assert isinstance(json_string, str)
