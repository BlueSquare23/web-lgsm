import os
import json
import pytest
import urllib.parse
import subprocess

from flask import url_for
from pathlib import Path

from app.infrastructure.persistence.models.game_server_model import GameServerModel

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
    server = GameServerModel.query.filter_by(install_name=install_name).first()
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
        server = GameServerModel.query.filter_by(id=server_id).first()
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
                "schedule": "* * * * *"
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
                "schedule": "* * * * *",
                "comment": "Test job"
            }
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data == {"success": "job updated"}


def test_manage_cron_post_invalid_cron(authed_client, add_mock_server, test_vars):
    """Test POST with invalid cron schedule"""
    server_id = get_server_id(test_vars["test_server"])
    with authed_client:
        response = authed_client.post(
            f"/api/cron/{server_id}",
            json={
                "command": "start",
                "schedule": "invalid schedule",
                "comment": "Test job"
            }
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data == {"Error": "Invalid cron schedule"}


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
                "schedule": "* * * * *"
            }
        )
        assert response.status_code == 201

        # Test 'custom' command
        response = authed_client.post(
            f"/api/cron/{server_id}",
            json={
                "command": "custom",
                "custom": "special_command",
                "schedule": "* * * * *"
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


def test_post_server_list_order(authed_client, add_mock_server, test_vars):
    """Test POST update-order"""
    server_name = test_vars["test_server"]
    server_id = get_server_id(server_name)
    with authed_client:
        response = authed_client.post(
            f"/api/update-order",
            json={
                "order": [{
                    "id":server_id,
                    "name":server_name
                }]
            }
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data == { "success": "Sort order updated successfully"}

def test_load_spec(authed_client, add_mock_server, test_vars):
    with authed_client:
        response = authed_client.get("/api/spec")
        assert response.status_code == 200

        data = json.loads(response.data)

        # basic structure check
        assert "paths" in data
        paths = data["paths"]

        # check a few important routes exist
        assert "/cmd-output/{server_id}" in paths
        assert "/cron/{server_id}" in paths
        assert "/server-status/{server_id}" in paths
        assert "/system-usage" in paths

        # optional: check methods exist for a route
        assert "get" in paths["/system-usage"]
        assert "post" in paths["/cron/{server_id}"]


def test_file_create(authed_client, add_mock_server, test_vars):
    """Test create file via api"""
    server_id = get_server_id(test_vars["test_server"])
    path = str(Path.home())
    name = 'testing1234'
    file = Path(os.path.join(path, name))

    # Make sure test file is removed before tests
    file.unlink(missing_ok=True)

    with authed_client:
        # Test only accept json
        response = authed_client.post(f"/api/files/create/{server_id}",
            data={
                "path": path,
                "name": name,
            },
        )
        check_api_response(response, 415, {'message': "Did not attempt to load JSON data because the request Content-Type was not 'application/json'."})

        # Test only accepts POSTs
        response = authed_client.delete(f"/api/files/create/{server_id}")
        check_api_response(response, 405, {'message': "The method is not allowed for the requested URL."})
        response = authed_client.get(f"/api/files/create/{server_id}")
        check_api_response(response, 405, {'message': "The method is not allowed for the requested URL."})

        # Test with bad server id
        response = authed_client.post("/api/files/create/BAD_SERVER_ID",
            json={
                "path": path,
                "name": name,
            },
        )
        check_api_response(response, 404, {"Error": "Server not found!"})

        # Test no path in response
        response = authed_client.post(f"/api/files/create/{server_id}",
            json={
                "name": name,
            },
        )
        check_api_response(response, 400, {"Error": "Missing path or name in request body"})

        # Test no name in response
        response = authed_client.post(f"/api/files/create/{server_id}",
            json={
                "path": path,
            },
        )
        check_api_response(response, 400, {"Error": "Missing path or name in request body"})

        # Test filename too long 
        too_long_name = 'a' * 101
        response = authed_client.post(f"/api/files/create/{server_id}",
            json={
                "path": path,
                "name": too_long_name,
            },
        )
        check_api_response(response, 400, {"Error": 'Filename must be at most 100 characters long'})

        # Test is excluded dir
        bad_path = '/etc/'
        response = authed_client.post(f"/api/files/create/{server_id}",
            json={
                "path": bad_path,
                "name": name,
            },
        )
        check_api_response(response, 403, {"Error": "Not allowed access to this file or directory"})

        # Test legit create file & ensure file actually created
        response = authed_client.post(f"/api/files/create/{server_id}",
            json={
                "path": path,
                "name": name,
            },
        )
        check_api_response(response, 201)
        assert file.is_file()

        # Cleanup
        file.unlink()


def test_file_create_no_perms(client, add_mock_server, user_authed_client_no_perms, test_vars):
    test_server = test_vars["test_server"]
    server_id = get_server_id(test_server)

    path = str(Path.home())
    name = 'testing1234'
    with client:
        # Test user has no perms for server
        response = client.post(f"/api/files/create/{server_id}",
            json={
                "path": path,
                "name": name,
            },
        )
        check_api_response(response, 403, {"Error": f"Insufficient permission to create files for {test_server}"})
 

def test_file_rename(authed_client, add_mock_server, test_vars):
    """Test rename file via api"""
    server_id = get_server_id(test_vars["test_server"])
    path = str(Path.home())
    name = 'testing1234'
    new_name = 'testing5678'
    file = Path(os.path.join(path, name))
    file_path = str(file)
    file_path_urlencoded = urllib.parse.quote(urllib.parse.quote(file_path, safe=""), safe="")  # URL encode twice
    file_new = Path(os.path.join(path, new_name))

    # Create file we're going to rename
    file.touch()

    # Make sure test file is removed before tests
    file_new.unlink(missing_ok=True)

    with authed_client:
        # Test only accept json
        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            data={
                "new_name": new_name,
            },
        )
        check_api_response(response, 415, {'message': "Did not attempt to load JSON data because the request Content-Type was not 'application/json'."})

        # Test only accepts POSTs
        response = authed_client.delete(f"/api/files/rename/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 405, {'message': "The method is not allowed for the requested URL."})
        response = authed_client.get(f"/api/files/rename/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 405, {'message': "The method is not allowed for the requested URL."})

        # Test with bad server id
        response = authed_client.post(f"/api/files/rename/BAD_SERVER_ID/{file_path_urlencoded}",
            json={
                "new_name": new_name,
            },
        )
        check_api_response(response, 404, {"Error": "Server not found!"})

        # Test bad path
        bad_path = '/etc/passwd'
        bad_path_urlencoded = urllib.parse.quote(urllib.parse.quote(bad_path, safe=""), safe="")  # URL encode twice
        response = authed_client.post(f"/api/files/rename/{server_id}/{bad_path_urlencoded}",
            json={
                "new_name": new_name,
            },
        )
        check_api_response(response, 403, {"Error": "Not allowed access to this directory"})

        # Test malformed/junk path
        bad_path = 'fartfartfartfart'
        bad_path_urlencoded = urllib.parse.quote(urllib.parse.quote(bad_path, safe=""), safe="")  # URL encode twice
        response = authed_client.post(f"/api/files/rename/{server_id}/{bad_path_urlencoded}",
            json={
                "new_name": new_name,
            },
        )
        check_api_response(response, 400, {"Error": "Bad file_path supplied!"})

        # Test with no new_name data
        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}", json={})
        check_api_response(response, 400, {"Error": "Missing new_name in request body"})

        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            json={
                "blah": 'blah',
            },
        )
        check_api_response(response, 400, {"Error": "Missing new_name in request body"})

        # Test invalid file_name
        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            json={
                "new_name": '',
            },
        )
        check_api_response(response, 400, {"Error": "Invalid filename"})

        bad_name = 'a' * 101
        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            json={
                "new_name": bad_name, 
            },
        )
        check_api_response(response, 400, {'Error': 'Filename must be at most 100 characters long'})

        # Test legit file rename
        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            json={
                "new_name": new_name, 
            },
        )
        check_api_response(response, 204)

        assert not file.is_file()
        assert file_new.is_file()

        # Cleanup
        file_new.unlink()

        # Test renaming non-existent file
        response = authed_client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            json={
                "new_name": new_name, 
            },
        )
        check_api_response(response, 500, {"Error": f"Problem renaming file"})

