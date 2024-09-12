import os
import json
import pytest
from flask import url_for, request
from game_servers import game_servers

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
TEST_SERVER = os.environ['TEST_SERVER']
TEST_SERVER_PATH = os.environ['TEST_SERVER_PATH']
TEST_SERVER_NAME = os.environ['TEST_SERVER_NAME']
VERSION = os.environ['VERSION']

# Checks response contains correct error msg and redirects to the right page.
def check_for_error(response, error_msg, url):
    # Is 200 bc follow_redirects=True.
    assert response.status_code == 200

    # Check redirect by seeing if path changed.
    assert response.request.path == url_for(url)
    assert error_msg in response.data


### Setup Page tests.
# Test setup page contents.
def test_setup_contents(app, client):
    with client:
        response = client.get('/setup')
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
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data

# Test setup page responses.
def test_setup_responses(app, client):
    with client:
        response = client.get('/setup')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Using follow_redirects=True bc only redirect on setup page is for
        # missing required args. The rest fall through to the render_template
        # statement with a 200.

        # Test with empty args.
        error_msg = b"Missing required form field(s)!"
        response = client.post('/setup', data={'username':'', 'password1':'', 'password2':''}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        response = client.post('/setup', data={'username':'a', 'password1':'a', 'password2':''}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        response = client.post('/setup', data={'username':'', 'password1':'a', 'password2':'a'}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        # Test with no args.
        response = client.post('/setup', data={}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        # Form field too long test.
        # First create a string that's too long for the form fields.
        too_long = 'a'
        count = 0
        while count < 150:
            too_long += 'a'
            count += 1

        error_msg = b'Form field too long!'
        response = client.post('/setup', data={'username':too_long, \
            'password1':PASSWORD, 'password2':PASSWORD}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        response = client.post('/setup', data={'username':USERNAME, \
            'password1':too_long, 'password2':PASSWORD}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        response = client.post('/setup', data={'username':USERNAME, \
            'password1':PASSWORD, 'password2':too_long}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.setup')

        ## Tests for if password doesn't meet criteria.
        # Test needs uppercase, lowercase, and special char.
        response = client.post('/setup', data={'username':USERNAME, 'password1':'blah', 'password2':'blah'}, follow_redirects=True)
        assert b"Passwords doesn&#39;t meet criteria!" in response.data

        ## Tests username contains bad char(s).
        def test_username_bad_chars(response):
            # Check redirect by seeing if path changed.
            assert response.request.path == url_for('auth.setup')
            assert b"Username Contains Illegal Character(s)" in response.data

        bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                      "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }

        for char in bad_chars:
            response = client.post('/setup', data={'username':char, 'password1':PASSWORD, 'password2':PASSWORD}, follow_redirects=True)
            test_username_bad_chars(response)

        # Test passwords don't match.
        response = client.post('/setup', data={'username':USERNAME, 'password1':PASSWORD, 'password2':'blah'}, follow_redirects=True)
        # No redirect on setup.
        assert b"Passwords don&#39;t match!" in response.data

        # Test password too short.
        response = client.post('/setup', data={'username':USERNAME, 'password1':'Ab3$', 'password2':'Ab3$'},  follow_redirects=True)
        # No redirect on setup.
        assert b"Password is too short!" in response.data

        # Try to request the login page, should get redirected to setup.
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200  # 200 because follow_redirects=True.
        assert response.request.path == url_for(f'auth.setup')
        assert b'Please add a user!' in response.data

        # Finally, create real test user.
        response = client.post('/setup', data={'username':USERNAME, \
                     'password1':PASSWORD, 'password2':PASSWORD})
        assert response.status_code == 302

        # Test user already added!
        error_msg = b"User already added. Please sign in!"
        response = client.post('/setup', data={'username':USERNAME, \
        'password1':PASSWORD, 'password2':PASSWORD}, follow_redirects=True)
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for(f'auth.login')
        assert error_msg in response.data


### Login Page tests.
# Test login page contents.
def test_login_contents(app, client):
    with client:
        response = client.get('/login')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
        assert b"Home" in response.data
        assert b"Login" in response.data
        assert b"Username" in response.data
        assert b"Enter Username" in response.data
        assert b"Password" in response.data
        assert b"Enter Password" in response.data
        assert b"Login" in response.data
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data

# Test login page responses.
def test_login_responses(app, client):
    with client:
        response = client.get('/login')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Test empty args.
        error_msg = b"Missing required form field(s)!"
        response = client.post('/login', data={'username':'', 'password':''}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.login')

        response = client.post('/login', data={'username':USERNAME, 'password':''}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.login')

        response = client.post('/login', data={'username':'', 'password':PASSWORD}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.login')

        # Form field too long test.
        # First create a string that's too long for the form fields.
        too_long = 'a'
        count = 0
        while count < 150:
            too_long += 'a'
            count += 1

        error_msg = b'Form field too long!'
        response = client.post('/login', data={'username':too_long, \
            'password':PASSWORD}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.login')

        response = client.post('/login', data={'username':USERNAME, \
            'password':too_long}, follow_redirects=True)
        check_for_error(response, error_msg, 'auth.login')

        # Finally, log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302


### Logout page tests.
def test_logout(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # GET Request tests.
        response = client.get('/logout', follow_redirects=True)
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('auth.login')
        assert b"Logged out!" in response.data

        # Check content matches login page.
        assert b"Home" in response.data
        assert b"Login" in response.data
        assert b"Username" in response.data
        assert b"Enter Username" in response.data
        assert b"Password" in response.data
        assert b"Enter Password" in response.data
        assert b"Login" in response.data
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


def test_edit_user_contents(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        response = client.get('/edit_users?username=newuser')
        assert response.status_code == 200

        assert b"New User" in response.data
        assert b"test" in response.data
        assert b"User Settings:" in response.data
        assert b"Username" in response.data
        assert b"Password" in response.data
        assert b"Confirm Password" in response.data
        assert b"Admin User - Can do anything in the web interface" in response.data
        assert b"Regular User - Configure limited user permissions below" in response.data
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
        assert b"You can adjust what servers this user has access to after installing or adding a game server" in response.data

def test_edit_user_responses(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # Test page redirects to username=newuser by default.
        response = client.get('/edit_users', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == url_for('auth.edit_users')

        # Test cannot edit invalid username.
        invalid_user_json = """{
            "selected_user": "noauser",
            "username": "notauser",
            "password1": "",
            "password2": "",
            "is_admin": "false"
        }"""
        response = client.post('/edit_users', data=json.loads(invalid_user_json), follow_redirects=True)
        print(response.data)
        assert response.request.path == url_for('auth.edit_users')
        assert b"Invalid user selected" in response.data

        # Test cannot edit main admin user.
        admin_user_json = """{
            "selected_user": "test",
            "username": "test",
            "password1": "",
            "password2": "",
            "is_admin": "false"
        }"""
        response = client.post('/edit_users', data=json.loads(admin_user_json), follow_redirects=True)
        assert response.request.path == url_for('auth.edit_users')
        assert b"Cannot modify main admin user" in response.data
        assert b"Anti-lockout protection" in response.data
        
        # Test add with invalid control supplied.
        invalid_control_user_json = """{
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
        }"""
        response = client.post('/edit_users', data=json.loads(invalid_control_user_json), follow_redirects=True)
        assert response.request.path == url_for('auth.edit_users')
        assert b"Invalid Control Supplied" in response.data

        # Test add with invalid server supplied.
        invalid_server_user_json = """{
            "selected_user": "newuser",
            "username": "test2",
            "password1": "**Testing12345",
            "password2": "**Testing12345",
            "is_admin": "false",
            "servers": [
                "fart",
                "blah",
                "notaservervalue"
            ]
        }"""
        response = client.post('/edit_users', data=json.loads(invalid_server_user_json), follow_redirects=True)
        assert response.request.path == url_for('auth.edit_users')
        assert b"Invalid Server Supplied" in response.data

def test_create_new_user(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        response = client.get('/edit_users?username=newuser')
        assert response.status_code == 200

        create_user_json = """{
            "selected_user": "newuser",
            "username": "test2",
            "password1": "**Testing12345",
            "password2": "**Testing12345",
            "is_admin": "false",
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
            ]
        }"""

        response = client.post('/edit_users', data=json.loads(create_user_json), follow_redirects=True)
        assert response.request.path == url_for('views.home')
        assert b"New User Added" in response.data


