import os
import pytest
from app.models import User, GameServer

@pytest.fixture
def new_user(test_vars):
    username = test_vars["username"]
    password = test_vars["username"]
    return User(username=username, password=password)


def test_new_user(new_user, test_vars):
    username = test_vars["username"]
    password = test_vars["username"]
    assert new_user.username == username
    assert new_user.password == password


@pytest.fixture
def new_game_server(test_vars):
    test_server = test_vars["test_server"]
    test_server_path = test_vars["test_server_path"]
    test_server_name = test_vars["test_server_name"]

    return GameServer(
        install_name=test_server,
        install_path=test_server_path,
        script_name=test_server_name,
    )


def test_new_game_server(new_game_server, test_vars):
    test_server = test_vars["test_server"]
    test_server_path = test_vars["test_server_path"]
    test_server_name = test_vars["test_server_name"]

    assert new_game_server.install_name == test_server
    assert new_game_server.install_path == test_server_path
    assert new_game_server.script_name == test_server_name

