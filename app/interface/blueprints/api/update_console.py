import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *
#from app.models import GameServer
from app.services import TmuxSocketNameCache

from . import api

from app.container import container

######### API Update Console #########

class UpdateConsole(Resource):

    @login_required
    def post(self, server_id):
        if not container.check_user_access().execute(current_user.id, "update-console"):
            resp_dict = {"Error": "Permission denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        # Check that the submitted server exists in db.
        server = container.get_game_server().execute(server_id)
        if server == None:
            resp_dict = {"Error": "Supplied server does not exist!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response

        tmux_socket = TmuxSocketNameCache().get_tmux_socket_name(server)

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

        container.run_command().execute(cmd, server, server.id)
        proc_info = container.get_process().execute(server.id, create=True)

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

