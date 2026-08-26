import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *

from . import api

from app.interface.use_cases import get_game_server, check_user_access, get_game_server_power_state

######### API Server Statuses #########

class ServerStatus(Resource):
    @login_required
    def get(self, server_id):
#        server = GameServer.query.filter_by(id=server_id).first()
        server = get_game_server(server_id)
        if server == None:
            resp_dict = {"Error": "Invalid id"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response

        if not check_user_access(current_user.id, "server-statuses", server.id):
            resp_dict = {"Error": "Permission Denied!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        server_status = get_game_server_power_state(server)

        resp_dict = {"id": server.id, "status": server_status}
        current_app.logger.info(log_wrap("resp_dict", resp_dict))

        response = Response(
            json.dumps(resp_dict, indent=4), status=200, mimetype="application/json"
        )
        return response

api.add_resource(ServerStatus, "/server-status/<string:server_id>")

