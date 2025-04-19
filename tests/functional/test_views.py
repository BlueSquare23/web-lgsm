import os
import pwd
import time
import json
import pytest
import psutil
from flask import url_for, request
from game_servers import game_servers
import subprocess
import configparser

from app.models import User, GameServer

def debug_response(response):
    """
    Debug helper, just prints all teh things for a response.
    """
    # Debug...
    print(type(response))
    print(response)
    print(response.status_code)
    print(response.headers)
    print(response.data)
    print(response.get_data(as_text=True))

# Checks response contains correct msg.
def check_response(response, msg, resp_code, url):
    # Any request with follow_redirects=True, will have a 200.
    assert response.status_code == resp_code

    # Check redirect by seeing if path changed.
    assert response.request.path == url_for(url)
    assert msg in response.data


def check_main_conf(confstr):
    with open("main.conf.local", "r") as f:
        content = f.read()

    assert confstr in content


def enable_cfg_editor():
    """
    Enable cfg editor setting in config file.
    """
    config = configparser.ConfigParser()
    config.read("main.conf.local")
    config['settings']['cfg_editor'] = 'yes'
    with open("main.conf.local", "w") as configfile:
        config.write(configfile)


def enable_send_cmd():
    """
    Enable send_cmd setting in config file.
    """
    config = configparser.ConfigParser()
    config.read("main.conf.local")
    config['settings']['send_cmd'] = 'yes'
    with open("main.conf.local", "w") as configfile:
        config.write(configfile)


def get_server_id(server_name):
    server = GameServer.query.filter_by(install_name=server_name).first()
#    server = db.session.query.filter_by(install_name=server_name).first()
    return server.id


def check_install_finished(server_id):
    server = GameServer.query.filter_by(id=server_id).first()
    return server.install_finished


### Home Page tests.
# Check basic content matches.
def test_home_content(db_session, client, authed_client, test_vars):
    version = test_vars["version"]

    with client:

        response = client.get("/home")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Installed Servers" in response.data
        assert b"Other Options" in response.data
        assert b"Install a New Game Server" in response.data
        assert b"Add an Existing LGSM Installation" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


# Test home responses.
def test_home_responses(db_session, client, authed_client, test_vars):
    with client:

        response = client.get("/home")
        assert response.status_code == 200  # Return's 200 to GET requests.

        response = client.get("/")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Home Page should only accept GET's.
        response = client.post("/home", data=dict(test=""))
        assert response.status_code == 405  # Return's 405 to POST requests.

        response = client.post("/", data=dict(test=""))
        assert response.status_code == 405  # Return's 405 to POST requests.


### Add page tests.
# Check basic content matches.
def test_add_content(db_session, client, authed_client, test_vars):
    version = test_vars["version"]

    with client:

        response = client.get("/add")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b" Add an Existing LGSM Installation" in response.data
        assert b"Game server is installed locally" in response.data
        assert b"Game server is installed on a remote machine" in response.data
        assert b"Game server is in a docker container" in response.data
        assert b"Installation Title" in response.data
        assert b"Enter a unique name for this install" in response.data
        assert b"Installation directory path" in response.data
        assert b"Enter the full path to the game server directory" in response.data
        assert b"LGSM script name" in response.data
        assert b"Enter the name of the game server script" in response.data
        assert b"Game server system username" in response.data
        assert b"Enter system user game server is installed under" in response.data
        assert b"Remote server's IP address or hostname" in response.data
        assert b"Enter remote server's IP address or hostname" in response.data
        assert b"Submit" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


#    = test_vars[""]

