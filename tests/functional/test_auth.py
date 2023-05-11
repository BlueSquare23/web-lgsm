import os
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
        response = client.post('/setup', data={'username':USERNAME, 'password1':'blah', 'password2':'blah'})
        # 400 bc bad form request.
        assert response.status_code == 400
        assert b"Passwords doesn&#39;t meet criteria!" in response.data

        ## Tests username contains bad char(s).
        def test_username_bad_chars(response):
            # No redirect on setup.
            assert response.status_code == 400

            # Check redirect by seeing if path changed.
            assert response.request.path == url_for('auth.setup')
            assert b"Username Contains Illegal Character(s)" in response.data

        bad_chars = { " ", "$", "'", '"', "\\", "#", "=", "[", "]", "!", "<", ">",
                      "|", ";", "{", "}", "(", ")", "*", ",", "?", "~", "&" }

        for char in bad_chars:
            response = client.post('/setup', data={'username':char, \
                        'password1':PASSWORD, 'password2':PASSWORD})
            test_username_bad_chars(response)

        # Test passwords don't match.
        response = client.post('/setup', data={'username':USERNAME, \
                        'password1':PASSWORD, 'password2':'blah'})
        # No redirect on setup.
        assert response.status_code == 400
        assert b"Passwords don&#39;t match!" in response.data

        # Test password too short.
        response = client.post('/setup', data={'username':USERNAME, \
                        'password1':'Ab3$', 'password2':'Ab3$'})
        # No redirect on setup.
        assert response.status_code == 400
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

