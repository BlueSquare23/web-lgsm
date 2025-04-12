import os
import sys
import pytest
import json
import configparser
from app import main

@pytest.fixture
def app():
    app = main()
    app.config.update({"TESTING": True})
    yield app

@pytest.fixture
def client(app):
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

