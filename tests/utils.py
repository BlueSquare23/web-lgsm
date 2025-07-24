import re
import pwd
from flask import url_for, request
import configparser
from bs4 import BeautifulSoup

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


def toggle_cfg_editor(enable=False):
    """
    Toggle cfg_editor setting in config file.
    """
    config = configparser.ConfigParser()
    config.read("main.conf.local")
    if enable:
        config['settings']['cfg_editor'] = 'yes'
    else:
        config['settings']['cfg_editor'] = 'no'
    with open("main.conf.local", "w") as configfile:
        config.write(configfile)


def toggle_send_cmd(enable=False):
    """
    Toggle send_cmd setting in config file.
    """
    config = configparser.ConfigParser()
    config.read("main.conf.local")
    if enable:
        config['settings']['send_cmd'] = 'yes'
    else:
        config['settings']['send_cmd'] = 'no' 
    with open("main.conf.local", "w") as configfile:
        config.write(configfile)


def check_install_finished(server_id):
    server = GameServer.query.filter_by(id=server_id).first()
    return server.install_finished


def get_server_id(server_name):
    server = GameServer.query.filter_by(install_name=server_name).first()
    return server.id


def get_csrf_token(response):
    # Parse the HTML to get the CSRF token.
    html = response.data.decode()
    return re.search(
        r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', html 
    ).group(1)


def check_for_error(response, error_msg, url, code=200):
    """ 
    Checks response contains correct error msg and redirects to the right page.
    """
    # Is 200 bc follow_redirects=True.
    assert response.status_code == code

    # Check redirect by seeing if path changed.
    assert response.request.path == url_for(url)
    assert error_msg in response.data


def page_requires_auth(client, page=''):
    """
    Tests that supplied page requires authentication. All unauthed reqs should
    return to login.
    """
    response = client.get(page)
    assert response.status_code == 302

    response = client.get(page, follow_redirects=True)
    assert response.status_code == 200  # 200 bc follow_redirects=True
    debug_response(response)
    assert response.request.path == url_for("auth.login")


def extract_alert_messages(response, alert_type=None):
    """
    Extracts messages from alert divs (both error and success).
    
    Args:
        response: Response object from test request.
        alert_type: Optional filter - 'danger', 'success', or None for both
        
    Returns:
        List of message strings
    """
    html_text = response.data.decode('utf-8')
    soup = BeautifulSoup(html_text, 'html.parser')
    messages = []

    # Find all alert divs (both danger and success)
    alert_divs = soup.find_all('div', class_='alert')

    for div in alert_divs:
        # Check if it's a alert-dismissible alert.
        if 'alert-dismissible' not in div.get('class', []):
            continue

        # Filter by type if specified.
        if alert_type and f'alert-{alert_type}' not in div.get('class', []):
            continue

        # Extract text and clean it.
        text = div.get_text()
        # Remove button text and extra whitespace
        message = ' '.join(text.split()).replace('×', '').strip()
        if message:  # Only add non-empty messages
            messages.append(message)

    return messages


def user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

