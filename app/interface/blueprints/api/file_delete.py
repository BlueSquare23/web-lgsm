import json

from urllib.parse import unquote

from flask import Response, flash, current_app
from flask_login import login_required, current_user
from flask_restful import Resource

from app import db

from . import api

from app.utils import log_wrap

from app.interface.use_cases import get_game_server, check_user_access, delete_file

######### API File Delete #########

class FileDelete(Resource):
    @login_required
    def delete(self, server_id, file_path):
        server = get_game_server(server_id)
        if server == None:
            resp_dict = {"Error": "Server not found!"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=404, mimetype="application/json"
            )
            return response

        # Try unwrap path url encoding
        try:
            file_path = unquote(file_path)
        except Exception as e:
            resp_dict = {"Error": f"Problem unwrapping path url encoding: {e}"}
            response = Response(
                json.dumps(resp_dict, indent=4), status=400, mimetype="application/json"
            )
            return response


        # Check if user has permissions to files delete route & server.
        if not check_user_access(current_user.id, "files", server_id):
            resp_dict = {
                "Error": f"Insufficient permission to delete files for {server.install_name}"
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=403, mimetype="application/json"
            )
            return response

        current_app.logger.info(log_wrap(f"{current_user} deleting {file_path}: ", server_id))
        current_app.logger.info(file_path)

        if delete_file(server, file_path):
            return "", 204
        else:
            resp_dict = {
                "Error": f"Problem deleting file"
            }
            response = Response(
                json.dumps(resp_dict, indent=4), status=500, mimetype="application/json"
            )
            return response

api.add_resource(FileDelete, "/files/delete/<string:server_id>/<string:file_path>")

