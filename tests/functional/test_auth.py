import os
import json
import pytest
from flask import url_for, request
from game_servers import game_servers
from app.models import User, GameServer
from utils import *


### Setup Page tests.

def test_setup_contents(db_session, client, test_vars):
    """
    Test setup page contents.
    """
    version = test_vars["version"]
    with client:
        response = client.get("/setup")
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Login" in response.data
        assert b"Web LGSM Setup" in response.data
        assert b"Username" in response.data
        assert b"Enter Username" in response.data
        assert b"Password" in response.data
        assert b"Enter Password" in response.data
        assert b"Confirm Password" in response.data
        assert b"Retype Password" in response.data
        assert b"Submit" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


def test_setup_responses(db_session, client, test_vars):
    """
    Test setup page responses.
    """
    username = test_vars["username"]
    password = test_vars["password"]

    with client:
        response = client.get("/setup")
        assert response.status_code == 200  # Return's 200 to GET requests.
        csrf_token = get_csrf_token(response)

        # Using follow_redirects=True bc only redirect on setup page is for
        # missing required args. The rest fall through to the render_template
        # statement with a 200.

        # Test with empty args.
        error_msg = b"Missing required form field(s)!"
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": "", "password1": "", "password2": ""},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.setup")

        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": "a", "password1": "a", "password2": ""},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.setup")

        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": "", "password1": "a", "password2": "a"},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.setup")

        # Test with no args.
        response = client.post("/setup", data={}, follow_redirects=True)
        check_for_error(response, error_msg, "auth.setup")

        # Form field too long test.
        # First create a string that's too long for the form fields.
        too_long = "a"
        count = 0
        while count < 150:
            too_long += "a"
            count += 1

        error_msg = b"Field must be between 4 and 20 characters long."
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": too_long, "password1": password, "password2": password},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.setup")

        error_msg = b"Field must be between 12 and 150 characters long."
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": too_long, "password2": password},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.setup")

        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": password, "password2": too_long},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.setup")

        ## Tests for if password doesn't meet criteria.
        # Test needs uppercase, lowercase, and special char.
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": "blah", "password2": "blah"},
            follow_redirects=True,
        )
        assert b"Password must contain at least one uppercase letter" in response.data

        ## Tests username contains bad char(s).
        def test_username_bad_chars(response):
            # Check redirect by seeing if path changed.
            assert response.request.path == url_for("auth.setup")
            assert b"Username contains invalid characters." in response.data

        bad_chars = {
            " ",
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

        for char in bad_chars:
            response = client.post(
                "/setup",
                data={"csrf_token": csrf_token, "username": char, "password1": password, "password2": password},
                follow_redirects=True,
            )
            test_username_bad_chars(response)

        # Test passwords don't match.
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": password, "password2": "**Test1234"},
            follow_redirects=True,
        )
        # No redirect on setup.
        assert b"Passwords do not match" in response.data

        # Test password too short.
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": "Ab3$", "password2": "Ab3$"},
            follow_redirects=True,
        )
        # No redirect on setup.
        debug_response(response)
        error_msg = b"Field must be between 12 and 150 characters long."
        assert error_msg in response.data

        # Try to request the login page, should get redirected to setup.
        response = client.get("/login", follow_redirects=True)
        csrf_token = get_csrf_token(response)
        assert response.status_code == 200  # 200 because follow_redirects=True.
        assert response.request.path == url_for(f"auth.setup")
        assert b"Please add a user!" in response.data

        # Finally, create real test user.
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": password, "password2": password},
        )
        assert response.status_code == 302

        # Test user already added!
        error_msg = b"User already added. Please sign in!"
        response = client.post(
            "/setup",
            data={"csrf_token": csrf_token, "username": username, "password1": password, "password2": password},
            follow_redirects=True,
        )
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for(f"auth.login")
        assert error_msg in response.data


### Login Page tests.

def test_login_contents(db_session, client, setup_client, test_vars):
    """
    Test login page contents.
    """
    version = test_vars["version"]

    with client:
        response = client.get("/login")
        assert response.status_code == 200

        # Check content matches.
        assert b"Home" in response.data
        assert b"Login" in response.data
        assert b"Username" in response.data
        assert b"Enter Username" in response.data
        assert b"Password" in response.data
        assert b"Enter Password" in response.data
        assert b"Login" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


