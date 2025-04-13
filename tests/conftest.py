import os
import sys
import pytest
import json
import shutil
import configparser

from app import main
from app.models import User, GameServer

# TODO: Move all these shared functions that are Not pytest fixtures into a
# test_utils.py file. There's other functions in test files too should just all
# be copied into one utils file and imported rather than dupe code.

def get_server_id(server_name):
    server = GameServer.query.filter_by(install_name=server_name).first()
#    server = db.session.query.filter_by(install_name=server_name).first()
    return server.id

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


@pytest.fixture
def app():
    app = main()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    # Reset config file.
    shutil.copyfile("main.conf", "main.conf.local")
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a clean database with proper transaction isolation for each test."""
    with app.app_context():
        from app.models import db

        # Drop and create all tables fresh.
        db.drop_all()
        db.create_all()

        # Establish a transaction.
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind the session to this specific connection.
        db.session = db._make_scoped_session(options={
            'bind': connection,
            'binds': {}
        })

        yield db

        # Clean up (undo all test changes).
        transaction.rollback()
        connection.close()
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="session")
def test_vars():
    """Load vars once per test session"""
    with open("tests/test_vars.json", "r") as f:
        config = json.load(f)

    return config


@pytest.fixture()
def config():
    """Load vars once per test session"""
    # Import config data.
    config = configparser.ConfigParser()
    config_file = "main.conf.local"  # Local config override.
    config.read(config_file)

    return config


@pytest.fixture()
def setup_client(client, test_vars):
    # First setup user.
    client.post("/setup",
        data={
            "username": test_vars["username"],
            "password1": test_vars["password"],
            "password2": test_vars["password"]
        },
        follow_redirects=True)

    return client


@pytest.fixture()
def authed_client(client, test_vars):
    # First setup user.
    client.post("/setup",
        data={
            "username": test_vars["username"],
            "password1": test_vars["password"],
            "password2": test_vars["password"]
        },
        follow_redirects=True)

    # Then login.
    response = client.post("/login",
        data={
            "username": test_vars["username"],
            "password": test_vars["password"],
        },
        follow_redirects=True)
    assert response.status_code == 200

    return client


@pytest.fixture()
def add_mock_server(db_session, client, authed_client, test_vars):
    test_server = test_vars["test_server"]
    test_server_path = os.path.join(os.getcwd(), test_vars["test_server_path"])
    test_server_name = test_vars["test_server_name"]
    cfg_dir = os.path.join(os.getcwd(), test_vars["cfg_dir"])

    # Setup Mockcraft testdir.
    if not os.path.isdir(test_server_path) or not os.path.isdir(cfg_dir):
        # will make test_server_path dir in the process.
        os.makedirs(cfg_dir)

    # Reset script file if missing.
    pwd = os.getcwd()
    script_file = os.path.join(test_server_path, "mcserver")
    if not os.path.isfile(script_file):
        os.chdir(test_server_path)
        os.system("wget -O linuxgsm.sh https://linuxgsm.sh")
        os.system("chmod +x linuxgsm.sh")
        os.system("./linuxgsm.sh mcserver")
        os.chdir(pwd)

    # Reset the conf.
    common_cfg = "tests/test_data/common.cfg"
    shutil.copy(common_cfg, cfg_dir)

    response = client.post(
        "/add",
        data={
            "install_type": "local",
            "install_name": test_server, 
            "install_path": test_server_path,
            "script_name": test_server_name,
            "install_host": 'localhost',
        },
        follow_redirects=True,
    )
    # Is 200 bc follow_redirects=True.
    assert response.status_code == 200
#    debug_response(response)
    assert b'Game server added' in response.data

    return client

# TODO: Refactor below four functions. These need to interact with the DB
# directly but I don't have time to do that rn. I also might be able to use a
# factory to return _create_user instead of doing all this.

@pytest.fixture()
def add_second_user_no_perms(add_mock_server, client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]

    # First setup user.
    client.post("/setup",
        data={
            "username": username,
            "password1": password,
            "password2": password
        },
        follow_redirects=True)

    # Then login.
    response = client.post("/login",
        data={
            "username": test_vars["username"],
            "password": test_vars["password"],
        },
        follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/edit_users?username=newuser")
    assert response.status_code == 200

    create_user_json = f"""{{
        "selected_user": "newuser",
        "username": "test2",
        "password1": "{password}",
        "password2": "{password}",
        "is_admin": "false",
        "install_servers": "false",
        "add_servers": "false",
        "mod_settings": "false",
        "edit_cfgs": "false",
        "delete_server": "false",
        "controls": []
    }}"""

    # Then create new user.
    response = client.post(
        "/edit_users", data=json.loads(create_user_json), follow_redirects=True
    )
#    debug_response(response)
    assert response.request.path == '/home'
    assert b"New User Added" in response.data

    return client

@pytest.fixture()
def user_authed_client_no_perms(add_second_user_no_perms, client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]

    # Then logout.
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Finally, login as new user.
    response = client.post(
        "/login", data={"username": 'test2', "password": password},
        follow_redirects=True
    )
    assert response.status_code == 200  # 200 bc follow_redirects=True
    assert response.request.path == '/home'

    return client

@pytest.fixture()
def add_second_user_all_perms(add_mock_server, client, test_vars):
    test_server = test_vars["test_server"]
    username = test_vars["username"]
    password = test_vars["password"]

    # First setup user.
    client.post("/setup",
        data={
            "username": username,
            "password1": password,
            "password2": password
        },
        follow_redirects=True)

    # Then login.
    response = client.post("/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True)
    assert response.status_code == 200

    response = client.get("/edit_users?username=newuser")
    assert response.status_code == 200

    server_id = get_server_id(test_server)

#    create_user_json = f"""{{
#        "selected_user": "newuser",
#        "username": "test2",
#        "password1": "{password}",
#        "password2": "{password}",
#        "is_admin": "false",
#        "install_servers": "false",
#        "add_servers": "false",
#        "mod_settings": "false",
#        "edit_cfgs": "false",
#        "delete_server": "false",
#        "controls": []
#    }}"""

    create_user_json = f"""{{
        "selected_user": "newuser",
        "username": "test2",
        "password1": "{password}",
        "password2": "{password}",
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

    # Then create new user.
    response = client.post(
        "/edit_users", data=json.loads(create_user_json), follow_redirects=True
    )
#    debug_response(response)
    assert response.request.path == '/home'
    assert b"New User Added" in response.data

    return client

@pytest.fixture()
def user_authed_client_all_perms(add_second_user_all_perms, client, test_vars):
    username = test_vars["username"]
    password = test_vars["password"]

    # Then logout.
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Finally, login as new user.
    response = client.post(
        "/login", data={"username": 'test2', "password": password},
        follow_redirects=True
    )
    assert response.status_code == 200  # 200 bc follow_redirects=True
    assert response.request.path == '/home'

    return client

