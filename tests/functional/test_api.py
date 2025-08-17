import json
import pytest
from flask import url_for
from app.models import GameServer
from utils import *

# TODO: Put each set of functions in their own classes. Then can call them with
# pytest based on the test they're in to run just the api tests for 'cron' for
# example.

### Helper functions
def gen_cmd_output(authed_client, server_id):
    # First run status to generate some output
    response = authed_client.get(
        f"/controls?server_id={server_id}",
        follow_redirects=True
    )
    assert response.status_code == 200
    csrf_token = get_csrf_token(response)

    # Test starting the server.
    response = authed_client.post(
        "/controls",
        data={
            "csrf_token": csrf_token,
            "server_id": server_id,
            "command": 'dt',
            "ctrl_form": 'true',
        },
        follow_redirects=True
    )
    assert response.status_code == 200


def check_api_response(response, expected_status, expected_data=None):
    """Helper to check API response status and data"""
    assert response.status_code == expected_status
    if expected_data:
        response_data = json.loads(response.data)
        assert response_data == expected_data


def get_server_id(install_name):
    """Helper to get server ID by install name"""
    server = GameServer.query.filter_by(install_name=install_name).first()
    return str(server.id) if server else None


### UpdateConsole API tests
def test_update_console_no_auth(client, add_mock_server, test_vars):
    """Test UpdateConsole without authentication"""
    server_id = get_server_id(test_vars["test_server"])
    with client:
        response = client.post(f"/api/update-console/{server_id}")
        check_api_response(response, 302)


def test_update_console_no_perms(user_authed_client_no_perms, add_mock_server, test_vars):
    """Test UpdateConsole without permissions"""
    server_id = get_server_id(test_vars["test_server"])
    with user_authed_client_no_perms:
        response = user_authed_client_no_perms.post(f"/api/update-console/{server_id}")
        check_api_response(response, 403, {"Error": "Permission denied!"})


def test_update_console_invalid_id(authed_client):
    """Test UpdateConsole with invalid server ID"""
    with authed_client:
        response = authed_client.post("/api/update-console/nonexistent")
        check_api_response(response, 400, {"Error": "Supplied server does not exist!"})


### ServerStatus API tests
def test_server_status_no_auth(client, add_mock_server, test_vars):
    """Test ServerStatus without authentication"""
    server_id = get_server_id(test_vars["test_server"])
    with client:
        response = client.get(f"/api/server-status/{server_id}")
        check_api_response(response, 302)


def test_server_status_no_perms(user_authed_client_no_perms, add_mock_server, test_vars):
    """Test ServerStatus without permissions"""
    server_id = get_server_id(test_vars["test_server"])
    with user_authed_client_no_perms:
        response = user_authed_client_no_perms.get(f"/api/server-status/{server_id}")
        check_api_response(response, 403, {"Error": "Permission Denied!"})


def test_server_status_invalid_id(authed_client):
    """Test ServerStatus with invalid server ID"""
    with authed_client:
        response = authed_client.get("/api/server-status/invalid")
        check_api_response(response, 400, {"Error": "Invalid id"})


def test_server_status_success(authed_client, add_mock_server, test_vars):
    """Test successful ServerStatus"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.get(f"/api/server-status/{server_id}")
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert "id" in response_data
        assert "status" in response_data
        assert response_data["id"] == server_id


### SystemUsage API tests
def test_system_usage_no_auth(client):
    """Test SystemUsage without authentication"""
    with client:
        response = client.get("/api/system-usage")
        check_api_response(response, 302)


def test_system_usage_success(authed_client):
    """Test successful SystemUsage"""
    with authed_client:
        response = authed_client.get("/api/system-usage")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, dict)


### CmdOutput API tests
def test_cmd_output_no_auth(client, add_mock_server, test_vars):
    """Test CmdOutput without authentication"""
    server_id = get_server_id(test_vars["test_server"])
    with client:
        response = client.get(f"/api/cmd-output/{server_id}")
        check_api_response(response, 302)


def test_cmd_output_invalid_id(authed_client):
    """Test CmdOutput with invalid server ID"""
    with authed_client:
        response = authed_client.get("/api/cmd-output/invalid")
        check_api_response(response, 200, {"Error": "eer never heard of em"})


def test_cmd_output_success(authed_client, add_mock_server, test_vars):
    """Test successful CmdOutput"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        gen_cmd_output(authed_client, server_id)

        response = authed_client.get(f"/api/cmd-output/{server_id}")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, dict)


### GameServerDelete API tests
def test_delete_server_no_auth(client, add_mock_server, test_vars):
    """Test GameServerDelete without authentication"""
    server_id = get_server_id(test_vars["test_server"])
    with client:
        response = client.delete(f"/api/delete/{server_id}")
        check_api_response(response, 302)


def test_delete_server_no_perms(user_authed_client_no_perms, add_mock_server, test_vars):
    """Test GameServerDelete without permissions"""
    server_id = get_server_id(test_vars["test_server"])
    with user_authed_client_no_perms:
        response = user_authed_client_no_perms.delete(f"/api/delete/{server_id}")
        check_api_response(response, 403, {
            "Error": f"Insufficient permission to delete {test_vars['test_server']}"
        })


