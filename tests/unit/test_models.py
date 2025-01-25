import os
import pytest
from app.models import User, GameServer

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
APP_PATH = os.environ["APP_PATH"]
APP_PATH = os.path.abspath(APP_PATH)
TEST_SERVER = os.environ["TEST_SERVER"]
TEST_SERVER_PATH = os.environ["TEST_SERVER_PATH"]
TEST_SERVER_NAME = os.environ["TEST_SERVER_NAME"]


@pytest.fixture
def new_user():
    return User(username=USERNAME, password=PASSWORD)


def test_new_user(new_user):
    assert new_user.username == USERNAME
    assert new_user.password == PASSWORD


@pytest.fixture
def new_game_server():
    return GameServer(
        install_name=TEST_SERVER,
        install_path=TEST_SERVER_PATH,
        script_name=TEST_SERVER_NAME,
    )


def test_new_game_server(new_game_server):
    assert new_game_server.install_name == TEST_SERVER
    assert new_game_server.install_path == TEST_SERVER_PATH
    assert new_game_server.script_name == TEST_SERVER_NAME