def test_login_responses(db_session, client, setup_client, test_vars):
    """
    Test login page responses.
    """
    username = test_vars["username"]
    password = test_vars["password"]

    with client:

        response = client.get("/login")
        csrf_token = get_csrf_token(response)

        # First test legit login
        response = client.post(
            "/login", data={"csrf_token": csrf_token, "username": username, "password": password}, 
            follow_redirects=True
        )
        msg = b"Logged in"
        check_for_error(response, msg, "views.home")

        # Logout again.
        response = client.get("/logout", follow_redirects=True)
        msg = b"Logged out"
        check_for_error(response, msg, "auth.login")

        # Test empty args.
        error_msg = b"Missing required form field(s)!"
        response = client.post(
            "/login", data={"csrf_token": csrf_token, "username": "", "password": ""}, follow_redirects=True
        )
        check_for_error(response, error_msg, "auth.login")

        response = client.post(
            "/login", data={"csrf_token": csrf_token, "username": username, "password": ""}, follow_redirects=True
        )
        check_for_error(response, error_msg, "auth.login")

        response = client.post(
            "/login", data={"csrf_token": csrf_token, "username": "", "password": password}, follow_redirects=True
        )
        check_for_error(response, error_msg, "auth.login")

        # Form field too long test.
        # First create a string that's too long for the form fields.
        too_long = "a"
        count = 0
        while count < 150:
            too_long += "a"
            count += 1

        error_msg = b"Field must be between 4 and 20 characters long."
        response = client.post(
            "/login",
            data={"csrf_token": csrf_token, "username": too_long, "password": password},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.login")

        error_msg = b"Field must be between 12 and 150 characters long."
        response = client.post(
            "/login",
            data={"csrf_token": csrf_token, "username": username, "password": too_long},
            follow_redirects=True,
        )
        check_for_error(response, error_msg, "auth.login")

        # CSRF token required check.
        response = client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )
        error_msg = b"The CSRF token is missing."
        check_for_error(response, error_msg, "auth.login")


### Logout page tests.

def test_logout(db_session, client, authed_client, test_vars):
    """
    Ensure logout works.
    """
    version = test_vars["version"]
    username = test_vars["username"]

    with client:

        # GET Request tests.
        response = client.get("/logout", follow_redirects=True)
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for("auth.login")
        assert b"Logged out!" in response.data

        # Check content matches login page.
        assert b"Home" in response.data
        assert b"Login" in response.data
        assert b"Username" in response.data
        assert b"Enter Username" in response.data
        assert b"Password" in response.data
        assert b"Enter Password" in response.data
        assert b"Login" in response.data
        assert f"Web LGSM - Version: {version}".encode() in response.data


def test_edit_user_contents(db_session, client, authed_client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]

    with client:

        response = client.get("/edit_users?username=newuser")
        assert response.status_code == 200

        assert b"New User" in response.data
        assert b"test" in response.data
        assert b"User Settings:" in response.data
        assert b"Username" in response.data
        assert b"Password" in response.data
        assert b"Confirm Password" in response.data
        assert b"Admin User - Can do anything in the web interface" in response.data
        assert (
            b"Regular User - Configure limited user permissions below" in response.data
        )
        assert b"Basic Permissions" in response.data
        assert b"Can Install New Game Servers" in response.data
        assert b"Can Add Existing Game Servers" in response.data
        assert b"Can Modify Web-LGSM Settings Page" in response.data
        assert b"Can Edit Game Server Configs" in response.data
        assert b"Can Delete Game Servers" in response.data
        assert b"Allowed Controls" in response.data
        assert b"start" in response.data
        assert b"stop" in response.data
        assert b"restart" in response.data
        assert b"monitor" in response.data
        assert b"test-alert" in response.data
        assert b"details" in response.data
        assert b"postdetails" in response.data
        assert b"update-lgsm" in response.data
        assert b"update" in response.data
        assert b"backup" in response.data
        assert b"console" in response.data
        assert b"send" in response.data
        assert b"Allow Access to Game Servers" in response.data
        assert b"No game servers installed yet" in response.data
        assert (
            b"You can adjust what servers this user has access to after installing or adding a game server"
            in response.data
        )


