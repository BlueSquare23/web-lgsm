import os
import re
import pwd
import time
import json
import pytest
import psutil
from flask import url_for, request
from game_servers import game_servers
import subprocess
import configparser

from app.models import User, GameServer, Job, Audit
from app.cron import CronService
from app.models import db
from utils import *

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
        assert b"Add or Edit Existing LGSM Installation" in response.data
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
        assert b"Add or Edit Existing LGSM Installation" in response.data
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
        assert b"Enter remote server&#39;s IP address or hostname. For example, &#34;gmod.domain.tld&#34;" in response.data
        assert b"Submit" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


# Test add responses.
def test_add_responses(db_session, client, authed_client, test_vars):
    test_server = test_vars["test_server"]
    test_server_path = test_vars["test_server_path"]
    test_server_name = test_vars["test_server_name"]
    test_remote_host = test_vars["test_remote_host"]

    with client:
        response = client.get("/add")
        assert response.status_code == 200  # Return's 200 to GET requests.

        csrf_token = get_csrf_token(response)

        ## Test empty parameters.
        resp_code = 200
        error_msg = b"This field is required."

        response = client.post(
            "/add",
            data={"csrf_token": csrf_token, "install_name": "", "install_path": "", "script_name": ""},
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        response = client.post(
            "/add",
            data={
                "csrf_token": csrf_token,
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
                "csrf_token": csrf_token,
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
                "csrf_token": csrf_token,
                "install_type": "local",
                "install_name": test_server,
                "install_path": "",
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        # Empty install_name.
        response = client.post(
            "/add",
            data={
                "csrf_token": csrf_token,
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
                "csrf_token": csrf_token,
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
                "csrf_token": csrf_token,
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
                "csrf_token": csrf_token,
                "install_name": test_server,
                "install_path": test_server_path, 
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.add")

        ## Test empty csrf_token.
        error_msg = b"The CSRF token is invalid"
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
        assert response.status_code == 200

        ## Test legit local server add with mock server.
        response = client.post(
            "/add",
            data={
                "csrf_token": csrf_token,
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

            # Check redirect by seeing if path changed.
            assert response.request.path == url_for("views.add")
            assert "Input contains invalid characters" in response.data.decode('utf-8')

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
            response = ''
            response1 = client.post(
                "/add",
                data={
                    "csrf_token": csrf_token,
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
                    "csrf_token": csrf_token,
                    "install_type": "local",
                    "install_name": test_server,
                    "install_path": char,
                    "script_name": test_server_name,
                },
                follow_redirects=True,
            )
            contains_bad_chars(response2)

            response3 = ''
            response3 = client.post(
                "/add",
                data={
                    "csrf_token": csrf_token,
                    "install_type": "local",
                    "install_name": test_server,
                    "install_path": test_server_path,
                    "script_name": char,
                },
                follow_redirects=True,
            )
            contains_bad_chars(response3)


        ## Test install details edit.
        server_id = get_server_id(test_server)

        # Change server name.
        response4 = client.post(
            "/add",
            data={
                "server_id": server_id,
                "csrf_token": csrf_token,
                "install_type": "local",
                "install_name": test_server + '1',
                "install_path": test_server_path,
                "script_name": test_server_name,
            },
            follow_redirects=True,
        )

        assert response4.status_code == 200
        alert_msgs = extract_alert_messages(response4, 'success')
        assert 'Game server added!' in alert_msgs

        ## Test legit remote server add with mock server details.
        response = client.post(
            "/add",
            data={
                "csrf_token": csrf_token,
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
                "csrf_token": csrf_token,
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


### Audit page tests.
# Check basic content matches.
def test_audit_content(db_session, client, authed_client, test_vars):
    version = test_vars["version"]

    with client:

        response = client.get("/audit")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Audit Log" in response.data
        assert b"Results Per Page" in response.data
        assert b"Filter by User" in response.data
        assert b"Search Messages" in response.data
        assert b"Search" in response.data
        assert b"Reset Filters" in response.data
        assert b"Event ID" in response.data
        assert b"User ID" in response.data
        assert b"Username" in response.data
        assert b"Event Message" in response.data
        assert b"Date/Time" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


# Check responses are expected.
def test_audit_responses(db_session, client, authed_client, add_mock_server, test_vars):
    version = test_vars["version"]
    test_server = test_vars["test_server"]

    server_id = get_server_id(test_server)

    with client:
        # Setup fake db entries.
        for i in range(100):
            db.session.add(Audit(
                user_id='1',
                message=f"Test entry {i+1}"
            ))
        db.session.commit()

        response = client.get(f"/audit")
        assert response.status_code == 200  # Return's 200 to GET requests.

        response = client.get(f"/audit?per_page=50&page=2&user_id=1&search=test+entry")
        assert response.data.count(b'Test entry') == 50


### Jobs page tests.
# Check basic content matches.
def test_jobs_content(db_session, client, authed_client, add_mock_server, test_vars):
    version = test_vars["version"]
    test_server = test_vars["test_server"]

    with client:

        response = client.get("/jobs")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Web-LGSM Job Scheduler" in response.data
        assert b"Select Game Server" in response.data
        assert b"Mockcraft" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data

        server_id = get_server_id(test_server)
        response = client.get(f"/jobs?server_id={server_id}")
        assert response.status_code == 200  # Return's 200 to GET requests.
        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Web-LGSM Job Scheduler" in response.data
        assert b"Select Game Server" in response.data
        assert b"Mockcraft" in response.data
        assert b"Cron Jobs for Mockcraft" in response.data
        assert b"Add New Cron Job" in response.data
        assert b"Cron Job Editor" in response.data
        assert b"Command" in response.data
        assert b"Comment" in response.data
        assert b"Schedule" in response.data
        assert b"Minutes" in response.data
        assert b"Hours" in response.data
        assert b"Day of Month" in response.data
        assert b"Month" in response.data
        assert b"Day of Week" in response.data
        assert b"Cron Expression" in response.data
        assert b"Close" in response.data
        assert b"Save Changes" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


# Check responses are expected.
def test_jobs_responses(db_session, client, authed_client, add_mock_server, test_vars):
    version = test_vars["version"]
    test_server = test_vars["test_server"]

    server_id = get_server_id(test_server)
    cron_service = CronService(server_id=server_id)

    with client:

        response = client.get(f"/jobs?server_id={server_id}")
        assert response.status_code == 200  # Return's 200 to GET requests.
        csrf_token = get_csrf_token(response)

        assert Job.query.first() is None

        # Test add job via POST.
        data = {
            "csrf_token": csrf_token,
            "job_id": "",
            "server_id": server_id,
            "command": "start",
            "comment": "Test job",
            "custom": "",
            "cron_expression": "30 1 * * *"
        }

        response = client.post("/jobs", data=data, follow_redirects=True)
        assert response.status_code == 200
        alert_msgs = extract_alert_messages(response, 'success')
        assert 'Cronjob updated successfully!' in alert_msgs

        assert Job.query.first() is not None

        jobs_list = cron_service.list_jobs()
        job_id = jobs_list[0]["job_id"]

        # Test update job via POST.
        data = {
            "csrf_token": csrf_token,
            "job_id": job_id, 
            "server_id": server_id,
            "command": "stop",
            "comment": "Test job comment updated",
            "custom": "",
            "cron_expression": "30 2 * * *"
        }
        response = client.post("/jobs", data=data, follow_redirects=True)
        assert response.status_code == 200
        alert_msgs = extract_alert_messages(response, 'success')
        assert 'Cronjob updated successfully!' in alert_msgs

        newjob = Job.query.first()
        assert newjob.id == job_id  # Aka job_id didn't change when updating job.
        assert newjob.command == "stop"
        assert newjob.comment == "Test job comment updated"
        assert newjob.expression == "30 2 * * *"


### Controls page tests.
# Check basic content matches.
def test_controls_content(db_session, client, authed_client, add_mock_server, test_vars):
    version = test_vars["version"]
    test_server = test_vars["test_server"]

    with client:
        # Test redirect for backward compat works.
        response = client.get(f"/controls?server={test_server}")
        server_id = get_server_id(test_server)

        response = client.get(f"/controls?server_id={server_id}")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check string on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Output:" in response.data
        assert f"Server Controls for {test_server}".encode() in response.data
        assert b"Top" in response.data
        assert b"Delete Server" in response.data

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

        # Enable send_cmd setting in config file.
        toggle_send_cmd(True)
        os.system("cat main.conf.local")
        time.sleep(1)

        # Check send cmd is there after main.conf.local setting is enabled.
        server_id = get_server_id(test_server)
        response = client.get(f"/controls?server_id={server_id}")

        assert response.status_code == 200  # Return's 200 to GET requests.
        assert b"sd" in response.data
        assert b"send" in response.data
        assert b"Send command to game server console" in response.data

        # Set it back to default state for sake of idempotency.
        toggle_send_cmd(False)


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
        assert b"server_id: This field is required." in response.data

        ## Test empty server name.
        response = client.get(f"/controls?server=", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"server_id: This field is required." in response.data

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
        assert b"server_id: This field is required." in response.data

        ## Test invalid server name.
        response = client.get(f"/controls?server_id=Blah", follow_redirects=True)
        # Should redirect to home. 200 bc
        assert response.status_code == 200
        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("views.home")
        assert b"Invalid game server ID!" in response.data

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
        response = client.get("/install")
        assert response.status_code == 200
        csrf_token = get_csrf_token(response)

        ## Leaving off legit install test(s) for now because that takes a
        # while to run. Only testing bad posts atm.

        ## Test for Missing Required Form Field error msg.

        # Test for no fields supplied.
        resp_code = 200
        error_msg = b"The CSRF token is missing."
        response = client.post("/install", follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.install")

        # Test no script_name.
        error_msg = b"This field is required."
        response = client.post(
            "/install", data={"csrf_token": csrf_token, "full_name": "Minecraft"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.install")

        # Test invalid script_name.
        error_msg = b"Invalid script name."
        response = client.post(
            "/install", data={"csrf_token": csrf_token, "script_name": "fartingbuttz", "full_name": "Minecraft"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.install")

        # Test no full_name.
        error_msg = b"This field is required."
        response = client.post(
            "/install", data={"csrf_token": csrf_token, "script_name": "mcserver"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.install")

        # Test for empty form fields.
        error_msg = b"Invalid full name."
        response = client.post(
            "/install", data={"csrf_token": csrf_token, "script_name": "mcserver", "full_name": "Jerry's still dead man"}, follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.install")

        # Test for empty form fields.
        error_msg = b"This field is required."
        response = client.post(
            "/install",
            data={"csrf_token": csrf_token, "server_name": "", "full_name": ""},
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
        assert b"Install new game servers under system user" in response.data
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

    response = client.get("/settings")
    assert response.status_code == 200  # Return's 200 to GET requests.
    csrf_token = get_csrf_token(response)

    default_data = {
        "csrf_token": csrf_token,
        "text_color": "#09ff00",
        "graphs_primary": "#e01b24",
        "graphs_secondary": "#0d6efd",
        "terminal_height": "10",
        "delete_user": "false",
        "remove_files": "false",
        "install_new_user": "true",
        "newline_ending": "true",
        "show_stderr": "true",
        "clear_output_on_reload": "true",
    }

    with client:
        resp_code = 200

        ## Test color input changes
        # NOTE: Only accepts hexcodes as valid colors.

        # Legit color change test first.
        error_msg = b"Settings Updated!"
        data = default_data.copy()

        text_color = "#000000"
        data["text_color"] = text_color
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf(f"text_color = {text_color}")

        # Test missing csrf_token.
        data = default_data.copy()
        del data['csrf_token']
        error_msg = b"The CSRF token is missing"

        response = client.post("/settings", data=data, follow_redirects=True)
        print(extract_alert_messages(response))
        check_response(response, error_msg, resp_code, "views.settings")

        # Text color tests.
        error_msg = b"Invalid text color!"
        data = default_data.copy()

        data["text_color"] = "test"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        data["text_color"] = "red"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        data["text_color"] = "#aaaaaaaaaaaaaaaa"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Primary color tests
        error_msg = b"Invalid primary color!"
        data = default_data.copy()

        data["graphs_primary"] = "test"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        data["graphs_primary"] = "red"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        data["graphs_primary"] = "#aaaaaaaaaaaaaaaa"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Secondary color tests
        error_msg = b"Invalid secondary color!"
        data = default_data.copy()

        data["graphs_secondary"] = "test"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        data["graphs_secondary"] = "red"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        data["graphs_secondary"] = "#aaaaaaaaaaaaaaaa"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        ## Test install as new user settings. 
        data = default_data.copy()
        error_msg = b"Settings Updated!"

        data["install_new_user"] = "false"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf("install_create_new_user = no")

        data["install_new_user"] = "true"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf("install_create_new_user = yes")

        # Test invalid choice.
        error_msg = b"Not a valid choice"
        data["install_new_user"] = "sneeeeeeeeeeeeeeeeee"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        ## Test text area height change.

        # Legit terminal height test.
        data = default_data.copy()
        error_msg = b"Settings Updated!"
        data["terminal_height"] = "10"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check changes are reflected in main.conf.local.
        check_main_conf("terminal_height = 10")

        # App only accepts terminal height between 5 and 100.
        error_msg = b"Number must be between 5 and 100"
        data["terminal_height"] = "-20"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check nothing changed in conf, just to be sure.
        check_main_conf("terminal_height = 10")

        data["terminal_height"] = "test"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check nothing changed in conf, just to be sure.
        check_main_conf("terminal_height = 10")

        data["terminal_height"] = "99999"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check nothing changed in conf, just to be sure.
        check_main_conf("terminal_height = 10")

        data["terminal_height"] = "-e^(i*3.14)"
        response = client.post("/settings", data=data, follow_redirects=True)
        check_response(response, error_msg, resp_code, "views.settings")

        # Check nothing changed in conf, just to be sure.
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
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={cfg_path}"
        )
        assert response.status_code == 302

        toggle_cfg_editor(True)
#        os.system("cat main.conf.local")  # Debug

        # Basic page load test.
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={cfg_path}"
        )
        assert response.status_code == 200

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Editing Config:" in response.data
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
        toggle_cfg_editor(True)

        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={cfg_path}"
        )
#        debug_response(response)
        csrf_token = get_csrf_token(response)

        ## Edit testing.

        # Test no csrf_token.
        response = client.post(
            "/edit",
            data={
                "server_id": server_id,
                "cfg_path": cfg_path,
                "file_contents": "#### Testing...",
            },
            follow_redirects=True
        )
        alerts = extract_alert_messages(response, 'danger')
        assert 'csrf_token: The CSRF token is missing.' in alerts

        # Test if edits are saved.
        response = client.post(
            "/edit",
            data={
                "csrf_token": csrf_token,
                "server_id": server_id,
                "cfg_path": cfg_path,
                "file_contents": "#### Testing...",
            },
            follow_redirects=True
        )
        assert response.status_code == 200

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Editing Config:" in response.data
        assert b"Full Path: " in response.data
        assert b"#### Testing..." in response.data
        assert b"Save File" in response.data
        assert b"Download Config File" in response.data
        assert b"Back to Controls" in response.data
        assert b"Please note," in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data

        ## Download testing.
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={cfg_path}&csrf_token={csrf_token}&download_submit=Download"
        )
        assert response.status_code == 200

        # No server specified tests.
        resp_code = 200
        error_msg = b"This field is required"
        # Test is none.
        response = client.get(
            f"/edit?cfg_path={cfg_path}", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test is null.
        response = client.get(
            f"/edit?server_id=&cfg_path={cfg_path}", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No cfg specified tests.
        # Test is none.
        response = client.get(
            f"/edit?server_id={server_id}", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Test is null.
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path=", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Invalid game server name test.
        error_msg = b"Invalid game server ID"
        response = client.get(
            f"/edit?server_id=TEST&cfg_path={cfg_path}", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No game server installation directory found test.
        # First move the installation directory to .bak.
        os.system(f"mv {test_server_path} {test_server_path}.bak")

        error_msg = b"Error reading file"
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={cfg_path}", follow_redirects=True
        )
        check_response(response, error_msg, resp_code, "views.home")

        # Finally move the installation back into place.
        os.system(f"mv {test_server_path}.bak {test_server_path}")

        # Invalid config file name test.
        error_msg = b"Invalid config file name!"
        invalid_name = cfg_path + "fartingbuttz"
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={invalid_name}&csrf_token={csrf_token}",
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")

        # No such file test.
        error_msg = b"Error reading file!"
        invalid_name = "/blahfart" + cfg_path
        response = client.get(
            f"/edit?server_id={server_id}&cfg_path={invalid_name}&csrf_token={csrf_token}",
            follow_redirects=True,
        )
        check_response(response, error_msg, resp_code, "views.home")


def test_new_user_has_no_permissions(client, add_mock_server, user_authed_client_no_perms, test_vars):
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


def test_enable_new_user_perms(db_session, client, authed_client, add_mock_server, add_second_user_no_perms, test_vars):
    test_server = test_vars["test_server"]

    with client:

        server_id = get_server_id(test_server)

        response = client.get("/edit_users?username=newuser")
        assert response.status_code == 200
        csrf_token = get_csrf_token(response)

        create_user_data = {
            "csrf_token": csrf_token,
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
            "server_ids": [server_id]
        }

        response = client.post(
            "/edit_users", data=create_user_data, follow_redirects=True
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
        csrf_token = get_csrf_token(response)
        msg = b"Add or Edit Existing LGSM Installation Details"
        check_response(response, msg, resp_code, "views.add")

        ## Test legit server add.
        response = client.post(
            "/add",
            data={
                "csrf_token": csrf_token,
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
        msg = b"Server Controls for Mockcraft"
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
        alerts = extract_alert_messages(response, 'danger')
        check_response(response, error_msg, resp_code, "auth.edit_users")
        assert 'Cannot delete currently logged in user!' in alerts

        error_msg = 'Cannot delete currently logged in user!'
        response = client.get(f'/edit_users?username={username}&delete=true', follow_redirects=True)
        alerts = extract_alert_messages(response, 'danger')
        assert error_msg in alerts

        # Do a legit user delete.
        response = client.get(
            "/edit_users?username=test2&delete=true", follow_redirects=True
        )
        assert response.status_code == 200
        assert b"User test2 deleted" in response.data

