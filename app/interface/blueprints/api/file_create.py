import os
import json

from flask import Response, request, current_app
from flask_login import login_required, current_user
from flask_restful import Resource

from . import api

from app.utils import log_wrap

from app.interface.use_cases import get_game_server, check_user_access, write_file


######### API File Create #########

class FileCreate(Resource):
    @login_required
    def post(self, server_id):
        server = get_game_server(server_id)
        if server == None:
            resp_dict = {"Error": "Server not found!"}
            return Response(json.dumps(resp_dict, indent=4), status=404, mimetype="application/json")

        data = request.get_json()
        if not data or "path" not in data or "name" not in data:
            resp_dict = {"Error": "Missing path or name in request body"}
            return Response(json.dumps(resp_dict, indent=4), status=400, mimetype="application/json")

        path = data["path"]
        name = data["name"]

        # Check permissions
        if not check_user_access(current_user.id, "files_edit", server_id):
            resp_dict = {
                "Error": f"Insufficient permission to create files for {server.install_name}"
            }
            return Response(json.dumps(resp_dict, indent=4), status=403, mimetype="application/json")

        current_app.logger.info(log_wrap(f"{current_user} creating {path}/{name}: ", server_id))

        full_path = os.path.join(path, name)

        if write_file(server, full_path, ""):
            log_audit_event(current_user.id, f"User '{current_user.username}', created file '{file_path}'")
            return "", 201
        else:
            resp_dict = {"Error": "Problem creating file"}
            return Response(json.dumps(resp_dict, indent=4), status=500, mimetype="application/json")


api.add_resource(FileCreate, "/files/create/<string:server_id>")
