import os
import pytest
from flask import url_for, request
from game_servers import game_servers
from pathlib import Path
from dotenv import load_dotenv

# Source env vars.
env_path = Path('.') / 'tests/test_data/test.env'
load_dotenv(dotenv_path=env_path)

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
TEST_SERVER = os.environ['TEST_SERVER']
TEST_SERVER_PATH = os.environ['TEST_SERVER_PATH']
TEST_SERVER_NAME = os.environ['TEST_SERVER_NAME']
CFG_PATH = os.environ['CFG_PATH']
VERSION = os.environ['VERSION']

def login(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

### Home Page tests.
# Test home responses.
def test_home_responses(app, client):
    login(app, client)
    response = client.get('/home')
    assert response.status_code == 200  # Return's 200 to GET requests.

    response = client.get('/')
    assert response.status_code == 200  # Return's 200 to GET requests.

    # Home Page should only accept GET's.
    response = client.post('/home', data=dict(test=''))
    assert response.status_code == 405  # Return's 405 to POST requests.

    response = client.post('/', data=dict(test=''))
    assert response.status_code == 405  # Return's 405 to POST requests.

# Check basic content matches.
def test_home_content(app, client):
    login(app, client)
    response = client.get('/home')
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


## Test home page.
#def test_home(app, client):
#    with client:
#        # Log test user in.
#        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
#        assert response.status_code == 302
#
#        ### Home Page GET Request tests.
#        ## Check basic content matches.
#        response = client.get('/home')
#        assert response.status_code == 200  # Return's 200 to GET requests.
#
#        # Check strings on page match.
#        assert b"Home" in response.data
#        assert b"Settings" in response.data
#        assert b"Logout" in response.data
#        assert b"Installed Servers" in response.data
#        assert b"Other Options" in response.data
#        assert b"Install a New Game Server" in response.data
#        assert b"Add an Existing LGSM Installation" in response.data
#        assert f"Web LGSM - Version: {VERSION}".encode() in response.data
#
#
#        ### Home Page POST Request test (should only accept GET's).
#        response = client.post('/home', data=dict(test=''))
#        assert response.status_code == 405  # Return's 405 to POST requests.
#
#        response = client.post('/', data=dict(test=''))
#        assert response.status_code == 405  # Return's 405 to POST requests.


# Test add page.
def test_add(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        ### Add page GET Request tests.
        ## Check basic content matches.
        response = client.get('/add')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check strings on page match.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Add Existing LGSM Installation" in response.data
        assert b"Installation Title" in response.data
        assert b"Enter a unique name for this install" in response.data
        assert b"Installation Directory Path" in response.data
        assert b"Enter the full path to the game server directory" in response.data
        assert b"LGSM Script Name" in response.data
        assert b"Enter the name of the game server script" in response.data
        assert b"Submit" in response.data
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


        ### Add Page Post Request tests.

        # Checks response contains correct error msg.
        def check_for_error(response, error_msg, resp_code):
            # Is 200 bc follow_redirects=True.
            assert response.status_code == resp_code

            # Check redirect by seeing if path changed.
            assert response.request.path == url_for(f'views.add')
            assert error_msg in response.data

        ## Test empty parameters.
        resp_code = 200
        error_msg = b"Missing required form field(s)!"
        response = client.post('/add', data={'install_name':'', \
            'install_path':'', 'script_name':''}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code)

        response = client.post('/add', data={'install_name':'', \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code)

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':TEST_SERVER_PATH, 'script_name':''}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code)

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':'', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code)


        ## Test empty parameters.
        resp_code = 200
        error_msg = b"Missing required form field(s)!"
        response = client.post('/add', data={'install_name':'', \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code)

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':TEST_SERVER_PATH, 'script_name':''}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code)

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':'', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code)


        ## Test upward directory traversal.
        error_msg = b"Only dirs under"
        response = client.post('/add', data={'install_name':'upup_test', \
            'install_path':'../../../../../..', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, 400)

        ## Test unauthorized dir.
        response = client.post('/add', data={'install_name':'root_test', \
            'install_path':'/root', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, 400)


        ## Test legit server add.
        response = client.post('/add', data={'install_name':TEST_SERVER, \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                       follow_redirects=True)
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('views.home')
        assert b"Game server added!" in response.data


        ## Bad char tests.
        # Checks response to see if it contains bad chars msg.
        def contains_bad_chars(response):
            # 200 bc redirect.
            assert response.status_code == 200

            # Check redirect by seeing if path changed.
            assert response.request.path == url_for('views.add')
            assert b"Illegal Character Entered!" in response.data

        bad_chars = { "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                      "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }

        # Test all three fields on add page reject bad chars.
        for char in bad_chars:

            response = client.post('/add', data={'install_name':char, \
                'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                       follow_redirects=True)
            contains_bad_chars(response)

            response = client.post('/add', data={'install_name':TEST_SERVER, \
                    'install_path':char, 'script_name':TEST_SERVER_NAME}, \
                                                       follow_redirects=True)
            contains_bad_chars(response)

            response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':TEST_SERVER_PATH, 'script_name':char}, \
                                                       follow_redirects=True)
            contains_bad_chars(response)


        ## Test install already exists.
        # Do a legit server add.
        response = client.post('/add', data={'install_name':TEST_SERVER, \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME})

        # Is 400 bc bad request.
        assert response.status_code == 400
        assert b"An installation by that name already exits." in response.data


# Test controls page.
def test_controls(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        ### Controls GET Request tests.
        ## Check basic content matches.
        response = client.get(f'/controls?server={TEST_SERVER}')
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
        short_cmds = ["st", "sp", "r", "m", "ta", "dt", "pd", "ul", "u", "b", "c", "do"]
        for cmd in short_cmds:
            assert f"{cmd}".encode() in response.data

        long_cmds = ["start", "stop", "restart", "monitor", "test-alert", \
        "details", "postdetails", "update-lgsm", "update", "backup", "console", \
        "donate"]
        for cmd in long_cmds:
            assert f"{cmd}".encode() in response.data

        # Check descriptions are all there.
        descriptions = [ "Start the server.",
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
          "Donation options."
        ]

        for description in descriptions:
            assert f"{description}".encode() in response.data

        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


        ## Test no params.
        response = client.get(f'/controls', follow_redirects=True)

        # Should redirect to home. 200 bc
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('views.home')
        assert b"No server specified!" in response.data


        ## Test empty server name.
        response = client.get(f'/controls?server=', follow_redirects=True)

        # Should redirect to home. 200 bc
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('views.home')
        assert b"Invalid game server name!" in response.data
        
        ## Test invalid server name.
        response = client.get(f'/controls?server=Blah', follow_redirects=True)

        # Should redirect to home. 200 bc
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('views.home')
        assert b"Invalid game server name!" in response.data


        ## Test No game server installation directory error.
        # First move the installation directory to .bak.
        os.rename(TEST_SERVER_PATH, TEST_SERVER_PATH + ".bak")

        # Then test going to the game server dir.
        response = client.get(f'/controls?server={TEST_SERVER}', follow_redirects=True)

        # Should redirect to home. 200 bc
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('views.home')
        assert b"No game server installation directory found!" in response.data

        # Finally move the installation back into place.
        os.rename(TEST_SERVER_PATH + ".bak", TEST_SERVER_PATH)


        ### Controls Page POST Request test (should only accept GET's).
        response = client.post('/controls', data=dict(test=''))
        assert response.status_code == 405  # Return's 405 to POST requests.


# Test install page.
def test_install(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        ### Install Page GET Request tests.
        ## Check basic content matches.
        response = client.get('/install')
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


        ### Install Page Post Request tests.
        ## Leaving off legit install test(s) for now because that takes a
        # while to run. Only testing bad posts atm.

        ## Test for Missing Required Form Feild error msg.
        # Checks response contains correct error msg.
        def check_for_error(response, error_msg):
            # 200 w/ redirect bc follow_redirects=True.
            assert response.status_code == 200

            # Check redirect by seeing if path changed.
            assert response.request.path == url_for('views.install')
            assert error_msg in response.data

        # Test for no feilds supplied.
        error_msg = b"Missing Required Form Feild!"
        response = client.post('/install', follow_redirects=True)
        check_for_error(response, error_msg)

        # Test no server_name.
        response = client.post('/install', data={'full_name':'', \
                        'sudo_pass':''}, follow_redirects=True)
        check_for_error(response, error_msg)

        # Test no full_name.
        response = client.post('/install', data={'server_name':'', \
                        'sudo_pass':''}, follow_redirects=True)
        check_for_error(response, error_msg)

        # Test no sudo_pass.
        response = client.post('/install', data={'server_name':'', \
                'full_name':''}, follow_redirects=True)

        # Test for empty form fields.
        error_msg = b"Invalid Installation Option(s)!"
        response = client.post('/install', data={'server_name':'', \
                'full_name':'', 'sudo_pass':''}, follow_redirects=True)

        check_for_error(response, error_msg)


# Test settings page.
def test_settings(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # GET Request tests.
        response = client.get('/settings')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Web LGSM Settings" in response.data
        assert b"Output Text Color" in response.data
        assert b"Remove Game Server Files on Delete" in response.data
        assert b"Leave Game Server Files on Delete" in response.data
        assert b"Apply" in response.data
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data


# Test Edit page.
def test_edit(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        ## POST Request tests.
        # Basic page load test.
        response = client.get('/edit', data={'server':TEST_SERVER, 'cfg_path':CFG_PATH})
        assert response.status_code == 200  # Return's 200 to GET requests.

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

        ## Edit testing.
        # Test if edits are saved.
        response = client.get('/edit', data={'server':TEST_SERVER, 'cfg_path':CFG_PATH, 'file_contents':'#### Testing...'})
        assert response.status_code == 200  # Return's 200 to GET requests.

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
        response = client.get('/edit', data={'server':TEST_SERVER, 'cfg_path':CFG_PATH, 'download':'yes'})
        assert response.status_code == 200  # Return's 200 to GET requests.