def test_edit_user_responses(db_session, client, authed_client, test_vars):
    """
    Check responses back from edit_user.
    """
    with client:
        # Test page redirects to username=newuser by default.
        response = client.get("/edit_users", follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == url_for("auth.edit_users")
        csrf_token = get_csrf_token(response)

        # Test cannot edit invalid username.
        invalid_user_data = {
            "csrf_token": csrf_token, 
            "selected_user": "noauser",
            "username": "notauser",
            "password1": "**Testing1234",
            "password2": "**Testing1234",
            "is_admin": "false"
        }
        response = client.post(
            "/edit_users", data=invalid_user_data, follow_redirects=True
        )
#        print(response.data)
        assert response.request.path == url_for("auth.edit_users")
        assert b"Invalid user selected" in response.data

        # Test cannot edit main admin user.
        admin_user_data = {
            "csrf_token": csrf_token, 
            "selected_user": "test",
            "username": "test",
            "password1": "**Testing1234",
            "password2": "**Testing1234",
            "is_admin": "false"
        }
        response = client.post(
            "/edit_users", data=admin_user_data, follow_redirects=True
        )
        assert response.request.path == url_for("auth.edit_users")
        assert b"Cannot modify main admin user" in response.data
        assert b"Anti-lockout protection" in response.data

        # Test add with invalid control supplied.
        invalid_control_user_data = { 
            "csrf_token": csrf_token, 
            "selected_user": "newuser",
            "username": "test2",
            "password1": "**Testing12345",
            "password2": "**Testing12345",
            "is_admin": "false",
            "controls": [
                "start",
                "fart",
                "blah",
                "notacontrolvalue"
            ]
        }
        response = client.post(
            "/edit_users",
            data=invalid_control_user_data,
            follow_redirects=True,
        )
        assert response.request.path == url_for("auth.edit_users")
        assert b"controls:" in response.data
        assert b"are not valid choices for this field." in response.data

        # Test add with invalid server supplied.
        invalid_server_user_data = { 
            "csrf_token": csrf_token, 
            "selected_user": "newuser",
            "username": "test2",
            "password1": "**Testing12345",
            "password2": "**Testing12345",
            "is_admin": "false",
            "server_ids": [
                "fart",
                "blah",
                "notaservervalue"
            ]
        }
        response = client.post(
            "/edit_users",
            data=invalid_server_user_data,
            follow_redirects=True,
        )
        debug_response(response)
        assert response.request.path == url_for("auth.edit_users")
        assert b"server_ids:" in response.data 
        assert b"are not valid choices for this field." in response.data


def test_create_new_user(db_session, client, authed_client, test_vars):
    """
    Tests adding new web interface user.
    """
    username = test_vars["username"]
    password = test_vars["password"]

    with client:
        response = client.get("/edit_users?username=newuser")
        assert response.status_code == 200
        assert response.request.path == url_for("auth.edit_users")
        csrf_token = get_csrf_token(response)

        create_user_data = {
            "csrf_token": csrf_token,
            "selected_user": "newuser",
            "username": "test2",
            "password1": password,
            "password2": password,
            "is_admin": "false",
            "install_servers": "false",
            "add_servers": "false",
            "mod_settings": "false",
            "edit_cfgs": "false",
            "delete_server": "false",
            "controls": []
        }

        response = client.post(
            "/edit_users", data=create_user_data, follow_redirects=True
        )
        assert response.request.path == url_for("views.home")
        assert b"New User Added" in response.data


def test_login_as_new_user(db_session, client, add_second_user_no_perms):
    """
    Tests logging in as user created in last test.

    This test is dependant on the test above it. However, in this case I think
    that's okay since they're really two sides of the same coin.
    """
    with client:
        response = client.get('/login')
        csrf_token = get_csrf_token(response)

        # Log test user in.
        response = client.post(
            "/login", data={"csrf_token":csrf_token, "username": 'test2', "password": "**Testing12345"},
            follow_redirects=True
        )
        assert response.status_code == 200  # 200 bc follow_redirects=True
        assert response.request.path == url_for("views.home")
