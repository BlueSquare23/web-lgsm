import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *

from . import api

from app.interface.use_cases import check_user_access, get_game_server, get_tmux_socket_name, run_command, get_process

######### API Update Console #########

class UpdateConsole(Resource):

    @login_required
    def post(self, server_id):
        if not check_user_access(current_user.id, "update-console"):
            resp_dict = {"Error": "Permission denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        # Check that the submitted server exists in db.
        server = get_game_server(server_id)
        if server == None:
            resp_dict = {"Error": "Supplied server does not exist!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response

        tmux_socket = get_tmux_socket_name(server)

        # TODO: Change all this, should NOT be happening in route code. Instead
        # convert to rpc procedure. Also should be happening in infra layer
        # with a simple usecase to call it.
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

        run_command(cmd, server, server.id)
        proc_info = get_process(server.id, create=True)

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

