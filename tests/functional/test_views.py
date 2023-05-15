import os
import pytest
from flask import url_for, request
from game_servers import game_servers

# Global testing env vars.
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
TEST_SERVER = os.environ['TEST_SERVER']
TEST_SERVER_PATH = os.environ['TEST_SERVER_PATH']
TEST_SERVER_NAME = os.environ['TEST_SERVER_NAME']
CFG_PATH = os.environ['CFG_PATH']
CFG_PATH = os.path.abspath(CFG_PATH)
VERSION = os.environ['VERSION']

# Checks response contains correct error msg.
def check_for_error(response, error_msg, resp_code, url):
    # Is 200 bc follow_redirects=True.
    assert response.status_code == resp_code

    # Check redirect by seeing if path changed.
    assert response.request.path == url_for(url)
    assert error_msg in response.data


### Home Page tests.
# Check basic content matches.
def test_home_content(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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

# Test home responses.
def test_home_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get('/home', follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == '/login' 

    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        response = client.get('/home')
        assert response.status_code == 200  # Return's 200 to GET requests.

        response = client.get('/')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Home Page should only accept GET's.
        response = client.post('/home', data=dict(test=''))
        assert response.status_code == 405  # Return's 405 to POST requests.

        response = client.post('/', data=dict(test=''))
        assert response.status_code == 405  # Return's 405 to POST requests.


### Add page tests.
# Check basic content matches.
def test_add_content(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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

# Test add responses.
def test_add_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get('/add', follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == '/login' 

    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        ## Test empty parameters.
        resp_code = 200
        error_msg = b"Missing required form field(s)!"
        response = client.post('/add', data={'install_name':'', \
            'install_path':'', 'script_name':''}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')

        response = client.post('/add', data={'install_name':'', \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':TEST_SERVER_PATH, 'script_name':''}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':'', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')


        ## Test empty parameters.
        resp_code = 200
        error_msg = b"Missing required form field(s)!"
        response = client.post('/add', data={'install_name':'', \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':TEST_SERVER_PATH, 'script_name':''}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':'', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')


        ## Test upward directory traversal.
        error_msg = b"Only dirs under"
        resp_code = 400
        response = client.post('/add', data={'install_name':'upup_test', \
            'install_path':'../../../../../..', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')

        ## Test unauthorized dir.
        response = client.post('/add', data={'install_name':'root_test', \
            'install_path':'/', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.add')


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


### Controls page tests.
# Check basic content matches.
def test_controls_content(app, client):
    # Login.
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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

# Test add responses.
def test_controls_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get(f'/controls?server={TEST_SERVER}', follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == '/login' 

    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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


### Install Page tests.
# Test install page content.
def test_install_content(app, client):
    # Login.
    with client:
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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

# Test install page responses.
def test_install_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get('/install', follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == '/login' 

    # Login.
    with client:
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        ## Leaving off legit install test(s) for now because that takes a
        # while to run. Only testing bad posts atm.

        ## Test for Missing Required Form Feild error msg.

        # Test for no feilds supplied.
        resp_code = 200
        error_msg = b"Missing Required Form Feild!"
        response = client.post('/install', follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.install')

        # Test no server_name.
        response = client.post('/install', data={'full_name':'', \
                        'sudo_pass':''}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.install')

        # Test no full_name.
        response = client.post('/install', data={'server_name':'', \
                        'sudo_pass':''}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.install')

        # Test no sudo_pass.
        response = client.post('/install', data={'server_name':'', \
                'full_name':''}, follow_redirects=True)

        # Test for empty form fields.
        error_msg = b"Invalid Installation Option(s)!"
        response = client.post('/install', data={'server_name':'', \
                'full_name':'', 'sudo_pass':''}, follow_redirects=True)

        check_for_error(response, error_msg, resp_code, 'views.install')


### Settings page tests.
# Test settings page content.
def test_settings_content(app, client):
    # Login.
    with client:
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

# Test settings page responses.
def test_settings_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get('/settings', follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == '/login' 

    # Login.
    with client:
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # Text color change tests.
        # Only accepts hexcode as text color.
        resp_code = 200
        error_msg = b'Invalid color!'
        response = client.post('/settings', data={'text_color':'test'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        response = client.post('/settings', data={'text_color':'red'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        response = client.post('/settings', data={'text_color':'#aaaaaaaaaaaaaaaa'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        # Legit color change test.
        error_msg = b'Settings Updated!'
        response = client.post('/settings', data={'text_color':'#0ed0fc'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        # Test text area height change.
        # App only accepts textarea height between 5 and 100.
        error_msg = b'Invalid Textarea Height!'
        response = client.post('/settings', data={'text_area_height':'-20'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        response = client.post('/settings', data={'text_area_height':'test'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        response = client.post('/settings', data={'text_area_height':'99999'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        response = client.post('/settings', data={'text_area_height':'-e^(i*3.14)'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')

        # Legit textarea height test.
        error_msg = b'Settings Updated!'
        response = client.post('/settings', data={'text_area_height':'10'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.settings')


### Edit page tests.
# Test edit page basic content.
def test_edit_content(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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

# Test edit page responses.
def test_edit_responses(app, client):
    # Test page redirects to login if user not already authenticated.
    response = client.get('/edit', data={'server':TEST_SERVER, 'cfg_path':CFG_PATH}, follow_redirects=True)
    assert response.status_code == 200  # 200 because follow_redirects=True.
    assert response.request.path == '/login' 

    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

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

        # No server specified tests.
        resp_code = 200
        error_msg = b'No server specified!'
        # Test is none.
        response = client.post('/edit', data={'cfg_path':CFG_PATH}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # Test is null.
        response = client.post('/edit', data={'server':'', 'cfg_path':CFG_PATH}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # No cfg specified tests.
        error_msg = b'No config file specified!'
        # Test is none.
        response = client.post('/edit', data={'server':TEST_SERVER}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # Test is null.
        response = client.post('/edit', data={'server':TEST_SERVER, 'cfg_path':''}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # Invalid game server name test.
        error_msg = b'Invalid game server name!'
        response = client.post('/edit', data={'server':'test', 'cfg_path':CFG_PATH}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # No game server installation directory found test.
        # First move the installation directory to .bak.
        os.rename(TEST_SERVER_PATH, TEST_SERVER_PATH + ".bak")

        error_msg = b'No game server installation directory found!'
        response = client.post('/edit', data={'server':'Minecraft', 'cfg_path':CFG_PATH}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # Finally move the installation back into place.
        os.rename(TEST_SERVER_PATH + ".bak", TEST_SERVER_PATH)

        # Invalid config file name test.
        error_msg = b'Invalid config file name!'
        response = client.post('/edit', data={'server':TEST_SERVER, 'cfg_path':CFG_PATH + 'test'}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')

        # No such file test.
        error_msg = b'No such file!'
        response = client.post('/edit', data={'server':TEST_SERVER, 'cfg_path':'/test' + CFG_PATH}, follow_redirects=True)
        check_for_error(response, error_msg, resp_code, 'views.home')