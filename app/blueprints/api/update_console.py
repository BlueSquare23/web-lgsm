import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.config.config_manager import ConfigManager
from app.utils import *
from app.models import GameServer
from app.services import ProcInfoService, CommandExecService, TmuxSocketNameService

from . import api

######### API Update Console #########

class UpdateConsole(Resource):
    config = ConfigManager()
    command_service = CommandExecService(config)

    @login_required
    def post(self, server_id):
        if not current_user.has_access("update-console"):
            resp_dict = {"Error": "Permission denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
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

        tmux_socket = TmuxSocketNameService().get_tmux_socket_name(server)

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

        command_service.run_command(cmd, server, server.id)
        proc_info = ProcInfoService().get_process(server.id, create=True)

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

