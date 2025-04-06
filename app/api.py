import json

from flask import Blueprint, request, Response, redirect
from flask_login import login_required, current_user
from flask_restful import Api, Resource, reqparse, abort

from . import db
from .utils import *
from .models import *
from .proc_info_vessel import ProcInfoVessel
from .processes_global import *

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

def abort_if_id_none(server_id):
    if server_id == None:
        resp_dict = {"Error": "No id supplied"}
        abort(404, message=resp_dict)


######### API Update Console #########

class UpdateConsole(Resource):
    @login_required
    def post(self, server_id):
        if not user_has_permissions(current_user, "update-console"):
            resp_dict = {"Error": "Permission denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

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

        if server.id in get_all_processes():
            proc_info = get_process(server_id)
        else:
            proc_info = add_process(server.id)

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

api.add_resource(UpdateConsole, "/update-console/<string:server_id>")

######### API Server Statuses #########

class ServerStatus(Resource):
    @login_required
    def get(self, server_id):
        abort_if_id_none(server_id)
        
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

api.add_resource(ServerStatus, "/server-status/<string:server_id>")


######### API System Usage #########

class SystemUsage(Resource):
    @login_required
    def get(self):
        server_stats = get_server_stats()
        response = Response(
            json.dumps(server_stats, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(SystemUsage, "/system-usage")


######### API CMD Output #########

class CmdOutput(Resource):
    @login_required
    def get(self, server_id):
        abort_if_id_none(server_id)

        # Can't do anything if we don't have proc info vessel stored.
        if server_id not in get_all_processes():
            resp_dict = {"Error": "eer never heard of em"}
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

api.add_resource(CmdOutput, "/cmd-output/<string:server_id>")


######### API GameServer Delete #########

class GameServerDelete(Resource):
    @login_required
    def delete(self, server_id):
        abort_if_id_none(server_id)

        server = GameServer.query.filter_by(id=server_id).first()
        if server == None:
            resp_dict = {"Error": "Server not found!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=404, mimetype="application/json"
            )
            return response

        config = read_config("delete")
        current_app.logger.info(log_wrap("config", config))

        # NOTE: For everyone's safety, if config options are incongruous, default
        # to safer keep user, keep files option. (ie. If delete_user is True and
        # remove_files is False, default to keep user.
        if config["delete_user"] and not config["remove_files"]:
            config["delete_user"] = False

        # Check if user has permissions to delete route & server.
        if not user_has_permissions(current_user, "delete", server_id):
            resp_dict = {"Error": f"Insufficient permission to delete {server.install_name}"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        current_app.logger.info(log_wrap(f"{current_user} deleting ID: ", server_id))

        current_app.logger.info(server)

        # Drop any saved proc_info objects.
        remove_process(server_id)

        # Log to ensure process was dropped.
        current_app.logger.info(log_wrap("All processes", get_all_processes()))

        if not delete_server(server, config["remove_files"], config["delete_user"]):
            resp_dict = {"Error": "Problem deleting server, see error logs for more details."}
            response = Response(
                json.dumps(resp_dict, indent=4), status=500, mimetype="application/json"
            )
            return response
            
        # We don't want to keep deleted servers in the cache.
        update_tmux_socket_name_cache(server_id, None, True)

        return "", 204

api.add_resource(GameServerDelete, "/delete/<string:server_id>")

