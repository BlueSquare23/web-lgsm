import pytest
from flask import url_for, request
from game_servers import game_servers

USERNAME = 'test'
PASSWORD = '**Testing12345'
TEST_SERVER = 'Minecraft'
TEST_SERVER_PATH = '/home/bluesquare23/Projects/new/web-lgsm/Minecraft'
TEST_SERVER_NAME = 'mcserver'
VERSION = 1.1

# Test home page.
def test_home(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # GET Request tests.
        response = client.get('/home')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
        assert b"Home" in response.data
        assert b"Settings" in response.data
        assert b"Logout" in response.data
        assert b"Installed Servers" in response.data
        assert b"Other Options" in response.data
        assert b"Install a New Game Server" in response.data
        assert b"Add an Existing LGSM Installation" in response.data
        assert f"Web LGSM - Version: {VERSION}".encode() in response.data

        # POST Request test, home page should only accept GETs.
        response = client.post('/home', data=dict(test=''))
        assert response.status_code == 405  # Return's 405 to POST requests.

        response = client.post('/', data=dict(test=''))
        assert response.status_code == 405  # Return's 405 to POST requests.

# Test add page.
def test_add(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # GET Request tests.
        response = client.get('/add')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
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

        # Tests with empty strings, helper function.
        def test_empty(response):
            # Is 200 bc follow_redirects=True.
            assert response.status_code == 200
        
            # Check redirect by seeing if path changed.
            assert response.request.path == url_for(f'views.add')
            assert b"Missing required form field(s)!" in response.data

        # Post Request tests.
        # Test empty parameters.
        response = client.post('/add', data={'install_name':'', \
            'install_path':'', 'script_name':''}, follow_redirects=True)
        test_empty(response)

        response = client.post('/add', data={'install_name':'', \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        test_empty(response)

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':TEST_SERVER_PATH, 'script_name':''}, \
                                                    follow_redirects=True)
        test_empty(response)

        response = client.post('/add', data={'install_name':TEST_SERVER, \
                     'install_path':'', 'script_name':TEST_SERVER_NAME}, \
                                                    follow_redirects=True)
        test_empty(response)

        # Test legit server add.
        response = client.post('/add', data={'install_name':TEST_SERVER, \
            'install_path':TEST_SERVER_PATH, 'script_name':TEST_SERVER_NAME}, \
                                                       follow_redirects=True)
        # Is 200 bc follow_redirects=True.
        assert response.status_code == 200

        # Check redirect by seeing if path changed.
        assert response.request.path == url_for('views.home')
        assert b"Game server added!" in response.data

        # Tests add fields contains bad char(s).
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

        # Test install already exists.
        # Test legit server add.
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

        # GET Request tests.
        response = client.get(f'/controls?server={TEST_SERVER}')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
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


# Test install page.
def test_install(app, client):
    with client:
        # Log test user in.
        response = client.post('/login', data={'username':USERNAME, 'password':PASSWORD})
        assert response.status_code == 302

        # GET Request tests.
        response = client.get('/install')
        assert response.status_code == 200  # Return's 200 to GET requests.

        # Check content matches.
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