def test_file_rename_no_perms(client, add_mock_server, user_authed_client_no_perms, test_vars):
    test_server = test_vars["test_server"]
    server_id = get_server_id(test_server)

    path = str(Path.home())
    name = 'testing1234'
    new_name = 'testing5678'
    file = Path(os.path.join(path, name))
    file_path = str(file)
    file_path_urlencoded = urllib.parse.quote(urllib.parse.quote(file_path, safe=""), safe="")  # URL encode twice

    with client:
        # Test user has no perms for server
        response = client.post(f"/api/files/rename/{server_id}/{file_path_urlencoded}",
            json={
                "new_name": new_name, 
            },
        )
        check_api_response(response, 403, {"Error": f"Insufficient permission to rename files for {test_server}"})


def test_file_delete(authed_client, add_mock_server, test_vars):
    """Test file delete via api"""
    test_server = test_vars["test_server"]
    server_id = get_server_id(test_server)

    path = str(Path.home())
    name = 'testing1234'
    file = Path(os.path.join(path, name))
    file_path = str(file)
    file_path_urlencoded = urllib.parse.quote(urllib.parse.quote(file_path, safe=""), safe="")  # URL encode twice

    # Create file we're going to delete
    file.touch()

    with authed_client:
        # Test with bad server id
        response = authed_client.delete(f"/api/files/delete/BAD_SERVER_ID/{file_path_urlencoded}")
        check_api_response(response, 404, {"Error": "Server not found!"})

        # Test only accepts DELETEs
        response = authed_client.post(f"/api/files/delete/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 405, {'message': "The method is not allowed for the requested URL."})
        response = authed_client.get(f"/api/files/delete/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 405, {'message': "The method is not allowed for the requested URL."})

        # Test not allowed path
        bad_path = '/etc/passwd'
        bad_path_urlencoded = urllib.parse.quote(urllib.parse.quote(bad_path, safe=""), safe="")  # URL encode twice
        response = authed_client.delete(f"/api/files/delete/{server_id}/{bad_path_urlencoded}")
        check_api_response(response, 403, {"Error": "Not allowed access to this directory"})

        # Test malformed/junk path
        bad_path = 'fartfartfartfart'
        bad_path_urlencoded = urllib.parse.quote(urllib.parse.quote(bad_path, safe=""), safe="")  # URL encode twice
        response = authed_client.delete(f"/api/files/delete/{server_id}/{bad_path_urlencoded}")
        check_api_response(response, 400, {"Error": "Bad file_path supplied!"})

        # Test actual delete
        response = authed_client.delete(f"/api/files/delete/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 204)
        assert not file.is_file()

        # Test deleting non-existent file
        response = authed_client.delete(f"/api/files/delete/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 500, {"Error": f"Problem deleting file"})


def test_file_delete_no_perms(client, add_mock_server, user_authed_client_no_perms, test_vars):
    test_server = test_vars["test_server"]
    server_id = get_server_id(test_server)

    path = str(Path.home())
    name = 'testing1234'
    new_name = 'testing5678'
    file = Path(os.path.join(path, name))
    file_path = str(file)
    file_path_urlencoded = urllib.parse.quote(urllib.parse.quote(file_path, safe=""), safe="")  # URL encode twice

    with client:
        # Test user has no perms for server
        response = client.delete(f"/api/files/delete/{server_id}/{file_path_urlencoded}")
        check_api_response(response, 403, {"Error": f"Insufficient permission to delete files for {test_server}"})

