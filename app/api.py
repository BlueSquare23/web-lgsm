import json

from flask_login import login_required, current_user
from flask import Blueprint, request, Response, redirect

from . import db
from .utils import *
from .models import *
from .proc_info_vessel import ProcInfoVessel
from .processes_global import *

api = Blueprint('api', __name__)


######### API Update Console #########

@api.route("/api/update-console", methods=["POST"])
@login_required
def update_console():
    global servers

    if not user_has_permissions(current_user, "update-console"):
        resp_dict = {"Error": "Permission denied!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
        )
        return response

    # Collect var from POST request.
    server_id = request.form.get("server_id")

    # Can't do needful without a server specified.
    if server_id == None:
        resp_dict = {"Error": "Required var: server"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    # Check that the submitted server exists in db.
    server = GameServer.query.filter_by(id=server_id).first()
    if server == None:
        resp_dict = {"Error": "Supplied server does not exist!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    tmux_socket = get_tmux_socket_name(server)

    cmd = [
        PATHS["tmux"],
        "-L",
        tmux_socket,
        "capture-pane",
        "-pt",
        server.script_name,
        "-S",
        "-",
        "-E",
        "-",
        "-J",
    ]

    if server.install_type == "docker":
        cmd = docker_cmd_build(server) + cmd

    if server.install_name in servers:
        proc_info = servers[server.install_name]
    else:
        proc_info = ProcInfoVessel()
        servers[server.install_name] = proc_info

    if should_use_ssh(server):
        pub_key_file = get_ssh_key_file(server.username, server.install_host)
        run_cmd_ssh(
            cmd,
            server.install_host,
            server.username,
            pub_key_file,
            proc_info,
            None,
            None,
        )
    else:
        run_cmd_popen(cmd, proc_info)

    if proc_info.exit_status > 0:
        resp_dict = {"Error": "Refresh cmd failed!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=503, mimetype="application/json"
        )
        return response

    resp_dict = {"Success": "Output updated!"}
    response = Response(
        json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API Server Statuses #########

@api.route("/api/server-status", methods=["GET"])
@login_required
def get_status():
    # Collect args from GET request.
    server_id = request.args.get("id")

    if server_id == None:
        resp_dict = {"Error": "No id supplied"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    server = GameServer.query.get(server_id)
    if server == None:
        resp_dict = {"Error": "Invalid id"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
        )
        return response

    if not user_has_permissions(current_user, "server-statuses", server.install_name):
        resp_dict = {"Error": "Permission Denied!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
        )
        return response

    server_status = get_server_status(server)
    resp_dict = {"id": server.id, "status": server_status}
    current_app.logger.info(log_wrap("resp_dict", resp_dict))

    response = Response(
        json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API System Usage #########

@api.route("/api/system-usage", methods=["GET"])
@login_required
def get_stats():
    server_stats = get_server_stats()
    response = Response(
        json.dumps(server_stats, indent=4), status=200, mimetype="application/json"
    )
    return response


######### API CMD Output Page #########

@api.route("/api/cmd-output", methods=["GET"])
@login_required
def no_output():
    global servers

    # Collect args from GET request.
    server_id = request.args.get("server_id")

    # Can't load the controls page without a server specified.
    if server_id == None:
        resp_dict = {"error": "eer can't load page n'@"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

    # Can't do anything if we don't have proc info vessel stored.
    if server_id not in get_all_processes():
        resp_dict = {"error": "eer never heard of em"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

    if not user_has_permissions(current_user, "cmd-output", server_id):
        resp_dict = {"Error": "Permission Denied!"}
        response = Response(
            json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
        )
        return response

    output = get_process(server_id)

    # Returns json for used by ajax code on /controls route.
    response = Response(output.toJSON(), status=200, mimetype="application/json")
    return response


