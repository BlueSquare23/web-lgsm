import os
import pwd
import time
import json
import pytest
import psutil
from flask import url_for, request
from game_servers import game_servers
import subprocess

# Global testing env vars.
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
TEST_SERVER = os.environ["TEST_SERVER"]
TEST_SERVER_PATH = os.environ["TEST_SERVER_PATH"]
TEST_SERVER_NAME = os.environ["TEST_SERVER_NAME"]
CFG_PATH = os.environ["CFG_PATH"]
CFG_PATH = os.path.abspath(CFG_PATH)
VERSION = os.environ["VERSION"]


# Checks response contains correct msg.
def check_response(response, msg, resp_code, url):
    # Any request with follow_redirects=True, will have a 200.
    assert response.status_code == resp_code

    # Check redirect by seeing if path changed.
    assert response.request.path == url_for(url)
    assert msg in response.data


def check_main_conf(confstr):
    with open("main.conf", "r") as f:
        content = f.read()

    assert confstr in content


### Home Page tests.
# Check basic content matches.
def test_home_content(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


# Test home responses.
def test_home_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get("/home", follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == "/login"

    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
def test_add_content(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


# Test add responses.
def test_add_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get("/add", follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == "/login"

    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
                "install_path": TEST_SERVER_PATH,
                "script_name": TEST_SERVER_NAME,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": TEST_SERVER,
                "install_path": TEST_SERVER_PATH,
                "script_name": "",
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": TEST_SERVER,
                "install_path": "",
                "script_name": TEST_SERVER_NAME,
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
                "install_path": TEST_SERVER_PATH,
                "script_name": TEST_SERVER_NAME,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        # Empty script_name.
        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": TEST_SERVER,
                "install_path": TEST_SERVER_PATH,
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
                "install_name": TEST_SERVER,
                "install_path": "",
                "script_name": TEST_SERVER_NAME,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        # Empty install_type.
        response = client.post(
            "/add",
            data={
                "install_name": TEST_SERVER,
                "install_path": TEST_SERVER_PATH, 
                "script_name": TEST_SERVER_NAME,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        ## Test legit local server add with mock server.
        response = client.post(
            "/add",
            data={
                "install_type": "local",
                "install_name": TEST_SERVER,
                "install_path": TEST_SERVER_PATH,
                "script_name": TEST_SERVER_NAME,
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
            print(f"Char: {char}")

            print(f"Bad install_name")
            response = ''
            response1 = client.post(
                "/add",
                data={
                    "install_type": "local",
                    "install_name": char,
                    "install_path": TEST_SERVER_PATH,
                    "script_name": TEST_SERVER_NAME,
                },
                follow_redirects=True,
            )

            contains_bad_chars(response1)

            response2 = ''
            response2 = client.post(
                "/add",
                data={
                    "install_type": "local",
                    "install_name": TEST_SERVER,
                    "install_path": char,
                    "script_name": TEST_SERVER_NAME,
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
#                    "install_name": TEST_SERVER,
#                    "install_path": TEST_SERVER_PATH,
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
                "install_name": TEST_SERVER,
                "install_path": TEST_SERVER_PATH,
                "script_name": TEST_SERVER_NAME,
            },
        )

        assert response4.status_code == 400
        assert b"An installation by that name already exits." in response4.data


### Controls page tests.
# Check basic content matches.
def test_controls_content(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        response = client.get(f"/controls?server={TEST_SERVER}")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check string on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Output:" in response.data
        assert f"Server Controls for: {TEST_SERVER}".encode() in response.data
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

        assert f"Web LGSM - Version: {VERSION}".encode() in response.data

        # Test send_cmd setting (disabled by default).
        assert response.status_code == 200  # Return's 200 to GET requests.
        assert b"Send command to game server console" not in response.data

        # Enable the send_cmd setting.
        os.system("sed -i 's/send_cmd = no/send_cmd = yes/g' main.conf")

        # Check send cmd is there after main.conf setting is enabled.
        response = client.get(f"/controls?server={TEST_SERVER}")
        assert response.status_code == 200  # Return's 200 to GET requests.
        assert b"sd" in response.data
        assert b"send" in response.data
        assert b"Send command to game server console" in response.data

        # Set it back to default state for sake of idempotency.
        os.system("sed -i 's/send_cmd = yes/send_cmd = no/g' main.conf")


# Test add responses.
def test_controls_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get(f"/controls?server={TEST_SERVER}", follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == "/login"

    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
        assert b"Invalid game server name!" in response.data

        ## Test invalid server name.
        response = client.get(f"/controls?server=Blah", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Invalid game server name!" in response.data

        ## Test No game server installation directory error.
        # First move the installation directory to .bak.
        os.system(f"mv {TEST_SERVER_PATH} {TEST_SERVER_PATH}.bak")

        # Then test going to the game server dir.
        response = client.get(f"/controls?server={TEST_SERVER}", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"No game server installation directory found!" in response.data

        # Finally move the installation back into place.
        os.system(f"mv {TEST_SERVER_PATH}.bak {TEST_SERVER_PATH}")

        ### Controls Page POST Request test (should only accept GET's).
        response = client.post("/controls", data=dict(test=""))
        assert response.status_code == 405  # Return's 405 to POST requests.


### Install Page tests.
# Test install page content.
def test_install_content(app, client):
    # Login.
    with client:
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


# Test install page responses.
def test_install_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get("/install", follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == "/login"

    # Login.
    with client:
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
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
def test_settings_content(app, client):
    # Login.
    with client:
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


# Test settings page responses.
def test_settings_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get("/settings", follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == "/login"

    # Login.
    with client:
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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

        # Check changes are reflected in main.conf.
        check_main_conf(f"text_color = {text_color}")

        # Test install as new user settings.
        error_msg = b"Settings Updated!"
        response = client.post(
            "/settings", data={"install_new_user": "false"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")
        # Check changes are reflected in main.conf.
        check_main_conf("install_create_new_user = no")

        response = client.post(
            "/settings", data={"install_new_user": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")
        # Check changes are reflected in main.conf.
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

        # Check changes are reflected in main.conf.
        check_main_conf("terminal_height = 10")

    # Re-disable remove_files for the sake of idempotency.
    os.system("sed -i 's/remove_files = yes/remove_files = no/g' main.conf")
    check_main_conf("remove_files = no")


### API system-usage tests.
# Test system usage content & responses.
def test_system_usage(app, client):
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

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
# Test edit page basic content.
def test_edit_content(app, client):
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        payload={"server": TEST_SERVER, "cfg_path": CFG_PATH}
        print(f"Payload: {payload}")
        # Default should be cfg_editor off, so page should 302 to home.
        response = client.post(
            "/edit", data=payload
        )
#        print(response.data.decode('utf-8'))
        assert response.status_code == 302

        # Edit main.conf to enable edit page for basic test.
        os.system("sed -i 's/cfg_editor = no/cfg_editor = yes/g' main.conf")

        # Basic page load test.
        response = client.get(
            "/edit", data={"server": TEST_SERVER, "cfg_path": CFG_PATH}
        )
        assert response.status_code == 200

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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


# Test edit page responses.
def test_edit_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get(
        "/edit",
        data={"server": TEST_SERVER, "cfg_path": CFG_PATH},
        follow_redirects=True,
    )
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == "/login"

    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        ## Edit testing.
        # Test if edits are saved.
        response = client.post(
            "/edit",
            data={
                "server": TEST_SERVER,
                "cfg_path": CFG_PATH,
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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data

        ## Download testing.
        response = client.post(
            "/edit",
            data={"server": TEST_SERVER, "cfg_path": CFG_PATH, "download": "yes"},
        )
        assert response.status_code == 200

        # No server specified tests.
        resp_code = 200
        error_msg = b"No server specified!"
        # Test is none.
        response = client.post(
            "/edit", data={"cfg_path": CFG_PATH}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test is null.
        response = client.post(
            "/edit", data={"server": "", "cfg_path": CFG_PATH}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No cfg specified tests.
        error_msg = b"No config file specified!"
        # Test is none.
        response = client.post(
            "/edit", data={"server": TEST_SERVER}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test is null.
        response = client.post(
            "/edit", data={"server": TEST_SERVER, "cfg_path": ""}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Invalid game server name test.
        error_msg = b"Invalid game server name!"
        response = client.post(
            "/edit",
            data={"server": "test", "cfg_path": CFG_PATH},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No game server installation directory found test.
        # First move the installation directory to .bak.
        os.system(f"mv {TEST_SERVER_PATH} {TEST_SERVER_PATH}.bak")

        error_msg = b"No such file"
        response = client.post(
            "/edit",
            data={"server": TEST_SERVER, "cfg_path": CFG_PATH},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Finally move the installation back into place.
        os.system(f"mv {TEST_SERVER_PATH}.bak {TEST_SERVER_PATH}")

        # Invalid config file name test.
        error_msg = b"Invalid config file name!"
        response = client.post(
            "/edit",
            data={"server": TEST_SERVER, "cfg_path": CFG_PATH + "test"},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No such file test.
        error_msg = b"No such file!"
        response = client.post(
            "/edit",
            data={"server": TEST_SERVER, "cfg_path": "/test" + CFG_PATH},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

    # Re-disable the cfg_editor for the sake of idempotency.
    os.system("sed -i 's/cfg_editor = yes/cfg_editor = no/g' main.conf")


def test_new_user_has_no_permissions(app, client):
    """
    Test's that the new user cannot do anything in the web interface yet,
    except login.
    """
    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": "test2", "password": PASSWORD}
        )
        assert response.status_code == 302

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

        # Test delete page.
        response = client.get(f"/delete?server={TEST_SERVER}", follow_redirects=True)
        error_msg = b"Your user does NOT have permission to delete servers"
        check_response(response, error_msg, resp_code, "views.home")

        # Test settings page.
        response = client.get("/settings", follow_redirects=True)
        error_msg = b"Your user does NOT have permission access the settings page"
        check_response(response, error_msg, resp_code, "views.home")

        # Test game server controls page.
        response = client.get(f"/controls?server={TEST_SERVER}", follow_redirects=True)
        error_msg = b"Your user does NOT have permission access this game server"
#        print(response.data.decode("utf-8"))
        check_response(response, error_msg, resp_code, "views.home")


def test_enable_new_user_perms(app, client):
    # Login as admin.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        response = client.get("/edit_users?username=newuser")
        assert response.status_code == 200

        create_user_json = """{
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
            "servers": ["Mockcraft"]
        }"""

        response = client.post(
            "/edit_users", data=json.loads(create_user_json), follow_redirects=True
        )
        assert response.request.path == url_for("auth.edit_users")
#        print(response.data.decode("utf-8"))
        assert b"User test2 Updated" in response.data


def test_delete_game_server(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        response = client.get("/delete?server=" + TEST_SERVER, follow_redirects=True)
        msg = b"Game server, Mockcraft deleted"
        check_response(response, msg, 200, "views.home")


def test_new_user_has_ALL_permissions(app, client):
    """
    Test's that the new user can do anything in the web interface.
    """
    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": "test2", "password": PASSWORD}
        )
        assert response.status_code == 302

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

        # Test add page.
        response = client.get("/add", follow_redirects=True)
        msg = b"Add an Existing LGSM Installation"
        check_response(response, msg, resp_code, "views.add")

        ## Test legit server add.
        response = client.post(
            "/add",
            data={
                "install_type": 'local',
                "install_name": TEST_SERVER,
                "install_path": TEST_SERVER_PATH,
                "script_name": TEST_SERVER_NAME,
            },
            follow_redirects=True,
        )
#        print(response.data.decode('utf-8'))

        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Game server added!" in response.data

        # Test game server controls page.
        response = client.get(f"/controls?server={TEST_SERVER}", follow_redirects=True)
        msg = b"Server Controls for: Mockcraft"
        check_response(response, msg, resp_code, "views.controls")

        # Test delete page.
        response = client.get("/delete?server=" + TEST_SERVER, follow_redirects=True)
        msg = b"Game server, Mockcraft deleted"
        check_response(response, msg, resp_code, "views.home")

        # Test settings page.
        response = client.get("/settings", follow_redirects=True)
        msg = b"Web LGSM Settings"
        check_response(response, msg, resp_code, "views.settings")


def test_delete_new_user(app, client):
    # Login as admin.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        # Make sure can't do certain delete options first.
        resp_code = 200
        error_msg = b"Can&#39;t delete user that doesn&#39;t exist yet"
        response = client.get(
            "/edit_users?username=newuser&delete=true", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "auth.edit_users")

        error_msg = b"Cannot delete currently logged in user"
        response = client.get(
            f"/edit_users?username={USERNAME}&delete=true", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "auth.edit_users")

        # TODO: Make test for this. Rn, this test doesn't work because above case block it.
        #        error_msg = b"Cannot delete main admin user"
        #        response = client.get(f'/edit_users?username={USERNAME}&delete=true', follow_redirects=True)
        #        check_response(response, error_msg, resp_code, 'auth.edit_users')

        # Do a legit user delete.
        response = client.get(
            "/edit_users?username=test2&delete=true", follow_redirects=True
        )
        assert response.status_code == 200
        assert b"User test2 deleted" in response.data


def full_game_server_install(client):
    # For good measure.
    os.system("sudo -n killall -9 java")

    # Do an install.
    response = client.post(
        "/install",
        data={"server_name": "mcserver", "full_name": "Minecraft"},
        follow_redirects=True,
    )
    assert response.status_code == 200
#    print(response.data.decode('utf-8'))
    assert b"Installing" in response.data

    # Some buffer time.
    time.sleep(5)
#    print(client.get("/api/cmd-output?server=Minecraft").data.decode("utf-8"))

    # TODO: Rewrite this, should be a while loop until successfully installed
    # message observed with a timeout.

    observed_running = False
    # While process is running check output route is producing output.
    while (
        b'"process_lock": true' in client.get("/api/cmd-output?server=Minecraft").data
    ):
        observed_running = True

        # Test to make sure output route is returning stuff for gs while
        # game server install is running.
        response = client.get("/api/cmd-output?server=Minecraft")
        assert response.status_code == 200
        assert b"stdout" in response.data

        # Check that the output lines are not empty.
        empty_resp = '{"stdout": [""], "pid": false, "process_lock": false}'
        json_data = json.loads(response.data.decode("utf8"))
        assert empty_resp != json.dumps(json_data)

        time.sleep(10)

    print("######################## GAME SERVER INSTALL OUTPUT")
    print(json.dumps(json_data, indent=4))

    # Test that install was observed to be running.
    assert observed_running

    assert b'Game server successfully installed' in response.data


def game_server_start_stop(client):
    # Log test user in.
    response = client.post("/login", data={"username": USERNAME, "password": PASSWORD})
    assert response.status_code == 302

    # Test starting the server.
    response = client.get(
        "/controls?server=Minecraft&command=st", follow_redirects=True
    )
    assert response.status_code == 200
#    print(
#        "######################## START CMD RESPONSE\n" + response.data.decode("utf8")
#    )

    time.sleep(2)
#    response = client.get("/controls?server=Minecraft", follow_redirects=True)
#    print(
#        "######################## CONTROLS PAGE RESPONSE 2 SEC LATER\n"
#        + response.data.decode("utf8")
#    )

    # More debug info.
    print("######################## ls -lah logs/")
    os.system(f"ls -lah logs/")

    print("######################## sudo -l")
    os.system(f"sudo -l")

    print("######################## sudo -n ls -lah /home/")
    os.system(f"sudo -n ls -lah /home/")

    print("######################## sudo -n ls -lah /home/mcserver/GameServers/Minecraft")
    os.system(f"sudo -n ls -lah /home/mcserver/GameServers/Minecraft")

    print("######################## sudo -n -u mcserver /home/mcserver/GameServers/Minecraft/mcserver")
    os.system(f"sudo -n -u mcserver /home/mcserver/GameServers/Minecraft/mcserver")

    # Check output lines are there.
    response = client.get("/api/cmd-output?server=Minecraft")
    assert response.status_code == 200
    assert b"stdout" in response.data
    print(
        "######################## OUTPUT ROUTE JSON\n" + response.data.decode("utf8")
    )

    # Check that the output lines are not empty.
    empty_resp = '{"stdout": [""], "pid": false, "process_lock": false}'
    json_data = json.loads(response.data.decode("utf8"))
    assert empty_resp != json.dumps(json_data)

    # Sleep until process is finished.
    while (
        b'"process_lock": true' in client.get("/api/cmd-output?server=Minecraft").data
    ):
        print(client.get("/api/cmd-output?server=Minecraft").data.decode("utf8"))
        time.sleep(5)

    assert b'"process_lock": false' in client.get("/api/cmd-output?server=Minecraft").data
    print(client.get("/api/cmd-output?server=Minecraft").data.decode("utf8"))

    #    print("######################## Minecraft Start Log\n")
    #    os.system("cat Minecraft/logs/script/mcserver-script.log")
    #    os.system("cat Minecraft/log/server/latest.log")
    #    os.system("cat Minecraft/log/console/mcserver-console.log")

    # Check status indicator api json.
    resp = client.get("/api/server-status?id=1").data.decode("utf8")
    print(resp)
    resp_dict = json.loads(resp)
    assert resp_dict['status'] == True

    # Enable the send_cmd setting.
    os.system("sed -i 's/send_cmd = no/send_cmd = yes/g' main.conf")
    time.sleep(1)

    # Test sending command to game server console
    response = client.get(
        "/controls?server=Minecraft&command=sd&cmd=test", follow_redirects=True
    )
    assert response.status_code == 200
    time.sleep(1)

    print("######################## SEND COMMAND OUTPUT")
    # Sleep until process is finished.
    while (
        b'"process_lock": true' in client.get("/api/cmd-output?server=Minecraft").data
    ):
        print(client.get("/api/cmd-output?server=Minecraft").data.decode("utf8"))
        time.sleep(3)

    time.sleep(1)
    assert b'"process_lock": false' in client.get("/api/cmd-output?server=Minecraft").data

    print(client.get("/api/cmd-output?server=Minecraft").data.decode("utf8"))
    assert (
        b"Sending command to console"
        in client.get("/api/cmd-output?server=Minecraft").data
    )

    # Set send_cmd back to default state for sake of idempotency.
    os.system("sed -i 's/send_cmd = yes/send_cmd = no/g' main.conf")
    time.sleep(1)

    # Test stopping the server
    response = client.get(
        "/controls?server=Minecraft&command=sp", follow_redirects=True
    )
    assert response.status_code == 200

    # Run until "process_lock": false (aka proc stopped).
    while (
        b'"process_lock": true' in client.get("/api/cmd-output?server=Minecraft").data
    ):
        time.sleep(3)

    # For good measure.
    os.system("sudo -n killall -9 java")

    # Check status indicator api, is off.
    resp = client.get("/api/server-status?id=1").data.decode("utf8")
    resp_dict = json.loads(resp)
    assert resp_dict['status'] == False


def console_output(client):
    # Test starting the server.
    response = client.get(
        "/controls?server=Minecraft&command=st", follow_redirects=True
    )
    assert response.status_code == 200

    time.sleep(5)

    # Check output lines are there.
    response = client.get("/api/cmd-output?server=Minecraft")
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
        b'"process_lock": true' in client.get("/api/cmd-output?server=Minecraft").data
    ):
        time.sleep(3)

    time.sleep(1)
    assert b'"process_lock": false' in client.get("/api/cmd-output?server=Minecraft").data

    # Simulate front end js console mode.
    # 1. First POST to /api/update-console
    # 2. Next GET /api/cmd-output to check for data

    # Sleep for long enough that some output comes through.
    time.sleep(10)

    response = client.post(
        "/api/update-console", data={"server": "Minecraft"}
    )
    assert response.status_code == 200

    print("######################## START CONSOLE OUTPUT")
    resp_json = client.get("/api/cmd-output?server=Minecraft").data.decode("utf8")
    resp_data = json.loads(resp_json)
    print(resp_json)

    # Just check that some stdout is coming through.
    assert len(resp_data['stdout']) > 0

    # Cleanup
    os.system("sudo -n killall -9 java")


def user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def test_install_newuser(app, client):
    """First test install as new user."""
    print(USERNAME)
    print(PASSWORD)
    print(TEST_SERVER)
    print(TEST_SERVER_PATH)
    print(TEST_SERVER_NAME)
    print(CFG_PATH)
    print(VERSION)

    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        # Change settings.
        error_msg = b"Settings Updated!"
        resp_code = 200
        response = client.post(
            "/settings", data={"install_new_user": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.
        check_main_conf("install_create_new_user = yes")

        # Test full install as new user.
        full_game_server_install(client)

        game_server_start_stop(client)
        console_output(client)

        response = client.post(
            "/settings", data={"delete_files": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Stop the server.
        response = client.get(
            "/controls?server=Minecraft&command=sp", follow_redirects=True
        )
        assert response.status_code == 200

        # Run until "process_lock": false (aka proc stopped).
        while (
            b'"process_lock": true'
            in client.get("/api/cmd-output?server=Minecraft").data
        ):
            time.sleep(3)

        response = client.get("/delete?server=Minecraft", follow_redirects=True)
        msg = b"Game server, Minecraft deleted"
        check_response(response, msg, 200, "views.home")

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


def test_install_sameuser(app, client):
    """Then test install as existing user."""
    print(USERNAME)
    print(PASSWORD)
    print(TEST_SERVER)
    print(TEST_SERVER_PATH)
    print(TEST_SERVER_NAME)
    print(CFG_PATH)
    print(VERSION)

    # Login.
    with client:
        # Log test user in.
        response = client.post(
            "/login", data={"username": USERNAME, "password": PASSWORD}
        )
        assert response.status_code == 302

        # Change settings.
        error_msg = b"Settings Updated!"
        resp_code = 200
        response = client.post(
            "/settings", data={"install_new_user": "false"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.
        check_main_conf("install_create_new_user = no")

        # Test full install as existing user.
        full_game_server_install(client)

        game_server_start_stop(client)
        console_output(client)

        response = client.post(
            "/settings", data={"delete_files": "true"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.settings")

        response = client.get("/delete?server=Minecraft", follow_redirects=True)
        msg = b"Game server, Minecraft deleted"
        check_response(response, msg, 200, "views.home")
        assert not os.path.exists("/home/mcserver")
