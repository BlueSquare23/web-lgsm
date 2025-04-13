import os
import subprocess
import pytest
import time

SCRIPT = "./web-lgsm.py"

def test_start_server():
    result = subprocess.run([SCRIPT, "--start"], capture_output=True, text=True)
    assert "Launched Gunicorn server with PID" in result.stdout


def test_stop_server():
    result = subprocess.run([SCRIPT, "--start"], capture_output=True, text=True)
    print(result.stdout)

    # Sleep to ensure the server has started.
    time.sleep(4)
    result = subprocess.run([SCRIPT, "--stop"], capture_output=True, text=True)
    assert "Server Killed!" in result.stdout


def test_check_status_running():
    subprocess.run([SCRIPT, "--start"], capture_output=True, text=True)
    # Sleep to ensure the server has started.
    time.sleep(4)
    result = subprocess.run([SCRIPT, "--status"], capture_output=True, text=True)
    assert "Server Currently Running." in result.stdout
    # Stop server after test.
    subprocess.run([SCRIPT, "--stop"], capture_output=True, text=True)


def test_check_status_not_running():
    result = subprocess.run([SCRIPT, "--status"], capture_output=True, text=True)
    assert "Server Not Running." in result.stdout


def test_update_gs_list():
    result = subprocess.run([SCRIPT, "--fetch_json"], capture_output=True, text=True)
    assert (
        "File game_servers.json JSON updated!" in result.stdout
        or "File game_servers.json JSON already up to date." in result.stdout
    )


def test_print_help():
    result = subprocess.run([SCRIPT, "--help"], capture_output=True, text=True)
    assert "Usage: web-lgsm.py [options]" in result.stdout

