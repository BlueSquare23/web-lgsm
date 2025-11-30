import os
import sys
import pytest
import json
import shutil
import getpass
import configparser
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import User, GameServer, Job
from app.services import CronService
from utils import *


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def reset(app):
    # Reset config file.
    os.system('git restore main.conf')
    shutil.copyfile("main.conf", "main.conf.local")

    # Reset crontab.
    os.system('crontab -r')


@pytest.fixture
def client(app, reset):
    # Reset config file.
    os.system('git restore main.conf')
    shutil.copyfile("main.conf", "main.conf.local")
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a clean database with proper transaction isolation for each test."""
    with app.app_context():
        from app import db

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
        test_vars = json.load(f)

    return test_vars


@pytest.fixture()
def test_config():
    """Load vars once per test session"""
    # Import config data.
    test_config = configparser.ConfigParser()
    config_file = "main.conf.local"  # Local config override.
    test_config.read(config_file)

    return test_config


@pytest.fixture()
def setup_client(db_session, test_vars):
    # Create initial user directly in database
    user = User(
        username=test_vars["username"],
        password=generate_password_hash(test_vars["password"], method="pbkdf2:sha256"),
        role="admin",
        permissions=json.dumps({"admin": True}),
    )
    db_session.session.add(user)
    db_session.session.commit()
    return client


@pytest.fixture()
def authed_client(client, setup_client, test_vars):
    # Login the client (still needs HTTP request for session)
    response = client.get("/login")
    csrf_token = get_csrf_token(response)

    response = client.post("/login",
        data={
            "username": test_vars["username"],
            "password": test_vars["password"],
            "csrf_token": csrf_token,
        },
        follow_redirects=True)
    assert response.status_code == 200
    return client


@pytest.fixture()
def add_mock_server(db_session, test_vars):
    test_server = test_vars["test_server"]
    test_server_path = os.path.join(os.getcwd(), test_vars["test_server_path"])
    test_server_name = test_vars["test_server_name"]
    cfg_dir = os.path.join(os.getcwd(), test_vars["cfg_dir"])

    if os.path.isdir(test_server_path + '.bak'):
        shutil.rmtree(test_server_path + '.bak')

    # Setup Mockcraft testdir.
    if not os.path.isdir(test_server_path) or not os.path.isdir(cfg_dir):
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

    # Create server directly in database
    server = GameServer(
        install_type='local',
        install_name=test_server,
        install_path=test_server_path,
        script_name=test_server_name,
        username=getpass.getuser(),
        install_host="127.0.0.1",
        is_container=False,
        install_finished=True
    )
    db_session.session.add(server)
    db_session.session.commit()

    return client


@pytest.fixture()
def add_second_user_no_perms(db_session, setup_client, test_vars):
    # Create second user with no permissions
    user = User(
        username="test2",
        password=generate_password_hash(test_vars["password"]),
        role="user",
        permissions=json.dumps({
            "install_servers": False, 
            "add_servers": False, 
            "mod_settings": False, 
            "edit_cfgs": False, 
            "edit_jobs": False, 
            "delete_server": False, 
            "controls": [], 
            "server_ids": []
        }),
    )
    db_session.session.add(user)
    db_session.session.commit()

    return client


@pytest.fixture()
def user_authed_client_no_perms(client, add_second_user_no_perms, test_vars):
    # Login the client (still needs HTTP request for session)
    response = client.get("/login")
    csrf_token = get_csrf_token(response)

    # Login as second user (still needs HTTP request)
    response = client.post(
        "/login", 
        data={"csrf_token":csrf_token, "username": "test2", "password": test_vars["password"]},
        follow_redirects=True
    )
    assert response.status_code == 200
    return client


@pytest.fixture()
def add_second_user_all_perms(db_session, add_mock_server, test_vars):
    test_server = test_vars["test_server"]
    server_id = get_server_id(test_server)

    # Create second user with all permissions
    user = User(
        username="test2",
        password=generate_password_hash(test_vars["password"]),
        role="user",
        permissions=json.dumps({
            "install": True,
            "add": True,
            "settings": True,
            "edit": True,
            "jobs": True,
            "delete": True,
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
        }),
    )
    db_session.session.add(user)
    db_session.session.commit()

    return client


@pytest.fixture()
def user_authed_client_all_perms(client, add_second_user_all_perms, test_vars):
    # Login the client (still needs HTTP request for session)
    response = client.get("/login")
    csrf_token = get_csrf_token(response)

    # Login as second user (still needs HTTP request)
    response = client.post(
        "/login", 
        data={"csrf_token":csrf_token, "username": "test2", "password": test_vars["password"]},
        follow_redirects=True
    )
    assert response.status_code == 200
    return client


@pytest.fixture()
def add_mock_cron_job(client, test_vars):
    test_server = test_vars["test_server"]
    server_id = get_server_id(test_server)
    cron_service = CronService(server_id=server_id)

    # Create a test job first
    job_data = {
        "job_id": None,
        "server_id": server_id,
        "command": "echo 'delete me'",
        "comment": "Delete test",
        "expression": "* * * * *"
    }
    cron_service.edit_job(job_data)
    jobs_list = cron_service.list_jobs()
    job_id = jobs_list[0]["job_id"]

    # Verify job exists
    assert Job.query.filter_by(id=job_id).first() is not None
    test_vars["job_id"] = job_id

    return client

