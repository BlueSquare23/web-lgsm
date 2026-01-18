import os
import time
import json
import pytest
import psutil
import getpass
from flask import url_for, request
from game_servers import game_servers
import subprocess
import configparser

from app.models import User, GameServer
from utils import *

def full_game_server_install(client, username=getpass.getuser(), cancel=False):
    response = client.get("/install")
    assert response.status_code == 200
    csrf_token = get_csrf_token(response)

    # TODO: Replace this with info from test json vars. I was lazy and just hardcoded it.
    install_data = {
        "csrf_token": csrf_token,
        "script_name": "mcserver",
        "install_type": "local",
        "install_path": f"/home/{username}/GameServers/Minecraft",
        "install_name": "Minecraft",
        "username": username,
    }

    # Do an install.
    response = client.post(
        "/install",
        data=install_data,
        follow_redirects=True,
    )

    print(extract_alert_messages(response))
#    debug_response(response)

    assert response.status_code == 200
    assert b"Installing" in response.data

    # Some buffer time.
    time.sleep(5)

    server_id = get_server_id("Minecraft")

    if cancel:
        response = client.get(
            f"/install?server_id={server_id}&cancel=true",
            follow_redirects=True,
        )
        assert response.status_code == 200
        alerts = extract_alert_messages(response)
        assert "Installation Canceled!" in alerts
        return

    timeout = 0
    installed_successfully = False

    while True:
        installed_successfully = check_install_finished(server_id)
        if installed_successfully:
            break 

        if timeout >= 360:  # Aka six minutes.
            print("######################## GAME SERVER INSTALL OUTPUT")
            print(f"Install Status: {installed_successfully}")
            print(json.dumps(json.loads(response.data.decode("utf8")), indent=4))
            assert True == False  # Fail test for timeout.

        response = client.get(f"/api/cmd-output/{server_id}")
        assert response.status_code == 200

        if b'Game server successfully installed' in response.data:
            installed_successfully = True
            break

        timeout += 1
        time.sleep(1)

    assert installed_successfully


