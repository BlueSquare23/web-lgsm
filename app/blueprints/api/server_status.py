import json

from flask import Response
from flask_login import login_required, current_user
from flask_restful import Resource

from app.utils import *
from app.models import GameServer

from . import api


######### API Server Statuses #########

class ServerStatus(Resource):
    @login_required
    def get(self, server_id):
        server = GameServer.query.filter_by(id=server_id).first()
        if server == None:
            resp_dict = {"Error": "Invalid id"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response

        if not current_user.has_access("server-statuses", server.id):
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