# Test add responses.
def test_add_responses(db_session, client, authed_client, test_vars):
    test_server = test_vars["test_server"]
    test_server_path = test_vars["test_server_path"]
    test_server_name = test_vars["test_server_name"]
    test_remote_host = test_vars["test_remote_host"]

    with client:

        ## Test empty parameters.
        resp_code = 400
        error_msg = b"Missing required form field(s)!"
        response = client.post(
            "/add",
            data={"install_name": "", "install_path": "", "script_name": ""},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": "",
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": test_server,
                "install_path": test_server_path,
                "script_name": "",
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": test_server,
                "install_path": "",
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        ## Test empty parameters.
        resp_code = 400
        error_msg = b"Missing required form field(s)!"

        # Empty install_name.
        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": "",
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        # Empty script_name.
        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": test_server,
                "install_path": test_server_path,
                "script_name": "",
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        # Empty install_path.
        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": test_server,
                "install_path": "",
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        # Empty install_type.
        response = client.post(
            "/add",
            data={
                "install_name": test_server,
                "install_path": test_server_path, 
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        ## Test legit local server add with mock server.
        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": test_server,
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Game server added!" in response.data

        ## Bad char tests.
        # Checks response to see if it contains bad chars msg.
        def contains_bad_chars(response):
            assert response.status_code == 400

            # DEBUG!
#            print(response.data.decode('utf-8'))
#            print('----------------------------------------')

            # Check redirect by seeing if path changed.
            assert response.request.path == url_for("views.add")
            assert "Illegal Character Entered" in response.data.decode('utf-8')

        bad_chars = {
            "$",
            "'",
            '"',
            "\\",
            "#",
            "=",
            "[",
            "]",
            "!",
            "<",
            ">",
            "|",
            ";",
            "{",
            "}",
            "(",
            ")",
            "*",
            ",",
            "?",
            "~",
            "&",
        }

        # Test all three fields on add page reject bad chars.
        for char in bad_chars:
#            print(f"Char: {char}")

#            print(f"Bad install_name")
            response = ''
            response1 = client.post(
                "/add",
                data={
                    "install_type": "local",
                    "install_name": char,
                    "install_path": test_server_path,
                    "script_name": test_server_name,
                },
                follow_redirects=True,
            )

            contains_bad_chars(response1)

            response2 = ''
            response2 = client.post(
                "/add",
                data={
                    "install_type": "local",
                    "install_name": test_server,
                    "install_path": char,
                    "script_name": test_server_name,
                },
                follow_redirects=True,
            )
            contains_bad_chars(response2)

# Will fail bc script_name validation happens first. Keeping for now bc
# refactor of main routes may see validation reordered so this is useful again.
#            response3 = ''
#            response3 = client.post(
#                "/add",
#                data={
#                    "install_type": "local",
#                    "install_name": test_server,
#                    "install_path": test_server_path,
#                    "script_name": char,
#                },
#                follow_redirects=True,
#            )
#            contains_bad_chars(response3)
#

        ## Test install already exists.
        # Do a legit server add.
        response4 = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": test_server,
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
        )

        assert response4.status_code == 400
        assert b"An installation by that name already exits." in response4.data

        ## Test legit remote server add with mock server details.
        response = client.post(
            "/add",
            data={
                "install_type": "remote",
                "install_name": test_server + '2',
                "install_path": test_server_path,
                "script_name": test_server_name,
                "install_host": test_remote_host,
            },
            follow_redirects=True,
        )
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200
        assert b'Game server added' in response.data

        ## Test legit docker server add with mock server details.
        response = client.post(
            "/add",
            data={
                "install_type": "docker",
                "install_name": test_server + '3',
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200
        assert b'Game server added' in response.data


### Controls page tests.
# Check basic content matches.
def test_controls_content(db_session, client, authed_client, add_mock_server, test_vars):
    version = test_vars["version"]
    test_server = test_vars["test_server"]

    with client:

        # Test redirect for backward compat works.
        response = client.get(f"/controls?server={test_server}")

        # Debug...
#        print(type(response))
#        print(response)
#        print(response.status_code)
#        print(response.headers)
#        print(response.data)
#        print(response.get_data(as_text=True))

#        assert response.status_code == 302  # Return's 200 to GET requests.
#        loc_header = response.headers.get('Location')
#        server_id = loc_header.split('server_id=')[1]
        server_id = get_server_id(test_server)
        

        response = client.get(f"/controls?server_id={server_id}")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check string on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Output:" in response.data
        assert f"Server Controls for: {test_server}".encode() in response.data
        assert b"Top" in response.data
        assert b"Delete Server" in response.data
        assert b"" in response.data

        # Check all cmds are there.
        short_cmds = ["st", "sp", "r", "m", "ta", "dt", "pd", "ul", "u", "b", "c"]
        for cmd in short_cmds:
            assert f"{cmd}".encode() in response.data

        long_cmds = [
            "start",
            "stop",
            "restart",
            "monitor",
            "test-alert",
            "details",
            "postdetails",
            "update-lgsm",
            "update",
            "backup",
            "console",
        ]
        for cmd in long_cmds:
            assert f"{cmd}".encode() in response.data

        # Check descriptions are all there.
        descriptions = [
            "Start the server.",
            "Stop the server.",
            "Restart the server.",
            "Check server status and restart if crashed.",
            "Send a test alert.",
            "Display server information.",
            "Post details to termbin.com (removing passwords).",
            "Check and apply any LinuxGSM updates.",
            "Check and apply any server updates.",
            "Create backup archives of the server.",
            "Access server console.",
        ]

        for description in descriptions:
            assert f"{description}".encode() in response.data

        assert f"Web LGSM - Version: {version}".encode() in response.data

        # Test send_cmd setting (disabled by default).
        assert response.status_code == 200  # Return's 200 to GET requests.
        assert b"Send command to game server console" not in response.data

        # Enable the send_cmd setting.
#        os.system("sed -i 's/send_cmd = no/send_cmd = yes/g' main.conf.local")

        # Enable send_cmd setting in config file.
        config = configparser.ConfigParser()
        config.read("main.conf.local")
        config['settings']['send_cmd'] = 'yes'
        with open("main.conf.local", "w") as configfile:
            config.write(configfile)

        os.system("cat main.conf.local")

        # Check send cmd is there after main.conf.local setting is enabled.
        server_id = get_server_id(test_server)
        response = client.get(f"/controls?server_id={server_id}")

        # DEBUG
        print(response.data.decode('utf8'))
        assert response.status_code == 200  # Return's 200 to GET requests.
        # TODO: These first two tests are bad. Should use html element as a
        # whole for all str matching tests.
        assert b"sd" in response.data
        assert b"send" in response.data
        assert b"Send command to game server console" in response.data


        # Set it back to default state for sake of idempotency.
        config['settings']['send_cmd'] = 'no'
        with open("main.conf.local", "w") as configfile:
            config.write(configfile)

        # Set it back to default state for sake of idempotency.
#        os.system("sed -i 's/send_cmd = yes/send_cmd = no/g' main.conf.local")


# Test add responses.
def test_controls_responses(db_session, client, authed_client, add_mock_server, test_vars):
    test_server = test_vars["test_server"]
    test_server_path = test_vars["test_server_path"]

    with client:
        server_id = get_server_id(test_server)

        ## Test no params.
        response = client.get(f"/controls", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"No server specified!" in response.data

        ## Test empty server name.
        response = client.get(f"/controls?server=", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"No server specified!" in response.data

        ## Test invalid server name.
        response = client.get(f"/controls?server=Blah", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Invalid game server name!" in response.data

        ## Test No game server installation directory error.
        # First move the installation directory to .bak.
        os.system(f"mv {test_server_path} {test_server_path}.bak")

        # Then test going to the game server dir.
        response = client.get(f"/controls?server_id={server_id}", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"No game server installation directory found!" in response.data

        # Finally move the installation back into place.
        os.system(f"mv {test_server_path}.bak {test_server_path}")

        # New test by ID.
        server_id = get_server_id(test_server)
        response = client.get(f"/controls?server_id={server_id}", follow_redirects=True)

        ## Test empty server name.
        response = client.get(f"/controls?server_id=", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Invalid game server id!" in response.data

        ## Test invalid server name.
        response = client.get(f"/controls?server_id=Blah", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Invalid game server id!" in response.data

        ## Test No game server installation directory error.
        # First move the installation directory to .bak.
        os.system(f"mv {test_server_path} {test_server_path}.bak")

        # Then test going to the game server dir.
        response = client.get(f"/controls?server_id={server_id}", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"No game server installation directory found!" in response.data

        # Finally move the installation back into place.
        os.system(f"mv {test_server_path}.bak {test_server_path}")

        ### Controls Page POST Request test (should only accept GET's).
        response = client.post("/controls", data=dict(test=""))
        assert response.status_code == 405  # Return's 405 to POST requests.


### Install Page tests.
# Test install page content.
def test_install_content(db_session, client, authed_client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]
    version = test_vars["version"]

    with client:
        response = client.post(
            "/login", data={"username": username, "password": password}
        )
        assert response.status_code == 302

        ## Check basic content matches.
        response = client.get("/install")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Install a New LGSM Server" in response.data

        # Compares against game_servers dictionary file.
        for script_name, full_name in game_servers.items():
            assert script_name.encode() in response.data
            assert full_name.encode() in response.data

        assert b"Top" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


# Test install page responses.
def test_install_responses(db_session, client, authed_client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]

    with client:
        response = client.post(
            "/login", data={"username": username, "password": password}
        )
        assert response.status_code == 302

        ## Leaving off legit install test(s) for now because that takes a
        # while to run. Only testing bad posts atm.

        ## Test for Missing Required Form Feild error msg.

        # Test for no feilds supplied.
        resp_code = 200
        error_msg = b"Missing Required Form Field!"
        response = client.post("/install", follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.install")

        # Test no server_name.
        response = client.post(
            "/install", data={"full_name": "", "sudo_pass": ""}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.install")

        # Test no full_name.
        response = client.post(
            "/install", data={"server_name": "", "sudo_pass": ""}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.install")

        # Test for empty form fields.
        error_msg = b"Invalid Installation Option(s)!"
        response = client.post(
            "/install",
            data={"server_name": "", "full_name": "", "sudo_pass": ""},
            follow_redirects=True,
        )

        check_response(response, error_msg, resp_code, "views.install")


### Settings page tests.
# Test settings page content.
def test_settings_content(db_session, client, authed_client, test_vars):
    version = test_vars["version"]

    with client:

        # GET Request tests.
        response = client.get("/settings")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Web LGSM Settings" in response.data
        assert b"Output Text Color" in response.data
        assert b"Stats Primary Color" in response.data
        assert b"Stats Secondary Color" in response.data
        assert b"Remove game server files on delete" in response.data
        assert b"Leave game server files on delete" in response.data
        assert (
            b"Setup new system user when installing new game servers" in response.data
        )
        assert b"Install new game servers under the " in response.data
        assert b"Show Live Server Stats on Home Page" in response.data
        assert b"Check for and update the Web LGSM" in response.data
        assert (
            b"Note: Checking this box will restart your Web LGSM instance"
            in response.data
        )
        assert b"Apply" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


# Test settings page responses.
def test_settings_responses(db_session, client, authed_client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]

    with client:

        # Text color change tests.
        # Only accepts hexcode as text color.
        resp_code = 200
        error_msg = b"Invalid text color!"
        response = client.post(
            "/settings", data={"text_color": "test"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"text_color": "red"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"text_color": "#aaaaaaaaaaaaaaaa"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        error_msg = b"Invalid primary color!"
        response = client.post(
            "/settings", data={"graphs_primary": "test"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"graphs_primary": "red"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings",
            data={"graphs_primary": "#aaaaaaaaaaaaaaaa"},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.settings")

        error_msg = b"Invalid secondary color!"
        response = client.post(
            "/settings", data={"graphs_secondary": "test"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"graphs_secondary": "red"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings",
            data={"graphs_secondary": "#aaaaaaaaaaaaaaaa"},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Legit color change test.
        error_msg = b"Settings Updated!"
        text_color = "#0ed0fc"
        response = client.post(
            "/settings", data={"text_color": text_color}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf(f"text_color = {text_color}")

        # Test install as new user settings.
        error_msg = b"Settings Updated!"
        response = client.post(
            "/settings", data={"install_new_user": "false"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")
        # Check changes are reflected in main.conf.local.
        check_main_conf("install_create_new_user = no")

        response = client.post(
            "/settings", data={"install_new_user": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")
        # Check changes are reflected in main.conf.local.
        check_main_conf("install_create_new_user = yes")

        # Check nonsense input has no effect.
        response = client.post(
            "/settings",
            data={"install_new_user": "sneeeeeeeeeeeeeeeeee"},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.settings")
        check_main_conf("install_create_new_user = yes")

        # Test text area height change.
        # App only accepts terminal height between 5 and 100.
        error_msg = b"Invalid Terminal Height!"
        response = client.post(
            "/settings", data={"terminal_height": "-20"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"terminal_height": "test"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"terminal_height": "99999"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.post(
            "/settings", data={"terminal_height": "-e^(i*3.14)"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Legit terminal height test.
        error_msg = b"Settings Updated!"
        response = client.post(
            "/settings", data={"terminal_height": "10"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf("terminal_height = 10")


### API system-usage tests.

def test_system_usage(db_session, client, authed_client, test_vars):
    """
    Test system usage content & responses.
    """
    with client:

        response = client.get("/api/system-usage")

        # Test json can be de-serialized to python dict.
        resp_json = response.data.decode()
        assert isinstance(resp_json, str)
        system_usage_data = json.loads(resp_json)
        assert isinstance(system_usage_data, dict)

        # Check json data is of appropriate form.
        assert "disk" in system_usage_data
        assert "cpu" in system_usage_data
        assert "mem" in system_usage_data
        assert "network" in system_usage_data

        assert isinstance(system_usage_data["disk"], dict)
        assert isinstance(system_usage_data["cpu"], dict)
        assert isinstance(system_usage_data["mem"], dict)
        assert isinstance(system_usage_data["network"], dict)

        # Check types of values in 'disk' dictionary.
        disk = system_usage_data["disk"]
        assert isinstance(disk["total"], int)
        assert isinstance(disk["used"], int)
        assert isinstance(disk["free"], int)
        assert isinstance(disk["percent_used"], float)

        # Check types of values in 'cpu' dictionary, excluding 'cpu_usage'.
        cpu = system_usage_data["cpu"]
        assert isinstance(cpu["load1"], float)
        assert isinstance(cpu["load5"], float)
        assert isinstance(cpu["load15"], float)

        # Check type of 'cpu_usage'
        assert isinstance(cpu["cpu_usage"], float)

        # Check types of values in 'mem' dictionary.
        mem = system_usage_data["mem"]
        assert isinstance(mem["total"], int)
        assert isinstance(mem["used"], int)
        assert isinstance(mem["free"], int)
        assert isinstance(mem["percent_used"], float)

        # Check types of values in 'network' dictionary.
        network = system_usage_data["network"]
        assert isinstance(network["bytes_sent_rate"], float)
        assert isinstance(network["bytes_recv_rate"], float)


### Edit page tests.
def test_edit_content(db_session, client, authed_client, add_mock_server, test_vars):
    """
    Test edit page basic content.
    """
    test_server = test_vars["test_server"]
    cfg_path = test_vars["cfg_path"]
    version = test_vars["version"]
    server_id = get_server_id(test_server)

    with client:
        payload={"server_id": server_id, "cfg_path": cfg_path}
        print(f"Payload: {payload}")

        # Default should be cfg_editor off, so page should 302 to home.
        response = client.post(
            "/edit", data=payload
        )
#        print(response.data.decode('utf-8'))
        assert response.status_code == 302

        enable_cfg_editor()
#        os.system("cat main.conf.local")  # Debug

        # Basic page load test.
        response = client.get(
            "/edit", data={"server_id": server_id, "cfg_path": cfg_path}
        )
        assert response.status_code == 200

#        print(response.get_data(as_text=True))  # Debug

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Editing Config: common.cfg" in response.data
        assert b"Full Path: " in response.data
        assert b"#### Game Server Settings ####" in response.data
        assert b"#### Testing..." in response.data
        assert b"Save File" in response.data
        assert b"Download Config File" in response.data
        assert b"Back to Controls" in response.data
        assert b"Please note," in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


def test_edit_responses(db_session, client, authed_client, add_mock_server, test_vars):
    """
    Test edit page responses.
    """
    test_server = test_vars["test_server"]
    cfg_path = os.path.join(os.getcwd(), test_vars["cfg_path"])
    test_server_path = os.path.join(os.getcwd(), test_vars["test_server_path"])

    version = test_vars["version"]
    server_id = get_server_id(test_server)

    with client:
        enable_cfg_editor()

        ## Edit testing.
        # Test if edits are saved.
        response = client.post(
            "/edit",
            data={
                "server_id": server_id,
                "cfg_path": cfg_path,
                "file_contents": "#### Testing...",
            },
        )
        assert response.status_code == 200

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Editing Config: common.cfg" in response.data
        assert b"Full Path: " in response.data
        assert b"#### Testing..." in response.data
        assert b"Save File" in response.data
        assert b"Download Config File" in response.data
        assert b"Back to Controls" in response.data
        assert b"Please note," in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data

        ## Download testing.
        response = client.post(
            "/edit",
            data={"server_id": server_id, "cfg_path": cfg_path, "download": "yes"},
        )
        assert response.status_code == 200

        # No server specified tests.
        resp_code = 200
        error_msg = b"No server specified!"
        # Test is none.
        response = client.post(
            "/edit", data={"cfg_path": cfg_path}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test is null.
        response = client.post(
            "/edit", data={"server_id": "", "cfg_path": cfg_path}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No cfg specified tests.
        error_msg = b"No config file specified!"
        # Test is none.
        response = client.post(
            "/edit", data={"server_id": server_id}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test is null.
        response = client.post(
            "/edit", data={"server_id": server_id, "cfg_path": ""}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Invalid game server name test.
        error_msg = b"Invalid game server id!"
        response = client.post(
            "/edit",
            data={"server_id": "test", "cfg_path": cfg_path},
            follow_redirects=True,
        )
        debug_response(response)
        check_response(response, error_msg, resp_code, "views.home")

        # No game server installation directory found test.
        # First move the installation directory to .bak.
        os.system(f"mv {test_server_path} {test_server_path}.bak")

        error_msg = b"No such file"
        response = client.post(
            "/edit",
            data={"server_id": server_id, "cfg_path": cfg_path},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Finally move the installation back into place.
        os.system(f"mv {test_server_path}.bak {test_server_path}")

        # Invalid config file name test.
        error_msg = b"Invalid config file name!"
        response = client.post(
            "/edit",
            data={"server_id": server_id, "cfg_path": cfg_path + "test"},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No such file test.
        error_msg = b"No such file!"
        response = client.post(
            "/edit",
            data={"server_id": server_id, "cfg_path": "/test" + cfg_path},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")


def test_new_user_has_no_permissions(client, user_authed_client_no_perms, test_vars):
    """
    Test's that the new user cannot do anything in the web interface yet,
    except login.
    """
    test_server = test_vars["test_server"]
    with client:

        server_id = get_server_id(test_server)

        # Test edit_user page. Should never be allowed with or without perms.
        resp_code = 200
        error_msg = b"Only Admins are allowed to edit users"
        response = client.get(
            "/edit_users", data={"username": "newuser"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test install page.
        response = client.get("/install", follow_redirects=True)
        error_msg = b"Your user does NOT have permission access the install page"
        check_response(response, error_msg, resp_code, "views.home")

        # Test add page.
        response = client.get("/add", follow_redirects=True)
        error_msg = b"Your user does NOT have permission access the add page"
        check_response(response, error_msg, resp_code, "views.home")

        # Test delete api.
        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
#        print(response.get_data(as_text=True))
        error_msg = "Insufficient permission to delete Mockcraft"
        assert error_msg in response.get_data(as_text=True)

        # Test settings page.
        response = client.get("/settings", follow_redirects=True)
        error_msg = b"Your user does NOT have permission access the settings page"
        check_response(response, error_msg, resp_code, "views.home")

        # Test game server controls page.
        response = client.get(f"/controls?server_id={server_id}", follow_redirects=True)
        error_msg = b"Your user does NOT have permission access this game server"
        print(response.get_data(as_text=True))
#        print(response.data.decode("utf-8"))
        check_response(response, error_msg, resp_code, "views.home")


def test_enable_new_user_perms(db_session, client, authed_client, add_second_user_no_perms, test_vars):
    test_server = test_vars["test_server"]

    with client:

        server_id = get_server_id(test_server)

        response = client.get("/edit_users?username=newuser")
        assert response.status_code == 200

        create_user_json = f"""{{
            "selected_user": "test2",
            "username": "test2",
            "is_admin": "false",
            "change_user_pass": "false",
            "install_servers": "true",
            "add_servers": "true",
            "mod_settings": "true",
            "edit_cfgs": "true",
            "delete_server": "true",
            "controls": [
                "start",
                "stop",
                "restart",
                "monitor",
                "test-alert",
                "details",
                "postdetails",
                "update-lgsm",
                "update",
                "backup",
                "console",
                "send"
            ],
            "server_ids": ["{server_id}"]
        }}"""

        response = client.post(
            "/edit_users", data=json.loads(create_user_json), follow_redirects=True
        )
        assert response.request.path == url_for("auth.edit_users")
#        print(response.data.decode("utf-8"))
        assert b"User test2 Updated" in response.data


def test_new_user_has_ALL_permissions(client, user_authed_client_all_perms, test_vars):
    """
    Test's that the new user can do anything in the web interface.
    """
    test_server = test_vars["test_server"]
    test_server_name = test_vars["test_server_name"]
    test_server_path = test_vars["test_server_path"]

    with client:

        server_id = get_server_id(test_server)

        # Test edit_user page. Should never be allowed with or without perms.
        resp_code = 200
        error_msg = b"Only Admins are allowed to edit users"
        response = client.get(
            "/edit_users", data={"username": "newuser"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test install page.
        response = client.get("/install", follow_redirects=True)
        msg = b"Install a New LGSM Server"
        check_response(response, msg, resp_code, "views.install")

        # Test delete page.
        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204

        # Test delete message pops up after delete
        response = client.get(f"/home", follow_redirects=True)
        msg = b"Game server, Mockcraft deleted"
        check_response(response, msg, resp_code, "views.home")

        # Test add page.
        response = client.get("/add", follow_redirects=True)
        msg = b"Add an Existing LGSM Installation"
        check_response(response, msg, resp_code, "views.add")

        ## Test legit server add.
        response = client.post(
            "/add",
            data={
                "install_type": 'local',
                "install_name": test_server,
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
#        print(response.data.decode('utf-8'))

        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Game server added!" in response.data

        server_id = get_server_id(test_server)
        print(server_id)

        # Test game server controls page.
        response = client.get(f"/controls?server_id={server_id}", follow_redirects=True)
        msg = b"Server Controls for: Mockcraft"
        check_response(response, msg, resp_code, "views.controls")

        # Test settings page.
        response = client.get("/settings", follow_redirects=True)
        msg = b"Web LGSM Settings"
        check_response(response, msg, resp_code, "views.settings")


def test_delete_game_server(add_mock_server, client, authed_client, test_vars):
    test_server = test_vars["test_server"]

    with client:

        server_id = get_server_id(test_server)

        # API delete.
        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204

        # Test delete message pops up after delete
        response = client.get(f"/home", follow_redirects=True)
        msg = b"Game server, Mockcraft deleted"
        check_response(response, msg, 200, "views.home")


def test_delete_new_user(add_second_user_no_perms, client, authed_client, test_vars):
    username = test_vars["username"]
    with client:

        # Make sure can't do certain delete options first.
        resp_code = 200
        error_msg = b"Can&#39;t delete user that doesn&#39;t exist yet"
        response = client.get(
            "/edit_users?username=newuser&delete=true", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "auth.edit_users")

        error_msg = b"Cannot delete currently logged in user"
        response = client.get(
            f"/edit_users?username={username}&delete=true", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "auth.edit_users")

        # TODO: Make test for this. Rn, this test doesn't work because above case block it.
        #        error_msg = b"Cannot delete main admin user"
        #        response = client.get(f'/edit_users?username={username}&delete=true', follow_redirects=True)
        #        check_response(response, error_msg, resp_code, 'auth.edit_users')

        # Do a legit user delete.
        response = client.get(
            "/edit_users?username=test2&delete=true", follow_redirects=True
        )
        assert response.status_code == 200
        assert b"User test2 deleted" in response.data


def full_game_server_install(client):
    # Do an install.
    response = client.post(
        "/install",
        data={"server_name": "mcserver", "full_name": "Minecraft"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Installing" in response.data

    # Some buffer time.
    time.sleep(5)

    server_id = get_server_id("Minecraft")

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
    # Test starting the server.
    response = client.get(
        f"/controls?server_id={server_id}&command=st", follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(5)

    # Check output lines are there.
    response = client.get(f"/api/cmd-output/{server_id}")
    assert response.status_code == 200
    print(response.get_data(as_text=True))

    # TODO: Fix this, almost certainly this test does nothing atm.
    ## Check that the output lines are not empty.
    #empty_resp = '{"stdout": [""], "pid": false, "process_lock": false}'
    #json_data = json.loads(response.data.decode("utf8"))
    #assert empty_resp != json.dumps(json_data)

    # Test starting the server.
    response = client.get(
        f"/controls?server_id={server_id}&command=st", follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(5)

    # Sleep until process is finished.
    while (b'"process_lock": true' in client.get(f"/api/cmd-output/{server_id}").data):
        time.sleep(5)

    # Can win the race if you're asleep.
    time.sleep(10)

# Things have changed, disabling for now.
#    assert b'"process_lock": false' in client.get(f"/api/cmd-output/{server_id}").data
#    print(client.get("/api/cmd-output?server=Minecraft").data.decode("utf8"))

    #    print("######################## Minecraft Start Log\n")
    #    os.system("cat Minecraft/logs/script/mcserver-script.log")
    #    os.system("cat Minecraft/log/server/latest.log")
    #    os.system("cat Minecraft/log/console/mcserver-console.log")

    # Check status indicator api json.
#    resp = client.get(f"/api/server-status/{server_id}").data.decode("utf8")
#    print(resp)
#    resp_dict = json.loads(resp)
#    assert resp_dict['status'] == True

    # Enable the send_cmd setting.
    enable_send_cmd()

    # Test sending command to game server console
    response = client.get(
        f"/controls?server_id={server_id}&command=sd&cmd=test", follow_redirects=True
    )
    assert response.status_code == 200
    time.sleep(1)

    # Sleep until process is finished.
    while (
        b'"process_lock": true' in client.get(f"/api/cmd-output/{server_id}").data
    ):
        time.sleep(3)

    time.sleep(1)

    assert (
        b"Sending command to console"
        in client.get(f"/api/cmd-output/{server_id}").data
    )

    time.sleep(1)

    # Test stopping the server
    response = client.get(
        f"/controls?server_id={server_id}&command=sp", follow_redirects=True
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
    resp = client.get(f"/api/server-status/{server_id}").data.decode("utf8")
    resp_dict = json.loads(resp)
    assert resp_dict['status'] == False


def console_output(client):
    server_id = get_server_id("Minecraft")

    # Test starting the server.
    response = client.get(
        f"/controls?server_id={server_id}&command=st", follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(5)

    # Check output lines are there.
    response = client.get(f"/api/cmd-output/{server_id}")
    assert response.status_code == 200
    assert b"stdout" in response.data

    # Check that the output lines are not empty.
    # TODO: Use proper dict instead of string for tests like this. Pretty sure
    # rn, this test is broken cause there's no stderr, which should be there
    # too. If it was a dict and then comparing the two dicts would be easier.
    empty_resp = '{"stdout": [""], "pid": false, "process_lock": false}'
    json_data = json.loads(response.data.decode("utf8"))
    assert empty_resp != json.dumps(json_data)

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

    # Cleanup
#    os.system("sudo -n killall -9 java")


def user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

# TODO: These tests and their supporting functions are too big. Too much all in
# one test. They need broken up and tested more modularly and or moved into
# their own sorta "integration tests" file.
def test_install_newuser(db_session, client, authed_client, test_vars):
    """Test install as new user."""
    version = test_vars["version"]

    with client:

        # Change settings.
        error_msg = b"Settings Updated!"
        resp_code = 200
        response = client.post(
            "/settings", data={"install_new_user": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf("install_create_new_user = yes")

        # Test full install as new user.
        full_game_server_install(client)
        server_id = get_server_id("Minecraft")

        game_server_start_stop(client, server_id)
        console_output(client)

        response = client.post(
            "/settings", data={"delete_files": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Stop the server.
        response = client.get(
            f"/controls?server_id={server_id}&command=sp", follow_redirects=True
        )
        assert response.status_code == 200

        # Run until "process_lock": false (aka proc stopped).
        while (
            b'"process_lock": true'
            in client.get(f"/api/cmd-output/{server_id}").data
        ):
            time.sleep(3)

        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204

        dir_path = "/home/mcserver"
        i = 0
        while os.path.exists(dir_path):
            # hacky timeout.
            if i > 10:
                assert True == False
            print(f"{dir_path} exists. Checking again in 1 second...")
            time.sleep(1)
            i += 1
        assert not os.path.exists(dir_path)

    # Will pass for both newuser and sameuser installs.
    assert user_exists("mcserver") == False


def test_install_sameuser(db_session, client, authed_client, test_vars):
    """Then test install as existing user."""

    # Skip same user install tests for docker. Containers force install new
    # user.
    if "CONTAINER" in os.environ:
        return

    version = test_vars["version"]

    with client:

        # Change settings.
        error_msg = b"Settings Updated!"
        resp_code = 200
        response = client.post(
            "/settings", data={"install_new_user": "false"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf("install_create_new_user = no")

        # Test full install as existing user.
        full_game_server_install(client)
        server_id = get_server_id("Minecraft")

        game_server_start_stop(client, server_id)
        console_output(client)

        server_id = get_server_id("Minecraft")
        response = client.post(
            "/settings", data={"delete_files": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.delete(f"/api/delete/{server_id}", follow_redirects=True)
        assert response.status_code == 204
        assert not os.path.exists("/home/mcserver")