def game_server_start_stop(client, server_id):
    response = client.get(
        f"/controls?server_id={server_id}",
        follow_redirects=True
    )
    assert response.status_code == 200
    csrf_token = get_csrf_token(response)
    print(csrf_token)

    # Test starting the server.
    response = client.post(
        "/controls",
        data={
            "csrf_token": csrf_token,
            "server_id": server_id,
            "control": 'st',
            "ctrl_form": 'true',
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(2)

    # Check output lines are there.
    response = client.get(f"/api/cmd-output/{server_id}")
    assert response.status_code == 200
    print(response.get_data(as_text=True))

    # Keep checking status till timeout.
    timeout = 60
    runtime = 0
    while True:
        response = client.get(f"/api/server-status/{server_id}")
        assert response.status_code == 200
        resp_dict = response.json
        assert "status" in resp_dict

        if resp_dict["status"] == True:
            break

        time.sleep(10)
        runtime += 10

        if runtime > timeout:
            assert True == False  # Force fail timeout.
    
    # Cant win the race if you're asleep.
    time.sleep(5)

    response = client.get(f"/api/server-status/{server_id}")
    # Assert server status is on.
    assert response.status_code == 200
    resp_dict = response.json
    print(resp_dict)
    assert "status" in resp_dict
    assert resp_dict["status"] == True

    # Enable the send_cmd setting.
    toggle_send_cmd(True)
    time.sleep(1)

    check_main_conf_bool('settings','send_cmd', True)

    # Test sending command to game server console
    response = client.post(
        "/controls",
        data={
            "csrf_token": csrf_token,
            "server_id": server_id,
            "control": 'sd',
            "send_cmd": 'test',
            "send_form": 'true',
        },
        follow_redirects=True
    )

    print(extract_alert_messages(response))
    assert response.status_code == 200
    # From flashed message
    assert b'Sending command to console' in response.data

    time.sleep(5)

    print("######################## SEND COMMAND TO CONSOLE\n")
    # Sleep until process is finished.
    while (
        b'"process_lock": true' in client.get(f"/api/cmd-output/{server_id}").data
    ):
        response = client.get(f"/api/cmd-output/{server_id}")
        print(response.get_data(as_text=True))
        time.sleep(5)

    time.sleep(1)

    response = client.get(f"/api/cmd-output/{server_id}")
    # From json data
    assert b"Sending command to console" in response.data

    time.sleep(15)

    # Test stopping the server
    response = client.post(
        "/controls",
        data={
            "csrf_token": csrf_token,
            "server_id": server_id,
            "control": 'sp',
            "ctrl_form": "true",
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    x = 0
    timeout = 60  # If shutdown takes more than 1 min, something's probably wrong.

    while True:
        # Fail test on timeout.
        if x > timeout:
            assert True == False

        resp = client.get(f"/api/cmd-output/{server_id}").data
        resp_dict = json.loads(resp)
        assert 'stdout' in resp_dict
        print(f'######################## STOP CMD OUTPUT, ATTEMPT #{int(x/5)+1}')
        print(json.dumps(resp_dict, indent=4))

        # Break on status indicator api, is off.
        resp = client.get(f"/api/server-status/{server_id}").data.decode("utf8")
        resp_dict = json.loads(resp)

        if resp_dict['status'] == False:
            break

        time.sleep(5)
        x += 5

    # Final check status indicator api, is off.
    response = client.get(f"/api/server-status/{server_id}")
    resp_dict = response.json
    assert 'status' in resp_dict
    assert resp_dict['status'] == False


def console_output(client):
    server_id = get_server_id("Minecraft")

    # Test starting the server.
    response = client.get(
        f"/controls?server_id={server_id}", follow_redirects=True
    )
    csrf_token = get_csrf_token(response)

    # Start the server
    response = client.post(
        "/controls",
        data={
            "csrf_token": csrf_token,
            "server_id": server_id,
            "control": 'st',
            "ctrl_form": "true",
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(5)

    # Check output lines are there.
    response = client.get(f"/api/cmd-output/{server_id}")
    assert response.status_code == 200
    assert b"stdout" in response.data

    # Check there are stdout output lines and no err lines
    resp_data = json.loads(response.data.decode("utf8"))
    assert len(resp_data["stdout"]) > 0
    assert len(resp_data["stderr"]) == 0

    # Run until "process_lock": false (aka proc stopped).
    while (
        b'"process_lock": true' in client.get(f"/api/cmd-output/{server_id}").data
    ):
        time.sleep(3)

    time.sleep(1)
    assert b'"process_lock": false' in client.get(f"/api/cmd-output/{server_id}").data

    # Simulate front end js console mode.
    # 1. First POST to /api/update-console
    # 2. Next GET /api/cmd-output to check for data

    # Sleep for long enough that some output comes through.
    time.sleep(10)

    response = client.post(
        f"/api/update-console/{server_id}"
    )
    assert response.status_code == 200

    print("######################## START CONSOLE OUTPUT")
    resp_json = client.get(f"/api/cmd-output/{server_id}").data.decode("utf8")
    resp_data = json.loads(resp_json)
    print(resp_json)

    # Just check that some stdout is coming through.
    assert len(resp_data['stdout']) > 0

    time.sleep(10)

    # Stop the server.
    response = client.post(
        "/controls",
        data={
            "csrf_token": csrf_token,
            "server_id": server_id,
            "control": 'sp',
            "ctrl_form": "true",
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(45)

    # Final check status indicator api, is off.
    response = client.get(f"/api/server-status/{server_id}")
    resp_dict = response.json
    assert 'status' in resp_dict
    assert resp_dict['status'] == False


@pytest.mark.integration
def test_install_newuser(db_session, client, authed_client, test_vars):
    """Test install as new user."""
    version = test_vars["version"]

    response = client.get('/settings')
    csrf_token = get_csrf_token(response)
    settings_data = {
        "csrf_token": csrf_token,
        "text_color": "#09ff00",
        "graphs_primary": "#e01b24",
        "graphs_secondary": "#0d6efd",
        "terminal_height": "10",
        "delete_user": "true",
        "remove_files": "true",
        "install_new_user": "true",
        "newline_ending": "true",
        "show_stderr": "true",
        "clear_output_on_reload": "true",
    }

    with client:
        # DEBUGGING...
        edit_main_conf('debug','debug', True)
        edit_main_conf('debug','log_level', 'debug')

        # TODO: This should really be done via editing the conf directly, but
        # ehh this works for now.
        # Change settings.
        error_msg = b"Settings Updated!"
        resp_code = 200
        response = client.post(
            "/settings", data=settings_data, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "main.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf_bool('settings','install_create_new_user', True)
        check_main_conf_bool('settings','remove_files', True)
        check_main_conf_bool('settings','delete_user', True)

        # Test full install as new user.
        full_game_server_install(client, username='mcserver')
        server_id = get_server_id("Minecraft")

        game_server_start_stop(client, server_id)
        console_output(client)

        # Refresh settings again after full server install cause paranoia. (probably unnecessary, am debugging rn)
        response = client.post(
            "/settings", data=settings_data, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "main.settings")
        time.sleep(1)

        check_main_conf_bool('settings','install_create_new_user', True)
        check_main_conf_bool('settings','remove_files', True)
        check_main_conf_bool('settings','delete_user', True)

        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204

        time.sleep(20)  # Allow time for delete job to finish.

        print("##################### Error Log #####################")
        os.system('cat logs/error.log')

        print("##################### Access Log #####################")
        os.system('cat logs/access.log')

        print("##################### Audit Log #####################")
        os.system('cat logs/audit.log')

        print("##################### Home Dirs #####################")
        os.system('ls /home')

        print("##################### Sudoers Rules #####################")
        os.system('sudo -l')

        dir_path = "/home/mcserver"
        assert not os.path.exists(dir_path)

        assert user_exists("mcserver") == False


@pytest.mark.integration
def test_install_sameuser(db_session, client, authed_client, test_vars):
    """Then test install as existing user."""

    # Skip same user install tests for docker. Containers force install new
    # user.
    if "CONTAINER" in os.environ:
        return

    version = test_vars["version"]

    response = client.get('/settings')
    csrf_token = get_csrf_token(response)
    settings_data = {
        "csrf_token": csrf_token,
        "text_color": "#09ff00",
        "graphs_primary": "#e01b24",
        "graphs_secondary": "#0d6efd",
        "terminal_height": "10",
        "delete_user": "false",
        "remove_files": "true",
        "install_new_user": "false",
        "newline_ending": "true",
        "show_stderr": "true",
        "clear_output_on_reload": "true",
    }

    with client:

        # TODO: Yeah said this above too, this needs refactored into a static
        # setup wopaguz. Shouldn't be doing this via post to settings route.
        # But oh well works for now.
        # Change settings.
        error_msg = b"Settings Updated!"
        resp_code = 200
        response = client.post(
            "/settings", data=settings_data, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "main.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf_bool('settings','install_create_new_user', False)

        # Test full install as existing user.
        full_game_server_install(client, username=getpass.getuser())
        server_id = get_server_id("Minecraft")

        game_server_start_stop(client, server_id)
        console_output(client)

        server_id = get_server_id("Minecraft")
        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204


@pytest.mark.integration
def test_install_cancel(db_session, client, authed_client, test_vars):
    """Tests starting and canceling a game server installation."""

    version = test_vars["version"]

    response = client.get('/settings')
    csrf_token = get_csrf_token(response)

    with client:

        # Test full install as existing user.
        full_game_server_install(client, username='mcserver', cancel=True)

        server_id = get_server_id("Minecraft")
        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204



