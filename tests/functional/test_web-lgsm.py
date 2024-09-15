import os
import subprocess
import pytest
import time

APP_PATH = os.environ["APP_PATH"]
SCRIPT = os.path.join(APP_PATH, "web-lgsm.py")


@pytest.fixture
def setup_venv():
    # Ensure virtual environment is created for tests.
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    if not os.path.exists(venv_path):
        subprocess.run(["python3", "-m", "venv", "venv"])
        subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"])
    yield


def test_start_server(setup_venv):
    result = subprocess.run([SCRIPT, "--start"], capture_output=True, text=True)
    assert "Launched Gunicorn server with PID" in result.stdout


def test_stop_server(setup_venv):
    subprocess.run([SCRIPT, "--start"], capture_output=True, text=True)
    # Sleep to ensure the server has started.
    time.sleep(2)
    result = subprocess.run([SCRIPT, "--stop"], capture_output=True, text=True)
    assert "Server Killed!" in result.stdout


def test_check_status_running(setup_venv):
    subprocess.run([SCRIPT, "--start"], capture_output=True, text=True)
    # Sleep to ensure the server has started.
    time.sleep(2)
    result = subprocess.run([SCRIPT, "--status"], capture_output=True, text=True)
    assert "Server Currently Running." in result.stdout
    # Stop server after test.
    subprocess.run([SCRIPT, "--stop"], capture_output=True, text=True)


def test_check_status_not_running(setup_venv):
    result = subprocess.run([SCRIPT, "--status"], capture_output=True, text=True)
    assert "Server Not Running." in result.stdout


def test_update_gs_list(setup_venv):
    result = subprocess.run([SCRIPT, "--fetch_json"], capture_output=True, text=True)
    assert (
        "File game_servers.json JSON updated!" in result.stdout
        or "File game_servers.json JSON already up to date." in result.stdout
    )


def test_print_help(setup_venv):
    result = subprocess.run([SCRIPT, "--help"], capture_output=True, text=True)
    assert "Usage: web-lgsm.py [options]" in result.stdout