def test_delete_server_invalid_id(authed_client):
    """Test GameServerDelete with invalid server ID"""
    with authed_client:
        response = authed_client.delete("/api/delete/invalid")
        check_api_response(response, 404, {"Error": "Server not found!"})


def test_delete_server_success(authed_client, add_mock_server, test_vars):
    """Test successful GameServerDelete"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.delete(f"/api/delete/{server_id}")
        assert response.status_code == 204
        assert response.data == b""
        
        # Verify server was actually deleted
        server = GameServer.query.filter_by(id=server_id).first()
        assert server is None


### ManageCron API tests
def test_manage_cron_no_auth(client, add_mock_server, test_vars):
    """Test ManageCron without authentication"""
    server_id = get_server_id(test_vars["test_server"])
    with client:
        # Test GET
        response = client.get(f"/api/cron/{server_id}")
        check_api_response(response, 302)

        # Test POST
        response = client.post(f"/api/cron/{server_id}")
        check_api_response(response, 302)

        # Test DELETE
        response = client.delete(f"/api/cron/{server_id}/test_job")
        check_api_response(response, 302)


def test_manage_cron_no_perms(user_authed_client_no_perms, add_mock_server, test_vars):
    """Test ManageCron without permissions"""
    server_id = get_server_id(test_vars["test_server"])
    with user_authed_client_no_perms:
        # Test GET
        response = user_authed_client_no_perms.get(f"/api/cron/{server_id}")
        check_api_response(response, 403, {"Error": "Insufficient permission"})

        # Test POST
        response = user_authed_client_no_perms.post(f"/api/cron/{server_id}")
        check_api_response(response, 403, {"Error": "Insufficient permission"})

        # Test DELETE
        response = user_authed_client_no_perms.delete(f"/api/cron/{server_id}/test_job")
        check_api_response(response, 403, {"Error": "Insufficient permission"})


def test_manage_cron_invalid_server_id(authed_client):
    """Test ManageCron with invalid server ID"""
    with authed_client:
        # Test GET
        response = authed_client.get("/api/cron/invalid_server")
        assert response.status_code == 404

        # Test POST
        response = authed_client.post(
            "/api/cron/invalid_server",
            json={
                "command": "start",
                "cron_expression": "* * * * *"
            }
        )
        assert response.status_code == 404

        # Test DELETE
        response = authed_client.delete("/api/cron/invalid_server/test_job")
        assert response.status_code == 404


def test_manage_cron_get_list(authed_client, add_mock_server, test_vars):
    """Test GET to list all cron jobs"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.get(f"/api/cron/{server_id}")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)


def test_manage_cron_get_single_job(authed_client, add_mock_server, test_vars, add_mock_cron_job):
    """Test GET to retrieve a single cron job"""
    server_id = get_server_id(test_vars["test_server"])
    job_id = test_vars["job_id"]

    with authed_client:
        response = authed_client.get(f"/api/cron/{server_id}/{job_id}")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, dict)
        assert response_data["job_id"] == job_id
        assert response_data["server_id"] == server_id


def test_manage_cron_get_nonexistent_job(authed_client, add_mock_server, test_vars):
    """Test GET with non-existent job ID"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.get(f"/api/cron/{server_id}/nonexistent_job")
        assert response.status_code == 404


def test_manage_cron_post_create_job(authed_client, add_mock_server, test_vars):
    """Test POST to create a new cron job"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.post(
            f"/api/cron/{server_id}",
            json={
                "command": "start",
                "cron_expression": "* * * * *",
                "comment": "Test job"
            }
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == {"success": "job updated"}


def test_manage_cron_post_invalid_cron(authed_client, add_mock_server, test_vars):
    """Test POST with invalid cron expression"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.post(
            f"/api/cron/{server_id}",
            json={
                "command": "start",
                "cron_expression": "invalid expression",
                "comment": "Test job"
            }
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data == {"Error": "Invalid cron expression"}


def test_manage_cron_post_custom_command(authed_client, add_mock_server, test_vars):
    """Test POST with custom command"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        # Test 'send' command
        response = authed_client.post(
            f"/api/cron/{server_id}",
            json={
                "command": "send",
                "custom": "say Hello",
                "cron_expression": "* * * * *"
            }
        )
        assert response.status_code == 201

        # Test 'custom' command
        response = authed_client.post(
            f"/api/cron/{server_id}",
            json={
                "command": "custom",
                "custom": "special_command",
                "cron_expression": "* * * * *"
            }
        )
        assert response.status_code == 201


def test_manage_cron_delete_job(authed_client, add_mock_server, test_vars, add_mock_cron_job):
    """Test DELETE to remove a cron job"""
    server_id = get_server_id(test_vars["test_server"])
    job_id = test_vars["job_id"]

    with authed_client:
        response = authed_client.delete(f"/api/cron/{server_id}/{job_id}")
        assert response.status_code == 204
        assert response.data == b""


def test_manage_cron_delete_nonexistent_job(authed_client, add_mock_server, test_vars):
    """Test DELETE with non-existent job ID"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.delete(f"/api/cron/{server_id}/nonexistent_job")
        debug_response(response)
        assert response.status_code == 500
